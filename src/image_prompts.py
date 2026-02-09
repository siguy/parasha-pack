"""
Gemini image generation prompt templates for Parasha Pack.
Ensures consistent visual style across all cards.

Version 2.0: No text rendered in images - text is overlaid programmatically.
Images focus on scene composition with reserved zones for text overlay.
"""

from typing import Optional, List
from schema import CHARACTER_DESIGNS, IMAGE_SAFETY_RULES, OVERLAY_SPECS


# =============================================================================
# BASE STYLE TEMPLATES
# =============================================================================

# Base style anchors for all images (v2 - explicitly no text)
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

# Legacy style (for backward compatibility)
STYLE_ANCHORS = """
Style: Vivid, high-contrast cartoon illustration for children ages 4-6.
Visual characteristics:
- Bold primary colors (red, blue, yellow, green) for foreground elements
- Soft pastel colors (pink, light blue, cream, mint) for backgrounds
- Rounded, friendly character designs with large expressive eyes
- Thick, clean black outlines
- Simple shapes with minimal clutter (3-4 main elements maximum)
- Warm, inviting atmosphere
- No text in the image
"""

# Safety rules as string
SAFETY_PROMPT = "\n".join(f"- {rule}" for rule in IMAGE_SAFETY_RULES)


def get_character_style(character_key: str) -> str:
    """Get the style prompt for a specific character."""
    character = CHARACTER_DESIGNS.get(character_key.lower())
    if character:
        return character["style_prompt"]
    return ""


def get_overlay_spec(card_type: str) -> dict:
    """Get overlay specification for a card type."""
    return OVERLAY_SPECS.get(card_type, {})


# =============================================================================
# VERSION 2 PROMPT BUILDERS (No text rendering)
# =============================================================================

def build_anchor_prompt_v2(
    parasha_name: str,
    symbol_description: str,
    emotional_tone: str,
) -> str:
    """
    Build a v2 image prompt for an Anchor card.

    No text will be rendered - top 20-25% is reserved for Hebrew title overlay.

    Args:
        parasha_name: Name of the parasha (for context, not rendered)
        symbol_description: Description of the central symbol
        emotional_tone: The emotional tone to convey
    """
    spec = get_overlay_spec("anchor")

    prompt = f"""
Create a full-bleed illustration for a children's educational card.

=== STYLE ===
{STYLE_ANCHORS_V2}

=== SAFETY RULES ===
{SAFETY_PROMPT}

=== SCENE ===
Central Symbol: {symbol_description}
Emotional Tone: {emotional_tone}

=== COMPOSITION ===
{spec.get('composition_hint', '')}

- The top 20-25% should be a simple, uncluttered area (gradient, sky, or soft glow)
  This zone will have Hebrew text overlaid programmatically.
- The central symbol should be positioned in the middle-to-lower portion of the card
- Use the full width - this is a full-bleed image
- Background should support but not compete with the central symbol
- Light rays or glowing effects can extend into the upper zone, but keep it simple

Aspect ratio: 5:7 portrait. Full-bleed illustration extending to all edges.

=== MOOD ===
Iconic, memorable, and emotionally resonant. The image should make children go "Wow!"
"""
    return prompt.strip()


def build_spotlight_prompt_v2(
    character_key: str,
    character_description: str,
    emotion: str,
    scene_context: str = "",
) -> str:
    """
    Build a v2 image prompt for a Spotlight card.

    No text will be rendered - top 30% is reserved for name and emotion overlay.

    Args:
        character_key: Key from CHARACTER_DESIGNS
        character_description: Full visual description of character
        emotion: The emotion the character should display
        scene_context: Optional context for the background
    """
    spec = get_overlay_spec("spotlight")
    character_style = get_character_style(character_key) or character_description

    prompt = f"""
Create a character portrait illustration for a children's educational card.

=== STYLE ===
{STYLE_ANCHORS_V2}

=== SAFETY RULES ===
{SAFETY_PROMPT}

=== CHARACTER ===
{character_style}

{f"Additional context: {character_description}" if character_description and character_description != character_style else ""}

Emotion to Display: {emotion}
- Face should clearly show the emotion (large expressive eyes, clear mouth expression)
- Body language should reinforce the emotion
- Expression should be readable from across a classroom

=== COMPOSITION ===
{spec.get('composition_hint', '')}

- The top 30% should be a simple, uncluttered area (gradient or soft background)
  This zone will have the character's name and emotion word overlaid.
- Character portrait from waist up, positioned in the center-to-lower portion
- Face should be the focal point, clearly visible
- Background suggests the setting but doesn't compete: {scene_context if scene_context else "simple desert/indoor scene"}

Aspect ratio: 5:7 portrait. Full-bleed illustration extending to all edges.

=== MOOD ===
Warm, inviting. This character should feel like someone children want to know.
"""
    return prompt.strip()


def build_story_prompt_v2(
    scene_description: str,
    characters: List[dict],
    key_elements: List[str],
    sequence_context: str = "",
) -> str:
    """
    Build a v2 image prompt for a Story card.

    No text will be rendered - bottom-left corner reserved for keyword badge overlay.

    Args:
        scene_description: Description of the scene/action
        characters: List of dicts with 'key', 'description', and 'emotion'
        key_elements: 2-4 key visual elements in the scene
        sequence_context: Where this fits in the story sequence
    """
    spec = get_overlay_spec("story")

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

    prompt = f"""
Create an action scene illustration for a children's educational card.

=== STYLE ===
{STYLE_ANCHORS_V2}

=== SAFETY RULES ===
{SAFETY_PROMPT}

=== SCENE ===
{scene_description}
{f"Story Context: {sequence_context}" if sequence_context else ""}

Characters in Scene:
{characters_text}

Key Visual Elements:
{elements_text}

=== COMPOSITION ===
{spec.get('composition_hint', '')}

- This is a FULL-BLEED scene - use the entire card
- The BOTTOM-LEFT CORNER should have a relatively simple area (about 15-20% of card width)
  This is where a keyword badge will be overlaid programmatically.
- Main action should be in the center or center-right of the image
- Keep the scene dynamic but not chaotic
- 5-7 visual elements maximum

Aspect ratio: 5:7 portrait. Full-bleed illustration extending to all edges.

=== MOOD ===
Dynamic, engaging. Capture the key emotional moment of this scene.
"""
    return prompt.strip()


def build_connection_prompt_v2(
    theme: str,
    scene_description: str = "",
) -> str:
    """
    Build a v2 image prompt for a Connection (discussion) card.

    No text will be rendered - bottom 20% reserved for emoji row overlay.

    Args:
        theme: The theme being explored
        scene_description: Optional scene description (default: children in discussion)
    """
    spec = get_overlay_spec("connection")

    default_scene = "2-3 diverse children in thoughtful, wondering poses - one with hand on chin thinking, one looking up curiously, one pondering with finger to lips"
    scene = scene_description if scene_description else default_scene

    prompt = f"""
Create an illustration for a children's discussion/thinking card.

=== STYLE ===
{STYLE_ANCHORS_V2}

=== SAFETY RULES ===
{SAFETY_PROMPT}

=== SCENE ===
Theme: {theme}
Visual: {scene}

The illustration should convey:
- Peaceful, reflective mood
- Characters in "wondering" poses (hand on chin, looking up, etc.)
- Safe space for sharing feelings
- Warm, inviting atmosphere

=== COMPOSITION ===
{spec.get('composition_hint', '')}

- The BOTTOM 20% should be a simple, uncluttered area (gradient or solid soft color)
  This zone will have emoji faces overlaid programmatically.
- Main illustration in the upper 80% of the card
- Characters should be clearly visible but not crowded
- Soft, warm lighting throughout
- Simple background that doesn't distract

Aspect ratio: 5:7 portrait. Full-bleed illustration extending to all edges.

=== MOOD ===
Calm, curious, inviting. Children should feel safe to share their thoughts.
"""
    return prompt.strip()


def build_power_word_prompt_v2(
    english_meaning: str,
    visual_representation: str,
    is_emotion_word: bool = False,
) -> str:
    """
    Build a v2 image prompt for a Power Word vocabulary card.

    No text will be rendered - top 30% reserved for Hebrew word and meaning overlay.

    Args:
        english_meaning: English translation (for context, not rendered)
        visual_representation: How to visually represent the word
        is_emotion_word: Whether this is an emotion vocabulary word
    """
    spec = get_overlay_spec("power_word")

    emotion_note = ""
    if is_emotion_word:
        emotion_note = """
Since this represents an emotion word, show a character clearly displaying this emotion.
The facial expression and body language should make the emotion unmistakable.
"""

    prompt = f"""
Create an illustration for a children's vocabulary card about "{english_meaning}".

=== STYLE ===
{STYLE_ANCHORS_V2}

=== SAFETY RULES ===
{SAFETY_PROMPT}

=== VISUAL CONCEPT ===
{visual_representation}

{emotion_note}

=== COMPOSITION ===
{spec.get('composition_hint', '')}

- The TOP 30% should be a simple, uncluttered area (gradient, sky, or soft glow)
  This zone will have the Hebrew word and English meaning overlaid.
- Main illustration in the lower 70% of the card
- One central element that clearly represents the concept
- Very simple, focused composition
- Bright, engaging colors

Aspect ratio: 5:7 portrait. Full-bleed illustration extending to all edges.

=== MOOD ===
Educational but fun! The concept should be immediately clear from the image alone.
"""
    return prompt.strip()


def build_tradition_prompt_v2(
    tradition_name: str,
    practice_description: str,
    scene_description: str = "",
) -> str:
    """
    Build a v2 image prompt for a Tradition card (holiday decks).

    No text will be rendered - top 25% reserved for title overlay.

    Args:
        tradition_name: Name of the tradition (for context, not rendered)
        practice_description: What the practice looks like
        scene_description: Optional specific scene description
    """
    spec = get_overlay_spec("tradition")

    default_scene = "Family or community joyfully participating in the practice together, warm golden lighting"
    scene = scene_description if scene_description else default_scene

    prompt = f"""
Create a warm, celebratory illustration for a children's tradition card.

=== STYLE ===
{STYLE_ANCHORS_V2}

Use a WARM GOLDEN color palette - this should feel like candlelight or sunset.
Colors: warm ambers, soft golds, cream, warm browns

=== SAFETY RULES ===
{SAFETY_PROMPT}

=== SCENE ===
Practice: {practice_description}
Visual: {scene}

Show people DOING the practice together - community/family scene.
Include children participating. Warm, inviting atmosphere.

=== COMPOSITION ===
{spec.get('composition_hint', '')}

- The TOP 25% should be a simple, uncluttered area (warm gradient or soft golden glow)
  This zone will have the tradition title overlaid.
- Main scene in the lower 75% of the card
- Community/family togetherness feeling
- Warm, golden lighting throughout
- NOT instructional or diagram-like - show the joy of the practice

Aspect ratio: 5:7 portrait. Full-bleed illustration extending to all edges.

=== MOOD ===
Warm, celebratory, joyful. The practice should look inviting and fun to participate in.
"""
    return prompt.strip()


def build_divine_presence_prompt_v2(
    scene_description: str,
    manifestation_type: str = "light_rays",
    overlay_zone: str = "top_25",
) -> str:
    """
    Build a v2 prompt for scenes involving divine presence.
    Never depicts God in human form - uses abstract representations.

    Args:
        scene_description: The scene context
        manifestation_type: How to show divine presence
        overlay_zone: Where text will be overlaid
    """
    manifestations = {
        "light_rays": "golden light rays streaming down from above, warm and gentle",
        "clouds": "soft, glowing clouds with light emanating from within",
        "hands_from_above": "gentle hands emerging from clouds above, made of light",
        "pillar_of_fire": "a magnificent pillar of warm, non-threatening fire reaching up to the sky",
        "pillar_of_cloud": "a tall, majestic pillar of soft white cloud",
    }

    divine_visual = manifestations.get(manifestation_type, manifestations["light_rays"])

    # Determine composition based on overlay zone
    if overlay_zone == "top_25" or overlay_zone == "top_30":
        composition_hint = "Compose the scene in the lower 70-75%. The divine light can extend into the top area but keep it simple for text overlay."
    else:
        composition_hint = "Full-bleed scene. Keep the specified overlay zone relatively simple."

    prompt = f"""
Create an illustration showing a scene of divine presence for children.

=== STYLE ===
{STYLE_ANCHORS_V2}

=== SAFETY RULES ===
CRITICAL: Do NOT depict God as a person or human figure.
Use only abstract representations: light, clouds, or symbolic imagery.
{SAFETY_PROMPT}

=== SCENE ===
{scene_description}

Divine Presence: {divine_visual}

=== COMPOSITION ===
{composition_hint}

- The divine presence should feel warm, loving, and safe (not scary)
- Light should be golden/warm, not harsh
- Characters in the scene should look awed but not frightened
- Create a sense of wonder and majesty

Aspect ratio: 5:7 portrait. Full-bleed illustration extending to all edges.

=== MOOD ===
Awe-inspiring, wondrous, sacred but not scary. Children should feel amazed, not afraid.
"""
    return prompt.strip()


# =============================================================================
# LEGACY PROMPT BUILDERS (v1 - for backward compatibility)
# =============================================================================

def build_anchor_prompt(
    parasha_name: str,
    symbol_description: str,
    emotional_tone: str,
    border_color: str,
) -> str:
    """
    Build an image prompt for an Anchor card (legacy v1).

    Args:
        parasha_name: Name of the parasha
        symbol_description: Description of the central symbol
        emotional_tone: The emotional tone to convey
        border_color: Hex color for thematic border
    """
    prompt = f"""
Create an illustration for a children's educational card introducing "{parasha_name}".

Central Element:
{symbol_description}

Emotional Tone: {emotional_tone}

{STYLE_ANCHORS}

Important:
- The image should be iconic and memorable
- Central symbol should be large and clear
- Use light rays or glowing effects to convey significance
- Background should be simple and not distract from the symbol
- Leave space at the bottom for text overlay

{SAFETY_PROMPT}
"""
    return prompt.strip()


def build_spotlight_prompt(
    character_key: str,
    emotion: str,
    scene_context: str = "",
    additional_details: str = "",
) -> str:
    """
    Build an image prompt for a Spotlight (character) card (legacy v1).

    Args:
        character_key: Key from CHARACTER_DESIGNS
        emotion: The emotion the character should display
        scene_context: Optional context for the scene
        additional_details: Any additional visual details
    """
    character_style = get_character_style(character_key)

    prompt = f"""
Create a character portrait illustration for a children's educational card.

Character: {character_style}

Emotion to Display: {emotion}
The character's face and body language should clearly show they are feeling {emotion}.
- Make the facial expression very clear and readable
- Eyes and mouth should strongly convey the emotion
- Body posture should match the emotional state

{f"Scene Context: {scene_context}" if scene_context else ""}
{f"Additional Details: {additional_details}" if additional_details else ""}

{STYLE_ANCHORS}

Important:
- Character should fill most of the frame (portrait style)
- Face should be clearly visible and expressive
- Background should be simple, suggesting the setting
- Leave space at the bottom for text overlay

{SAFETY_PROMPT}
"""
    return prompt.strip()


def build_action_prompt(
    scene_description: str,
    characters: list,
    emotional_reactions: list,
    key_elements: list,
    sequence_context: str = "",
) -> str:
    """
    Build an image prompt for an Action card (legacy v1).

    Args:
        scene_description: Description of the scene/action
        characters: List of character keys involved
        emotional_reactions: Emotions characters should display
        key_elements: 2-4 key visual elements in the scene
        sequence_context: Where this fits in the story sequence
    """
    # Build character descriptions
    character_prompts = []
    for i, char_key in enumerate(characters):
        char_style = get_character_style(char_key)
        emotion = emotional_reactions[i] if i < len(emotional_reactions) else "engaged"
        character_prompts.append(f"- {char_style}, looking {emotion}")

    characters_text = "\n".join(character_prompts)
    elements_text = "\n".join(f"- {elem}" for elem in key_elements[:4])

    prompt = f"""
Create an action scene illustration for a children's educational card.

Scene: {scene_description}
{f"Story Context: {sequence_context}" if sequence_context else ""}

Characters in Scene:
{characters_text}

Key Visual Elements (show these clearly):
{elements_text}

{STYLE_ANCHORS}

Important:
- Show action and movement
- Characters should be clearly reacting emotionally to the scene
- Keep composition simple with 3-4 main elements
- Dynamic but not chaotic
- Leave space at the bottom for text overlay

{SAFETY_PROMPT}
"""
    return prompt.strip()


def build_thinker_prompt(
    theme: str,
    characters: list,
    wondering_context: str,
) -> str:
    """
    Build an image prompt for a Thinker card (legacy v1).

    Args:
        theme: The theme being explored
        characters: Characters to show in wondering poses
        wondering_context: What they might be thinking about
    """
    character_prompts = []
    for char_key in characters:
        char_style = get_character_style(char_key)
        character_prompts.append(f"- {char_style}, with a thoughtful, wondering expression")

    characters_text = "\n".join(character_prompts)

    prompt = f"""
Create an illustration for a children's discussion/thinking card.

Theme: {theme}
Context: {wondering_context}

Characters:
{characters_text}

The characters should appear to be:
- Deep in thought
- Looking curious or contemplative
- Perhaps looking at each other or at something meaningful
- Showing a mix of emotions (wonder, curiosity, reflection)

{STYLE_ANCHORS}

Important:
- Peaceful, reflective mood
- Characters in "wondering" poses (hand on chin, looking up, etc.)
- Soft, warm lighting
- Simple background that doesn't distract
- Leave significant space at the bottom for questions overlay

{SAFETY_PROMPT}
"""
    return prompt.strip()


def build_power_word_prompt(
    hebrew_word: str,
    english_meaning: str,
    visual_representation: str,
    is_emotion_word: bool = False,
) -> str:
    """
    Build an image prompt for a Power Word vocabulary card (legacy v1).

    Args:
        hebrew_word: The Hebrew word (without nikud for prompt)
        english_meaning: English translation
        visual_representation: How to visually represent the word
        is_emotion_word: Whether this is an emotion vocabulary word
    """
    emotion_note = ""
    if is_emotion_word:
        emotion_note = """
Since this is an emotion word, show a character clearly displaying this emotion.
The facial expression and body language should make the emotion unmistakable.
"""

    prompt = f"""
Create an illustration for a Hebrew vocabulary card teaching the word "{english_meaning}".

Visual Representation:
{visual_representation}

{emotion_note}

{STYLE_ANCHORS}

Important:
- The concept should be immediately clear from the image alone
- Very simple, focused composition
- One central element that represents the word
- Bright, engaging colors
- Leave space for the Hebrew word at top and English at bottom

{SAFETY_PROMPT}
"""
    return prompt.strip()


def build_divine_presence_prompt(
    scene_description: str,
    manifestation_type: str = "light_rays",
) -> str:
    """
    Build a prompt for scenes involving divine presence (legacy v1).
    Never depicts God in human form - uses abstract representations.

    Args:
        scene_description: The scene context
        manifestation_type: How to show divine presence
            Options: "light_rays", "clouds", "hands_from_above", "pillar_of_fire", "pillar_of_cloud"
    """
    manifestations = {
        "light_rays": "golden light rays streaming down from above, warm and gentle",
        "clouds": "soft, glowing clouds with light emanating from within",
        "hands_from_above": "gentle hands emerging from clouds above, made of light",
        "pillar_of_fire": "a magnificent pillar of warm, non-threatening fire reaching up to the sky",
        "pillar_of_cloud": "a tall, majestic pillar of soft white cloud",
    }

    divine_visual = manifestations.get(manifestation_type, manifestations["light_rays"])

    prompt = f"""
Create an illustration showing a scene of divine presence for children.

Scene: {scene_description}

Divine Presence Representation:
{divine_visual}

CRITICAL: Do NOT depict God as a person or human figure.
Use only abstract representations: light, clouds, or symbolic imagery.

{STYLE_ANCHORS}

Important:
- The divine presence should feel warm, loving, and safe (not scary)
- Light should be golden/warm, not harsh
- Characters in the scene should look awed but not frightened
- Create a sense of wonder and majesty

{SAFETY_PROMPT}
"""
    return prompt.strip()


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("=== V2 ANCHOR CARD PROMPT ===")
    print(build_anchor_prompt_v2(
        parasha_name="Yitro",
        symbol_description="Two stone tablets with rounded tops, glowing with warm golden light rays streaming from clouds above",
        emotional_tone="awe, wonder, and reverence",
    ))

    print("\n\n=== V2 SPOTLIGHT CARD PROMPT ===")
    print(build_spotlight_prompt_v2(
        character_key="moshe",
        character_description="Moses with kind eyes, head covering, blue and cream robes",
        emotion="devoted and caring",
        scene_context="desert setting with people waiting",
    ))

    print("\n\n=== V2 STORY CARD PROMPT ===")
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

    print("\n\n=== V2 CONNECTION CARD PROMPT ===")
    print(build_connection_prompt_v2(
        theme="Being Brave",
        scene_description="Children sitting in a circle, some with hands raised, sharing their feelings",
    ))
