"""
Printable extras for a deck: bingo, I-spy, match-it and Listen & Do, as letter PDFs.

How it works (like a mail-merge):
  1. Read decks/{id}/extras.yaml (the words and settings) and deck.json (title, colors).
  2. Get the pictures ready: item art from generate_items.py, plus two AI pictures
     (the empty I-spy garden and the Listen & Do line-art scene). Missing AI pictures
     are generated once and then reused from decks/{id}/extras/art/.
  3. Fill an HTML template per activity (templates/activities/*.html, Jinja2).
  4. Print each HTML page to a letter PDF with Playwright (a headless Chrome),
     and save a PNG preview of page 1.

Output:
  decks/{id}/extras/{bingo,ispy,match,listen_do}.pdf
  decks/{id}/extras/previews/{name}_p1.png
  decks/{id}/extras/build/   (HTML + resized pictures; safe to delete, rebuilt each run)

Usage (from src/):
  python generate_activities.py ../decks/bereshit
  python generate_activities.py ../decks/bereshit --only bingo,ispy
  python generate_activities.py ../decks/bereshit --no-ai          # never call the image API
  python generate_activities.py ../decks/bereshit --all-previews /tmp/pages   # every page as PNG
"""

import argparse
import html
import json
import logging
import math
import re
import shutil
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image, ImageChops, ImageDraw, ImageFont

import bingo
import extras_data
import ispy
from generate_items import (binarize_line_art, crop_to_content, request_image, setup_logging)

logger = logging.getLogger("generate_activities")

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = REPO_ROOT / "templates" / "activities"
PLATES = REPO_ROOT / "style" / "plates"
ACTIVITIES = ("bingo", "ispy", "match", "listen_do")

ISPY_SCENE_IN = 7.5        # the I-spy picture is 7.5" square on the page
ISPY_SCENE_PX = 2048       # composed at 2048 px = 273 pixels per inch
ITEM_PX = 700              # item pictures are resized to this for the PDFs (keeps files small)
PREVIEW_DPI = 100

LABEL_FONT_PATHS = ["/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
                    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                    "/Library/Fonts/Arial.ttf", "DejaVuSans-Bold.ttf"]

# Colors a 4-6 year old has in the crayon box, for the drawn answer keys
CRAYON = {"green": "#3BAA3B", "yellow": "#F6D02F", "blue": "#3B82F6", "red": "#E53935",
          "orange": "#FB8C00", "purple": "#8E44AD", "brown": "#8D5524", "gray": "#9E9E9E"}

ISPY_BG_PROMPT = """=== REFERENCE IMAGES ===
Image 1: style plate 'landscape' (match art style only, not content).

=== WHAT TO DRAW ===
{scene}

=== STYLE ===
The same children's cartoon style as Image 1: thick clean dark outlines, flat bright colors with soft gradients,
warm and inviting. Clean crisp illustration, no grain or texture.

=== RULES ===
Do NOT render any text, letters, numbers or Hebrew anywhere. No border or frame."""

LISTEN_SCENE_PROMPT = """{scene}

This is a coloring page for children ages 4-6: thick bold black outlines on pure white, no shading, no gray,
no color, no texture. Large, simple, closed shapes that are easy to color with crayons.
Do NOT render any text, letters, numbers or Hebrew anywhere. No border or frame."""


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def label_font(size: int):
    for path in LABEL_FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def hebrew_html(text: str) -> str:
    """Escape text, wrap Hebrew words in RTL spans, and turn ⏸ into a pause badge."""
    escaped = html.escape(text)
    escaped = re.sub(r"([א-ת][א-ת֑-ׇ׳״־]*"
                     r"(?:\s+[א-ת][א-ת֑-ׇ׳״־]*)*)",
                     r'<span class="he" lang="he">\1</span>', escaped)
    return escaped.replace("⏸", '<span class="pause">⏸ wait</span>')


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9א-ת'’-]+", text))


class Builder:
    """Holds the paths and data for one deck's extras build."""

    def __init__(self, deck_dir: Path, use_ai: bool = True):
        self.deck_dir = deck_dir
        self.data = extras_data.load_extras(deck_dir)
        self.deck = json.loads((deck_dir / "deck.json").read_text(encoding="utf-8"))
        self.deck_id = self.data["deck_id"]
        self.items = extras_data.items_by_id(self.data)
        self.out_dir = deck_dir / "extras"
        self.art_dir = self.out_dir / "art"
        self.build_dir = self.out_dir / "build"
        self.preview_dir = self.out_dir / "previews"
        self.use_ai = use_ai
        for folder in (self.art_dir, self.build_dir, self.preview_dir, self.build_dir / "items"):
            folder.mkdir(parents=True, exist_ok=True)
        palette = self.deck.get("palette") or ["#1E3A5F", "#E0A526", "#4F9A4A", "#9BD7F5", "#FFF4D6"]
        self.env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html"]))
        self.base_context = {"deck": self.deck, "palette": palette}
        self.palette = palette
        self.warnings = []

    # ---- item pictures -------------------------------------------------------

    def item_file(self, item_id: str, kind: str) -> Path:
        return extras_data.item_dir(self.items[item_id], self.deck_dir) / f"{kind}.png"

    def item_img(self, item_id: str, kind: str = "color") -> str:
        """Resized copy of an item picture inside build/, returned as a path relative to build/."""
        name = f"{item_id}.jpg" if kind == "color" else f"{item_id}_line.png"
        target = self.build_dir / "items" / name
        if not target.exists():
            source = self.item_file(item_id, kind)
            if not source.exists():
                raise FileNotFoundError(f"Missing item art {source} — run generate_items.py first")
            pic = Image.open(source).convert("RGB" if kind == "color" else "L")
            pic = crop_to_content(pic, pad=12)
            pic.thumbnail((ITEM_PX, ITEM_PX))
            if kind == "color":
                pic.save(target, quality=88)
            else:
                binarize_line_art(pic, thicken=0).convert("1").save(target, optimize=True)
        return f"items/{name}"

    # ---- AI pictures ---------------------------------------------------------

    def ensure_art(self, name: str, prompt: str, refs: list, aspect: str, line_art: bool = False) -> Path:
        """Return art/{name}.png, generating it once (2K) if it's missing and AI is allowed."""
        path = self.art_dir / f"{name}.png"
        if path.exists():
            return path
        if not self.use_ai:
            raise FileNotFoundError(f"{path} is missing and --no-ai was given")
        raw = self.art_dir / f"{name}.raw.png"
        if not request_image(prompt, raw, refs, "2K", aspect, f"{self.deck_id} extras {name}"):
            raise RuntimeError(f"Could not generate {name}")
        pic = Image.open(raw)
        if line_art:
            binarize_line_art(pic, thicken=3).convert("1").save(path, optimize=True)
        else:
            pic.convert("RGB").save(path, optimize=True)
        raw.unlink(missing_ok=True)
        return path

    # ---- rendering -----------------------------------------------------------

    def render(self, name: str, template: str, context: dict) -> Path:
        html_text = self.env.get_template(template).render(**self.base_context, **context)
        html_path = self.build_dir / f"{name}.html"
        html_path.write_text(html_text, encoding="utf-8")
        return html_path


# ---------------------------------------------------------------------------
# Bingo
# ---------------------------------------------------------------------------

RULE_DOTS = {"corners": [(15, 15), (45, 15), (15, 45), (45, 45)],
             "line": [(15, 15), (30, 15), (45, 15)],
             "blackout": [(x, y) for y in (15, 30, 45) for x in (15, 30, 45) if (x, y) != (30, 30)]}


def bingo_instructions(win_rule: str) -> str:
    return ("Cut out the cards and shuffle. Show one card and say the Hebrew word; children echo it "
            "and cover that picture with a pom-pom or counter (not food). The candles are free. "
            f"{bingo.WIN_RULE_TEXT[win_rule]}")


def build_bingo(b: Builder) -> tuple:
    settings = b.data.get("bingo", {})
    win_rule = settings.get("win_rule", "corners")
    vocab_ids = [item["id"] for item in b.data["vocab"]]
    boards, stats = bingo.choose_boards(
        vocab_ids, b.deck_id, n_boards=settings.get("boards", 10), max_shared=settings.get("max_shared", 6),
        games=settings.get("simulations", 2000), candidates=settings.get("candidates", 300),
        target_median=tuple(settings.get("target_median_first_win", (5, 8))),
        max_avg_winners=settings.get("max_avg_simultaneous_winners", 2.0), win_rule=win_rule)
    if not stats["passed"]:
        b.warnings.append(f"bingo: no candidate met the targets; best: {stats}")
    free = b.data["free_space"]
    board_cells = []
    for board in boards:
        cells = []
        for cell in board:
            if cell == bingo.FREE:
                cells.append({"free": True, "img": b.item_img(free["id"]), "he": free["he"]})
            else:
                cells.append({"free": False, "img": b.item_img(cell), "he": b.items[cell]["he"]})
        board_cells.append(cells)
    cards = [{"img": b.item_img(i), "he": b.items[i]["he"], "translit": b.items[i]["translit"],
              "en": b.items[i]["en"]} for i in vocab_ids]
    call_pages = [cards[i:i + 4] for i in range(0, len(cards), 4)]
    html_path = b.render("bingo", "bingo.html", {
        "title": "Bingo", "boards": board_cells, "call_pages": call_pages,
        "instructions": bingo_instructions(win_rule), "rule_dots": RULE_DOTS[win_rule]})
    (b.build_dir / "bingo_boards.json").write_text(json.dumps({"boards": boards, "stats": stats}, indent=2))
    return html_path, {"bingo": stats}


# ---------------------------------------------------------------------------
# I-spy
# ---------------------------------------------------------------------------

def ispy_counts(level_cfg: dict) -> dict:
    counts = dict(level_cfg["targets"])
    counts.update(level_cfg.get("distractors", {}))
    return counts


def ispy_aspects(b: Builder, item_ids) -> dict:
    aspects = {}
    for item_id in item_ids:
        with Image.open(b.item_file(item_id, "cutout")) as pic:
            aspects[item_id] = pic.width / pic.height
    return aspects


def compose_scene(b: Builder, background: Image.Image, placements: list, kind: str = "color") -> Image.Image:
    """Stick the item pictures onto the background at their placements (kind: color | line)."""
    ppi = ISPY_SCENE_PX / ISPY_SCENE_IN
    scene = background.convert("RGB").resize((ISPY_SCENE_PX, ISPY_SCENE_PX))
    cache = {}
    for p in placements:
        if p["id"] not in cache:
            if kind == "color":
                cache[p["id"]] = Image.open(b.item_file(p["id"], "cutout")).convert("RGBA")
            else:
                cache[p["id"]] = crop_to_content(Image.open(b.item_file(p["id"], "line")).convert("L"))
        art = cache[p["id"]]
        size = (max(1, round(p["art_w"] * ppi)), max(1, round(p["art_h"] * ppi)))
        if kind == "color":
            pic = art.resize(size, Image.LANCZOS).rotate(p["angle"], expand=True, resample=Image.BICUBIC)
            x = round((p["x"] + p["w"] / 2) * ppi - pic.width / 2)
            y = round((p["y"] + p["h"] / 2) * ppi - pic.height / 2)
            scene.paste(pic, (x, y), pic)
        else:
            fitted = art.copy()
            fitted.thumbnail(size, Image.LANCZOS)
            pic = fitted.rotate(p["angle"], expand=True, resample=Image.BICUBIC, fillcolor=255)
            x = round((p["x"] + p["w"] / 2) * ppi - pic.width / 2)
            y = round((p["y"] + p["h"] / 2) * ppi - pic.height / 2)
            region = scene.crop((x, y, x + pic.width, y + pic.height))
            # "darker" keeps black lines from both, so white corners never cover a neighbour
            scene.paste(ImageChops.darker(region, pic.convert("RGB")), (x, y))
    return scene


def coloring_background(zones: dict) -> Image.Image:
    """A plain white page with a hill line and a pond line, for the coloring version."""
    size = ISPY_SCENE_PX
    img = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(img)
    hill_y = int(zones["land"][0] * size) - 30
    pond_y = int(zones["water"][0] * size) - 25
    points = [(x, hill_y + int(45 * math.sin(x / size * 6.28 * 1.3))) for x in range(0, size + 8, 8)]
    draw.line(points, fill="black", width=9)
    draw.line([(0, pond_y), (size, pond_y)], fill="black", width=9)
    for i in range(6):  # a few little waves in the pond
        cx = int((i + 0.5) * size / 6)
        draw.arc((cx - 60, pond_y + 120, cx + 60, pond_y + 200), 200, 340, fill="black", width=7)
    return img


def draw_answer_key(scene: Image.Image, placements: list, targets: dict, out_px: int = 1100) -> Image.Image:
    """Circle and number every TARGET (distractors are left alone)."""
    scale = out_px / scene.width
    key = scene.resize((out_px, out_px)).convert("RGB")
    overlay = Image.new("RGBA", key.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    colors = ["#E53935", "#1E88E5", "#8E24AA", "#F4511E", "#00897B", "#6D4C41"]
    item_color = {item: colors[i % len(colors)] for i, item in enumerate(targets)}
    numbers = {}
    font = label_font(30)
    ppi = ISPY_SCENE_PX / ISPY_SCENE_IN * scale
    for p in placements:
        if p["id"] not in targets:
            continue
        numbers[p["id"]] = numbers.get(p["id"], 0) + 1
        cx, cy = (p["x"] + p["w"] / 2) * ppi, (p["y"] + p["h"] / 2) * ppi
        r = max(p["w"], p["h"]) * ppi * 0.58
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=item_color[p["id"]], width=6)
        label = str(numbers[p["id"]])
        draw.ellipse((cx + r * 0.55, cy - r - 4, cx + r * 0.55 + 38, cy - r + 34), fill=item_color[p["id"]])
        draw.text((cx + r * 0.55 + 19, cy - r + 15), label, fill="white", font=font, anchor="mm")
    key.paste(overlay, (0, 0), overlay)
    return key


def build_ispy(b: Builder) -> tuple:
    cfg = b.data["ispy"]
    background_path = b.ensure_art("ispy_background", ISPY_BG_PROMPT.format(scene=cfg["background_prompt"]),
                                   [PLATES / "landscape.png"], "1:1")
    background = Image.open(background_path)
    levels, answer_keys, report = [], [], {}
    for number, level in enumerate(("easy", "challenge")):
        counts = ispy_counts(cfg[level])
        placements = ispy.place_items(counts, cfg["zones"], cfg["item_zones"], ispy_aspects(b, counts),
                                      level, scene_in=ISPY_SCENE_IN, seed=bingo.seed_for(b.deck_id) + number)
        placed = ispy.count_by_item(placements)
        if placed != counts:
            raise RuntimeError(f"I-spy {level}: placed {placed} but wanted {counts}")
        targets = cfg[level]["targets"]
        scene = compose_scene(b, background, placements, "color")
        scene_file = f"ispy_{level}.jpg"
        scene.save(b.build_dir / scene_file, quality=90)
        key_strip = [{"img": b.item_img(i), "count": n, "he": b.items[i]["he"],
                      "translit": b.items[i]["translit"]} for i, n in targets.items()]
        label = "Easy" if level == "easy" else "Challenge"
        levels.append({"label": f"{label}: find them all, then count!", "scene": scene_file,
                       "key": key_strip, "bw": False})
        key_img = draw_answer_key(scene, placements, targets)
        key_file = f"ispy_{level}_key.jpg"
        key_img.save(b.build_dir / key_file, quality=88)
        rows = [{"en": b.items[i]["en"], "he": b.items[i]["he"], "count": n, "role": "find"}
                for i, n in targets.items()]
        rows += [{"en": b.items[i]["en"], "he": b.items[i]["he"], "count": n, "role": "extra (not counted)"}
                 for i, n in cfg[level].get("distractors", {}).items()]
        answer_keys.append({"label": label, "img": key_file, "rows": rows})
        report[f"ispy_{level}"] = {"placed": placed, "targets": sum(targets.values()),
                                   "total": len(placements)}
        (b.build_dir / f"ispy_{level}_placements.json").write_text(json.dumps(placements, indent=1))
        if level == "easy":
            easy_placements = placements
    # Coloring version: the Easy layout, in line art on white
    color_scene = compose_scene(b, coloring_background(cfg["zones"]), easy_placements, "line")
    binarize_line_art(color_scene, thicken=0).convert("1").save(b.build_dir / "ispy_coloring.png", optimize=True)
    levels.append({"label": "Coloring page: find them, count them, color them!", "scene": "ispy_coloring.png",
                   "bw": True, "key": [{"img": b.item_img(i, "line"), "count": n, "he": b.items[i]["he"],
                                        "translit": b.items[i]["translit"]}
                                       for i, n in cfg["easy"]["targets"].items()]})
    note = ("How to play: children find each picture in the key strip and count them, touching each one. "
            "Say the Hebrew word together each time (\"דָּג, דָּג, דָּג…\"). The coloring page uses the Easy "
            "layout, so this Easy key also checks it.")
    html_path = b.render("ispy", "ispy.html", {"title": "I spy", "levels": levels,
                                                "answer_keys": answer_keys, "note": note})
    return html_path, report


# ---------------------------------------------------------------------------
# Match-it
# ---------------------------------------------------------------------------

BACK_TILE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 60 60">
<rect width="60" height="60" fill="{bg}"/>
<g fill="{star}" opacity="0.9">{stars}</g>
</svg>"""


def star_path(cx: float, cy: float, r: float) -> str:
    points = []
    for i in range(10):
        radius = r if i % 2 == 0 else r * 0.45
        angle = math.radians(-90 + i * 36)
        points.append(f"{cx + radius * math.cos(angle):.2f},{cy + radius * math.sin(angle):.2f}")
    return f'<polygon points="{" ".join(points)}"/>'


def write_back_tile(path: Path, bg: str, star: str) -> None:
    """A seamless tile: one star in the middle, quarter stars in each corner (they join up)."""
    stars = star_path(30, 30, 7) + "".join(star_path(x, y, 7) for x in (0, 60) for y in (0, 60))
    path.write_text(BACK_TILE_SVG.format(bg=bg, star=star, stars=stars), encoding="utf-8")


def build_match(b: Builder) -> tuple:
    cfg = b.data["match"]
    sets = []
    if "pic_pic" in cfg["modes"]:
        ids = cfg["sets"]["pic_pic"]
        cards = [{"kind": "pic", "img": b.item_img(i)} for i in ids] * 2
        sets.append({"letter": "A", "cards": cards})
    if "pic_word" in cfg["modes"]:
        ids = cfg["sets"]["pic_word"]
        cards = [{"kind": "pic", "img": b.item_img(i)} for i in ids]
        cards += [{"kind": "word", "he": b.items[i]["he"], "translit": b.items[i]["translit"],
                   "hint": b.item_img(i, "line")} for i in ids]
        sets.append({"letter": "B", "cards": cards})
    if cfg.get("bonus_days"):
        days = cfg["bonus_days"]
        cards = [{"kind": "day", "day": d["day"], "he": d["he"]} for d in days]
        cards += [{"kind": "pic", "img": b.item_img(d["item"])} for d in days]
        sets.append({"letter": "C", "cards": cards})
    for s in sets:
        if len(s["cards"]) != 12:
            raise ValueError(f"match set {s['letter']} has {len(s['cards'])} cards, expected 12")
    write_back_tile(b.build_dir / "back_tile.svg", b.palette[0], b.palette[1])
    html_path = b.render("match", "match.html", {"title": "Match-it", "sets": sets,
                                                  "back_tile": "back_tile.svg", "back_color": b.palette[0]})
    return html_path, {"match_sets": [s["letter"] for s in sets]}


# ---------------------------------------------------------------------------
# Listen & Do
# ---------------------------------------------------------------------------

def draw_listen_key(scene: Image.Image, objects: dict, steps: list, out_w: int = 1100) -> Image.Image:
    """Scene + 2 boxes, with what each direction should look like (tints, X marks, labels)."""
    w = out_w
    h = round(scene.height * w / scene.width)
    box_h = round(h * 0.42)
    canvas = Image.new("RGB", (w, h + box_h + 20), "white")
    canvas.paste(scene.convert("RGB").resize((w, h)), (0, 0))
    tint = Image.new("RGB", canvas.size, "white")
    tdraw = ImageDraw.Draw(tint)
    draw = ImageDraw.Draw(canvas)
    font = label_font(34)
    boxes = {"box_1": (10, h + 20, w // 2 - 15, h + box_h + 10), "box_2": (w // 2 + 15, h + 20, w - 10, h + box_h + 10)}

    def rect(obj_id):
        if obj_id in boxes:
            return boxes[obj_id]
        x, y, bw, bh = objects[obj_id]["pos"]
        return (x * w, y * h, (x + bw) * w, (y + bh) * h)

    marks = []
    for step in steps:
        for exp in step["expected"]:
            left, top, right, bottom = rect(exp["object"])
            if exp["action"] == "color":
                tdraw.ellipse((left, top, right, bottom), fill=CRAYON.get(exp["color"], exp["color"]))
            else:
                marks.append((exp, (left, top, right, bottom)))
    # multiply: the tint shows through the white areas, black lines stay black
    canvas = ImageChops.multiply(canvas, tint)
    draw = ImageDraw.Draw(canvas)
    for obj_id, box in boxes.items():
        draw.rectangle(box, outline="black", width=4)
        draw.text((box[0] + 14, box[1] + 8), obj_id[-1], fill="black", font=font)
    for exp, (left, top, right, bottom) in marks:
        cx, cy = (left + right) / 2, (top + bottom) / 2
        if exp["action"] == "mark":
            d = min(right - left, bottom - top) * 0.35
            draw.line((cx - d, cy - d, cx + d, cy + d), fill="#E53935", width=10)
            draw.line((cx - d, cy + d, cx + d, cy - d), fill="#E53935", width=10)
        else:
            label = exp.get("label", "draw")
            if exp["object"] == "cloud" and "rain" in label:
                cy = bottom + 40
            text_box = draw.textbbox((cx, cy), label, font=font, anchor="mm")
            pad = 8
            draw.rounded_rectangle((text_box[0] - pad, text_box[1] - pad, text_box[2] + pad, text_box[3] + pad),
                                   radius=10, fill="#FFF4D6", outline="#E0A526", width=4)
            draw.text((cx, cy), label, fill="#1E3A5F", font=font, anchor="mm")
    return canvas


def build_listen_do(b: Builder) -> tuple:
    cfg = b.data["listen_do"]
    scene_path = b.ensure_art("listen_do_scene", LISTEN_SCENE_PROMPT.format(scene=cfg["scene_prompt"]),
                              [], "4:3", line_art=True)
    scene = Image.open(scene_path).convert("RGB")
    shutil.copy(scene_path, b.build_dir / "listen_do_scene.png")
    objects = {o["id"]: o for o in cfg["objects"]}
    levels, keys = [], []
    for level in (1, 2):
        steps = [s for s in cfg["steps"] if s["level"] == level]
        label = ("Level 1 (one step, or two steps that go together)" if level == 1
                 else "Level 2 (two steps, then one 3-step direction)")
        levels.append({"label": label, "steps": [hebrew_html(s["text"]) for s in steps]})
        key_file = f"listen_do_key_{level}.jpg"
        draw_listen_key(scene, objects, steps).save(b.build_dir / key_file, quality=88)
        keys.append({"img": key_file, "label": f"Answer key, Level {level}"})
    words = [o for o in cfg["objects"] if o.get("he")]
    how_to = ("Read one direction at a time, slowly. When you say a Hebrew word, the children say it back "
              "(echo), then you say the English. At each “⏸ wait”, stop until everyone is done. "
              "Use Level 1 with younger children; Level 2 when they are ready. Each level uses a fresh copy.")
    html_path = b.render("listen_do", "listen_do.html", {
        "title": "Listen & Do", "scene": "listen_do_scene.png", "levels": levels,
        "answer_keys": keys, "how_to": how_to, "words": words})
    return html_path, {"listen_do_steps": len(cfg["steps"])}


# ---------------------------------------------------------------------------
# HTML -> PDF -> PNG preview
# ---------------------------------------------------------------------------

CHECK_LAYOUT_JS = """
async () => {
  await document.fonts.ready;
  // Ask for each web font explicitly (browsers only load fonts a page uses)
  await Promise.all(['700 20px Heebo', '600 20px Fredoka', '400 20px Assistant'].map(f => document.fonts.load(f)));
  const problems = [];
  document.querySelectorAll('.page').forEach((page, i) => {
    if (page.scrollHeight > page.clientHeight + 1) problems.push(`page ${i + 1}: content taller than the page`);
    page.querySelectorAll('.cell, .call, .card, .k, .howto, .box').forEach(el => {
      if (el.scrollHeight > el.clientHeight + 2 || el.scrollWidth > el.clientWidth + 2)
        problems.push(`page ${i + 1}: ${el.className} overflows (${el.scrollWidth}x${el.scrollHeight} > ${el.clientWidth}x${el.clientHeight})`);
    });
  });
  const fonts = {heebo: document.fonts.check('700 20px Heebo'), fredoka: document.fonts.check('600 20px Fredoka'),
                 assistant: document.fonts.check('400 20px Assistant')};
  return {problems, fonts, pages: document.querySelectorAll('.page').length};
}
"""


def html_to_pdf(html_paths: dict, out_dir: Path) -> dict:
    """Print each HTML file to {name}.pdf with headless Chrome. Returns layout reports per name."""
    from playwright.sync_api import sync_playwright
    reports = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for name, html_path in html_paths.items():
            page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
            report = page.evaluate(CHECK_LAYOUT_JS)
            pdf_path = out_dir / f"{name}.pdf"
            page.pdf(path=str(pdf_path), width="8.5in", height="11in", print_background=True,
                     margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}, prefer_css_page_size=True)
            report["pdf"] = pdf_path
            reports[name] = report
            for problem in report["problems"]:
                logger.warning(f"  {name}: {problem}")
            if not all(report["fonts"].values()):
                logger.warning(f"  {name}: web fonts not loaded {report['fonts']} (offline?) — system fonts used")
            logger.info(f"  {name}.pdf: {report['pages']} pages ({pdf_path.stat().st_size // 1024} KB)")
        browser.close()
    return reports


def save_previews(pdf_path: Path, out_path: Path, all_pages_dir: Path = None) -> None:
    """Page 1 of the PDF as a PNG (and every page, if all_pages_dir is given)."""
    import fitz  # PyMuPDF
    with fitz.open(pdf_path) as doc:
        first = doc[0].get_pixmap(dpi=PREVIEW_DPI)
        # 256-color PNG: a quarter of the size, still fine for a quick look
        Image.frombytes("RGB", (first.width, first.height), first.samples).quantize(256).save(
            out_path, optimize=True)
        if all_pages_dir:
            all_pages_dir.mkdir(parents=True, exist_ok=True)
            for number, page in enumerate(doc, 1):
                page.get_pixmap(dpi=PREVIEW_DPI).save(all_pages_dir / f"{pdf_path.stem}_p{number}.png")


BUILDERS = {"bingo": build_bingo, "ispy": build_ispy, "match": build_match, "listen_do": build_listen_do}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Build printable extras PDFs for a deck")
    parser.add_argument("deck_dir")
    parser.add_argument("--only", help=f"Comma-separated subset of {','.join(ACTIVITIES)}")
    parser.add_argument("--no-ai", action="store_true", help="Never call the image API (fail if art is missing)")
    parser.add_argument("--all-previews", help="Also write every page as a PNG into this folder")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    setup_logging()
    args = parse_args(argv)
    deck_dir = Path(args.deck_dir).resolve()
    builder = Builder(deck_dir, use_ai=not args.no_ai)
    wanted = args.only.split(",") if args.only else list(ACTIVITIES)
    unknown = set(wanted) - set(ACTIVITIES)
    if unknown:
        raise SystemExit(f"Unknown activities: {sorted(unknown)}")

    html_paths, summary = {}, {}
    for name in wanted:
        logger.info(f"Building {name}")
        try:
            html_path, report = BUILDERS[name](builder)
        except Exception as error:  # one broken activity shouldn't stop the others
            logger.error(f"{name}: {error}")
            continue
        html_paths[name] = html_path
        summary.update(report)

    reports = html_to_pdf(html_paths, builder.out_dir)
    all_dir = Path(args.all_previews) if args.all_previews else None
    for name, report in reports.items():
        save_previews(report["pdf"], builder.preview_dir / f"{name}_p1.png", all_dir)
    for warning in builder.warnings:
        logger.warning(warning)
    logger.info("Summary: " + json.dumps(summary, default=str))
    failed = set(wanted) - set(reports)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
