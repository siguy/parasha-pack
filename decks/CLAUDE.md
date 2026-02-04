# Decks Directory Documentation

Each subdirectory contains a complete card deck for one Torah portion (parasha).

## Directory Structure

```
decks/
├── CLAUDE.md           # This file
└── yitro/              # Example deck
    ├── deck.json       # All card data and metadata
    ├── feedback.json   # Review comments and status
    ├── images/         # Generated card images
    │   ├── anchor_1.png
    │   ├── spotlight_1.png
    │   └── ...
    └── references/     # Character identity references
        ├── manifest.json
        ├── moses_identity.png      # Single source of truth
        └── yitro_identity.png
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
   - Open `review-site/index.html`
   - Add feedback for each card
   - Export feedback JSON

6. **Iterate:**
   - Make revisions based on feedback
   - Regenerate images as needed
   - Mark cards as approved

## Image Naming Convention

Card images: `{card_id}.png`
- `anchor_1.png`
- `spotlight_1.png`, `spotlight_2.png`
- `action_1.png` through `action_5.png`
- `thinker_1.png`, `thinker_2.png`
- `power_word_1.png`, `power_word_2.png`

Reference sheets: `{character_key}_{type}.png`
- `moses_identity.png`
- `moses_expressions.png`
- `moses_turnaround.png`
- `moses_poses.png`
