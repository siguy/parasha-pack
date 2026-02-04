"""
Character workflow for Parasha Pack.

Complete workflow for creating a new character with research, design, and reference generation.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .models import CharacterResearch, CharacterDesign
from .research import research_character


# =============================================================================
# DEFAULT DESIGNS
# =============================================================================

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
    "esther": {
        "visual_description": "Young Jewish woman with warm olive skin and kind determined eyes",
        "clothing": ["Royal purple and blue flowing dress", "Elegant modest head covering", "Simple gold tiara"],
        "features": ["Large kind brown eyes", "Long dark hair", "Gentle determined expression", "Warm approachable features"],
        "props": ["Royal scepter (occasionally)"],
        "poses": [
            "Hand on heart, showing courage",
            "Standing tall before the king",
            "Kneeling in prayer",
            "Arms open, embracing her people",
        ],
    },
    "mordechai": {
        "visual_description": "Older Jewish man with wise grandfatherly presence",
        "clothing": ["Jewish head covering (kippah or cloth wrap)", "Modest robes in earth tones - browns, creams, subtle blues"],
        "features": ["Full gray-brown beard", "Kind wise eyes", "Dignified posture", "Grandfatherly warmth"],
        "props": [],
        "poses": [
            "Hands clasped peacefully",
            "Standing tall, not bowing",
            "Giving advice to Esther",
            "Celebrating with raised hands",
        ],
    },
    "haman": {
        "visual_description": "Adult man with frustrated pouty expression - NOT scary",
        "clothing": ["DISTINCTIVE THREE-CORNERED HAT (like hamantaschen shape)", "Persian-style clothing in MUTED dusty purple and gray-brown"],
        "features": ["Dark pointed goatee with connected mustache", "Furrowed brow", "Jealous expression (not angry)", "Arms often crossed", "Shoulders hunched"],
        "props": ["Three-cornered hat"],
        "poses": [
            "Arms crossed, looking jealous",
            "Turned away, frustrated",
            "Pouty face, upset",
            "Looking embarrassed",
        ],
    },
    "achashverosh": {
        "visual_description": "King with confused bewildered expression - somewhat comedic",
        "clothing": ["Large ornate crown", "Royal Persian robes in golds and reds"],
        "features": ["Bewildered look", "Eyebrows often raised", "Distracted expression", "Somewhat cartoonish"],
        "props": ["Royal scepter", "Crown"],
        "poses": [
            "Scratching head, confused",
            "Sitting on throne, distracted",
            "Surprised expression",
            "Making a proclamation",
        ],
    },
}


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

        # Generate ONLY identity reference (single source of truth)
        output_path = ref_dir / f"{self.key}_identity.png"
        print(f"\n[IDENTITY] Generating single reference sheet...")

        prompt = self._get_identity_prompt(base_desc)
        if generate_image(prompt, api_key, str(output_path), "16:9"):
            print(f"  -> Saved: {output_path.name}")
            self.reference_paths["identity"] = str(output_path)
        else:
            print(f"  -> FAILED")

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
            # Store relative path from project root
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
