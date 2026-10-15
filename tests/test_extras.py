"""
Tests for the printable extras: extras.yaml schema, bingo boards, I-spy counts,
line-art clean-up and cutouts. No network and no browser.
"""

import copy
import itertools
import sys
from pathlib import Path

import pytest
import yaml
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import bingo  # noqa: E402
import extras_data  # noqa: E402
import ispy  # noqa: E402
from generate_activities import bingo_instructions, hebrew_html, word_count  # noqa: E402
from generate_items import binarize_line_art, make_cutout  # noqa: E402

DECK = Path(__file__).resolve().parent.parent / "decks" / "bereshit"


@pytest.fixture
def data():
    return yaml.safe_load((DECK / "extras.yaml").read_text(encoding="utf-8"))


# ---- schema + cross-checks ---------------------------------------------------

def test_bereshit_extras_are_valid(data):
    assert extras_data.validate_extras(data) == []
    assert len(data["vocab"]) == 12


def test_missing_nikud_fails(data):
    broken = copy.deepcopy(data)
    broken["vocab"][0]["he"] = "אור"
    assert any("vocab/0/he" in p for p in extras_data.validate_extras(broken))


def test_unknown_ispy_item_fails(data):
    broken = copy.deepcopy(data)
    broken["ispy"]["easy"]["targets"]["dragon"] = 2
    assert any("dragon" in p for p in extras_data.validate_extras(broken))


def test_too_many_hebrew_words_in_listen_do_fails(data):
    broken = copy.deepcopy(data)
    broken["listen_do"]["steps"][0]["text"] += " Then find the פֶּרַח and the כּוֹכָב."
    assert any("Hebrew words" in p for p in extras_data.validate_extras(broken))


# ---- bingo -------------------------------------------------------------------

@pytest.fixture(scope="module")
def chosen():
    raw = yaml.safe_load((DECK / "extras.yaml").read_text(encoding="utf-8"))
    ids = [item["id"] for item in raw["vocab"]]
    boards, stats = bingo.choose_boards(ids, "bereshit", candidates=60)
    return ids, boards, stats


def test_bingo_boards_are_unique_and_overlap_at_most_6(chosen):
    ids, boards, _ = chosen
    assert len(boards) == 10
    for board in boards:
        assert board[bingo.CENTER] == bingo.FREE
        pictures = [c for c in board if c != bingo.FREE]
        assert len(pictures) == 8 and len(set(pictures)) == 8
        assert set(pictures) <= set(ids)
    for a, b in itertools.combinations(boards, 2):
        assert bingo.shared_items(a, b) <= 6
        assert sorted(a) != sorted(b)


def test_bingo_is_seeded(chosen):
    ids, boards, _ = chosen
    again, _ = bingo.choose_boards(ids, "bereshit", candidates=60)
    assert again == boards


def test_bingo_game_length_meets_targets(chosen):
    _, _, stats = chosen
    assert stats["passed"]
    assert 5 <= stats["median_first_win"] <= 8
    assert stats["avg_simultaneous_winners"] < 2


def test_three_in_a_row_with_free_center_is_too_quick(chosen):
    ids, boards, _ = chosen
    stats = bingo.simulate(boards, ids, 2000, seed=1, win_rule="line")
    assert stats["median_first_win"] < 5  # why the default rule is "corners"


def test_teacher_instructions_are_short():
    for rule in bingo.WIN_RULES:
        text = bingo_instructions(rule)
        assert word_count(text) <= 40
        assert "not food" in text


# ---- I-spy -------------------------------------------------------------------

@pytest.mark.parametrize("level", ["easy", "challenge"])
def test_ispy_counts_match_answer_key(data, level):
    cfg = data["ispy"]
    counts = dict(cfg[level]["targets"])
    counts.update(cfg[level].get("distractors", {}))
    placements = ispy.place_items(counts, cfg["zones"], cfg["item_zones"], {}, level, seed=7)
    assert ispy.count_by_item(placements) == counts
    targets = sum(cfg[level]["targets"].values())
    if level == "easy":
        assert targets == 15
    else:
        assert 20 <= targets <= 25 and cfg[level]["distractors"]
    rules = ispy.LEVELS[level]
    for p in placements:
        zone = cfg["zones"][cfg["item_zones"][p["id"]]]
        center_y = (p["y"] + p["h"] / 2) / 7.5
        assert zone[0] - 1e-9 <= center_y <= zone[1] + 1e-9
        assert rules["size_in"][0] - 1e-9 <= max(p["art_w"], p["art_h"]) <= rules["size_in"][1] + 1e-9
        assert abs(p["angle"]) <= rules["max_rotation"]
        assert 0 <= p["x"] and p["x"] + p["w"] <= 7.5 and 0 <= p["y"] and p["y"] + p["h"] <= 7.5
    for a, b in itertools.combinations(placements, 2):
        assert ispy.overlap_fraction(a, b) <= rules["max_overlap"] + 1e-9


# ---- image clean-up ------------------------------------------------------------

def test_binarize_gives_pure_black_and_white():
    img = Image.new("RGB", (100, 100), (250, 250, 250))
    draw = ImageDraw.Draw(img)
    draw.line((10, 50, 90, 50), fill=(90, 90, 90), width=2)   # gray line -> black
    draw.rectangle((10, 70, 40, 90), fill=(225, 225, 225))   # light gray smudge -> white
    out = binarize_line_art(img)
    assert set(out.getdata()) == {0, 255}
    assert out.getpixel((50, 50)) == 0 and out.getpixel((25, 80)) == 255
    assert out.getpixel((50, 52)) == 0  # the line got thicker


def test_cutout_removes_only_outside_white():
    img = Image.new("RGB", (200, 200), "white")
    draw = ImageDraw.Draw(img)
    draw.ellipse((40, 40, 160, 160), fill="orange", outline="black", width=6)
    draw.ellipse((90, 90, 110, 110), fill="white")  # the white of an eye
    out = make_cutout(img)
    assert out.mode == "RGBA"
    assert out.size[0] < 200  # cropped to the item
    assert out.getpixel((0, 0))[3] == 0
    cx, cy = out.size[0] // 2, out.size[1] // 2
    assert out.getpixel((cx, cy))[3] == 255  # inner white stays opaque


def test_hebrew_is_wrapped_rtl():
    out = hebrew_html("Find the עֵץ (ETZ). ⏸ Color it.")
    assert '<span class="he" lang="he">עֵץ</span>' in out
    assert 'class="pause"' in out
