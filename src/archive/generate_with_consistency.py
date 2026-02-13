#!/usr/bin/env python3
"""
Generate images with character consistency using Nano Banana Pro.

Workflow:
1. Generate character reference sheets (portrait + full body)
2. Use reference sheets when generating cards with those characters

Usage:
    export GEMINI_API_KEY="your-api-key"
    python generate_with_consistency.py ../decks/yitro/deck.json
"""

import argparse
import json
import os
import sys
import time
import base64
import urllib.request
import urllib.error
from pathlib import Path


# Character reference sheet prompts
CHARACTER_REFERENCE_PROMPTS = {
    "moses": """Create a CHARACTER REFERENCE SHEET for a children's book character named MOSES.

=== STYLE ===
Vivid, high-contrast cartoon style for ages 4-6.
- Rounded, friendly shapes
- Large expressive eyes (20% of face)
- Thick, clean black outlines
- Bold primary colors
- Simple, memorable design

=== CHARACTER DESIGN: MOSES ===
Friendly middle-aged man with:
- Warm brown skin
- Kind, gentle eyes (LARGE and expressive)
- Short dark beard with touch of gray
- Simple blue and cream robes
- Wooden shepherd's staff
- Calm, caring expression

=== REFERENCE SHEET LAYOUT ===
Create a SIDE-BY-SIDE image with:

LEFT PANEL (50%): CLOSE-UP PORTRAIT
- Face and shoulders only
- Neutral, friendly expression
- Clear view of facial features
- Eyes looking slightly toward viewer
- Label: "MOSES - Portrait"

RIGHT PANEL (50%): FULL BODY
- Standing pose, facing slightly left
- Holding wooden staff
- Same outfit: blue and cream robes
- Full figure from head to toe
- Label: "MOSES - Full Body"

BOTH PANELS must show the EXACT SAME CHARACTER with identical:
- Face shape and features
- Skin tone
- Beard style and color
- Clothing colors and style

=== FORMAT ===
- Aspect ratio: 16:9 (wide reference sheet)
- Clean white or light gray background
- Clear separation between panels
- Labels under each panel

This reference will be used to maintain character consistency across multiple illustrations.""",

    "yitro": """Create a CHARACTER REFERENCE SHEET for a children's book character named YITRO (Jethro).

=== STYLE ===
Vivid, high-contrast cartoon style for ages 4-6.
- Rounded, friendly shapes
- Large expressive eyes (20% of face)
- Thick, clean black outlines
- Bold colors
- Simple, memorable design

=== CHARACTER DESIGN: YITRO ===
Wise elderly man with:
- Long flowing WHITE/GRAY beard (distinguished)
- Warm, twinkling eyes that show wisdom
- Grandfatherly gentle smile
- COLORFUL earth-toned robes (browns, tans, with red and gold accents - Midianite style)
- Walking stick/staff
- Head held with dignity

=== REFERENCE SHEET LAYOUT ===
Create a SIDE-BY-SIDE image with:

LEFT PANEL (50%): CLOSE-UP PORTRAIT
- Face and shoulders only
- Wise, kind expression
- Clear view of facial features and long beard
- Eyes with warmth and wisdom
- Label: "YITRO - Portrait"

RIGHT PANEL (50%): FULL BODY
- Standing pose, slightly turned
- Holding walking stick
- Colorful Midianite-style robes visible
- Full figure from head to toe
- Label: "YITRO - Full Body"

BOTH PANELS must show the EXACT SAME CHARACTER with identical:
- Face shape and features
- Long white/gray beard
- Clothing colors and patterns
- Walking stick style

=== FORMAT ===
- Aspect ratio: 16:9 (wide reference sheet)
- Clean white or light gray background
- Clear separation between panels
- Labels under each panel

This reference will be used to maintain character consistency across multiple illustrations.""",
}


def encode_image_to_base64(image_path: str) -> str:
    """Read an image file and encode it as base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def generate_image_nano_banana(
    prompt: str,
    api_key: str,
    output_path: str,
    reference_images: list[str] = None,
    aspect_ratio: str = "3:4",
) -> bool:
    """
    Generate an image using Nano Banana Pro with optional reference images.

    Args:
        prompt: Text prompt for generation
        api_key: Gemini API key
        output_path: Path to save the generated image
        reference_images: List of paths to reference images for consistency
        aspect_ratio: Output aspect ratio (e.g., "3:4" for cards, "16:9" for reference sheets)

    Returns:
        True if successful, False otherwise
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/nano-banana-pro-preview:generateContent?key={api_key}"

    # Build the contents array
    contents_parts = []

    # Add reference images first (if any)
    if reference_images:
        for ref_path in reference_images:
            if os.path.exists(ref_path):
                image_data = encode_image_to_base64(ref_path)
                # Determine mime type
                mime_type = "image/png" if ref_path.lower().endswith(".png") else "image/jpeg"
                contents_parts.append({
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": image_data
                    }
                })
                print(f"    Added reference: {os.path.basename(ref_path)}")

    # Add the text prompt
    contents_parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": contents_parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "imageConfig": {
                "aspectRatio": aspect_ratio
            }
        }
    }

    headers = {"Content-Type": "application/json"}

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=180) as response:
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
                            with open(output_path, "wb") as f:
                                f.write(image_bytes)
                            return True

        print(f"    No image in response")
        return False

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"    HTTP Error {e.code}: {error_body[:300]}")
        return False
    except Exception as e:
        print(f"    Error: {e}")
        return False


def generate_character_references(api_key: str, output_dir: str) -> dict:
    """
    Generate character reference sheets for Moses and Yitro.

    Returns:
        Dict mapping character name to reference sheet path
    """
    references = {}
    ref_dir = Path(output_dir) / "references"
    ref_dir.mkdir(exist_ok=True)

    for char_name, prompt in CHARACTER_REFERENCE_PROMPTS.items():
        output_path = ref_dir / f"{char_name}_reference.png"

        if output_path.exists():
            print(f"[EXISTS] {char_name} reference sheet already exists")
            references[char_name] = str(output_path)
            continue

        print(f"[GEN] Generating {char_name} reference sheet...")

        if generate_image_nano_banana(
            prompt=prompt,
            api_key=api_key,
            output_path=str(output_path),
            reference_images=None,
            aspect_ratio="16:9",  # Wide format for reference sheets
        ):
            print(f"    -> Saved: {output_path}")
            references[char_name] = str(output_path)
        else:
            print(f"    -> FAILED to generate reference for {char_name}")

        time.sleep(3)  # Rate limiting

    return references


def get_characters_in_card(card: dict) -> list[str]:
    """Determine which characters appear in a card based on its content."""
    characters = []

    card_type = card.get("card_type", "")
    title = card.get("title_en", "").lower()
    description = card.get("english_description", "").lower()
    char_name = card.get("character_name_en", "").lower()

    # Spotlight cards
    if card_type == "spotlight":
        if "moses" in char_name or "moshe" in char_name:
            characters.append("moses")
        elif "yitro" in char_name or "jethro" in char_name:
            characters.append("yitro")

    # Action cards - check content
    elif card_type == "action":
        if "moses" in title or "moses" in description:
            characters.append("moses")
        if "yitro" in title or "yitro" in description or "jethro" in title:
            characters.append("yitro")
        # Reunion and advice scenes have both
        if "reunion" in title or "advice" in title:
            if "moses" not in characters:
                characters.append("moses")
            if "yitro" not in characters:
                characters.append("yitro")

    # Thinker cards about specific characters
    elif card_type == "thinker":
        if "help" in title or "yitro" in description:
            characters.append("moses")
            characters.append("yitro")

    return characters


def build_card_prompt_with_references(card: dict, deck: dict, character_refs: list[str]) -> str:
    """
    Build a card prompt that instructs the model to use reference images.
    """
    base_prompt = card.get("image_prompt", "")

    if not character_refs:
        return base_prompt

    # Add reference instruction at the beginning
    ref_instruction = """IMPORTANT: Use the provided reference image(s) to maintain EXACT character consistency.
The characters in this card MUST look IDENTICAL to their reference sheets:
- Same face shape and features
- Same clothing colors and style
- Same beard style (if applicable)
- Same overall proportions

"""

    return ref_instruction + base_prompt


def generate_deck_with_consistency(
    deck_path: str,
    api_key: str,
    skip_existing: bool = False,
) -> list:
    """
    Generate all card images with character consistency.

    Args:
        deck_path: Path to deck.json
        api_key: Gemini API key
        skip_existing: Skip cards that already have images

    Returns:
        List of generated file paths
    """
    # Load deck
    deck_path = Path(deck_path)
    with open(deck_path, "r", encoding="utf-8") as f:
        deck = json.load(f)

    images_dir = deck_path.parent / "images"
    images_dir.mkdir(exist_ok=True)

    print(f"=== Generating deck: {deck['parasha_en']} ===\n")

    # Step 1: Generate character reference sheets
    print("STEP 1: Generating character reference sheets...")
    print("-" * 50)
    char_references = generate_character_references(api_key, str(deck_path.parent))
    print(f"\nGenerated references for: {list(char_references.keys())}\n")

    # Step 2: Generate card images using references
    print("STEP 2: Generating card images with consistency...")
    print("-" * 50)

    generated_files = []
    success_count = 0
    skip_count = 0
    fail_count = 0

    for card in deck["cards"]:
        card_id = card["card_id"]
        output_path = images_dir / f"{card_id}.png"

        # Skip if exists
        if skip_existing and output_path.exists():
            print(f"[SKIP] {card_id} - image exists")
            skip_count += 1
            continue

        # Get characters in this card
        characters = get_characters_in_card(card)

        # Get reference images for those characters
        ref_images = [char_references[c] for c in characters if c in char_references]

        print(f"[GEN] {card_id}: {card['title_en'][:30]}...")
        if ref_images:
            print(f"    Using references: {[os.path.basename(r) for r in ref_images]}")

        # Build prompt with reference instruction
        prompt = build_card_prompt_with_references(card, deck, ref_images)

        # Generate image
        if generate_image_nano_banana(
            prompt=prompt,
            api_key=api_key,
            output_path=str(output_path),
            reference_images=ref_images if ref_images else None,
            aspect_ratio="3:4",  # Card aspect ratio
        ):
            print(f"    -> Saved: {output_path.name}")
            card["image_path"] = f"images/{card_id}.png"
            generated_files.append(str(output_path))
            success_count += 1
        else:
            fail_count += 1

        time.sleep(3)  # Rate limiting

    # Save updated deck
    with open(deck_path, "w", encoding="utf-8") as f:
        json.dump(deck, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 50)
    print(f"Complete! Success: {success_count}, Skipped: {skip_count}, Failed: {fail_count}")

    if char_references:
        print(f"\nCharacter references saved to: {deck_path.parent}/references/")
    print(f"Card images saved to: {images_dir}")

    return generated_files


def main():
    parser = argparse.ArgumentParser(
        description="Generate card images with character consistency"
    )
    parser.add_argument("deck_path", help="Path to deck.json file")
    parser.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY)")
    parser.add_argument("--skip-existing", action="store_true", help="Skip existing images")
    parser.add_argument("--references-only", action="store_true", help="Only generate reference sheets")

    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Gemini API key required.")
        print("Set GEMINI_API_KEY or use --api-key")
        sys.exit(1)

    if args.references_only:
        deck_path = Path(args.deck_path)
        refs = generate_character_references(api_key, str(deck_path.parent))
        print(f"\nGenerated {len(refs)} reference sheets")
    else:
        generate_deck_with_consistency(
            args.deck_path,
            api_key,
            args.skip_existing,
        )


if __name__ == "__main__":
    main()
