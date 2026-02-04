"""
Parasha Pack Workflows Package

High-level workflow functions for character and deck creation.

Usage:
    from workflows import CharacterWorkflow, DeckWorkflow

    # Create a new character with full research
    char = CharacterWorkflow.create("miriam", deck_path="decks/beshalach")

    # Create a new deck
    deck = DeckWorkflow.full_create("Beshalach")

    # Research functions
    from workflows import research_character, research_parasha
    research = research_character("moses")
"""

# Models (data structures)
from .models import (
    CharacterResearch,
    CharacterDesign,
    ParashaResearch,
)

# Research functions
from .research import (
    research_character,
    research_parasha,
    list_available_characters,
    list_available_parshiyot,
    get_character_summary,
    get_parasha_summary,
    CHARACTER_DATABASE,
    PARASHA_DATABASE,
)

# Workflow classes
from .character import CharacterWorkflow
from .deck import DeckWorkflow

# CLI
from .cli import main

__all__ = [
    # Models
    "CharacterResearch",
    "CharacterDesign",
    "ParashaResearch",
    # Research
    "research_character",
    "research_parasha",
    "list_available_characters",
    "list_available_parshiyot",
    "get_character_summary",
    "get_parasha_summary",
    "CHARACTER_DATABASE",
    "PARASHA_DATABASE",
    # Workflows
    "CharacterWorkflow",
    "DeckWorkflow",
    # CLI
    "main",
]
