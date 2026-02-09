#!/usr/bin/env python3
"""
Generate fresh art for a specific card using the Hybrid Pipeline constraints.
Target: Card-Designer Isolation.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path so we can import src.generate_images
# script is in card-designer/scripts
# project root is ../../
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# Add src to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.append(str(SRC_DIR))

try:
    from generate_images import generate_image_nano_banana
except ImportError as e:
    print(f"Error importing generate_images: {e}")
    print(f"sys.path: {sys.path}")
    sys.exit(1)

def main():
    # 1. Configuration
    deck_path = Path("content/terumah/deck.json") # Relative to card-designer root
    target_card_id = "story_1"
    
    # Check Isolation
    if not deck_path.exists():
        print(f"Error: Could not find deck at {deck_path}")
        print("Make sure you are running this from 'card-designer' directory!")
        sys.exit(1)

    # 2. Get API Key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set.")
        sys.exit(1)

    # 3. Load Data
    with open(deck_path, "r", encoding="utf-8") as f:
        deck = json.load(f)

    # 4. Find Card
    card = next((c for c in deck["cards"] if c["card_id"] == target_card_id), None)
    if not card:
        print(f"Error: Card {target_card_id} not found in deck.")
        sys.exit(1)

    # 5. Get Clean Prompt
    prompt = card.get("image_prompt_clean")
    if not prompt:
        print(f"Error: No 'image_prompt_clean' found for {target_card_id}. Run prepare_hybrid_prompts.py first.")
        sys.exit(1)

    print(f"--- Generating Art for {target_card_id} ---")
    print(f"Model: nano-banana-pro-preview")
    print(f"Prompt Length: {len(prompt)} chars")
    print("--- Prompt Preview ---")
    print(prompt[:300] + "...")
    print("----------------------")

    # 6. Generate
    output_dir = deck_path.parent / "images"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"{target_card_id}.png"

    print(f"Generating to {output_path}...")
    
    # We pass None for reference_images for this test to keep it simple, 
    # unless we want to enforce character consistency immediately. 
    # User asked for "test this out layout-wise", so pure generation is safer first.
    success = generate_image_nano_banana(
        prompt=prompt,
        api_key=api_key,
        output_path=str(output_path),
        aspect_ratio="3:4" # Using standard ratio, widely supported
    )

    if success:
        print(f"SUCCESS: Image saved to {output_path}")
    else:
        print("FAILURE: Generation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
