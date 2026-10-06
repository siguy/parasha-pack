#!/usr/bin/env python3
"""
Merge a deck's pipeline YAML files into decks/<id>/deck.json (v3).

Each agent writes one YAML file in decks/<id>/pipeline/. This script is the "stapler":
it checks every file against its schema (schemas/pipeline/*.schema.json), then takes
each part from the agent that owns it:

    00-series.yaml       -> deck name, ref, holiday flag, value (middah), deck_pattern + story_cards
    02-structure.yaml    -> card list and order, core/minutes, week_plan, story world, text_ref
    02b-sensitivity.yaml -> checkpoint must be approved; "if they ask" answers -> guide
    03-content.yaml      -> titles, back, guide, hebrew_keyword
    05-visual.yaml       -> palette, web_theme, image_prompt, characters_in_scene, exclude (optional)
    05b-image-qa.yaml    -> image_path from the picks                              (optional)
    06-editor.yaml       -> only checked; a failing editor review is a warning      (optional)

01-research.yaml is checked against its schema; only its text map is used: each card's key_hebrew
(and its text_ref must agree with 02-structure and 05-visual). Story cards must cite a text_ref.
After merging, the deck is checked against schemas/deck.v3.schema.json and then
src/validate_deck.py runs on the written file.

Usage (from the repo root):
    python3 src/assemble_deck.py decks/bereshit            # writes decks/bereshit/deck.json
    python3 src/assemble_deck.py decks/bereshit --dry-run  # checks only, writes nothing

Exit code 0 = deck.json written and every check passed; 1 = something failed (read the log).
"""

import argparse
import json
import logging
import subprocess
import sys
from collections import Counter
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

import character_library
import deck_pattern

logger = logging.getLogger("assemble_deck")

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas"
PIPELINE_SCHEMA_DIR = SCHEMA_DIR / "pipeline"
DECK_SCHEMA_PATH = SCHEMA_DIR / "deck.v3.schema.json"
IMAGE_QA_RUBRIC = REPO_ROOT / "agents" / "rubrics" / "image_qa.yaml"
VALIDATOR = REPO_ROOT / "src" / "validate_deck.py"
PROJECT_LOG = REPO_ROOT / "project.log"

# (file name, required?) in pipeline order. Schema = schemas/pipeline/<stem>.schema.json
PIPELINE_FILES = [
    ("00-series.yaml", True),
    ("01-research.yaml", True),
    ("02-structure.yaml", True),
    ("02b-sensitivity.yaml", True),
    ("03-content.yaml", True),
    ("05-visual.yaml", False),
    ("05b-image-qa.yaml", False),
    ("06-editor.yaml", False),
]

# The card mix: decision D1 (10 cards standard, 12 holiday) or a sequence deck with one story
# card per item (6 + N cards). The numbers live in src/deck_pattern.py.
def card_mix(series: dict, holiday: bool) -> dict:
    """Expected {card_type: count} for this deck, from 00-series.yaml's deck_pattern/story_cards."""
    _, story_cards, _ = deck_pattern.story_card_count({**series, "holiday": holiday})
    return deck_pattern.expected_type_counts(holiday, story_cards)


# Used only when 05-visual.yaml doesn't exist yet (e.g. assembling right after the Content Writer).
PLACEHOLDER_PALETTE = ["#444444", "#777777", "#999999", "#BBBBBB", "#EEEEEE"]
PLACEHOLDER_WEB_THEME = {"primary": "#444444", "secondary": "#777777", "accent": "#999999", "wash": "#EEEEEE"}
PLACEHOLDER_PROMPT = "TODO: scene prompt from the Visual Director (05-visual.yaml)"


class Report:
    """Collects errors (the deck is not ready) and warnings (worth a look)."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, msg):
        self.errors.append(msg)
        logger.error(msg)

    def warn(self, msg):
        self.warnings.append(msg)
        logger.warning(msg)


# ---------------------------------------------------------------------------
# Loading and schema checks
# ---------------------------------------------------------------------------

def _read_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _registry() -> Registry:
    """All our schemas, by $id, so 03-content can reuse the deck schema's back/guide shapes."""
    resources = []
    for path in [DECK_SCHEMA_PATH, *sorted(PIPELINE_SCHEMA_DIR.glob("*.schema.json"))]:
        schema = _read_json(path)
        resources.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(resources)


def schema_errors(data: dict, schema_path: Path) -> list:
    """Return readable schema errors ('cards/3/back: ...'); empty list = valid."""
    validator = Draft202012Validator(_read_json(schema_path), registry=_registry())
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        where = "/".join(str(p) for p in err.absolute_path) or "(top)"
        errors.append(f"{where}: {err.message}")
    return errors


def load_pipeline(pipeline_dir: Path, report: Report) -> dict:
    """Read and schema-check every pipeline file. Returns {file stem: data or None}."""
    steps = {}
    for filename, required in PIPELINE_FILES:
        stem = filename[: -len(".yaml")]
        path = pipeline_dir / filename
        if not path.exists():
            steps[stem] = None
            if required:
                report.error(f"{filename}: missing (required)")
            else:
                logger.info(f"{filename}: not written yet (optional), skipping")
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        problems = schema_errors(data, PIPELINE_SCHEMA_DIR / f"{stem}.schema.json")
        for p in problems:
            report.error(f"{filename}: {p}")
        # "records" = the file's main list: cards, scored images, or research claims
        count = len(data.get("cards") or data.get("images") or data.get("claims") or [])
        logger.info(f"{filename}: loaded ({count} records, {len(problems)} schema errors)")
        steps[stem] = data
    return steps


# ---------------------------------------------------------------------------
# Cross-file rules (things one schema alone can't see)
# ---------------------------------------------------------------------------

def check_deck_ids(steps: dict, deck_id_from_folder: str, report: Report) -> None:
    for stem, data in steps.items():
        if data and data.get("deck_id") != deck_id_from_folder:
            report.error(f"{stem}.yaml: deck_id '{data.get('deck_id')}' does not match folder '{deck_id_from_folder}'")


def check_card_mix(structure: dict, series: dict, report: Report) -> None:
    """Card mix (D1, or 6 + N for a sequence deck). A wrong total is an error; a wrong per-type mix a warning."""
    pattern, story_cards, problem = deck_pattern.story_card_count({**series, "holiday": structure.get("holiday")})
    if problem:
        report.error(f"00-series: {problem}")
    expected = card_mix(series, bool(structure.get("holiday")))
    if len(structure["cards"]) != sum(expected.values()):
        report.error(f"02-structure: a {pattern} deck with {story_cards} story cards needs "
                     f"{sum(expected.values())} cards, found {len(structure['cards'])}")
    actual = Counter(c["card_type"] for c in structure["cards"])
    if dict(actual) != expected:
        report.warn(f"02-structure: card mix {dict(actual)} differs from the {pattern} mix {expected}")
    ids = [c["card_id"] for c in structure["cards"]]
    for dup in [i for i, n in Counter(ids).items() if n > 1]:
        report.error(f"02-structure: card_id '{dup}' appears more than once")
    week_ids = [cid for day in structure["week_plan"] for cid in day["cards"]]
    for cid in sorted(set(week_ids) - set(ids)):
        report.error(f"02-structure: week_plan names unknown card '{cid}'")
    for cid in [i for i in ids if i not in week_ids]:
        report.warn(f"02-structure: card '{cid}' is not in any week_plan day")


def check_text_map(research: dict, structure: dict, visual: dict, report: Report) -> None:
    """Text fidelity: story cards cite their verses, and every step cites the SAME verses as the text map."""
    text_map = _by_card(research, "text_map")
    if not text_map:
        report.warn("01-research: no text_map (what each card's verses say and don't); text_ref not cross-checked")
    visual_by_id = _by_card(visual)
    for card in structure["cards"]:
        cid, text_ref = card["card_id"], card.get("text_ref")
        if card["card_type"] == "story" and not text_ref:
            report.error(f"02-structure: {cid} is a story card with no text_ref (which verses does it show?)")
        if text_map and text_ref:
            row = text_map.get(cid)
            if row is None:
                report.error(f"01-research: text_map has no row for {cid}")
            elif row["text_ref"] != text_ref:
                report.error(f"02-structure: {cid} text_ref '{text_ref}' but the text map says '{row['text_ref']}'")
        visual_ref = (visual_by_id.get(cid) or {}).get("text_ref")
        if visual_ref and text_ref and visual_ref != text_ref:
            report.error(f"05-visual: {cid} text_ref '{visual_ref}' but 02-structure says '{text_ref}'")


def check_sensitivity(structure: dict, sensitivity: dict, report: Report) -> None:
    """The ★ checkpoint must be approved, and every planned card must have an ok/reframe verdict."""
    checkpoint = sensitivity["checkpoint"]
    if not checkpoint["approved"]:
        report.error(f"02b-sensitivity: checkpoint not approved (decided_by: {checkpoint['decided_by']})")
    verdicts = {c["card_id"]: c["verdict"] for c in sensitivity["cards"]}
    for card in structure["cards"]:
        verdict = verdicts.get(card["card_id"])
        if verdict is None:
            report.error(f"02b-sensitivity: no verdict for {card['card_id']}")
        elif verdict in ("guide-only", "skip"):
            report.error(f"02b-sensitivity: {card['card_id']} is marked '{verdict}' but is still in "
                         f"02-structure; the Curriculum Designer must replace it")


def _by_card(data: dict, key: str = "cards") -> dict:
    return {c["card_id"]: c for c in (data or {}).get(key, [])}


def check_card_sets(structure: dict, other: dict, filename: str, report: Report) -> None:
    """A later step must cover exactly the cards in 02-structure."""
    planned = {c["card_id"] for c in structure["cards"]}
    written = set(_by_card(other))
    for cid in sorted(planned - written):
        report.error(f"{filename}: no entry for {cid}")
    for cid in sorted(written - planned):
        report.error(f"{filename}: {cid} is not in 02-structure")


def image_qa_result(scores: dict, rubric: dict) -> tuple:
    """Apply the Image QA pass rule. Returns (total, passed).

    Pass = no criterion scored 0 and total >= pass_total (16 of 22). Each criterion beyond the
    11 core ones (added_criteria from v1.1, sequence_criteria) raises the line by 2.
    """
    base = {c["id"] for c in rubric["criteria"]}
    extra = len([cid for cid in scores if cid not in base])
    total = sum(scores.values())
    no_zero = (0 not in scores.values()) if rubric.get("no_zeros", True) else True
    return total, (no_zero and total >= rubric["pass_total"] + 2 * extra)


def _version(text) -> tuple:
    """'1.10' -> (1, 10), so versions compare as numbers."""
    return tuple(int(part) for part in str(text).split("."))


def required_criteria(rubric: dict, version: str, sequence_story: bool) -> set:
    """Criterion ids a row must score: the core list, plus extras that exist in its rubric version."""
    ids = {c["id"] for c in rubric["criteria"]}
    extras = rubric.get("added_criteria", []) + (rubric.get("sequence_criteria", []) if sequence_story else [])
    ids |= {c["id"] for c in extras if _version(c.get("since", "1.0")) <= _version(version)}
    return ids


def check_image_qa(image_qa: dict, report: Report, sequence_story_ids: set = frozenset()) -> None:
    """Every score row uses the rubric's criteria (for its rubric_version) and its total/pass add up.

    sequence_story_ids: story cards of a sequence deck; their rows also need the rubric's
    sequence_criteria (is the new item the hero?).
    """
    with open(IMAGE_QA_RUBRIC, "r", encoding="utf-8") as f:
        rubric = yaml.safe_load(f)
    file_version = image_qa.get("rubric_version", "1.0")
    for row in image_qa["images"]:
        criteria = required_criteria(rubric, row.get("rubric_version", file_version),
                                     row["card_id"] in sequence_story_ids)
        label = f"05b-image-qa: {row['file']}"
        if set(row["scores"]) != criteria:
            missing = sorted(criteria - set(row["scores"]))
            extra = sorted(set(row["scores"]) - criteria)
            report.error(f"{label}: scores must cover the rubric exactly (missing {missing}, unknown {extra})")
            continue
        total, passed = image_qa_result(row["scores"], rubric)
        if total != row["total"] or passed != row["pass"]:
            report.error(f"{label}: total/pass say {row['total']}/{row['pass']} but the scores give {total}/{passed}")
    passed_files = {r["file"] for r in image_qa["images"] if r["pass"]}
    for pick in image_qa["picks"]:
        if pick["chosen_draft"] not in passed_files:
            report.warn(f"05b-image-qa: {pick['card_id']} pick {pick['chosen_draft']} did not pass QA (flag-only)")
        if pick["decided_by"] == "pending":
            report.warn(f"05b-image-qa: {pick['card_id']} pick is still pending")


# ---------------------------------------------------------------------------
# The merge itself
# ---------------------------------------------------------------------------

def _deck_schema_allows(field: str, level: str) -> bool:
    """True if deck.v3.schema.json knows this optional field ('deck' or 'card' level).

    story_world_setting / style_plate / continuity_ref are read by generate_images.py but are
    added to the deck schema on another branch. Until then we leave them out instead of
    writing a deck.json that fails its own schema.
    """
    schema = _read_json(DECK_SCHEMA_PATH)
    props = schema["properties"] if level == "deck" else schema["$defs"]["card"]["properties"]
    return field in props


def merge_card(planned: dict, content: dict, visual: dict, pick: dict, sensitivity: dict,
               report: Report, text_row: dict = None) -> dict:
    """Build one deck.json card from the parts each agent owns."""
    cid = planned["card_id"]
    back = dict(content["back"])
    if planned["card_type"] != "home":
        for field in ("minutes", "core"):
            if back.get(field) != planned[field]:
                report.error(f"03-content: {cid} back.{field}={back.get(field)!r} but 02-structure says "
                             f"{planned[field]!r} (02 owns it)")

    # "If they ask" answers from the Sensitivity Reviewer go into the guide (no duplicates).
    guide = json.loads(json.dumps(content["guide"]))
    asked = {q["q"] for q in guide["hard_questions"]}
    for item in sensitivity["if_they_ask"]:
        if item["card_id"] == cid and item["q"] not in asked:
            guide["hard_questions"].append({k: item[k] for k in ("q", "answer", "redirect")})

    card = {
        "card_id": cid,
        "card_type": planned["card_type"],
        "title_en": content["title_en"],
        "title_he": content["title_he"],
        "characters_in_scene": visual["characters_in_scene"] if visual else planned.get("characters", []),
        "image_prompt": visual["image_prompt"] if visual else PLACEHOLDER_PROMPT,
        "image_path": (pick or {}).get("final") or f"raw/{cid}.png",
    }
    if "sequence_number" in planned:
        card["sequence_number"] = planned["sequence_number"]
    if planned.get("text_ref"):
        card["text_ref"] = planned["text_ref"]
    if text_row and text_row.get("key_hebrew"):
        card["key_hebrew"] = text_row["key_hebrew"]
    if visual and visual.get("exclude"):
        card["exclude"] = visual["exclude"]
    if "hebrew_keyword" in content:
        card["hebrew_keyword"] = content["hebrew_keyword"]
    for field in ("style_plate", "continuity_ref"):
        if visual and field in visual:
            if _deck_schema_allows(field, "card"):
                card[field] = visual[field]
            else:
                report.warn(f"{cid}: deck schema has no '{field}' yet; left out of deck.json")
    card["back"] = back
    card["guide"] = guide
    return card


def merge(steps: dict, report: Report) -> dict:
    """Combine the pipeline steps into one v3 deck dict (in 02-structure card order)."""
    series, structure, sensitivity = steps["00-series"], steps["02-structure"], steps["02b-sensitivity"]
    content, visual, image_qa = steps["03-content"], steps["05-visual"], steps["05b-image-qa"]

    if visual is None:
        report.warn("05-visual.yaml not written yet: placeholder palette and image prompts used")
    deck = {
        "id": series["deck_id"],
        "version": "3.0",
        "parasha_en": series["name_en"],
        "parasha_he": series["name_he"],
        "holiday": series["holiday"],
        "ref": series["ref"],
        "value": dict(series["middah"]),
        "palette": visual["palette"] if visual else PLACEHOLDER_PALETTE,
        "web_theme": visual["web_theme"] if visual else PLACEHOLDER_WEB_THEME,
        "story_world": structure["story_world"],
    }
    if _deck_schema_allows("story_world_setting", "deck"):
        deck["story_world_setting"] = structure["story_world_setting"]
    else:
        report.warn("deck schema has no 'story_world_setting' yet; left out of deck.json "
                    "(generate_images.py then defaults to the landscape plate)")
    if series.get("deck_pattern", deck_pattern.STANDARD) != deck_pattern.STANDARD:
        deck["deck_pattern"] = series["deck_pattern"]
        deck["story_cards"] = series["story_cards"]
    deck["week_plan"] = structure["week_plan"]

    content_by_id, visual_by_id = _by_card(content), _by_card(visual)
    picks_by_id = _by_card(image_qa, "picks")
    text_map = _by_card(steps["01-research"], "text_map")
    deck["cards"] = [
        merge_card(planned, content_by_id[planned["card_id"]], visual_by_id.get(planned["card_id"]),
                   picks_by_id.get(planned["card_id"]), sensitivity, report, text_map.get(planned["card_id"]))
        for planned in structure["cards"]
        if planned["card_id"] in content_by_id
    ]
    return deck


# ---------------------------------------------------------------------------
# Checks on the finished deck
# ---------------------------------------------------------------------------

def check_characters(deck: dict, report: Report, library_dir=None) -> None:
    known = set(character_library.list_characters(library_dir))
    for card in deck["cards"]:
        for key in card["characters_in_scene"]:
            if character_library.resolve_key(key, library_dir) not in known:
                report.error(f"{card['card_id']}: character '{key}' is not in characters/")


def run_validator(deck_json: Path, report: Report) -> None:
    """Run src/validate_deck.py <deck.json>; its failures become report errors."""
    result = subprocess.run([sys.executable, str(VALIDATOR), str(deck_json)],
                            capture_output=True, text=True)
    output = (result.stdout + result.stderr).strip()
    if result.returncode != 0:
        report.error(f"validate_deck.py failed:\n{output}")
    else:
        logger.info(f"validate_deck.py passed{': ' + output if output else ''}")


def assemble(deck_dir, write: bool = True, library_dir=None) -> tuple:
    """Merge decks/<id>/pipeline/*.yaml into deck.json. Returns (deck or None, Report)."""
    deck_dir = Path(deck_dir)
    report = Report()
    steps = load_pipeline(deck_dir / "pipeline", report)
    if report.errors:
        logger.error(f"{len(report.errors)} pipeline errors; deck.json not written")
        return None, report

    check_deck_ids(steps, deck_dir.name, report)
    check_card_mix(steps["02-structure"], steps["00-series"], report)
    check_sensitivity(steps["02-structure"], steps["02b-sensitivity"], report)
    check_text_map(steps["01-research"], steps["02-structure"], steps["05-visual"], report)
    check_card_sets(steps["02-structure"], steps["03-content"], "03-content.yaml", report)
    if steps["05-visual"]:
        check_card_sets(steps["02-structure"], steps["05-visual"], "05-visual.yaml", report)
    if steps["05b-image-qa"]:
        sequence_story_ids = set()
        if steps["00-series"].get("deck_pattern") == deck_pattern.SEQUENCE:
            sequence_story_ids = {c["card_id"] for c in steps["02-structure"]["cards"] if c["card_type"] == "story"}
        check_image_qa(steps["05b-image-qa"], report, sequence_story_ids)
    editor = steps["06-editor"]
    if editor and not editor["pass"]:
        report.warn(f"06-editor: review did not pass ({editor['weighted_percent']}%, "
                    f"{len(editor['issues'])} issues)")

    deck = merge(steps, report)
    logger.info(f"Merged {len(deck['cards'])} cards from {sum(1 for s in steps.values() if s)} pipeline files")
    check_characters(deck, report, library_dir)
    for problem in schema_errors(deck, DECK_SCHEMA_PATH):
        report.error(f"deck.json schema: {problem}")

    if report.errors:
        logger.error(f"{len(report.errors)} errors; deck.json not written")
        return deck, report
    if write:
        deck_json = deck_dir / "deck.json"
        with open(deck_json, "w", encoding="utf-8") as f:
            json.dump(deck, f, ensure_ascii=False, indent=2)
            f.write("\n")
        logger.info(f"Wrote {deck_json} ({len(deck['cards'])} cards)")
        run_validator(deck_json, report)
    return deck, report


def _setup_logging() -> None:
    """INFO to the console, ERROR+ also to project.log."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    error_file = logging.FileHandler(PROJECT_LOG, delay=True)
    error_file.setLevel(logging.ERROR)
    error_file.setFormatter(logging.Formatter("%(asctime)s assemble_deck %(levelname)s %(message)s"))
    logging.getLogger().addHandler(error_file)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Merge decks/<id>/pipeline/*.yaml into deck.json (v3)")
    parser.add_argument("deck_dir", help="Deck folder, e.g. decks/bereshit")
    parser.add_argument("--dry-run", action="store_true", help="Check everything, write nothing")
    args = parser.parse_args(argv)
    _setup_logging()

    _, report = assemble(args.deck_dir, write=not args.dry_run)
    print(f"\n{len(report.errors)} errors, {len(report.warnings)} warnings")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
