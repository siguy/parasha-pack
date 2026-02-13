#!/usr/bin/env python3
"""
Card back generator for Parasha Pack.

Generates 5x7 printable card backs with teacher content.
Designed for double-sided printing with card fronts.

Usage:
    python card_back_generator.py ../decks/purim/deck.json
    python card_back_generator.py ../decks/purim/deck.json --card story_1
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

# Margins and spacing
MARGIN_X = 80
MARGIN_Y = 80
CONTENT_WIDTH = CARD_WIDTH - (MARGIN_X * 2)

# Colors
COLORS = {
    "background": (255, 252, 245),    # Cream/off-white
    "header_bg": {
        "anchor": (92, 45, 145),       # Royal purple
        "spotlight": (212, 168, 75),   # Gold
        "story": (255, 65, 54),        # Red
        "connection": (0, 116, 217),   # Blue
        "power_word": (46, 204, 64),   # Green
        "tradition": (212, 168, 75),   # Gold/amber
    },
    "text_dark": (51, 51, 51),
    "text_light": (255, 255, 255),
    "text_muted": (102, 102, 102),
    "divider": (200, 200, 200),
    "section_bg": (245, 245, 240),
    "roleplay_bg": (255, 240, 230),
    "teacher_bg": (230, 245, 255),
}

# Font sizes (scaled up for readability)
FONT_SIZES = {
    "header": 64,
    "title_he": 72,
    "title_en": 52,
    "section_header": 44,
    "body": 38,
    "body_he": 42,
    "small": 32,
    "footer": 28,
}


# =============================================================================
# FONT HANDLING (reuse from overlay.py logic)
# =============================================================================

HEBREW_FONT_PREFERENCES = [
    "NotoSansHebrew-Bold.ttf",
    "NotoSansHebrew-Regular.ttf",
    "David-Bold.ttf",
    "Arial Hebrew Bold.ttf",
]

ENGLISH_FONT_PREFERENCES = [
    "NotoSans-Bold.ttf",
    "NotoSans-Regular.ttf",
    "Arial Bold.ttf",
    "DejaVuSans-Bold.ttf",
]

FONT_DIRS = [
    "/System/Library/Fonts",
    "/Library/Fonts",
    "~/Library/Fonts",
    "/usr/share/fonts",
    "/usr/local/share/fonts",
    "fonts/",
]


def find_font(font_names: List[str], size: int = 72) -> Optional[ImageFont.FreeTypeFont]:
    """Search for a font from a list of preferences."""
    for font_name in font_names:
        if os.path.exists(font_name):
            try:
                return ImageFont.truetype(font_name, size)
            except Exception:
                continue

        for font_dir in FONT_DIRS:
            font_path = Path(os.path.expanduser(font_dir)) / font_name
            if font_path.exists():
                try:
                    return ImageFont.truetype(str(font_path), size)
                except Exception:
                    continue

    try:
        return ImageFont.load_default()
    except Exception:
        return None


def get_font(font_type: str, size: int) -> ImageFont.FreeTypeFont:
    """Get a font with the specified type and size."""
    if font_type == "hebrew":
        font = find_font(HEBREW_FONT_PREFERENCES, size)
    else:
        font = find_font(ENGLISH_FONT_PREFERENCES, size)

    if font is None:
        font = ImageFont.load_default()
    return font


# =============================================================================
# TEXT RENDERING HELPERS
# =============================================================================

def get_text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    """Get the size of rendered text."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        width, _ = get_text_size(draw, test_line, font)

        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    position: Tuple[int, int],
    font: ImageFont.FreeTypeFont,
    max_width: int,
    fill: Tuple[int, int, int],
    line_spacing: int = 8,
) -> int:
    """
    Draw wrapped text and return the bottom y position.

    Args:
        draw: ImageDraw object
        text: Text to draw
        position: Starting (x, y) position
        font: Font to use
        max_width: Maximum width for text
        fill: Text color
        line_spacing: Extra spacing between lines

    Returns:
        Bottom y position after drawing
    """
    x, y = position
    lines = wrap_text(text, font, max_width, draw)

    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        _, line_height = get_text_size(draw, line, font)
        y += line_height + line_spacing

    return y


def draw_divider(draw: ImageDraw.ImageDraw, y: int, margin: int = MARGIN_X) -> int:
    """Draw a horizontal divider line."""
    draw.line([(margin, y), (CARD_WIDTH - margin, y)], fill=COLORS["divider"], width=2)
    return y + 20


# =============================================================================
# CARD BACK GENERATORS BY TYPE
# =============================================================================

def generate_anchor_back(image: Image.Image, back: Dict, deck_meta: Dict) -> Image.Image:
    """Generate card back for Anchor card."""
    draw = ImageDraw.Draw(image)
    y = MARGIN_Y

    # Header bar
    header_height = 100
    draw.rectangle([0, 0, CARD_WIDTH, header_height], fill=COLORS["header_bg"]["anchor"])

    badge_font = get_font("english", FONT_SIZES["header"])
    draw.text((MARGIN_X, 20), "ANCHOR", font=badge_font, fill=COLORS["text_light"])

    # Deck name (right side)
    deck_name = deck_meta.get("holiday_en", deck_meta.get("parasha_en", ""))
    if deck_name:
        name_width, _ = get_text_size(draw, deck_name, badge_font)
        draw.text((CARD_WIDTH - MARGIN_X - name_width, 20), deck_name, font=badge_font, fill=COLORS["text_light"])

    y = header_height + 40

    # Title section - Hebrew large
    title_he = back.get("title_he", "")
    title_en = back.get("title_en", "")

    if title_he:
        hebrew_font = get_font("hebrew", FONT_SIZES["title_he"])
        draw.text((MARGIN_X, y), title_he, font=hebrew_font, fill=COLORS["text_dark"])
        _, h = get_text_size(draw, title_he, hebrew_font)
        y += h + 15

    if title_en:
        english_font = get_font("english", FONT_SIZES["title_en"])
        draw.text((MARGIN_X, y), title_en, font=english_font, fill=COLORS["text_muted"])
        _, h = get_text_size(draw, title_en, english_font)
        y += h + 25

    y = draw_divider(draw, y)

    section_font = get_font("english", FONT_SIZES["section_header"])
    section_font_he = get_font("hebrew", FONT_SIZES["section_header"])
    body_font = get_font("english", FONT_SIZES["body"])
    body_font_he = get_font("hebrew", FONT_SIZES["body_he"])

    # Emotional Hook - Hebrew first
    emotional_hook_he = back.get("emotional_hook_he", "")
    if emotional_hook_he:
        draw.text((MARGIN_X, y), "פתיחה רגשית", font=section_font_he, fill=COLORS["text_muted"])
        y += 55
        y = draw_wrapped_text(draw, emotional_hook_he, (MARGIN_X, y), body_font_he, CONTENT_WIDTH, COLORS["text_dark"])
        y += 30

    y = draw_divider(draw, y)

    # Teacher Script
    remaining_height = CARD_HEIGHT - y - MARGIN_Y - 50
    draw.rectangle([MARGIN_X - 10, y, CARD_WIDTH - MARGIN_X + 10, y + remaining_height], fill=COLORS["teacher_bg"])
    y += 20

    draw.text((MARGIN_X, y), "Teacher Script", font=section_font, fill=COLORS["text_muted"])
    y += 55

    teacher_script = back.get("teacher_script", "")
    if teacher_script:
        y = draw_wrapped_text(draw, teacher_script, (MARGIN_X, y), body_font, CONTENT_WIDTH, COLORS["text_dark"])

    return image


def generate_spotlight_back(image: Image.Image, back: Dict, deck_meta: Dict) -> Image.Image:
    """Generate card back for Spotlight card."""
    draw = ImageDraw.Draw(image)
    y = MARGIN_Y

    # Header bar
    header_height = 100
    draw.rectangle([0, 0, CARD_WIDTH, header_height], fill=COLORS["header_bg"]["spotlight"])

    badge_font = get_font("english", FONT_SIZES["header"])
    draw.text((MARGIN_X, 20), "SPOTLIGHT", font=badge_font, fill=COLORS["text_light"])

    # Emotion badge on right
    emotion_he = back.get("emotion_label_he", "")
    if emotion_he:
        emotion_font = get_font("hebrew", FONT_SIZES["title_en"])
        ew, _ = get_text_size(draw, emotion_he, emotion_font)
        draw.text((CARD_WIDTH - MARGIN_X - ew, 25), emotion_he, font=emotion_font, fill=COLORS["text_light"])

    y = header_height + 40

    # Character name - Hebrew large
    char_he = back.get("character_name_he", "")
    char_en = back.get("character_name_en", "")

    if char_he:
        hebrew_font = get_font("hebrew", FONT_SIZES["title_he"])
        draw.text((MARGIN_X, y), char_he, font=hebrew_font, fill=COLORS["text_dark"])
        _, h = get_text_size(draw, char_he, hebrew_font)
        y += h + 15

    if char_en:
        english_font = get_font("english", FONT_SIZES["title_en"])
        draw.text((MARGIN_X, y), char_en, font=english_font, fill=COLORS["text_muted"])
        _, h = get_text_size(draw, char_en, english_font)
        y += h + 25

    y = draw_divider(draw, y)

    section_font = get_font("english", FONT_SIZES["section_header"])
    section_font_he = get_font("hebrew", FONT_SIZES["section_header"])
    body_font = get_font("english", FONT_SIZES["body"])
    body_font_he = get_font("hebrew", FONT_SIZES["body_he"])

    # Character Description - Hebrew
    description_he = back.get("character_description_he", "")
    if description_he:
        draw.text((MARGIN_X, y), "תיאור הדמות", font=section_font_he, fill=COLORS["text_muted"])
        y += 55
        y = draw_wrapped_text(draw, description_he, (MARGIN_X, y), body_font_he, CONTENT_WIDTH, COLORS["text_dark"])
        y += 25

    # Teaching Moment (for villains) - if present
    teaching_moment = back.get("teaching_moment_en", "")
    if teaching_moment:
        y = draw_divider(draw, y)
        draw.rectangle([MARGIN_X - 10, y, CARD_WIDTH - MARGIN_X + 10, y + 140], fill=COLORS["roleplay_bg"])
        y += 20
        draw.text((MARGIN_X, y), "לקח", font=section_font_he, fill=COLORS["text_muted"])
        y += 55
        y = draw_wrapped_text(draw, teaching_moment, (MARGIN_X, y), body_font, CONTENT_WIDTH, COLORS["text_dark"])
        y += 25

    y = draw_divider(draw, y)

    # Teacher Script
    remaining_height = CARD_HEIGHT - y - MARGIN_Y - 50
    draw.rectangle([MARGIN_X - 10, y, CARD_WIDTH - MARGIN_X + 10, y + remaining_height], fill=COLORS["teacher_bg"])
    y += 20

    draw.text((MARGIN_X, y), "Teacher Script", font=section_font, fill=COLORS["text_muted"])
    y += 55

    teacher_script = back.get("teacher_script", "")
    if teacher_script:
        y = draw_wrapped_text(draw, teacher_script, (MARGIN_X, y), body_font, CONTENT_WIDTH, COLORS["text_dark"])

    return image


def generate_story_back(image: Image.Image, back: Dict, deck_meta: Dict) -> Image.Image:
    """Generate card back for Story card."""
    draw = ImageDraw.Draw(image)
    y = MARGIN_Y

    # Header bar
    header_height = 100
    draw.rectangle([0, 0, CARD_WIDTH, header_height], fill=COLORS["header_bg"]["story"])

    badge_font = get_font("english", FONT_SIZES["header"])
    seq_num = back.get("sequence_number", "")
    header_text = f"STORY #{seq_num}" if seq_num else "STORY"
    draw.text((MARGIN_X, 20), header_text, font=badge_font, fill=COLORS["text_light"])

    y = header_height + 40

    # Title - Hebrew first, larger
    title_he = back.get("title_he", "")
    title_en = back.get("title_en", "")

    if title_he:
        hebrew_font = get_font("hebrew", FONT_SIZES["title_he"])
        draw.text((MARGIN_X, y), title_he, font=hebrew_font, fill=COLORS["text_dark"])
        _, h = get_text_size(draw, title_he, hebrew_font)
        y += h + 15

    if title_en:
        english_font = get_font("english", FONT_SIZES["title_en"])
        draw.text((MARGIN_X, y), title_en, font=english_font, fill=COLORS["text_muted"])
        _, h = get_text_size(draw, title_en, english_font)
        y += h + 25

    y = draw_divider(draw, y)

    section_font = get_font("english", FONT_SIZES["section_header"])
    body_font = get_font("english", FONT_SIZES["body"])
    body_font_he = get_font("hebrew", FONT_SIZES["body_he"])

    # Story Description - Hebrew
    description_he = back.get("description_he", "")
    if description_he:
        draw.text((MARGIN_X, y), "הסיפור", font=get_font("hebrew", FONT_SIZES["section_header"]), fill=COLORS["text_muted"])
        y += 55
        y = draw_wrapped_text(draw, description_he, (MARGIN_X, y), body_font_he, CONTENT_WIDTH, COLORS["text_dark"])
        y += 25

    # Roleplay Prompt (highlighted box)
    roleplay = back.get("roleplay_prompt", "")
    if roleplay:
        y = draw_divider(draw, y)
        box_height = 160
        draw.rectangle([MARGIN_X - 10, y, CARD_WIDTH - MARGIN_X + 10, y + box_height], fill=COLORS["roleplay_bg"])
        y += 20

        draw.text((MARGIN_X, y), "★ Act it out!", font=section_font, fill=COLORS["header_bg"]["story"])
        y += 55
        y = draw_wrapped_text(draw, roleplay, (MARGIN_X, y), body_font, CONTENT_WIDTH, COLORS["text_dark"])
        y = max(y, y) + 35

    y = draw_divider(draw, y)

    # Teacher Script
    remaining_height = CARD_HEIGHT - y - MARGIN_Y - 50
    draw.rectangle([MARGIN_X - 10, y, CARD_WIDTH - MARGIN_X + 10, y + remaining_height], fill=COLORS["teacher_bg"])
    y += 20

    draw.text((MARGIN_X, y), "Teacher Script", font=section_font, fill=COLORS["text_muted"])
    y += 55

    teacher_script = back.get("teacher_script", "")
    if teacher_script:
        y = draw_wrapped_text(draw, teacher_script, (MARGIN_X, y), body_font, CONTENT_WIDTH, COLORS["text_dark"])

    return image


def generate_connection_back(image: Image.Image, back: Dict, deck_meta: Dict) -> Image.Image:
    """Generate card back for Connection card."""
    draw = ImageDraw.Draw(image)
    y = MARGIN_Y

    # Header bar
    header_height = 100
    draw.rectangle([0, 0, CARD_WIDTH, header_height], fill=COLORS["header_bg"]["connection"])

    badge_font = get_font("english", FONT_SIZES["header"])
    draw.text((MARGIN_X, 20), "CONNECTION", font=badge_font, fill=COLORS["text_light"])

    y = header_height + 40

    # Title - Hebrew large
    title_he = back.get("title_he", "")
    title_en = back.get("title_en", "")

    if title_he:
        hebrew_font = get_font("hebrew", FONT_SIZES["title_he"])
        draw.text((MARGIN_X, y), title_he, font=hebrew_font, fill=COLORS["text_dark"])
        _, h = get_text_size(draw, title_he, hebrew_font)
        y += h + 15

    if title_en:
        english_font = get_font("english", FONT_SIZES["title_en"])
        draw.text((MARGIN_X, y), title_en, font=english_font, fill=COLORS["text_muted"])
        _, h = get_text_size(draw, title_en, english_font)
        y += h + 25

    y = draw_divider(draw, y)

    section_font = get_font("english", FONT_SIZES["section_header"])
    section_font_he = get_font("hebrew", FONT_SIZES["section_header"])
    body_font = get_font("english", FONT_SIZES["body"])
    body_font_he = get_font("hebrew", FONT_SIZES["body_he"])

    # Questions - Hebrew
    draw.text((MARGIN_X, y), "שאלות לדיון", font=section_font_he, fill=COLORS["text_muted"])
    y += 55

    questions = back.get("questions", [])
    for i, q in enumerate(questions, 1):
        question_he = q.get("question_he", "")
        if question_he:
            y = draw_wrapped_text(draw, f"• {question_he}", (MARGIN_X, y), body_font_he, CONTENT_WIDTH, COLORS["text_dark"])
            y += 20

    y += 15
    y = draw_divider(draw, y)

    # Feeling Faces - with Hebrew labels
    draw.text((MARGIN_X, y), "פרצופי רגשות", font=section_font_he, fill=COLORS["text_muted"])
    y += 50

    feeling_faces = back.get("feeling_faces", [])
    faces_text = "  ".join([f"{f.get('emoji', '')} {f.get('label_he', f.get('label_en', ''))}" for f in feeling_faces])
    if faces_text:
        faces_font = get_font("hebrew", FONT_SIZES["body"])
        draw.text((MARGIN_X, y), faces_text, font=faces_font, fill=COLORS["text_dark"])
        y += 55

    y = draw_divider(draw, y)

    # Teacher Script
    remaining_height = CARD_HEIGHT - y - MARGIN_Y - 50
    draw.rectangle([MARGIN_X - 10, y, CARD_WIDTH - MARGIN_X + 10, y + remaining_height], fill=COLORS["teacher_bg"])
    y += 20

    draw.text((MARGIN_X, y), "Teacher Script", font=section_font, fill=COLORS["text_muted"])
    y += 55

    teacher_script = back.get("teacher_script", "")
    if teacher_script:
        y = draw_wrapped_text(draw, teacher_script, (MARGIN_X, y), body_font, CONTENT_WIDTH, COLORS["text_dark"])

    return image


def generate_power_word_back(image: Image.Image, back: Dict, deck_meta: Dict) -> Image.Image:
    """Generate card back for Power Word card."""
    draw = ImageDraw.Draw(image)
    y = MARGIN_Y

    # Header bar
    header_height = 100
    draw.rectangle([0, 0, CARD_WIDTH, header_height], fill=COLORS["header_bg"]["power_word"])

    badge_font = get_font("english", FONT_SIZES["header"])
    draw.text((MARGIN_X, 20), "POWER WORD", font=badge_font, fill=COLORS["text_light"])

    # Transliteration on right
    transliteration = back.get("transliteration", "")
    if transliteration:
        trans_font = get_font("english", FONT_SIZES["title_en"])
        tw, _ = get_text_size(draw, transliteration, trans_font)
        draw.text((CARD_WIDTH - MARGIN_X - tw, 25), transliteration, font=trans_font, fill=COLORS["text_light"])

    y = header_height + 40

    # Hebrew word (large)
    hebrew_word = back.get("hebrew_word_nikud", back.get("hebrew_word", ""))
    english_meaning = back.get("english_meaning", "")

    if hebrew_word:
        hebrew_font = get_font("hebrew", FONT_SIZES["title_he"] + 20)  # Extra large for power word
        draw.text((MARGIN_X, y), hebrew_word, font=hebrew_font, fill=COLORS["text_dark"])
        _, h = get_text_size(draw, hebrew_word, hebrew_font)
        y += h + 15

    if english_meaning:
        english_font = get_font("english", FONT_SIZES["title_en"])
        draw.text((MARGIN_X, y), english_meaning, font=english_font, fill=COLORS["text_muted"])
        _, h = get_text_size(draw, english_meaning, english_font)
        y += h + 25

    y = draw_divider(draw, y)

    section_font = get_font("english", FONT_SIZES["section_header"])
    section_font_he = get_font("hebrew", FONT_SIZES["section_header"])
    body_font = get_font("english", FONT_SIZES["body"])
    body_font_he = get_font("hebrew", FONT_SIZES["body_he"])

    # Kid-friendly explanation - Hebrew first
    explanation_he = back.get("kid_friendly_explanation_he", "")
    if explanation_he:
        draw.text((MARGIN_X, y), "מה המשמעות", font=section_font_he, fill=COLORS["text_muted"])
        y += 55
        y = draw_wrapped_text(draw, explanation_he, (MARGIN_X, y), body_font_he, CONTENT_WIDTH, COLORS["text_dark"])
        y += 25

    # English explanation
    explanation_en = back.get("kid_friendly_explanation_en", "")
    if explanation_en:
        draw.text((MARGIN_X, y), "What it means", font=section_font, fill=COLORS["text_muted"])
        y += 55
        y = draw_wrapped_text(draw, explanation_en, (MARGIN_X, y), body_font, CONTENT_WIDTH, COLORS["text_dark"])
        y += 25

    y = draw_divider(draw, y)

    # Example sentences
    example_he = back.get("example_sentence_he", "")
    example_en = back.get("example_sentence_en", "")

    if example_he or example_en:
        draw.text((MARGIN_X, y), "דוגמה / Example", font=section_font_he, fill=COLORS["text_muted"])
        y += 55

        if example_he:
            y = draw_wrapped_text(draw, f'"{example_he}"', (MARGIN_X, y), body_font_he, CONTENT_WIDTH, COLORS["text_dark"])
            y += 15
        if example_en:
            y = draw_wrapped_text(draw, f'"{example_en}"', (MARGIN_X, y), body_font, CONTENT_WIDTH, COLORS["text_muted"])
            y += 25

    y = draw_divider(draw, y)

    # Teacher Script
    remaining_height = CARD_HEIGHT - y - MARGIN_Y - 50
    draw.rectangle([MARGIN_X - 10, y, CARD_WIDTH - MARGIN_X + 10, y + remaining_height], fill=COLORS["teacher_bg"])
    y += 20

    draw.text((MARGIN_X, y), "Teacher Script", font=section_font, fill=COLORS["text_muted"])
    y += 55

    teacher_script = back.get("teacher_script", "")
    if teacher_script:
        y = draw_wrapped_text(draw, teacher_script, (MARGIN_X, y), body_font, CONTENT_WIDTH, COLORS["text_dark"])

    return image


def generate_tradition_back(image: Image.Image, back: Dict, deck_meta: Dict) -> Image.Image:
    """Generate card back for Tradition card."""
    draw = ImageDraw.Draw(image)
    y = MARGIN_Y

    # Header bar
    header_height = 100
    draw.rectangle([0, 0, CARD_WIDTH, header_height], fill=COLORS["header_bg"]["tradition"])

    badge_font = get_font("english", FONT_SIZES["header"])
    draw.text((MARGIN_X, 20), "TRADITION", font=badge_font, fill=COLORS["text_light"])

    y = header_height + 40

    # Title - Hebrew large
    title_he = back.get("title_he", "")
    title_en = back.get("title_en", "")

    if title_he:
        hebrew_font = get_font("hebrew", FONT_SIZES["title_he"])
        draw.text((MARGIN_X, y), title_he, font=hebrew_font, fill=COLORS["text_dark"])
        _, h = get_text_size(draw, title_he, hebrew_font)
        y += h + 15

    if title_en:
        english_font = get_font("english", FONT_SIZES["title_en"])
        draw.text((MARGIN_X, y), title_en, font=english_font, fill=COLORS["text_muted"])
        _, h = get_text_size(draw, title_en, english_font)
        y += h + 25

    y = draw_divider(draw, y)

    section_font = get_font("english", FONT_SIZES["section_header"])
    section_font_he = get_font("hebrew", FONT_SIZES["section_header"])
    body_font = get_font("english", FONT_SIZES["body"])
    body_font_he = get_font("hebrew", FONT_SIZES["body_he"])

    # Story Connection - Hebrew first
    story_connection_he = back.get("story_connection_he", "")
    story_connection_en = back.get("story_connection_en", "")

    if story_connection_he:
        draw.text((MARGIN_X, y), "למה אנחנו עושים את זה", font=section_font_he, fill=COLORS["text_muted"])
        y += 55
        y = draw_wrapped_text(draw, story_connection_he, (MARGIN_X, y), body_font_he, CONTENT_WIDTH, COLORS["text_dark"])
        y += 25

    if story_connection_en and not story_connection_he:
        draw.text((MARGIN_X, y), "Why we do this", font=section_font, fill=COLORS["text_muted"])
        y += 55
        y = draw_wrapped_text(draw, story_connection_en, (MARGIN_X, y), body_font, CONTENT_WIDTH, COLORS["text_dark"])
        y += 25

    y = draw_divider(draw, y)

    # Practice Description - Hebrew first
    practice_he = back.get("practice_description_he", "")
    practice_en = back.get("practice_description_en", "")

    if practice_he:
        draw.text((MARGIN_X, y), "מה אנחנו עושים", font=section_font_he, fill=COLORS["text_muted"])
        y += 55
        y = draw_wrapped_text(draw, practice_he, (MARGIN_X, y), body_font_he, CONTENT_WIDTH, COLORS["text_dark"])
        y += 25

    if practice_en and not practice_he:
        draw.text((MARGIN_X, y), "What we do", font=section_font, fill=COLORS["text_muted"])
        y += 55
        y = draw_wrapped_text(draw, practice_en, (MARGIN_X, y), body_font, CONTENT_WIDTH, COLORS["text_dark"])
        y += 25

    # Child Action (highlighted box)
    child_action_he = back.get("child_action_he", "")
    child_action_en = back.get("child_action_en", "")

    if child_action_he or child_action_en:
        y = draw_divider(draw, y)
        box_height = 160
        draw.rectangle([MARGIN_X - 10, y, CARD_WIDTH - MARGIN_X + 10, y + box_height], fill=COLORS["roleplay_bg"])
        y += 20

        draw.text((MARGIN_X, y), "✨ נסו את זה! / Try it!", font=section_font_he, fill=COLORS["header_bg"]["tradition"])
        y += 55

        if child_action_he:
            y = draw_wrapped_text(draw, child_action_he, (MARGIN_X, y), body_font_he, CONTENT_WIDTH, COLORS["text_dark"])
            y += 15
        elif child_action_en:
            y = draw_wrapped_text(draw, child_action_en, (MARGIN_X, y), body_font, CONTENT_WIDTH, COLORS["text_dark"])
        y = max(y, y) + 35

    y = draw_divider(draw, y)

    # Hebrew term (larger)
    hebrew_term = back.get("hebrew_term", "")
    term_meaning = back.get("hebrew_term_meaning", "")
    if hebrew_term:
        term_font_he = get_font("hebrew", FONT_SIZES["body_he"])
        term_text = f"{hebrew_term} • {term_meaning}" if term_meaning else hebrew_term
        draw.text((MARGIN_X, y), term_text, font=term_font_he, fill=COLORS["text_dark"])
        y += 60

    y = draw_divider(draw, y)

    # Teacher Script
    remaining_height = CARD_HEIGHT - y - MARGIN_Y - 50
    draw.rectangle([MARGIN_X - 10, y, CARD_WIDTH - MARGIN_X + 10, y + remaining_height], fill=COLORS["teacher_bg"])
    y += 20

    draw.text((MARGIN_X, y), "Teacher Script", font=section_font, fill=COLORS["text_muted"])
    y += 55

    teacher_script = back.get("teacher_script", "")
    if teacher_script:
        y = draw_wrapped_text(draw, teacher_script, (MARGIN_X, y), body_font, CONTENT_WIDTH, COLORS["text_dark"])

    return image


# =============================================================================
# MAIN GENERATOR
# =============================================================================

BACK_GENERATORS = {
    "anchor": generate_anchor_back,
    "spotlight": generate_spotlight_back,
    "story": generate_story_back,
    "connection": generate_connection_back,
    "power_word": generate_power_word_back,
    "tradition": generate_tradition_back,
}


def generate_card_back(
    card_type: str,
    back_data: Dict,
    deck_meta: Dict,
    output_path: str,
) -> bool:
    """
    Generate a 5x7 printable card back.

    Args:
        card_type: Type of card
        back_data: The card's "back" dict from JSON
        deck_meta: Deck metadata (parasha name, etc.)
        output_path: Where to save the card back image

    Returns:
        True if successful, False otherwise
    """
    generator_fn = BACK_GENERATORS.get(card_type)
    if not generator_fn:
        print(f"Warning: No back generator for card type: {card_type}")
        return False

    try:
        # Create blank card back
        image = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), COLORS["background"])

        # Generate content
        image = generator_fn(image, back_data, deck_meta)

        # Add footer
        draw = ImageDraw.Draw(image)
        footer_font = get_font("english", FONT_SIZES["footer"])
        footer_y = CARD_HEIGHT - MARGIN_Y

        # Deck name
        deck_name = deck_meta.get("parasha_en", deck_meta.get("holiday_en", ""))
        if deck_name:
            draw.text((MARGIN_X, footer_y), deck_name, font=footer_font, fill=COLORS["text_muted"])

        # Card count
        card_id = back_data.get("_card_id", "")
        if card_id:
            id_width, _ = get_text_size(draw, card_id, footer_font)
            draw.text((CARD_WIDTH - MARGIN_X - id_width, footer_y), card_id, font=footer_font, fill=COLORS["text_muted"])

        # Save
        image.save(output_path)
        return True

    except Exception as e:
        print(f"Error generating card back: {e}")
        return False


def process_deck(deck_path: str, card_id: str = None, output_dir: str = None) -> None:
    """
    Generate card backs for all cards in a deck.

    Args:
        deck_path: Path to deck.json
        card_id: Optional specific card to process
        output_dir: Optional output directory (default: backs/ in deck folder)
    """
    deck_path = Path(deck_path)
    if not deck_path.exists():
        print(f"Error: Deck file not found: {deck_path}")
        return

    with open(deck_path, "r", encoding="utf-8") as f:
        deck = json.load(f)

    # Output directory
    if output_dir:
        backs_dir = Path(output_dir)
    else:
        backs_dir = deck_path.parent / "backs"

    backs_dir.mkdir(exist_ok=True)

    # Deck metadata
    deck_meta = {
        "parasha_en": deck.get("parasha_en", ""),
        "parasha_he": deck.get("parasha_he", ""),
        "holiday_en": deck.get("holiday_en", ""),
        "holiday_he": deck.get("holiday_he", ""),
    }

    print(f"Generating card backs for: {deck_meta.get('parasha_en') or deck_meta.get('holiday_en', 'Unknown')}")
    print(f"Output directory: {backs_dir}")
    print("-" * 50)

    success_count = 0
    skip_count = 0
    fail_count = 0

    for card in deck.get("cards", []):
        current_card_id = card.get("card_id", "")

        # Filter by specific card if requested
        if card_id and current_card_id != card_id:
            continue

        # Check for back data (v2 format)
        back = card.get("back")
        if not back:
            print(f"[SKIP] {current_card_id} - no back data (v1 format)")
            skip_count += 1
            continue

        # Add card_id to back for footer
        back["_card_id"] = current_card_id

        card_type = card.get("card_type", "")
        output_path = backs_dir / f"{current_card_id}_back.png"

        print(f"[GEN] {current_card_id}: {card_type}")

        if generate_card_back(card_type, back, deck_meta, str(output_path)):
            print(f"  -> Saved: {output_path.name}")
            success_count += 1
        else:
            fail_count += 1

    print("-" * 50)
    print(f"Complete! Success: {success_count}, Skipped: {skip_count}, Failed: {fail_count}")

    if success_count > 0:
        print(f"\nCard backs saved to: {backs_dir}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate Parasha Pack card backs")
    parser.add_argument("deck_path", help="Path to deck.json file")
    parser.add_argument("--card", help="Generate back for specific card ID only")
    parser.add_argument("--output", help="Output directory (default: backs/ in deck folder)")

    args = parser.parse_args()
    process_deck(args.deck_path, args.card, args.output)


if __name__ == "__main__":
    main()
