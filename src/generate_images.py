#!/usr/bin/env python3
"""
Generate images for Parasha Pack cards using Google Gemini.

Usage:
    export GEMINI_API_KEY="your-api-key"
    python generate_images.py ../decks/yitro/deck.json

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


def generate_image_gemini(prompt: str, api_key: str, output_path: str) -> bool:
    """
    Generate an image using Google Gemini's Imagen model.

    Args:
        prompt: The image generation prompt
        api_key: Gemini API key
        output_path: Path to save the generated image

    Returns:
        True if successful, False otherwise
    """
    # Gemini Imagen 4.0 API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={api_key}"

    # Request payload
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "3:4",  # Close to 5:7 ratio for cards
            "personGeneration": "allow_adult",
            "safetySetting": "block_some"
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')

        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode())

        # Extract and save image
        if "predictions" in result and len(result["predictions"]) > 0:
            image_data = result["predictions"][0].get("bytesBase64Encoded")
            if image_data:
                image_bytes = base64.b64decode(image_data)
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)
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
    parser.add_argument("--model", choices=["imagen", "flash"], default="imagen", help="Model to use")

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

    # Setup output directory
    images_dir = deck_path.parent / "images"
    images_dir.mkdir(exist_ok=True)

    print(f"Generating images for: {deck['parasha_en']}")
    print(f"Output directory: {images_dir}")
    print(f"Model: {args.model}")
    print("-" * 50)

    # Select generation function
    generate_fn = generate_image_gemini if args.model == "imagen" else generate_image_gemini_flash

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

        output_path = images_dir / f"{card_id}.png"

        # Skip if image exists and flag set
        if args.skip_existing and output_path.exists():
            print(f"[SKIP] {card_id} - image exists")
            skip_count += 1
            continue

        prompt = card.get("image_prompt", "")
        if not prompt:
            print(f"[SKIP] {card_id} - no prompt")
            skip_count += 1
            continue

        print(f"[GEN] {card_id}: {card['title_en'][:30]}...")

        if generate_fn(prompt, api_key, str(output_path)):
            print(f"  -> Saved: {output_path.name}")
            success_count += 1

            # Update deck with image path
            card["image_path"] = f"images/{card_id}.png"
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
        print(f"\nImages saved to: {images_dir}")
        print(f"Deck updated with image paths: {deck_path}")


if __name__ == "__main__":
    main()
