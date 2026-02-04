"""
Data structures for Parasha Pack workflows.

Contains dataclasses for research and design data.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List


@dataclass
class CharacterResearch:
    """Research data for a biblical character."""
    name_en: str
    name_he: str
    biblical_refs: List[str] = field(default_factory=list)
    key_stories: List[str] = field(default_factory=list)
    personality_traits: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)
    emotional_moments: List[Dict[str, str]] = field(default_factory=list)
    age_appropriate_summary: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CharacterDesign:
    """Visual and descriptive design for a character."""
    key: str  # lowercase identifier (e.g., "miriam")
    name_en: str
    name_he: str

    # Visual traits
    visual_description: str = ""
    clothing: List[str] = field(default_factory=list)
    distinguishing_features: List[str] = field(default_factory=list)
    props: List[str] = field(default_factory=list)

    # Personality for expressions
    default_emotion: str = "kind"
    emotional_range: List[str] = field(default_factory=list)

    # Key poses for this character
    signature_poses: List[str] = field(default_factory=list)

    # Full prompt snippet for image generation
    style_prompt: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def get_base_description(self) -> str:
        """Generate the base description for reference sheets."""
        lines = [f"Children's book cartoon character {self.name_en.upper()}:"]

        if self.visual_description:
            lines.append(f"- {self.visual_description}")

        for trait in self.distinguishing_features:
            lines.append(f"- {trait}")

        for item in self.clothing:
            lines.append(f"- {item}")

        for prop in self.props:
            lines.append(f"- {prop}")

        # Add standard style elements
        lines.extend([
            "- Rounded, friendly cartoon style",
            "- Thick clean black outlines",
            "- Bold colors, simple shapes",
            "- LARGE expressive eyes (20% of face)",
        ])

        return "\n".join(lines)


@dataclass
class ParashaResearch:
    """Research data for a Torah portion."""
    name_en: str
    name_he: str
    ref: str
    book: str

    # Story elements
    summary: str = ""
    key_events: List[str] = field(default_factory=list)
    main_characters: List[str] = field(default_factory=list)
    key_verses: List[Dict[str, str]] = field(default_factory=list)

    # Educational elements
    themes: List[str] = field(default_factory=list)
    emotions: List[str] = field(default_factory=list)
    mitzvot: List[str] = field(default_factory=list)
    child_friendly_lesson: str = ""

    # Theming
    suggested_theme: str = "covenant"
    border_color: str = "#5c2d91"

    def to_dict(self) -> dict:
        return asdict(self)
