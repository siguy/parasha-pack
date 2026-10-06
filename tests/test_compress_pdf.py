"""Tests for scripts/compress_pdf.py. Run from the repo root:  python3 -m pytest tests -q"""

import sys
from pathlib import Path

from PIL import Image
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from compress_pdf import compress_pdf, main  # noqa: E402


def _png_pdf(path, size=(400, 300)):
    """A one-page PDF holding a lossless picture, like the Playwright export.

    Pillow would store an RGB image as JPEG already, so we use a palette ("P")
    image: Pillow stores that losslessly, and it also exercises the
    convert-to-RGB step.
    """
    width, height = size
    img = Image.new("RGB", size)
    img.putdata([(x * 255 // width, y * 255 // height, 120) for y in range(height) for x in range(width)])
    img.quantize(256).save(path, "PDF")
    return path


def _image_sizes(path):
    return [im.image.size for page in PdfReader(path).pages for im in page.images]


def test_smaller_and_same_pixel_size(tmp_path):
    pdf = _png_pdf(tmp_path / "card.pdf")
    before_bytes = pdf.stat().st_size
    before_sizes = _image_sizes(pdf)
    page_before = PdfReader(pdf).pages[0].mediabox

    assert compress_pdf(pdf, quality=88) == 1

    assert pdf.stat().st_size < before_bytes
    assert _image_sizes(pdf) == before_sizes == [(400, 300)]
    assert PdfReader(pdf).pages[0].mediabox == page_before
    assert list(tmp_path.iterdir()) == [pdf]   # temp file cleaned up


def test_missing_file_is_skipped(tmp_path):
    assert main([str(tmp_path / "nope.pdf")]) == 0


def test_keeps_original_when_jpeg_would_be_bigger(tmp_path):
    """Pure black-and-white line art: JPEG is bigger than the PNG, so the file must not change."""
    from PIL import Image, ImageDraw
    import compress_pdf as cp
    img = Image.new("L", (600, 600), 255)
    draw = ImageDraw.Draw(img)
    for x in range(0, 600, 20):
        draw.line([(x, 0), (600 - x, 600)], fill=0, width=3)
    pdf = tmp_path / "lineart.pdf"
    img.convert("1").save(pdf, "PDF")
    before = pdf.read_bytes()
    cp.compress_pdf(pdf, quality=88)
    assert pdf.read_bytes() == before
