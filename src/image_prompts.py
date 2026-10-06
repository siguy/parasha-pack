"""
Gemini image generation prompt templates for Parasha Pack.
Ensures consistent visual style across all cards.

AI generates scene-only images. Text and borders are rendered by Card Designer (React).
System constants (style, safety, composition) are layered by build_generation_prompt()
in generate_images.py at generation time.
"""

from typing import Optional, List
from schema import CHARACTER_DESIGNS
import style_config

# All style text now lives in style/style_config.yaml (one source shared by the
# prompt builder, the Visual Director and Image QA). These names are kept so
# existing imports keep working.
_cfg = style_config.load()

# Base style anchors for all images (unchanged Purim look)
STYLE_ANCHORS_V2 = _cfg["style_anchors"]

# Modern world (connection + tradition cards). Story world comes from deck.json "story_world".
MODERN_WORLD_STYLE = _cfg["modern_world"]

# Per-card-type composition block, built from the config
COMPOSITION_GUIDANCE = {card_type: style_config.composition_for(card_type)
                        for card_type in _cfg["composition"]}

# Shared suffix appended to all prompts at generation time (no text, no borders)
COMPOSITION_SUFFIX = _cfg["composition_suffix"]

# Safety rules as one prompt-ready string
IMAGE_SAFETY_RULES = style_config.safety_rules()
SAFETY_PROMPT = "\n".join(f"- {rule}" for rule in IMAGE_SAFETY_RULES)


def get_character_style(character_key: str) -> str:
    """Get the style prompt for a specific character."""
    character = CHARACTER_DESIGNS.get(character_key.lower())
    if character:
        return character["style_prompt"]
    return ""


# =============================================================================
# SCENE PROMPT BUILDERS (scene descriptions only)
# =============================================================================
# These produce SCENE-ONLY prompts suitable for deck.json image_prompt fields.
# Style, safety, composition, and critical rules are added automatically
# by generate_images.py's build_generation_prompt() at generation time.
#
# Usage:
#   prompt = build_anchor_prompt_v2(...)    # Scene-only prompt
#   # Store in deck.json as image_prompt
#   # generate_images.py adds all system layers when generating


def build_anchor_prompt_v2(
    parasha_name: str,
    symbol_description: str,
    emotional_tone: str,
) -> str:
    """
    Build a scene-only prompt for an Anchor card.

    Args:
        parasha_name: Name of the parasha (for context, not rendered)
        symbol_description: Description of the central symbol
        emotional_tone: The emotional tone to convey
    """
    return f"""\
Full-bleed illustration for a children's educational card introducing "{parasha_name}".

Central Symbol: {symbol_description}
The symbol should be iconic and memorable — large, simple, immediately recognizable.
Glowing or radiant quality. Background supports but doesn't compete.

Emotional Tone: {emotional_tone}
The image should make children go "Wow!" — iconic, memorable, emotionally resonant."""


def build_spotlight_prompt_v2(
    character_key: str,
    character_description: str,
    emotion: str,
    scene_context: str = "",
) -> str:
    """
    Build a scene-only prompt for a Spotlight (character portrait) card.

    Args:
        character_key: Key from CHARACTER_DESIGNS
        character_description: Full visual description of character
        emotion: The emotion the character should display
        scene_context: Optional context for the background
    """
    character_style = get_character_style(character_key) or character_description
    context_line = f"\nBackground setting: {scene_context}" if scene_context else ""

    additional = ""
    if character_description and character_description != character_style:
        additional = f"\nAdditional context: {character_description}"

    return f"""\
Character portrait illustration for a children's educational card.

Character: {character_style}{additional}

Emotion: {emotion}
Face should clearly show the emotion with large expressive eyes and clear mouth expression.
Body language reinforces the emotion. Expression readable from across a classroom.{context_line}

Warm, inviting. This character should feel like someone children want to know."""


def build_story_prompt_v2(
    scene_description: str,
    characters: List[dict],
    key_elements: List[str],
    sequence_context: str = "",
) -> str:
    """
    Build a scene-only prompt for a Story (action moment) card.

    Args:
        scene_description: Description of the scene/action
        characters: List of dicts with 'key', 'description', and 'emotion'
        key_elements: 2-4 key visual elements in the scene
        sequence_context: Where this fits in the story sequence
    """
    # Build character descriptions
    character_prompts = []
    for char in characters:
        char_key = char.get('key', '')
        char_desc = char.get('description', '') or get_character_style(char_key)
        emotion = char.get('emotion', 'engaged')
        if char_desc:
            character_prompts.append(f"- {char_desc}, looking {emotion}")

    characters_text = "\n".join(character_prompts) if character_prompts else "- Generic characters appropriate to the scene"
    elements_text = "\n".join(f"- {elem}" for elem in key_elements[:4])
    context_line = f"\nStory Context: {sequence_context}" if sequence_context else ""

    return f"""\
Action scene illustration for a children's educational card.

{scene_description}{context_line}

Characters in Scene:
{characters_text}

Key Visual Elements:
{elements_text}

Dynamic, engaging. Capture the key emotional moment of this scene."""


def build_connection_prompt_v2(
    theme: str,
    scene_description: str = "",
) -> str:
    """
    Build a scene-only prompt for a Connection (discussion) card.

    Args:
        theme: The theme being explored
        scene_description: Optional scene description (default: children in discussion)
    """
    default_scene = "2-3 diverse children in thoughtful, wondering poses — one with hand on chin thinking, one looking up curiously, one pondering with finger to lips"
    scene = scene_description if scene_description else default_scene

    return f"""\
Illustration for a children's discussion/thinking card.

Theme: {theme}
Visual: {scene}

Characters in "wondering" poses — hand on chin, looking up, contemplating.
Peaceful, reflective mood. Safe space for sharing feelings.
Soft, warm lighting. Simple background that doesn't distract.

Calm, curious, inviting. Children should feel safe to share their thoughts."""


def build_power_word_prompt_v2(
    english_meaning: str,
    visual_representation: str,
    is_emotion_word: bool = False,
) -> str:
    """
    Build a scene-only prompt for a Power Word vocabulary card.

    Args:
        english_meaning: English translation (for context, not rendered)
        visual_representation: How to visually represent the word
        is_emotion_word: Whether this is an emotion vocabulary word
    """
    emotion_note = ""
    if is_emotion_word:
        emotion_note = "\nSince this represents an emotion word, show a character clearly displaying this emotion. The facial expression and body language should make the emotion unmistakable."

    return f"""\
Illustration for a children's vocabulary card about "{english_meaning}".

Visual Concept: {visual_representation}{emotion_note}

One central element that clearly represents the concept.
Very simple, focused composition. Bright, engaging colors.

Educational but fun! The concept should be immediately clear from the image alone."""


def build_tradition_prompt_v2(
    tradition_name: str,
    practice_description: str,
    scene_description: str = "",
) -> str:
    """
    Build a scene-only prompt for a Tradition card (holiday decks).

    Args:
        tradition_name: Name of the tradition (for context, not rendered)
        practice_description: What the practice looks like
        scene_description: Optional specific scene description
    """
    default_scene = "Family or community joyfully participating in the practice together"
    scene = scene_description if scene_description else default_scene

    return f"""\
Warm, celebratory illustration for a children's tradition card about "{tradition_name}".

Practice: {practice_description}
Visual: {scene}

Show people DOING the practice together — community/family scene.
Include children participating. Warm golden color palette — candlelight, sunset feeling.
Warm ambers, soft golds, cream, warm browns.

NOT instructional or diagram-like — show the joy of the practice.
Warm, celebratory, joyful. The practice should look inviting and fun."""


def build_divine_presence_prompt_v2(
    scene_description: str,
    manifestation_type: str = "light_rays",
) -> str:
    """
    Build a scene-only prompt for scenes involving divine presence.
    Never depicts God in human form — uses abstract representations.

    Args:
        scene_description: The scene context
        manifestation_type: How to show divine presence
    """
    manifestations = {
        "light_rays": "golden light rays streaming down from above, warm and gentle",
        "clouds": "soft, glowing clouds with light emanating from within",
        "hands_from_above": "gentle hands emerging from clouds above, made of light",
        "pillar_of_fire": "a magnificent pillar of warm, non-threatening fire reaching up to the sky",
        "pillar_of_cloud": "a tall, majestic pillar of soft white cloud",
    }

    divine_visual = manifestations.get(manifestation_type, manifestations["light_rays"])

    return f"""\
Illustration showing a scene of divine presence for children.

CRITICAL: Do NOT depict God as a person or human figure.
Use only abstract representations: light, clouds, or symbolic imagery.

{scene_description}

Divine Presence: {divine_visual}
The divine presence should feel warm, loving, and safe (not scary).
Light should be golden/warm, not harsh.
Characters in the scene should look awed but not frightened.

Awe-inspiring, wondrous, sacred but not scary. Children should feel amazed, not afraid."""


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("=== ANCHOR CARD PROMPT ===")
    print(build_anchor_prompt_v2(
        parasha_name="Yitro",
        symbol_description="Two stone tablets with rounded tops, glowing with warm golden light rays streaming from clouds above",
        emotional_tone="awe, wonder, and reverence",
    ))

    print("\n\n=== SPOTLIGHT CARD PROMPT ===")
    print(build_spotlight_prompt_v2(
        character_key="moshe",
        character_description="Moses with kind eyes, head covering, blue and cream robes",
        emotion="devoted and caring",
        scene_context="desert setting with people waiting",
    ))

    print("\n\n=== STORY CARD PROMPT ===")
    print(build_story_prompt_v2(
        scene_description="Moses and Yitro embracing in a joyful reunion",
        characters=[
            {"key": "moshe", "emotion": "overjoyed"},
            {"key": "yitro", "emotion": "loving"},
        ],
        key_elements=[
            "Two men embracing warmly",
            "Desert camp in background",
            "Warm sunset colors",
        ],
        sequence_context="The moment when Yitro arrives to visit Moses",
    ))

    print("\n\n=== CONNECTION CARD PROMPT ===")
    print(build_connection_prompt_v2(
        theme="Being Brave",
        scene_description="Children sitting in a circle, some with hands raised, sharing their feelings",
    ))
