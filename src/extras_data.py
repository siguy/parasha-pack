"""
Load and check a deck's printable-extras data (decks/{id}/extras.yaml).

Think of extras.yaml as the shopping list for the extras: which 12 words, how many
fish hide in the I-spy picture, which directions the teacher reads. This module reads
the list and checks it twice:
  1. against schemas/extras.schema.json (right fields, right types)
  2. cross-checks the schema can't do (every I-spy item is a real vocab item, ...)

It also knows where each item's pictures live:
  items/shared/{id}/                    generic items, reused by every deck
  decks/{deck}/extras/items/{id}/       deck_specific: true (e.g. Bereshit's snake)
"""

import json
import logging
import re
from pathlib import Path

import jsonschema
import yaml

logger = logging.getLogger("extras_data")

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "extras.schema.json"
SHARED_ITEMS_DIR = REPO_ROOT / "items" / "shared"

# Hebrew letters (no nikud) — used to count Hebrew words in a direction
HEBREW_WORD = re.compile(r"[א-ת][א-ת֑-ׇ]*")
MAX_LISTEN_DO_HEBREW_WORDS = 3


class ExtrasError(ValueError):
    """extras.yaml is missing, malformed, or inconsistent."""


def load_extras(deck_dir) -> dict:
    """Read decks/{id}/extras.yaml, validate it, and return the data (raises ExtrasError)."""
    path = Path(deck_dir) / "extras.yaml"
    if not path.exists():
        raise ExtrasError(f"No extras.yaml in {deck_dir}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    problems = validate_extras(data)
    if problems:
        raise ExtrasError(f"{path} has {len(problems)} problem(s):\n  - " + "\n  - ".join(problems))
    logger.info(f"extras.yaml OK: {len(data['vocab'])} vocab items ({path})")
    return data


def validate_extras(data: dict) -> list:
    """Return a list of human-readable problems (empty list = valid)."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    problems = [f"{'/'.join(str(p) for p in err.path) or '(top)'}: {err.message}"
                for err in validator.iter_errors(data)]
    if problems:
        return problems  # cross-checks assume the basic shape is right

    ids = [item["id"] for item in data["vocab"]]
    known = set(ids) | {data["free_space"]["id"]}
    if len(ids) != len(set(ids)):
        problems.append("vocab: duplicate ids")

    ispy = data["ispy"]
    for level in ("easy", "challenge"):
        counts = dict(ispy[level]["targets"])
        counts.update(ispy[level].get("distractors", {}))
        for item_id in counts:
            if item_id not in known:
                problems.append(f"ispy.{level}: unknown item '{item_id}'")
            elif item_id not in ispy["item_zones"]:
                problems.append(f"ispy.{level}: item '{item_id}' has no zone in item_zones")
    for item_id, zone in ispy["item_zones"].items():
        if zone not in ispy["zones"]:
            problems.append(f"ispy.item_zones.{item_id}: unknown zone '{zone}'")
    overlap = set(ispy["challenge"]["targets"]) & set(ispy["challenge"].get("distractors", {}))
    if overlap:
        problems.append(f"ispy.challenge: items are both target and distractor: {sorted(overlap)}")

    for set_name, items in data["match"]["sets"].items():
        for item_id in items:
            if item_id not in known:
                problems.append(f"match.sets.{set_name}: unknown item '{item_id}'")
    for entry in data["match"].get("bonus_days", []):
        if entry["item"] not in known:
            problems.append(f"match.bonus_days: unknown item '{entry['item']}'")

    listen = data["listen_do"]
    object_ids = {obj["id"] for obj in listen["objects"]} | {"box_1", "box_2"}
    hebrew_words = set()
    for number, step in enumerate(listen["steps"], 1):
        for exp in step["expected"]:
            if exp["object"] not in object_ids:
                problems.append(f"listen_do.steps[{number}]: unknown object '{exp['object']}'")
            if exp["action"] == "color" and not exp.get("color"):
                problems.append(f"listen_do.steps[{number}]: color action needs a color")
        hebrew_words.update(strip_nikud(w) for w in HEBREW_WORD.findall(step["text"]))
    if len(hebrew_words) > MAX_LISTEN_DO_HEBREW_WORDS:
        problems.append(f"listen_do: {len(hebrew_words)} different Hebrew words used "
                        f"(max {MAX_LISTEN_DO_HEBREW_WORDS})")
    coloring, sequencing = data.get("coloring"), data.get("sequencing")
    if coloring:
        if sorted(coloring["page_order"]) != sorted(coloring["cards"]):
            problems.append("coloring.page_order must use exactly the same cards as coloring.cards")
        for entry in coloring.get("days_strip", []):
            for item_id in entry["items"]:
                if item_id not in known:
                    problems.append(f"coloring.days_strip: unknown item '{item_id}'")
    if sequencing and not set(sequencing["easy_subset"]) <= set(sequencing["cards"]):
        problems.append("sequencing.easy_subset must be a subset of sequencing.cards")
    levels = [s["level"] for s in listen["steps"]]
    if 1 not in levels or 2 not in levels:
        problems.append("listen_do: needs Level 1 and Level 2 steps")
    return problems


def strip_nikud(text: str) -> str:
    """Remove Hebrew vowel points so אוֹר and אור compare equal."""
    return re.sub(r"[֑-ׇ]", "", text)


def all_items(data: dict) -> list:
    """The vocab items plus the free-space item (all items that need art)."""
    return list(data["vocab"]) + [data["free_space"]]


def items_by_id(data: dict) -> dict:
    return {item["id"]: item for item in all_items(data)}


def item_dir(item: dict, deck_dir) -> Path:
    """Folder that holds color.png / cutout.png / line.png for one item."""
    if item.get("deck_specific"):
        return Path(deck_dir) / "extras" / "items" / item["id"]
    return SHARED_ITEMS_DIR / item["id"]
