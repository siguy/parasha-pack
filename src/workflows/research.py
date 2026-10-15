"""
Research functions and databases for Parasha Pack.

Character research is read from the shared characters/ library.
Parasha research is still a small built-in dict (PARASHA_DATABASE).
"""

from typing import List

import character_library

from .models import CharacterResearch, ParashaResearch


# =============================================================================
# CHARACTERS
# =============================================================================
# Character research lives in the shared library: characters/{key}/character.yaml
# (the old CHARACTER_DATABASE dict was retired so there is one source of truth).


# =============================================================================
# PARASHA DATABASE
# =============================================================================

PARASHA_DATABASE = {
    "yitro": ParashaResearch(
        name_en="Yitro",
        name_he="יִתְרוֹ",
        ref="Exodus 18:1-20:23",
        book="Exodus",
        summary="Yitro brings Moses's family back and gives wise advice. The Israelites receive the Ten Commandments at Mount Sinai.",
        key_events=[
            "Yitro hears about the Exodus and visits",
            "Yitro brings Tzipporah and the children",
            "Yitro sees Moses judging all day and gives advice",
            "Moses appoints helpers to share the work",
            "The Israelites camp at Mount Sinai",
            "God gives the Ten Commandments",
        ],
        main_characters=["Moses", "Yitro", "Aaron", "Tzipporah"],
        themes=["listening", "wisdom", "teamwork", "rules", "respect"],
        emotions=["joy", "amazement", "reverence", "gratitude"],
        mitzvot=["Honor your father and mother", "Keep Shabbat"],
        child_friendly_lesson="When someone gives us good advice, we should listen! Sharing work helps everyone.",
        suggested_theme="covenant",
        border_color="#5c2d91",
    ),
    "beshalach": ParashaResearch(
        name_en="Beshalach",
        name_he="בְּשַׁלַּח",
        ref="Exodus 13:17-17:16",
        book="Exodus",
        summary="The Israelites leave Egypt, cross the sea, and begin their journey in the desert with miracles along the way.",
        key_events=[
            "Leaving Egypt with joy",
            "Pharaoh chases the Israelites",
            "Crossing the sea on dry land",
            "Miriam leads singing and dancing",
            "Finding water at Marah",
            "Manna falls from heaven",
        ],
        main_characters=["Moses", "Miriam", "Aaron", "Pharaoh"],
        themes=["freedom", "trust", "miracles", "gratitude", "music"],
        emotions=["scared", "brave", "joyful", "grateful", "amazed"],
        mitzvot=["Remember Shabbat", "Trust in God"],
        child_friendly_lesson="Even when things seem scary, we can be brave! And when good things happen, we celebrate together.",
        suggested_theme="water",
        border_color="#2d8a8a",
    ),
}


# =============================================================================
# RESEARCH FUNCTIONS
# =============================================================================

def research_character(name: str) -> CharacterResearch:
    """
    Look up a biblical character in the shared characters/ library.

    Args:
        name: Character name or alias (e.g., "Miriam", "Moses", "Abraham")

    Returns:
        CharacterResearch dataclass (mostly empty if the character isn't in the library yet)
    """
    character = character_library.load_character(name)
    if not character:
        # Unknown characters get an empty record to fill in
        return CharacterResearch(
            name_en=name.title(),
            name_he="",
            age_appropriate_summary=f"Research needed for {name}",
        )

    research = character.get("research") or {}
    return CharacterResearch(
        name_en=character["name_en"],
        name_he=character["name_he"],
        biblical_refs=research.get("biblical_refs", []),
        key_stories=research.get("key_stories", []),
        personality_traits=character.get("personality", []),
        relationships=research.get("relationships", {}),
        emotional_moments=research.get("emotional_moments", []),
        age_appropriate_summary=research.get("age_appropriate_summary", ""),
    )


def research_parasha(name: str) -> ParashaResearch:
    """
    Research a Torah portion using pre-defined database.

    Args:
        name: Parasha name (English, e.g., "Yitro", "Beshalach")

    Returns:
        ParashaResearch dataclass with all gathered information
    """
    # Try to get theme colors from sefaria_client if available
    try:
        from sefaria_client import PARASHA_THEMES, get_border_color
    except ImportError:
        PARASHA_THEMES = {}
        get_border_color = lambda n, b: "#5c2d91"

    name_lower = name.lower().strip()

    if name_lower in PARASHA_DATABASE:
        return PARASHA_DATABASE[name_lower]

    # Get theme from sefaria_client if available
    theme = PARASHA_THEMES.get(name.title(), "covenant")
    border_color = get_border_color(name.title(), "")

    return ParashaResearch(
        name_en=name.title(),
        name_he="",
        ref="",
        book="",
        summary=f"Research needed for {name}",
        suggested_theme=theme,
        border_color=border_color,
    )


def list_available_characters() -> List[str]:
    """List all characters in the shared characters/ library."""
    return character_library.list_characters()


def list_available_parshiyot() -> List[str]:
    """List all parshiyot with pre-defined research data."""
    return list(PARASHA_DATABASE.keys())


def get_character_summary(name: str) -> str:
    """Get a quick summary of a character's research."""
    research = research_character(name)
    return f"""
{research.name_en} ({research.name_he})
{'='*40}
Traits: {', '.join(research.personality_traits)}
Stories: {', '.join(research.key_stories[:3])}...
Summary: {research.age_appropriate_summary}
"""


def get_parasha_summary(name: str) -> str:
    """Get a quick summary of a parasha's research."""
    research = research_parasha(name)
    return f"""
{research.name_en} ({research.name_he})
{'='*40}
Reference: {research.ref}
Theme: {research.suggested_theme}
Characters: {', '.join(research.main_characters)}
Lesson: {research.child_friendly_lesson}
"""
