#!/usr/bin/env python3
"""
Generate character identity reference sheets for Parasha Pack.

Creates a single identity sheet per character (portrait + full body) which
serves as the visual source of truth for all card image generations.

Usage:
    python generate_references.py --output ../decks/purim/references
    python generate_references.py --output ../decks/purim/references --character esther
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


def generate_image(prompt: str, api_key: str, output_path: str, aspect_ratio: str = "16:9") -> bool:
    """Generate image using Nano Banana Pro."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/nano-banana-pro-preview:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "imageConfig": {"aspectRatio": aspect_ratio}
        }
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

        with urllib.request.urlopen(req, timeout=180) as response:
            result = json.loads(response.read().decode())

        if "candidates" in result:
            for candidate in result["candidates"]:
                for part in candidate.get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        image_data = part["inlineData"].get("data")
                        if image_data:
                            with open(output_path, "wb") as f:
                                f.write(base64.b64decode(image_data))
                            return True
        return False
    except Exception as e:
        print(f"    Error: {e}")
        return False


# =============================================================================
# CHARACTER DEFINITIONS
# =============================================================================

CHARACTERS = {
    "moses": {
        "name": "Moses",
        "base_description": """Children's book cartoon character MOSES:
- Friendly middle-aged man
- Warm brown skin
- Kind, gentle LARGE expressive eyes (20% of face)
- Short dark beard with touch of gray
- Blue head covering flowing down
- Blue outer robe with cream/white undergarment
- Wooden shepherd's crook staff
- Rounded, friendly cartoon style
- Thick clean black outlines
- Bold colors, simple shapes""",
    },
    "yitro": {
        "name": "Yitro",
        "base_description": """Children's book cartoon character YITRO (Jethro):
- Wise elderly grandfather figure
- Long flowing WHITE/GRAY beard (distinguished)
- Warm, twinkling wise eyes (LARGE, 20% of face)
- Tan/olive head covering
- Colorful earth-toned Midianite robes (browns, reds, golds with geometric patterns)
- Walking staff (wooden, gnarled)
- Grandfatherly gentle smile
- Rounded, friendly cartoon style
- Thick clean black outlines
- Bold colors, simple shapes""",
    },
}


def get_identity_prompt(char_key: str) -> str:
    """Portrait + Full Body identity sheet."""
    char = CHARACTERS[char_key]
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
{char["base_description"]}

=== LAYOUT ===
Side-by-side panels on clean white background:

LEFT (50%): CLOSE-UP PORTRAIT
- Head and shoulders
- Neutral friendly expression
- Clear view of face, eyes, beard, head covering
- Looking slightly toward viewer

RIGHT (50%): FULL BODY STANDING
- Complete figure head to toe
- Same outfit and features
- Standing in relaxed pose
- Holding staff naturally
- Same character, same style

Both panels must show the EXACT SAME CHARACTER with identical features, colors, and style.
Clean white background, no environment.
"""


def generate_identity_refs(api_key: str, output_dir: str, characters: list = None):
    """Generate identity reference sheets for specified characters."""
    ref_dir = Path(output_dir)
    ref_dir.mkdir(parents=True, exist_ok=True)

    if characters is None:
        characters = list(CHARACTERS.keys())

    manifest = {}

    # Load existing manifest to preserve entries for characters we're not regenerating
    manifest_path = ref_dir / "manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except Exception:
            pass

    for char_key in characters:
        if char_key not in CHARACTERS:
            print(f"Unknown character: {char_key}")
            continue

        char_name = CHARACTERS[char_key]["name"]
        print(f"\n{'='*50}")
        print(f"Generating identity reference for: {char_name}")
        print('='*50)

        identity_path = ref_dir / f"{char_key}_identity.png"
        print(f"\n  Identity Sheet (Portrait + Full Body)...")
        if generate_image(get_identity_prompt(char_key), api_key, str(identity_path), "16:9"):
            print(f"    -> Saved: {identity_path.name}")
            manifest[char_key] = {"identity": identity_path.name}
        else:
            print(f"    -> FAILED")
        time.sleep(3)

    # Save manifest with relative filenames
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\n\nManifest saved to: {manifest_path}")

    return manifest


def main():
    parser = argparse.ArgumentParser(description="Generate character identity reference sheets")
    parser.add_argument("--output", "-o", default="decks/yitro/references", help="Output directory")
    parser.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY)")
    parser.add_argument("--character", "-c", help="Generate for specific character only")

    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Gemini API key required")
        sys.exit(1)

    characters = [args.character] if args.character else None

    generate_identity_refs(api_key, args.output, characters)

    print("\n" + "="*50)
    print("REFERENCE GENERATION COMPLETE")
    print("="*50)
    print(f"\nIdentity sheets saved to: {args.output}/")
    print("  - *_identity.png : Portrait + Full Body")


if __name__ == "__main__":
    main()
