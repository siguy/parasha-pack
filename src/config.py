"""
Parasha Pack Configuration

Central location for all constants used across the codebase.
This is the single source of truth for visual specs, colors, and card settings.

For documentation, see: ../agents/VISUAL_SPECS.md and ../agents/CARD_SPECS.md
"""

# =============================================================================
# PRINT SPECIFICATIONS
# =============================================================================

CARD_WIDTH = 1500  # pixels at 300 DPI
CARD_HEIGHT = 2100  # pixels at 300 DPI
CARD_SIZE = (CARD_WIDTH, CARD_HEIGHT)

CARD_WIDTH_INCHES = 5.0
CARD_HEIGHT_INCHES = 7.0

DPI = 300
BLEED_INCHES = 0.125
BLEED_PX = int(BLEED_INCHES * DPI)  # 38px

BORDER_WIDTH = 24  # 8px at 300dpi = 24px
CORNER_RADIUS = 30  # ~10px at 300dpi

OUTER_PADDING = 40
INNER_PADDING = 30

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
# ART STYLE
# =============================================================================

CARD_STYLE = """
=== STYLE ===
Vivid, high-contrast cartoon style suitable for ages 4-6.
Think: Colorful children's book illustration meets educational flashcard.
- Characters: Rounded, friendly shapes. Large expressive eyes (20% of face).
- Forms: Simple shapes, no fine details or complex patterns.
- Lines: Thick, clean black outlines (2-3px equivalent).
- Contrast: High contrast between foreground and background.
- Emotion: Big, clear facial expressions visible from across a classroom.
- Complexity: Maximum 5-7 distinct visual elements per scene.

Card Format: 5x7 inches (1500x2100px)
Corners: rounded (8-10px radius)

Colors:
- Characters and main elements: Bold primary colors (#FF4136, #0074D9, #FFDC00, #2ECC40)
- Backgrounds: Soft pastels (#FFE5E5, #E5F0FF, #FFFBE5, #E5FFE5)
"""

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
# CHARACTER DESIGNS
# =============================================================================

CHARACTER_DESIGNS = {
    "moses": {
        "name": "Moses",
        "name_he": "מֹשֶׁה",
        "description": """Friendly middle-aged man with warm brown skin and kind, gentle eyes. Short dark beard with some gray showing he's experienced. Wears simple blue and cream robes with a HEAD COVERING (cloth wrap or simple turban). Often holds a wooden shepherd's staff. Has a calm, patient expression.""",
        "key_features": [
            "Kind gentle eyes",
            "Short beard with touch of gray",
            "HEAD COVERING (cloth wrap/turban) - ALWAYS INCLUDE",
            "Wooden shepherd's staff",
            "Blue and cream robes",
            "Calm caring expression",
        ],
    },
    "yitro": {
        "name": "Yitro/Jethro",
        "name_he": "יִתְרוֹ",
        "description": """Wise elderly man with long flowing white/gray beard. Warm twinkling eyes that show wisdom and kindness. Wears earth-toned desert robes (browns, tans). Has a gentle grandfatherly smile. May have a walking stick.""",
        "key_features": [
            "Long flowing white/gray beard",
            "Twinkling wise eyes",
            "Grandfatherly warm smile",
            "Earth-toned desert robes",
            "Optional walking stick",
        ],
    },
    "esther": {
        "name": "Esther",
        "name_he": "אֶסְתֵּר",
        "description": """Young Jewish woman with warm olive skin and kind determined eyes. Long dark hair with elegant modest head covering. Royal purple and blue flowing dress, simple gold tiara. Gentle, determined expression.""",
        "key_features": [
            "Large kind brown eyes",
            "Long dark hair",
            "Elegant modest head covering",
            "Royal purple and blue dress",
            "Simple gold tiara",
            "Gentle determined expression",
        ],
    },
    "mordechai": {
        "name": "Mordechai",
        "name_he": "מׇרְדְּכַי",
        "description": """Older Jewish man with wise grandfatherly presence. Full gray-brown beard, kind wise eyes, dignified posture. Jewish head covering (kippah or cloth wrap). Modest robes in earth tones (browns, creams, subtle blues).""",
        "key_features": [
            "Full gray-brown beard",
            "Kind wise eyes",
            "Dignified posture",
            "Jewish head covering",
            "Earth-toned robes",
            "Grandfatherly warmth",
        ],
    },
    "haman": {
        "name": "Haman",
        "name_he": "הָמָן",
        "description": """Adult man with DARK POINTED GOATEE WITH CONNECTED MUSTACHE. DISTINCTIVE THREE-CORNERED HAT (like hamantaschen pastry shape). Pouty frustrated expression, furrowed brow (NOT scary or angry). Persian clothing in MUTED dusty purple and gray-brown. Arms crossed defensively.""",
        "key_features": [
            "DARK POINTED GOATEE WITH CONNECTED MUSTACHE",
            "THREE-CORNERED HAT (hamantaschen shape)",
            "Pouty frustrated expression (NOT scary)",
            "Muted dusty purple and gray-brown clothing",
            "Arms crossed, shoulders hunched",
        ],
        "villain": True,
    },
    "achashverosh": {
        "name": "King Achashverosh",
        "name_he": "אֲחַשְׁוֵרוֹשׁ",
        "description": """King with confused bewildered expression - somewhat comedic. Large ornate crown. Royal Persian robes in golds and reds. Bewildered look, eyebrows often raised, distracted expression.""",
        "key_features": [
            "Large ornate crown",
            "Confused bewildered expression",
            "Royal Persian robes (golds, reds)",
            "Somewhat cartoonish",
            "NOT scary - just distracted",
        ],
        "misguided": True,
    },
    "israelites": {
        "name": "The Israelites",
        "name_he": "בְּנֵי יִשְׂרָאֵל",
        "description": """A diverse group of friendly-looking people - men, women, and children. Wear simple robes in warm earth tones and soft colors. Faces show a mix of emotions appropriate to the scene. Include families together.""",
        "key_features": [
            "Diverse ages (children, adults, elderly)",
            "Simple modest clothing",
            "Warm, relatable expressions",
            "Show as community/group",
        ],
    },
}

# =============================================================================
# IMAGE GENERATION
# =============================================================================

DEFAULT_MODEL = "nano-banana"  # ALWAYS use this - never imagen or flash

ASPECT_RATIOS = {
    "card": "5:7",
    "identity": "16:9",
    "square": "1:1",
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_border_color(card_type: str) -> str:
    """Get the border color hex for a card type."""
    return CARD_TYPE_BORDERS.get(card_type, {}).get("color", "#5C2D91")


def get_character_description(character_key: str) -> str:
    """Get the full character description for prompts."""
    char = CHARACTER_DESIGNS.get(character_key.lower())
    if not char:
        return ""
    return char["description"]


def get_character_features(character_key: str) -> list:
    """Get the key features list for a character."""
    char = CHARACTER_DESIGNS.get(character_key.lower())
    if not char:
        return []
    return char.get("key_features", [])
