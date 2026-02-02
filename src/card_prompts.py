"""
Complete Card Prompt Generator for Parasha Pack

Generates full card images (not just illustrations) with:
- Borders and frames
- Title zones
- Text zones
- Character continuity
- Age-appropriate styling
"""

from typing import Optional

# =============================================================================
# STYLE CONSTANTS
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
# CHARACTER DESIGNS (for continuity)
# =============================================================================

CHARACTER_DESIGNS = {
    "moses": {
        "name": "Moses",
        "description": """=== CHARACTER: MOSES ===
Friendly middle-aged man with warm brown skin and kind, gentle eyes. Short dark beard with some gray showing he's experienced. Wears simple blue and cream robes with a HEAD COVERING (cloth wrap or simple turban). Often holds a wooden shepherd's staff. Has a calm, patient expression.

Key features (MUST include):
- Kind gentle eyes
- Short beard with touch of gray
- HEAD COVERING (cloth wrap/turban) - ALWAYS INCLUDE
- Wooden shepherd's staff
- Blue and cream robes
- Calm caring expression

CONTINUITY: This character must look identical in every card they appear in."""
    },
    "yitro": {
        "name": "Yitro/Jethro",
        "description": """=== CHARACTER: YITRO ===
Wise elderly man with long flowing white/gray beard. Warm twinkling eyes that show wisdom and kindness. Wears earth-toned desert robes (browns, tans). Has a gentle grandfatherly smile. May have a walking stick.

Key features (MUST include):
- Long flowing white/gray beard
- Twinkling wise eyes
- Grandfatherly warm smile
- Earth-toned desert robes
- Optional walking stick

CONTINUITY: This character must look identical in every card they appear in."""
    },
    "israelites": {
        "name": "The Israelites",
        "description": """=== CHARACTERS: ISRAELITES ===
A diverse group of friendly-looking people - men, women, and children. Wear simple robes in warm earth tones and soft colors. Faces show a mix of emotions appropriate to the scene. Include families together.

Key features:
- Diverse ages (children, adults, elderly)
- Simple modest clothing
- Warm, relatable expressions
- Show as a community/group

CONTINUITY: Group scenes should feel consistent across cards."""
    },
    "children": {
        "name": "Children of Israel",
        "description": """=== CHARACTERS: CHILDREN ===
Young children (ages 4-7 appearance) with big curious eyes. Wear simple robes. Show wonder and excitement. Relatable to the card's young audience.

Key features:
- Big expressive eyes
- Curious, engaged expressions
- Simple child-sized robes
- Relatable to young viewers"""
    }
}

# =============================================================================
# BORDER COLORS BY CARD TYPE
# =============================================================================

CARD_TYPE_BORDERS = {
    "anchor": {"color": "#5c2d91", "icon": "star", "name": "Royal Purple"},
    "spotlight": {"color": "#FFD700", "icon": "person", "name": "Gold"},
    "action": {"color": "#FF4136", "icon": "lightning-bolt", "name": "Red"},
    "thinker": {"color": "#0074D9", "icon": "thought-bubble", "name": "Blue"},
    "power_word": {"color": "#2ECC40", "icon": "aleph", "name": "Green"},
}

# =============================================================================
# PROMPT BUILDERS
# =============================================================================

def build_card_header(card_type: str) -> str:
    """Build the common header for all card prompts."""
    return f"""A vertical children's educational card in 5:7 aspect ratio (1500x2100 pixels).

{CARD_STYLE}
{SAFETY_RESTRICTIONS}
"""


def build_anchor_card_prompt(
    parasha_name_en: str,
    parasha_name_he: str,
    emotional_hook: str,
    symbol_description: str,
    border_color: str = "#5c2d91",
) -> str:
    """
    Build prompt for an Anchor card (parasha introduction).
    """
    return f"""{build_card_header("anchor")}

=== CARD TYPE: ANCHOR (Parasha Introduction) ===
This card introduces the weekly Torah portion and sets the emotional tone.

=== CONTENT ===
Hebrew Title: "פרשת {parasha_name_he}" (large, centered, with vowel marks/nikud)
English Title: "Parashat {parasha_name_en}"
Emotional Hook: "{emotional_hook}"

IMPORTANT: Define any complex emotions in simple terms for 4-6 year olds.
For example, "Awe means feeling amazed and a little bit surprised by something really special!"

=== CENTRAL SYMBOL ===
{symbol_description}

The symbol should be ICONIC and MEMORABLE - this is what children will associate with this parasha.

=== COMPOSITION ===
Layout (top to bottom):
1. HEBREW TITLE (top 15%): "פרשת {parasha_name_he}" in beautiful Hebrew lettering with nikud
2. ENGLISH TITLE (below Hebrew, 5%): "Parashat {parasha_name_en}" in friendly font
3. CENTRAL SYMBOL (center 55%): The main iconic image
   - Large, simple, immediately recognizable
   - Glowing or radiant quality
   - Centered and commanding attention
4. EMOTIONAL HOOK (bottom 15%): "{emotional_hook}" in playful, engaging font
5. DECORATIVE FOOTER (bottom 10%): Simple pattern or design element

=== FRAME ===
- Rounded corners (8-10px radius)
- Border: {border_color} (8px width)
- Star icon in top-left corner (anchor card indicator)

=== MOOD ===
This card should feel SPECIAL and EXCITING - like opening a present.
Children should feel: "Wow, what's THIS week's story about?"
"""


def build_spotlight_card_prompt(
    character_key: str,
    character_name_en: str,
    character_name_he: str,
    emotion: str,
    trait: str,
    description: str,
    border_color: str = "#FFD700",
) -> str:
    """
    Build prompt for a Spotlight card (character introduction).
    """
    char_design = CHARACTER_DESIGNS.get(character_key, {}).get("description", "")

    return f"""{build_card_header("spotlight")}

=== CARD TYPE: SPOTLIGHT (Character Introduction) ===
This card introduces a main character and shows ONE CLEAR EMOTION.

=== CONTENT ===
Character Name (Hebrew): "{character_name_he}"
Character Name (English): "{character_name_en}"
Emotion Label: "{emotion.upper()}"
Description: "{description}"

IMPORTANT - Emotion Guidelines:
- Use NUANCED emotions, not basic ones like "happy" or "sad"
- Good examples: joyful, grateful, caring, relieved, proud, curious, brave, hopeful
- The emotion should be specific to the story moment

IMPORTANT - Description Guidelines:
- Include rich context about who this character is
- Explain any relationships in child-friendly terms (e.g., "father-in-law means your wife's daddy")
- Describe what the character does in THIS parasha specifically

{char_design}

Expression: {emotion} - make this emotion VERY CLEAR in face and body language

=== COMPOSITION ===
Layout (top to bottom):
1. NAME ZONE (top 12%):
   - Hebrew name "{character_name_he}" (large, with nikud)
   - English name "{character_name_en}" below
2. CHARACTER PORTRAIT (center 65%):
   - Character fills most of this space (portrait/bust style)
   - Face clearly visible with BIG {emotion.upper()} expression
   - Eyes and mouth strongly convey the emotion
   - Body posture matches emotional state
   - Simple, contextual background (suggests setting)
3. EMOTION LABEL (corner badge): "{emotion.upper()}" in a colorful badge/bubble
4. DESCRIPTION (bottom 20%): "{description}"
   - Rich, detailed description (NOT a simple trait line)
   - Should explain who this character is and their role in the story

=== FRAME ===
- Rounded corners (8-10px radius)
- Border: {border_color} (8px width)
- Person icon in top-left corner (spotlight card indicator)

=== MOOD ===
Children should IMMEDIATELY understand how this character feels.
The emotion should be readable from across the room.
"""


def build_action_card_prompt(
    sequence_number: int,
    title_en: str,
    title_he: str,
    scene_description: str,
    text: str,
    characters: list[dict],  # [{"key": "moses", "emotion": "surprised"}]
    visual_description: str,
    hebrew_key_word: str,
    roleplay_prompt: str,
    border_color: str = "#FF4136",
) -> str:
    """
    Build prompt for an Action card (story moment).
    """
    # Build character section
    char_sections = []
    char_emotions = []
    for char in characters:
        key = char.get("key", "")
        emotion = char.get("emotion", "engaged")
        design = CHARACTER_DESIGNS.get(key, {}).get("description", "")
        if design:
            char_sections.append(f"{design}\n\nExpression: {emotion}\n")
        char_emotions.append(f"- {key}: {emotion}")

    characters_text = "\n".join(char_sections)
    emotions_list = "\n".join(char_emotions)

    return f"""{build_card_header("action")}

=== CARD TYPE: ACTION (Key Plot Moment) ===
Story moment #{sequence_number}
This card shows SOMETHING HAPPENING - characters reacting to an event.

=== CONTENT ===
Title: "{title_en}"
Hebrew Key Word: "{hebrew_key_word}"
Text: "{text}"

=== CHARACTERS IN SCENE ===
{characters_text}

Character emotions:
{emotions_list}

=== VISUAL DESCRIPTION ===
{visual_description}

=== COMPOSITION ===
Layout (top to bottom):
1. TITLE ZONE (top 10%): "{title_en}" in dynamic, action-oriented font
   - CONSISTENCY: Use the SAME font style across ALL action cards
2. SEQUENCE NUMBER: #{sequence_number} badge in top-left corner
   - CONSISTENCY: Use the SAME position and styling across ALL action cards
3. ACTION SCENE (center 65%): The main event happening
   - Characters REACTING emotionally (not just standing there)
   - Clear focal point - what's happening?
   - Movement and energy appropriate to the moment
   - Rich contextual details that tell the story
4. HEBREW KEY WORD BOX (prominent badge):
   - Hebrew word "{hebrew_key_word}" in large, clear lettering with nikud
   - English meaning directly below the Hebrew (NO transliteration)
   - CONSISTENCY: Use the SAME styling across ALL action cards (see action_5 style as template)
5. TEXT ZONE (bottom 15%): "{text}"
6. ROLEPLAY PROMPT (bottom strip): "{roleplay_prompt}"
   - Should be physically actionable and connect to emotional content

Action priorities:
- DYNAMIC - something is clearly happening
- EMOTIONAL - we see how characters FEEL about what's happening
- CONTEXTUAL - rich details that connect to the story
- CLEAR - children understand the moment at a glance

=== FRAME ===
- Rounded corners (8-10px radius)
- Border: {border_color} (8px width)
- Lightning bolt icon in top-left corner (action card indicator)
- Sequence number #{sequence_number} in top-right corner

=== MOOD ===
This is a "something's happening!" moment. Children should feel the excitement, wonder,
or emotion of this story beat.
"""


def build_thinker_card_prompt(
    title_en: str,
    title_he: str,
    theme: str,
    questions: list[dict],  # [{"type": "emotional_empathy", "text": "..."}]
    characters: list[str],
    visual_description: str,
    border_color: str = "#0074D9",
) -> str:
    """
    Build prompt for a Thinker card (discussion questions).
    """
    # Build character section
    char_sections = []
    for key in characters:
        design = CHARACTER_DESIGNS.get(key, {}).get("description", "")
        if design:
            char_sections.append(design)

    characters_text = "\n".join(char_sections) if char_sections else "Show thoughtful children in wondering poses."

    # Format questions
    q_text = "\n".join([f"• {q['text']}" for q in questions[:3]])

    return f"""{build_card_header("thinker")}

=== CARD TYPE: THINKER (Discussion Card) ===
This card sparks conversation and emotional connection.

=== CONTENT ===
Title: "{title_en}"
Hebrew Title: "{title_he}"
Theme: {theme}

Discussion Questions:
{q_text}

=== CHARACTERS ===
{characters_text}

All characters should appear THOUGHTFUL and WONDERING - in contemplative poses.

=== VISUAL DESCRIPTION ===
{visual_description}

=== COMPOSITION ===
Layout (top to bottom):
1. HEADER BAR (top 10%):
   - Thinker-type color bar (#0074D9 blue)
   - "{title_en}" with thought-bubble styling
   - CONSISTENCY: Header structure should match ALL card types, using thinker color
2. WONDERING SCENE (center 45%):
   - Characters in thoughtful poses (hand on chin, looking up, contemplating)
   - Peaceful, reflective atmosphere
   - Soft, warm lighting
   - Simple background that doesn't distract
3. FEELING FACES ROW (10%): Six emoji-style faces showing:
   😊 Happy | 😢 Sad | 😨 Scared | 😮 Surprised | 🥹 Proud | 😕 Confused
4. QUESTIONS ZONE (bottom 30%):
   - Three discussion questions in speech-bubble style boxes
   - Friendly, inviting typography
5. "Torah Talk: Sit in a circle and share!" instruction at bottom

=== FRAME ===
- Rounded corners (8-10px radius)
- Border: {border_color} (8px width)
- Thought-bubble icon in top-left corner (thinker card indicator)

=== MOOD ===
Calm, curious, and inviting. Children should feel safe to share their thoughts.
"""


def build_power_word_card_prompt(
    hebrew_word: str,
    hebrew_word_nikud: str,
    transliteration: str,
    english_meaning: str,
    example_sentence: str,
    visual_representation: str,
    is_emotion_word: bool = False,
    border_color: str = "#2ECC40",
) -> str:
    """
    Build prompt for a Power Word card (vocabulary).
    """
    emotion_note = ""
    if is_emotion_word:
        emotion_note = """
This is an EMOTION word - show a character CLEARLY displaying this emotion.
The facial expression and body language should make the emotion unmistakable.
"""

    return f"""{build_card_header("power_word")}

=== CARD TYPE: POWER WORD (Hebrew Vocabulary) ===
Teaching the Hebrew word: {english_meaning}

=== CONTENT ===
Hebrew Word (with nikud): "{hebrew_word_nikud}"
English Meaning: "{english_meaning}"
Example: "{example_sentence}"

IMPORTANT: Include a direct Torah quote showing this word in context from the parasha.

{emotion_note}

=== VISUAL REPRESENTATION ===
{visual_representation}

The visual should make the word's meaning IMMEDIATELY clear without reading.

=== COMPOSITION ===
Layout (top to bottom):
1. HEBREW WORD (top 25%):
   - "{hebrew_word_nikud}" in LARGE, beautiful Hebrew lettering
   - With full nikud (vowel marks) for pronunciation
   - Decorative but readable
   - NO transliteration (phonetic spelling) anywhere
2. VISUAL (center 45%):
   - Clear, simple illustration of the concept
   - One central element that represents the word
   - Bright, engaging colors
3. ENGLISH MEANING (10%): "{english_meaning}" in bold, clear font
4. TORAH QUOTE (10%): Direct quote from parasha where this word appears
5. EXAMPLE SENTENCE (bottom 10%): "{example_sentence}"

=== FRAME ===
- Rounded corners (8-10px radius)
- Border: {border_color} (8px width)
- NO icon in top-left corner
- NO QR codes anywhere

=== MOOD ===
Educational but FUN. Learning Hebrew should feel like discovering treasure.
"""


# =============================================================================
# CONVENIENCE FUNCTION TO BUILD ALL PROMPTS FOR A DECK
# =============================================================================

def build_prompts_for_deck(deck: dict) -> dict:
    """
    Build all card prompts for a deck.

    Returns dict mapping card_id to prompt string.
    """
    prompts = {}

    for card in deck.get("cards", []):
        card_id = card.get("card_id", "")
        card_type = card.get("card_type", "")

        if card_type == "anchor":
            prompts[card_id] = build_anchor_card_prompt(
                parasha_name_en=card.get("title_en", ""),
                parasha_name_he=card.get("title_he", ""),
                emotional_hook=card.get("emotional_hook_en", ""),
                symbol_description=card.get("symbol_description", ""),
                border_color=card.get("border_color", deck.get("border_color", "#5c2d91")),
            )

        elif card_type == "spotlight":
            # Determine character key from name
            char_key = card.get("character_name_en", "").lower().replace(" ", "_")
            if "moses" in char_key or "moshe" in char_key:
                char_key = "moses"
            elif "yitro" in char_key or "jethro" in char_key:
                char_key = "yitro"

            prompts[card_id] = build_spotlight_card_prompt(
                character_key=char_key,
                character_name_en=card.get("character_name_en", card.get("title_en", "")),
                character_name_he=card.get("character_name_he", card.get("title_he", "")),
                emotion=card.get("emotion_label", "happy"),
                trait=card.get("character_trait", ""),
                description=card.get("character_description_en", ""),
            )

        elif card_type == "action":
            # Build characters list from emotional_reactions
            characters = []
            reactions = card.get("emotional_reactions", [])
            # Infer characters from the card content
            title_lower = card.get("title_en", "").lower()
            if "reunion" in title_lower or "yitro" in title_lower.lower():
                characters = [
                    {"key": "moses", "emotion": reactions[0] if len(reactions) > 0 else "happy"},
                    {"key": "yitro", "emotion": reactions[1] if len(reactions) > 1 else "happy"},
                ]
            elif "mountain" in title_lower or "sinai" in title_lower:
                characters = [
                    {"key": "israelites", "emotion": reactions[0] if len(reactions) > 0 else "awed"},
                ]
            elif "commandments" in title_lower or "listen" in title_lower:
                characters = [
                    {"key": "israelites", "emotion": "attentive"},
                    {"key": "children", "emotion": "focused"},
                ]
            else:
                characters = [
                    {"key": "moses", "emotion": reactions[0] if len(reactions) > 0 else "engaged"},
                ]

            prompts[card_id] = build_action_card_prompt(
                sequence_number=card.get("sequence_number", 1),
                title_en=card.get("title_en", ""),
                title_he=card.get("title_he", ""),
                scene_description=card.get("english_description", ""),
                text=card.get("english_description", ""),
                characters=characters,
                visual_description=card.get("english_description", ""),
                hebrew_key_word=card.get("hebrew_key_word_nikud", ""),
                roleplay_prompt=card.get("roleplay_prompt", ""),
            )

        elif card_type == "thinker":
            questions = card.get("questions", [])
            q_list = [{"type": q.get("question_type", ""), "text": q.get("question_en", "")} for q in questions]

            prompts[card_id] = build_thinker_card_prompt(
                title_en=card.get("title_en", ""),
                title_he=card.get("title_he", ""),
                theme=card.get("title_en", ""),
                questions=q_list,
                characters=["children"],
                visual_description=f"Children thinking about: {card.get('title_en', '')}",
            )

        elif card_type == "power_word":
            prompts[card_id] = build_power_word_card_prompt(
                hebrew_word=card.get("hebrew_word", ""),
                hebrew_word_nikud=card.get("hebrew_word_nikud", ""),
                transliteration=card.get("transliteration", ""),
                english_meaning=card.get("english_meaning", ""),
                example_sentence=card.get("example_sentence_en", ""),
                visual_representation=f"Visual showing the concept of '{card.get('english_meaning', '')}'",
                is_emotion_word=card.get("is_emotion_word", False),
            )

    return prompts


if __name__ == "__main__":
    # Test with sample data
    print(build_action_card_prompt(
        sequence_number=2,
        title_en="Yitro's Good Idea",
        title_he="עֵצַת יִתְרוֹ",
        scene_description="Yitro advises Moses to appoint judges",
        text="Yitro said: 'Moses, you can't help everyone alone! Let others help too!'",
        characters=[
            {"key": "yitro", "emotion": "confident"},
            {"key": "moses", "emotion": "surprised-then-grateful"},
        ],
        visual_description="Yitro standing next to Moses, Yitro gesturing wisely with open palm, Moses has surprised/thoughtful expression with hand on chin, in background show multiple smaller figures representing other helpers/judges, warm desert colors, simple tent setting",
        hebrew_key_word="עֵצָה",
        roleplay_prompt="Act it out: Point your finger like a wise advisor!",
    ))
