"""
Tests for the coloring + sequencing extras, the teacher guide booklet and the pilot kit.
No network, no browser, no AI calls (the committed PDF is checked if it exists).
"""

import copy
import json
import sys
from pathlib import Path

import pytest
import yaml
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import build_guide  # noqa: E402
import build_pilot_kit  # noqa: E402
import coloring  # noqa: E402
import generate_activities as ga  # noqa: E402

DECK = ROOT / "decks" / "bereshit"


@pytest.fixture
def deck():
    return json.loads((DECK / "deck.json").read_text(encoding="utf-8"))


@pytest.fixture
def layout(deck):
    return build_guide.layout_for(deck)


# ---- cut-line geometry -------------------------------------------------------

def test_coloring_panels_are_exact_and_fit_the_page():
    cells = coloring.grid_cells(2, 2, ga.PANEL_W, ga.PANEL_H, ga.PANEL_LEFT, ga.PANEL_TOP)
    assert len(cells) == 4
    assert all((c["w"], c["h"]) == (3.75, 4.5) for c in cells)
    assert coloring.fits_on_page(cells, margin=0.3)


def test_cut_lines_are_straight_and_shared():
    lines = coloring.cut_lines(2, 2, 3.75, 4.5, 0.5, 1.65)
    assert len(lines) == 6                     # 3 vertical + 3 horizontal: neighbours share a line
    for x1, y1, x2, y2 in lines:
        assert x1 == x2 or y1 == y2            # straight
    xs = sorted({x1 for x1, _, x2, _ in lines if x1 == x2})
    assert xs == [0.5, 4.25, 8.0]
    ys = sorted({y1 for _, y1, _, y2 in lines if y1 == y2})
    assert ys == [1.65, 6.15, 10.65]


def test_sequencing_minis_keep_the_card_shape_and_fit():
    page1 = coloring.grid_cells(ga.MINI_COLS, 3, ga.MINI_W, ga.MINI_H, ga.MINI_LEFT, ga.MINI_TOP)
    assert len(page1) == 12                                   # 14 minis (7 days x 2) = 12 + 2 on page 2
    assert all(round(c["h"] / c["w"], 3) == 1.4 for c in page1)   # 5:7, like the real cards
    assert coloring.fits_on_page(page1, margin=0.3)
    assert len(coloring.cut_lines(3, 2, 2.5, 3.5)) == 7


def test_seven_day_panels_fit_and_the_8th_spot_is_not_cut():
    cells = coloring.grid_cells(ga.DAY_COLS, 2, ga.DAY_W, ga.DAY_H, ga.DAY_LEFT, ga.DAY_TOP)[:7]
    assert coloring.fits_on_page(cells, margin=0.3)
    lines = coloring.cell_cut_lines(cells)
    for x1, y1, x2, y2 in lines:
        assert x1 == x2 or y1 == y2                         # straight
    right = round(ga.DAY_LEFT + 4 * ga.DAY_W, 4)
    bottom = round(ga.DAY_TOP + 2 * ga.DAY_H, 4)
    # the far-right line stops at the first row, and the bottom line stops after 3 boxes
    assert (right, ga.DAY_TOP, right, round(ga.DAY_TOP + ga.DAY_H, 4)) in lines
    assert (ga.DAY_LEFT, bottom, round(ga.DAY_LEFT + 3 * ga.DAY_W, 4), bottom) in lines
    # neighbours share one line: 5 verticals + 3 horizontals
    assert len(lines) == 8


def test_cell_cut_lines_match_cut_lines_for_a_full_grid():
    full = coloring.grid_cells(2, 2, 3.75, 4.5, 0.5, 1.65)
    assert sorted(coloring.cell_cut_lines(full)) == sorted(coloring.cut_lines(2, 2, 3.75, 4.5, 0.5, 1.65))


def test_glue_strips_hold_the_7_days_and_fit():
    strips = ga.glue_strips(7)
    assert [[b["n"] for b in s["boxes"]] for s in strips] == [[1, 2, 3, 4], [5, 6, 7]]
    assert strips[0]["tab"] == 0 and strips[1]["tab"] > 0     # strip 2 tapes under strip 1
    for s in strips:
        assert coloring.fits_on_page([s], margin=0.3)
        assert all(b["w"] == ga.DAY_W and b["h"] == ga.DAY_H for b in s["boxes"])   # = the cut panels


def test_day_captions_do_not_give_away_the_order(deck):
    for card in deck["cards"]:
        if card["card_type"] == "story":
            caption = ga.day_caption(card)
            assert "Day" not in caption["en"] and not any(ch.isdigit() for ch in caption["en"])
            assert caption["he"] == card["hebrew_keyword"]["word"]


def test_instructions_are_at_most_40_words():
    for text in (ga.COLORING_INSTRUCTIONS, ga.DAYS_INSTRUCTIONS, ga.SEQUENCING_INSTRUCTIONS):
        assert ga.word_count(text) <= 40


def test_story_captions_are_at_most_4_words(deck):
    for card in deck["cards"]:
        if card["card_type"] == "story":
            assert ga.caption_words(card) <= 4, card["title_en"]


def test_missing_hint_uses_the_hebrew_keyword(deck):
    story_1 = next(c for c in deck["cards"] if c["card_id"] == "story_1")
    assert "אוֹר" in ga.missing_hint(story_1)


# ---- line art -----------------------------------------------------------------

def test_clean_line_art_is_pure_black_and_white_with_thicker_lines():
    img = Image.new("RGB", (200, 200), (250, 250, 250))
    ImageDraw.Draw(img).line((20, 100, 180, 100), fill=(90, 90, 90), width=2)
    out = coloring.clean_line_art(img).convert("L")
    assert set(out.getdata()) <= {0, 255}
    black_rows = {y for y in range(200) if out.getpixel((100, y)) == 0}
    assert len(black_rows) >= 5                 # 2px line grew by ~2px each side


def test_count_regions_counts_closed_areas():
    img = Image.new("L", (300, 300), 255)
    draw = ImageDraw.Draw(img)
    draw.line((150, 0, 150, 300), fill=0, width=6)   # 2 halves
    draw.line((0, 150, 150, 150), fill=0, width=6)   # left half split in 2 -> 3 areas
    assert coloring.count_regions(img) == 3


def test_committed_line_art_is_binary():
    for n in range(1, 8):          # one picture per day of creation
        path = coloring.line_art_path(DECK, f"story_{n}")
        assert path.exists(), path
        assert set(Image.open(path).convert("L").getdata()) <= {0, 255}


# ---- booklet page map -------------------------------------------------------------

def test_page_plan_covers_every_page_once(deck, layout):
    pages = build_guide.page_plan(deck, layout)
    last = max([*layout["cards"].values(), *layout["fixed"].values()])
    assert [p["n"] for p in pages] == list(range(1, last + 1))
    assert last == 19          # Bereshit is a sequence deck: 7 story pages instead of 4
    placed = [c for p in pages for c in p["cards"]]
    assert sorted(placed) == sorted(c["card_id"] for c in deck["cards"])


def test_card_backs_match_the_layout(deck, layout):
    assert build_guide.check_guide_refs(deck, layout) == []
    broken = copy.deepcopy(deck)
    broken["cards"][3]["back"]["guide_ref"]["page"] = 99
    assert build_guide.check_guide_refs(broken, layout)


def test_layout_gap_is_an_error(deck, layout):
    gappy = copy.deepcopy(layout)
    gappy["fixed"]["sources"] = max(gappy["fixed"].values()) + 2
    with pytest.raises(build_guide.GuideError):
        build_guide.page_plan(deck, gappy)


def test_family_letter_uses_the_same_script_as_the_teacher():
    guide = build_guide.Guide(DECK)
    letter = guide.family_letter()["question_raw"]
    script = yaml.safe_load((DECK / "pipeline" / "02b-sensitivity.yaml").read_text(encoding="utf-8"))
    teacher = next(q for q in script["if_they_ask"] if q["topic"] == letter["topic"])
    assert (letter["q"], letter["answer"], letter["redirect"]) == (teacher["q"], teacher["answer"], teacher["redirect"])
    assert len(guide.family_letter()["learned"]) == 3


def test_script_html_marks_say_and_do():
    out = build_guide.script_html("**Day 1: light!** [Open hands wide] אוֹר")
    assert '<b class="say">Day 1: light!</b>' in out
    assert '<span class="do">[Open hands wide]</span>' in out
    assert 'class="he"' in out


def test_committed_booklet_pdf_matches_the_layout(deck, layout):
    """The committed booklet must be rebuilt whenever the deck changes shape: python3 src/build_guide.py decks/bereshit"""
    pdf = DECK / "print" / "bereshit-guide.pdf"
    assert pdf.exists(), "booklet not built"
    pages = len(build_guide.pdf_page_texts(pdf))
    assert pages == max([*layout["cards"].values(), *layout["fixed"].values()]) == 19
    assert build_guide.verify_pdf(pdf, deck, layout) == []


def test_sequence_deck_story_slots_read_day_n(deck):
    assert build_guide.slot_label("story_3", deck) == "Day 3"
    assert build_guide.slot_label("story_3", {}) == "Story 3"
    assert build_guide.slot_label("spotlight_1", deck) == "Spotlight 1"


def test_booklet_day_pages_show_the_verses_and_key_hebrew(deck):
    guide = build_guide.Guide(DECK)
    page = guide.card_page("story_4")
    assert page["slot"] == "Day 4" and page["title_en"] == "Sun & Moon"
    assert page["text_ref"] == "Genesis 1:14-19" and page["key_hebrew"] == "יְהִי מְאֹרֹת"
    assert page["day"] == "Tue"                      # the teaching day is a weekday, not "Day 2"


# ---- pilot kit ----------------------------------------------------------------------

def test_pilot_kit_has_8_questions_and_week_rows(deck):
    kit = build_pilot_kit.load_kit()
    assert [q["n"] for q in kit["feedback"]] == list(range(1, 9))
    rows = build_pilot_kit.grid_rows(deck)
    assert len(rows) == len(deck["cards"])
    assert sum(r["first"] for r in rows) == len(deck["week_plan"])


def test_day1_light_and_darkness_is_simple(tmp_path):
    img = Image.open(coloring.light_and_darkness_art(tmp_path / "day1.png", size=(448, 600)))
    assert img.mode == "1" and img.size == (448, 600)
    assert 6 <= coloring.count_regions(img) <= 15
