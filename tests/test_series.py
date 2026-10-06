"""Tests for series.yaml and src/series.py. Run: python3 -m pytest tests -q"""

import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import series  # noqa: E402


@pytest.fixture(scope="module")
def real_series():
    return series.load_series()


def test_real_series_is_valid(real_series):
    assert series.validate_series(real_series) == []


def test_has_54_parshiyot_and_12_holidays(real_series):
    entries = series.year_order(real_series)
    assert len(entries) == 66
    assert sum(e["type"] == "parasha" for e in entries) == 54
    assert sum(e["type"] == "holiday" for e in entries) == 12


def test_year_starts_with_fall_holidays_then_bereshit(real_series):
    ids = [e["id"] for e in series.year_order(real_series)]
    assert ids[:5] == ["rosh_hashanah", "yom_kippur", "sukkot", "simchat_torah", "bereshit"]
    assert ids[-1] == "vzot_haberachah"
    assert ids.index("purim") < ids.index("ki_tisa")


def test_required_decks_are_filled(real_series):
    by_id = {e["id"]: e for e in series.year_order(real_series)}
    assert by_id["bereshit"]["middah"] == "Caring for the world"
    assert by_id["bereshit"]["power_word"]["he"] == "טוֹב"
    assert by_id["bereshit"]["characters"] == ["adam", "chava"]
    assert by_id["purim"]["status"] == "done"
    assert by_id["purim"]["middah"] == "Courage"
    assert by_id["purim"]["power_word"]["he"] == "גִּבּוֹר"
    for deck in ["noach", "lech_lecha", "rosh_hashanah", "yom_kippur", "sukkot", "simchat_torah"]:
        assert series.is_filled(by_id[deck]), deck


def test_middot_come_from_values_spine():
    middot = series.load_middot()
    assert len(middot) == 15
    assert "Caring for the world" in middot and "Courage" in middot


def _tiny_series():
    return {
        "fall_holidays": [],
        "parshiyot": [
            {"id": f"p{i}", "type": "parasha", "book": "Genesis", "status": "planned",
             "middah": "TBD", "power_word": "TBD"} for i in range(6)
        ],
        "holidays": [],
    }


def test_duplicate_id_and_bad_status_are_caught():
    data = _tiny_series()
    data["parshiyot"][1]["id"] = "p0"
    data["parshiyot"][2]["status"] = "finished"
    problems = series.validate_series(data, middot=["Kindness"])
    assert any("duplicate id" in p for p in problems)
    assert any("status 'finished'" in p for p in problems)


def test_unknown_middah_is_caught():
    data = _tiny_series()
    data["parshiyot"][0]["middah"] = "Being loud"
    assert any("not in values-spine" in p for p in series.validate_series(data, middot=["Kindness"]))


def test_middah_repeat_within_four_filled_decks_is_caught():
    data = _tiny_series()
    for i, middah in enumerate(["Kindness", "Joy", "Peace", "Kindness"]):
        data["parshiyot"][i]["middah"] = middah
    problems = series.validate_series(data, middot=["Kindness", "Joy", "Peace", "Truth"])
    assert any("repeats p0" in p for p in problems)


def test_middah_repeat_after_four_decks_is_allowed():
    data = _tiny_series()
    for i, middah in enumerate(["Kindness", "Joy", "Peace", "Truth", "Kindness"]):
        data["parshiyot"][i]["middah"] = middah
    assert series.validate_series(data, middot=["Kindness", "Joy", "Peace", "Truth"]) == []


def test_holiday_before_must_be_a_parasha():
    data = _tiny_series()
    data["holidays"].append({"id": "h", "type": "holiday", "before": "nowhere", "status": "planned",
                             "middah": "TBD", "power_word": "TBD"})
    assert any("not a parasha id" in p for p in series.validate_series(data, middot=[]))


def test_missing_characters_lists_noach(real_series):
    assert "noach" in series.missing_characters(real_series)
    assert "adam" not in series.missing_characters(copy.deepcopy(real_series))


def test_bereshit_is_a_seven_card_sequence_deck(real_series):
    by_id = {e["id"]: e for e in series.year_order(real_series)}
    assert (by_id["bereshit"]["deck_pattern"], by_id["bereshit"]["story_cards"]) == ("sequence", 7)


@pytest.mark.parametrize("fields, problem", [
    ({"deck_pattern": "sequence"}, "needs story_cards"),
    ({"deck_pattern": "sequence", "story_cards": 11}, "story_cards is 11"),
    ({"deck_pattern": "list", "story_cards": 7}, "deck_pattern 'list'"),
    ({"story_cards": 7}, "only for deck_pattern: sequence"),
])
def test_bad_deck_pattern_is_reported(real_series, fields, problem):
    broken = copy.deepcopy(real_series)
    entry = next(p for p in broken["parshiyot"] if p["id"] == "noach")
    entry.update(fields)
    assert any(p.startswith("noach:") and problem in p for p in series.validate_series(broken))
