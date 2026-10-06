"""
Parasha Pack Configuration

Central location for all constants used across the codebase.
This is the single source of truth for visual specs, colors, and card settings.

For documentation, see: ../agents/VISUAL_SPECS.md and ../agents/CARD_SPECS.md
"""

# =============================================================================
# PRINT SIZES
# =============================================================================
# Print sizes (letter default, 5x7 vendor) live in card-designer/print_formats.json.
# The Card Designer reads them from there; Python code has no copy of its own.

# =============================================================================
# COLOR PALETTE
# =============================================================================

# Primary colors (main elements)
COLORS = {
    "red": "#FF4136",
    "blue": "#0074D9",
    "yellow": "#FFDC00",
    "green": "#2ECC40",
    "gold": "#D4A84B",
    "amber": "#D4A84B",
    "purple": "#8B5CF6",
}

# Background colors (soft pastels)
BACKGROUND_COLORS = {
    "pink": "#FFE5E5",
    "light_blue": "#E5F0FF",
    "cream": "#FFFBE5",
    "mint": "#E5FFE5",
}

# Theme colors (deck borders)
THEME_COLORS = {
    "creation": "#1E3A5F",
    "desert": "#C9A227",
    "water": "#2D8A8A",
    "family": "#D4A84B",
    "covenant": "#5C2D91",
    "redemption": "#A52A2A",
    "courage": "#8B5CF6",
}

# =============================================================================
# CARD TYPE SETTINGS
# =============================================================================

CARD_TYPE_BORDERS = {
    "anchor": {"color": "#5C2D91", "icon": "star", "name": "Royal Purple"},
    "spotlight": {"color": "#D4A84B", "icon": "person", "name": "Gold"},
    "story": {"color": "#FF4136", "icon": "lightning-bolt", "name": "Red"},
    "action": {"color": "#FF4136", "icon": "lightning-bolt", "name": "Red"},  # Alias
    "connection": {"color": "#0074D9", "icon": "thought-bubble", "name": "Blue"},
    "thinker": {"color": "#0074D9", "icon": "thought-bubble", "name": "Blue"},  # Alias
    "power_word": {"color": "#2ECC40", "icon": "aleph", "name": "Green"},
    "tradition": {"color": "#D4A84B", "icon": "sparkle", "name": "Gold/Amber"},
}

# =============================================================================
# ART STYLE AND SAFETY
# =============================================================================
# The art style for image prompts lives in style/style_config.yaml (read by
# src/image_prompts.py). Only the legacy safety text below is kept here.

SAFETY_RESTRICTIONS = """
=== RESTRICTIONS ===
NEVER depict:
- God in any human or physical form
- God's name in Hebrew (יהוה / yud-hey-vav-hey) - NEVER INCLUDE THIS
- Graphic violence, blood, or injury
- Death shown explicitly (no bodies, graves visible)
- Scary monsters, demons, or frightening creatures
- Weapons striking or causing harm
- Complex scenes with many small details
- Dark, shadowy, or threatening environments
- Realistic styles that might be too intense
- QR codes
- Transliterations (phonetic spellings) on card images

SPECIAL RULE FOR 10 COMMANDMENTS TABLETS:
- NEVER write God's name or actual commandment text
- Always show exactly 5 letters on each tablet
- Use the first 10 letters of the Hebrew alphabet as placeholders:
  Left tablet: א ב ג ד ה
  Right tablet: ו ז ח ט י

If depicting divine presence:
- Warm golden/white light rays from above
- Glowing, soft clouds with radiance
- Environmental effects (gentle wind, soft fire)
- Stylized Hebrew text with gentle glow (but NEVER God's name)
- Hands reaching down from clouds (no body visible)
- A soft, welcoming light source
"""

# =============================================================================
# IMAGE GENERATION
# =============================================================================

# Default image model: Nano Banana 2. Override with GEMINI_IMAGE_MODEL in .env
# (e.g. GEMINI_IMAGE_MODEL=gemini-3-pro-image for Nano Banana Pro).
DEFAULT_IMAGE_MODEL = "gemini-3.1-flash-image"

# Output resolution sent as imageConfig.imageSize. Must be exactly one of these
# (uppercase K). The API rejects lowercase like "2k".
VALID_IMAGE_SIZES = ("512", "1K", "2K", "4K")
DEFAULT_IMAGE_SIZE = "2K"

# Expected pixel dimensions (width, height) for 3:4 images at each size.
# Used only to log a warning if the API returns something unexpected.
# Source: Google's resolution table for Gemini 3.1 Flash Image
# (ai.google.dev/gemini-api/docs/image-generation). Note "1K" is NOT 768x1024 —
# the short side is 896, not a power of two.
#   512 and 4K: documented only (not yet seen in a real call)
#   1K and 2K: documented AND observed in real API calls (Oct 2026)
EXPECTED_DIMENSIONS_3_4 = {
    "512": (448, 600),
    "1K": (896, 1200),
    "2K": (1792, 2400),
    "4K": (3584, 4800),
}

# Price in USD per generated image, by imageSize (Nano Banana 2, standard, Oct 2026).
# Used by the spend ledger (src/spend_ledger.py).
IMAGE_PRICE_USD = {
    "512": 0.045,
    "1K": 0.067,
    "2K": 0.101,
    "4K": 0.151,
}

# Sizes for the draft -> final flow (generate_images.py --draft / --final)
DRAFT_IMAGE_SIZE = "1K"
FINAL_IMAGE_SIZE = "2K"
DEFAULT_DRAFT_VARIANTS = 2

ASPECT_RATIOS = {
    "card": "5:7",
    "identity": "16:9",
    "square": "1:1",
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

# CHARACTER_DESIGNS consolidated into schema.py as single source of truth.
# Import from there for character data.
from schema import CHARACTER_DESIGNS


def get_border_color(card_type: str) -> str:
    """Get the border color hex for a card type."""
    return CARD_TYPE_BORDERS.get(card_type, {}).get("color", "#5C2D91")


def get_character_description(character_key: str) -> str:
    """Get the full character description for prompts."""
    char = CHARACTER_DESIGNS.get(character_key.lower())
    if not char:
        return ""
    return char.get("description", "")


def get_character_features(character_key: str) -> list:
    """Get the key features list for a character."""
    char = CHARACTER_DESIGNS.get(character_key.lower())
    if not char:
        return []
    return char.get("key_features", [])
