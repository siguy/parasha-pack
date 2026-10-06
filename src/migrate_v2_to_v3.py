"""
Migrate a v2 deck.json to the v3 format (schemas/deck.v3.schema.json).

This is a MECHANICAL move of fields. It does not rewrite or shorten any
content, so migrated decks will usually be over the v3 word budgets
(say <= 50 words, etc.). That is expected: the validator will flag them and
the content gets rewritten by hand later.

Like moving house: every box goes into the right room of the new house,
but nobody unpacks it yet. Anything that has no room in the new house is
listed at the end so you know what was left on the truck.

Usage:
    python src/migrate_v2_to_v3.py decks/purim/deck.json [more decks...]

The file is rewritten in place. Git is the backup (use `git diff` to review,
`git checkout -- <file>` to undo).
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger("migrate_v2_to_v3")
PROJECT_LOG = Path(__file__).resolve().parent.parent / "project.log"

# Feeling faces we can draw as SVG (see card-designer/components/cards/icons.tsx)
SVG_FACES = {"happy", "proud", "calm", "excited", "scared", "brave", "sad", "surprised"}

# Default minutes per card type (v2 had no timing info)
DEFAULT_MINUTES = {"anchor": 5, "spotlight": 3, "story": 5, "connection": 5, "tradition": 5, "power_word": 3}

# Neutral filler used when a v2 deck has no 5-color palette
FILLER_PALETTE = ["#1E293B", "#F5F0E8", "#475569", "#E7E2D9"]

# v2 card fields that the migration moves somewhere. Anything else is reported.
MAPPED_CARD_FIELDS = {
    "card_id", "card_type", "title_en", "title_he", "characters_in_scene", "image_prompt",
    "image_path", "sequence_number", "teacher_script", "roleplay_prompt", "discussion_prompts",
    "questions", "teacher_tip", "teaching_moment_en", "transition_line", "optional",
    "hebrew_key_word", "hebrew_key_word_nikud", "english_key_word", "description_en",
    "english_description", "character_description_en", "practice_description_en",
    "kid_friendly_explanation_en", "hebrew_term", "hebrew_term_meaning", "hebrew_word",
    "hebrew_word_nikud", "english_meaning", "pronunciation_guide", "emotion_label_en",
    "emotion_label_he", "feeling_faces", "front",
}


def setup_logging() -> None:
    """Print INFO+ to the console and append ERROR+ to project.log."""
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(message)s"))
    error_file = logging.FileHandler(PROJECT_LOG, delay=True)
    error_file.setLevel(logging.ERROR)
    error_file.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    logger.setLevel(logging.INFO)
    logger.addHandler(console)
    logger.addHandler(error_file)


# ---------------------------------------------------------------- helpers

def script_to_say(script: str, roleplay: str) -> str:
    """
    Turn a v2 teacher_script into v3 'say' markup.

    v2 scripts are plain text with occasional [stage directions]. In v3,
    spoken words are **bold** and actions are [cues]. So we bold every
    piece of text between the [..] parts and keep the [..] parts as cues.
    The roleplay prompt ("Act it out: ...") is appended as one more cue.
    """
    parts = re.split(r"(\[[^\]]*\])", script or "")
    out = []
    for part in parts:
        if part.startswith("[") and part.endswith("]"):
            out.append(part)
        elif part.strip():
            out.append(f"**{part.strip()}**")
    if roleplay:
        cue = re.sub(r"^act it out:\s*", "", roleplay.strip(), flags=re.IGNORECASE)
        out.append(f"[{cue}]")
    return " ".join(out)


def guess_ask_type(text: str) -> str:
    """'open' unless it is obviously a show-me question."""
    return "nonverbal" if text.strip().lower().startswith("show") else "open"


# v2 connection question_type -> v3 ask type
CONNECTION_ASK_TYPES = {"empathy": "distancing"}


def build_ask(card: dict) -> list:
    if card.get("discussion_prompts"):
        return [{"text": q, "type": guess_ask_type(q)} for q in card["discussion_prompts"][:2]]
    if card.get("questions"):
        return [
            {"text": q.get("question_en", ""), "type": CONNECTION_ASK_TYPES.get(q.get("question_type"), "open")}
            for q in card["questions"][:2]
        ]
    return []


def build_hebrew(card: dict):
    """The Hebrew strip on the back (word, translit, meaning, gesture)."""
    t = card["card_type"]
    if t == "story" and card.get("hebrew_key_word_nikud"):
        return {"word": card["hebrew_key_word_nikud"], "translit": "", "meaning": card.get("english_key_word", ""), "gesture": ""}
    if t == "spotlight" and card.get("emotion_label_he"):
        return {"word": card["emotion_label_he"], "translit": "", "meaning": card.get("emotion_label_en", ""), "gesture": ""}
    if t == "tradition" and card.get("hebrew_term"):
        return {"word": card["hebrew_term"], "translit": "", "meaning": card.get("hebrew_term_meaning", ""), "gesture": ""}
    if t == "power_word" and (card.get("hebrew_word_nikud") or card.get("hebrew_word")):
        # "Gee-BOR. Rhymes with 'dinosaur'!" -> "Gee-BOR"
        translit = (card.get("pronunciation_guide") or "").split(".")[0].strip()
        return {"word": card.get("hebrew_word_nikud") or card["hebrew_word"], "translit": translit,
                "meaning": card.get("english_meaning", ""), "gesture": ""}
    return None


def build_pshat(card: dict) -> str:
    """The plain-meaning summary for the guide, from whichever v2 field held it."""
    for field in ("description_en", "english_description", "character_description_en",
                  "practice_description_en", "kid_friendly_explanation_en"):
        if card.get(field):
            return card[field]
    return ""


def migrate_card(card: dict, flags: list) -> dict:
    cid, t = card["card_id"], card["card_type"]

    back = {
        "objective": "",
        "say": script_to_say(card.get("teacher_script", ""), card.get("roleplay_prompt", "")),
        "ask": build_ask(card),
        "minutes": DEFAULT_MINUTES.get(t, 5),
        "core": not card.get("optional", False),
        "transition": card.get("transition_line", ""),
    }
    flags.append(f"{cid}: back.objective is empty (write one, <=10 words)")
    flags.append(f"{cid}: back.minutes set to default {back['minutes']}")
    flags.append(f"{cid}: back.guide_ref not set (no guide page map yet)")
    if not back["transition"]:
        flags.append(f"{cid}: no transition_line in v2, back.transition is empty")

    hebrew = build_hebrew(card)
    if hebrew:
        back["hebrew"] = hebrew
        flags.append(f"{cid}: back.hebrew needs translit/gesture filled in")

    if t == "connection" and card.get("feeling_faces"):
        labels = [(f.get("label_en") or "").lower() for f in card["feeling_faces"]]
        back["faces"] = [l for l in labels if l in SVG_FACES][:4]
        dropped = [l for l in labels if l not in SVG_FACES]
        if dropped:
            flags.append(f"{cid}: feeling faces with no SVG drawing were dropped: {dropped}")

    new = {
        "card_id": cid,
        "card_type": t,
        "title_en": card.get("title_en") or (card.get("front") or {}).get("english_title", ""),
        "title_he": card.get("title_he") or (card.get("front") or {}).get("hebrew_title", ""),
        "characters_in_scene": card.get("characters_in_scene", []),
        "image_prompt": card.get("image_prompt", ""),
        "image_path": (card.get("image_path") or f"raw/{cid}.png").replace("images/", "raw/"),
    }
    if t == "story":
        new["sequence_number"] = card.get("sequence_number", 1)
        if card.get("hebrew_key_word_nikud"):
            new["hebrew_keyword"] = {"word": card["hebrew_key_word_nikud"], "translit": "",
                                     "meaning": (card.get("english_key_word") or "").lower()}
            flags.append(f"{cid}: hebrew_keyword.translit is empty")

    new["back"] = back
    new["guide"] = {
        "pshat": {"text": build_pshat(card), "refs": []},
        "sages": [],
        "hard_questions": [],
        "adapt": {"see": "", "do": "", "join": ""},
        "extend": card.get("teaching_moment_en", ""),
        "tip": card.get("teacher_tip", ""),
    }

    for field in sorted(set(card) - MAPPED_CARD_FIELDS):
        flags.append(f"{cid}: v2 field '{field}' has no v3 home (dropped)")
    return new


def migrate_deck(v2: dict, deck_id: str, flags: list) -> dict:
    is_holiday = "holiday_en" in v2 or v2.get("content_type") == "holiday"
    color = v2.get("border_color", "#5B2D8E")

    # Week plan: v2 'session' numbers become days. No sessions -> one day.
    days = {}
    for card in v2["cards"]:
        days.setdefault(card.get("session", 1), []).append(card["card_id"])
    if not any("session" in c for c in v2["cards"]):
        flags.append("deck: no sessions in v2, week_plan has a single day")
    week_plan = [{"day": d, "label": f"Session {d}", "cards": ids} for d, ids in sorted(days.items())]

    theme = v2.get("theme", "")
    deck = {
        "id": deck_id,
        "version": "3.0",
        "parasha_en": v2.get("parasha_en") or v2.get("holiday_en", deck_id.title()),
        "parasha_he": v2.get("parasha_he") or v2.get("holiday_he", ""),
        "holiday": is_holiday,
    }
    if v2.get("ref") or v2.get("source"):
        deck["ref"] = v2.get("ref") or v2.get("source")
    deck.update({
        "value": {"en": theme.capitalize(), "he": "", "kid_phrase": v2.get("emotional_core", ""), "gesture": ""},
        "palette": [color] + FILLER_PALETTE,
        "web_theme": {"primary": color, "secondary": "#475569", "accent": color, "wash": "#F5F0E8"},
        "story_world": v2.get("story_world", ""),
        "week_plan": week_plan,
        "cards": [migrate_card(c, flags) for c in v2["cards"]],
    })
    flags.append("deck: value.he and value.gesture are empty")
    flags.append("deck: palette/web_theme are placeholders built from border_color")

    known = {"parasha_en", "parasha_he", "holiday_en", "holiday_he", "ref", "source", "content_type",
             "border_color", "theme", "version", "story_world", "emotional_core", "sessions", "cards"}
    for field in sorted(set(v2) - known):
        flags.append(f"deck: v2 field '{field}' has no v3 home (dropped)")
    return deck


def main() -> int:
    setup_logging()
    parser = argparse.ArgumentParser(description="Migrate v2 deck.json files to v3 in place.")
    parser.add_argument("decks", nargs="+", type=Path, help="Paths to deck.json files")
    args = parser.parse_args()

    failures = 0
    for path in args.decks:
        try:
            v2 = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"{path}: could not read ({e}), skipping")
            failures += 1
            continue
        if v2.get("version") == "3.0":
            logger.warning(f"{path}: already v3, skipping")
            continue

        deck_id = path.parent.name
        flags = []
        v3 = migrate_deck(v2, deck_id, flags)
        path.write_text(json.dumps(v3, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        logger.info(f"\n{path}: migrated {len(v3['cards'])} cards (source: v{v2.get('version', '?')})")
        long_says = [c["card_id"] for c in v3["cards"] if len(re.sub(r"\*\*|\[[^\]]*\]", "", c["back"]["say"]).split()) > 50]
        logger.info(f"  cards over the 50-word SAY budget: {len(long_says)} {long_says}")
        logger.info(f"  {len(flags)} fields could not be mapped or need a human:")
        for f in flags:
            logger.info(f"    - {f}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
