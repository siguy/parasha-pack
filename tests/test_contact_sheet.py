"""Tests for src/contact_sheet.py. Run from the repo root:  python3 -m pytest tests -q"""

import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from contact_sheet import GAP, LABEL_HEIGHT, main, make_contact_sheet  # noqa: E402


def _images(tmp_path, n, size=(300, 400)):
    paths = []
    for i in range(n):
        path = tmp_path / f"img_{i}.png"
        Image.new("RGB", size, (40 * i % 255, 120, 200)).save(path)
        paths.append(path)
    return paths


def test_grid_size(tmp_path):
    paths = _images(tmp_path, 5)
    out = make_contact_sheet(paths, [p.stem for p in paths], tmp_path / "sheet.png", cols=3, thumb_width=150)
    with Image.open(out) as sheet:
        tile_h = 200 + LABEL_HEIGHT   # 300x400 scaled to width 150 -> 200 tall
        assert sheet.size == (GAP + 3 * (150 + GAP), GAP + 2 * (tile_h + GAP))


def test_fewer_images_than_cols_shrinks_width(tmp_path):
    paths = _images(tmp_path, 2)
    out = make_contact_sheet(paths, ["a", "b"], tmp_path / "sheet.png", cols=4, thumb_width=100)
    with Image.open(out) as sheet:
        assert sheet.width == GAP + 2 * (100 + GAP)


def test_unreadable_image_becomes_grey_tile(tmp_path):
    paths = _images(tmp_path, 1)
    bad = tmp_path / "broken.png"
    bad.write_bytes(b"not an image")
    out = make_contact_sheet([*paths, bad], ["ok", "broken"], tmp_path / "sheet.png", cols=2, thumb_width=90)
    assert out.exists()


def test_label_count_must_match(tmp_path):
    paths = _images(tmp_path, 2)
    with pytest.raises(ValueError):
        make_contact_sheet(paths, ["only one"], tmp_path / "sheet.png")
    with pytest.raises(ValueError):
        make_contact_sheet([], [], tmp_path / "sheet.png")


def test_cli(tmp_path):
    paths = _images(tmp_path, 3)
    out = tmp_path / "sub" / "cli.png"
    assert main([str(out), *map(str, paths), "--cols", "2"]) == 0
    assert out.exists()
