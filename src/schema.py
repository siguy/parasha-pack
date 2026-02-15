"""
Data schema definitions for Parasha Pack card decks.

Front/back separation for teacher-friendly cards:
- Card fronts: Scene-only AI images with React text overlay
- Card backs: 5x7 printable teacher content rendered by Card Designer
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, List, Dict, Any
import json


class CardType(Enum):
    """Types of cards in a deck."""
    ANCHOR = "anchor"
    SPOTLIGHT = "spotlight"
    STORY = "story"          # Renamed from ACTION
    CONNECTION = "connection" # Renamed from THINKER
    POWER_WORD = "power_word"
    TRADITION = "tradition"   # Holiday-specific


class EmotionCategory(Enum):
    """Categories of emotions for emotional literacy."""
    POSITIVE = "positive"
    CHALLENGING = "challenging"
    COMPLEX = "complex"


# Core emotions by category
EMOTIONS = {
    EmotionCategory.POSITIVE: [
        "happy", "proud", "excited", "loved", "safe", "grateful"
    ],
    EmotionCategory.CHALLENGING: [
        "scared", "worried", "sad", "angry", "confused", "lonely"
    ],
    EmotionCategory.COMPLEX: [
        "nervous-but-excited", "sad-but-hopeful"
    ],
}

# Feeling faces for Connection cards
FEELING_FACES = [
    {"emoji": "😊", "label_en": "Happy", "label_he": "שָׂמֵחַ"},
    {"emoji": "😢", "label_en": "Sad", "label_he": "עָצוּב"},
    {"emoji": "😨", "label_en": "Scared", "label_he": "מְפֻחָד"},
    {"emoji": "😮", "label_en": "Surprised", "label_he": "מֻפְתָּע"},
    {"emoji": "🥹", "label_en": "Proud", "label_he": "גֵּאֶה"},
    {"emoji": "😕", "label_en": "Confused", "label_he": "מְבֻלְבָּל"},
]


# =============================================================================
# FRONT/BACK CARD STRUCTURE
# =============================================================================

@dataclass
class AnchorFront:
    """Front overlay content for Anchor cards."""
    hebrew_title: str  # Parasha/holiday name in Hebrew


@dataclass
class AnchorBack:
    """Back content for Anchor cards (teacher reads)."""
    title_en: str
    title_he: str
    emotional_hook_en: str
    emotional_hook_he: str
    symbol_description: str
    teacher_script: str
    border_color: str = "#5c2d91"


@dataclass
class SpotlightFront:
    """Front overlay content for Spotlight cards."""
    hebrew_name: str
    english_name: str
    emotion_word_en: str
    emotion_word_he: str


@dataclass
class SpotlightBack:
    """Back content for Spotlight cards (teacher reads)."""
    character_name_en: str
    character_name_he: str
    emotion_label_en: str
    emotion_label_he: str
    character_description_en: str
    character_description_he: str
    teacher_script: str
    # Optional for villain characters
    portrayal: str = ""  # "misguided" for villains
    teaching_moment_en: str = ""
    teaching_moment_he: str = ""


@dataclass
class StoryFront:
    """Front overlay content for Story cards."""
    hebrew_keyword: str      # With nikud
    english_keyword: str


@dataclass
class StoryBack:
    """Back content for Story cards (teacher reads)."""
    title_en: str
    title_he: str
    sequence_number: int
    description_en: str
    description_he: str
    roleplay_prompt: str
    teacher_script: str
    # Original fields for prompt generation
    hebrew_key_word: str = ""       # Without nikud
    hebrew_key_word_nikud: str = "" # With nikud
    english_key_word: str = ""


@dataclass
class ConnectionFront:
    """Front overlay content for Connection cards."""
    emojis: List[str]  # List of 4 emoji characters


@dataclass
class ConnectionBack:
    """Back content for Connection cards (teacher reads)."""
    title_en: str
    title_he: str
    questions: List[Dict[str, str]]  # List of {question_type, question_en, question_he}
    feeling_faces: List[Dict[str, str]]  # Full emoji data with labels
    torah_talk_instruction: str
    teacher_script: str


@dataclass
class PowerWordFront:
    """Front overlay content for Power Word cards."""
    hebrew_word: str      # With nikud
    english_meaning: str


@dataclass
class PowerWordBack:
    """Back content for Power Word cards (teacher reads)."""
    title_en: str
    title_he: str
    hebrew_word: str           # Without nikud
    hebrew_word_nikud: str     # With nikud
    english_meaning: str
    example_sentence_en: str
    example_sentence_he: str
    kid_friendly_explanation_en: str
    kid_friendly_explanation_he: str
    teacher_script: str
    # Optional fields
    torah_quote_en: str = ""
    torah_quote_he: str = ""
    is_emotion_word: bool = False


@dataclass
class TraditionFront:
    """Front overlay content for Tradition cards."""
    hebrew_title: str
    english_title: str


@dataclass
class TraditionBack:
    """Back content for Tradition cards (teacher reads)."""
    title_en: str
    title_he: str
    story_connection_en: str
    story_connection_he: str
    practice_description_en: str
    practice_description_he: str
    child_action_en: str
    child_action_he: str
    hebrew_term: str
    hebrew_term_meaning: str
    teacher_script: str
    border_color: str = "#D4A84B"


# =============================================================================
# CARD STRUCTURE (front/back separation)
# =============================================================================

@dataclass
class CardV2:
    """
    Card structure with front/back separation.

    - front: Minimal text for React overlay (Card Designer)
    - back: Full content for teacher's printable card back
    - image_prompt: Scene description only (no text to render)
    """
    card_id: str
    card_type: str
    front: Dict[str, Any]
    back: Dict[str, Any]
    image_prompt: str
    image_path: Optional[str] = None
    session: int = 1
    optional: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_legacy(cls, legacy_card: dict) -> "CardV2":
        """
        Convert a legacy card format to CardV2 format.

        Extracts front fields and moves remaining to back.
        """
        card_type = legacy_card.get("card_type", "")

        # Extract front based on card type
        front = extract_front_fields(legacy_card, card_type)

        # Everything else goes to back
        back = extract_back_fields(legacy_card, card_type)

        return cls(
            card_id=legacy_card.get("card_id", ""),
            card_type=card_type,
            front=front,
            back=back,
            image_prompt=legacy_card.get("image_prompt", ""),
            image_path=legacy_card.get("image_path"),
            session=legacy_card.get("session", 1),
            optional=legacy_card.get("optional", False),
        )


def extract_front_fields(card: dict, card_type: str) -> dict:
    """Extract front overlay fields from a card."""
    if card_type == "anchor":
        return {
            "hebrew_title": card.get("title_he", ""),
        }
    elif card_type == "spotlight":
        return {
            "hebrew_name": card.get("character_name_he", ""),
            "english_name": card.get("character_name_en", ""),
            "emotion_word_en": card.get("emotion_label_en", card.get("emotion_label", "")),
            "emotion_word_he": card.get("emotion_label_he", ""),
        }
    elif card_type == "story":
        return {
            "hebrew_keyword": card.get("hebrew_key_word_nikud", card.get("hebrew_key_word", "")),
            "english_keyword": card.get("english_key_word", ""),
        }
    elif card_type == "connection":
        feeling_faces = card.get("feeling_faces", [])
        emojis = [f.get("emoji", "") for f in feeling_faces[:4]]
        return {
            "emojis": emojis,
        }
    elif card_type == "power_word":
        return {
            "hebrew_word": card.get("hebrew_word_nikud", card.get("hebrew_word", "")),
            "english_meaning": card.get("english_meaning", ""),
        }
    elif card_type == "tradition":
        return {
            "hebrew_title": card.get("title_he", ""),
            "english_title": card.get("title_en", ""),
        }
    else:
        return {}


def extract_back_fields(card: dict, card_type: str) -> dict:
    """Extract back content fields from a legacy card."""
    # Common fields that go to back
    back = {
        "teacher_script": card.get("teacher_script", ""),
    }

    if card_type == "anchor":
        back.update({
            "title_en": card.get("title_en", ""),
            "title_he": card.get("title_he", ""),
            "emotional_hook_en": card.get("emotional_hook_en", ""),
            "emotional_hook_he": card.get("emotional_hook_he", ""),
            "symbol_description": card.get("symbol_description", ""),
            "border_color": card.get("border_color", "#5c2d91"),
        })
    elif card_type == "spotlight":
        back.update({
            "character_name_en": card.get("character_name_en", ""),
            "character_name_he": card.get("character_name_he", ""),
            "emotion_label_en": card.get("emotion_label_en", card.get("emotion_label", "")),
            "emotion_label_he": card.get("emotion_label_he", ""),
            "character_description_en": card.get("character_description_en", ""),
            "character_description_he": card.get("character_description_he", ""),
            "portrayal": card.get("portrayal", ""),
            "teaching_moment_en": card.get("teaching_moment_en", ""),
            "teaching_moment_he": card.get("teaching_moment_he", ""),
        })
    elif card_type == "story":
        back.update({
            "title_en": card.get("title_en", ""),
            "title_he": card.get("title_he", ""),
            "sequence_number": card.get("sequence_number", 0),
            "description_en": card.get("description_en", ""),
            "description_he": card.get("description_he", ""),
            "roleplay_prompt": card.get("roleplay_prompt", ""),
            "hebrew_key_word": card.get("hebrew_key_word", ""),
            "hebrew_key_word_nikud": card.get("hebrew_key_word_nikud", ""),
            "english_key_word": card.get("english_key_word", ""),
        })
    elif card_type == "connection":
        back.update({
            "title_en": card.get("title_en", ""),
            "title_he": card.get("title_he", ""),
            "questions": card.get("questions", []),
            "feeling_faces": card.get("feeling_faces", []),
            "torah_talk_instruction": card.get("torah_talk_instruction", "Sit in a circle and share!"),
        })
    elif card_type == "power_word":
        back.update({
            "title_en": card.get("title_en", ""),
            "title_he": card.get("title_he", ""),
            "hebrew_word": card.get("hebrew_word", ""),
            "hebrew_word_nikud": card.get("hebrew_word_nikud", ""),
            "english_meaning": card.get("english_meaning", ""),
            "example_sentence_en": card.get("example_sentence_en", ""),
            "example_sentence_he": card.get("example_sentence_he", ""),
            "kid_friendly_explanation_en": card.get("kid_friendly_explanation_en", ""),
            "kid_friendly_explanation_he": card.get("kid_friendly_explanation_he", ""),
            "torah_quote_en": card.get("torah_quote_en", ""),
            "torah_quote_he": card.get("torah_quote_he", ""),
            "is_emotion_word": card.get("is_emotion_word", False),
        })
    elif card_type == "tradition":
        back.update({
            "title_en": card.get("title_en", ""),
            "title_he": card.get("title_he", ""),
            "story_connection_en": card.get("story_connection_en", ""),
            "story_connection_he": card.get("story_connection_he", ""),
            "practice_description_en": card.get("practice_description_en", ""),
            "practice_description_he": card.get("practice_description_he", ""),
            "child_action_en": card.get("child_action_en", ""),
            "child_action_he": card.get("child_action_he", ""),
            "hebrew_term": card.get("hebrew_term", ""),
            "hebrew_term_meaning": card.get("hebrew_term_meaning", ""),
            "border_color": card.get("border_color", "#D4A84B"),
        })

    return back


@dataclass
class Deck:
    """A complete card deck for a parasha or holiday."""
    parasha_en: str
    parasha_he: str
    ref: str
    border_color: str
    theme: str
    version: str = "2.0"
    cards: list = field(default_factory=list)

    # Deck metadata
    target_age: str = "4-6"
    card_count: int = 0

    def add_card(self, card: CardV2):
        """Add a card to the deck."""
        self.cards.append(card.to_dict())
        self.card_count = len(self.cards)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Deck":
        """Create a Deck from a dictionary."""
        cards = data.pop("cards", [])
        deck = cls(**data)
        deck.cards = cards
        deck.card_count = len(cards)
        return deck

    @classmethod
    def from_json(cls, json_str: str) -> "Deck":
        """Create a Deck from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class FeedbackItem:
    """A feedback item for card review."""
    card_id: str
    category: str  # "visual", "text", "hebrew", "educational", "layout"
    comment: str
    priority: str = "medium"  # "low", "medium", "high"
    resolved: bool = False


@dataclass
class DeckFeedback:
    """Feedback for a complete deck."""
    parasha: str
    deck_version: str
    review_date: str
    cards: list = field(default_factory=list)  # List of card feedback
    global_feedback: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


# Print specifications
PRINT_SPECS = {
    "card_size": {"width": 5, "height": 7, "unit": "inches"},
    "card_size_mm": {"width": 127, "height": 178, "unit": "mm"},
    "orientation": "portrait",
    "bleed": {"size": 0.125, "unit": "inches"},
    "bleed_mm": {"size": 3, "unit": "mm"},
    "safe_zone": {"size": 0.25, "unit": "inches"},
    "resolution_dpi": 300,
    "color_mode": "CMYK",
    "paper_gsm": 350,
    "finish": "matte_lamination",
}

# Layout zones (percentages)
LAYOUT_ZONES = {
    "border": {"width": "full", "style": "thematic_color"},
    "image_area": {"height_percent": 70},
    "text_area": {"height_percent": 20},
    "footer": {"height_percent": 10},
}


# Character design guide — single source of truth for character visuals.
# Imported by image_prompts.py:get_character_style() (reads style_prompt).
# key_features used by config.py helpers and agent definitions.
CHARACTER_DESIGNS = {
    "moses": {
        "name": "Moses",
        "name_he": "מֹשֶׁה",
        "description": "Friendly middle-aged man with warm brown skin and kind, gentle eyes. Short dark beard with some gray showing he's experienced. Wears simple blue and cream robes with a HEAD COVERING (cloth wrap or simple turban). Often holds a wooden shepherd's staff. Has a calm, patient expression.",
        "key_features": [
            "Kind gentle eyes",
            "Short beard with touch of gray",
            "HEAD COVERING (cloth wrap/turban) - ALWAYS INCLUDE",
            "Wooden shepherd's staff",
            "Blue and cream robes",
            "Calm caring expression",
        ],
        "style_prompt": "Moses wearing blue and cream robes with a head covering, holding a wooden staff, with a short gray-touched beard and kind gentle eyes",
    },
    "avraham": {
        "name": "Abraham",
        "name_he": "אַבְרָהָם",
        "description": "Elderly patriarch with white robes and walking stick. Wise, warm expression.",
        "key_features": [
            "White robe",
            "Walking stick",
            "White beard",
        ],
        "style_prompt": "Abraham wearing a white robe, with a walking stick and white beard",
    },
    "sarah": {
        "name": "Sarah",
        "name_he": "שָׂרָה",
        "description": "Matriarch with blue head covering and warm, welcoming smile.",
        "key_features": [
            "Blue head covering",
            "Warm smile",
        ],
        "style_prompt": "Sarah wearing a blue head covering with a warm, welcoming smile",
    },
    "yitro": {
        "name": "Yitro/Jethro",
        "name_he": "יִתְרוֹ",
        "description": "Wise elderly man with long flowing white/gray beard. Warm twinkling eyes that show wisdom and kindness. Wears earth-toned desert robes (browns, tans). Has a gentle grandfatherly smile. May have a walking stick.",
        "key_features": [
            "Long flowing white/gray beard",
            "Twinkling wise eyes",
            "Grandfatherly warm smile",
            "Earth-toned desert robes",
            "Optional walking stick",
        ],
        "style_prompt": "Jethro wearing colorful Midianite-style robes with a gray beard and wise expression",
    },
    "miriam": {
        "name": "Miriam",
        "name_he": "מִרְיָם",
        "description": "Young woman with long dark hair, often holding a tambourine. Joyful, spirited expression.",
        "key_features": [
            "Long dark hair",
            "Tambourine",
        ],
        "style_prompt": "Miriam with long dark hair, holding a tambourine",
    },
    "pharaoh": {
        "name": "Pharaoh",
        "name_he": "פַּרְעֹה",
        "description": "King with gold Egyptian crown and stern expression.",
        "key_features": [
            "Gold crown",
            "Stern expression",
        ],
        "style_prompt": "Pharaoh wearing a gold Egyptian crown with a stern expression",
    },
    "esther": {
        "name": "Esther",
        "name_he": "אֶסְתֵּר",
        "description": "Young Jewish woman with warm olive skin and kind determined eyes. Long dark hair with elegant modest head covering. Royal purple and blue flowing dress, simple gold tiara. Gentle, determined expression.",
        "key_features": [
            "Large kind brown eyes",
            "Long dark hair",
            "Elegant modest head covering",
            "Royal purple and blue dress",
            "Simple gold tiara",
            "Gentle determined expression",
        ],
        "style_prompt": "Esther with long dark hair, elegant head covering, royal purple and blue dress, gold tiara, gentle determined expression",
    },
    "mordechai": {
        "name": "Mordechai",
        "name_he": "מׇרְדְּכַי",
        "description": "Older Jewish man with wise grandfatherly presence. Full gray-brown beard, kind wise eyes, dignified posture. Jewish head covering (kippah or cloth wrap). Modest robes in earth tones (browns, creams, subtle blues).",
        "key_features": [
            "Full gray-brown beard",
            "Kind wise eyes",
            "Dignified posture",
            "Jewish head covering",
            "Earth-toned robes",
            "Grandfatherly warmth",
        ],
        "style_prompt": "Mordechai with full gray-brown beard, Jewish head covering, dignified posture, earth-toned robes",
    },
    "haman": {
        "name": "Haman",
        "name_he": "הָמָן",
        "description": "Adult man with DARK POINTED GOATEE WITH CONNECTED MUSTACHE. DISTINCTIVE THREE-CORNERED HAT (like hamantaschen pastry shape). Pouty frustrated expression, furrowed brow (NOT scary or angry). Persian clothing in MUTED dusty purple and gray-brown. Arms crossed defensively.",
        "key_features": [
            "DARK POINTED GOATEE WITH CONNECTED MUSTACHE",
            "THREE-CORNERED HAT (hamantaschen shape)",
            "Pouty frustrated expression (NOT scary)",
            "Muted dusty purple and gray-brown clothing",
            "Arms crossed, shoulders hunched",
        ],
        "style_prompt": "Haman with three-cornered hat, dark pointed goatee, muted dusty purple and gray-brown robes, pouty frustrated expression",
        "villain": True,
    },
    "achashverosh": {
        "name": "King Achashverosh",
        "name_he": "אֲחַשְׁוֵרוֹשׁ",
        "description": "King with confused bewildered expression - somewhat comedic. Large ornate crown. Royal Persian robes in golds and reds. Bewildered look, eyebrows often raised, distracted expression.",
        "key_features": [
            "Large ornate crown",
            "Confused bewildered expression",
            "Royal Persian robes (golds, reds)",
            "Somewhat cartoonish",
            "NOT scary - just distracted",
        ],
        "style_prompt": "King Achashverosh with large ornate crown, royal Persian robes in golds and reds, confused bewildered expression",
        "misguided": True,
    },
    "israelites": {
        "name": "The Israelites",
        "name_he": "בְּנֵי יִשְׂרָאֵל",
        "description": "A diverse group of friendly-looking people - men, women, and children. Wear simple robes in warm earth tones and soft colors. Faces show a mix of emotions appropriate to the scene. Include families together.",
        "key_features": [
            "Diverse ages (children, adults, elderly)",
            "Simple modest clothing",
            "Warm, relatable expressions",
            "Show as community/group",
        ],
        "style_prompt": "A diverse group of Israelites in simple earth-toned robes, families together, warm expressions",
    },
}

# Legacy alias: old code may reference "moshe" instead of "moses"
CHARACTER_DESIGNS["moshe"] = CHARACTER_DESIGNS["moses"]

# Safety rules for image generation
IMAGE_SAFETY_RULES = [
    "NEVER depict God in human form - use light rays, clouds, or hands from above",
    "No graphic violence or death",
    "No scary monsters",
    "All characters dressed modestly",
    "Friendly, approachable expressions on all characters",
    "Age-appropriate content for 4-6 year olds",
]
