"""
Character workflow for Parasha Pack.

Complete workflow for creating a new character with research, design, and reference generation.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import character_library

from .models import CharacterResearch, CharacterDesign
from .research import research_character


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
        self.key = character_library.resolve_key(name)  # "Abraham" -> "avraham"
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

        # Defaults come from the locked design in characters/{key}/character.yaml
        library = character_library.load_character(self.key) or {}

        self.design_data = CharacterDesign(
            key=self.key,
            name_en=self.research_data.name_en,
            name_he=self.research_data.name_he,
            visual_description=visual_description or "",
            clothing=clothing or [],
            distinguishing_features=features or library.get("visual_anchors", []),
            props=props or library.get("props", []),
            emotional_range=self.research_data.personality_traits,
            signature_poses=poses or library.get("signature_poses", []),
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
        Step 3: Generate 2 candidate identity sheets in characters/{key}/.

        Args:
            api_key: Gemini API key (or uses GEMINI_API_KEY env var)
            output_dir: Ignored (kept for old callers); sheets always go to characters/{key}/

        Returns:
            Dictionary mapping reference type to file path
        """
        if not self.design_data:
            self.design()

        api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API key required. Set GEMINI_API_KEY or pass api_key parameter.")

        print(f"\n{'='*50}")
        print(f"GENERATING IDENTITY SHEETS: {self.name}  ->  characters/{self.key}/")
        print('='*50)

        # Identity sheets now live in the shared library: characters/{key}/identity_vN.png
        try:
            import character_library
            from generate_references import generate_identity_versions
        except ImportError:
            print("ERROR: generate_references module not found")
            return {}

        if not character_library.load_character(self.key):
            print(f"ERROR: characters/{self.key}/character.yaml is missing. Create it (locked anchors) "
                  f"first; identity sheets are built from it.")
            return {}

        # 2 candidate versions; Simon picks one with
        #   python generate_references.py --character {key} --accept vN
        for number, path in enumerate(generate_identity_versions(self.key, api_key, versions=2), start=1):
            self.reference_paths[f"identity_candidate_{number}"] = str(path)

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
