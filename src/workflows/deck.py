"""
Deck workflow for Parasha Pack.

Complete workflow for creating a new deck with research, template, and structure.
"""

import json
from pathlib import Path
from typing import Optional

from .models import ParashaResearch
from .research import research_parasha


class DeckWorkflow:
    """
    Complete workflow for creating a new deck.

    Steps:
    1. research() - Gather parasha information
    2. create() - Generate deck template with smart defaults
    3. save_research() - Save research data for reference

    Example:
        workflow = DeckWorkflow("Beshalach")
        workflow.research()
        workflow.create(output_dir="decks/beshalach")
    """

    def __init__(self, parasha_name: str):
        """
        Initialize a deck workflow.

        Args:
            parasha_name: Name of the Torah portion
        """
        self.parasha_name = parasha_name
        self.research_data: Optional[ParashaResearch] = None
        self.deck_path: Optional[Path] = None
        self.deck_data: Optional[dict] = None

    def research(self) -> ParashaResearch:
        """
        Step 1: Research the parasha.

        Returns:
            ParashaResearch with story and educational information
        """
        print(f"\n{'='*50}")
        print(f"RESEARCHING PARASHA: {self.parasha_name}")
        print('='*50)

        self.research_data = research_parasha(self.parasha_name)

        print(f"\nName: {self.research_data.name_en} ({self.research_data.name_he})")
        print(f"Reference: {self.research_data.ref}")
        print(f"Theme: {self.research_data.suggested_theme}")
        print(f"Key events: {len(self.research_data.key_events)}")
        print(f"Characters: {', '.join(self.research_data.main_characters)}")

        return self.research_data

    def create(self, output_dir: str = None) -> dict:
        """
        Step 2: Create the deck template.

        Args:
            output_dir: Output directory for deck files

        Returns:
            Deck dictionary
        """
        if not self.research_data:
            self.research()

        print(f"\n{'='*50}")
        print(f"CREATING DECK: {self.parasha_name}")
        print('='*50)

        # Import generate_deck functionality
        try:
            from generate_deck import create_deck_template
        except ImportError:
            print("ERROR: generate_deck module not found")
            return {}

        self.deck_data = create_deck_template(
            parasha_name=self.research_data.name_en,
            parasha_he=self.research_data.name_he,
            ref=self.research_data.ref,
            theme=self.research_data.suggested_theme,
            border_color=self.research_data.border_color,
        )

        # Determine output path
        if output_dir:
            self.deck_path = Path(output_dir)
        else:
            safe_name = self.parasha_name.lower().replace("'", "").replace(" ", "_")
            self.deck_path = Path("decks") / safe_name

        # Create directories
        self.deck_path.mkdir(parents=True, exist_ok=True)
        (self.deck_path / "images").mkdir(exist_ok=True)
        (self.deck_path / "references").mkdir(exist_ok=True)
        (self.deck_path / "backs").mkdir(exist_ok=True)

        # Save deck.json
        deck_file = self.deck_path / "deck.json"
        with open(deck_file, "w", encoding="utf-8") as f:
            json.dump(self.deck_data, f, indent=2, ensure_ascii=False)

        # Save empty feedback.json
        feedback = {
            "parasha": self.research_data.name_en,
            "deck_version": "2.0",
            "review_date": None,
            "cards": [],
            "global_feedback": ""
        }
        feedback_file = self.deck_path / "feedback.json"
        with open(feedback_file, "w", encoding="utf-8") as f:
            json.dump(feedback, f, indent=2, ensure_ascii=False)

        print(f"\nDeck created: {deck_file}")
        print(f"Cards: {self.deck_data['card_count']}")

        return self.deck_data

    def save_research(self) -> None:
        """Save research data for reference."""
        if not self.deck_path or not self.research_data:
            return

        research_file = self.deck_path / "parasha_research.json"
        with open(research_file, "w", encoding="utf-8") as f:
            json.dump(self.research_data.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"Research saved: {research_file}")

    @classmethod
    def full_create(cls, parasha_name: str, output_dir: str = None) -> "DeckWorkflow":
        """
        Convenience method to run the complete deck creation workflow.

        Args:
            parasha_name: Name of the Torah portion
            output_dir: Output directory for deck files

        Returns:
            Completed DeckWorkflow instance
        """
        workflow = cls(parasha_name)
        workflow.research()
        workflow.create(output_dir)
        workflow.save_research()

        print(f"\n{'='*50}")
        print(f"DECK CREATION COMPLETE: {parasha_name}")
        print(f"Path: {workflow.deck_path}")
        print('='*50)

        return workflow
