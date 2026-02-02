"""
Gemini image generation prompt templates for Parasha Pack.
Ensures consistent visual style across all cards.
"""

from typing import Optional
from schema import CHARACTER_DESIGNS, IMAGE_SAFETY_RULES


# Base style anchors for all images
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


def build_anchor_prompt(
    parasha_name: str,
    symbol_description: str,
    emotional_tone: str,
    border_color: str,
) -> str:
    """
    Build an image prompt for an Anchor card.

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
    Build an image prompt for a Spotlight (character) card.

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
    characters: list[str],
    emotional_reactions: list[str],
    key_elements: list[str],
    sequence_context: str = "",
) -> str:
    """
    Build an image prompt for an Action card.

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
    characters: list[str],
    wondering_context: str,
) -> str:
    """
    Build an image prompt for a Thinker card.

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
    Build an image prompt for a Power Word vocabulary card.

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
    Build a prompt for scenes involving divine presence.
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


# Example usage
if __name__ == "__main__":
    # Test anchor prompt
    print("=== ANCHOR CARD PROMPT ===")
    print(build_anchor_prompt(
        parasha_name="Yitro",
        symbol_description="Two stone tablets with the Ten Commandments, glowing with golden light, with light rays emanating from above",
        emotional_tone="awe, wonder, and reverence",
        border_color="#5c2d91",
    ))

    print("\n\n=== SPOTLIGHT CARD PROMPT ===")
    print(build_spotlight_prompt(
        character_key="moshe",
        emotion="happy and joyful",
        scene_context="reuniting with his father-in-law Yitro",
    ))

    print("\n\n=== ACTION CARD PROMPT ===")
    print(build_action_prompt(
        scene_description="Mount Sinai shaking with thunder and lightning",
        characters=["moshe"],
        emotional_reactions=["awed"],
        key_elements=[
            "Mountain with smoke rising",
            "Lightning in the sky",
            "People gathered at the base looking up",
        ],
        sequence_context="The dramatic moment when God descends on the mountain",
    ))
