# Source Code Documentation

Python modules for generating and managing Parasha Pack card decks.

## Module Overview

| Module | Purpose |
|--------|---------|
| `workflows/` | High-level reusable workflows for character/deck creation (CLI, research, models) |
| `generate_deck.py` | Create new deck templates (story, connection, tradition card types) |
| `generate_images.py` | Generate raw card images to `raw/`; assembles system prompt layers via `build_generation_prompt()` |
| `generate_references.py` | Generate character identity reference sheets |
| `image_prompts.py` | System constants (style, safety, composition, world styles) + scene-only `build_*_v2()` templates |
| `schema.py` | Data structures, type definitions, and card schemas |
| `sefaria_client.py` | Sefaria API integration |
| `config.py` | Configuration constants |

Deprecated v1 code lives in `archive/` for reference. Do not use for new decks.

## Image Generation Flow

```
deck.json image_prompt (pure scene description)
        ↓
build_generation_prompt() layers style + world + safety + composition + rules
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
- `build_generation_prompt()` layers style, world setting, safety, composition, and rules at generation time.

---

## workflows/

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
workflow.generate_references()   # -> creates identity PNG reference sheet
workflow.add_to_manifest()       # -> updates manifest.json
workflow.save_research()         # -> saves research JSON
```

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

**`create_deck_template(parasha_name, parasha_he, ref, theme, border_color, is_holiday) -> dict`**
- Standard deck: 10 cards (1 anchor, 2 spotlight, 4 story, 2 connection, 1 power_word)
- Holiday deck: +3 tradition cards = 13 cards

```bash
python generate_deck.py                              # Current parasha from Sefaria
python generate_deck.py --parasha "Yitro"            # Specific parasha
python generate_deck.py --parasha "Purim" --holiday  # Holiday deck (adds tradition cards)
python generate_deck.py --output ../decks/yitro      # Custom output path
```

---

## generate_images.py

Generates card images using Gemini API (nano-banana model).

```bash
python generate_images.py ../decks/yitro/deck.json              # Generate all
python generate_images.py ../decks/yitro/deck.json --card spotlight_1  # Single card
python generate_images.py ../decks/yitro/deck.json --skip-existing     # Skip existing
python generate_images.py ../decks/yitro/deck.json --no-refs           # Without character refs
```

### Reference Image Integration

1. Reads `references/manifest.json` in the deck directory
2. Scans prompt for character names, loads matching identity PNGs
3. Base64-encodes and passes alongside text prompt to API

---

## generate_references.py

Generates character identity reference sheets (single source of truth for character appearance).

We generate ONLY identity sheets. A single identity image serves as the visual anchor for all card generations.

```bash
python generate_references.py --output ../decks/yitro/references
python generate_references.py --character moses
```

---

## Prompt Assembly System

`build_generation_prompt()` in `generate_images.py` assembles all system layers at generation time:

1. `STYLE_ANCHORS_V2` — children's illustration style, anatomy rules
2. **World style** — `MODERN_WORLD_STYLE` for connection/tradition cards (modern Orthodox Jewish community, same across all decks), or `story_world` from deck.json for all other cards (per-deck historical setting)
3. `SAFETY_PROMPT` — content restrictions (no God in human form, no violence, etc.)
4. Scene description — from deck.json, passed through unchanged
4b. **Ref hint** — when character ref images are loaded, tells model to prioritize refs for appearance
5. `COMPOSITION_GUIDANCE[card_type]` — per-card-type cinematography
6. `COMPOSITION_SUFFIX` — universal no-border, no-text rules

### Generation Provenance

Every generation is logged to `raw/generations.jsonl` (append-only JSONL, 6 fields: card_id, timestamp, model, full_prompt, character_refs, success). Full assembled prompts also saved to `raw/prompts/{card_id}.txt` for quick debugging.

### Selective Character References

Cards include a `characters_in_scene` field in deck.json that controls which character ref images are loaded. `load_reference_images()` filters by this list. Empty list `[]` = no refs loaded (for tradition/connection cards). `null`/absent = load all (backwards compatible).

### Card Type Composition

| Card Type | Subject Position | Open Space |
|-----------|-----------------|------------|
| Anchor | Center-low | Headroom above (for title) |
| Spotlight | Chest-up portrait, center | Headroom above, shadow lower-left |
| Story | Action center-right | Headroom above, shadow lower-left |
| Connection | Upper two-thirds | Simple floor/gradient below |
| Tradition | Center-low, grounded | Golden glow/warm haze above |
| Power Word | Center-low, heroic angle | Bright sky/light above |

Key files: `image_prompts.py` (constants), `generate_images.py` (`build_generation_prompt()`)

---

## schema.py

Data structures and type definitions.

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

```python
parasha = fetch_current_parasha()
parasha.title_en      # "Yitro"
parasha.title_he      # "יִתְרוֹ"
parasha.ref           # "Exodus 18:1-20:23"
parasha.book          # "Exodus"
parasha.border_color  # "#5c2d91"
```

---

## Adding New Functionality

### Add a New Character to Research Database

1. Edit `workflows/research.py`
2. Add entry to `CHARACTER_DATABASE` dict
3. Add visual defaults to `DEFAULT_DESIGNS` dict

### Add a New Parasha to Research Database

1. Edit `workflows/research.py`
2. Add entry to `PARASHA_DATABASE` dict
