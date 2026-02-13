"""
Gemini image generation prompt templates for Parasha Pack.
Ensures consistent visual style across all cards.

AI generates scene-only images. Text and borders are rendered by Card Designer (React).
System constants (style, safety, composition) are layered by build_generation_prompt()
in generate_images.py at generation time.
"""

from typing import Optional, List
from schema import CHARACTER_DESIGNS, IMAGE_SAFETY_RULES


# =============================================================================
# COMPOSITION GUIDANCE (injected at generation time per card type)
# =============================================================================
# These use natural cinematography language so the model understands
# composition through subject placement rather than "leave space for text."

COMPOSITION_GUIDANCE = {
    "anchor": """
=== COMPOSITION ===
Subject (symbol/object) positioned in the center-to-lower portion of the frame.
Generous headroom above — atmospheric space, sky, ceiling glow, or gradient above the subject.
The upper portion of the frame should be visually calm: soft gradient, ambient light, or simple environment.
Think of this as a movie poster where the title would sit at the top — give it that kind of open, cinematic space above.""",

    "spotlight": """
=== COMPOSITION ===
Character portrait framed from chest up, face centered in the middle of the frame.
Generous headroom — palace ceiling, archways, sky, or atmospheric haze visible above the character's head.
The top of the frame should feel open and calm: architectural detail fading into shadow, or sky.
Lower-left corner should be darker or in shadow — ground, dark fabric, or shadow pooling there.
Character looks slightly right of center, creating natural breathing room on the left side.""",

    "story": """
=== COMPOSITION ===
Scene action positioned in the center and right side of the frame.
Generous headroom — ceiling, sky, or atmospheric space above the characters' heads.
The top of the frame should be visually calm: architecture fading up, sky, or warm ambient light.
Lower-left corner should be darker or simpler — ground shadow, dark foreground element, or negative space.
Think of a film still where the action is center-right and the lower-left has a moody shadow.""",

    "connection": """
=== COMPOSITION ===
Characters positioned in the upper two-thirds of the frame.
The bottom of the frame should be simple and calm — a soft floor, rug edge, or gentle gradient.
Think of a photo taken from slightly above, looking down at children sitting, with floor visible at the bottom.
Warm, even lighting throughout. No busy details in the lower 20% of the image.""",

    "tradition": """
=== COMPOSITION ===
Scene grounded in the center-to-lower portion of the frame.
Generous headroom — warm golden glow, ceiling, hanging decorations, or ambient light above.
The top of the frame should glow warmly but be visually simple: golden light, soft bokeh, or warm haze.
Think of a photo shot at a warm holiday gathering where you see the ceiling lights above the scene.""",

    "power_word": """
=== COMPOSITION ===
Character or concept positioned in the center-to-lower portion of the frame.
Generous headroom — bright sky, warm glow, or atmospheric space above.
The top of the frame should be open and luminous: bright light, sky, or soft radiance.
Think of a heroic low-angle shot looking slightly up at the subject, with sky/light above.""",
}

# Shared suffix appended to all prompts at generation time
COMPOSITION_SUFFIX = """
=== CRITICAL RULES ===
DO NOT include any border, frame, or rounded corners in the image.
DO NOT render any text, titles, labels, Hebrew letters, or words anywhere in the image.
The image should be PURELY visual — all text and borders are added separately by software."""


# =============================================================================
# BASE STYLE TEMPLATES
# =============================================================================

# Base style anchors for all images (no text — text rendered by Card Designer)
STYLE_ANCHORS_V2 = """
Style: Vivid, high-contrast cartoon illustration for children ages 4-6.

Visual characteristics:
- Bold primary colors (red, blue, yellow, green) for foreground elements
- Soft pastel colors (pink, light blue, cream, mint) for backgrounds
- Rounded, friendly character designs with large expressive eyes
- Thick, clean black outlines (2-3px equivalent)
- Simple shapes with minimal clutter (5-7 main elements maximum)
- Warm, inviting atmosphere
- Clean, crisp illustration - NO grain, noise, film texture, or visual artifacts
- Smooth color fills with no stippling or dithering

ANATOMY REQUIREMENTS:
- All humans must have exactly 2 arms and 2 legs
- Hands have exactly 5 fingers each
- Correct proportions - no extra limbs or merged body parts

CULTURAL CONTEXT:
- This is for a JEWISH school (preschool/kindergarten ages 4-6)
- When showing children: Jewish children in a Jewish school setting
- Boys wear kippot (head coverings)
- Girls wear modest skirts or dresses (girls do NOT wear kippot)
- Classroom scenes should look like a Jewish preschool/gan
- Do NOT put any Hebrew letters or text on walls, posters, or signs - Hebrew will be wrong

CRITICAL: Do NOT render any text in the image. No Hebrew, no English, no titles,
no labels, no badges. Text will be added programmatically after generation.
The image should be purely visual.
"""

# Safety rules as string
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
