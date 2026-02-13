#!/usr/bin/env python3
"""
Text overlay module for Parasha Pack card fronts.

Overlays minimal text on generated card images programmatically.
Supports Hebrew with nikud and proper RTL text handling.

Usage:
    python overlay.py ../decks/purim/deck.json
    python overlay.py ../decks/purim/deck.json --card story_1
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow")
    sys.exit(1)


# =============================================================================
# CONFIGURATION
# =============================================================================

# Card dimensions (5x7 at 300 DPI)
CARD_WIDTH = 1500
CARD_HEIGHT = 2100

# Default fonts (will search for these)
HEBREW_FONT_PREFERENCES = [
    "NotoSansHebrew-Bold.ttf",
    "NotoSansHebrew-Regular.ttf",
    "David-Bold.ttf",
    "David.ttf",
    "FrankRuhlLibre-Bold.ttf",
    "Arial Hebrew Bold.ttf",
    "Arial Hebrew.ttf",
]

ENGLISH_FONT_PREFERENCES = [
    "NotoSans-Bold.ttf",
    "NotoSans-Regular.ttf",
    "Arial Bold.ttf",
    "Arial.ttf",
    "DejaVuSans-Bold.ttf",
    "DejaVuSans.ttf",
]

# System font directories to search
FONT_DIRS = [
    "/System/Library/Fonts",
    "/Library/Fonts",
    "~/Library/Fonts",
    "/usr/share/fonts",
    "/usr/local/share/fonts",
    "fonts/",  # Local fonts directory
]

# Overlay zone colors (for badges/backgrounds)
COLORS = {
    "badge_red": (255, 65, 54),       # Story keyword badge
    "badge_gold": (212, 168, 75),     # Spotlight/Tradition
    "badge_green": (46, 204, 64),     # Power Word
    "badge_blue": (0, 116, 217),      # Connection
    "text_white": (255, 255, 255),
    "text_dark": (51, 51, 51),
    "shadow": (0, 0, 0, 80),          # Semi-transparent shadow
}


# =============================================================================
# FONT HANDLING
# =============================================================================

def find_font(font_names: List[str], size: int = 72) -> Optional[ImageFont.FreeTypeFont]:
    """
    Search for a font from a list of preferences.

    Args:
        font_names: List of font filenames to search for
        size: Font size in points

    Returns:
        ImageFont object or None if not found
    """
    for font_name in font_names:
        # Try direct path first
        if os.path.exists(font_name):
            try:
                return ImageFont.truetype(font_name, size)
            except Exception:
                continue

        # Search in font directories
        for font_dir in FONT_DIRS:
            font_path = Path(os.path.expanduser(font_dir)) / font_name
            if font_path.exists():
                try:
                    return ImageFont.truetype(str(font_path), size)
                except Exception:
                    continue

    # Fall back to default font
    try:
        return ImageFont.load_default()
    except Exception:
        return None


def get_hebrew_font(size: int = 72) -> ImageFont.FreeTypeFont:
    """Get a Hebrew font with the specified size."""
    font = find_font(HEBREW_FONT_PREFERENCES, size)
    if font is None:
        print(f"Warning: No Hebrew font found, using default")
        font = ImageFont.load_default()
    return font


def get_english_font(size: int = 48) -> ImageFont.FreeTypeFont:
    """Get an English font with the specified size."""
    font = find_font(ENGLISH_FONT_PREFERENCES, size)
    if font is None:
        print(f"Warning: No English font found, using default")
        font = ImageFont.load_default()
    return font


# =============================================================================
# TEXT RENDERING HELPERS
# =============================================================================

def get_text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    """Get the size of rendered text."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_text_with_shadow(
    draw: ImageDraw.ImageDraw,
    position: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: Tuple[int, int, int],
    shadow_offset: int = 2,
) -> None:
    """Draw text with a subtle shadow for better visibility."""
    x, y = position
    # Draw shadow
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=COLORS["shadow"])
    # Draw main text
    draw.text(position, text, font=font, fill=fill)


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: Tuple[int, int, int],
    width: int = CARD_WIDTH,
) -> int:
    """
    Draw horizontally centered text.

    Returns the bottom y position of the text.
    """
    text_width, text_height = get_text_size(draw, text, font)
    x = (width - text_width) // 2
    draw_text_with_shadow(draw, (x, y), text, font, fill)
    return y + text_height


def draw_badge(
    draw: ImageDraw.ImageDraw,
    position: Tuple[int, int],
    hebrew_text: str,
    english_text: str,
    hebrew_font: ImageFont.FreeTypeFont,
    english_font: ImageFont.FreeTypeFont,
    bg_color: Tuple[int, int, int],
    padding: int = 20,
) -> None:
    """
    Draw a badge with Hebrew text on top, English below.

    Args:
        position: Top-left corner of the badge
        hebrew_text: Hebrew text (with nikud)
        english_text: English text
        hebrew_font: Font for Hebrew
        english_font: Font for English
        bg_color: Background color for the badge
        padding: Padding inside the badge
    """
    x, y = position

    # Calculate text sizes
    heb_width, heb_height = get_text_size(draw, hebrew_text, hebrew_font)
    eng_width, eng_height = get_text_size(draw, english_text, english_font)

    # Badge dimensions
    badge_width = max(heb_width, eng_width) + padding * 2
    badge_height = heb_height + eng_height + padding * 3

    # Draw rounded rectangle background
    draw.rounded_rectangle(
        [x, y, x + badge_width, y + badge_height],
        radius=15,
        fill=bg_color,
    )

    # Draw Hebrew text (centered in badge)
    heb_x = x + (badge_width - heb_width) // 2
    heb_y = y + padding
    draw.text((heb_x, heb_y), hebrew_text, font=hebrew_font, fill=COLORS["text_white"])

    # Draw English text (centered in badge)
    eng_x = x + (badge_width - eng_width) // 2
    eng_y = heb_y + heb_height + padding // 2
    draw.text((eng_x, eng_y), english_text, font=english_font, fill=COLORS["text_white"])


# =============================================================================
# CARD TYPE SPECIFIC OVERLAYS
# =============================================================================

def overlay_anchor(image: Image.Image, front: Dict) -> Image.Image:
    """
    Overlay text on an Anchor card.

    Front fields:
    - hebrew_title: Parasha name in Hebrew
    """
    draw = ImageDraw.Draw(image)

    hebrew_title = front.get("hebrew_title", "")
    if not hebrew_title:
        return image

    # Large Hebrew title in top zone
    hebrew_font = get_hebrew_font(size=120)

    # Position: centered, about 10% from top
    y_position = int(CARD_HEIGHT * 0.08)
    draw_centered_text(draw, y_position, hebrew_title, hebrew_font, COLORS["text_white"])

    return image


def overlay_spotlight(image: Image.Image, front: Dict) -> Image.Image:
    """
    Overlay text on a Spotlight card.

    Front fields:
    - hebrew_name: Character name in Hebrew
    - english_name: Character name in English
    - emotion_word_en: Emotion word in English
    - emotion_word_he: Emotion word in Hebrew
    """
    draw = ImageDraw.Draw(image)

    hebrew_name = front.get("hebrew_name", "")
    english_name = front.get("english_name", "")
    emotion_en = front.get("emotion_word_en", "")
    emotion_he = front.get("emotion_word_he", "")

    # Fonts
    hebrew_font_large = get_hebrew_font(size=100)
    english_font_medium = get_english_font(size=48)
    emotion_font = get_english_font(size=36)

    # Hebrew name (large, centered, top)
    y = int(CARD_HEIGHT * 0.05)
    if hebrew_name:
        y = draw_centered_text(draw, y, hebrew_name, hebrew_font_large, COLORS["text_white"])
        y += 10

    # English name (medium, centered, below Hebrew)
    if english_name:
        y = draw_centered_text(draw, y, english_name, english_font_medium, COLORS["text_white"])
        y += 20

    # Emotion badge (small, right-aligned)
    if emotion_en or emotion_he:
        emotion_text = emotion_en.upper() if emotion_en else emotion_he
        badge_x = CARD_WIDTH - 200
        badge_y = int(CARD_HEIGHT * 0.05)

        # Draw emotion badge
        text_width, text_height = get_text_size(draw, emotion_text, emotion_font)
        padding = 15
        badge_width = text_width + padding * 2
        badge_height = text_height + padding * 2

        draw.rounded_rectangle(
            [badge_x, badge_y, badge_x + badge_width, badge_y + badge_height],
            radius=10,
            fill=COLORS["badge_gold"],
        )
        draw.text(
            (badge_x + padding, badge_y + padding),
            emotion_text,
            font=emotion_font,
            fill=COLORS["text_white"],
        )

    return image


def overlay_story(image: Image.Image, front: Dict) -> Image.Image:
    """
    Overlay for Story cards.

    Story cards rely on composition guidance (bottom-left kept clear) rather
    than programmatic overlay. The keyword badge is rendered in print layout,
    not overlaid on the image.

    Front fields (stored for print layout, not overlaid):
    - hebrew_keyword: Keyword in Hebrew (with nikud)
    - english_keyword: Keyword in English
    """
    # No overlay - composition handles keeping bottom-left clear
    return image


def get_emoji_font(size: int = 100) -> Optional[ImageFont.FreeTypeFont]:
    """Get an emoji-capable font."""
    emoji_fonts = [
        "/System/Library/Fonts/Apple Color Emoji.ttc",  # macOS
        "/System/Library/Fonts/AppleColorEmoji.ttf",    # macOS alternate
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",  # Linux
        "C:\\Windows\\Fonts\\seguiemj.ttf",  # Windows
    ]
    for font_path in emoji_fonts:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue
    # Fallback to regular font
    return get_english_font(size)


def overlay_connection(image: Image.Image, front: Dict) -> Image.Image:
    """
    Overlay title and emojis on a Connection card.

    Front fields:
    - hebrew_title: Title in Hebrew (with nikud)
    - english_title: Title in English
    - emojis: List of 4 emoji characters (optional)
    """
    draw = ImageDraw.Draw(image)

    hebrew_title = front.get("hebrew_title", "")
    english_title = front.get("english_title", "")
    emojis = front.get("emojis", [])

    # === Title at top (same style as story keyword badge) ===
    if hebrew_title or english_title:
        hebrew_font = get_hebrew_font(size=80)
        english_font = get_english_font(size=44)

        y = int(CARD_HEIGHT * 0.06)
        if hebrew_title:
            y = draw_centered_text(draw, y, hebrew_title, hebrew_font, COLORS["text_white"])
            y += 15

        if english_title:
            draw_centered_text(draw, y, english_title, english_font, COLORS["text_white"])

    # === Emojis at bottom ===
    if emojis:
        emoji_font = get_emoji_font(size=120)
        y = int(CARD_HEIGHT * 0.82)
        spacing = CARD_WIDTH // (len(emojis) + 1)

        for i, emoji in enumerate(emojis[:4]):
            x = spacing * (i + 1)
            text_width, _ = get_text_size(draw, emoji, emoji_font)
            try:
                draw.text((x - text_width // 2, y), emoji, font=emoji_font, embedded_color=True)
            except TypeError:
                draw.text((x - text_width // 2, y), emoji, font=emoji_font, fill=COLORS["text_dark"])

    return image


def overlay_power_word(image: Image.Image, front: Dict) -> Image.Image:
    """
    Overlay text on a Power Word card.

    Front fields:
    - hebrew_word: Hebrew word (with nikud)
    - english_meaning: English meaning
    """
    draw = ImageDraw.Draw(image)

    hebrew_word = front.get("hebrew_word", "")
    english_meaning = front.get("english_meaning", "")

    # Fonts
    hebrew_font_large = get_hebrew_font(size=140)
    english_font_medium = get_english_font(size=56)

    # Hebrew word (very large, centered, top)
    y = int(CARD_HEIGHT * 0.06)
    if hebrew_word:
        y = draw_centered_text(draw, y, hebrew_word, hebrew_font_large, COLORS["text_white"])
        y += 20

    # English meaning (medium, centered, below Hebrew)
    if english_meaning:
        draw_centered_text(draw, y, english_meaning, english_font_medium, COLORS["text_white"])

    return image


def overlay_tradition(image: Image.Image, front: Dict) -> Image.Image:
    """
    Overlay text on a Tradition card.

    Front fields:
    - hebrew_title: Tradition name in Hebrew
    - english_title: Tradition name in English
    """
    draw = ImageDraw.Draw(image)

    hebrew_title = front.get("hebrew_title", "")
    english_title = front.get("english_title", "")

    # Fonts
    hebrew_font = get_hebrew_font(size=80)
    english_font = get_english_font(size=44)

    # Hebrew title (large, centered, top)
    y = int(CARD_HEIGHT * 0.06)
    if hebrew_title:
        y = draw_centered_text(draw, y, hebrew_title, hebrew_font, COLORS["text_white"])
        y += 15

    # English title (medium, centered, below Hebrew)
    if english_title:
        draw_centered_text(draw, y, english_title, english_font, COLORS["text_white"])

    return image


# =============================================================================
# MAIN OVERLAY FUNCTION
# =============================================================================

OVERLAY_FUNCTIONS = {
    "anchor": overlay_anchor,
    "spotlight": overlay_spotlight,
    "story": overlay_story,
    "connection": overlay_connection,
    "power_word": overlay_power_word,
    "tradition": overlay_tradition,
}


def overlay_card_front(
    image_path: str,
    card_type: str,
    front_data: Dict,
    output_path: str = None,
) -> bool:
    """
    Overlay front text on a generated card image.

    Args:
        image_path: Path to the generated image
        card_type: Type of card (anchor, story, etc.)
        front_data: The card's "front" dict from JSON
        output_path: Where to save overlaid image (defaults to overwriting input)

    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        return False

    overlay_fn = OVERLAY_FUNCTIONS.get(card_type)
    if not overlay_fn:
        print(f"Warning: No overlay function for card type: {card_type}")
        return False

    try:
        # Load image
        image = Image.open(image_path).convert("RGBA")

        # Apply overlay
        image = overlay_fn(image, front_data)

        # Save result
        output = output_path or image_path
        image.save(output)
        return True

    except Exception as e:
        print(f"Error overlaying {image_path}: {e}")
        return False


def process_deck(deck_path: str, card_id: str = None, output_suffix: str = "") -> None:
    """
    Process all cards in a deck, applying overlays.

    Args:
        deck_path: Path to deck.json
        card_id: Optional specific card to process
        output_suffix: Optional suffix for output files (e.g., "_overlaid")
    """
    deck_path = Path(deck_path)
    if not deck_path.exists():
        print(f"Error: Deck file not found: {deck_path}")
        return

    with open(deck_path, "r", encoding="utf-8") as f:
        deck = json.load(f)

    images_dir = deck_path.parent / "images"

    print(f"Processing deck: {deck.get('parasha_en', deck.get('holiday_en', 'Unknown'))}")
    print(f"Images directory: {images_dir}")
    print("-" * 50)

    success_count = 0
    skip_count = 0
    fail_count = 0

    for card in deck.get("cards", []):
        current_card_id = card.get("card_id", "")

        # Filter by specific card if requested
        if card_id and current_card_id != card_id:
            continue

        # Check for front data (v2 format)
        front = card.get("front")
        if not front:
            print(f"[SKIP] {current_card_id} - no front data (v1 format)")
            skip_count += 1
            continue

        card_type = card.get("card_type", "")
        image_path = images_dir / f"{current_card_id}.png"

        if not image_path.exists():
            print(f"[SKIP] {current_card_id} - image not found")
            skip_count += 1
            continue

        # Determine output path
        if output_suffix:
            output_path = images_dir / f"{current_card_id}{output_suffix}.png"
        else:
            output_path = image_path

        print(f"[OVERLAY] {current_card_id}: {card_type}")

        if overlay_card_front(str(image_path), card_type, front, str(output_path)):
            print(f"  -> Saved: {output_path.name}")
            success_count += 1
        else:
            fail_count += 1

    print("-" * 50)
    print(f"Complete! Success: {success_count}, Skipped: {skip_count}, Failed: {fail_count}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Overlay text on Parasha Pack card images")
    parser.add_argument("deck_path", help="Path to deck.json file")
    parser.add_argument("--card", help="Process specific card ID only")
    parser.add_argument("--suffix", default="", help="Output filename suffix (e.g., '_overlaid')")
    parser.add_argument("--list-fonts", action="store_true", help="List available fonts")

    args = parser.parse_args()

    if args.list_fonts:
        print("Searching for fonts...")
        print("\nHebrew fonts:")
        for font_name in HEBREW_FONT_PREFERENCES:
            font = find_font([font_name], 12)
            status = "✓ Found" if font else "✗ Not found"
            print(f"  {font_name}: {status}")

        print("\nEnglish fonts:")
        for font_name in ENGLISH_FONT_PREFERENCES:
            font = find_font([font_name], 12)
            status = "✓ Found" if font else "✗ Not found"
            print(f"  {font_name}: {status}")
        return

    process_deck(args.deck_path, args.card, args.suffix)


if __name__ == "__main__":
    main()
