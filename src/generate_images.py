#!/usr/bin/env python3
"""
Generate images for Parasha Pack cards using Google Gemini.

Usage:
    export GEMINI_API_KEY="your-api-key"
    python generate_images.py ../decks/yitro/deck.json                 # 2K, one image per card
    python generate_images.py ../decks/yitro/deck.json --card story_1 --draft     # 1K drafts
    python generate_images.py ../decks/yitro/deck.json --final --from-draft ../decks/yitro/raw/drafts/story_1_d2.png
    python generate_images.py ../decks/bereshit/deck.json --card story_5 --edit-from ../decks/bereshit/raw/story_6.png
        (image EDIT: the card's image_prompt says only what to change; same composition, 2K)

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
import io
import logging
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

import character_library
import spend_ledger
import style_config
from config import (DEFAULT_IMAGE_MODEL, DEFAULT_IMAGE_SIZE, VALID_IMAGE_SIZES,
                    EXPECTED_DIMENSIONS_3_4, DRAFT_IMAGE_SIZE, FINAL_IMAGE_SIZE,
                    DEFAULT_DRAFT_VARIANTS)

logger = logging.getLogger("generate_images")

# Image generation can take a while at 2K/4K, especially with "thinking"
REQUEST_TIMEOUT_SECONDS = 300

# Errors also go to project.log in the repo root
PROJECT_LOG = Path(__file__).resolve().parent.parent / "project.log"


def setup_logging() -> None:
    """Print INFO+ to the console and append ERROR+ to project.log."""
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(message)s"))

    error_file = logging.FileHandler(PROJECT_LOG, delay=True)  # file created only on first error
    error_file.setLevel(logging.ERROR)
    error_file.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))

    logger.setLevel(logging.INFO)
    logger.addHandler(console)
    logger.addHandler(error_file)

# PIL overlay system is deprecated - text overlay now handled by Card Designer React components
# See card-designer/ for the React-based text overlay system


def is_v2_card(card: dict) -> bool:
    """Check if a card uses v2 format (has front/back structure)."""
    return "front" in card and "back" in card


def build_generation_prompt(scene_prompt: str, card_type: str, story_world: str = "",
                            character_refs_loaded: list = None,
                            manifest: dict = None,
                            palette: list = None,
                            anchor_keys: list = None,
                            reference_labels: list = None) -> str:
    """
    Build a complete generation prompt by layering system concerns onto a scene description.

    Deck prompts (image_prompt in deck.json) should be PURE SCENE DESCRIPTIONS —
    what to draw, not how to draw it. This function adds all system layers
    (all text comes from style/style_config.yaml via image_prompts):

    0. Reference images  — numbered list naming each reference image ("Image 1 = style plate ...")
    1. Style anchors     — visual consistency (children's illustration style)
    2. World style       — MODERN_WORLD_STYLE for connection/tradition,
                           story_world (from deck.json) for all other card types,
                           plus "Deck palette accents" when deck.json has a palette
    3. Safety rules      — content restrictions (no God in human form, etc.)
    4. Scene description — from deck.json (passed through unchanged)
    4a. Character anchors — locked visual anchors from characters/{key}/character.yaml
    4b. Ref hint         — when character refs are loaded, tell model to prioritize them
    5. Composition       — per-card-type cinematography (where to place subjects)
    6. Critical rules    — universal (no text, no borders)

    Args:
        scene_prompt: Scene-only image prompt from deck.json
        card_type: Card type (anchor, spotlight, story, etc.)
        story_world: Per-deck historical setting (from deck.json "story_world")
        character_refs_loaded: Character keys whose identity images were loaded
        manifest: Deck references/manifest.json (only for labels of non-library characters)
        palette: Optional list of hex colors from deck.json "palette"
        anchor_keys: Character keys whose locked anchors should be added (characters_in_scene)
        reference_labels: Labels of the reference images, in the order they are sent

    Returns:
        Complete prompt with all system layers applied
    """
    from image_prompts import (
        STYLE_ANCHORS_V2, SAFETY_PROMPT,
        COMPOSITION_GUIDANCE, COMPOSITION_SUFFIX,
        MODERN_WORLD_STYLE,
    )

    # Card types that use the modern world vs story world
    modern_world_cards = {"connection", "tradition"}
    palette_line = f"Deck palette accents: {', '.join(palette)}." if palette else ""

    parts = []

    # 0. Name every reference image so the model knows what each one is for
    if reference_labels:
        lines = [f"Image {n} = {label}" for n, label in enumerate(reference_labels, start=1)]
        parts.append("=== REFERENCE IMAGES ===\n" + "\n".join(lines))

    # 1. Style anchors (all cards)
    parts.append(f"=== STYLE ===\n{STYLE_ANCHORS_V2.strip()}")

    # 2. World style (modern or story, based on card type) + optional deck palette
    if card_type in modern_world_cards:
        world = MODERN_WORLD_STYLE.strip()
        parts.append(f"{world}\n\n{palette_line}" if palette_line else world)
    elif story_world:
        world = (f"=== WORLD: STORY SETTING ===\n{story_world.strip()}\n\n"
                 f"All scenes should feel like they belong in this world. Consistent architecture, "
                 f"clothing, lighting, and color palette throughout.")
        parts.append(f"{world}\n{palette_line}" if palette_line else world)
    elif palette_line:
        parts.append(f"=== WORLD ===\n{palette_line}")

    # 3. Safety rules
    parts.append(f"=== SAFETY RULES ===\n{SAFETY_PROMPT}")

    # 4. Scene description (from deck.json — passed through unchanged)
    parts.append(f"=== SCENE ===\n{scene_prompt.strip()}")

    # 4a. Locked character anchors from the library (typed once in character.yaml, not per deck)
    anchor_lines = [character_library.visual_anchor_text(key) for key in (anchor_keys or [])]
    anchor_lines = [line for line in anchor_lines if line]
    if anchor_lines:
        parts.append("=== CHARACTER ANCHORS (locked, always keep) ===\n" +
                     "\n".join(f"- {line}" for line in anchor_lines))

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
                   character_refs: list, success: bool, image_size: str = None,
                   references: list = None, output_file: str = None) -> None:
    """
    Append a generation record to the deck's JSONL log (append-only, never rotated).

    Fields: card_id, timestamp, model, image_size, prompt_version, full_prompt,
    character_refs, references (label + path of every reference image, in order),
    output_file, success.
    """
    log_path = deck_path.parent / "raw" / "generations.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "card_id": card_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "image_size": image_size,
        "prompt_version": style_config.prompt_version(),
        "full_prompt": full_prompt,
        "character_refs": character_refs,
        "references": references or [],
        "output_file": output_file,
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
    prompts_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = prompts_dir / f"{card_id}.txt"
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(full_prompt)


def get_character_label(character_key: str, manifest: dict) -> str:
    """Derive human-readable label: library name_en, else manifest 'label', else title-cased key.

    Only call for character entries — non-character keys (style_hero) are skipped
    by the caller before reaching this function.
    """
    character = character_library.load_character(character_key)
    if character:
        return character["name_en"]
    entry = manifest.get(character_key, {})
    if isinstance(entry, dict):
        return entry.get("label", character_key.replace("_", " ").title())
    return character_key.replace("_", " ").title()


# Reference images bigger than this (long side, pixels) are shrunk before sending.
# Six 2K PNGs (~5 MB each) would blow the API's 20 MB inline request limit.
MAX_REFERENCE_SIDE = 1536


def _load_image_as_part(image_path: Path) -> dict:
    """Load an image file as an API inline-data part, shrinking big images to a JPEG."""
    with Image.open(image_path) as img:
        if max(img.size) <= MAX_REFERENCE_SIDE:
            data, mime = Path(image_path).read_bytes(), Image.MIME.get(img.format, "image/png")
        else:
            small = img.convert("RGB")
            small.thumbnail((MAX_REFERENCE_SIDE, MAX_REFERENCE_SIDE))
            buffer = io.BytesIO()
            small.save(buffer, format="JPEG", quality=90)
            data, mime = buffer.getvalue(), "image/jpeg"
    return {"inlineData": {"mimeType": mime, "data": base64.b64encode(data).decode("utf-8")}}


# Card types that belong to the story world (receive the legacy style hero)
STORY_WORLD_CARDS = {"anchor", "spotlight", "story", "power_word"}

# Nano Banana 2 accepts at most 4 character reference images per request
MAX_CHARACTER_REFS = style_config.max_character_refs()


def _find_character_ref(key: str, manifest: dict, refs_dir: Path) -> tuple:
    """Find one character's identity image: shared library first, then the deck manifest.

    Returns (path, label), or (None, None) if no image exists anywhere.
    """
    library_path = character_library.identity_path(key)
    if library_path:
        character = character_library.load_character(key)
        return library_path, character["name_en"]

    # Fallback: the deck's own references/manifest.json (older decks)
    entry = manifest.get(key)
    identity_file = entry.get("identity", "") if isinstance(entry, dict) else ""
    if identity_file and (refs_dir / identity_file).exists():
        logger.warning(f"  -> {key}: not in characters/ library, using deck manifest image {identity_file}")
        return refs_dir / identity_file, get_character_label(key, manifest)

    logger.warning(f"  -> {key}: no identity image in characters/ or the deck manifest; skipping")
    return None, None


def load_manifest(deck_path: Path) -> dict:
    """Read the deck's references/manifest.json ({} if missing or broken)."""
    manifest_path = deck_path.parent / "references" / "manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"  -> Warning: failed to load manifest: {e}")
        return {}


# Image edits (--edit-from): the model gets ONE picture to change and a short "only change ..." list.
# No style plates (the input picture already has the style) and no long scene layers, so it doesn't
# redraw the whole scene. Used for sequence decks whose cards are one frame filling up (or emptying).
EDIT_INSTRUCTIONS = (
    "Edit Image 1. Keep the exact same composition, camera position, framing, horizon line and art "
    "style: every element that is not mentioned below stays exactly where and how it is.\n"
    "Only change:"
)


def build_edit_prompt(change: str, reference_labels: list = None, anchor_keys: list = None) -> str:
    """
    Prompt for an image EDIT (--edit-from): reference list, the edit instruction, the change from
    the card's image_prompt, locked character anchors, safety rules and the no-text rules.
    """
    from image_prompts import SAFETY_PROMPT, COMPOSITION_SUFFIX

    parts = []
    if reference_labels:
        lines = [f"Image {n} = {label}" for n, label in enumerate(reference_labels, start=1)]
        parts.append("=== REFERENCE IMAGES ===\n" + "\n".join(lines))
    parts.append(f"=== EDIT ===\n{EDIT_INSTRUCTIONS}\n{change.strip()}")
    anchor_lines = [character_library.visual_anchor_text(key) for key in (anchor_keys or [])]
    anchor_lines = [line for line in anchor_lines if line]
    if anchor_lines:
        parts.append("=== CHARACTER ANCHORS (locked, always keep) ===\n" +
                     "\n".join(f"- {line}" for line in anchor_lines))
    parts.append(f"=== SAFETY RULES ===\n{SAFETY_PROMPT}")
    parts.append(COMPOSITION_SUFFIX.strip())
    return "\n\n".join(parts)


def _resolve_continuity_ref(deck_path: Path, value: str):
    """continuity_ref is a card_id ('story_1' -> raw/story_1.png) or a path relative to the deck folder."""
    deck_dir = deck_path.parent
    for candidate in (deck_dir / "raw" / f"{value}.png", deck_dir / value, Path(value)):
        if candidate.is_file():
            return candidate
    logger.error(f"  -> continuity_ref '{value}' not found (looked in raw/ and the deck folder); skipping")
    return None


def assemble_references(deck_path: Path, card: dict, deck: dict = None,
                        no_style: bool = False, no_refs: bool = False,
                        draft_path: Path = None, edit_path: Path = None) -> dict:
    """
    Collect every reference image for one card, in a FIXED, LABELED order:

      0. The image to edit           only for --edit-from (then no style plates and no
                                     continuity ref: the input image already carries both)
      1. Style plates (1-2, max 3)   chosen by card.style_plate, else the plate mapping
                                     (legacy deck style_hero only if style/plates/ is empty)
      2. Draft composition           only for --final --from-draft
      3. Continuity reference        card.continuity_ref (an earlier raw image)
      4. Character identity sheets   from characters/ (max 4), filtered by characters_in_scene

    Args:
        no_style: skip style plates / style hero (the --no-hero flag)
        no_refs: skip continuity + character refs (the --no-refs flag). Style plates
                 are also skipped, matching the old "no references at all" behaviour;
                 an explicit draft is still passed.

    Returns a dict:
        parts       - API parts (a short "Image N:" text before each image, then a closing line)
        labels      - label strings in send order (for the prompt's REFERENCE IMAGES block)
        references  - [{"label", "path"}] for generations.jsonl
        characters  - character keys whose identity images were loaded
    """
    deck = deck or {}
    card_type = card.get("card_type", "")
    refs_dir = deck_path.parent / "references"
    manifest = load_manifest(deck_path)
    images = []  # (label, path, character_key or None) in send order

    # 0. The image to edit (--edit-from) always goes first, as Image 1
    if edit_path:
        images.append((style_config.reference_label("edit"), Path(edit_path), None))

    # 1. Style plates (or the legacy per-deck style hero when no plates exist)
    if not no_style and not no_refs and not edit_path:
        if style_config.any_plates_exist():
            for name in style_config.plates_for_card(card, deck):
                path = style_config.plate_path(name)
                if path:
                    images.append((style_config.reference_label("style_plate", name), path, None))
        elif card_type in STORY_WORLD_CARDS:
            hero_file = (manifest.get("style_hero") or {}).get("identity", "")
            if hero_file and (refs_dir / hero_file).exists():
                images.append((style_config.reference_label("legacy_style_hero"), refs_dir / hero_file, None))

    # 2. Draft composition (--final --from-draft)
    if draft_path:
        images.append((style_config.reference_label("draft"), Path(draft_path), None))

    if not no_refs:
        # 3. Continuity reference
        continuity = card.get("continuity_ref")
        if continuity and not edit_path:
            path = _resolve_continuity_ref(deck_path, continuity)
            if path:
                images.append((style_config.reference_label("continuity", Path(continuity).stem), path, None))

        # 4. Character identity sheets
        characters_in_scene = card.get("characters_in_scene")  # None = all in manifest (old decks)
        if characters_in_scene is None:
            keys = [k for k in manifest if not k.startswith("style_hero")]
        else:
            keys = list(characters_in_scene)

        found = []  # (key, path, label)
        for key in keys:
            path, label = _find_character_ref(key, manifest, refs_dir)
            if path:
                found.append((key, path, label))

        if len(found) > MAX_CHARACTER_REFS:
            dropped = [key for key, _, _ in found[MAX_CHARACTER_REFS:]]
            logger.error(
                f"  -> {card.get('card_id', '?')}: {len(found)} character refs requested but the model "
                f"allows {MAX_CHARACTER_REFS}; sending the first {MAX_CHARACTER_REFS} and dropping: "
                f"{', '.join(dropped)}"
            )
            found = found[:MAX_CHARACTER_REFS]

        for key, path, label in found:
            images.append((style_config.reference_label("character", label), path, key))

    # Turn (label, path) pairs into API parts
    parts, labels, references, character_keys = [], [], [], []
    for label, path, key in images:
        try:
            image_part = _load_image_as_part(path)
        except Exception as e:
            logger.error(f"  -> Failed to load reference {path}: {e}")
            continue
        if key:
            character_keys.append(key)
        labels.append(label)
        parts.append({"text": f"Image {len(labels)} = {label}:"})
        parts.append(image_part)
        references.append({"label": label, "path": _display_path(path)})
        print(f"  -> Ref {len(labels)}: {label}")

    if parts:
        parts.append({"text": "Use the reference images above exactly as labeled. Now generate:"})

    return {"parts": parts, "labels": labels, "references": references, "characters": character_keys}


def _display_path(path: Path) -> str:
    """Path relative to the repo root when possible (shorter, machine-independent logs)."""
    try:
        return str(Path(path).resolve().relative_to(PROJECT_LOG.parent))
    except ValueError:
        return str(path)


def load_reference_images(deck_path: Path, characters_in_scene: list = None,
                          card_type: str = "", no_hero: bool = False) -> tuple:
    """
    Older entry point kept for callers/tests: returns (image_parts, loaded_char_keys).
    See assemble_references() for the full, labeled version.
    """
    card = {"card_type": card_type, "characters_in_scene": characters_in_scene}
    refs = assemble_references(deck_path, card, no_style=no_hero)
    return refs["parts"], refs["characters"]


def get_image_model() -> str:
    """Return the image model ID: GEMINI_IMAGE_MODEL from .env/env, else the default."""
    return os.environ.get("GEMINI_IMAGE_MODEL") or DEFAULT_IMAGE_MODEL


def validate_image_size(image_size: str) -> str:
    """Raise a clear error unless image_size is exactly one of 512, 1K, 2K, 4K."""
    if image_size not in VALID_IMAGE_SIZES:
        raise ValueError(
            f"Invalid image size {image_size!r}. "
            f"Use one of: {', '.join(VALID_IMAGE_SIZES)} (uppercase K)."
        )
    return image_size


def build_image_request(prompt: str, api_key: str, model: str, aspect_ratio: str = "3:4",
                        image_size: str = DEFAULT_IMAGE_SIZE, reference_images: list = None) -> tuple:
    """
    Build the URL and JSON payload for one image generation call.

    Pure function (no network) so it can be tested.

    Returns:
        (url, payload) tuple
    """
    validate_image_size(image_size)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    # Build parts list: reference images first, then prompt
    parts = []
    if reference_images:
        parts.extend(reference_images)
    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "imageConfig": {"aspectRatio": aspect_ratio, "imageSize": image_size},
        },
    }
    return url, payload


def extract_final_image(result: dict):
    """
    Pull the final image (base64 string) out of an API response.

    The model may "think" first and return draft images marked with
    "thought": true. We skip those and keep the LAST real image part.

    Returns:
        base64 image string, or None if the response has no final image
    """
    final_image = None
    for candidate in result.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if part.get("thought"):
                continue  # interim draft, not the final answer
            image_data = part.get("inlineData", {}).get("data")
            if image_data:
                final_image = image_data
    return final_image


def save_image_as_png(image_bytes: bytes, output_path: str) -> str:
    """
    Save image bytes to output_path as a real PNG file.

    Nano Banana 2 returns JPEG data, but the rest of the pipeline expects
    .png files. Writing JPEG bytes into a .png file "works" but the file
    lies about its format, so we re-encode anything that isn't already PNG.

    Returns:
        The MIME type the API actually sent (e.g. "image/jpeg")
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        original_mime = Image.MIME.get(img.format, img.format)
        if img.format == "PNG":
            with open(output_path, 'wb') as f:
                f.write(image_bytes)  # already PNG, save untouched
        else:
            logger.info(f"  -> API returned {original_mime}; re-encoding to PNG")
            img.save(output_path, format="PNG")
    return original_mime


def check_image_dimensions(output_path: str, aspect_ratio: str, image_size: str) -> tuple:
    """Log the saved image's pixel size and warn if it isn't what we asked for."""
    with Image.open(output_path) as img:
        width, height = img.size
    logger.info(f"  -> Image size: {width}x{height}")

    if aspect_ratio == "3:4":
        expected = EXPECTED_DIMENSIONS_3_4[image_size]
        if (width, height) != expected:
            logger.warning(
                f"  Unexpected dimensions {width}x{height} for {image_size} {aspect_ratio} "
                f"(expected {expected[0]}x{expected[1]}): {output_path}"
            )
    return width, height


def generate_image_nano_banana(prompt: str, api_key: str, output_path: str, aspect_ratio: str = "3:4",
                               reference_images: list = None, image_size: str = DEFAULT_IMAGE_SIZE,
                               model: str = None, purpose: str = "") -> dict:
    """
    Generate an image with Nano Banana 2 (or the model set in GEMINI_IMAGE_MODEL).

    Every real call is written to the spend ledger (when PP_SPEND_LEDGER is set),
    and the call is refused before any network request once PP_BUDGET_USD is reached.

    Args:
        prompt: The image generation prompt
        api_key: Gemini API key
        output_path: Path to save the generated image
        aspect_ratio: Aspect ratio (default 3:4 for cards)
        reference_images: Optional list of reference image parts
        image_size: "512", "1K", "2K" (default) or "4K"
        model: Model ID override (default: get_image_model())
        purpose: Short description for the spend ledger (e.g. "bereshit story_1 draft 1")

    Returns:
        Dict with 'success' (bool), 'prompt' (str) and, if refused, 'refused': True
    """
    model = model or get_image_model()
    url, payload = build_image_request(prompt, api_key, model, aspect_ratio, image_size, reference_images)
    purpose = purpose or Path(output_path).stem

    try:
        spend_ledger.check_budget()
    except spend_ledger.BudgetExceeded as e:
        logger.error(f"  {e} ({purpose})")
        return {"success": False, "prompt": prompt, "refused": True}

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method='POST')

        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            result = json.loads(response.read().decode())

        image_data = extract_final_image(result)
        if not image_data:
            logger.error(f"  No image in response from {model} for {output_path}")
            spend_ledger.record(purpose, image_size, 0.0, note="no image in response, not billed as an image")
            return {"success": False, "prompt": prompt}

        spend_ledger.record(purpose, image_size, spend_ledger.price_for(image_size))
        save_image_as_png(base64.b64decode(image_data), output_path)
        check_image_dimensions(output_path, aspect_ratio, image_size)
        return {"success": True, "prompt": prompt}

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        logger.error(f"  HTTP Error {e.code} from {model}: {error_body[:500]}")
        spend_ledger.record(purpose, image_size, 0.0, note=f"HTTP {e.code}, no image, not billed")
        return {"success": False, "prompt": prompt}
    except Exception as e:
        logger.error(f"  Error generating {output_path} with {model}: {e}")
        spend_ledger.record(purpose, image_size, 0.0, note=f"error: {type(e).__name__}")
        return {"success": False, "prompt": prompt}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Generate images for Parasha Pack cards")
    parser.add_argument("deck_path", help="Path to deck.json file")
    parser.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY env var)")
    parser.add_argument("--card", help="Generate image for specific card ID only")
    parser.add_argument("--skip-existing", action="store_true", help="Skip cards that already have images")
    parser.add_argument("--no-refs", action="store_true", help="Send no reference images (plates, continuity, characters)")
    parser.add_argument("--no-hero", action="store_true", help="Skip the style plates (and legacy style hero)")
    parser.add_argument("--variants", type=int, default=None,
                        help="Generate N variants per card (default 1, or 2 with --draft)")
    parser.add_argument("--size", default=None, choices=VALID_IMAGE_SIZES,
                        help=f"Output resolution (default {DEFAULT_IMAGE_SIZE}; --draft uses {DRAFT_IMAGE_SIZE})")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--draft", action="store_true",
                      help=f"Cheap drafts at {DRAFT_IMAGE_SIZE} to raw/drafts/{{card_id}}_d{{n}}.png")
    mode.add_argument("--final", action="store_true",
                      help=f"Final at {FINAL_IMAGE_SIZE} using --from-draft as a composition reference")
    parser.add_argument("--from-draft", help="Chosen draft image for --final (e.g. raw/drafts/story_1_d2.png)")
    mode.add_argument("--edit-from", metavar="IMAGE",
                      help=f"Edit this image instead of drawing a new one ({FINAL_IMAGE_SIZE}, needs --card): "
                           "the card's image_prompt lists only what to change; saved to raw/{card_id}.png")

    args = parser.parse_args(argv)
    if args.edit_from and not args.card:
        parser.error("--edit-from needs --card (one card per edit)")
    if args.final and not args.from_draft:
        parser.error("--final needs --from-draft path/to/{card_id}_dN.png")
    if args.from_draft and not args.final:
        parser.error("--from-draft only works with --final")
    return args


def resolve_run_mode(args) -> dict:
    """
    Turn the CLI flags into concrete settings:
      default  -> size 2K, 1 variant, raw/{card_id}.png
      --draft  -> size 1K, 2 variants, raw/drafts/{card_id}_d{n}.png
      --final  -> size 2K, 1 image, raw/{card_id}.png, the draft passed as a composition ref
    """
    if args.draft:
        return {"mode": "draft", "size": args.size or DRAFT_IMAGE_SIZE,
                "variants": args.variants or DEFAULT_DRAFT_VARIANTS, "draft_path": None, "card": args.card}
    if args.edit_from:
        return {"mode": "edit", "size": args.size or FINAL_IMAGE_SIZE, "variants": 1,
                "draft_path": None, "edit_path": Path(args.edit_from), "card": args.card}
    if args.final:
        draft_path = Path(args.from_draft)
        # story_1_d2.png -> story_1
        card_id = args.card or draft_path.stem.rsplit("_d", 1)[0]
        return {"mode": "final", "size": args.size or FINAL_IMAGE_SIZE, "variants": 1,
                "draft_path": draft_path, "card": card_id}
    return {"mode": "default", "size": args.size or DEFAULT_IMAGE_SIZE,
            "variants": args.variants or 1, "draft_path": None, "card": args.card}


# Card types whose front is drawn entirely by the Card Designer: no AI art, ever.
NO_ART_CARD_TYPES = ("home",)


def no_art_reason(card: dict) -> str | None:
    """Why this card gets no generated image, or None if it should be generated.

    Home cards have an image_prompt, but it is only a note ("No art: ..."), so the
    card type is checked first. Cards with an empty prompt are skipped too.
    """
    if card.get("card_type") in NO_ART_CARD_TYPES:
        return f"{card['card_type']} card (front drawn by the Card Designer)"
    if not card.get("image_prompt", "").strip():
        return "no image_prompt"
    return None


def output_path_for(raw_dir: Path, card_id: str, mode: str, variant_num: int, num_variants: int) -> Path:
    """Where one generated image goes."""
    if mode == "draft":
        return raw_dir / "drafts" / f"{card_id}_d{variant_num}.png"
    if num_variants > 1:
        return raw_dir / f"{card_id}_v{variant_num}.png"
    return raw_dir / f"{card_id}.png"


def main(argv=None):
    args = parse_args(argv)
    setup_logging()
    model_name = get_image_model()
    run = resolve_run_mode(args)

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
    if run["draft_path"] and not run["draft_path"].exists():
        print(f"Error: draft not found: {run['draft_path']}")
        sys.exit(1)
    if run.get("edit_path") and not run["edit_path"].exists():
        print(f"Error: image to edit not found: {run['edit_path']}")
        sys.exit(1)

    with open(deck_path, 'r', encoding='utf-8') as f:
        deck = json.load(f)

    # Setup output directory - raw/ for scene-only images
    raw_dir = deck_path.parent / "raw"
    raw_dir.mkdir(exist_ok=True)
    if run["mode"] == "draft":
        (raw_dir / "drafts").mkdir(exist_ok=True)

    # Get deck name, story world and optional palette
    deck_name = deck.get('parasha_en') or deck.get('holiday_en') or deck.get('deck_id') or 'Unknown'
    story_world = deck.get('story_world', '')
    palette = deck.get('palette') or None
    manifest = load_manifest(deck_path)

    print(f"Generating images for: {deck_name}")
    print(f"Output directory: {raw_dir}")
    print(f"Model: {model_name}  Size: {run['size']}  Mode: {run['mode']}  "
          f"Prompt version: {style_config.prompt_version()}")
    print("-" * 50)
    print("Note: Images are saved WITHOUT text overlay.")
    print("Use Card Designer (card-designer/) to render final cards with text.")
    print("-" * 50)

    success_count = 0
    skip_count = 0
    fail_count = 0
    matched = 0

    for card in deck["cards"]:
        card_id = card["card_id"]

        # Filter by specific card if requested
        if run["card"] and card_id != run["card"]:
            continue
        matched += 1

        reason = no_art_reason(card)
        if reason:
            logger.info(f"[SKIP] {card_id} - {reason}")
            skip_count += 1
            continue

        if args.skip_existing and (raw_dir / f"{card_id}.png").exists() and run["mode"] != "draft":
            print(f"[SKIP] {card_id} - image exists")
            skip_count += 1
            continue

        raw_prompt = card["image_prompt"]
        card_type = card.get("card_type", "")
        if is_v2_card(card):
            title = card.get("back", {}).get("title_en", card_id)[:30]
        else:
            title = card.get("title_en", card_id)[:30]
        print(f"[GEN] {card_id}: {title}...")

        # Reference images in a fixed, labeled order (plates, draft, continuity, characters)
        refs = assemble_references(deck_path, card, deck, no_style=args.no_hero,
                                   no_refs=args.no_refs, draft_path=run["draft_path"],
                                   edit_path=run.get("edit_path"))

        if run["mode"] == "edit":
            # Edit prompt: refs block + "keep everything, only change:" + the card's change list
            prompt = build_edit_prompt(raw_prompt, reference_labels=refs["labels"],
                                       anchor_keys=card.get("characters_in_scene") or [])
        else:
            # Full prompt: refs block + style + world + safety + scene + anchors + composition + rules
            prompt = build_generation_prompt(
                raw_prompt, card_type, story_world=story_world,
                character_refs_loaded=refs["characters"],
                manifest=manifest,
                palette=palette,
                anchor_keys=card.get("characters_in_scene") or [],
                reference_labels=refs["labels"],
            )
        save_prompt_sidecar(deck_path, card_id, prompt)

        num_variants = run["variants"]
        for variant_num in range(1, num_variants + 1):
            variant_path = output_path_for(raw_dir, card_id, run["mode"], variant_num, num_variants)
            if num_variants > 1:
                print(f"  variant {variant_num}/{num_variants}...")

            purpose = f"{deck.get('deck_id', deck_path.parent.name)} {card_id} {run['mode']} {variant_num}"
            result = generate_image_nano_banana(prompt, api_key, str(variant_path),
                                                reference_images=refs["parts"],
                                                image_size=run["size"], model=model_name,
                                                purpose=purpose)
            success = result["success"]

            log_generation(deck_path, card_id, model_name, prompt, refs["characters"], success,
                           image_size=run["size"], references=refs["references"],
                           output_file=_display_path(variant_path))

            if success:
                print(f"  -> Saved: {variant_path.relative_to(raw_dir)}")
                success_count += 1
            else:
                fail_count += 1
                if result.get("refused"):
                    print("Budget reached; stopping.")
                    break

            time.sleep(2)  # rate limiting between requests

        # Drafts don't change the card's canonical image
        if run["mode"] != "draft":
            card["image_path"] = f"raw/{card_id}.png"

    if run["card"] and matched == 0:
        logger.error(f"No card with card_id '{run['card']}' in {deck_path}")

    # Save updated deck with image paths
    if run["mode"] != "draft":
        with open(deck_path, 'w', encoding='utf-8') as f:
            json.dump(deck, f, indent=2, ensure_ascii=False)

    print("-" * 50)
    print(f"Complete! Success: {success_count}, Skipped: {skip_count}, Failed: {fail_count}")
    if run["mode"] == "draft" and success_count:
        print(f"\nDrafts in {raw_dir / 'drafts'}. Pick one, then run:")
        print(f"  python generate_images.py {deck_path} --final --from-draft {raw_dir / 'drafts'}/<card>_dN.png")
    elif success_count > 0:
        print(f"\nRaw images saved to: {raw_dir}")
        print(f"\nNext steps:")
        print(f"  1. cd card-designer && npm run dev")
        print(f"  2. npm run export {deck_path.parent.name}")


if __name__ == "__main__":
    main()
