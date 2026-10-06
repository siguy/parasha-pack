"""Shrink a print PDF by re-encoding its embedded pictures as JPEG.

Why this exists
---------------
The Card Designer export (Playwright's page.pdf) embeds every card's artwork
as a lossless PNG. A 20-page deck PDF ends up around 57 MB: too big for
GitHub (it warns at 50 MB) and slow to download.

Think of PNG as a photocopy that keeps every speck exactly, and JPEG as a
very good photo: for painted artwork the eye can't tell them apart, but the
JPEG is a fraction of the size. Text in the PDF is not an image (it stays
sharp vector text), so only the artwork changes.

What it does
------------
For every image on every page: decode it, convert it to RGB if needed, and
put it back as a JPEG with the SAME pixel width and height. Same pixels on
the same page size means the print resolution (DPI) doesn't change. Then
duplicate copies of identical images are merged and unused objects dropped.
The file is rewritten in place through a temp file, so a crash never leaves
a half-written PDF behind.

Usage (from the repo root):
    python3 scripts/compress_pdf.py decks/bereshit/print/bereshit-letter.pdf
    python3 scripts/compress_pdf.py a.pdf b.pdf --quality 85

Errors also go to project.log. A missing file is a warning, not a crash.
"""

import argparse
import logging
import os
import sys
import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECT_LOG = REPO_ROOT / "project.log"
DEFAULT_QUALITY = 88

logger = logging.getLogger("compress_pdf")


def _mb(path: Path) -> float:
    return path.stat().st_size / 1_000_000


def compress_pdf(path: Path, quality: int = DEFAULT_QUALITY) -> int:
    """Re-encode every embedded image in `path` as JPEG. Returns the image count.

    The file is replaced only after the new version was written completely.
    """
    path = Path(path)
    writer = PdfWriter(clone_from=PdfReader(path))

    count = 0
    for page in writer.pages:
        for image_file in page.images:
            picture = image_file.image
            # JPEG can only hold RGB (colour) or L (greyscale) pixels;
            # anything else (RGBA, palette "P", CMYK...) becomes RGB.
            if picture.mode not in ("RGB", "L"):
                picture = picture.convert("RGB")
            image_file.replace(picture, quality=quality)
            count += 1

    # The same picture used twice is stored once; leftovers are removed.
    writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)

    # Write next to the original, then swap it in (atomic on the same disk).
    fd, tmp_name = tempfile.mkstemp(suffix=".pdf", dir=path.parent)
    os.close(fd)
    try:
        with open(tmp_name, "wb") as f:
            writer.write(f)
        # Black-and-white line art is smaller as PNG than as JPEG: never make a file bigger.
        if os.path.getsize(tmp_name) >= path.stat().st_size:
            logger.info(f"{path.name}: re-encoding would not shrink it; keeping the original")
            return 0
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
    return count


def _setup_logging() -> None:
    """INFO to the console, ERROR+ also to project.log."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    error_file = logging.FileHandler(PROJECT_LOG, delay=True)
    error_file.setLevel(logging.ERROR)
    error_file.setFormatter(logging.Formatter("%(asctime)s compress_pdf %(levelname)s %(message)s"))
    logging.getLogger().addHandler(error_file)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Re-encode a PDF's images as JPEG (same pixel size) to shrink it.")
    parser.add_argument("pdfs", nargs="+", help="PDF file(s) to compress in place")
    parser.add_argument("--quality", type=int, default=DEFAULT_QUALITY,
                        help=f"JPEG quality 1-95 (default {DEFAULT_QUALITY})")
    args = parser.parse_args(argv)
    _setup_logging()

    failures = 0
    for name in args.pdfs:
        path = Path(name)
        if not path.exists():
            logger.warning(f"Skipping {path}: file not found")
            continue
        before = _mb(path)
        try:
            count = compress_pdf(path, args.quality)
        except Exception as error:  # keep going with the other files
            logger.error(f"Could not compress {path}: {error}")
            failures += 1
            continue
        logger.info(f"{path}: {count} images re-encoded at quality {args.quality}, "
                    f"{before:.1f} MB -> {_mb(path):.1f} MB")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
