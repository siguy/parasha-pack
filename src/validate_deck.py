"""
Check a v3 deck.json for mistakes before images are generated or cards exported.

Think of it as a spell-checker for a whole deck: it reads deck.json and lists
every problem it finds, grouped as ERRORS (must fix) and WARNINGS (look at it).

Usage (from the repo root):
    python3 src/validate_deck.py decks/bereshit/deck.json
    python3 src/validate_deck.py decks/bereshit/deck.json --strict   # warnings count as errors
    python3 src/validate_deck.py decks/bereshit/deck.json --json     # machine-readable output

Exit code: 0 = no errors, 1 = errors found (or warnings, with --strict).

What it checks:
    1. JSON Schema (schemas/deck.v3.schema.json)
    2. Word budgets on the backs (objective, say, cues, ask)
    3. Card count and card types (10 standard / 12 holiday, decision D1; a sequence deck has
       one story card per item, so 6 + N cards: see src/deck_pattern.py)
    4. Characters: listed characters exist; named characters are listed; <= 4 per card
    5. Hebrew: nikud present; unpointed copies match; grammatical gender vs. character gender
    6. Transitions don't depend on card order
    7. Image prompts are scene-only and never depict God
    8. Guide page numbers match guide_layout.yaml
    9. Question types (distancing questions only on connection/home cards)
"""

import argparse
import json
import logging
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

import jsonschema
import yaml

import deck_pattern

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "deck.v3.schema.json"
LAYOUT_PATH = REPO_ROOT / "guide_layout.yaml"
CHARACTERS_DIR = REPO_ROOT / "characters"
GENDER_LEXICON_PATH = Path(__file__).resolve().parent / "hebrew_gender.yaml"
PROJECT_LOG = REPO_ROOT / "project.log"

logger = logging.getLogger("validate_deck")

# ---------------------------------------------------------------- rules (edit here)

# Word budgets for the card back (see docs/mockups/back-v3.html)
MAX_OBJECTIVE_WORDS = 10
MAX_SAY_WORDS = 50       # spoken words only: [cue] text is not counted
MAX_CUE_WORDS = 25       # all [cue] chips on one back, added together
MAX_ASK_ITEMS = 2
MAX_ASK_WORDS = 12
MAX_HOME_WORDS = 70      # all English text on the home card back
MAX_CHARACTERS_PER_CARD = 4  # Nano Banana 2 accepts up to 4 character references

# How many cards of each type a deck needs: see src/deck_pattern.py (decision D1 + sequence decks)

# Transitions must work in any teaching order, so no "first" / "next card"
DECK_ORDER_WORDS = ["first", "begins", "one more", "last card", "next card"]

# Image prompts are scene-only: style, layout and text are added by the system
BANNED_PROMPT_TERMS = ["=== STYLE", "=== COMPOSITION"]
BANNED_PROMPT_WORDS = ["text", "letters", "border", "frame"]
PERCENT_PATTERN = re.compile(r"\d+\s*%")
# Connection and home cards show the modern world; every other card is the story world
MODERN_WORLD_TYPES = {"connection", "home"}

# Never show God as a person (safety rule)
GOD_DEPICTION_PHRASES = ["god's face", "face of god", "god as a man", "old man in the clouds",
                         "hashem's face", "face of hashem", "hashem as a man"]

# Question types allowed only on some cards
DISTANCING_ALLOWED_TYPES = {"connection", "home"}

# Hebrew character ranges
HEBREW_LETTER = re.compile(r"[א-ת]")
NIKUD = re.compile(r"[ְ-ׇ]")
# Cantillation + vowel points + dots, but NOT maqaf (05BE), paseq (05C0) or sof pasuq (05C3),
# which separate words
POINTS = re.compile(r"[֑-ׇֽֿׁׂׅׄ]")
POINTED_WORD = re.compile(r"[א-ת֑-ׇֽֿׁׂׅׄ]+")


# ---------------------------------------------------------------- data

@dataclass
class Issue:
    severity: str  # "error" or "warning"
    card_id: str   # "deck" for deck-level problems
    field: str     # e.g. "back.say"
    message: str


class Report:
    """Collects issues while the checks run."""

    def __init__(self, deck_path: Path):
        self.deck_path = deck_path
        self.issues: list[Issue] = []
        self.card_count = 0
        self.deck_name = ""

    def error(self, card_id: str, field: str, message: str) -> None:
        self.issues.append(Issue("error", card_id, field, message))

    def warn(self, card_id: str, field: str, message: str) -> None:
        self.issues.append(Issue("warning", card_id, field, message))

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "warning"]


# ---------------------------------------------------------------- text helpers

def strip_nikud(text: str) -> str:
    """Remove vowel points and cantillation, keep the letters."""
    return POINTS.sub("", text)


def hebrew_words(text: str) -> list[str]:
    """Hebrew words in a string, letters only (nikud stripped)."""
    return re.findall(r"[א-ת]+", strip_nikud(text))


def pointed_hebrew_words(text: str) -> list[str]:
    """Hebrew words with their nikud kept (normalized so marks compare equal)."""
    return [unicodedata.normalize("NFC", w) for w in POINTED_WORD.findall(text)]


def cue_texts(markup: str) -> list[str]:
    """The [cue] chips in a 'say' string, without brackets."""
    return re.findall(r"\[([^\]]+)\]", markup)


def count_words(text: str) -> int:
    """Count words that contain a letter or digit (so '…' and '—' don't count)."""
    return sum(1 for token in text.split() if re.search(r"\w", token))


def spoken_text(markup: str) -> str:
    """'say' markup with [cues] removed and ** bold markers dropped."""
    return re.sub(r"\[[^\]]*\]", " ", markup).replace("**", "")


def contains_phrase(text: str, phrase: str) -> bool:
    """Whole-word, case-insensitive phrase match."""
    return re.search(rf"\b{re.escape(phrase)}\b", text, re.IGNORECASE) is not None


def walk_strings(value, path: str = ""):
    """Yield (path, string) for every string inside nested dicts/lists."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from walk_strings(child, f"{path}.{key}" if path else key)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk_strings(child, f"{path}[{i}]")


# ---------------------------------------------------------------- loading

def load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_character_library(deck_dir: Path, characters_dir: Path) -> tuple[dict, str]:
    """
    Return ({key: {"name_en": ..., "gender": ...}}, source_name).

    Looks in characters/{key}/character.yaml first (the shared library). If that
    folder doesn't exist yet, falls back to the deck's references/manifest.json.
    Returns ({}, "") when neither exists.
    """
    if characters_dir.is_dir():
        library = {}
        for yaml_path in sorted(characters_dir.glob("*/character.yaml")):
            try:
                data = load_yaml(yaml_path)
            except yaml.YAMLError as e:
                logger.error(f"{yaml_path}: could not read ({e}), skipping")
                continue
            key = yaml_path.parent.name
            library[key] = {"name_en": data.get("name_en") or key.title(), "gender": data.get("gender")}
        return library, str(characters_dir)

    manifest_path = deck_dir / "references" / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        library = {key: {"name_en": key.title(), "gender": None}
                   for key in manifest if key != "style_hero"}
        return library, str(manifest_path)

    return {}, ""


# ---------------------------------------------------------------- checks

def check_schema(deck: dict, schema: dict, report: Report) -> None:
    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(deck), key=lambda e: list(e.absolute_path)):
        path = list(err.absolute_path)
        card_id = "deck"
        if len(path) >= 2 and path[0] == "cards" and isinstance(path[1], int):
            cards = deck.get("cards", [])
            card_id = cards[path[1]].get("card_id", f"cards[{path[1]}]") if path[1] < len(cards) else "deck"
            path = path[2:]
        field = ".".join(str(p) for p in path) or "(root)"
        report.error(card_id, field, f"schema: {err.message[:200]}")


def check_card_counts(deck: dict, report: Report, series_path: Path = deck_pattern.SERIES_PATH) -> None:
    cards = deck.get("cards", [])
    holiday = bool(deck.get("holiday"))
    pattern, story_cards, problem = deck_pattern.story_card_count(deck, series_path)
    if problem:
        report.error("deck", "deck_pattern", problem)
    expected = deck_pattern.expected_type_counts(holiday, story_cards)
    if pattern == deck_pattern.STANDARD:
        kind = "holiday" if holiday else "standard"
    else:
        kind = f"holiday {pattern}" if holiday else pattern
    total = sum(expected.values())
    if len(cards) != total:
        report.error("deck", "cards", f"{kind} deck needs {total} cards, found {len(cards)}")

    actual: dict[str, int] = {}
    for card in cards:
        actual[card.get("card_type", "?")] = actual.get(card.get("card_type", "?"), 0) + 1
    for card_type in sorted(set(expected) | set(actual)):
        want, got = expected.get(card_type, 0), actual.get(card_type, 0)
        if want != got:
            report.error("deck", "cards", f"{kind} deck needs {want} '{card_type}' card(s), found {got}")


def check_budgets(card: dict, report: Report) -> None:
    cid = card.get("card_id", "?")
    back = card.get("back") or {}

    objective = back.get("objective", "")
    n = count_words(objective.replace("**", ""))
    if n > MAX_OBJECTIVE_WORDS:
        report.error(cid, "back.objective", f"{n} words (max {MAX_OBJECTIVE_WORDS})")
    if not objective.strip():
        report.warn(cid, "back.objective", "empty")

    if card.get("card_type") == "home":
        english = [objective, back.get("transition", ""),
                   (back.get("shabbat_question") or {}).get("en", "")]
        english += [(back.get("hebrew") or {}).get(k, "") for k in ("meaning", "gesture")]
        english += [item.get("text", "") for item in back.get("try_at_home", [])]
        n = count_words(" ".join(english).replace("**", ""))
        if n > MAX_HOME_WORDS:
            report.warn(cid, "back", f"home card has {n} English words (max {MAX_HOME_WORDS})")
        return

    say = back.get("say", "")
    n = count_words(spoken_text(say))
    if n > MAX_SAY_WORDS:
        report.error(cid, "back.say", f"{n} spoken words (max {MAX_SAY_WORDS})")
    cue_words = sum(count_words(c) for c in cue_texts(say))
    if cue_words > MAX_CUE_WORDS:
        report.error(cid, "back.say", f"{cue_words} words inside [cues] (max {MAX_CUE_WORDS})")

    asks = back.get("ask", [])
    if len(asks) > MAX_ASK_ITEMS:
        report.error(cid, "back.ask", f"{len(asks)} questions (max {MAX_ASK_ITEMS})")
    for i, ask in enumerate(asks):
        n = count_words(ask.get("text", ""))
        if n > MAX_ASK_WORDS:
            report.error(cid, f"back.ask[{i}]", f"{n} words (max {MAX_ASK_WORDS})")
        if ask.get("type") == "distancing" and card.get("card_type") not in DISTANCING_ALLOWED_TYPES:
            report.warn(cid, f"back.ask[{i}]", "'distancing' questions belong on connection/home cards")


def check_required_by_type(card: dict, report: Report) -> None:
    cid, ctype, back = card.get("card_id", "?"), card.get("card_type"), card.get("back") or {}
    if ctype == "power_word" and not back.get("trio"):
        report.error(cid, "back.trio", "power_word cards need the 3-box trio")
    if ctype == "story" and not card.get("hebrew_keyword"):
        report.warn(cid, "hebrew_keyword", "story card has no Hebrew keyword badge")
    if ctype != "home" and not back.get("guide_ref"):
        report.warn(cid, "back.guide_ref", "no 'Guide p.N' link")


def check_characters(card: dict, library: dict, deck_names: dict, report: Report) -> None:
    cid = card.get("card_id", "?")
    in_scene = card.get("characters_in_scene", [])

    if library:
        for key in in_scene:
            if key not in library:
                report.error(cid, "characters_in_scene", f"'{key}' is not in the character library")

    if len(in_scene) > MAX_CHARACTERS_PER_CARD:
        report.warn(cid, "characters_in_scene",
                    f"{len(in_scene)} characters (Nano Banana 2 takes at most {MAX_CHARACTERS_PER_CARD} references)")

    # Every known character named in the prompt should be listed, so its reference is sent
    prompt = card.get("image_prompt", "")
    for key, name in deck_names.items():
        if key not in in_scene and contains_phrase(prompt, name):
            report.warn(cid, "image_prompt", f"mentions {name} but '{key}' is not in characters_in_scene")


def is_vocab_field(path: str) -> bool:
    return path in ("back.hebrew.word", "hebrew_keyword.word")


def is_hebrew_field(path: str) -> bool:
    last = path.split(".")[-1]
    return is_vocab_field(path) or last.endswith("_he") or last == "he"


def check_nikud(item: dict, card_id: str, report: Report) -> None:
    strings = dict(walk_strings(item))
    for path, text in strings.items():
        if is_hebrew_field(path) and HEBREW_LETTER.search(text) and not NIKUD.search(text):
            if is_vocab_field(path):
                report.error(card_id, path, f"Hebrew vocabulary word has no nikud: {text}")
            else:
                report.warn(card_id, path, f"Hebrew has no nikud: {text}")

        # Paired fields: 'word_unpointed' must equal 'word' with nikud removed
        for suffix in ("_unpointed", "_plain"):
            if path.endswith(suffix):
                pointed = strings.get(path[: -len(suffix)])
                if pointed is not None and strip_nikud(pointed) != text:
                    report.error(card_id, path, f"'{text}' doesn't match the pointed form '{pointed}'")


def load_gender_lexicon(path: Path = GENDER_LEXICON_PATH) -> tuple[list[dict], dict]:
    data = load_yaml(path)
    return data.get("pairs", []), data.get("known_character_genders", {})


def gender_of_word(word_pointed: str, pairs: list[dict]) -> tuple[str, dict] | None:
    """Return ("male"|"female", pair) if the word is a gendered form from the lexicon."""
    letters = strip_nikud(word_pointed)
    for pair in pairs:
        m, f = pair["masculine"], pair["feminine"]
        m_letters, f_letters = strip_nikud(m), strip_nikud(f)
        if m_letters == f_letters:
            # Same letters (יפה): only the nikud tells them apart
            if word_pointed == unicodedata.normalize("NFC", m):
                return "male", pair
            if word_pointed == unicodedata.normalize("NFC", f):
                return "female", pair
        elif letters == m_letters:
            return "male", pair
        elif letters == f_letters:
            return "female", pair
    return None


def note_mentions_both(note: str, pair: dict) -> bool:
    if strip_nikud(pair["masculine"]) == strip_nikud(pair["feminine"]):
        words = pointed_hebrew_words(note)
        return (unicodedata.normalize("NFC", pair["masculine"]) in words
                and unicodedata.normalize("NFC", pair["feminine"]) in words)
    words = hebrew_words(note)
    return strip_nikud(pair["masculine"]) in words and strip_nikud(pair["feminine"]) in words


def check_gender(card: dict, genders: dict, pairs: list[dict], report: Report) -> None:
    """Masculine Hebrew on an all-female card (or the reverse) is an error."""
    cid = card.get("card_id", "?")
    in_scene = card.get("characters_in_scene", [])
    card_genders = {genders.get(key) for key in in_scene}
    if not in_scene or None in card_genders or len(card_genders) != 1:
        return  # no characters, unknown gender, or a mixed group: nothing to check
    card_gender = card_genders.pop()

    note = ((card.get("back") or {}).get("hebrew") or {}).get("note", "")
    fields = {"title_he": card.get("title_he", ""), "hebrew_keyword": card.get("hebrew_keyword") or {},
              "back": card.get("back") or {}}
    for path, text in walk_strings(fields):
        if path == "back.hebrew.note":
            continue
        for word in pointed_hebrew_words(text):
            found = gender_of_word(word, pairs)
            if not found:
                continue
            word_gender, pair = found
            if word_gender != card_gender and not note_mentions_both(note, pair):
                right = pair["feminine"] if card_gender == "female" else pair["masculine"]
                report.error(cid, path,
                             f"'{word}' is the {'masculine' if word_gender == 'male' else 'feminine'} form, "
                             f"but the character(s) {in_scene} are {card_gender}: use '{right}' "
                             f"(or mention both forms in back.hebrew.note)")


def check_transition(card: dict, report: Report) -> None:
    cid = card.get("card_id", "?")
    transition = (card.get("back") or {}).get("transition", "")
    for phrase in DECK_ORDER_WORDS:
        if contains_phrase(transition, phrase):
            report.warn(cid, "back.transition", f"mentions deck order (\"{phrase}\"): cards may be taught in any order")


def check_image_prompt(card: dict, report: Report) -> None:
    cid = card.get("card_id", "?")
    prompt = card.get("image_prompt", "")

    for phrase in GOD_DEPICTION_PHRASES:
        if phrase in prompt.lower():
            report.error(cid, "image_prompt", f"depicts God as a person (\"{phrase}\"): show only light")

    for term in BANNED_PROMPT_TERMS:
        if term in prompt:
            report.warn(cid, "image_prompt", f"contains '{term}': prompts are scene-only")
    for word in BANNED_PROMPT_WORDS:
        if contains_phrase(prompt, word):
            report.warn(cid, "image_prompt", f"contains '{word}': text and borders are added by the Card Designer")
    if PERCENT_PATTERN.search(prompt):
        report.warn(cid, "image_prompt", f"contains a percentage ('{PERCENT_PATTERN.search(prompt).group()}'): "
                                         "layout is added by the system")
    if card.get("card_type") not in MODERN_WORLD_TYPES and contains_phrase(prompt, "Star of David"):
        report.warn(cid, "image_prompt", "Star of David in a story-world scene (anachronism)")


def check_guide_ref(card: dict, pages: dict, kind: str, report: Report) -> None:
    """pages = {card_id: page} for this deck (deck_pattern.deck_page_map(...)['cards'])."""
    cid = card.get("card_id", "?")
    guide_ref = (card.get("back") or {}).get("guide_ref")
    if not guide_ref:
        return
    expected = pages.get(cid)
    if expected is None:
        report.error(cid, "back.guide_ref.page", f"'{cid}' has no slot in the {kind} guide layout")
    elif guide_ref.get("page") != expected:
        report.error(cid, "back.guide_ref.page",
                     f"says p.{guide_ref.get('page')}, but guide_layout.yaml puts {cid} on p.{expected}")


def check_todos(item: dict, card_id: str, report: Report) -> None:
    """One warning per card listing every field that still says TODO."""
    fields = [path for path, text in walk_strings(item) if "TODO" in text]
    if fields:
        report.warn(card_id, "TODO", f"placeholder text still in: {', '.join(fields)}")


# ---------------------------------------------------------------- main entry

def validate_deck(deck_path, characters_dir: Path = CHARACTERS_DIR, layout_path: Path = LAYOUT_PATH,
                  schema_path: Path = SCHEMA_PATH, series_path: Path = deck_pattern.SERIES_PATH) -> Report:
    """Run every check on one deck.json and return the Report."""
    deck_path = Path(deck_path)
    report = Report(deck_path)
    try:
        deck = json.loads(deck_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        report.error("deck", "(file)", f"could not read deck.json: {e}")
        return report

    cards = deck.get("cards", [])
    report.card_count = len(cards)
    report.deck_name = deck.get("parasha_en", deck.get("id", deck_path.parent.name))
    logger.debug(f"{deck_path}: loaded {len(cards)} cards")

    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    layout = load_yaml(Path(layout_path))
    pairs, fallback_genders = load_gender_lexicon()
    library, library_source = load_character_library(deck_path.parent, Path(characters_dir))
    if not library:
        report.warn("deck", "characters_in_scene",
                    "no character library found (characters/ or references/manifest.json): "
                    "character keys not checked")

    # Gender: library first, then the lexicon's fallback list
    genders = {key: (library.get(key) or {}).get("gender") or fallback_genders.get(key)
               for card in cards for key in card.get("characters_in_scene", [])}
    # Names to look for in prompts: the library plus every character used in this deck
    deck_names = {key: info["name_en"] for key, info in library.items()}
    for key in genders:
        deck_names.setdefault(key, key.title())

    check_schema(deck, schema, report)
    check_card_counts(deck, report, series_path)
    deck_fields = {k: v for k, v in deck.items() if k != "cards"}
    check_todos(deck_fields, "deck", report)
    check_nikud(deck_fields, "deck", report)
    kind = "holiday" if deck.get("holiday") else "standard"
    guide_pages = deck_pattern.deck_page_map(deck, layout, series_path)["cards"]
    for card in cards:
        if not isinstance(card, dict):
            continue
        check_todos(card, card.get("card_id", "?"), report)
        check_budgets(card, report)
        check_required_by_type(card, report)
        check_characters(card, library, deck_names, report)
        check_nikud(card, card.get("card_id", "?"), report)
        check_gender(card, genders, pairs, report)
        check_transition(card, report)
        check_image_prompt(card, report)
        check_guide_ref(card, guide_pages, kind, report)

    # Group issues by card in deck order (deck-level first); sorted() keeps check order within a card
    order = {"deck": -1, **{c.get("card_id"): i for i, c in enumerate(cards) if isinstance(c, dict)}}
    report.issues = sorted(report.issues, key=lambda issue: order.get(issue.card_id, len(order)))
    logger.debug(f"{deck_path}: character library = {library_source or 'none'} ({len(library)} characters)")
    return report


def format_report(report: Report, strict: bool = False) -> str:
    """A readable text report: errors first, then warnings, each grouped by card."""
    lines = [f"Validating {report.deck_path} ({report.deck_name}, {report.card_count} cards)", ""]
    for title, issues in (("ERRORS", report.errors), ("WARNINGS", report.warnings)):
        lines.append(f"{title} ({len(issues)})")
        if not issues:
            lines.append("  none")
        current = None
        for issue in issues:
            if issue.card_id != current:
                current = issue.card_id
                lines.append(f"  [{current}]")
            lines.append(f"    {issue.field}: {issue.message}")
        lines.append("")
    failed = bool(report.errors) or (strict and bool(report.warnings))
    lines.append(f"Result: {'FAIL' if failed else 'PASS'} "
                 f"({len(report.errors)} errors, {len(report.warnings)} warnings{', strict' if strict else ''})")
    return "\n".join(lines)


def setup_logging() -> None:
    """Errors (a deck that fails, an unreadable file) are appended to project.log."""
    if logger.handlers:
        return
    error_file = logging.FileHandler(PROJECT_LOG, delay=True)
    error_file.setLevel(logging.ERROR)
    error_file.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    logger.setLevel(logging.INFO)
    logger.addHandler(error_file)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check a v3 deck.json for mistakes.")
    parser.add_argument("decks", nargs="+", help="Path(s) to deck.json")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--json", action="store_true", help="Print the report as JSON")
    parser.add_argument("--characters-dir", default=str(CHARACTERS_DIR), help="Character library folder")
    args = parser.parse_args(argv)
    setup_logging()

    exit_code = 0
    json_out = []
    for deck_path in args.decks:
        report = validate_deck(deck_path, characters_dir=Path(args.characters_dir))
        failed = bool(report.errors) or (args.strict and bool(report.warnings))
        if failed:
            exit_code = 1
            logger.error(f"{deck_path}: {len(report.errors)} errors, {len(report.warnings)} warnings "
                         f"({report.card_count} cards)")
        if args.json:
            json_out.append({"deck": str(deck_path), "cards": report.card_count, "passed": not failed,
                             "errors": [asdict(i) for i in report.errors],
                             "warnings": [asdict(i) for i in report.warnings]})
        else:
            print(format_report(report, args.strict))
            print()
    if args.json:
        print(json.dumps(json_out if len(json_out) > 1 else json_out[0], ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
