# Decks Directory Documentation

Each subdirectory contains a complete card deck for one Torah portion (parasha).

## Directory Structure

```
decks/
├── CLAUDE.md           # This file
└── purim/              # Example deck
    ├── deck.json       # All card data and metadata
    ├── feedback.json   # Review comments and status
    ├── raw/            # AI-generated images (scene only, NO text)
    │   ├── anchor_1.png
    │   ├── story_1.png
    │   └── ...
    ├── images/         # Final exports with text overlay (from Card Designer)
    │   ├── anchor_1.png
    │   ├── story_1.png
    │   └── ...
    ├── backs/          # Teacher content backs (from Card Designer)
    │   ├── anchor_1_back.png
    │   ├── story_1_back.png
    │   └── ...
    └── references/     # Character identity references
        ├── manifest.json
        ├── esther_identity.png
        └── mordechai_identity.png
```

## Image Flow

1. **AI generates to `raw/`** - Scene-only images, no text baked in
2. **Card Designer renders** - React components add text overlay
3. **Export to `images/` and `backs/`** - Final print-ready files

```bash
# Generate raw images
cd src && python generate_images.py ../decks/purim/deck.json

# Export with Card Designer
cd card-designer && npm run export purim -- --backs
```

## Creating a New Deck

```bash
cd src
python workflows.py deck "ParashaName" --output ../decks/parasha_name
```

This creates:
- `deck.json` - Template with 12 placeholder cards
- `feedback.json` - Empty feedback structure
- `images/` - Directory for generated images
- `references/` - Directory for character sheets

## deck.json Structure

```json
{
  "parasha_en": "Yitro",
  "parasha_he": "יִתְרוֹ",
  "ref": "Exodus 18:1-20:23",
  "border_color": "#5c2d91",
  "theme": "covenant",
  "version": "2.0",
  "target_age": "4-6",
  "card_count": 12,
  "mitzvah_connection": "Listening carefully and respecting parents/teachers",
  "cards": [...]
}
```

### Card Structure by Type

**Anchor Card (1 per deck)**
```json
{
  "card_id": "anchor_1",
  "card_type": "anchor",
  "title_en": "Yitro",
  "title_he": "יִתְרוֹ",
  "emotional_hook_en": "This week is about feeling listened to!",
  "emotional_hook_he": "השבוע על להרגיש שמקשיבים לנו!",
  "symbol_description": "Mountain with clouds and light rays",
  "border_color": "#5c2d91",
  "image_prompt": "...",
  "image_path": "images/anchor_1.png",
  "teacher_script": "Gather children in a circle..."
}
```

**Spotlight Card (2 per deck)**
```json
{
  "card_id": "spotlight_1",
  "card_type": "spotlight",
  "title_en": "Moses",
  "title_he": "מֹשֶׁה",
  "character_name_en": "Moses",
  "character_name_he": "מֹשֶׁה",
  "emotion_label": "caring",
  "character_trait": "A kind leader who loves his family",
  "character_description_en": "Moses led the people out of Egypt...",
  "character_description_he": "משה הוביל את העם ממצרים...",
  "image_prompt": "...",
  "image_path": "images/spotlight_1.png",
  "teacher_script": "This is Moses! He's feeling..."
}
```

**Action Card (5 per deck)**
```json
{
  "card_id": "action_1",
  "card_type": "action",
  "title_en": "The Happy Reunion",
  "title_he": "הפגישה השמחה",
  "sequence_number": 1,
  "hebrew_key_word": "שמח",
  "hebrew_key_word_nikud": "שָׂמֵחַ",
  "english_description": "Yitro brings Moses's family to him",
  "roleplay_prompt": "Give someone a big hug like Moses!",
  "emotional_reactions": ["happy", "grateful", "excited"],
  "image_prompt": "...",
  "image_path": "images/action_1.png",
  "teacher_script": "Look at this happy moment..."
}
```

**Thinker Card (2 per deck)**
```json
{
  "card_id": "thinker_1",
  "card_type": "thinker",
  "title_en": "Feeling Tired",
  "title_he": "להרגיש עייף",
  "questions": [
    {
      "question_type": "emotional_empathy",
      "question_en": "How do you think Moses felt when he was so tired?",
      "question_he": "איך לדעתכם הרגיש משה כשהיה עייף?"
    },
    {
      "question_type": "cognitive_empathy",
      "question_en": "Why do you think Moses kept working so hard?",
      "question_he": "למה לדעתכם משה המשיך לעבוד כל כך קשה?"
    },
    {
      "question_type": "connection",
      "question_en": "Have you ever felt tired from helping others?",
      "question_he": "האם פעם הרגשתם עייפים מלעזור לאחרים?"
    }
  ],
  "torah_talk_instruction": "Sit in a circle and share!",
  "feeling_faces": [
    {"emoji": "😊", "label_en": "Happy", "label_he": "שָׂמֵחַ"},
    {"emoji": "😢", "label_en": "Sad", "label_he": "עָצוּב"},
    ...
  ],
  "image_prompt": "...",
  "image_path": "images/thinker_1.png",
  "teacher_script": "Let's talk about feelings..."
}
```

**Power Word Card (2 per deck)**
```json
{
  "card_id": "power_word_1",
  "card_type": "power_word",
  "title_en": "Shema - Listen",
  "title_he": "שְׁמַע",
  "hebrew_word": "שמע",
  "hebrew_word_nikud": "שְׁמַע",
  "transliteration": "Shema",
  "english_meaning": "Listen / Hear",
  "example_sentence_en": "We listen with our ears and our hearts!",
  "example_sentence_he": "אנחנו מקשיבים עם האוזניים ועם הלב!",
  "is_emotion_word": false,
  "image_prompt": "...",
  "image_path": "images/power_word_1.png",
  "teacher_script": "Let's learn a special Hebrew word..."
}
```

## v2 Card Format (Front/Back Separation)

v2 cards separate content for children (front) and teachers (back). Text is overlaid programmatically after image generation.

### Detecting v2 Cards

```python
def is_v2_card(card):
    return "front" in card and "back" in card
```

### v2 Directory Structure

```
decks/purim/
├── deck.json
├── images/
│   ├── anchor_1.png       # Image with overlaid text
│   ├── story_1.png
│   └── ...
├── backs/                  # NEW: Teacher card backs
│   ├── anchor_1_back.png
│   ├── story_1_back.png
│   └── ...
└── references/
```

### v2 Card Schemas by Type

**Anchor Card (v2)**
```json
{
  "card_id": "anchor_1",
  "card_type": "anchor",
  "front": {
    "overlay_zone": "top",
    "hebrew_title": "פּוּרִים"
  },
  "back": {
    "title_en": "Purim",
    "title_he": "פּוּרִים",
    "emotional_hook_en": "This week is about being brave!",
    "emotional_hook_he": "השבוע על להיות אמיצים!",
    "teacher_script": "Gather children in a circle..."
  },
  "image_prompt": "... === COMPOSITION ZONES === ...",
  "image_path": "images/anchor_1.png"
}
```

**Spotlight Card (v2)**
```json
{
  "card_id": "spotlight_1",
  "card_type": "spotlight",
  "front": {
    "overlay_zone": "top",
    "hebrew_name": "אֶסְתֵּר",
    "english_name": "Esther",
    "emotion_word_en": "brave",
    "emotion_word_he": "אַמִּיצָה"
  },
  "back": {
    "title_en": "Queen Esther",
    "title_he": "הַמַּלְכָּה אֶסְתֵּר",
    "character_description_en": "Esther was a brave queen...",
    "character_description_he": "אסתר הייתה מלכה אמיצה...",
    "teacher_script": "This is Queen Esther! She's feeling..."
  },
  "image_prompt": "...",
  "image_path": "images/spotlight_1.png"
}
```

**Story Card (v2)** *(replaces Action Card)*
```json
{
  "card_id": "story_1",
  "card_type": "story",
  "front": {
    "overlay_zone": "bottom_left",
    "hebrew_keyword": "מַלְכָּה",
    "english_keyword": "Queen"
  },
  "back": {
    "title_en": "Esther Becomes Queen",
    "title_he": "אֶסְתֵּר נַעֲשֵׂית מַלְכָּה",
    "sequence_number": 1,
    "description_en": "The king chose Esther to be his new queen...",
    "description_he": "הַמֶּלֶךְ בָּחַר בְּאֶסְתֵּר...",
    "roleplay_prompt": "Put an imaginary crown on your head and give a royal wave!",
    "teacher_script": "The king needed a new queen..."
  },
  "image_prompt": "...",
  "image_path": "images/story_1.png"
}
```

**Connection Card (v2)** *(replaces Thinker Card)*
```json
{
  "card_id": "connection_1",
  "card_type": "connection",
  "front": {
    "overlay_zone": "bottom",
    "emojis": ["😊", "😢", "😨", "😮"]
  },
  "back": {
    "title_en": "Being Brave",
    "title_he": "לִהְיוֹת אַמִּיץ",
    "questions": [
      "Have you ever had to do something scary?",
      "How did it feel to be brave?",
      "Who helps you feel brave?"
    ],
    "feeling_faces": [
      {"emoji": "😊", "label_he": "שָׂמֵחַ"},
      {"emoji": "😢", "label_he": "עָצוּב"},
      {"emoji": "😨", "label_he": "מְפֻחָד"},
      {"emoji": "😮", "label_he": "מֻפְתָּע"}
    ],
    "torah_talk_instruction": "Sit in a circle and share!",
    "teacher_script": "Let's talk about being brave..."
  },
  "image_prompt": "...",
  "image_path": "images/connection_1.png"
}
```

**Power Word Card (v2)**
```json
{
  "card_id": "power_word_1",
  "card_type": "power_word",
  "front": {
    "overlay_zone": "top",
    "hebrew_word": "גִּבּוֹר",
    "english_meaning": "Hero"
  },
  "back": {
    "title_en": "Gibor - Hero",
    "title_he": "גִּבּוֹר",
    "transliteration": "Gibor",
    "kid_friendly_explanation_en": "A hero is someone who helps others even when it's hard!",
    "kid_friendly_explanation_he": "גיבור הוא מי שעוזר לאחרים גם כשזה קשה!",
    "example_sentence_en": "Esther was a gibor when she spoke to the king.",
    "example_sentence_he": "אסתר הייתה גיבורה כשדיברה עם המלך.",
    "teacher_script": "Let's learn a special Hebrew word..."
  },
  "image_prompt": "...",
  "image_path": "images/power_word_1.png"
}
```

**Tradition Card (v2)** *(Holiday decks only)*
```json
{
  "card_id": "tradition_1",
  "card_type": "tradition",
  "front": {
    "overlay_zone": "top",
    "hebrew_title": "מִשְׁלוֹחַ מָנוֹת",
    "english_title": "Sending Gifts"
  },
  "back": {
    "title_en": "Mishloach Manot",
    "title_he": "מִשְׁלוֹחַ מָנוֹת",
    "story_connection_en": "Because everyone shared joy in Esther's time...",
    "story_connection_he": "כי כולם חלקו שמחה בימי אסתר...",
    "practice_description_en": "We give baskets of treats to friends and neighbors!",
    "practice_description_he": "אנחנו נותנים סלי מתנות לחברים ושכנים!",
    "child_action_en": "Can you help pack a gift basket?",
    "child_action_he": "?האם תוכלו לעזור לארוז סלת מתנות",
    "hebrew_term": "מִשְׁלוֹחַ מָנוֹת",
    "hebrew_term_meaning": "Sending portions (gifts)",
    "teacher_script": "On Purim, we give gifts to friends..."
  },
  "image_prompt": "...",
  "image_path": "images/tradition_1.png"
}
```

### v2 Front Overlay Zones

| Card Type | Zone | Content |
|-----------|------|---------|
| Anchor | Top 20-25% | Hebrew title |
| Spotlight | Top 30% | Hebrew name, English name, emotion |
| Story | Bottom-left | Hebrew/English keyword badge |
| Connection | Bottom 20% | 4 emojis (no labels) |
| Power Word | Top 30% | Hebrew word + English meaning |
| Tradition | Top 25% | Hebrew/English title |

### Generating v2 Cards

```bash
cd src

# Full v2 pipeline: generate images + overlay + card backs
python generate_images.py ../decks/purim/deck.json --with-overlay

# Just apply overlays to existing images
python generate_images.py ../decks/purim/deck.json --overlay-only

# Just generate card backs
python generate_images.py ../decks/purim/deck.json --backs-only

# Generate raw images without overlay (debugging)
python generate_images.py ../decks/purim/deck.json --no-overlay
```

### v2 Output Files

| File | Size | Purpose |
|------|------|---------|
| `images/{card_id}.png` | 1500x2100 | Card front with overlaid text |
| `backs/{card_id}_back.png` | 1500x2100 | Teacher card back (5x7 @ 300 DPI) |

---

## feedback.json Structure

```json
{
  "parasha": "Yitro",
  "deck_version": "2.0",
  "review_date": "2024-01-15",
  "cards": [
    {
      "card_id": "spotlight_1",
      "status": "needs_revision",
      "feedback": [
        {
          "category": "visual",
          "comment": "Moses's beard should be grayer",
          "priority": "medium",
          "resolved": false
        }
      ]
    }
  ],
  "global_feedback": "Overall style is good"
}
```

**Feedback categories:** visual, text, hebrew, educational, layout

**Priority levels:** low, medium, high

**Status values:** pending, approved, needs_revision

## references/ Directory

Contains character identity reference sheets for visual consistency.

**Important:** We generate ONLY the identity sheet per character (portrait + full body).
This single image is the source of truth for character appearance and is passed to
all card image generations to maintain consistency.

### manifest.json

```json
{
  "moses": {
    "identity": "decks/yitro/references/moses_identity.png"
  },
  "esther": {
    "identity": "decks/purim/references/esther_identity.png"
  }
}
```

### Why Only Identity?

Previously we generated 4 reference types (identity, expressions, turnaround, poses).
However, each was generated independently from text, resulting in inconsistent
interpretations of the same character. Now we generate ONE identity sheet and use
it as the reference for ALL card generations.

### Character Review Workflow

Before finalizing a new character identity:

1. **Generate versions:** Create 2+ identity variants
   ```bash
   # Generates {character}_identity_v1.png, {character}_identity_v2.png
   python workflows.py character haman --deck ../decks/purim --generate --versions 2
   ```

2. **User review:** Present versions for selection

3. **Finalize:** Rename selected version to canonical name
   ```bash
   mv haman_identity_v2.png haman_identity.png
   rm haman_identity_v1.png
   ```

4. **Update manifest:** Ensure manifest.json points to canonical file

### Generating References

```bash
cd src

# Generate identity reference for a character
python workflows.py character moses --deck ../decks/yitro --generate
```

## Workflow: Creating a Complete Deck

1. **Create deck structure:**
   ```bash
   python workflows.py deck "Beshalach" --output ../decks/beshalach
   ```

2. **Research and edit deck.json:**
   - Fill in card content (titles, descriptions, prompts)
   - Add Hebrew text with nikud
   - Write teacher scripts

3. **Create character references:**
   ```bash
   python workflows.py character miriam --deck ../decks/beshalach --generate
   python workflows.py character moses --deck ../decks/beshalach --generate
   ```

4. **Generate card images:**
   ```bash
   python generate_images.py ../decks/beshalach/deck.json
   ```

5. **Review in browser:**
   - v1 decks: Open `review-site/index.html`
   - v2 decks: Open `review-site-v2/index.html` (supports front/back flip preview)
   - Add feedback for each card
   - Export feedback JSON

6. **Iterate:**
   - Make revisions based on feedback
   - Regenerate images as needed
   - Mark cards as approved

## Image Naming Convention

### v1 Cards

Card images: `images/{card_id}.png`
- `anchor_1.png`
- `spotlight_1.png`, `spotlight_2.png`
- `action_1.png` through `action_5.png`
- `thinker_1.png`, `thinker_2.png`
- `power_word_1.png`, `power_word_2.png`

### v2 Cards

Card fronts: `images/{card_id}.png`
- `anchor_1.png`, `spotlight_1.png`, `story_1.png`, etc.

Card backs: `backs/{card_id}_back.png`
- `anchor_1_back.png`, `spotlight_1_back.png`, `story_1_back.png`, etc.

### Reference Sheets

Identity images: `references/{character_key}_identity.png`
- `moses_identity.png`
- `esther_identity.png`
- `haman_identity.png`

**Note:** We only use identity sheets now. Expression, turnaround, and pose sheets are deprecated.
