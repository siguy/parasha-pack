# Decks Directory Documentation

Each subdirectory contains a complete card deck for one Torah portion (parasha) or holiday.

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
    │   ├── ...
    │   ├── generations.jsonl  # Generation log (append-only provenance)
    │   └── prompts/           # Full assembled prompts (human-readable sidecars)
    │       ├── anchor_1.txt
    │       └── ...
    ├── images/         # Final exports with text overlay (from Card Designer)
    │   ├── anchor_1.png
    │   ├── story_1.png
    │   └── ...
    ├── backs/          # Teacher content backs (from Card Designer)
    │   ├── anchor_1_back.png
    │   ├── story_1_back.png
    │   └── ...
    └── references/     # Character + style references
        ├── manifest.json
        ├── style_hero.png         # Style anchor for story-world cards (optional)
        ├── esther_identity.png
        └── mordechai_identity.png
```

## Image Flow

1. **AI generates to `raw/`** — Scene-only images, no text baked in
2. **`build_generation_prompt()`** — Layers style, safety, composition, and rules at generation time
3. **Card Designer renders** — React components add text overlay
4. **Export to `images/` and `backs/`** — Final print-ready files

```bash
# Generate raw images (system layers added automatically)
cd src && python generate_images.py ../decks/purim/deck.json

# Export with Card Designer
cd card-designer && npm run export purim -- --backs
```

## Creating a New Deck

```bash
cd src
python generate_deck.py --parasha "Beshalach"              # Standard parasha deck (10 cards)
python generate_deck.py --parasha "Purim" --holiday         # Holiday deck (13 cards)
python generate_deck.py --output ../decks/beshalach         # Custom output path
```

This creates:
- `deck.json` — Template with placeholder cards
- `feedback.json` — Empty feedback structure
- `raw/` — Directory for AI-generated scene images
- `images/` — Directory for final exports
- `references/` — Directory for character sheets

## deck.json Structure

```json
{
  "parasha_en": "Purim",
  "parasha_he": "פּוּרִים",
  "ref": "",
  "border_color": "#8B5CF6",
  "theme": "celebration",
  "story_world": "Ancient Persian Empire, city of Shushan...",
  "version": "2.0",
  "target_age": "4-6",
  "card_count": 16,
  "holiday_en": "Purim",
  "holiday_he": "פּוּרִים",
  "cards": [...]
}
```

## Card Schemas by Type

### Anchor Card (1 per deck)
```json
{
  "card_id": "anchor_1",
  "card_type": "anchor",
  "title_en": "Purim",
  "title_he": "פּוּרִים",
  "emotional_hook_en": "Have you ever had to be really, really brave?",
  "emotional_hook_he": "הֲאִם אֵי פַּעַם הָיִיתָ צָרִיךְ לִהְיוֹת מַמָּשׁ אַמִּיץ?",
  "symbol_description": "A golden crown with Star of David",
  "border_color": "#8B5CF6",
  "characters_in_scene": [],
  "image_prompt": "A golden crown sitting on a royal purple velvet cushion...",
  "image_path": "raw/anchor_1.png",
  "teacher_script": "Gather children in a circle...",
  "teacher_tip": "Have children close their eyes while you describe the crown.",
  "transition_line": "Now let's meet the characters in our story!",
  "discussion_prompts": ["What do you think a queen's secret could be?", "When have you had a really big feeling inside?"],
  "session": 1
}
```

### Spotlight Card (2 per deck)
```json
{
  "card_id": "spotlight_1",
  "card_type": "spotlight",
  "title_en": "Queen Esther",
  "title_he": "אֶסְתֵּר",
  "character_name_en": "Queen Esther",
  "character_name_he": "אֶסְתֵּר",
  "emotion_label_en": "brave",
  "emotion_label_he": "אַמִּיצָה",
  "character_description_en": "Esther was a brave queen...",
  "character_description_he": "אסתר הייתה מלכה אמיצה...",
  "teaching_moment_en": "Even when she was scared, Esther did the right thing.",
  "border_color": "#8B5CF6",
  "characters_in_scene": ["esther"],
  "image_prompt": "Character portrait of Esther...",
  "image_path": "raw/spotlight_1.png",
  "teacher_script": "This is Queen Esther!...",
  "teacher_tip": "Ask children to show you a brave face, then a nervous face.",
  "transition_line": "Let's meet another important person in our story!",
  "discussion_prompts": ["What do you notice about how Esther looks?", "Have you ever kept something special about yourself quiet?"],
  "session": 1
}
```

### Story Card (4 per deck)
```json
{
  "card_id": "story_1",
  "card_type": "story",
  "title_en": "Esther Becomes Queen",
  "title_he": "אֶסְתֵּר נַעֲשֵׂית מַלְכָּה",
  "sequence_number": 1,
  "hebrew_key_word": "מלכה",
  "hebrew_key_word_nikud": "מַלְכָּה",
  "english_key_word": "Queen",
  "english_description": "The king chose Esther to be his new queen.",
  "roleplay_prompt": "Put an imaginary crown on your head and give a royal wave!",
  "border_color": "#8B5CF6",
  "characters_in_scene": ["esther"],
  "image_prompt": "Esther in the palace throne room...",
  "image_path": "raw/story_1.png",
  "teacher_script": "The king needed a new queen...",
  "teacher_tip": "Whisper 'shhh' when you mention the secret — children love the dramatic effect.",
  "transition_line": "Let's find out what happens next!",
  "discussion_prompts": ["How would it feel to live in a beautiful palace?", "What would be hard about keeping a really big secret?"],
  "session": 1
}
```

### Connection Card (2 per deck)
```json
{
  "card_id": "connection_1",
  "card_type": "connection",
  "title_en": "Being Brave",
  "title_he": "לִהְיוֹת אַמִּיץ",
  "questions": [
    {
      "question_type": "personal",
      "question_en": "Have you ever had to do something scary?",
      "question_he": ""
    },
    {
      "question_type": "empathy",
      "question_en": "How do you think Esther felt when she went to the king?",
      "question_he": ""
    }
  ],
  "emojis": ["😊", "😢", "😮", "💪"],
  "border_color": "#8B5CF6",
  "characters_in_scene": [],
  "image_prompt": "Children sitting in a circle on a colorful rug...",
  "image_path": "raw/connection_1.png",
  "teacher_script": "Let's talk about being brave...",
  "teacher_tip": "Share your own brave moment first to model vulnerability.",
  "transition_line": "You are all so brave for sharing!",
  "session": 2
}
```

Note: Connection cards do NOT have `discussion_prompts` — they use `questions[]` instead.

### Tradition Card (3 per holiday deck)
```json
{
  "card_id": "tradition_1",
  "card_type": "tradition",
  "title_en": "Mishloach Manot",
  "title_he": "מִשְׁלוֹחַ מָנוֹת",
  "story_connection_en": "Because everyone shared joy in Esther's time...",
  "story_connection_he": "כי כולם חלקו שמחה בימי אסתר...",
  "practice_description_en": "We give baskets of treats to friends!",
  "practice_description_he": "אנחנו נותנים סלי מתנות לחברים!",
  "child_action_en": "Can you help pack a gift basket?",
  "child_action_he": "",
  "hebrew_term": "מִשְׁלוֹחַ מָנוֹת",
  "hebrew_term_meaning": "Sending portions (gifts)",
  "border_color": "#8B5CF6",
  "characters_in_scene": [],
  "image_prompt": "Warm golden scene of families packing colorful baskets...",
  "image_path": "raw/tradition_1.png",
  "teacher_script": "On Purim, we give gifts to friends...",
  "teacher_tip": "Have small baskets or bags ready for children to practice packing.",
  "transition_line": "There's another special Purim tradition to discover!",
  "discussion_prompts": ["Who would you like to give a gift basket to?", "How does it feel when someone gives you a surprise gift?"],
  "session": 2
}
```

### Power Word Card (1 per deck)
```json
{
  "card_id": "power_word_1",
  "card_type": "power_word",
  "title_en": "Gibor - Hero",
  "title_he": "גִּבּוֹר",
  "hebrew_word": "גיבור",
  "hebrew_word_nikud": "גִּבּוֹר",
  "english_meaning": "Hero",
  "example_sentence_en": "Esther was a gibor when she spoke to the king.",
  "example_sentence_he": "אסתר הייתה גיבורה כשדיברה עם המלך.",
  "kid_friendly_explanation_en": "A hero helps others even when it's hard!",
  "kid_friendly_explanation_he": "",
  "border_color": "#8B5CF6",
  "characters_in_scene": ["esther"],
  "image_prompt": "Esther standing tall in the throne room...",
  "image_path": "raw/power_word_1.png",
  "teacher_script": "Let's learn a special Hebrew word...",
  "teacher_tip": "Have children repeat 'I am a gibor!' three times, louder each time.",
  "transition_line": "Now you know an amazing Hebrew word!",
  "discussion_prompts": ["Who is a gibor in your life?", "What is one brave thing you could do this week?"],
  "pronunciation_guide": "Gee-BOR. Rhymes with 'dinosaur'!",
  "session": 2
}
```

## Two Visual Worlds

Cards exist in one of two visual "worlds," injected automatically by `build_generation_prompt()`:

| World | Card Types | Source | Description |
|-------|-----------|--------|-------------|
| **Story World** | anchor, spotlight, story, power_word | `deck.json "story_world"` field | Historical/holiday setting, per-deck. E.g., ancient Persia for Purim. |
| **Modern World** | connection, tradition | `MODERN_WORLD_STYLE` in `image_prompts.py` | Modern Orthodox Jewish community. Same across all decks. |

The `story_world` field is a top-level string in deck.json describing the historical/geographic setting for the deck's story cards. The Torah Scholar determines this as part of research.

## Image Prompt Rules

Image prompts in deck.json should be **pure scene descriptions** — what to draw, not how to draw it.

**DO include:**
- Scene setting and characters
- Character appearance details (reinforces reference images)
- Emotional tone and mood
- Key visual elements

**DO NOT include:**
- Style instructions (`=== STYLE ===`) — injected automatically
- World/setting instructions (`=== WORLD ===`) — injected automatically from `story_world` or `MODERN_WORLD_STYLE`
- Safety rules (`=== RESTRICTIONS ===`) — injected automatically
- Composition guidance (`=== COMPOSITION ===`) — injected automatically
- Border/frame instructions — rendered by Card Designer
- Text rendering instructions — rendered by Card Designer
- Aspect ratio — handled by generation config

## Selective Character References

Each card includes `characters_in_scene` — a list of character keys whose identity reference images are loaded during generation. This prevents wrong characters from appearing (e.g., Haman in tradition cards).

| Card Type | characters_in_scene | Rationale |
|-----------|-------------------|-----------|
| Anchor | `[]` | Symbol only, no characters |
| Spotlight | `["character_key"]` | Single featured character |
| Story | `["char1", "char2"]` | Only characters depicted |
| Connection | `[]` | Generic children |
| Tradition | `[]` | Generic community |
| Power Word | `["character_key"]` | Character demonstrating word |

## Generation Provenance

Every image generation is tracked:

- **`raw/generations.jsonl`** — Append-only log. One JSON line per generation with card_id, timestamp, model, full_prompt, character_refs, success.
- **`raw/prompts/{card_id}.txt`** — Human-readable full assembled prompt. Overwritten each run (JSONL is the durable record).

To reproduce an image: find the entry in `generations.jsonl`, copy the `full_prompt`, and re-run with the same refs.

## Output Files

| File | Size | Purpose |
|------|------|---------|
| `raw/{card_id}.png` | 1500x2100 | Scene-only AI image (no text) |
| `raw/generations.jsonl` | — | Generation provenance log |
| `raw/prompts/{card_id}.txt` | — | Full assembled prompt (debug) |
| `images/{card_id}.png` | 1500x2100 | Card front with text overlay |
| `backs/{card_id}_back.png` | 1500x2100 | Teacher card back (5x7 @ 300 DPI) |

## Generating Cards

```bash
# Generate raw scene images
cd src && python generate_images.py ../decks/purim/deck.json

# Generate specific card
python generate_images.py ../decks/purim/deck.json --card story_1

# Skip existing images
python generate_images.py ../decks/purim/deck.json --skip-existing

# Without character references (debugging)
python generate_images.py ../decks/purim/deck.json --no-refs

# Backup existing images before regenerating
python generate_images.py ../decks/purim/deck.json --backup

# Export with Card Designer
cd card-designer && npm run export purim -- --backs
```

---

## feedback.json Structure

```json
{
  "parasha": "Purim",
  "deck_version": "2.0",
  "review_date": "2024-01-15",
  "cards": [
    {
      "card_id": "spotlight_1",
      "status": "needs_revision",
      "feedback": [
        {
          "category": "visual",
          "comment": "Esther's crown should be more prominent",
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
  "style_hero": {
    "identity": "style_hero.png",
    "description": "Persian palace throne room, golden light, ornate arches"
  },
  "esther": {
    "identity": "esther_identity.png"
  },
  "mordechai": {
    "identity": "mordechai_identity.png"
  }
}
```

The `style_hero` entry is optional. When present, its image is loaded as the first reference for story-world cards (anchor, spotlight, story, power_word) to anchor art style, color palette, and rendering quality. Modern-world cards skip it.

### Character Review Workflow

Before finalizing a new character identity:

1. **Generate versions:** Create 2+ identity variants
2. **User review:** Present versions for selection
3. **Finalize:** Rename selected version to canonical name (e.g., `haman_identity.png`)
4. **Update manifest:** Ensure manifest.json points to canonical file

```bash
cd src
python workflows.py character moses --deck ../decks/yitro --generate
```

## Workflow: Creating a Complete Deck

1. **Create deck structure:**
   ```bash
   python generate_deck.py --parasha "Beshalach"
   ```

2. **Research and edit deck.json:**
   - Fill in card content (titles, descriptions, prompts)
   - Write scene-only image prompts
   - Add Hebrew text with nikud
   - Write teacher scripts

3. **Create character references:**
   ```bash
   python workflows.py character miriam --deck ../decks/beshalach --generate
   ```

4. **Generate card images:**
   ```bash
   python generate_images.py ../decks/beshalach/deck.json
   ```

5. **Export with Card Designer:**
   ```bash
   cd card-designer && npm run export beshalach -- --backs
   ```

6. **Review and iterate:**
   - Open Card Designer dev server to preview
   - Add feedback to feedback.json
   - Regenerate images as needed
