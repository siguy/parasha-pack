"""
How many cards of each type a deck has, and which guide page each card is on.

There are two deck patterns:

  standard  the usual mix (decision D1): 4 story cards (3 on a holiday deck).
  sequence  the Torah text itself is a numbered list (the 7 days of creation, the Ten
            Commandments, the 12 tribes...), so the deck gets ONE story card per item.
            The number of story cards comes from `story_cards` (in series.yaml, copied into
            00-series.yaml and deck.json).

Everything else stays the same: 1 anchor, 2 spotlights, 1 connection, 1 power word, 1 home
(+3 tradition cards on a holiday deck). So a sequence deck has 6 + N cards (9 + N on a holiday).

The guide booklet grows with the deck: guide_layout.yaml is written for the standard number of
story cards, and every page after the story pages moves down by the extra story cards. Think of
it like inserting pages into a binder: everything behind the insert gets a bigger page number.

Used by src/validate_deck.py, src/assemble_deck.py and src/build_guide.py, so the three can
never disagree about the card mix or the page map.
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SERIES_PATH = REPO_ROOT / "series.yaml"

STANDARD = "standard"
SEQUENCE = "sequence"
PATTERNS = (STANDARD, SEQUENCE)

# Story cards in a standard deck (decision D1): a holiday swaps one story card for 3 tradition cards
STANDARD_STORY_CARDS = {False: 4, True: 3}
# A sequence deck needs at least 3 items to be worth it, and more than 10 cards of one kind is
# too many to teach in a week
MIN_SEQUENCE_STORY_CARDS = 3
MAX_SEQUENCE_STORY_CARDS = 10
HOLIDAY_TRADITION_CARDS = 3


def expected_type_counts(holiday: bool, story_cards: int) -> dict:
    """{'anchor': 1, 'spotlight': 2, 'story': N, ...} for a deck with N story cards."""
    counts = {"anchor": 1, "spotlight": 2, "story": story_cards, "connection": 1}
    if holiday:
        counts["tradition"] = HOLIDAY_TRADITION_CARDS
    counts.update(power_word=1, home=1)
    return counts


def total_cards(holiday: bool, story_cards: int) -> int:
    return sum(expected_type_counts(holiday, story_cards).values())


def find_series_entry(deck_id: str, series_path: Path = SERIES_PATH) -> dict:
    """This deck's entry in series.yaml, or {} if it isn't there (or series.yaml is missing)."""
    if not series_path or not Path(series_path).exists():
        return {}
    with open(series_path, encoding="utf-8") as f:
        series = yaml.safe_load(f) or {}
    for section in ("fall_holidays", "parshiyot", "holidays"):
        for entry in series.get(section) or []:
            if entry.get("id") == deck_id:
                return entry
    return {}


def story_card_count(deck: dict, series_path: Path = SERIES_PATH) -> tuple:
    """
    Return (pattern, N, problem) for a deck.json dict (or a 00-series.yaml dict).

    The deck's own `deck_pattern` / `story_cards` win. A sequence deck without `story_cards`
    falls back to its series.yaml entry. `problem` is a readable message, or "" if all is well.
    """
    holiday = bool(deck.get("holiday"))
    pattern = deck.get("deck_pattern", STANDARD)
    if pattern not in PATTERNS:
        return STANDARD, STANDARD_STORY_CARDS[holiday], f"deck_pattern '{pattern}' must be one of {list(PATTERNS)}"
    if pattern == STANDARD:
        return STANDARD, STANDARD_STORY_CARDS[holiday], ""

    n = deck.get("story_cards")
    if n is None:
        deck_id = deck.get("id") or deck.get("deck_id") or ""
        n = find_series_entry(deck_id, series_path).get("story_cards")
    if not isinstance(n, int):
        return SEQUENCE, STANDARD_STORY_CARDS[holiday], \
            "sequence deck needs story_cards (in deck.json or its series.yaml entry)"
    if not MIN_SEQUENCE_STORY_CARDS <= n <= MAX_SEQUENCE_STORY_CARDS:
        return SEQUENCE, n, (f"story_cards is {n}; a sequence deck has "
                             f"{MIN_SEQUENCE_STORY_CARDS}-{MAX_SEQUENCE_STORY_CARDS} story cards")
    return SEQUENCE, n, ""


def page_map(layout: dict, holiday: bool, story_cards: int) -> dict:
    """
    Turn one section of guide_layout.yaml into the real page map for a deck.

    layout = the whole guide_layout.yaml dict. Returns {'cards': {card_id: page}, 'fixed': {name: page}}:
    one page per story card (story_1 .. story_N) from story_pages_start on, and every page after the
    story pages shifted by (N - the story_cards the layout was written for).
    """
    section = layout["holiday" if holiday else "standard"]
    start, written_for = section["story_pages_start"], section["story_cards"]
    shift = story_cards - written_for

    def moved(page: int) -> int:
        return page + shift if page >= start + written_for else page

    cards = {card_id: page for card_id, page in section["cards"].items() if page < start}
    for n in range(1, story_cards + 1):
        cards[f"story_{n}"] = start + n - 1
    cards.update({card_id: moved(page) for card_id, page in section["cards"].items() if page >= start})
    fixed = {name: moved(page) for name, page in section["fixed"].items()}
    return {"cards": cards, "fixed": fixed}


def deck_page_map(deck: dict, layout: dict, series_path: Path = SERIES_PATH) -> dict:
    """page_map() for one deck.json dict: picks standard/holiday and the deck's story count."""
    _, n, _ = story_card_count(deck, series_path)
    return page_map(layout, bool(deck.get("holiday")), n)
