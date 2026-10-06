"""
Story line art and cut-sheet geometry for the coloring + sequencing extras.

Two jobs, both small:

1. Turn a story card's finished art (decks/{id}/raw/story_N.png) into a coloring page.
   One Gemini *edit* call redraws the picture as thick black outlines on white (1K),
   then Pillow cleans it up exactly like the item line art: grayscale -> threshold
   -> thicken the lines. The result is saved once to decks/{id}/extras/art/coloring/
   and reused on every later run (like a photocopy master).

2. Work out where the cut lines go on a page of cards (a "grid": columns x rows of
   equal boxes that share their edges). The templates draw the boxes from these
   numbers, and the tests check them, so a panel that should be 3.75" wide really is.

Usage (from src/):
    python coloring.py ../decks/bereshit                    # make any missing line art
    python coloring.py ../decks/bereshit --redo story_2     # remake one (costs 1 call)
    python coloring.py ../decks/bereshit --contact-sheet /tmp/sheet.png
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from generate_items import binarize_line_art, request_image, setup_logging

logger = logging.getLogger("coloring")

LINE_ART_SIZE = "1K"
LINE_ART_ASPECT = "3:4"   # the story art is 1792 x 2400 = 3:4
THRESHOLD = 200
THICKEN = 5               # MinFilter size: spreads each black line ~2px on every side

LINE_ART_PROMPT = """Convert this picture into a children's coloring page for ages 4-6.
Thick bold black outlines only, at least 8 pixels wide. Pure white fill everywhere.
No shading, no gray, no color, no texture, no hatching, no tiny details.
Use at most 12 large, simple, closed regions that a small child can color with a crayon.
Simplify the background a lot: keep only its few biggest shapes. Never add anything that is not
already in the picture (no new hills, river, ground, sun, moon or clouds).
Keep the main characters, animals and objects recognizable, in the same places and poses.
Close every outline so each area can be colored in. Do NOT add any text, letters, numbers or border."""


# ---------------------------------------------------------------------------
# Line art
# ---------------------------------------------------------------------------

def line_art_prompt(card: dict, hint: str = "") -> str:
    """The line-art prompt, plus the card's `exclude` list (text fidelity: e.g. no sun before Day 4)."""
    prompt = LINE_ART_PROMPT
    if card.get("exclude"):
        prompt += "\nThis picture must NOT contain: " + "; ".join(card["exclude"]) + "."
    return prompt + (f"\n{hint}" if hint else "")


def line_art_path(deck_dir: Path, card_id: str) -> Path:
    return Path(deck_dir) / "extras" / "art" / "coloring" / f"{card_id}.png"


def clean_line_art(img: Image.Image) -> Image.Image:
    """Grayscale -> pure black/white at THRESHOLD -> thicker lines. Returns a 1-bit image."""
    return binarize_line_art(img, threshold=THRESHOLD, thicken=THICKEN).convert("1")


def ensure_line_art(deck_dir: Path, card: dict, deck_id: str, use_ai: bool = True, redo: bool = False,
                    hint: str = "") -> Path:
    """Return the coloring-page version of a story card, making it (1 AI call) if missing.

    hint: an extra sentence for a redo (e.g. "keep only the 4 biggest animals").
    """
    out = line_art_path(deck_dir, card["card_id"])
    if redo:
        out.unlink(missing_ok=True)
    if out.exists():
        return out
    if not use_ai:
        raise FileNotFoundError(f"{out} is missing and AI calls are off")
    source = Path(deck_dir) / card["image_path"]
    if not source.exists():
        raise FileNotFoundError(f"Story art {source} is missing")
    raw = out.with_suffix(".raw.png")
    prompt = line_art_prompt(card, hint)
    ok = request_image(prompt, raw, [source], LINE_ART_SIZE, LINE_ART_ASPECT,
                       f"{deck_id} extras coloring {card['card_id']} line edit")
    if not ok:
        raise RuntimeError(f"Line-art call failed for {card['card_id']}")
    clean_line_art(Image.open(raw)).save(out, optimize=True)
    raw.unlink(missing_ok=True)
    logger.info(f"  {card['card_id']}: line art saved to {out}")
    return out


def count_regions(img: Image.Image, min_area_frac: float = 0.002, work_px: int = 300) -> int:
    """
    Count the white areas a child would color (a quick check of "≤12 large regions").

    The picture is shrunk to ~300 px, then every white area is flood-filled one at a
    time; areas smaller than min_area_frac of the picture (specks) are not counted.
    """
    small = img.convert("L")
    small.thumbnail((work_px, work_px))
    bw = small.point(lambda v: 255 if v >= 128 else 0)
    w, h = bw.size
    pixels = bw.load()
    min_area = max(1, int(w * h * min_area_frac))
    seen = bytearray(w * h)
    regions = 0
    for y in range(h):
        for x in range(w):
            if pixels[x, y] != 255 or seen[y * w + x]:
                continue
            stack, area = [(x, y)], 0          # iterative flood fill
            seen[y * w + x] = 1
            while stack:
                cx, cy = stack.pop()
                area += 1
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx] and pixels[nx, ny] == 255:
                        seen[ny * w + nx] = 1
                        stack.append((nx, ny))
            if area >= min_area:
                regions += 1
    return regions


def contact_sheet(pairs: list, out_path: Path, tile_h: int = 520) -> Path:
    """One row per story card: original art | line art, with the card id and region count."""
    label_h = 34
    tile_w = round(tile_h * 3 / 4)
    sheet = Image.new("RGB", (2 * tile_w + 36, len(pairs) * (tile_h + label_h + 12) + 12), "#e7e2d9")
    draw = ImageDraw.Draw(sheet)
    for row, (card_id, original, line) in enumerate(pairs):
        y = 12 + row * (tile_h + label_h + 12)
        for col, path in enumerate((original, line)):
            cell = Image.new("RGB", (tile_w, tile_h), "white")
            pic = Image.open(path).convert("RGB")
            pic.thumbnail((tile_w, tile_h))
            cell.paste(pic, ((tile_w - pic.width) // 2, (tile_h - pic.height) // 2))
            sheet.paste(cell, (12 + col * (tile_w + 12), y))
        regions = count_regions(Image.open(line))
        draw.text((16, y + tile_h + 8), f"{card_id}   regions ~ {regions}", fill="#1e293b")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    return out_path


# ---------------------------------------------------------------------------
# Cut-sheet geometry (inches)
# ---------------------------------------------------------------------------

def grid_cells(cols: int, rows: int, cell_w: float, cell_h: float, left: float = 0.0, top: float = 0.0) -> list:
    """Boxes of a cut grid, row by row: [{'col', 'row', 'x', 'y', 'w', 'h'}] in inches."""
    return [{"col": c, "row": r, "x": round(left + c * cell_w, 4), "y": round(top + r * cell_h, 4),
             "w": cell_w, "h": cell_h}
            for r in range(rows) for c in range(cols)]


def cut_lines(cols: int, rows: int, cell_w: float, cell_h: float, left: float = 0.0, top: float = 0.0) -> list:
    """
    Every straight cut line of the grid as (x1, y1, x2, y2), in inches.

    Neighbouring boxes share one line, so a grid has (cols + 1) vertical and
    (rows + 1) horizontal lines, each running the full width or height.
    """
    right, bottom = round(left + cols * cell_w, 4), round(top + rows * cell_h, 4)
    vertical = [(round(left + c * cell_w, 4), top, round(left + c * cell_w, 4), bottom) for c in range(cols + 1)]
    horizontal = [(left, round(top + r * cell_h, 4), right, round(top + r * cell_h, 4)) for r in range(rows + 1)]
    return vertical + horizontal


def cell_cut_lines(cells: list) -> list:
    """
    The straight cut lines around a set of boxes that need not fill a whole grid (e.g. 7 boxes
    in a 4 x 2 grid), as (x1, y1, x2, y2) in inches.

    Every box edge is collected, edges on the same line are joined when they touch, so two
    neighbours still share one line and a row of boxes gets one long cut instead of many short ones.
    """
    horizontal, vertical = {}, {}
    for c in cells:
        x1, y1 = round(c["x"], 4), round(c["y"], 4)
        x2, y2 = round(c["x"] + c["w"], 4), round(c["y"] + c["h"], 4)
        for y in (y1, y2):
            horizontal.setdefault(y, []).append((x1, x2))
        for x in (x1, x2):
            vertical.setdefault(x, []).append((y1, y2))

    def joined(spans: list) -> list:
        out = []
        for start, end in sorted(spans):
            if out and start <= out[-1][1] + 1e-6:
                out[-1] = (out[-1][0], max(out[-1][1], end))
            else:
                out.append((start, end))
        return out

    lines = [(x, a, x, b) for x, spans in sorted(vertical.items()) for a, b in joined(spans)]
    lines += [(a, y, b, y) for y, spans in sorted(horizontal.items()) for a, b in joined(spans)]
    return lines


def fits_on_page(cells: list, page_w: float = 8.5, page_h: float = 11.0, margin: float = 0.25) -> bool:
    """True if every box stays inside the printable area (page minus margin on each side)."""
    return all(c["x"] >= margin - 1e-6 and c["y"] >= margin - 1e-6
               and c["x"] + c["w"] <= page_w - margin + 1e-6 and c["y"] + c["h"] <= page_h - margin + 1e-6
               for c in cells)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def story_cards(deck: dict, card_ids: list) -> list:
    by_id = {c["card_id"]: c for c in deck["cards"]}
    return [by_id[i] for i in card_ids]


def main(argv=None) -> int:
    import extras_data
    setup_logging()
    parser = argparse.ArgumentParser(description="Make coloring-page line art for a deck's story cards")
    parser.add_argument("deck_dir")
    parser.add_argument("--redo", default="", help="Comma-separated card ids to remake")
    parser.add_argument("--hint", default="", help="Extra prompt sentence for the cards in --redo")
    parser.add_argument("--contact-sheet", help="Write original | line art contact sheet here")
    args = parser.parse_args(argv)
    deck_dir = Path(args.deck_dir).resolve()
    deck = json.loads((deck_dir / "deck.json").read_text(encoding="utf-8"))
    data = extras_data.load_extras(deck_dir)
    redo = {r for r in args.redo.split(",") if r}
    pairs = []
    for card in story_cards(deck, data["coloring"]["cards"]):
        try:
            path = ensure_line_art(deck_dir, card, data["deck_id"], redo=card["card_id"] in redo,
                                   hint=args.hint if card["card_id"] in redo else "")
        except Exception as error:  # one failed card shouldn't stop the others
            logger.error(f"{card['card_id']}: {error}")
            continue
        logger.info(f"  {card['card_id']}: {path.name}, about {count_regions(Image.open(path))} regions")
        pairs.append((card["card_id"], deck_dir / card["image_path"], path))
    if args.contact_sheet:
        logger.info(f"Contact sheet: {contact_sheet(pairs, Path(args.contact_sheet))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
