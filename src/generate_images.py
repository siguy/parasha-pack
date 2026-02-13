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
import sys
import time
import urllib.request
import urllib.error
import base64
from pathlib import Path

# PIL overlay system is deprecated - text overlay now handled by Card Designer React components
# See card-designer/ for the React-based text overlay system


def is_v2_card(card: dict) -> bool:
    """Check if a card uses v2 format (has front/back structure)."""
    return "front" in card and "back" in card


def build_generation_prompt(scene_prompt: str, card_type: str) -> str:
    """
    Build a complete generation prompt by layering system concerns onto a scene description.

    Deck prompts (image_prompt in deck.json) should be PURE SCENE DESCRIPTIONS —
    what to draw, not how to draw it. This function adds all system layers:

    1. Style anchors     — visual consistency (children's illustration style)
    2. Safety rules      — content restrictions (no God in human form, etc.)
    3. Scene description  — from deck.json (passed through unchanged)
    4. Composition        — per-card-type cinematography (where to place subjects)
    5. Critical rules     — universal (no text, no borders)

    All system concerns are defined in image_prompts.py and applied here.
    To change style, safety, or composition: update image_prompts.py once.

    Args:
        scene_prompt: Scene-only image prompt from deck.json
        card_type: Card type (anchor, spotlight, story, etc.)

    Returns:
        Complete prompt with all system layers applied
    """
    try:
        from image_prompts import (
            STYLE_ANCHORS_V2, SAFETY_PROMPT,
            COMPOSITION_GUIDANCE, COMPOSITION_SUFFIX,
        )
    except ImportError:
        # Fallback if image_prompts not available
        return scene_prompt

    parts = []

    # 1. Style anchors
    parts.append(f"=== STYLE ===\n{STYLE_ANCHORS_V2.strip()}")

    # 2. Safety rules
    parts.append(f"=== SAFETY RULES ===\n{SAFETY_PROMPT}")

    # 3. Scene description (from deck.json — passed through unchanged)
    parts.append(f"=== SCENE ===\n{scene_prompt.strip()}")

    # 4. Per-card-type composition guidance
    guidance = COMPOSITION_GUIDANCE.get(card_type, "")
    if guidance:
        parts.append(guidance.strip())

    # 5. Universal critical rules (no text, no borders)
    parts.append(COMPOSITION_SUFFIX.strip())

    return "\n\n".join(parts)


def load_reference_images(deck_path: Path) -> list:
    """
    Load ALL character reference images from the deck's manifest.

    Always passes all character identities to ensure consistency across cards.
    Each image is labeled with text so the model knows which character it represents.

    Args:
        deck_path: Path to deck.json

    Returns:
        List of image parts for API payload (alternating text labels and images)
    """
    refs_dir = deck_path.parent / "references"
    manifest_path = refs_dir / "manifest.json"

    if not manifest_path.exists():
        return []

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"  -> Warning: failed to load manifest: {e}")
        return []

    image_parts = []
    loaded_chars = []

    # Character name mappings for clearer labels
    character_labels = {
        "esther": "Esther (Queen Esther)",
        "mordechai": "Mordechai",
        "haman": "Haman (the villain)",
        "achashverosh": "King Achashverosh (the king)",
        "moses": "Moses",
        "miriam": "Miriam",
        "yitro": "Yitro",
    }

    for character, data in manifest.items():
        identity_file = data.get("identity", "")
        if identity_file:
            identity_path = refs_dir / identity_file
            if identity_path.exists():
                try:
                    with open(identity_path, 'rb') as f:
                        image_data = base64.b64encode(f.read()).decode('utf-8')

                    # Add text label BEFORE the image so model knows who it is
                    label = character_labels.get(character, character.title())
                    image_parts.append({
                        "text": f"Character reference for {label}:"
                    })
                    image_parts.append({
                        "inlineData": {
                            "mimeType": "image/png",
                            "data": image_data
                        }
                    })
                    loaded_chars.append(character)
                except Exception as e:
                    print(f"  -> Failed to load {character} reference: {e}")

    # Add instruction after all references
    if image_parts:
        image_parts.append({
            "text": "Use the above character references for visual consistency. Now generate:"
        })

    if loaded_chars:
        print(f"  -> References: {', '.join(loaded_chars)}")

    return image_parts


def generate_image_nano_banana(prompt: str, api_key: str, output_path: str, aspect_ratio: str = "3:4", reference_images: list = None) -> bool:
    """
    Generate an image using Nano Banana Pro model (best for children's book style).

    Args:
        prompt: The image generation prompt
        api_key: Gemini API key
        output_path: Path to save the generated image
        aspect_ratio: Aspect ratio (default 3:4 for cards)
        reference_images: Optional list of reference image parts for character consistency

    Returns:
        True if successful, False otherwise
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
                            return True

        print(f"  No image in response")
        return False

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"  HTTP Error {e.code}: {error_body[:200]}")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def generate_image_imagen(prompt: str, api_key: str, output_path: str) -> bool:
    """
    Generate an image using Google Imagen 4.0 model (not recommended).
    Note: Prefer nano-banana for better children's book style results.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={api_key}"

    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "3:4",
            "personGeneration": "allow_adult",
            "safetySetting": "block_low_and_above"
        }
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method='POST')

        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode())

        if "predictions" in result and len(result["predictions"]) > 0:
            image_data = result["predictions"][0].get("bytesBase64Encoded")
            if image_data:
                with open(output_path, 'wb') as f:
                    f.write(base64.b64decode(image_data))
                return True

        print(f"  No image in response: {result}")
        return False

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"  HTTP Error {e.code}: {error_body[:200]}")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def generate_image_gemini_flash(prompt: str, api_key: str, output_path: str) -> bool:
    """
    Generate an image using Gemini Flash model with image generation.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent?key={api_key}"

    payload = {
        "contents": [{
            "parts": [{"text": f"Generate an image: {prompt}"}]
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"]
        }
    }

    headers = {"Content-Type": "application/json"}

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')

        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode())

        # Extract image from response
        if "candidates" in result:
            for candidate in result["candidates"]:
                content = candidate.get("content", {})
                for part in content.get("parts", []):
                    if "inlineData" in part:
                        image_data = part["inlineData"].get("data")
                        if image_data:
                            image_bytes = base64.b64decode(image_data)
                            with open(output_path, 'wb') as f:
                                f.write(image_bytes)
                            return True

        print(f"  No image in response")
        return False

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"  HTTP Error {e.code}: {error_body[:200]}")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate images for Parasha Pack cards")
    parser.add_argument("deck_path", help="Path to deck.json file")
    parser.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY env var)")
    parser.add_argument("--card", help="Generate image for specific card ID only")
    parser.add_argument("--skip-existing", action="store_true", help="Skip cards that already have images")
    parser.add_argument("--model", choices=["nano-banana", "imagen", "flash"], default="nano-banana", help="Model to use (nano-banana recommended)")
    parser.add_argument("--no-refs", action="store_true", help="Disable character reference images")

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

    # Get deck name
    deck_name = deck.get('parasha_en') or deck.get('holiday_en') or 'Unknown'

    print(f"Generating images for: {deck_name}")
    print(f"Output directory: {raw_dir}")
    print(f"Model: {args.model}")
    print("-" * 50)
    print("Note: Images are saved WITHOUT text overlay.")
    print("Use Card Designer (card-designer/) to render final cards with text.")
    print("-" * 50)

    # Select generation function (nano-banana is default and recommended)
    if args.model == "nano-banana":
        generate_fn = generate_image_nano_banana
    elif args.model == "imagen":
        generate_fn = generate_image_imagen
    else:
        generate_fn = generate_image_gemini_flash

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

        raw_prompt = card.get("image_prompt", "")
        if not raw_prompt:
            print(f"[SKIP] {card_id} - no prompt")
            skip_count += 1
            continue

        # Build full prompt: scene description + style + safety + composition + rules
        card_type = card.get("card_type", "")
        prompt = build_generation_prompt(raw_prompt, card_type)

        # Get title for display
        if is_v2_card(card):
            title = card.get("back", {}).get("title_en", card_id)[:30]
        else:
            title = card.get("title_en", card_id)[:30]

        print(f"[GEN] {card_id}: {title}...")

        # Load reference images for character consistency (nano-banana only)
        reference_images = []
        if args.model == "nano-banana" and not args.no_refs:
            reference_images = load_reference_images(deck_path)

        # Generate image
        if args.model == "nano-banana":
            success = generate_fn(prompt, api_key, str(output_path), reference_images=reference_images)
        else:
            success = generate_fn(prompt, api_key, str(output_path))

        if success:
            print(f"  -> Saved: {output_path.name}")
            success_count += 1

            # Update deck with image path (raw/ for scene-only images)
            card["image_path"] = f"raw/{card_id}.png"
        else:
            fail_count += 1

        # Rate limiting - wait between requests
        time.sleep(2)

    # Save updated deck with image paths
    with open(deck_path, 'w', encoding='utf-8') as f:
        json.dump(deck, f, indent=2, ensure_ascii=False)

    print("-" * 50)
    print(f"Complete! Success: {success_count}, Skipped: {skip_count}, Failed: {fail_count}")

    if success_count > 0:
        print(f"\nRaw images saved to: {raw_dir}")
        print(f"Deck updated with image paths: {deck_path}")
        print(f"\nNext steps:")
        print(f"  1. cd card-designer && npm run dev")
        print(f"  2. npm run export {deck_path.parent.name}")


if __name__ == "__main__":
    main()
