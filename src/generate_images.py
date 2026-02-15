#!/usr/bin/env python3
"""
Generate images for Parasha Pack cards using Google Gemini.

Usage:
    export GEMINI_API_KEY="your-api-key"
    python generate_images.py ../decks/yitro/deck.json

Output:
    Images are saved to decks/{deck}/raw/ as scene-only images (no text).
    Use the Card Designer React app to render final cards with text overlays.
    Run `npm run export <deckId>` in card-designer/ to export final images.

Get your API key at: https://aistudio.google.com/app/apikey
"""

import argparse
import json
import os
import shutil
import sys
import time
import urllib.request
import urllib.error
import base64
from datetime import datetime, timezone
from pathlib import Path

# PIL overlay system is deprecated - text overlay now handled by Card Designer React components
# See card-designer/ for the React-based text overlay system


def is_v2_card(card: dict) -> bool:
    """Check if a card uses v2 format (has front/back structure)."""
    return "front" in card and "back" in card


def build_generation_prompt(scene_prompt: str, card_type: str, story_world: str = "",
                            character_refs_loaded: list = None,
                            manifest: dict = None) -> str:
    """
    Build a complete generation prompt by layering system concerns onto a scene description.

    Deck prompts (image_prompt in deck.json) should be PURE SCENE DESCRIPTIONS —
    what to draw, not how to draw it. This function adds all system layers:

    1. Style anchors     — visual consistency (children's illustration style)
    2. World style       — MODERN_WORLD_STYLE for connection/tradition,
                           story_world (from deck.json) for all other card types
    3. Safety rules      — content restrictions (no God in human form, etc.)
    4. Scene description  — from deck.json (passed through unchanged)
    4b. Ref hint         — when character refs are loaded, tell model to prioritize them
    5. Composition        — per-card-type cinematography (where to place subjects)
    6. Critical rules     — universal (no text, no borders)

    Two visual "worlds" exist:
      - Modern World (connection + tradition): modern Orthodox Jewish community,
        same across all decks. Defined in MODERN_WORLD_STYLE constant.
      - Story World (anchor, spotlight, story, power_word): historical/holiday
        setting specific to this deck. Defined in deck.json "story_world" field.

    Args:
        scene_prompt: Scene-only image prompt from deck.json
        card_type: Card type (anchor, spotlight, story, etc.)
        story_world: Per-deck historical setting (from deck.json "story_world")
        character_refs_loaded: List of character keys with ref images loaded.
            When provided, adds a hint to prioritize reference images over
            inline text descriptions for character appearance.

    Returns:
        Complete prompt with all system layers applied
    """
    try:
        from image_prompts import (
            STYLE_ANCHORS_V2, SAFETY_PROMPT,
            COMPOSITION_GUIDANCE, COMPOSITION_SUFFIX,
            MODERN_WORLD_STYLE,
        )
    except ImportError:
        # Fallback if image_prompts not available
        return scene_prompt

    # Card types that use the modern world vs story world
    modern_world_cards = {"connection", "tradition"}

    parts = []

    # 1. Style anchors (all cards)
    parts.append(f"=== STYLE ===\n{STYLE_ANCHORS_V2.strip()}")

    # 2. World style (modern or story, based on card type)
    if card_type in modern_world_cards:
        parts.append(MODERN_WORLD_STYLE.strip())
    elif story_world:
        parts.append(f"=== WORLD: STORY SETTING ===\n{story_world.strip()}\n\nAll scenes should feel like they belong in this world. Consistent architecture, clothing, lighting, and color palette throughout.")

    # 3. Safety rules
    parts.append(f"=== SAFETY RULES ===\n{SAFETY_PROMPT}")

    # 4. Scene description (from deck.json — passed through unchanged)
    parts.append(f"=== SCENE ===\n{scene_prompt.strip()}")

    # 4b. When character ref images are loaded, tell model to prioritize them
    if character_refs_loaded:
        _manifest = manifest or {}
        ref_names = ", ".join(
            get_character_label(key, _manifest) for key in character_refs_loaded
        )
        parts.append(
            f"=== CHARACTER REFERENCES ===\n"
            f"Reference images provided for: {ref_names}.\n"
            f"For these characters, prioritize the reference images for appearance "
            f"(face, clothing, coloring). Use the text description above for pose, "
            f"action, and emotion only."
        )

    # 5. Per-card-type composition guidance
    guidance = COMPOSITION_GUIDANCE.get(card_type, "")
    if guidance:
        parts.append(guidance.strip())

    # 6. Universal critical rules (no text, no borders)
    parts.append(COMPOSITION_SUFFIX.strip())

    return "\n\n".join(parts)


def log_generation(deck_path: Path, card_id: str, model: str, full_prompt: str,
                   character_refs: list, success: bool) -> None:
    """
    Append a generation record to the deck's JSONL log.

    Each line is a self-contained JSON object with 6 fields.
    The log is append-only — never overwritten, never rotated at current scale.

    Args:
        deck_path: Path to deck.json
        card_id: Card being generated
        model: Model name (e.g. "nano-banana-pro")
        full_prompt: Complete assembled prompt (all layers)
        character_refs: List of character keys whose refs were passed
        success: Whether the generation succeeded
    """
    log_path = deck_path.parent / "raw" / "generations.jsonl"
    record = {
        "card_id": card_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "full_prompt": full_prompt,
        "character_refs": character_refs,
        "success": success,
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def save_prompt_sidecar(deck_path: Path, card_id: str, full_prompt: str) -> None:
    """
    Save the full assembled prompt as a human-readable sidecar file.

    Overwritten each run — the JSONL log is the durable record.
    Useful for quick debugging without parsing JSONL.
    """
    prompts_dir = deck_path.parent / "raw" / "prompts"
    prompts_dir.mkdir(exist_ok=True)
    prompt_path = prompts_dir / f"{card_id}.txt"
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(full_prompt)


def get_character_label(character_key: str, manifest: dict) -> str:
    """Derive human-readable label from manifest entry or key name.

    Reads optional 'label' field from manifest. Falls back to title-cased key.
    Only call for character entries — non-character keys (style_hero) are skipped
    by the caller before reaching this function.
    """
    entry = manifest.get(character_key, {})
    if isinstance(entry, dict):
        return entry.get("label", character_key.replace("_", " ").title())
    return character_key.replace("_", " ").title()


def _load_image_as_part(image_path: Path) -> dict:
    """Load an image file and return it as an API-compatible inline data part."""
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    return {
        "inlineData": {
            "mimeType": "image/png",
            "data": image_data
        }
    }


# Card types that belong to the story world (receive style hero)
STORY_WORLD_CARDS = {"anchor", "spotlight", "story", "power_word"}


def load_reference_images(deck_path: Path, characters_in_scene: list = None,
                          card_type: str = "", no_hero: bool = False) -> tuple:
    """
    Load reference images from the deck's manifest: style hero + character refs.

    Style hero is loaded first (for story-world cards only) as a visual anchor,
    then character refs filtered by characters_in_scene.

    Args:
        deck_path: Path to deck.json
        characters_in_scene: List of character keys to load, None for all, [] for none
        card_type: Card type (determines whether style hero is loaded)
        no_hero: If True, skip style hero even for story-world cards

    Returns:
        Tuple of (image_parts, loaded_char_keys):
          - image_parts: List of image parts for API payload (style hero first, then chars)
          - loaded_char_keys: List of character keys that were loaded
    """
    refs_dir = deck_path.parent / "references"
    manifest_path = refs_dir / "manifest.json"

    if not manifest_path.exists():
        return [], []

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"  -> Warning: failed to load manifest: {e}")
        return [], []

    image_parts = []
    loaded_chars = []

    # 1. Style hero — loaded first as visual anchor for story-world cards
    if not no_hero and card_type in STORY_WORLD_CARDS:
        hero_data = manifest.get("style_hero")
        if hero_data:
            hero_file = hero_data.get("identity", "")
            hero_path = refs_dir / hero_file
            if hero_path.exists():
                try:
                    image_parts.append({
                        "text": "Style reference — match this art style, color palette, and rendering quality:"
                    })
                    image_parts.append(_load_image_as_part(hero_path))
                    print(f"  -> Style hero: {hero_file}")
                except Exception as e:
                    print(f"  -> Warning: failed to load style hero: {e}")

    # 2. Character refs — filtered by characters_in_scene
    # Empty list means explicitly no characters
    if characters_in_scene is not None and len(characters_in_scene) == 0:
        if not image_parts:
            print("  -> References: none (no characters in scene)")
        else:
            print("  -> Characters: none (no characters in scene)")
        return image_parts, loaded_chars

    for character, data in manifest.items():
        # Skip non-character entries (style_hero, etc.)
        if character.startswith("style_hero"):
            continue
        # Filter by characters_in_scene if provided
        if characters_in_scene is not None and character not in characters_in_scene:
            continue
        identity_file = data.get("identity", "")
        if identity_file:
            identity_path = refs_dir / identity_file
            if identity_path.exists():
                try:
                    label = get_character_label(character, manifest)
                    image_parts.append({
                        "text": f"Character reference for {label}:"
                    })
                    image_parts.append(_load_image_as_part(identity_path))
                    loaded_chars.append(character)
                except Exception as e:
                    print(f"  -> Failed to load {character} reference: {e}")

    # Add instruction after all references
    if image_parts:
        image_parts.append({
            "text": "Use the above references for visual consistency. Now generate:"
        })

    if loaded_chars:
        print(f"  -> Characters: {', '.join(loaded_chars)}")

    return image_parts, loaded_chars


def generate_image_nano_banana(prompt: str, api_key: str, output_path: str, aspect_ratio: str = "3:4", reference_images: list = None) -> dict:
    """
    Generate an image using Nano Banana Pro model (best for children's book style).

    Args:
        prompt: The image generation prompt
        api_key: Gemini API key
        output_path: Path to save the generated image
        aspect_ratio: Aspect ratio (default 3:4 for cards)
        reference_images: Optional list of reference image parts for character consistency

    Returns:
        Dict with 'success' (bool) and 'prompt' (str) keys
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/nano-banana-pro-preview:generateContent?key={api_key}"

    # Build parts list: reference images first, then prompt
    parts = []
    if reference_images:
        parts.extend(reference_images)
    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "imageConfig": {"aspectRatio": aspect_ratio}
        }
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method='POST')

        with urllib.request.urlopen(req, timeout=180) as response:
            result = json.loads(response.read().decode())

        if "candidates" in result:
            for candidate in result["candidates"]:
                for part in candidate.get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        image_data = part["inlineData"].get("data")
                        if image_data:
                            with open(output_path, 'wb') as f:
                                f.write(base64.b64decode(image_data))
                            return {"success": True, "prompt": prompt}

        print(f"  No image in response")
        return {"success": False, "prompt": prompt}

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"  HTTP Error {e.code}: {error_body[:200]}")
        return {"success": False, "prompt": prompt}
    except Exception as e:
        print(f"  Error: {e}")
        return {"success": False, "prompt": prompt}


def main():
    parser = argparse.ArgumentParser(description="Generate images for Parasha Pack cards")
    parser.add_argument("deck_path", help="Path to deck.json file")
    parser.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY env var)")
    parser.add_argument("--card", help="Generate image for specific card ID only")
    parser.add_argument("--skip-existing", action="store_true", help="Skip cards that already have images")
    parser.add_argument("--no-refs", action="store_true", help="Disable character reference images")
    parser.add_argument("--no-hero", action="store_true", help="Skip style hero reference image")
    parser.add_argument("--variants", type=int, default=1, help="Generate N variants per card (e.g. --variants 3)")
    parser.add_argument("--backup", action="store_true", help="Backup existing images before overwriting")

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Gemini API key required.")
        print("Set GEMINI_API_KEY environment variable or use --api-key flag")
        print("\nGet your API key at: https://aistudio.google.com/app/apikey")
        sys.exit(1)

    # Load deck
    deck_path = Path(args.deck_path)
    if not deck_path.exists():
        print(f"Error: Deck file not found: {deck_path}")
        sys.exit(1)

    with open(deck_path, 'r', encoding='utf-8') as f:
        deck = json.load(f)

    # Setup output directory - raw/ for scene-only images
    raw_dir = deck_path.parent / "raw"
    raw_dir.mkdir(exist_ok=True)

    # Setup backup directory if --backup flag set
    backup_dir = None
    if args.backup:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = raw_dir / f"backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        print(f"Backup directory: {backup_dir}")

    # Get deck name and story world
    deck_name = deck.get('parasha_en') or deck.get('holiday_en') or 'Unknown'
    story_world = deck.get('story_world', '')

    # Load manifest once for character labels
    manifest_path = deck_path.parent / "references" / "manifest.json"
    manifest = {}
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except Exception:
            pass

    print(f"Generating images for: {deck_name}")
    print(f"Output directory: {raw_dir}")
    print(f"Model: nano-banana-pro")
    print("-" * 50)
    print("Note: Images are saved WITHOUT text overlay.")
    print("Use Card Designer (card-designer/) to render final cards with text.")
    print("-" * 50)

    # Track results
    success_count = 0
    skip_count = 0
    fail_count = 0

    # Generate images for each card
    for card in deck["cards"]:
        card_id = card["card_id"]

        # Filter by specific card if requested
        if args.card and card_id != args.card:
            continue

        output_path = raw_dir / f"{card_id}.png"

        # Skip if image exists and flag set
        if args.skip_existing and output_path.exists():
            print(f"[SKIP] {card_id} - image exists")
            skip_count += 1
            continue

        # Backup existing image before overwriting
        if backup_dir and output_path.exists():
            shutil.copy2(output_path, backup_dir / output_path.name)

        raw_prompt = card.get("image_prompt", "")
        if not raw_prompt:
            print(f"[SKIP] {card_id} - no prompt")
            skip_count += 1
            continue

        card_type = card.get("card_type", "")

        # Get title for display
        if is_v2_card(card):
            title = card.get("back", {}).get("title_en", card_id)[:30]
        else:
            title = card.get("title_en", card_id)[:30]

        print(f"[GEN] {card_id}: {title}...")

        # Load reference images for character consistency
        # characters_in_scene controls which refs are loaded:
        #   None  = load all refs (backwards compatible, field absent)
        #   []    = load no refs (tradition/connection cards)
        #   ["esther", "mordechai"] = load only those refs
        reference_images = []
        loaded_char_keys = []
        if not args.no_refs:
            characters_in_scene = card.get("characters_in_scene")  # None if absent
            reference_images, loaded_char_keys = load_reference_images(
                deck_path, characters_in_scene=characters_in_scene,
                card_type=card_type, no_hero=args.no_hero,
            )

        # Build full prompt: scene + world + style + safety + composition + rules + ref hints
        prompt = build_generation_prompt(
            raw_prompt, card_type, story_world=story_world,
            character_refs_loaded=loaded_char_keys,
            manifest=manifest,
        )

        # Save prompt sidecar for quick debugging
        save_prompt_sidecar(deck_path, card_id, prompt)

        # Generate image(s) — loop for --variants N
        num_variants = args.variants
        for variant_num in range(1, num_variants + 1):
            if num_variants > 1:
                variant_path = raw_dir / f"{card_id}_v{variant_num}.png"
                print(f"  variant {variant_num}/{num_variants}...")
            else:
                variant_path = output_path

            result = generate_image_nano_banana(prompt, api_key, str(variant_path), reference_images=reference_images)
            success = result["success"]

            # Log every generation attempt
            model_name = "nano-banana-pro"
            log_generation(deck_path, card_id, model_name, prompt, loaded_char_keys, success)

            if success:
                print(f"  -> Saved: {variant_path.name}")
                success_count += 1
            else:
                fail_count += 1

            # Rate limiting - wait between requests
            time.sleep(2)

        # Update deck with canonical image path (raw/ for scene-only images)
        card["image_path"] = f"raw/{card_id}.png"

    # Save updated deck with image paths
    with open(deck_path, 'w', encoding='utf-8') as f:
        json.dump(deck, f, indent=2, ensure_ascii=False)

    print("-" * 50)
    label = "images" if args.variants == 1 else f"images ({args.variants} variants per card)"
    print(f"Complete! Success: {success_count} {label}, Skipped: {skip_count}, Failed: {fail_count}")

    if backup_dir:
        backed_up = list(backup_dir.glob("*.png"))
        if backed_up:
            print(f"\nBacked up {len(backed_up)} images to: {backup_dir}")
        else:
            # No images were backed up — remove empty directory
            backup_dir.rmdir()

    if success_count > 0:
        print(f"\nRaw images saved to: {raw_dir}")
        print(f"Deck updated with image paths: {deck_path}")
        print(f"\nNext steps:")
        print(f"  1. cd card-designer && npm run dev")
        print(f"  2. npm run export {deck_path.parent.name}")


if __name__ == "__main__":
    main()
