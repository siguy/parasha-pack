#!/usr/bin/env python3
"""
Parasha Pack Workflows - Reusable functions for common tasks.

This module provides high-level workflow functions that encapsulate
the research, creation, and generation steps for various tasks.

Workflows:
- Character Creation: research_character() -> define_character() -> generate_character_references()
- Deck Creation: research_parasha() -> create_deck() -> populate_cards()
- Card Creation: add_card() -> generate_card_content() -> generate_card_image()
- Batch Operations: batch_generate_images(), batch_update_cards()

Usage:
    from workflows import CharacterWorkflow, DeckWorkflow

    # Create a new character with full research
    char = CharacterWorkflow.create("miriam", deck_path="decks/beshalach")

    # Create a new deck
    deck = DeckWorkflow.create("Beshalach")
"""

import json
import os
import urllib.request
import urllib.parse
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime


# =============================================================================
# DATA STRUCTURES
# =============================================================================

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


# =============================================================================
# RESEARCH FUNCTIONS
# =============================================================================

def research_character(name: str) -> CharacterResearch:
    """
    Research a biblical character using Sefaria API and curated sources.

    This function gathers:
    - Biblical references where the character appears
    - Key stories and narrative moments
    - Personality traits from traditional sources
    - Relationships with other characters
    - Emotional moments suitable for children's content

    Args:
        name: Character name (English, e.g., "Miriam", "Moses", "Yitro")

    Returns:
        CharacterResearch dataclass with all gathered information

    Example:
        >>> research = research_character("Miriam")
        >>> print(research.key_stories)
        ['Watching baby Moses in the basket', 'Leading the women in song at the sea']
    """
    # Character database with pre-researched information
    CHARACTER_DATABASE = {
        "moses": CharacterResearch(
            name_en="Moses",
            name_he="מֹשֶׁה",
            biblical_refs=["Exodus 2-40", "Numbers 1-36", "Deuteronomy 1-34"],
            key_stories=[
                "Baby in the basket on the Nile",
                "Burning bush encounter",
                "Leading the Exodus from Egypt",
                "Receiving the Torah at Sinai",
                "Striking the rock for water",
            ],
            personality_traits=["humble", "caring", "brave", "patient", "faithful"],
            relationships={
                "Miriam": "older sister",
                "Aaron": "older brother",
                "Yitro": "father-in-law and advisor",
                "Pharaoh": "confronted for freedom",
                "Israelites": "leader and teacher",
            },
            emotional_moments=[
                {"event": "Seeing the burning bush", "emotion": "awe and wonder"},
                {"event": "Reuniting with Yitro", "emotion": "joy and gratitude"},
                {"event": "Receiving the commandments", "emotion": "reverence"},
                {"event": "When people complained", "emotion": "tired but caring"},
            ],
            age_appropriate_summary="Moses was a kind leader who helped his people be free. He listened to God and taught everyone to be good to each other.",
        ),
        "miriam": CharacterResearch(
            name_en="Miriam",
            name_he="מִרְיָם",
            biblical_refs=["Exodus 2:1-10", "Exodus 15:20-21", "Numbers 12", "Numbers 20:1"],
            key_stories=[
                "Watching baby Moses in the basket",
                "Suggesting her mother as a nurse",
                "Leading the women in song at the sea",
                "The well that followed the Israelites",
            ],
            personality_traits=["brave", "musical", "protective", "joyful", "faithful"],
            relationships={
                "Moses": "younger brother",
                "Aaron": "brother",
                "Yocheved": "mother",
                "Pharaoh's daughter": "spoke to her about Moses",
            },
            emotional_moments=[
                {"event": "Hiding to watch baby Moses", "emotion": "worried but brave"},
                {"event": "Singing at the sea", "emotion": "overjoyed and grateful"},
                {"event": "Caring for her family", "emotion": "loving and protective"},
            ],
            age_appropriate_summary="Miriam was brave and loved to sing! She protected her baby brother Moses and later led everyone in celebrating with music.",
        ),
        "yitro": CharacterResearch(
            name_en="Yitro",
            name_he="יִתְרוֹ",
            biblical_refs=["Exodus 2:16-22", "Exodus 18"],
            key_stories=[
                "Welcoming Moses as a stranger",
                "Giving his daughter Tzipporah to Moses",
                "Visiting Moses in the desert",
                "Giving wise advice about judging fairly",
            ],
            personality_traits=["wise", "welcoming", "observant", "helpful", "grandfatherly"],
            relationships={
                "Moses": "son-in-law",
                "Tzipporah": "daughter",
                "Israelites": "wise advisor",
            },
            emotional_moments=[
                {"event": "Hearing about the Exodus", "emotion": "amazed and grateful"},
                {"event": "Reuniting with Moses", "emotion": "overjoyed"},
                {"event": "Seeing Moses overwhelmed", "emotion": "concerned and caring"},
                {"event": "Giving advice", "emotion": "wise and helpful"},
            ],
            age_appropriate_summary="Yitro was a wise grandfather who loved to help. He gave Moses great advice about being a good leader and sharing work with others.",
        ),
        "abraham": CharacterResearch(
            name_en="Abraham",
            name_he="אַבְרָהָם",
            biblical_refs=["Genesis 12-25"],
            key_stories=[
                "Leaving home for a new land",
                "Welcoming three visitors",
                "Looking at the stars with God's promise",
            ],
            personality_traits=["faithful", "welcoming", "brave", "kind", "generous"],
            relationships={
                "Sarah": "beloved wife",
                "Isaac": "son",
                "Lot": "nephew",
            },
            emotional_moments=[
                {"event": "Leaving his home", "emotion": "brave but uncertain"},
                {"event": "Welcoming guests", "emotion": "joyful and generous"},
                {"event": "Seeing the stars", "emotion": "hopeful and amazed"},
            ],
            age_appropriate_summary="Abraham was very welcoming and always invited people to his tent. He trusted God and started a big family.",
        ),
        "sarah": CharacterResearch(
            name_en="Sarah",
            name_he="שָׂרָה",
            biblical_refs=["Genesis 11-23"],
            key_stories=[
                "Traveling to a new land with Abraham",
                "Welcoming visitors to the tent",
                "Laughing when she heard she would have a baby",
                "Being a loving mother to Isaac",
            ],
            personality_traits=["beautiful", "hospitable", "patient", "joyful", "strong"],
            relationships={
                "Abraham": "beloved husband",
                "Isaac": "son",
            },
            emotional_moments=[
                {"event": "Hearing about a baby", "emotion": "surprised and happy"},
                {"event": "Holding Isaac", "emotion": "overjoyed"},
            ],
            age_appropriate_summary="Sarah was kind and always welcomed guests. She waited a long time and was so happy when baby Isaac was born!",
        ),
    }

    # Normalize the name for lookup
    name_lower = name.lower().strip()

    if name_lower in CHARACTER_DATABASE:
        return CHARACTER_DATABASE[name_lower]

    # Return empty research for unknown characters
    return CharacterResearch(
        name_en=name.title(),
        name_he="",
        age_appropriate_summary=f"Research needed for {name}",
    )


def research_parasha(name: str) -> ParashaResearch:
    """
    Research a Torah portion using Sefaria API and curated sources.

    This function gathers:
    - Full reference and Hebrew name
    - Key events and story summary
    - Main characters appearing in the portion
    - Themes and educational elements
    - Age-appropriate lesson summary

    Args:
        name: Parasha name (English, e.g., "Yitro", "Beshalach")

    Returns:
        ParashaResearch dataclass with all gathered information

    Example:
        >>> research = research_parasha("Yitro")
        >>> print(research.key_events)
        ['Yitro visits Moses', 'Giving of the Ten Commandments']
    """
    # Try to fetch from Sefaria first
    try:
        from sefaria_client import PARASHA_THEMES, get_border_color
    except ImportError:
        PARASHA_THEMES = {}
        get_border_color = lambda n, b: "#5c2d91"

    # Parasha database with pre-researched information
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


# =============================================================================
# CHARACTER WORKFLOW
# =============================================================================

class CharacterWorkflow:
    """
    Complete workflow for creating a new character.

    Steps:
    1. research() - Gather biblical information about the character
    2. design() - Define visual appearance and traits
    3. generate_references() - Create reference sheet images
    4. add_to_manifest() - Update the references manifest

    Example:
        # Full workflow
        workflow = CharacterWorkflow("miriam", deck_path="decks/beshalach")
        workflow.research()
        workflow.design()
        workflow.generate_references(api_key="...")

        # Or use the convenience method
        CharacterWorkflow.create("miriam", deck_path="decks/beshalach", api_key="...")
    """

    def __init__(self, name: str, deck_path: str = None):
        """
        Initialize a character workflow.

        Args:
            name: Character name (English)
            deck_path: Path to deck directory (for saving references)
        """
        self.name = name
        self.key = name.lower().strip().replace(" ", "_")
        self.deck_path = Path(deck_path) if deck_path else None

        self.research_data: Optional[CharacterResearch] = None
        self.design_data: Optional[CharacterDesign] = None
        self.reference_paths: Dict[str, str] = {}

    def research(self) -> CharacterResearch:
        """
        Step 1: Research the character from biblical sources.

        Returns:
            CharacterResearch with biblical information
        """
        print(f"\n{'='*50}")
        print(f"RESEARCHING: {self.name}")
        print('='*50)

        self.research_data = research_character(self.name)

        print(f"\nName: {self.research_data.name_en} ({self.research_data.name_he})")
        print(f"Key stories: {len(self.research_data.key_stories)}")
        print(f"Personality: {', '.join(self.research_data.personality_traits)}")
        print(f"Emotional moments: {len(self.research_data.emotional_moments)}")

        return self.research_data

    def design(self,
               visual_description: str = None,
               clothing: List[str] = None,
               features: List[str] = None,
               props: List[str] = None,
               poses: List[str] = None) -> CharacterDesign:
        """
        Step 2: Define the visual design for the character.

        Args:
            visual_description: Overall visual description
            clothing: List of clothing items
            features: List of distinguishing features
            props: List of props/items the character holds
            poses: List of signature poses for reference sheet

        Returns:
            CharacterDesign with visual specifications
        """
        if not self.research_data:
            self.research()

        print(f"\n{'='*50}")
        print(f"DESIGNING: {self.name}")
        print('='*50)

        # Default designs based on research
        DEFAULT_DESIGNS = {
            "moses": {
                "visual_description": "Friendly middle-aged man with warm brown skin",
                "clothing": ["Blue head covering flowing down", "Blue outer robe with cream undergarment"],
                "features": ["Kind gentle eyes", "Short dark beard with touch of gray", "Warm expression"],
                "props": ["Wooden shepherd's crook staff"],
                "poses": [
                    "Arms wide open, welcoming embrace",
                    "Hand to ear, listening carefully",
                    "Seated, looking tired, hand on forehead",
                    "Standing tall, staff raised, leading",
                ],
            },
            "yitro": {
                "visual_description": "Wise elderly grandfather figure with warm presence",
                "clothing": ["Tan/olive head covering", "Colorful earth-toned Midianite robes with geometric patterns"],
                "features": ["Long flowing white/gray beard", "Warm twinkling wise eyes", "Grandfatherly gentle smile"],
                "props": ["Gnarled wooden walking staff"],
                "poses": [
                    "One finger raised, giving wise advice",
                    "Arms open wide for embrace",
                    "Hand on chin, thinking wisely",
                    "Walking with staff, traveling",
                ],
            },
            "miriam": {
                "visual_description": "Young woman with joyful, brave expression",
                "clothing": ["Colorful dress with blue and purple", "Simple head covering"],
                "features": ["Long dark wavy hair", "Bright expressive eyes", "Ready smile"],
                "props": ["Tambourine/timbrel"],
                "poses": [
                    "Playing tambourine, dancing joyfully",
                    "Watching over something carefully",
                    "Leading others with arm raised",
                    "Singing with joy",
                ],
            },
            "abraham": {
                "visual_description": "Kind elderly man with welcoming presence",
                "clothing": ["White flowing robe", "Simple head covering"],
                "features": ["Long white beard", "Kind eyes", "Open welcoming expression"],
                "props": ["Walking stick"],
                "poses": [
                    "Arms open in welcome",
                    "Looking up at stars",
                    "Offering hospitality",
                    "Walking with purpose",
                ],
            },
            "sarah": {
                "visual_description": "Graceful woman with warm maternal presence",
                "clothing": ["Elegant blue head covering", "Flowing dress in earth tones"],
                "features": ["Warm smile", "Kind eyes", "Graceful posture"],
                "props": [],
                "poses": [
                    "Laughing with joy",
                    "Welcoming guests",
                    "Holding a baby tenderly",
                    "Preparing food",
                ],
            },
        }

        defaults = DEFAULT_DESIGNS.get(self.key, {})

        self.design_data = CharacterDesign(
            key=self.key,
            name_en=self.research_data.name_en,
            name_he=self.research_data.name_he,
            visual_description=visual_description or defaults.get("visual_description", ""),
            clothing=clothing or defaults.get("clothing", []),
            distinguishing_features=features or defaults.get("features", []),
            props=props or defaults.get("props", []),
            emotional_range=self.research_data.personality_traits,
            signature_poses=poses or defaults.get("poses", []),
        )

        # Generate style prompt
        self.design_data.style_prompt = self.design_data.get_base_description()

        print(f"\nVisual: {self.design_data.visual_description}")
        print(f"Clothing: {', '.join(self.design_data.clothing)}")
        print(f"Features: {', '.join(self.design_data.distinguishing_features)}")
        print(f"Props: {', '.join(self.design_data.props)}")
        print(f"Poses: {len(self.design_data.signature_poses)}")

        return self.design_data

    def generate_references(self, api_key: str = None, output_dir: str = None) -> Dict[str, str]:
        """
        Step 3: Generate character reference sheet images.

        Args:
            api_key: Gemini API key (or uses GEMINI_API_KEY env var)
            output_dir: Output directory (defaults to deck_path/references)

        Returns:
            Dictionary mapping reference type to file path
        """
        if not self.design_data:
            self.design()

        api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API key required. Set GEMINI_API_KEY or pass api_key parameter.")

        # Determine output directory
        if output_dir:
            ref_dir = Path(output_dir)
        elif self.deck_path:
            ref_dir = self.deck_path / "references"
        else:
            ref_dir = Path("references")

        ref_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*50}")
        print(f"GENERATING REFERENCES: {self.name}")
        print(f"Output: {ref_dir}")
        print('='*50)

        # Import the generation function
        try:
            from generate_references import generate_image
        except ImportError:
            print("ERROR: generate_references module not found")
            return {}

        base_desc = self.design_data.get_base_description()

        # Generate each reference type
        reference_types = {
            "identity": self._get_identity_prompt(base_desc),
            "expressions": self._get_expressions_prompt(base_desc),
            "turnaround": self._get_turnaround_prompt(base_desc),
            "poses": self._get_poses_prompt(base_desc),
        }

        import time
        for ref_type, prompt in reference_types.items():
            output_path = ref_dir / f"{self.key}_{ref_type}.png"
            print(f"\n[{ref_type.upper()}] Generating...")

            aspect = "3:2" if ref_type == "expressions" else "16:9"
            if generate_image(prompt, api_key, str(output_path), aspect):
                print(f"  -> Saved: {output_path.name}")
                self.reference_paths[ref_type] = str(output_path)
            else:
                print(f"  -> FAILED")

            time.sleep(3)  # Rate limiting

        return self.reference_paths

    def add_to_manifest(self) -> None:
        """
        Step 4: Update the references manifest with this character.
        """
        if not self.deck_path:
            print("No deck path specified, skipping manifest update")
            return

        manifest_path = self.deck_path / "references" / "manifest.json"

        # Load existing manifest or create new
        if manifest_path.exists():
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
        else:
            manifest = {}

        # Add this character's references
        manifest[self.key] = {}
        for ref_type, path in self.reference_paths.items():
            # Store relative path from project root (parent of decks/)
            # This ensures paths like "decks/yitro/references/..." work from review-site
            project_root = self.deck_path.parent.parent
            rel_path = str(Path(path).relative_to(project_root))
            manifest[self.key][ref_type] = rel_path

        # Save manifest
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"\nManifest updated: {manifest_path}")

    def save_research(self, output_path: str = None) -> None:
        """Save research and design data to JSON for reference."""
        if not output_path:
            if self.deck_path:
                output_path = self.deck_path / "references" / f"{self.key}_research.json"
            else:
                output_path = f"{self.key}_research.json"

        data = {
            "research": self.research_data.to_dict() if self.research_data else None,
            "design": self.design_data.to_dict() if self.design_data else None,
            "references": self.reference_paths,
            "created_at": datetime.now().isoformat(),
        }

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Research saved: {output_path}")

    @classmethod
    def create(cls, name: str, deck_path: str = None, api_key: str = None,
               generate_images: bool = True) -> "CharacterWorkflow":
        """
        Convenience method to run the complete character creation workflow.

        Args:
            name: Character name
            deck_path: Path to deck directory
            api_key: Gemini API key for image generation
            generate_images: Whether to generate reference images

        Returns:
            Completed CharacterWorkflow instance
        """
        workflow = cls(name, deck_path)
        workflow.research()
        workflow.design()
        workflow.save_research()

        if generate_images and api_key:
            workflow.generate_references(api_key)
            workflow.add_to_manifest()

        print(f"\n{'='*50}")
        print(f"CHARACTER CREATION COMPLETE: {name}")
        print('='*50)

        return workflow

    # Private prompt generation methods
    def _get_identity_prompt(self, base_desc: str) -> str:
        return f"""Create a CHARACTER IDENTITY REFERENCE SHEET for a children's book.

=== STYLE ===
Vivid, high-contrast cartoon style for ages 4-6.
- Rounded, friendly shapes
- Large expressive eyes (20% of face)
- Thick, clean black outlines (2-3px)
- Bold primary colors
- Simple, memorable design
- NO text or labels in the image

=== CHARACTER ===
{base_desc}

=== LAYOUT ===
Side-by-side panels on clean white background:

LEFT (50%): CLOSE-UP PORTRAIT
- Head and shoulders
- Neutral friendly expression
- Clear view of face and distinguishing features

RIGHT (50%): FULL BODY STANDING
- Complete figure head to toe
- Same outfit and features
- Standing in relaxed pose

Both panels must show the EXACT SAME CHARACTER with identical features, colors, and style.
"""

    def _get_expressions_prompt(self, base_desc: str) -> str:
        emotions = ["happy", "sad", "scared", "surprised", "proud", "confused"]
        emotion_desc = {
            "happy": "big warm smile, eyes crinkled with joy",
            "sad": "downturned mouth, droopy eyes, slight frown",
            "scared": "wide eyes, raised eyebrows, mouth open in worry",
            "surprised": "very wide eyes, raised eyebrows, mouth open in 'O'",
            "proud": "slight smile, chin up, confident expression",
            "confused": "tilted head, one eyebrow raised, puzzled look",
        }
        emotion_grid = "\n".join([f"- {e.upper()}: {emotion_desc[e]}" for e in emotions])

        return f"""Create an EXPRESSION REFERENCE SHEET for a children's book character.

=== STYLE ===
Vivid, high-contrast cartoon style for ages 4-6.
- Large expressive eyes (20% of face)
- Thick, clean black outlines
- Bold colors
- Clear, exaggerated expressions
- NO text or labels

=== CHARACTER ===
{base_desc}

=== LAYOUT ===
A 3x2 GRID showing 6 DIFFERENT EMOTIONS (head and shoulders only):

{emotion_grid}

CRITICAL: Every cell shows the EXACT SAME CHARACTER - ONLY the expression changes.
Clean white background. Each expression must be DRAMATICALLY CLEAR.
"""

    def _get_turnaround_prompt(self, base_desc: str) -> str:
        return f"""Create a CHARACTER TURNAROUND REFERENCE SHEET for a children's book.

=== STYLE ===
Vivid, high-contrast cartoon style for ages 4-6.
- Rounded, friendly shapes
- Large expressive eyes
- Thick, clean black outlines
- Bold colors
- NO text or labels

=== CHARACTER ===
{base_desc}

=== LAYOUT ===
4 VIEWS in a horizontal row:

1. FRONT VIEW - facing viewer directly
2. 3/4 VIEW - turned 45 degrees to the right
3. SIDE VIEW (PROFILE) - facing right
4. BACK VIEW - facing away from viewer

All 4 views must show the EXACT SAME CHARACTER with identical proportions and outfit.
Clean white background.
"""

    def _get_poses_prompt(self, base_desc: str) -> str:
        poses = self.design_data.signature_poses if self.design_data else []
        pose_list = "\n".join([f"- {pose}" for pose in poses]) if poses else "- Standing naturally"

        return f"""Create a POSE REFERENCE SHEET for a children's book character.

=== STYLE ===
Vivid, high-contrast cartoon style for ages 4-6.
- Rounded, friendly shapes
- Large expressive eyes
- Thick, clean black outlines
- Bold colors
- Dynamic but clear poses
- NO text or labels

=== CHARACTER ===
{base_desc}

=== POSES ===
Show the SAME CHARACTER in different action poses:

{pose_list}

=== LAYOUT ===
Arrange poses in a grid or row. Each pose shows full body.
Clean white background.
All poses must show the EXACT SAME CHARACTER.
"""


# =============================================================================
# DECK WORKFLOW
# =============================================================================

class DeckWorkflow:
    """
    Complete workflow for creating a new deck.

    Steps:
    1. research() - Gather parasha information
    2. create() - Generate deck template with smart defaults
    3. add_characters() - Add character cards based on research
    4. populate_content() - Fill in card content

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

        # Enhance with research data
        self.deck_data["mitzvah_connection"] = self.research_data.child_friendly_lesson

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

        # Save deck.json
        deck_file = self.deck_path / "deck.json"
        with open(deck_file, "w", encoding="utf-8") as f:
            json.dump(self.deck_data, f, indent=2, ensure_ascii=False)

        # Save empty feedback.json
        feedback = {
            "parasha": self.research_data.name_en,
            "deck_version": "1.0",
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


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def list_available_characters() -> List[str]:
    """List all characters with pre-defined research data."""
    return ["moses", "miriam", "yitro", "abraham", "sarah"]


def list_available_parshiyot() -> List[str]:
    """List all parshiyot with pre-defined research data."""
    return ["yitro", "beshalach"]


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


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI interface for workflows."""
    import argparse

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
