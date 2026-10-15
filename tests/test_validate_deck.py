"""
Tests for src/validate_deck.py.

Fixtures (tests/fixtures/):
  valid_deck/deck.json   a minimal 10-card deck with no problems
  broken_deck/deck.json  the same deck with 5 deliberate mistakes
  characters/            a tiny character library (adam = male, chava = female)

Run from the repo root:  python3 -m pytest tests -q
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import validate_deck  # noqa: E402
from validate_deck import count_words, spoken_text, strip_nikud, validate_deck as run  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
CHARACTERS = FIXTURES / "characters"
VALID = FIXTURES / "valid_deck" / "deck.json"
BROKEN = FIXTURES / "broken_deck" / "deck.json"


def messages(report, severity="error"):
    return [f"{i.card_id} {i.field} {i.message}" for i in report.issues if i.severity == severity]


@pytest.fixture
def deck():
    """A fresh copy of the valid deck to break in one way per test."""
    return json.loads(VALID.read_text(encoding="utf-8"))


def validate(deck, tmp_path):
    path = tmp_path / "deck.json"
    path.write_text(json.dumps(deck, ensure_ascii=False), encoding="utf-8")
    return run(path, characters_dir=CHARACTERS)


def card(deck, card_id):
    return next(c for c in deck["cards"] if c["card_id"] == card_id)


# ---------------------------------------------------------------- whole decks

def test_valid_fixture_has_no_errors_or_warnings():
    report = run(VALID, characters_dir=CHARACTERS)
    assert report.issues == []


def test_broken_fixture_reports_every_planted_mistake():
    errors = " | ".join(messages(run(BROKEN, characters_dir=CHARACTERS)))
    assert "needs 10 cards, found 9" in errors
    assert "story_1 back.say 60 spoken words" in errors
    assert "spotlight_2 back.hebrew.word 'אַמִּיץ' is the masculine form" in errors
    assert "'noach' is not in the character library" in errors
    assert "says p.99" in errors


def test_bereshit_deck_has_no_errors():
    assert messages(run(ROOT / "decks" / "bereshit" / "deck.json")) == []


def test_cli_exit_codes(capsys):
    assert validate_deck.main([str(VALID), "--characters-dir", str(CHARACTERS)]) == 0
    assert validate_deck.main([str(BROKEN), "--characters-dir", str(CHARACTERS)]) == 1
    assert "Result: FAIL" in capsys.readouterr().out


def test_cli_strict_fails_on_warnings(deck, tmp_path):
    card(deck, "anchor_1")["back"]["transition"] = "Now the next card!"
    path = tmp_path / "deck.json"
    path.write_text(json.dumps(deck, ensure_ascii=False), encoding="utf-8")
    args = [str(path), "--characters-dir", str(CHARACTERS)]
    assert validate_deck.main(args) == 0
    assert validate_deck.main(args + ["--strict"]) == 1


def test_cli_json_output(capsys):
    validate_deck.main([str(BROKEN), "--characters-dir", str(CHARACTERS), "--json"])
    out = json.loads(capsys.readouterr().out)
    assert out["passed"] is False and len(out["errors"]) >= 5


# ---------------------------------------------------------------- word budgets

def test_word_counting_ignores_cues_and_markup():
    say = "**Day 1: light!** [Open hands wide]\n**Day 2 — sky…**"
    assert spoken_text(say).split() == ["Day", "1:", "light!", "Day", "2", "—", "sky…"]
    assert count_words(spoken_text(say)) == 6  # the dash doesn't count


def test_too_many_cue_words(deck, tmp_path):
    card(deck, "story_2")["back"]["say"] = "**Go!** [" + " ".join(["clap"] * 26) + "]"
    assert any("26 words inside [cues]" in m for m in messages(validate(deck, tmp_path)))


def test_long_objective_and_ask(deck, tmp_path):
    back = card(deck, "story_2")["back"]
    back["objective"] = "one two three four five six seven eight nine ten eleven"
    back["ask"] = [{"text": " ".join(["why"] * 13), "type": "open"}]
    errors = messages(validate(deck, tmp_path))
    assert any("back.objective 11 words" in m for m in errors)
    assert any("back.ask[0] 13 words" in m for m in errors)


def test_distancing_question_only_on_connection(deck, tmp_path):
    card(deck, "story_2")["back"]["ask"] = [{"text": "Have you ever felt sad?", "type": "distancing"}]
    card(deck, "connection_1")["back"]["ask"] = [{"text": "Have you ever helped?", "type": "distancing"}]
    warnings = messages(validate(deck, tmp_path), "warning")
    assert any(m.startswith("story_2") and "distancing" in m for m in warnings)
    assert not any(m.startswith("connection_1") for m in warnings)


# ---------------------------------------------------------------- card counts

def test_holiday_deck_needs_12_cards(deck, tmp_path):
    deck["holiday"] = True
    errors = messages(validate(deck, tmp_path))
    assert any("holiday deck needs 12 cards" in m for m in errors)
    assert any("3 'tradition'" in m for m in errors)


# ---------------------------------------------------------------- characters

def test_more_than_four_characters_warns(deck, tmp_path):
    card(deck, "anchor_1")["characters_in_scene"] = ["adam", "chava", "adam", "chava", "adam"]
    assert any("5 characters" in m for m in messages(validate(deck, tmp_path), "warning"))


def test_named_character_must_be_listed(deck, tmp_path):
    card(deck, "story_2")["image_prompt"] = "Adam names a lion."
    assert any("mentions Adam" in m for m in messages(validate(deck, tmp_path), "warning"))


# ---------------------------------------------------------------- Hebrew

def test_strip_nikud():
    assert strip_nikud("אַמִּיצָה") == "אמיצה"


def test_vocab_word_without_nikud_is_error(deck, tmp_path):
    card(deck, "story_2")["hebrew_keyword"]["word"] = "אור"
    card(deck, "story_3")["title_he"] = "שבת"
    report = validate(deck, tmp_path)
    assert any("story_2 hebrew_keyword.word" in m for m in messages(report))
    assert any("story_3 title_he" in m for m in messages(report, "warning"))


def test_unpointed_copy_must_match():
    # The v3 schema has no paired fields yet, so test the helper directly
    report = validate_deck.Report(Path("x"))
    validate_deck.check_nikud({"word": "עוֹזְרִים", "word_unpointed": "עוזר"}, "spotlight_2", report)
    assert any("doesn't match" in m for m in messages(report))
    report = validate_deck.Report(Path("x"))
    validate_deck.check_nikud({"word": "עוֹזְרִים", "word_unpointed": "עוזרים"}, "spotlight_2", report)
    assert messages(report) == []


def test_feminine_word_on_male_card_is_error(deck, tmp_path):
    card(deck, "spotlight_1")["title_he"] = "גִּבּוֹרָה"
    assert any("spotlight_1 title_he" in m and "feminine" in m for m in messages(validate(deck, tmp_path)))


def test_correct_gender_passes(deck, tmp_path):
    card(deck, "spotlight_2")["back"]["hebrew"] = {"word": "אַמִּיצָה", "translit": "a-mi-TZAH", "meaning": "brave"}
    assert messages(validate(deck, tmp_path)) == []


def test_note_with_both_forms_allows_it(deck, tmp_path):
    card(deck, "spotlight_2")["back"]["hebrew"] = {
        "word": "אַמִּיץ", "translit": "a-MITZ", "meaning": "brave",
        "note": "for a girl: אַמִּיצָה, for a boy: אַמִּיץ"}
    assert messages(validate(deck, tmp_path)) == []


def test_same_letters_pair_uses_nikud(deck, tmp_path):
    # יָפֶה (m) and יָפָה (f) have the same letters
    card(deck, "spotlight_2")["title_he"] = "יָפֶה"
    assert any("masculine" in m for m in messages(validate(deck, tmp_path)))
    card(deck, "spotlight_2")["title_he"] = "יָפָה"
    assert messages(validate(deck, tmp_path)) == []


def test_mixed_group_is_not_checked(deck, tmp_path):
    c = card(deck, "spotlight_2")
    c["characters_in_scene"] = ["chava", "adam"]
    c["image_prompt"] = "Chava and Adam in a garden."
    c["title_he"] = "אַמִּיץ"
    assert messages(validate(deck, tmp_path)) == []


# ---------------------------------------------------------------- transitions, prompts, guide

def test_transition_with_deck_order_words(deck, tmp_path):
    card(deck, "story_1")["back"]["transition"] = "The first day begins!"
    warnings = messages(validate(deck, tmp_path), "warning")
    assert any('"first"' in m for m in warnings) and any('"begins"' in m for m in warnings)


def test_banned_prompt_terms(deck, tmp_path):
    card(deck, "story_1")["image_prompt"] = "=== STYLE === A gold border, title text in the top 22%, a Star of David."
    card(deck, "connection_1")["image_prompt"] = "Children by a Star of David poster."
    warnings = " | ".join(messages(validate(deck, tmp_path), "warning"))
    for term in ("'=== STYLE'", "'border'", "'text'", "'22%'", "story_1 image_prompt Star of David"):
        assert term in warnings
    assert "connection_1" not in warnings


def test_god_depiction_is_error(deck, tmp_path):
    card(deck, "anchor_1")["image_prompt"] = "An old man in the clouds making the world."
    assert any("depicts God" in m for m in messages(validate(deck, tmp_path)))


def test_card_without_guide_slot(deck, tmp_path):
    c = card(deck, "connection_1")
    c["card_id"] = "connection_2"
    assert any("no slot in the standard guide layout" in m for m in messages(validate(deck, tmp_path)))


def test_guide_layout_matches_card_counts():
    layout = validate_deck.load_yaml(validate_deck.LAYOUT_PATH)
    assert len(layout["standard"]["cards"]) == sum(validate_deck.STANDARD_TYPE_COUNTS.values())
    assert len(layout["holiday"]["cards"]) == sum(validate_deck.HOLIDAY_TYPE_COUNTS.values())
    for kind in ("standard", "holiday"):
        pages = list(layout[kind]["cards"].values()) + list(layout[kind]["fixed"].values())
        # Only the home card shares a page (with the family letter)
        assert len(pages) - len(set(pages)) == 1
