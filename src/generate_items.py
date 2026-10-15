"""
Item art for the printable extras (bingo, I-spy, match-it): one picture per vocab word.

For every item in decks/{id}/extras.yaml we make three files:

    color.png   the item in the series style, alone on white (1 AI call, 1K)
    line.png    a coloring-page version: pure black lines on white
                (1 AI *edit* call that redraws color.png as line art, then Pillow
                 cleans it to exactly two colors)
    cutout.png  color.png with the white background made transparent and cropped,
                so it can be stuck onto the I-spy picture like a sticker

Files already on disk are reused, so running this twice costs nothing the second time.
Use --redo to throw one picture away and make it again.

Usage (from src/):
    python generate_items.py ../decks/bereshit
    python generate_items.py ../decks/bereshit --only fish,snake
    python generate_items.py ../decks/bereshit --redo snake:color   # also remakes its line art
    python generate_items.py ../decks/bereshit --redo fish:line
    python generate_items.py ../decks/bereshit --dry-run            # show what would be called
    python generate_items.py ../decks/bereshit --contact-sheet out.png
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

import extras_data
import spend_ledger
from generate_images import _load_image_as_part, generate_image_nano_banana

logger = logging.getLogger("generate_items")

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECT_LOG = REPO_ROOT / "project.log"
STYLE_PLATE = REPO_ROOT / "style" / "plates" / "object.png"

ITEM_SIZE = "1K"
ITEM_ASPECT = "1:1"

COLOR_PROMPT = """=== REFERENCE IMAGES ===
Image 1: style plate 'object' (match art style only, not content). Do NOT copy its wall, candles or bread unless asked below.

=== WHAT TO DRAW ===
{item_prompt}.
A single isolated item, centered, filling about 75% of the square frame, on a plain pure white background.

=== STYLE ===
The same children's cartoon style as Image 1: thick clean dark outlines, flat bright colors with soft gentle shading,
rounded friendly shapes, warm and inviting. Clean crisp illustration with no grain or texture.
Friendly and age-appropriate for children ages 4-6.

=== RULES ===
Only ONE item. No background scenery, no ground, no cast shadow, no border or frame.
Do NOT render any text, letters, numbers or Hebrew anywhere in the image."""

LINE_PROMPT = """Convert this picture into a coloring-page line drawing for young children.
Thick bold black outlines only, pure white fill everywhere, no shading, no gray, no color, no texture, no hatching.
Keep exactly the same single object, shape and pose, centered on a plain white background.
Close every outline so each area can be colored in. Do NOT add any text, letters or numbers."""


def setup_logging() -> None:
    """Print INFO+ to the console and append ERROR+ to project.log (same as generate_images)."""
    root = logging.getLogger()
    if root.handlers:
        return
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(message)s"))
    error_file = logging.FileHandler(PROJECT_LOG, delay=True)
    error_file.setLevel(logging.ERROR)
    error_file.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    root.setLevel(logging.INFO)
    root.addHandler(console)
    root.addHandler(error_file)


# ---------------------------------------------------------------------------
# Image clean-up (no AI, fully testable)
# ---------------------------------------------------------------------------

def binarize_line_art(img: Image.Image, threshold: int = 200, thicken: int = 3) -> Image.Image:
    """
    Turn a grayish line drawing into pure black-and-white.

    Every pixel darker than `threshold` becomes black, everything else white. Then the
    black lines are thickened a little (a "min filter" spreads dark pixels outward), so
    thin lines survive photocopying. Returns an "L" image with only the values 0 and 255.
    """
    gray = ImageOps.grayscale(img.convert("RGB"))
    bw = gray.point(lambda v: 0 if v < threshold else 255)
    if thicken and thicken > 1:
        bw = bw.filter(ImageFilter.MinFilter(thicken))
    return bw


def make_cutout(img: Image.Image, white_level: int = 235, pad: int = 8) -> Image.Image:
    """
    Make a sticker: the white background becomes transparent, then crop to the item.

    Only white that touches the edge of the picture is removed (a flood fill from the
    border), so white INSIDE the item — the white of an eye, a candle — stays white.
    """
    rgb = img.convert("RGB")
    gray = ImageOps.grayscale(rgb)
    # 255 = "near white", 0 = "part of the item"
    mask = gray.point(lambda v: 255 if v >= white_level else 0)
    # Flood fill near-white from a frame of border points with the value 128
    w, h = mask.size
    step = max(1, min(w, h) // 64)
    border = ([(x, 0) for x in range(0, w, step)] + [(x, h - 1) for x in range(0, w, step)]
              + [(0, y) for y in range(0, h, step)] + [(w - 1, y) for y in range(0, h, step)])
    for point in border:
        if mask.getpixel(point) == 255:
            ImageDraw.floodfill(mask, point, 128)
    # Background (128) -> transparent; everything else opaque. Soften the edge by 1px.
    alpha = mask.point(lambda v: 0 if v == 128 else 255).filter(ImageFilter.MaxFilter(3))
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.8))
    cutout = rgb.convert("RGBA")
    cutout.putalpha(alpha)
    box = alpha.point(lambda v: 255 if v > 16 else 0).getbbox()
    if box:
        left, top, right, bottom = box
        cutout = cutout.crop((max(0, left - pad), max(0, top - pad), min(w, right + pad), min(h, bottom + pad)))
    return cutout


def content_bbox(img: Image.Image, white_level: int = 235):
    """Bounding box of the non-white part of an image (None if all white)."""
    gray = ImageOps.grayscale(img.convert("RGB"))
    return gray.point(lambda v: 255 if v < white_level else 0).getbbox()


def crop_to_content(img: Image.Image, pad: int = 8) -> Image.Image:
    box = content_bbox(img)
    if not box:
        return img
    w, h = img.size
    left, top, right, bottom = box
    return img.crop((max(0, left - pad), max(0, top - pad), min(w, right + pad), min(h, bottom + pad)))


# ---------------------------------------------------------------------------
# AI calls
# ---------------------------------------------------------------------------

def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set (set -a; source .env; set +a)")
    return key


def request_image(prompt: str, out_path: Path, refs: list, size: str, aspect: str,
                  purpose: str, dry_run: bool = False) -> bool:
    """One image call through the shared generator (spend ledger + budget check included)."""
    if dry_run:
        logger.info(f"  [dry-run] would call {size} {aspect}: {purpose} -> {out_path}")
        return False
    out_path.parent.mkdir(parents=True, exist_ok=True)
    parts = [_load_image_as_part(Path(r)) for r in refs]
    result = generate_image_nano_banana(prompt, get_api_key(), str(out_path), aspect_ratio=aspect,
                                        reference_images=parts, image_size=size, purpose=purpose)
    if not result["success"]:
        logger.error(f"  Image call failed: {purpose}")
    return result["success"]


def build_item(item: dict, deck_dir: Path, deck_id: str, redo: set, dry_run: bool) -> dict:
    """Make (or reuse) color.png, line.png and cutout.png for one item. Returns a status dict."""
    folder = extras_data.item_dir(item, deck_dir)
    color, line, cutout = folder / "color.png", folder / "line.png", folder / "cutout.png"
    status = {"id": item["id"], "calls": 0, "folder": folder}

    if f"{item['id']}:color" in redo:
        for path in (color, line, cutout):
            path.unlink(missing_ok=True)
    if f"{item['id']}:line" in redo:
        line.unlink(missing_ok=True)

    if not color.exists():
        prompt = COLOR_PROMPT.format(item_prompt=item["item_prompt"])
        status["calls"] += 1
        if not request_image(prompt, color, [STYLE_PLATE], ITEM_SIZE, ITEM_ASPECT,
                             f"{deck_id} extras item {item['id']} color", dry_run):
            return status
        cutout.unlink(missing_ok=True)

    if not cutout.exists() and color.exists():
        make_cutout(Image.open(color)).save(cutout, optimize=True)

    if not line.exists() and color.exists():
        raw = folder / "line_raw.tmp.png"
        status["calls"] += 1
        if not request_image(LINE_PROMPT, raw, [color], ITEM_SIZE, ITEM_ASPECT,
                             f"{deck_id} extras item {item['id']} line edit", dry_run):
            return status
        binarize_line_art(Image.open(raw)).convert("1").save(line, optimize=True)
        raw.unlink(missing_ok=True)
    status["done"] = color.exists() and line.exists() and cutout.exists()
    return status


# ---------------------------------------------------------------------------
# Contact sheet
# ---------------------------------------------------------------------------

def make_contact_sheet(items: list, deck_dir: Path, out_path: Path, tile: int = 220) -> Path:
    """One row per pair of items: color | line, with the item id under each pair."""
    cols = 4  # 4 items per row, each item = color + line tiles
    rows = (len(items) + cols - 1) // cols
    label_h = 26
    sheet = Image.new("RGB", (cols * tile * 2 + (cols + 1) * 12, rows * (tile + label_h + 12) + 12), "#e7e2d9")
    draw = ImageDraw.Draw(sheet)
    for index, item in enumerate(items):
        folder = extras_data.item_dir(item, deck_dir)
        x = 12 + (index % cols) * (tile * 2 + 12)
        y = 12 + (index // cols) * (tile + label_h + 12)
        for offset, name in enumerate(("color.png", "line.png")):
            path = folder / name
            cell = Image.new("RGB", (tile, tile), "white")
            if path.exists():
                pic = Image.open(path).convert("RGB")
                pic.thumbnail((tile, tile))
                cell.paste(pic, ((tile - pic.width) // 2, (tile - pic.height) // 2))
            else:
                ImageDraw.Draw(cell).text((10, 10), f"missing {name}", fill="red")
            sheet.paste(cell, (x + offset * tile, y))
        draw.text((x + 4, y + tile + 6), f"{item['id']}  {item['en']}", fill="#1e293b")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    logger.info(f"Contact sheet: {out_path} ({len(items)} items)")
    return out_path


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Make item art (color, line, cutout) for a deck's extras")
    parser.add_argument("deck_dir", help="Deck folder with extras.yaml, e.g. ../decks/bereshit")
    parser.add_argument("--only", help="Comma-separated item ids (default: all)")
    parser.add_argument("--redo", default="", help="Comma-separated id:color or id:line to remake")
    parser.add_argument("--dry-run", action="store_true", help="Show the calls, make none")
    parser.add_argument("--contact-sheet", help="Write a contact sheet PNG to this path")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    setup_logging()
    args = parse_args(argv)
    deck_dir = Path(args.deck_dir).resolve()
    data = extras_data.load_extras(deck_dir)
    items = extras_data.all_items(data)
    if args.only:
        wanted = set(args.only.split(","))
        items = [item for item in items if item["id"] in wanted]
    redo = {r for r in args.redo.split(",") if r}

    spent_before = spend_ledger.total_spent()
    calls = 0
    for item in items:
        logger.info(f"Item {item['id']} ({item['en']})")
        status = build_item(item, deck_dir, data["deck_id"], redo, args.dry_run)
        calls += status["calls"]
        if not status.get("done") and not args.dry_run:
            logger.warning(f"  {item['id']} is incomplete; continuing with the next item")
    spent = spend_ledger.total_spent() - spent_before
    logger.info(f"Items: {len(items)} processed, {calls} image calls, ${spent:.3f} recorded this run")

    if args.contact_sheet:
        make_contact_sheet(extras_data.all_items(data), deck_dir, Path(args.contact_sheet))
    return 0


if __name__ == "__main__":
    sys.exit(main())
