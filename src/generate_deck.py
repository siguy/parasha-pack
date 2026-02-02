#!/usr/bin/env python3
"""
Generate a new card deck for the current parasha.

This script:
1. Fetches the current parasha from Sefaria API
2. Creates a deck template with appropriate theming
3. Outputs the deck structure for manual content creation

Usage:
    python generate_deck.py [--parasha NAME] [--output PATH]
"""

import argparse
import json
import os
from datetime import datetime

from sefaria_client import fetch_current_parasha, get_border_color, PARASHA_THEMES
from schema import (
    Deck,
    AnchorCard,
    SpotlightCard,
    ActionCard,
    ThinkerCard,
    PowerWordCard,
    FEELING_FACES,
)


def create_deck_template(parasha_name: str, parasha_he: str, ref: str, theme: str, border_color: str) -> dict:
    """
    Create a deck template with placeholder cards.

    Args:
        parasha_name: English name of the parasha
        parasha_he: Hebrew name of the parasha
        ref: Scripture reference
        theme: Theme category
        border_color: Hex color for borders

    Returns:
        Dictionary representing the deck
    """
    deck = {
        "parasha_en": parasha_name,
        "parasha_he": parasha_he,
        "ref": ref,
        "border_color": border_color,
        "theme": theme,
        "version": "1.0",
        "target_age": "4-6",
        "card_count": 0,
        "mitzvah_connection": "",
        "cards": []
    }

    # Add template cards

    # 1. Anchor Card
    anchor = {
        "card_id": "anchor_1",
        "card_type": "anchor",
        "title_en": parasha_name,
        "title_he": parasha_he,
        "emotional_hook_en": "This week is about feeling [EMOTION]!",
        "emotional_hook_he": "",
        "symbol_description": "[DESCRIBE CENTRAL SYMBOL]",
        "border_color": border_color,
        "image_prompt": "",
        "image_path": None,
        "teacher_script": ""
    }
    deck["cards"].append(anchor)

    # 2-3. Spotlight Cards (2 characters)
    for i in range(1, 3):
        spotlight = {
            "card_id": f"spotlight_{i}",
            "card_type": "spotlight",
            "title_en": f"[CHARACTER {i} NAME]",
            "title_he": "",
            "character_name_en": "",
            "character_name_he": "",
            "emotion_label": "[happy/proud/brave/etc]",
            "character_trait": "",
            "character_description_en": "",
            "character_description_he": "",
            "image_prompt": "",
            "image_path": None,
            "teacher_script": ""
        }
        deck["cards"].append(spotlight)

    # 4-8. Action Cards (5 scenes)
    for i in range(1, 6):
        action = {
            "card_id": f"action_{i}",
            "card_type": "action",
            "title_en": f"[SCENE {i} TITLE]",
            "title_he": "",
            "sequence_number": i,
            "hebrew_key_word": "",
            "hebrew_key_word_nikud": "",
            "english_description": "",
            "roleplay_prompt": "Act it out: [ACTION]!",
            "emotional_reactions": [],
            "image_prompt": "",
            "image_path": None,
            "teacher_script": ""
        }
        deck["cards"].append(action)

    # 9-10. Thinker Cards (2 discussion cards)
    for i in range(1, 3):
        thinker = {
            "card_id": f"thinker_{i}",
            "card_type": "thinker",
            "title_en": f"[DISCUSSION THEME {i}]",
            "title_he": "",
            "questions": [
                {
                    "question_type": "emotional_empathy",
                    "question_en": "How do you think [character] felt when...?",
                    "question_he": ""
                },
                {
                    "question_type": "cognitive_empathy",
                    "question_en": "Why do you think [character] did...?",
                    "question_he": ""
                },
                {
                    "question_type": "connection",
                    "question_en": "Have you ever felt...? What did you do?",
                    "question_he": ""
                }
            ],
            "torah_talk_instruction": "Sit in a circle and share!",
            "feeling_faces": FEELING_FACES,
            "image_prompt": "",
            "image_path": None,
            "teacher_script": ""
        }
        deck["cards"].append(thinker)

    # 11-12. Power Word Cards (2 vocabulary words)
    for i in range(1, 3):
        power_word = {
            "card_id": f"power_word_{i}",
            "card_type": "power_word",
            "title_en": f"[WORD {i}] - [MEANING]",
            "title_he": "",
            "hebrew_word": "",
            "hebrew_word_nikud": "",
            "transliteration": "",
            "english_meaning": "",
            "example_sentence_en": "",
            "example_sentence_he": "",
            "is_emotion_word": False,
            "audio_qr_url": None,
            "image_prompt": "",
            "image_path": None,
            "teacher_script": ""
        }
        deck["cards"].append(power_word)

    deck["card_count"] = len(deck["cards"])
    return deck


def main():
    parser = argparse.ArgumentParser(
        description="Generate a card deck template for a Torah portion"
    )
    parser.add_argument(
        "--parasha",
        type=str,
        help="Parasha name (if not specified, fetches current from Sefaria)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory path"
    )

    args = parser.parse_args()

    # Get parasha info
    if args.parasha:
        # Use provided parasha name
        parasha_name = args.parasha
        theme = PARASHA_THEMES.get(parasha_name, "covenant")
        border_color = get_border_color(parasha_name, "")
        parasha_he = ""  # Would need to look up
        ref = ""
        print(f"Creating deck for: {parasha_name}")
    else:
        # Fetch current parasha from Sefaria
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
    )

    # Determine output path
    if args.output:
        output_dir = args.output
    else:
        # Create in decks directory
        safe_name = parasha_name.lower().replace("'", "").replace(" ", "_")
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "decks",
            safe_name
        )

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)

    # Write deck.json
    deck_path = os.path.join(output_dir, "deck.json")
    with open(deck_path, 'w', encoding='utf-8') as f:
        json.dump(deck, f, indent=2, ensure_ascii=False)
    print(f"\nCreated deck template: {deck_path}")

    # Write empty feedback.json
    feedback = {
        "parasha": parasha_name,
        "deck_version": "1.0",
        "review_date": None,
        "cards": [],
        "global_feedback": ""
    }
    feedback_path = os.path.join(output_dir, "feedback.json")
    with open(feedback_path, 'w', encoding='utf-8') as f:
        json.dump(feedback, f, indent=2, ensure_ascii=False)
    print(f"Created feedback file: {feedback_path}")

    print(f"\nDeck template created with {deck['card_count']} placeholder cards.")
    print("Edit deck.json to fill in the content for each card.")
    print("\nCard structure:")
    print("  1 Anchor card (parasha introduction)")
    print("  2 Spotlight cards (character introductions)")
    print("  5 Action cards (story sequence)")
    print("  2 Thinker cards (discussion questions)")
    print("  2 Power Word cards (vocabulary)")


if __name__ == "__main__":
    main()
