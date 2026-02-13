"""
Parasha Pack - Educational Card Deck Generator

This package provides tools for creating educational Torah portion
card decks for preschool/kindergarten classrooms (ages 4-6).
"""

from .schema import (
    CardType,
    CardV2,
    Deck,
    FEELING_FACES,
    CHARACTER_DESIGNS,
    PRINT_SPECS,
)

from .sefaria_client import (
    Parasha,
    fetch_current_parasha,
    fetch_parasha_text,
    get_border_color,
)

from .image_prompts import (
    build_anchor_prompt_v2,
    build_spotlight_prompt_v2,
    build_story_prompt_v2,
    build_connection_prompt_v2,
    build_power_word_prompt_v2,
    build_tradition_prompt_v2,
    build_divine_presence_prompt_v2,
    get_character_style,
)

__version__ = "2.0.0"
__all__ = [
    # Schema
    "CardType",
    "CardV2",
    "Deck",
    "FEELING_FACES",
    "CHARACTER_DESIGNS",
    "PRINT_SPECS",
    # Sefaria
    "Parasha",
    "fetch_current_parasha",
    "fetch_parasha_text",
    "get_border_color",
    # Image Prompts (scene-only builders)
    "build_anchor_prompt_v2",
    "build_spotlight_prompt_v2",
    "build_story_prompt_v2",
    "build_connection_prompt_v2",
    "build_power_word_prompt_v2",
    "build_tradition_prompt_v2",
    "build_divine_presence_prompt_v2",
    "get_character_style",
]
