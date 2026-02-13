#!/usr/bin/env python3
"""
Generate a new card deck template for a parasha or holiday.

Creates a deck.json with placeholder cards using v2 card types.
Image prompts should be SCENE DESCRIPTIONS ONLY — style, safety,
composition, and rules are injected automatically by generate_images.py.

Usage:
    python generate_deck.py                          # Current parasha from Sefaria
    python generate_deck.py --parasha "Yitro"        # Specific parasha
    python generate_deck.py --parasha "Purim" --holiday  # Holiday deck (adds tradition cards)
    python generate_deck.py --output ../decks/yitro  # Custom output path
"""

import argparse
import json
import os

from sefaria_client import fetch_current_parasha, get_border_color, PARASHA_THEMES
from schema import FEELING_FACES


def create_deck_template(
    parasha_name: str,
    parasha_he: str,
    ref: str,
    theme: str,
    border_color: str,
    is_holiday: bool = False,
) -> dict:
    """
    Create a v2 deck template with placeholder cards.

    Card types:
      - anchor: Parasha/holiday introduction
      - spotlight: Character portraits
      - story: Key narrative moments
      - connection: Discussion questions
      - tradition: Holiday practices (holiday decks only)
      - power_word: Hebrew vocabulary

    Image prompts should be SCENE DESCRIPTIONS ONLY.
    generate_images.py adds style, safety, composition, and rules at generation time.
    """
    deck_meta = {
        "parasha_en": parasha_name,
        "parasha_he": parasha_he,
        "ref": ref,
        "border_color": border_color,
        "theme": theme,
        "version": "2.0",
        "target_age": "4-6",
        "card_count": 0,
        "cards": []
    }

    if is_holiday:
        deck_meta["holiday_en"] = parasha_name
        deck_meta["holiday_he"] = parasha_he

    cards = deck_meta["cards"]

    # --- Anchor Card (1) ---
    cards.append({
        "card_id": "anchor_1",
        "card_type": "anchor",
        "title_en": parasha_name,
        "title_he": parasha_he,
        "emotional_hook_en": "[Opening hook — 'Have you ever...' or 'Today we meet...']",
        "emotional_hook_he": "",
        "symbol_description": "[Central symbol that represents this parasha/holiday]",
        "border_color": border_color,
        # Scene-only prompt. Style/safety/composition injected at generation time.
        "image_prompt": "",
        "image_path": None,
        "teacher_script": "",
        "session": 1,
    })

    # --- Spotlight Cards (2) ---
    for i in range(1, 3):
        cards.append({
            "card_id": f"spotlight_{i}",
            "card_type": "spotlight",
            "title_en": f"[Character {i} English Name]",
            "title_he": "",
            "character_name_en": "",
            "character_name_he": "",
            "emotion_label_en": "[brave/caring/wise/etc]",
            "emotion_label_he": "",
            "character_description_en": "",
            "character_description_he": "",
            "teaching_moment_en": "",
            "border_color": border_color,
            "image_prompt": "",
            "image_path": None,
            "teacher_script": "",
            "session": 1,
        })

    # --- Story Cards (4) ---
    for i in range(1, 5):
        cards.append({
            "card_id": f"story_{i}",
            "card_type": "story",
            "title_en": f"[Scene {i} Title]",
            "title_he": "",
            "sequence_number": i,
            "hebrew_key_word": "",
            "hebrew_key_word_nikud": "",
            "english_key_word": "",
            "english_description": "",
            "roleplay_prompt": "[Act it out: ...]",
            "border_color": border_color,
            "image_prompt": "",
            "image_path": None,
            "teacher_script": "",
            "session": 1,
        })

    # --- Connection Cards (2) ---
    for i in range(1, 3):
        cards.append({
            "card_id": f"connection_{i}",
            "card_type": "connection",
            "title_en": f"[Discussion Theme {i}]",
            "title_he": "",
            "questions": [
                {
                    "question_type": "personal",
                    "question_en": "Have you ever...?",
                    "question_he": "",
                },
                {
                    "question_type": "empathy",
                    "question_en": "How do you think [character] felt when...?",
                    "question_he": "",
                },
            ],
            "emojis": ["😊", "😢", "😮", "💪"],
            "border_color": border_color,
            "image_prompt": "",
            "image_path": None,
            "teacher_script": "",
            "session": 2,
        })

    # --- Tradition Cards (holiday decks only) ---
    if is_holiday:
        for i in range(1, 4):
            cards.append({
                "card_id": f"tradition_{i}",
                "card_type": "tradition",
                "title_en": f"[Tradition {i} Name]",
                "title_he": "",
                "story_connection_en": "[How this tradition connects to the story]",
                "story_connection_he": "",
                "practice_description_en": "[What we do for this tradition]",
                "practice_description_he": "",
                "child_action_en": "[How a child can participate]",
                "child_action_he": "",
                "hebrew_term": "",
                "hebrew_term_meaning": "",
                "border_color": border_color,
                "image_prompt": "",
                "image_path": None,
                "teacher_script": "",
                "session": 2,
            })

    # --- Power Word Card (1) ---
    cards.append({
        "card_id": "power_word_1",
        "card_type": "power_word",
        "title_en": "[Word] - [Meaning]",
        "title_he": "",
        "hebrew_word": "",
        "hebrew_word_nikud": "",
        "english_meaning": "",
        "example_sentence_en": "",
        "example_sentence_he": "",
        "kid_friendly_explanation_en": "",
        "kid_friendly_explanation_he": "",
        "border_color": border_color,
        "image_prompt": "",
        "image_path": None,
        "teacher_script": "",
        "session": 2,
    })

    deck_meta["card_count"] = len(cards)
    return deck_meta


def main():
    parser = argparse.ArgumentParser(
        description="Generate a card deck template for a Torah portion or holiday"
    )
    parser.add_argument(
        "--parasha", type=str,
        help="Parasha/holiday name (if not specified, fetches current from Sefaria)"
    )
    parser.add_argument(
        "--output", type=str,
        help="Output directory path"
    )
    parser.add_argument(
        "--holiday", action="store_true",
        help="Create a holiday deck (adds tradition cards)"
    )

    args = parser.parse_args()

    # Get parasha info
    if args.parasha:
        parasha_name = args.parasha
        theme = PARASHA_THEMES.get(parasha_name, "covenant")
        border_color = get_border_color(parasha_name, "")
        parasha_he = ""  # Would need to look up
        ref = ""
        print(f"Creating deck for: {parasha_name}")
    else:
        print("Fetching current parasha from Sefaria API...")
        parasha = fetch_current_parasha()

        if not parasha:
            print("Error: Could not fetch parasha from Sefaria API")
            return

        parasha_name = parasha.title_en
        parasha_he = parasha.title_he
        ref = parasha.ref
        theme = PARASHA_THEMES.get(parasha_name, "covenant")
        border_color = parasha.border_color

        print(f"Current parasha: {parasha_name} ({parasha_he})")
        print(f"Reference: {ref}")
        print(f"Theme: {theme}")
        print(f"Border color: {border_color}")

    # Create deck template
    deck = create_deck_template(
        parasha_name=parasha_name,
        parasha_he=parasha_he,
        ref=ref,
        theme=theme,
        border_color=border_color,
        is_holiday=args.holiday,
    )

    # Determine output path
    if args.output:
        output_dir = args.output
    else:
        safe_name = parasha_name.lower().replace("'", "").replace(" ", "_")
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "decks",
            safe_name
        )

    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "raw"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "references"), exist_ok=True)

    # Write deck.json
    deck_path = os.path.join(output_dir, "deck.json")
    with open(deck_path, 'w', encoding='utf-8') as f:
        json.dump(deck, f, indent=2, ensure_ascii=False)
    print(f"\nCreated deck template: {deck_path}")

    # Write empty feedback.json
    feedback = {
        "parasha": parasha_name,
        "deck_version": "2.0",
        "review_date": None,
        "cards": [],
        "global_feedback": ""
    }
    feedback_path = os.path.join(output_dir, "feedback.json")
    with open(feedback_path, 'w', encoding='utf-8') as f:
        json.dump(feedback, f, indent=2, ensure_ascii=False)
    print(f"Created feedback file: {feedback_path}")

    # Summary
    card_types = {}
    for card in deck["cards"]:
        t = card["card_type"]
        card_types[t] = card_types.get(t, 0) + 1

    print(f"\nDeck template created with {deck['card_count']} placeholder cards:")
    for card_type, count in card_types.items():
        print(f"  {count} {card_type} card{'s' if count > 1 else ''}")

    print(f"\nNext steps:")
    print(f"  1. Fill in card content in {deck_path}")
    print(f"  2. Write scene-only image prompts (no style/composition/rules)")
    print(f"  3. python generate_images.py {deck_path}")
    print(f"  4. cd ../card-designer && npm run export {os.path.basename(output_dir)}")


if __name__ == "__main__":
    main()
