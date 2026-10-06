#!/usr/bin/env python3
"""
Load and check series.yaml, the year plan for every deck.

Usage:
    cd src && python3 series.py          # prints a summary and any problems

    from series import load_series, year_order, validate_series
    entries = year_order(load_series())
"""

import logging
import re
import sys
from pathlib import Path

import yaml

import character_library
import deck_pattern

logger = logging.getLogger("series")

REPO_ROOT = Path(__file__).resolve().parent.parent
SERIES_PATH = REPO_ROOT / "series.yaml"
VALUES_SPINE_PATH = REPO_ROOT / "docs" / "policies" / "values-spine.md"

VALID_STATUSES = {"done", "in_progress", "planned"}
VALID_TYPES = {"parasha", "holiday"}
TBD = "TBD"
NO_REPEAT_WINDOW = 4  # values-spine rule: no middah repeats within 4 consecutive decks


def load_series(path=SERIES_PATH) -> dict:
    """Read series.yaml into a dict."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_middot(path=VALUES_SPINE_PATH) -> list:
    """Read the English middah names from the table in values-spine.md.

    Table rows look like:  | 1 | Kindness | חֶסֶד | ... |
    Reading the doc (instead of copying the list here) keeps one source of truth.
    """
    middot = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r"\|\s*\d+\s*\|\s*([^|]+?)\s*\|", line)
            if match:
                middot.append(match.group(1))
    return middot


def year_order(series: dict) -> list:
    """Return every entry in teaching order for the school year.

    Fall holidays first, then the parshiyot in Torah order, with each other holiday
    placed just before the parasha named in its "before" field.
    """
    holidays_before = {}
    for holiday in series.get("holidays", []):
        holidays_before.setdefault(holiday.get("before"), []).append(holiday)

    ordered = list(series.get("fall_holidays", []))
    for parasha in series.get("parshiyot", []):
        ordered.extend(holidays_before.pop(parasha["id"], []))
        ordered.append(parasha)
    # Holidays with an unknown "before" go at the end (validate_series flags them)
    for leftovers in holidays_before.values():
        ordered.extend(leftovers)
    return ordered


def is_filled(entry: dict) -> bool:
    """A deck counts as 'filled' once it has a real middah (not TBD)."""
    return entry.get("middah") not in (None, TBD)


def validate_series(series: dict, middot: list = None) -> list:
    """Return a list of problems (empty list = valid)."""
    middot = middot if middot is not None else load_middot()
    problems = []
    entries = year_order(series)
    parasha_ids = {p["id"] for p in series.get("parshiyot", [])}

    seen_ids = set()
    for entry in entries:
        entry_id = entry.get("id", "?")
        if entry_id in seen_ids:
            problems.append(f"{entry_id}: duplicate id")
        seen_ids.add(entry_id)

        if entry.get("status") not in VALID_STATUSES:
            problems.append(f"{entry_id}: status '{entry.get('status')}' must be one of {sorted(VALID_STATUSES)}")
        if entry.get("type") not in VALID_TYPES:
            problems.append(f"{entry_id}: type '{entry.get('type')}' must be parasha or holiday")
        if entry.get("type") == "parasha" and not entry.get("book"):
            problems.append(f"{entry_id}: parasha needs a book")

        middah = entry.get("middah")
        if middah != TBD and middah not in middot:
            problems.append(f"{entry_id}: middah '{middah}' is not in values-spine.md")

        # Sequence decks (deck_pattern: sequence) get one story card per item: see src/deck_pattern.py
        pattern = entry.get("deck_pattern", deck_pattern.STANDARD)
        if pattern not in deck_pattern.PATTERNS:
            problems.append(f"{entry_id}: deck_pattern '{pattern}' must be one of {list(deck_pattern.PATTERNS)}")
        elif pattern == deck_pattern.SEQUENCE:
            _, _, problem = deck_pattern.story_card_count({**entry, "holiday": entry.get("type") == "holiday"}, None)
            if problem:
                problems.append(f"{entry_id}: {problem}")
        elif "story_cards" in entry:
            problems.append(f"{entry_id}: story_cards is only for deck_pattern: sequence")

        power_word = entry.get("power_word")
        if power_word != TBD and not (isinstance(power_word, dict)
                                      and all(power_word.get(k) for k in ("he", "translit", "en"))):
            problems.append(f"{entry_id}: power_word must be TBD or have he, translit and en")

    for holiday in series.get("holidays", []):
        if holiday.get("before") not in parasha_ids:
            problems.append(f"{holiday.get('id')}: 'before: {holiday.get('before')}' is not a parasha id")

    # No middah repeats inside any 4 consecutive filled decks
    filled = [e for e in entries if is_filled(e)]
    for i, entry in enumerate(filled):
        for earlier in filled[max(0, i - NO_REPEAT_WINDOW + 1):i]:
            if earlier["middah"] == entry["middah"]:
                problems.append(
                    f"{entry['id']}: middah '{entry['middah']}' repeats {earlier['id']} "
                    f"within {NO_REPEAT_WINDOW} consecutive filled decks"
                )
    return problems


def missing_characters(series: dict) -> list:
    """Character keys used in series.yaml that have no characters/{key}/character.yaml yet.

    Not an error (new decks need new characters), just a to-do list.
    """
    known = set(character_library.list_characters())
    missing = []
    for entry in year_order(series):
        for key in entry.get("characters", []):
            if character_library.resolve_key(key) not in known and key not in missing:
                missing.append(key)
    return missing


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    series = load_series()
    entries = year_order(series)
    filled = [e for e in entries if is_filled(e)]
    logger.info(f"series.yaml: {len(entries)} entries, {len(filled)} filled")
    for status in sorted(VALID_STATUSES):
        logger.info(f"  {status}: {sum(1 for e in entries if e.get('status') == status)}")

    missing = missing_characters(series)
    if missing:
        logger.warning(f"Characters not in characters/ yet: {', '.join(missing)}")

    problems = validate_series(series)
    for problem in problems:
        logger.error(problem)
    if not problems:
        logger.info("series.yaml is valid")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
