#!/usr/bin/env python3
"""
Generate character identity sheets into the shared character library (characters/{key}/).

An identity sheet is the one picture every card generation copies a character from:
a 3-angle turnaround (front, 3/4, side) plus a row of 4 expressions, plain light
background, no text. The look comes from the character's locked visual_anchors in
characters/{key}/character.yaml, and the art style from a series style plate.

Workflow (Simon picks, like an audition):
    # 1. Make 2 candidate versions -> characters/adam/identity_v1.png, identity_v2.png
    python generate_references.py --character adam --versions 2
    # 2. Promote the winner -> identity.png; the others move to characters/adam/alternates/
    python generate_references.py --character adam --accept v2

character.yaml `identity:` is updated by --accept.
"""

import argparse
import logging
import os
import re
import shutil
import sys
import time
from pathlib import Path

import character_library
import style_config
from config import DEFAULT_IMAGE_SIZE, VALID_IMAGE_SIZES
from generate_images import _load_image_as_part, generate_image_nano_banana, setup_logging

logger = logging.getLogger("generate_images")  # same logger: errors go to project.log

IDENTITY_ASPECT_RATIO = "16:9"
DEFAULT_STYLE_PLATE = "landscape"
VERSION_PATTERN = re.compile(r"identity_v(\d+)\.png$")


def generate_image(prompt: str, api_key: str, output_path: str, aspect_ratio: str = IDENTITY_ASPECT_RATIO,
                   image_size: str = DEFAULT_IMAGE_SIZE, reference_images: list = None,
                   purpose: str = "") -> bool:
    """Generate one image with the shared Nano Banana 2 helper (model from GEMINI_IMAGE_MODEL)."""
    result = generate_image_nano_banana(prompt, api_key, output_path, aspect_ratio=aspect_ratio,
                                        image_size=image_size, reference_images=reference_images,
                                        purpose=purpose)
    return result["success"]


# =============================================================================
# PROMPT
# =============================================================================

def get_identity_prompt(key: str, library_dir=None, with_style_plate: bool = True) -> str:
    """Build the identity-sheet prompt from the character's locked anchors in character.yaml."""
    character = character_library.load_character(key, library_dir)
    if not character:
        raise ValueError(f"'{key}' is not in the characters/ library. Create characters/{key}/character.yaml first.")

    anchors = "\n".join(f"- {a}" for a in character["visual_anchors"])
    personality = ", ".join(character.get("personality", []))
    style_line = ("Image 1 is a style plate: match its art style exactly (line weight, flat colors "
                  "with one soft gradient, warm palette). Copy the style only, not its content.\n"
                  if with_style_plate else "")

    return f"""{style_line}Create a CHARACTER IDENTITY SHEET for a children's picture-card series (ages 4-6).

=== STYLE ===
{style_config.load()["style_anchors"].strip()}
Head-to-body ratio about 1:3. Large friendly eyes. Rounded, simple shapes.
Same proportions and line weight as every other character in this series.

=== CHARACTER: {character["name_en"].upper()} ({character["gender"]}) ===
{anchors}
Personality: {personality}.
Modest Modern Orthodox dress: simple, full-coverage clothing as described above. No leaves, nothing revealing.

=== LAYOUT ===
One clean sheet on a plain, light, solid background. No scenery.
TOP ROW: a 3-angle turnaround of the full figure, head to toe, standing relaxed:
front view, three-quarter view, side view.
BOTTOM ROW: 4 head-and-shoulders portraits with different expressions:
happy, curious, caring, surprised.
Every drawing shows the EXACT SAME CHARACTER: same face, hair, skin, clothing and colors.
Hands relaxed and simple, exactly 5 fingers each.

=== CRITICAL ===
NO text, captions, labels, names, numbers or letters anywhere on the sheet.
No borders or panel frames; just the drawings on the plain background."""


# =============================================================================
# VERSIONS
# =============================================================================

def character_folder(key: str, library_dir=None) -> Path:
    return Path(library_dir or character_library.LIBRARY_DIR) / character_library.resolve_key(key, library_dir)


def next_version(folder: Path) -> int:
    """1 + the highest identity_vN.png already in the folder or its alternates/ (so numbers never repeat)."""
    numbers = [int(m.group(1)) for p in list(folder.glob("identity_v*.png")) + list(folder.glob("alternates/identity_v*.png"))
               if (m := VERSION_PATTERN.search(p.name))]
    return max(numbers, default=0) + 1


def generate_identity_versions(key: str, api_key: str, versions: int = 2, style_plate: str = DEFAULT_STYLE_PLATE,
                               image_size: str = DEFAULT_IMAGE_SIZE, library_dir=None) -> list:
    """Generate N candidate sheets as characters/{key}/identity_vN.png. Returns the saved paths."""
    folder = character_folder(key, library_dir)
    prompt = get_identity_prompt(key, library_dir, with_style_plate=bool(style_plate))

    reference_images = []
    if style_plate:
        plate = style_config.plate_path(style_plate)
        if plate:
            reference_images = [{"text": f"Image 1 = {style_config.reference_label('style_plate', style_plate)}:"},
                                _load_image_as_part(plate)]
        else:
            logger.error(f"Style plate '{style_plate}' not found; generating {key} without a style reference")

    saved = []
    start = next_version(folder)
    for number in range(start, start + versions):
        path = folder / f"identity_v{number}.png"
        print(f"[GEN] {key} identity v{number} ({image_size}, {IDENTITY_ASPECT_RATIO})...")
        if generate_image(prompt, api_key, str(path), IDENTITY_ASPECT_RATIO, image_size,
                          reference_images, purpose=f"{key} identity v{number}"):
            print(f"  -> Saved: {path}")
            saved.append(path)
        else:
            logger.error(f"  {key} identity v{number} FAILED")
        time.sleep(2)

    (folder / "identity_prompt.txt").write_text(prompt, encoding="utf-8")
    print(f"{key}: {len(saved)} of {versions} versions saved")
    return saved


def set_yaml_identity(yaml_path: Path, filename: str) -> None:
    """Set `identity:` in character.yaml, keeping every comment and line as written."""
    text = yaml_path.read_text(encoding="utf-8")
    new_text, count = re.subn(r"^identity:.*$", f"identity: {filename}", text, count=1, flags=re.M)
    if count == 0:
        raise ValueError(f"No 'identity:' line in {yaml_path}")
    yaml_path.write_text(new_text, encoding="utf-8")


def accept_version(key: str, version, library_dir=None) -> Path:
    """
    Promote identity_vN.png to identity.png. Every other identity_v*.png (and an older
    identity.png, if there was one) moves to characters/{key}/alternates/.
    Updates character.yaml `identity: identity.png`.
    """
    number = int(str(version).lower().lstrip("v"))
    folder = character_folder(key, library_dir)
    chosen = folder / f"identity_v{number}.png"
    if not chosen.exists():
        raise FileNotFoundError(f"{chosen} does not exist")

    alternates = folder / "alternates"
    alternates.mkdir(exist_ok=True)

    current = folder / "identity.png"
    if current.exists():
        backup = alternates / "identity_previous.png"
        n = 2
        while backup.exists():
            backup = alternates / f"identity_previous_{n}.png"
            n += 1
        shutil.move(str(current), str(backup))
        print(f"  old identity.png -> {backup.relative_to(folder)}")

    shutil.move(str(chosen), str(current))
    for other in sorted(folder.glob("identity_v*.png")):
        shutil.move(str(other), str(alternates / other.name))
        print(f"  {other.name} -> alternates/")

    set_yaml_identity(folder / "character.yaml", "identity.png")
    print(f"{key}: identity_v{number}.png is now identity.png")
    return current


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate or accept character identity sheets (characters/{key}/)")
    parser.add_argument("--character", "-c", required=True, help="Library key, e.g. adam")
    parser.add_argument("--versions", type=int, default=2, help="How many candidate versions to make (default 2)")
    parser.add_argument("--accept", help="Promote a version to identity.png, e.g. --accept v2 (no API call)")
    parser.add_argument("--style-plate", default=DEFAULT_STYLE_PLATE,
                        help=f"Style plate to pass as Image 1 (default {DEFAULT_STYLE_PLATE}; 'none' to skip)")
    parser.add_argument("--size", default=DEFAULT_IMAGE_SIZE, choices=VALID_IMAGE_SIZES,
                        help=f"Output resolution (default {DEFAULT_IMAGE_SIZE})")
    parser.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY)")
    args = parser.parse_args(argv)
    setup_logging()

    if args.accept:
        accept_version(args.character, args.accept)
        return

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Gemini API key required")
        sys.exit(1)

    plate = None if args.style_plate.lower() == "none" else args.style_plate
    generate_identity_versions(args.character, api_key, args.versions, plate, args.size)
    print(f"\nLook at characters/{args.character}/identity_v*.png, then run:")
    print(f"  python generate_references.py --character {args.character} --accept vN")


if __name__ == "__main__":
    main()
