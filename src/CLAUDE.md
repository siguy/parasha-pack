# Source Code Documentation

Python modules for generating and managing Parasha Pack card decks.

## Module Overview

| Module | Purpose |
|--------|---------|
| `workflows.py` | High-level reusable workflows for character/deck creation |
| `generate_deck.py` | Create new deck templates |
| `generate_images.py` | Generate card images via Gemini API |
| `generate_references.py` | Generate character reference sheets |
| `generate_with_consistency.py` | Generate consistent character images |
| `card_prompts.py` | Build complete card prompts |
| `image_prompts.py` | Image generation prompt templates |
| `schema.py` | Data structures and type definitions |
| `sefaria_client.py` | Sefaria API integration |
| `card_generator.py` | Print layout generation |

---

## workflows.py

High-level workflow functions that encapsulate research, creation, and generation steps.

### Character Workflow

```python
from workflows import CharacterWorkflow

# Full workflow (research + design + generate + save)
CharacterWorkflow.create("miriam", deck_path="decks/beshalach", api_key="...")

# Step-by-step
workflow = CharacterWorkflow("miriam", "decks/beshalach")
workflow.research()              # -> CharacterResearch dataclass
workflow.design()                # -> CharacterDesign dataclass
workflow.generate_references()   # -> creates 4 PNG reference sheets
workflow.add_to_manifest()       # -> updates manifest.json
workflow.save_research()         # -> saves research JSON
```

**CharacterResearch fields:**
- `name_en`, `name_he` - Character names
- `biblical_refs` - Scripture references
- `key_stories` - Major story appearances
- `personality_traits` - Character traits
- `relationships` - Dict of related characters
- `emotional_moments` - List of {event, emotion} dicts
- `age_appropriate_summary` - Child-friendly description

**CharacterDesign fields:**
- `key` - Lowercase identifier
- `visual_description` - Overall appearance
- `clothing`, `distinguishing_features`, `props` - Visual elements
- `signature_poses` - Key poses for reference sheet
- `style_prompt` - Full prompt snippet

### Deck Workflow

```python
from workflows import DeckWorkflow

# Full workflow
DeckWorkflow.full_create("Beshalach", "decks/beshalach")

# Step-by-step
workflow = DeckWorkflow("Beshalach")
workflow.research()       # -> ParashaResearch dataclass
workflow.create()         # -> creates deck.json, feedback.json, directories
workflow.save_research()  # -> saves parasha_research.json
```

**ParashaResearch fields:**
- `name_en`, `name_he`, `ref`, `book`
- `summary`, `key_events`, `main_characters`
- `themes`, `emotions`, `mitzvot`
- `child_friendly_lesson`
- `suggested_theme`, `border_color`

### Research Functions

```python
from workflows import research_character, research_parasha

# Get character research
research = research_character("moses")
print(research.key_stories)
print(research.personality_traits)

# Get parasha research
research = research_parasha("yitro")
print(research.key_events)
print(research.main_characters)
```

### Utility Functions

```python
from workflows import (
    list_available_characters,  # -> ["moses", "miriam", "yitro", ...]
    list_available_parshiyot,   # -> ["yitro", "beshalach", ...]
    get_character_summary,      # -> formatted string summary
    get_parasha_summary,        # -> formatted string summary
)
```

### CLI

```bash
# Character creation
python workflows.py character miriam --deck ../decks/beshalach --generate

# Deck creation
python workflows.py deck Beshalach --output ../decks/beshalach

# Research only
python workflows.py research character moses
python workflows.py research parasha yitro

# List available data
python workflows.py list characters
python workflows.py list parshiyot
```

---

## generate_deck.py

Creates new deck templates with placeholder cards.

### Functions

**`create_deck_template(parasha_name, parasha_he, ref, theme, border_color) -> dict`**
- Creates 12-card deck structure
- Returns dict ready for JSON serialization

### CLI

```bash
python generate_deck.py                    # Uses current parasha from Sefaria
python generate_deck.py --parasha "Yitro"  # Specific parasha
python generate_deck.py --output ../decks/yitro  # Custom output path
```

---

## generate_images.py

Generates card images using Gemini API.

### CLI

```bash
# Generate all images
python generate_images.py ../decks/yitro/deck.json

# Generate specific card
python generate_images.py ../decks/yitro/deck.json --card spotlight_1

# Skip existing images
python generate_images.py ../decks/yitro/deck.json --skip-existing

# Use different model
python generate_images.py ../decks/yitro/deck.json --model flash
```

**Options:**
- `--card CARD_ID` - Generate only specific card
- `--skip-existing` - Don't regenerate existing images
- `--model` - Model to use (imagen, flash)
- `--api-key` - Override GEMINI_API_KEY env var

---

## generate_references.py

Generates character reference sheets (identity, expressions, turnaround, poses).

### Functions

**`generate_image(prompt, api_key, output_path, aspect_ratio) -> bool`**
- Calls Gemini API to generate image
- Returns True on success

**`generate_all_references(api_key, output_dir, characters) -> dict`**
- Generates all 4 reference types for each character
- Creates manifest.json
- Returns dict of paths

**`get_identity_prompt(char_key) -> str`**
- Portrait + full body reference

**`get_expression_sheet_prompt(char_key) -> str`**
- 6-emotion expression grid

**`get_turnaround_prompt(char_key) -> str`**
- Front/3-4/side/back views

**`get_pose_sheet_prompt(char_key, poses) -> str`**
- Character action poses

### CLI

```bash
python generate_references.py --output ../decks/yitro/references
python generate_references.py --character moses  # Single character
python generate_references.py --type expressions  # Single type
```

---

## card_prompts.py

Builds complete card prompts with all styling and safety rules.

### Functions

**`build_anchor_prompt(deck, card) -> str`**
**`build_spotlight_prompt(deck, card) -> str`**
**`build_action_prompt(deck, card) -> str`**
**`build_thinker_prompt(deck, card) -> str`**
**`build_power_word_prompt(deck, card) -> str`**

Each function:
- Takes deck metadata and card data
- Returns complete prompt with style, safety rules, and layout specs

---

## schema.py

Data structures and type definitions.

### Card Types

```python
from schema import AnchorCard, SpotlightCard, ActionCard, ThinkerCard, PowerWordCard

# All inherit from BaseCard with:
# card_id, card_type, title_en, title_he, image_prompt, image_path, teacher_script
```

**AnchorCard:** `emotional_hook_en/he`, `symbol_description`, `border_color`

**SpotlightCard:** `character_name_en/he`, `emotion_label`, `character_trait`, `character_description_en/he`

**ActionCard:** `sequence_number`, `hebrew_key_word`, `hebrew_key_word_nikud`, `english_description`, `roleplay_prompt`, `emotional_reactions`

**ThinkerCard:** `questions` (list), `torah_talk_instruction`, `feeling_faces`

**PowerWordCard:** `hebrew_word`, `hebrew_word_nikud`, `transliteration`, `english_meaning`, `example_sentence_en/he`, `is_emotion_word`

### Deck

```python
from schema import Deck

deck = Deck(
    parasha_en="Yitro",
    parasha_he="יִתְרוֹ",
    ref="Exodus 18:1-20:23",
    border_color="#5c2d91",
    theme="covenant"
)
deck.add_card(some_card)
json_str = deck.to_json()
```

### Constants

- `EMOTIONS` - Categorized emotion lists
- `FEELING_FACES` - Emoji + label mappings
- `CHARACTER_DESIGNS` - Visual trait definitions
- `IMAGE_SAFETY_RULES` - Content restrictions
- `PRINT_SPECS` - Print specifications
- `LAYOUT_ZONES` - Card layout percentages

---

## sefaria_client.py

Sefaria API integration for Torah text and parasha data.

### Functions

**`fetch_current_parasha(diaspora=True) -> Parasha`**
- Gets this week's Torah portion from Sefaria calendar API

**`fetch_parasha_text(ref) -> dict`**
- Gets Hebrew and English text for a reference
- Returns `{"hebrew": [...], "english": [...], "ref": "..."}`

**`get_border_color(parasha_name, book) -> str`**
- Returns thematic hex color for parasha

### Parasha Dataclass

```python
parasha = fetch_current_parasha()
parasha.title_en      # "Yitro"
parasha.title_he      # "יִתְרוֹ"
parasha.ref           # "Exodus 18:1-20:23"
parasha.book          # "Exodus"
parasha.border_color  # "#5c2d91"
```

### Theme Mappings

- `THEME_COLORS` - Theme name to hex color
- `PARASHA_THEMES` - Parasha name to theme name

---

## card_generator.py

Generates print-ready card layouts.

### CLI

```bash
python card_generator.py ../decks/yitro/deck.json ../exports/yitro_layouts
```

Creates 300 DPI PNG files with:
- Proper bleed (0.125")
- Safe zones
- Card border styling

---

## Adding New Functionality

### Add a New Character to Research Database

1. Edit `workflows.py`
2. Add entry to `CHARACTER_DATABASE` dict:

```python
"new_character": CharacterResearch(
    name_en="New Character",
    name_he="שֵׁם",
    biblical_refs=["Genesis 1:1"],
    key_stories=["Story 1", "Story 2"],
    personality_traits=["kind", "brave"],
    relationships={"other": "relationship"},
    emotional_moments=[{"event": "...", "emotion": "..."}],
    age_appropriate_summary="Child-friendly description.",
),
```

3. Add visual defaults to `DEFAULT_DESIGNS` dict in `CharacterWorkflow.design()`

### Add a New Parasha to Research Database

1. Edit `workflows.py`
2. Add entry to `PARASHA_DATABASE` dict:

```python
"new_parasha": ParashaResearch(
    name_en="New Parasha",
    name_he="פָּרָשָׁה",
    ref="Book X:Y-Z",
    book="Book",
    summary="Brief summary",
    key_events=["Event 1", "Event 2"],
    main_characters=["Character1", "Character2"],
    themes=["theme1", "theme2"],
    emotions=["happy", "brave"],
    child_friendly_lesson="What kids should learn.",
    suggested_theme="covenant",
    border_color="#5c2d91",
),
```
