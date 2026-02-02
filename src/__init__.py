"""
Parasha Pack - Educational Card Deck Generator

This package provides tools for creating educational Torah portion
card decks for preschool/kindergarten classrooms (ages 4-6).
"""

from .schema import (
    CardType,
    BaseCard,
    AnchorCard,
    SpotlightCard,
    ActionCard,
    ThinkerCard,
    PowerWordCard,
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
    build_anchor_prompt,
    build_spotlight_prompt,
    build_action_prompt,
    build_thinker_prompt,
    build_power_word_prompt,
    build_divine_presence_prompt,
    get_character_style,
)

__version__ = "1.0.0"
__all__ = [
    # Schema
    "CardType",
    "BaseCard",
    "AnchorCard",
    "SpotlightCard",
    "ActionCard",
    "ThinkerCard",
    "PowerWordCard",
    "Deck",
    "FEELING_FACES",
    "CHARACTER_DESIGNS",
    "PRINT_SPECS",
    # Sefaria
    "Parasha",
    "fetch_current_parasha",
    "fetch_parasha_text",
    "get_border_color",
    # Image Prompts
    "build_anchor_prompt",
    "build_spotlight_prompt",
    "build_action_prompt",
    "build_thinker_prompt",
    "build_power_word_prompt",
    "build_divine_presence_prompt",
    "get_character_style",
]
