"""
Data schema definitions for Parasha Pack card decks.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
import json


class CardType(Enum):
    """Types of cards in a deck."""
    ANCHOR = "anchor"
    SPOTLIGHT = "spotlight"
    ACTION = "action"
    THINKER = "thinker"
    POWER_WORD = "power_word"


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
