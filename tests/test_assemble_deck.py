"""Tests for src/assemble_deck.py and the pipeline schemas. No network.

The fixture tests/fixtures/pipeline_min/pipeline/ is a tiny 10-card Bereshit pipeline.
Each test copies it to a temp folder, optionally breaks one thing, and assembles it.

Run from the repo root:  python3 -m pytest tests -q
"""

import json
import shutil
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import assemble_deck  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "pipeline_min"
REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def deck_dir(tmp_path):
    target = tmp_path / "pipeline_min"
    shutil.copytree(FIXTURE, target)
    return target


def _edit(deck_dir, filename, change):
    """Load a pipeline YAML, let `change(data)` modify it, save it back."""
    path = deck_dir / "pipeline" / filename
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _card(data, card_id):
    return next(c for c in data["cards"] if c["card_id"] == card_id)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_fixture_assembles_into_valid_v3_deck(deck_dir):
    deck, report = assemble_deck.assemble(deck_dir)
    assert report.errors == []
    written = json.loads((deck_dir / "deck.json").read_text(encoding="utf-8"))
    assert written == deck
    assert assemble_deck.schema_errors(written, assemble_deck.DECK_SCHEMA_PATH) == []
    assert len(deck["cards"]) == 10


def test_each_part_comes_from_its_owner(deck_dir):
    deck, _ = assemble_deck.assemble(deck_dir, write=False)
    # 00 series: names and value
    assert deck["parasha_he"] == "בְּרֵאשִׁית"
    assert deck["value"]["en"] == "Caring for the world"
    # 02 structure: order, week plan, sequence numbers
    assert [c["card_id"] for c in deck["cards"]][:3] == ["anchor_1", "spotlight_1", "spotlight_2"]
    assert len(deck["week_plan"]) == 5
    assert _card(deck, "story_4")["sequence_number"] == 4
    # 03 content: titles, back, keyword
    assert _card(deck, "spotlight_2")["title_he"] == "חַוָּה"
    assert _card(deck, "story_1")["hebrew_keyword"]["word"] == "אוֹר"
    # 05 visual: prompts, characters, palette
    assert _card(deck, "spotlight_1")["characters_in_scene"] == ["adam"]
    assert deck["palette"][0] == "#1E3A5F"
    # 05b picks: chosen final image path
    assert _card(deck, "story_1")["image_path"] == "raw/story_1_final.png"
    assert _card(deck, "story_2")["image_path"] == "raw/story_2.png"


def test_if_they_ask_answers_land_in_the_guide(deck_dir):
    deck, _ = assemble_deck.assemble(deck_dir, write=False)
    questions = [q["q"] for q in _card(deck, "story_4")["guide"]["hard_questions"]]
    assert questions == ["Did they eat the fruit?"]
    assert _card(deck, "story_3")["guide"]["hard_questions"] == []


def test_missing_visual_step_uses_placeholders(deck_dir):
    (deck_dir / "pipeline" / "05-visual.yaml").unlink()
    deck, report = assemble_deck.assemble(deck_dir, write=False)
    assert report.errors == []
    assert _card(deck, "anchor_1")["image_prompt"] == assemble_deck.PLACEHOLDER_PROMPT
    assert _card(deck, "spotlight_1")["characters_in_scene"] == ["adam"]  # from 02 structure
    assert any("05-visual.yaml not written" in w for w in report.warnings)


def test_validator_runs_after_writing(deck_dir, tmp_path, monkeypatch):
    fake = tmp_path / "validate_deck.py"
    fake.write_text("import sys; print('checked', sys.argv[1]); sys.exit(0)\n")
    monkeypatch.setattr(assemble_deck, "VALIDATOR", fake)
    _, report = assemble_deck.assemble(deck_dir)
    assert report.errors == []

    fake.write_text("import sys; print('say over 50 words'); sys.exit(1)\n")
    _, report = assemble_deck.assemble(deck_dir)
    assert any("validate_deck.py failed" in e for e in report.errors)


# ---------------------------------------------------------------------------
# Things that must fail
# ---------------------------------------------------------------------------

def test_missing_required_file_fails(deck_dir):
    (deck_dir / "pipeline" / "02b-sensitivity.yaml").unlink()
    deck, report = assemble_deck.assemble(deck_dir)
    assert deck is None
    assert any("02b-sensitivity.yaml: missing" in e for e in report.errors)
    assert not (deck_dir / "deck.json").exists()


def test_schema_error_is_reported_with_location(deck_dir):
    _edit(deck_dir, "01-research.yaml", lambda d: d["claims"][1].pop("source"))
    _, report = assemble_deck.assemble(deck_dir, write=False)
    assert any(e.startswith("01-research.yaml: claims/1") and "source" in e for e in report.errors)


def test_wrong_card_count_fails(deck_dir):
    _edit(deck_dir, "02-structure.yaml", lambda d: d["cards"].pop())
    _, report = assemble_deck.assemble(deck_dir, write=False)
    assert any("standard deck with 4 story cards needs 10 cards, found 9" in e for e in report.errors)


# ---------------------------------------------------------------------------
# Sequence decks (one story card per item, e.g. the 7 days of creation)
# ---------------------------------------------------------------------------

def _make_sequence(deck_dir, story_cards=7):
    """Turn the 10-card fixture into a sequence deck: copy story_4 into story_5..story_N everywhere."""
    import copy
    import deck_pattern
    layout = yaml.safe_load((REPO_ROOT / "guide_layout.yaml").read_text(encoding="utf-8"))
    pages = deck_pattern.page_map(layout, False, story_cards)["cards"]

    _edit(deck_dir, "00-series.yaml", lambda d: d.update(deck_pattern="sequence", story_cards=story_cards))

    def add_stories(d, key="cards"):
        rows = d[key]
        at = next(i for i, c in enumerate(rows) if c["card_id"] == "story_4")
        for n in range(5, story_cards + 1):
            row = copy.deepcopy(rows[at])
            row["card_id"] = f"story_{n}"
            if "sequence_number" in row:
                row["sequence_number"] = n
            rows.insert(at + n - 4, row)
        for row in rows:   # guide pages move down behind the extra story pages
            guide_ref = (row.get("back") or {}).get("guide_ref")
            if guide_ref:
                guide_ref["page"] = pages[row["card_id"]]

    def structure(d):
        add_stories(d)
        d["week_plan"][2]["cards"] += [f"story_{n}" for n in range(5, story_cards + 1)]
    _edit(deck_dir, "02-structure.yaml", structure)
    for filename in ("02b-sensitivity.yaml", "03-content.yaml", "05-visual.yaml"):
        _edit(deck_dir, filename, add_stories)


def test_sequence_deck_assembles_with_one_story_card_per_item(deck_dir):
    _make_sequence(deck_dir, 7)
    deck, report = assemble_deck.assemble(deck_dir)
    assert report.errors == []
    assert len(deck["cards"]) == 13
    assert (deck["deck_pattern"], deck["story_cards"]) == ("sequence", 7)
    assert _card(deck, "story_7")["sequence_number"] == 7
    assert _card(deck, "connection_1")["back"]["guide_ref"]["page"] == 13


def test_sequence_deck_with_wrong_story_count_fails(deck_dir):
    _make_sequence(deck_dir, 7)
    _edit(deck_dir, "00-series.yaml", lambda d: d.update(story_cards=6))
    _, report = assemble_deck.assemble(deck_dir, write=False)
    assert any("sequence deck with 6 story cards needs 12 cards, found 13" in e for e in report.errors)


def test_sequence_deck_needs_story_cards(deck_dir):
    _edit(deck_dir, "00-series.yaml", lambda d: d.update(deck_pattern="sequence"))
    _, report = assemble_deck.assemble(deck_dir, write=False)
    assert any("00-series.yaml" in e and "story_cards" in e for e in report.errors)


def test_standard_deck_has_no_pattern_fields(deck_dir):
    deck, _ = assemble_deck.assemble(deck_dir, write=False)
    assert "deck_pattern" not in deck and "story_cards" not in deck


def test_unapproved_checkpoint_fails(deck_dir):
    def unapprove(d):
        d["checkpoint"] = {"approved": False, "decided_by": "pending"}
    _edit(deck_dir, "02b-sensitivity.yaml", unapprove)
    _, report = assemble_deck.assemble(deck_dir)
    assert any("checkpoint not approved" in e for e in report.errors)
    assert not (deck_dir / "deck.json").exists()


def test_guide_only_card_still_planned_fails(deck_dir):
    def mark(d):
        _card(d, "story_4").update(verdict="guide-only")
        _card(d, "story_4").pop("reframe")
    _edit(deck_dir, "02b-sensitivity.yaml", mark)
    _, report = assemble_deck.assemble(deck_dir, write=False)
    assert any("story_4 is marked 'guide-only'" in e for e in report.errors)


def test_minutes_must_match_structure(deck_dir):
    _edit(deck_dir, "03-content.yaml", lambda d: _card(d, "story_1")["back"].update(minutes=9))
    _, report = assemble_deck.assemble(deck_dir, write=False)
    assert any("story_1 back.minutes=9" in e for e in report.errors)


def test_unknown_character_fails(deck_dir):
    _edit(deck_dir, "05-visual.yaml", lambda d: _card(d, "story_4").update(characters_in_scene=["kayin"]))
    _, report = assemble_deck.assemble(deck_dir, write=False)
    assert any("'kayin' is not in characters/" in e for e in report.errors)


def test_more_than_four_characters_fails(deck_dir):
    _edit(deck_dir, "05-visual.yaml",
          lambda d: _card(d, "story_4").update(characters_in_scene=["adam", "chava", "moses", "miriam", "yitro"]))
    _, report = assemble_deck.assemble(deck_dir, write=False)
    assert any("05-visual.yaml: cards/6/characters_in_scene" in e for e in report.errors)


def test_missing_content_card_fails(deck_dir):
    _edit(deck_dir, "03-content.yaml", lambda d: d["cards"].pop(0))
    _, report = assemble_deck.assemble(deck_dir, write=False)
    assert any("03-content.yaml: no entry for anchor_1" in e for e in report.errors)


def test_image_qa_totals_are_rechecked(deck_dir):
    # d2 has a 0 (hard band), so claiming it passed must be caught
    _edit(deck_dir, "05b-image-qa.yaml", lambda d: d["images"][1].update({"pass": True}))
    _, report = assemble_deck.assemble(deck_dir, write=False)
    assert any("but the scores give 20/False" in e for e in report.errors)


def test_deck_id_must_match_folder(deck_dir):
    _edit(deck_dir, "00-series.yaml", lambda d: d.update(deck_id="noach"))
    _, report = assemble_deck.assemble(deck_dir, write=False)
    assert any("does not match folder" in e for e in report.errors)


# ---------------------------------------------------------------------------
# Image QA pass rule
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def rubric():
    return yaml.safe_load((REPO_ROOT / "agents" / "rubrics" / "image_qa.yaml").read_text(encoding="utf-8"))


def test_rubric_has_11_criteria_out_of_22(rubric):
    assert len(rubric["criteria"]) == 11
    assert rubric["max_total"] == 22 and rubric["pass_total"] == 16


def test_pass_rule(rubric):
    ids = [c["id"] for c in rubric["criteria"]]
    all_twos = dict.fromkeys(ids, 2)
    assert assemble_deck.image_qa_result(all_twos, rubric) == (22, True)
    one_zero = {**all_twos, ids[0]: 0}
    assert assemble_deck.image_qa_result(one_zero, rubric) == (20, False)   # a 0 always fails
    six_ones = {**all_twos, **dict.fromkeys(ids[:6], 1)}
    assert assemble_deck.image_qa_result(six_ones, rubric) == (16, True)    # exactly the line
    seven_ones = {**all_twos, **dict.fromkeys(ids[:7], 1)}
    assert assemble_deck.image_qa_result(seven_ones, rubric) == (15, False)


def test_editor_rubric_weights_add_to_100():
    editor = yaml.safe_load((REPO_ROOT / "agents" / "rubrics" / "editor.yaml").read_text(encoding="utf-8"))
    assert sum(s["weight"] for s in editor["sections"]) == 100
    assert {s["id"] for s in editor["sections"]} == {"content", "torah_accuracy", "hebrew", "art", "print"}


def test_every_pipeline_file_has_a_schema():
    for filename, _ in assemble_deck.PIPELINE_FILES:
        stem = filename[: -len(".yaml")]
        assert (assemble_deck.PIPELINE_SCHEMA_DIR / f"{stem}.schema.json").exists(), stem


def test_cli_dry_run_writes_nothing(deck_dir, tmp_path, monkeypatch):
    monkeypatch.setattr(assemble_deck, "PROJECT_LOG", tmp_path / "project.log")  # keep the real log clean
    assert assemble_deck.main([str(deck_dir), "--dry-run"]) == 0
    assert not (deck_dir / "deck.json").exists()
