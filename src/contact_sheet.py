#!/usr/bin/env python3
"""
Make a contact sheet: many images in one grid, each with a label underneath.

Used by Image QA (agent 05b) to compare drafts side by side, and for identity-sheet reviews.
Like the proof sheets photographers print: one page, every shot, a number under each.

Usage:
    from contact_sheet import make_contact_sheet
    make_contact_sheet(["raw/drafts/story_1_d1.png", "raw/drafts/story_1_d2.png"],
                       ["story_1 d1", "story_1 d2"], "raw/drafts/contact_sheet.png", cols=4)

    # Command line (labels = file names):
    python3 src/contact_sheet.py out.png decks/bereshit/raw/drafts/*.png --cols 4
"""

import argparse
import logging
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("contact_sheet")

THUMB_WIDTH = 360        # each tile's image width in px (3:4 art -> 480 px tall)
LABEL_HEIGHT = 36
GAP = 16
BACKGROUND = "white"
MISSING_TILE = "#DDDDDD"  # grey box when an image can't be opened


def _font(size: int):
    """A readable TrueType font if one is installed, else Pillow's built-in one."""
    for name in ("Arial.ttf", "Helvetica.ttc", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _thumbnail(path: Path, width: int) -> Image.Image:
    """Open an image and scale it to `width`, keeping its shape. Grey tile if it can't be read."""
    try:
        with Image.open(path) as img:
            img = img.convert("RGB")
            height = round(img.height * width / img.width)
            return img.resize((width, height), Image.LANCZOS)
    except (OSError, ValueError) as e:
        logger.warning(f"Could not open {path}: {e}; using a grey tile")
        return Image.new("RGB", (width, round(width * 4 / 3)), MISSING_TILE)


def make_contact_sheet(paths, labels, out_path, cols: int = 4, thumb_width: int = THUMB_WIDTH) -> Path:
    """Lay the images out in a grid with a label under each, and save to out_path.

    Args:
        paths: image files, in reading order (left to right, top to bottom)
        labels: one label per image (same length as paths)
        out_path: where to save the sheet (.png or .jpg)
        cols: images per row
        thumb_width: width of each image in the sheet, in pixels

    Returns:
        Path of the saved sheet.
    """
    paths = [Path(p) for p in paths]
    labels = list(labels)
    if not paths:
        raise ValueError("make_contact_sheet needs at least one image")
    if len(labels) != len(paths):
        raise ValueError(f"{len(paths)} images but {len(labels)} labels")
    if cols < 1:
        raise ValueError("cols must be at least 1")

    thumbs = [_thumbnail(p, thumb_width) for p in paths]
    tile_h = max(t.height for t in thumbs) + LABEL_HEIGHT
    cols = min(cols, len(thumbs))
    rows = -(-len(thumbs) // cols)  # ceiling division
    sheet = Image.new("RGB", (GAP + cols * (thumb_width + GAP), GAP + rows * (tile_h + GAP)), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    font = _font(20)

    for i, (thumb, label) in enumerate(zip(thumbs, labels)):
        x = GAP + (i % cols) * (thumb_width + GAP)
        y = GAP + (i // cols) * (tile_h + GAP)
        sheet.paste(thumb, (x, y))
        draw.text((x + 4, y + thumb.height + 8), str(label), fill="black", font=font)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    logger.info(f"Contact sheet: {len(thumbs)} images, {rows}x{cols} -> {out_path}")
    return out_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Make a labeled contact sheet from images")
    parser.add_argument("out", help="Output image, e.g. decks/bereshit/raw/drafts/contact_sheet.png")
    parser.add_argument("images", nargs="+", help="Images to include (label = file name)")
    parser.add_argument("--cols", type=int, default=4)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    make_contact_sheet(args.images, [Path(p).stem for p in args.images], args.out, cols=args.cols)
    return 0


if __name__ == "__main__":
    sys.exit(main())
