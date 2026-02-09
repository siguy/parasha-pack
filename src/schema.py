"""
Data schema definitions for Parasha Pack card decks.

Version 2.0: Front/Back separation for teacher-friendly cards.
- Card fronts: Minimal text overlay on full-bleed images
- Card backs: 5x7 printable templates with teacher content
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
    # Legacy aliases
    ACTION = "story"
    THINKER = "connection"


class OverlayZone(Enum):
    """Zones where text can be overlaid on card fronts."""
    TOP_20 = "top_20"           # Top 20% of card
    TOP_25 = "top_25"           # Top 25% of card
    TOP_30 = "top_30"           # Top 30% of card
    BOTTOM_20 = "bottom_20"     # Bottom 20% of card
    BOTTOM_LEFT = "bottom_left" # Bottom-left corner badge


# Overlay zone specifications per card type
OVERLAY_SPECS = {
    "anchor": {
        "zone": OverlayZone.TOP_25,
        "content": ["hebrew_title"],
        "composition_hint": "Compose the scene in the lower 75-80%. Keep top 20-25% uncluttered for Hebrew title overlay."
    },
    "spotlight": {
        "zone": OverlayZone.TOP_30,
        "content": ["hebrew_name", "english_name", "emotion_word_en", "emotion_word_he"],
        "composition_hint": "Compose the portrait in the lower 70%. Keep top 30% uncluttered for name and emotion overlay."
    },
    "story": {
        "zone": OverlayZone.BOTTOM_LEFT,
        "content": ["hebrew_keyword", "english_keyword"],
        "composition_hint": "Full-bleed scene. Keep bottom-left corner relatively simple for keyword badge overlay."
    },
    "connection": {
        "zone": OverlayZone.BOTTOM_20,
        "content": ["emojis"],
        "composition_hint": "Compose the illustration in the upper 80%. Keep bottom 20% simple for emoji row overlay."
    },
    "power_word": {
        "zone": OverlayZone.TOP_30,
        "content": ["hebrew_word", "english_meaning"],
        "composition_hint": "Compose the illustration in the lower 70%. Keep top 30% uncluttered for Hebrew word overlay."
    },
    "tradition": {
        "zone": OverlayZone.TOP_25,
        "content": ["hebrew_title", "english_title"],
        "composition_hint": "Compose the scene in the lower 75%. Keep top 25% uncluttered for title overlay."
    },
}


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

# Feeling faces for Thinker cards
FEELING_FACES = [
    {"emoji": "😊", "label_en": "Happy", "label_he": "שָׂמֵחַ"},
    {"emoji": "😢", "label_en": "Sad", "label_he": "עָצוּב"},
    {"emoji": "😨", "label_en": "Scared", "label_he": "מְפֻחָד"},
    {"emoji": "😮", "label_en": "Surprised", "label_he": "מֻפְתָּע"},
    {"emoji": "🥹", "label_en": "Proud", "label_he": "גֵּאֶה"},
    {"emoji": "😕", "label_en": "Confused", "label_he": "מְבֻלְבָּל"},
]


@dataclass
class ThinkerQuestion:
    """A perspective-taking question for Thinker cards."""
    question_type: str  # "emotional_empathy", "cognitive_empathy", "connection"
    question_en: str
    question_he: str


# =============================================================================
# FRONT/BACK CARD STRUCTURE (v2.0)
# =============================================================================

@dataclass
class AnchorFront:
    """Front overlay content for Anchor cards."""
    hebrew_title: str  # Parasha/holiday name in Hebrew
    overlay_zone: str = "top_25"


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
    overlay_zone: str = "top_30"


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
    overlay_zone: str = "bottom_left"


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
    overlay_zone: str = "bottom_20"


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
    overlay_zone: str = "top_30"


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
    overlay_zone: str = "top_25"


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
# CARD V2 STRUCTURE (with front/back separation)
# =============================================================================

@dataclass
class CardV2:
    """
    Version 2 card structure with front/back separation.

    - front: Minimal text for programmatic overlay
    - back: Full content for teacher's printable card back
    - image_prompt: Scene composition only (no text to render)
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
    """Extract front overlay fields from a legacy card."""
    if card_type == "anchor":
        return {
            "overlay_zone": "top_25",
            "hebrew_title": card.get("title_he", ""),
        }
    elif card_type == "spotlight":
        return {
            "overlay_zone": "top_30",
            "hebrew_name": card.get("character_name_he", ""),
            "english_name": card.get("character_name_en", ""),
            "emotion_word_en": card.get("emotion_label_en", card.get("emotion_label", "")),
            "emotion_word_he": card.get("emotion_label_he", ""),
        }
    elif card_type == "story":
        return {
            "overlay_zone": "bottom_left",
            "hebrew_keyword": card.get("hebrew_key_word_nikud", card.get("hebrew_key_word", "")),
            "english_keyword": card.get("english_key_word", ""),
        }
    elif card_type == "connection":
        # Extract just emojis from feeling_faces
        feeling_faces = card.get("feeling_faces", [])
        emojis = [f.get("emoji", "") for f in feeling_faces[:4]]
        return {
            "overlay_zone": "bottom_20",
            "emojis": emojis,
        }
    elif card_type == "power_word":
        return {
            "overlay_zone": "top_30",
            "hebrew_word": card.get("hebrew_word_nikud", card.get("hebrew_word", "")),
            "english_meaning": card.get("english_meaning", ""),
        }
    elif card_type == "tradition":
        return {
            "overlay_zone": "top_25",
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


# =============================================================================
# LEGACY CARD CLASSES (v1.0 - kept for backward compatibility)
# =============================================================================

@dataclass
class BaseCard:
    """Base class for all card types."""
    card_id: str
    card_type: str
    title_en: str
    title_he: str
    image_prompt: str
    image_path: Optional[str] = None
    teacher_script: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class AnchorCard(BaseCard):
    """The Anchor card - introduces parasha and sets emotional tone."""
    emotional_hook_en: str = ""
    emotional_hook_he: str = ""
    symbol_description: str = ""
    border_color: str = "#5c2d91"  # Default royal purple

    def __post_init__(self):
        self.card_type = CardType.ANCHOR.value


@dataclass
class SpotlightCard(BaseCard):
    """Spotlight card - character introduction."""
    character_name_en: str = ""
    character_name_he: str = ""
    emotion_label: str = ""  # e.g., "happy", "proud"
    character_trait: str = ""
    character_description_en: str = ""
    character_description_he: str = ""

    def __post_init__(self):
        self.card_type = CardType.SPOTLIGHT.value


@dataclass
class ActionCard(BaseCard):
    """Action card - plot moments with sequence and roleplay."""
    sequence_number: int = 0
    hebrew_key_word: str = ""
    hebrew_key_word_nikud: str = ""
    english_description: str = ""
    roleplay_prompt: str = ""
    emotional_reactions: list = field(default_factory=list)

    def __post_init__(self):
        self.card_type = CardType.ACTION.value


@dataclass
class ThinkerCard(BaseCard):
    """Thinker card - discussion and emotional connection."""
    questions: list = field(default_factory=list)  # List of ThinkerQuestion dicts
    torah_talk_instruction: str = "Sit in a circle and share!"
    feeling_faces: list = field(default_factory=lambda: FEELING_FACES.copy())

    def __post_init__(self):
        self.card_type = CardType.THINKER.value


@dataclass
class PowerWordCard(BaseCard):
    """Power Word card - Hebrew vocabulary."""
    hebrew_word: str = ""
    hebrew_word_nikud: str = ""
    transliteration: str = ""
    english_meaning: str = ""
    example_sentence_en: str = ""
    example_sentence_he: str = ""
    is_emotion_word: bool = False
    audio_qr_url: Optional[str] = None

    def __post_init__(self):
        self.card_type = CardType.POWER_WORD.value


@dataclass
class Deck:
    """A complete card deck for a parasha."""
    parasha_en: str
    parasha_he: str
    ref: str
    border_color: str
    theme: str
    version: str = "1.0"
    cards: list = field(default_factory=list)

    # Deck metadata
    target_age: str = "4-6"
    card_count: int = 0
    mitzvah_connection: str = ""

    def add_card(self, card: BaseCard):
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


# Character design guide
CHARACTER_DESIGNS = {
    "moshe": {
        "name_en": "Moses",
        "name_he": "מֹשֶׁה",
        "visual_traits": [
            "Brown robe",
            "Wooden staff",
            "Gray beard",
            "Kind eyes",
        ],
        "style_prompt": "Moses wearing a brown robe, holding a wooden staff, with a gray beard and kind expressive eyes",
    },
    "avraham": {
        "name_en": "Abraham",
        "name_he": "אַבְרָהָם",
        "visual_traits": [
            "White robe",
            "Walking stick",
            "White beard",
        ],
        "style_prompt": "Abraham wearing a white robe, with a walking stick and white beard",
    },
    "sarah": {
        "name_en": "Sarah",
        "name_he": "שָׂרָה",
        "visual_traits": [
            "Blue head covering",
            "Warm smile",
        ],
        "style_prompt": "Sarah wearing a blue head covering with a warm, welcoming smile",
    },
    "yitro": {
        "name_en": "Jethro/Yitro",
        "name_he": "יִתְרוֹ",
        "visual_traits": [
            "Colorful robes (Midianite style)",
            "Gray beard",
            "Wise expression",
        ],
        "style_prompt": "Jethro wearing colorful Midianite-style robes with a gray beard and wise expression",
    },
    "miriam": {
        "name_en": "Miriam",
        "name_he": "מִרְיָם",
        "visual_traits": [
            "Long dark hair",
            "Tambourine",
        ],
        "style_prompt": "Miriam with long dark hair, holding a tambourine",
    },
    "pharaoh": {
        "name_en": "Pharaoh",
        "name_he": "פַּרְעֹה",
        "visual_traits": [
            "Gold crown",
            "Stern expression",
        ],
        "style_prompt": "Pharaoh wearing a gold Egyptian crown with a stern expression",
    },
}

# Safety rules for image generation
IMAGE_SAFETY_RULES = [
    "NEVER depict God in human form - use light rays, clouds, or hands from above",
    "No graphic violence or death",
    "No scary monsters",
    "All characters dressed modestly",
    "Friendly, approachable expressions on all characters",
    "Age-appropriate content for 4-6 year olds",
]
