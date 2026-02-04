"""
CLI interface for Parasha Pack workflows.
"""

import argparse
import os

from .character import CharacterWorkflow
from .deck import DeckWorkflow
from .research import (
    list_available_characters,
    list_available_parshiyot,
    get_character_summary,
    get_parasha_summary,
)


def main():
    """CLI interface for workflows."""
    parser = argparse.ArgumentParser(description="Parasha Pack Workflows")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Character command
    char_parser = subparsers.add_parser("character", help="Character workflow")
    char_parser.add_argument("name", help="Character name")
    char_parser.add_argument("--deck", "-d", help="Deck path")
    char_parser.add_argument("--generate", "-g", action="store_true", help="Generate reference images")
    char_parser.add_argument("--api-key", help="Gemini API key")

    # Deck command
    deck_parser = subparsers.add_parser("deck", help="Deck workflow")
    deck_parser.add_argument("parasha", help="Parasha name")
    deck_parser.add_argument("--output", "-o", help="Output directory")

    # Research command
    research_parser = subparsers.add_parser("research", help="Research only (no generation)")
    research_parser.add_argument("type", choices=["character", "parasha"], help="What to research")
    research_parser.add_argument("name", help="Name to research")

    # List command
    list_parser = subparsers.add_parser("list", help="List available research data")
    list_parser.add_argument("type", choices=["characters", "parshiyot"], help="What to list")

    args = parser.parse_args()

    if args.command == "character":
        api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
        CharacterWorkflow.create(
            args.name,
            deck_path=args.deck,
            api_key=api_key,
            generate_images=args.generate and bool(api_key)
        )

    elif args.command == "deck":
        DeckWorkflow.full_create(args.parasha, args.output)

    elif args.command == "research":
        if args.type == "character":
            print(get_character_summary(args.name))
        else:
            print(get_parasha_summary(args.name))

    elif args.command == "list":
        if args.type == "characters":
            print("Available characters with research data:")
            for char in list_available_characters():
                print(f"  - {char}")
        else:
            print("Available parshiyot with research data:")
            for p in list_available_parshiyot():
                print(f"  - {p}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
