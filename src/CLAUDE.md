# Source Code Documentation

Python modules for generating and managing Parasha Pack card decks.

## Module Overview

| Module | Purpose |
|--------|---------|
| `workflows.py` | High-level reusable workflows for character/deck creation |
| `generate_deck.py` | Create new v2 deck templates (story, connection, tradition card types) |
| `generate_images.py` | Generate raw card images to `raw/`; assembles system prompt layers via `build_generation_prompt()` |
| `generate_references.py` | Generate character reference sheets |
| `generate_with_consistency.py` | Generate consistent character images |
| `card_prompts.py` | **DEPRECATED** — old prompt generator (embeds borders/text in prompts) |
| `image_prompts.py` | System constants (style, safety, composition) + scene-only `build_*_v2()` templates |
| `schema.py` | Data structures, type definitions, and card schemas |
| `sefaria_client.py` | Sefaria API integration |
| `card_generator.py` | Print layout generation |
| `overlay.py` | **DEPRECATED** - Text overlay now handled by Card Designer React components |
| `card_back_generator.py` | **DEPRECATED** - Card backs now rendered by Card Designer React components |
| `cleanup_prompts.py` | One-time migration script to remove text rendering from prompts |

## Image Generation Flow (v2)

```
deck.json image_prompt (pure scene description)
        ↓
build_generation_prompt() layers style + safety + composition + rules
        ↓
    raw/{card_id}.png (scene only, NO text, NO borders)
        ↓
Card Designer React (card-designer/)
        ↓
    npm run export <deckId>
        ↓
    images/{card_id}.png (final fronts with text + borders)
    backs/{card_id}_back.png (teacher content backs)
```

**Key principles:**
- AI generates scene-only images. Text and borders are rendered by React components.
- Deck prompts are **pure scene descriptions** — no composition, no rules.
- `build_generation_prompt()` layers style, safety, composition, and rules at generation time.

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

Creates new v2 deck templates with placeholder cards.

### Functions

**`create_deck_template(parasha_name, parasha_he, ref, theme, border_color, is_holiday) -> dict`**
- Standard deck: 10 cards (1 anchor, 2 spotlight, 4 story, 2 connection, 1 power_word)
- Holiday deck: +3 tradition cards = 13 cards
- v2 field names throughout
- Returns dict ready for JSON serialization

### CLI

```bash
python generate_deck.py                              # Current parasha from Sefaria
python generate_deck.py --parasha "Yitro"            # Specific parasha
python generate_deck.py --parasha "Purim" --holiday  # Holiday deck (adds tradition cards)
python generate_deck.py --output ../decks/yitro      # Custom output path
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
- `--model` - Model to use: nano-banana (default, recommended), imagen, flash
- `--api-key` - Override GEMINI_API_KEY env var
- `--no-refs` - Disable character reference images (for debugging)

### v2 Card Generation

For v2 decks, images are generated to `raw/` without text. Use Card Designer for final output:

```bash
# Generate raw scene images (no text)
python generate_images.py ../decks/purim/deck.json

# Then use Card Designer for text overlay and card backs
cd ../card-designer && npm run export purim -- --backs
```

---

## generate_references.py

Generates character identity reference sheets (single source of truth for character appearance).

**Note:** We generate ONLY identity sheets. Previously we generated 4 types (identity, expressions, turnaround, poses), but each was generated independently from text, producing inconsistent character interpretations. A single identity image now serves as the visual anchor for all card generations.

### Functions

**`generate_image(prompt, api_key, output_path, aspect_ratio) -> bool`**
- Calls Gemini API (nano-banana-pro model) to generate image
- Returns True on success

### CLI

```bash
python generate_references.py --output ../decks/yitro/references
python generate_references.py --character moses  # Single character
```

## generate_images.py - Reference Image Integration

When generating card images, reference images are automatically loaded and passed to the API.

### How It Works

1. **Load references:** Reads `references/manifest.json` in the deck directory
2. **Match characters:** Scans the image prompt for character names
3. **Encode images:** Base64-encodes matching identity PNG files
4. **API payload:** Includes image data alongside text prompt:
   ```python
   contents = [
       {"text": prompt},
       {"inlineData": {"mimeType": "image/png", "data": base64_image}}
   ]
   ```

### Key Functions

**`load_reference_images(deck_path, prompt) -> List[Dict]`**
- Loads identity images for characters mentioned in the prompt
- Returns list of base64-encoded image parts for API

**`generate_image_nano_banana(prompt, output_path, aspect_ratio, reference_images) -> bool`**
- Accepts optional reference_images parameter
- Passes images to API for consistency

### CLI Options

```bash
# Normal (with references)
python generate_images.py ../decks/purim/deck.json

# Without references (for debugging)
python generate_images.py ../decks/purim/deck.json --no-refs
```

---

## Prompt Assembly System

All system concerns are defined once and layered automatically at generation time by `build_generation_prompt()` in `generate_images.py`.

### How It Works

1. **Deck prompts** (`deck.json` `image_prompt`) are pure scene descriptions — no style, safety, composition, or rules
2. **At generation time**, `build_generation_prompt(scene_prompt, card_type)` assembles:
   1. `STYLE_ANCHORS_V2` — children's illustration style, cultural context, anatomy rules
   2. `SAFETY_PROMPT` — content restrictions (no God in human form, no violence, etc.)
   3. Scene description — from deck.json, passed through unchanged
   4. `COMPOSITION_GUIDANCE[card_type]` — per-card-type cinematography (headroom, subject placement, shadow)
   5. `COMPOSITION_SUFFIX` — universal no-border, no-text rules
3. **The model** interprets cinematography language natively (where the subject IS, not where text will go)

### Card Type Composition

| Card Type | Subject Position | Open Space |
|-----------|-----------------|------------|
| Anchor | Center-low | Headroom above (for title) |
| Spotlight | Chest-up portrait, center | Headroom above, shadow lower-left |
| Story | Action center-right | Headroom above, shadow lower-left |
| Connection | Upper two-thirds | Simple floor/gradient below |
| Tradition | Center-low, grounded | Golden glow/warm haze above |
| Power Word | Center-low, heroic angle | Bright sky/light above |

### Key Files

- **`image_prompts.py`**: `STYLE_ANCHORS_V2`, `SAFETY_PROMPT`, `COMPOSITION_GUIDANCE`, `COMPOSITION_SUFFIX` + scene-only `build_*_v2()` template functions
- **`generate_images.py`**: `build_generation_prompt()` — assembles all layers

---

## card_prompts.py (DEPRECATED)

Old prompt generator that embeds borders, text zones, and layout instructions in image prompts. Incompatible with current pipeline where AI generates scene-only images and Card Designer renders text.

For new decks, use:
- `image_prompts.py` `build_*_v2()` functions for scene-only prompt templates
- Or write scene descriptions directly in `deck.json` `image_prompt` fields

---

## schema.py

Data structures and type definitions.

### Card Structure

```python
from schema import CardV2, Deck

# CardV2: front/back separation
# card_id, card_type, front (dict), back (dict), image_prompt, session, optional
```

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

## overlay.py (v2)

Programmatic text overlay for v2 card fronts using PIL/Pillow.

### Functions

**`overlay_card_front(image_path, card_type, front_data, output_path) -> bool`**
- Overlays text on generated card image
- Different zones per card type (top, bottom-left, etc.)
- Supports Hebrew with nikud

### CLI

```bash
# Process all v2 cards in a deck
python overlay.py ../decks/purim/deck.json

# Process specific card
python overlay.py ../decks/purim/deck.json --card story_1
```

### Overlay Zones by Card Type

| Card Type | Zone | Content |
|-----------|------|---------|
| Anchor | Top 20-25% | Hebrew parasha title |
| Spotlight | Top 30% | Names + emotion |
| Story | Bottom-left | Keyword badge |
| Connection | Bottom 20% | 4 emojis |
| Power Word | Top 30% | Hebrew + English |
| Tradition | Top 25% | Titles |

---

## card_back_generator.py (v2)

Generates 5x7 printable card backs for teacher content.

### Functions

**`generate_card_back(card_type, back_data, deck_meta, output_path) -> bool`**
- Creates 1500x2100px (300 DPI) card back image
- Template-based layout with sections

### CLI

```bash
# Generate backs for all cards in deck
python card_back_generator.py ../decks/purim/deck.json

# Process specific card
python card_back_generator.py ../decks/purim/deck.json --card story_1

# Custom output directory
python card_back_generator.py ../decks/purim/deck.json --output ../exports/backs
```

### Card Back Layout

```
┌─────────────────────────────────────────┐
│  [Card Type Badge]        [Deck Name]   │
│  ═══════════════════════════════════════│
│  [Title - Hebrew & English]             │
│  ───────────────────────────────────────│
│  [Main Content Area]                    │
│  - Description                          │
│  - Questions (for connection cards)     │
│  - Roleplay prompt                      │
│  ───────────────────────────────────────│
│  [Teacher Script]                       │
│  ───────────────────────────────────────│
│  [Session #]              [Card #/Total]│
└─────────────────────────────────────────┘
```

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
