#!/usr/bin/env python3
"""
Generate comprehensive character reference sheets for Parasha Pack.

Creates multiple reference types:
1. Portrait + Full Body (basic identity)
2. Expression Sheet (6 key emotions)
3. Turnaround Sheet (front, side, back, 3/4 views)
4. Pose References (key action poses)
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

EMOTIONS = ["happy", "sad", "scared", "surprised", "proud", "confused"]

EMOTION_DESCRIPTIONS = {
    "happy": "big warm smile, eyes crinkled with joy, eyebrows raised",
    "sad": "downturned mouth, droopy eyes, slight frown, eyebrows angled down",
    "scared": "wide eyes, raised eyebrows, mouth open in worry, leaning back slightly",
    "surprised": "very wide eyes, raised eyebrows high, mouth open in 'O' shape",
    "proud": "slight smile, chin up, chest out, confident knowing expression",
    "confused": "tilted head, one eyebrow raised, slight frown, puzzled look",
}


# =============================================================================
# REFERENCE SHEET PROMPTS
# =============================================================================

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


def get_expression_sheet_prompt(char_key: str) -> str:
    """6-emotion expression sheet."""
    char = CHARACTERS[char_key]
    emotion_grid = "\n".join([
        f"- {emo.upper()}: {EMOTION_DESCRIPTIONS[emo]}"
        for emo in EMOTIONS
    ])

    return f"""Create an EXPRESSION REFERENCE SHEET for a children's book character.

=== STYLE ===
Vivid, high-contrast cartoon style for ages 4-6.
- Rounded, friendly shapes
- Large expressive eyes (20% of face)
- Thick, clean black outlines
- Bold colors
- Clear, exaggerated expressions visible from across a room
- NO text or labels

=== CHARACTER ===
{char["base_description"]}

=== LAYOUT ===
A 3x2 GRID of the SAME CHARACTER showing 6 DIFFERENT EMOTIONS.
Each cell shows head and shoulders only, same angle, same character.

The 6 expressions (in order, left to right, top to bottom):
{emotion_grid}

CRITICAL: Every cell must show the EXACT SAME CHARACTER (same face shape, same beard, same clothing colors, same style) - ONLY the facial expression changes.

Clean white background for each cell.
Grid layout with thin dividing lines between cells.
Each expression must be DRAMATICALLY CLEAR - a child should instantly recognize the emotion.
"""


def get_turnaround_prompt(char_key: str) -> str:
    """4-view turnaround sheet."""
    char = CHARACTERS[char_key]
    return f"""Create a CHARACTER TURNAROUND REFERENCE SHEET for a children's book.

=== STYLE ===
Vivid, high-contrast cartoon style for ages 4-6.
- Rounded, friendly shapes
- Large expressive eyes
- Thick, clean black outlines
- Bold colors
- NO text or labels

=== CHARACTER ===
{char["base_description"]}

=== LAYOUT ===
4 VIEWS of the SAME CHARACTER in a horizontal row:

1. FRONT VIEW - facing viewer directly, neutral pose
2. 3/4 VIEW - turned 45 degrees to the right
3. SIDE VIEW (PROFILE) - facing right, full profile
4. BACK VIEW - facing away from viewer

All 4 views must show:
- The EXACT SAME CHARACTER
- Same height/proportions
- Same outfit colors and details
- Same staff
- Standing in similar neutral pose
- Clean white background

This is a turnaround reference for maintaining consistency from any angle.
"""


def get_pose_sheet_prompt(char_key: str, poses: list) -> str:
    """Custom pose reference sheet."""
    char = CHARACTERS[char_key]
    pose_list = "\n".join([f"- {pose}" for pose in poses])

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
{char["base_description"]}

=== POSES ===
Show the SAME CHARACTER in {len(poses)} different action poses:

{pose_list}

=== LAYOUT ===
Arrange poses in a grid or row.
Each pose shows full body.
Clean white background.
All poses must show the EXACT SAME CHARACTER with identical features, clothing, and style.
"""


# =============================================================================
# MAIN GENERATION
# =============================================================================

def generate_all_references(api_key: str, output_dir: str, characters: list = None):
    """Generate all reference sheets for specified characters."""
    ref_dir = Path(output_dir)
    ref_dir.mkdir(parents=True, exist_ok=True)

    if characters is None:
        characters = list(CHARACTERS.keys())

    results = {}

    for char_key in characters:
        char_name = CHARACTERS[char_key]["name"]
        print(f"\n{'='*50}")
        print(f"Generating references for: {char_name}")
        print('='*50)

        char_results = {}

        # 1. Identity Sheet (Portrait + Full Body)
        identity_path = ref_dir / f"{char_key}_identity.png"
        print(f"\n[1/4] Identity Sheet (Portrait + Full Body)...")
        if generate_image(get_identity_prompt(char_key), api_key, str(identity_path), "16:9"):
            print(f"    -> Saved: {identity_path.name}")
            char_results["identity"] = str(identity_path)
        else:
            print(f"    -> FAILED")
        time.sleep(3)

        # 2. Expression Sheet (6 emotions)
        expression_path = ref_dir / f"{char_key}_expressions.png"
        print(f"\n[2/4] Expression Sheet (6 emotions)...")
        if generate_image(get_expression_sheet_prompt(char_key), api_key, str(expression_path), "3:2"):
            print(f"    -> Saved: {expression_path.name}")
            char_results["expressions"] = str(expression_path)
        else:
            print(f"    -> FAILED")
        time.sleep(3)

        # 3. Turnaround Sheet (4 angles)
        turnaround_path = ref_dir / f"{char_key}_turnaround.png"
        print(f"\n[3/4] Turnaround Sheet (4 angles)...")
        if generate_image(get_turnaround_prompt(char_key), api_key, str(turnaround_path), "16:9"):
            print(f"    -> Saved: {turnaround_path.name}")
            char_results["turnaround"] = str(turnaround_path)
        else:
            print(f"    -> FAILED")
        time.sleep(3)

        # 4. Pose Sheet (key actions)
        poses = {
            "moses": [
                "Arms wide open, welcoming embrace (for reunion scene)",
                "Hand to ear, listening carefully (for Sinai scene)",
                "Seated, looking tired, hand on forehead (for advice scene)",
                "Standing tall, staff raised, leading (for journey scene)",
            ],
            "yitro": [
                "One finger raised, giving wise advice (for advice scene)",
                "Arms open wide for embrace (for reunion scene)",
                "Hand on chin, thinking wisely (for contemplation)",
                "Walking with staff, traveling (for journey scene)",
            ],
        }

        pose_path = ref_dir / f"{char_key}_poses.png"
        print(f"\n[4/4] Pose Sheet (4 key poses)...")
        if generate_image(get_pose_sheet_prompt(char_key, poses.get(char_key, [])), api_key, str(pose_path), "16:9"):
            print(f"    -> Saved: {pose_path.name}")
            char_results["poses"] = str(pose_path)
        else:
            print(f"    -> FAILED")
        time.sleep(3)

        results[char_key] = char_results

    # Save manifest
    manifest_path = ref_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n\nManifest saved to: {manifest_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Generate character reference sheets")
    parser.add_argument("--output", "-o", default="decks/yitro/references", help="Output directory")
    parser.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY)")
    parser.add_argument("--character", "-c", help="Generate for specific character only (moses/yitro)")
    parser.add_argument("--type", "-t", choices=["identity", "expressions", "turnaround", "poses", "all"],
                        default="all", help="Type of reference to generate")

    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Gemini API key required")
        sys.exit(1)

    characters = [args.character] if args.character else None

    generate_all_references(api_key, args.output, characters)

    print("\n" + "="*50)
    print("REFERENCE GENERATION COMPLETE")
    print("="*50)
    print(f"\nReference sheets saved to: {args.output}/")
    print("\nGenerated sheets per character:")
    print("  - *_identity.png    : Portrait + Full Body")
    print("  - *_expressions.png : 6 Emotions Grid")
    print("  - *_turnaround.png  : Front/3-4/Side/Back")
    print("  - *_poses.png       : Key Action Poses")


if __name__ == "__main__":
    main()
