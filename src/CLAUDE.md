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
| `sefaria_client.py` | Sefaria API: current parasha, plus the `research/{parasha}.yaml` verse cache |
| `character_library.py` | Reads the shared `characters/{key}/character.yaml` library (single source of truth for characters) |
| `series.py` | Loads and validates `series.yaml` (the year plan) |
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

Run from `src/` (the old `workflows.py` script became the `workflows/` package):

```bash
# Character creation
python -m workflows character miriam --deck ../decks/beshalach --generate

# Deck creation
python -m workflows deck Beshalach --output ../decks/beshalach

# Research only
python -m workflows research character moses
python -m workflows research parasha yitro

# List available data
python -m workflows list characters
python -m workflows list parshiyot
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

Generates card images using Gemini API. Default model is Nano Banana 2 (`gemini-3.1-flash-image`); override with `GEMINI_IMAGE_MODEL` in `.env` (e.g. `gemini-3-pro-image`). Set resolution with `--size 512|1K|2K|4K` (default 2K; 3:4 at 2K = 1792x2400). The API returns JPEG, which `save_image_as_png()` re-encodes so `raw/*.png` files are real PNGs. `generate_references.py` uses the same helper and also accepts `--size`.

```bash
python generate_images.py ../decks/yitro/deck.json              # Generate all
python generate_images.py ../decks/yitro/deck.json --card spotlight_1  # Single card
python generate_images.py ../decks/yitro/deck.json --skip-existing     # Skip existing
python generate_images.py ../decks/yitro/deck.json --no-refs           # Without character refs
python generate_images.py ../decks/yitro/deck.json --variants 3        # Generate 3 variants per card
python generate_images.py ../decks/yitro/deck.json --card story_1 --variants 3  # 3 variants of one card
```

### Reference Image Integration

1. For each key in the card's `characters_in_scene`, looks up `characters/{key}/identity.png` in the shared library first
2. Falls back to the deck's `references/manifest.json` and logs a warning when a character isn't in the library
3. Sends at most `MAX_CHARACTER_REFS = 4` character images (Nano Banana 2 limit). More than 4 logs an error to `project.log` and only the first 4 are sent
4. Base64-encodes identity PNGs and passes them alongside the text prompt
5. Labels come from the library's `name_en` (else manifest `label`, else the key) via `get_character_label()`
6. The style hero still comes from the deck manifest

### Variant Generation

`--variants N` generates N images per card, named `{card_id}_v{N}.png`. Each variant is logged separately in `generations.jsonl`. Selection workflow: pick the winner from `raw/`, rename to `{card_id}.png`, delete variants.

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

Every generation is logged to `raw/generations.jsonl` (append-only JSONL, 7 fields: card_id, timestamp, model, image_size, full_prompt, character_refs, success). Full assembled prompts also saved to `raw/prompts/{card_id}.txt` for quick debugging.

### Selective Character References

Cards include a `characters_in_scene` field in deck.json that controls which character ref images are loaded. `load_reference_images()` filters by this list. Empty list `[]` = no refs loaded (for tradition/connection cards). `null`/absent = load all (backwards compatible).

### Style Hero Reference

If `references/manifest.json` contains a `style_hero` entry, its image is loaded as the **first** reference for all story-world cards (anchor, spotlight, story, power_word). The hero provides a visual anchor for art style, color palette, and rendering quality. Modern-world cards (connection, tradition) skip the hero — they use `MODERN_WORLD_STYLE` text instead.

```bash
# Generate with hero (default when manifest has style_hero)
python generate_images.py ../decks/purim/deck.json

# Skip hero for A/B comparison
python generate_images.py ../decks/purim/deck.json --no-hero
```

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
- `CHARACTER_DESIGNS` - Built at import time from `characters/` (kept so older helpers work; edit the yaml, not this)
- `IMAGE_SAFETY_RULES` - Content restrictions
- `PRINT_SPECS` - Print specifications
- `LAYOUT_ZONES` - Card layout percentages

---

## sefaria_client.py

Sefaria API integration for Torah text and parasha data.

```python
parasha = fetch_current_parasha()
parasha.title_en      # "Yitro"
parasha.ref           # "Exodus 18:1-20:23"
parasha.border_color  # "#5c2d91"
```

### Research cache

`fetch_parasha_research(parasha, verses=None, commentaries=None)` fetches key verses (EN + HE) and
commentary pointers from Sefaria's v3 texts API and writes `research/{parasha}.yaml`. If the file
already exists (and is complete) it is reused, not refetched. Verses and commentaries default to
`RESEARCH_PLANS[parasha]`.

```bash
python3 sefaria_client.py research bereshit            # uses the cache if present
python3 sefaria_client.py research bereshit --refresh  # refetch
```

- English: Metsudah Chumash (CC-BY). Hebrew: Tanach with Nikkud (Public Domain, vowels without cantillation).
- HTML tags and footnotes are stripped (`clean_text()`). Commentary text is cut at 1500 characters.
- Network failure logs a warning and continues. A partly fetched cache is marked `incomplete: true` and is refetched next time; if nothing is fetched, no file is written.

---

## character_library.py

```python
from character_library import load_character, list_characters, identity_path, visual_anchor_text
load_character("abraham")["key"]      # "avraham" (aliases resolve)
identity_path("adam")                 # None until the identity sheet exists
visual_anchor_text("mordechai")       # "MORDECHAI: older man...; striped cream-and-brown cloth headwrap; ..."
```

Also `validate_character(dict)` and `legacy_design(key)` (feeds `schema.CHARACTER_DESIGNS`).
The old `CHARACTER_DATABASE` (workflows/research.py) and `DEFAULT_DESIGNS` (workflows/character.py)
were removed; the workflows read the library instead. See `characters/README.md`.

---

## series.py

`series.yaml` (repo root) lists every deck: 4 fall holidays, 54 parshiyot by book, and 8 more
holidays placed with `before: <parasha id>`.

```bash
python3 series.py   # summary + validation
```

`year_order()` gives the teaching order. `validate_series()` checks unique ids, valid status/type,
middah from the `docs/policies/values-spine.md` table (or `TBD`), power word shape, and that no middah
repeats within 4 consecutive filled decks. `missing_characters()` lists character keys that still
need a `characters/` entry.

---

## Adding New Functionality

### Add a New Character

1. Create `characters/{key}/character.yaml` (copy an existing one; see `characters/README.md`)
2. Run `python3 -m pytest tests -q` to validate it

### Add a New Parasha to Research Database

1. Edit `workflows/research.py`
2. Add entry to `PARASHA_DATABASE` dict
