# Source Code Documentation

Python modules for generating and managing Parasha Pack card decks.

## Module Overview

| Module | Purpose |
|--------|---------|
| `workflows/` | High-level reusable workflows for character/deck creation (CLI, research, models) |
| `generate_deck.py` | Create new deck templates (story, connection, tradition card types) |
| `generate_images.py` | Generate raw card images to `raw/`; assembles system prompt layers via `build_generation_prompt()` |
| `generate_references.py` | Generate identity sheet versions into `characters/{key}/` and `--accept` one |
| `style_config.py` | Loads `style/style_config.yaml` (style text, safety rules, composition, plates, limits, `prompt_version`) |
| `spend_ledger.py` | Records every image API call and refuses calls past the budget (`PP_SPEND_LEDGER`, `PP_BUDGET_USD`) |
| `image_prompts.py` | Exposes the style constants read from `style/style_config.yaml` + scene-only `build_*_v2()` templates |
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
workflow.generate_references()   # -> characters/{key}/identity_v1.png, identity_v2.png (then --accept vN)
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
python generate_images.py ../decks/yitro/deck.json --card story_1 --draft       # 1K x2 -> raw/drafts/story_1_d1.png, _d2.png
python generate_images.py ../decks/yitro/deck.json --final --from-draft ../decks/yitro/raw/drafts/story_1_d2.png  # 2K final
```

### Draft → final

`--draft` makes cheap 1K drafts (default 2 variants) in `raw/drafts/{card_id}_d{n}.png` and does not touch `image_path`. `--final --from-draft <file>` makes the 2K final at `raw/{card_id}.png` (card id read from the file name) and passes the chosen draft as a reference labeled "re-render this exact composition at full detail in the same style". No flag = 2K single image as before.

### Spend ledger

`generate_image_nano_banana()` (used by both scripts) writes one line per real call to `$PP_SPEND_LEDGER` (`ts, branch, purpose, size, usd`; prices in `config.IMAGE_PRICE_USD`; failed calls are logged at $0 with a note). If `PP_BUDGET_USD` is set and the ledger total is at or above it, the call is refused before any network request and `{"refused": True}` is returned.

### Reference Image Integration

`assemble_references()` builds the reference list in a **fixed, labeled order**:

1. **Style plates** from `style/plates/` (1–2, max 3): `card.style_plate` override, else `plate_mapping` in `style_config.yaml` (connection/tradition → classroom, anchor/power_word → object, spotlight/story → deck `story_world_setting`: outdoor → landscape, indoor → interior, default landscape). The deck's `references/style_hero.png` is only a fallback when no plates exist.
2. **Draft composition** (only `--final --from-draft`).
3. **Continuity reference** — `card.continuity_ref`, a card_id (→ `raw/{id}.png`) or a path relative to the deck folder.
4. **Character identity sheets** — each key in `characters_in_scene`, library first, deck manifest fallback with a warning; at most 4 (`limits.max_character_refs`), extras dropped with an error in `project.log`.

Each image is preceded by an `Image N = <label>:` text part, and the prompt starts with a matching `=== REFERENCE IMAGES ===` block (e.g. "Image 3 = Adam identity sheet — match face, hair, clothing exactly"). Images over 1536px are shrunk to JPEG before sending (keeps requests under the 20 MB limit). `--no-hero` skips the plates; `--no-refs` sends no references (except an explicit `--from-draft`). `load_reference_images()` is kept as a thin wrapper for older callers.

### Variant Generation

`--variants N` generates N images per card, named `{card_id}_v{N}.png`. Each variant is logged separately in `generations.jsonl`. Selection workflow: pick the winner from `raw/`, rename to `{card_id}.png`, delete variants.

---

## generate_references.py

Makes identity sheets in the shared library from the character's locked `visual_anchors`: a 3-angle turnaround (front, 3/4, side) plus a row of 4 expressions (happy, curious, caring, surprised), plain light background, no text, 16:9, with a style plate (default `landscape`) as Image 1.

```bash
python generate_references.py --character adam --versions 2   # -> characters/adam/identity_v1.png, identity_v2.png
python generate_references.py --character adam --accept v2     # -> identity.png; others to alternates/; updates character.yaml
```

Version numbers never repeat (alternates are counted). The exact prompt is saved as `characters/{key}/identity_prompt.txt`. The character workflow (`workflows/character.py`) calls `generate_identity_versions()` too.

---

## Prompt Assembly System

`build_generation_prompt()` in `generate_images.py` assembles all system layers at generation time:

All text comes from `style/style_config.yaml` (one source shared with the Visual Director and Image QA).

0. **Reference images** — numbered labels of every reference image, in send order
1. `STYLE_ANCHORS_V2` — children's illustration style, anatomy rules (unchanged Purim look)
2. **World style** — `MODERN_WORLD_STYLE` for connection/tradition cards (modern Orthodox community: named diverse mix, every boy in a kippah, girls never, megillah without twin rollers), or `story_world` from deck.json for all other cards. Adds `Deck palette accents: …` when deck.json has `palette`.
3. `SAFETY_PROMPT` — content restrictions (no God in human form, villains sulky/comic not scary, etc.)
4. Scene description — from deck.json, passed through unchanged
4a. **Character anchors** — `visual_anchor_text(key)` for each key in `characters_in_scene`, added automatically
4b. **Ref hint** — when character ref images are loaded, tells model to prioritize refs for appearance
5. `COMPOSITION_GUIDANCE[card_type]` — per-card-type cinematography + natural title area + central 90% + max 5 figures + simple ground plane
6. `COMPOSITION_SUFFIX` — universal no-border, no-text rules

### Generation Provenance

Every generation is logged to `raw/generations.jsonl` (append-only JSONL: card_id, timestamp, model, image_size, `prompt_version` (from style_config.yaml, now "v2.0"), full_prompt, character_refs, `references` (label + path of each reference image, in order), output_file, success). Full assembled prompts also saved to `raw/prompts/{card_id}.txt` for quick debugging.

### Selective Character References

Cards include a `characters_in_scene` field in deck.json that controls which character ref images are loaded. `load_reference_images()` filters by this list. Empty list `[]` = no refs loaded (for tradition/connection cards). `null`/absent = load all (backwards compatible).

### Style Plates (replace the per-deck style hero)

See `style/README.md`. `--no-hero` turns the plates off for A/B comparison.

### Card Type Composition

| Card Type | Subject Position | Open Space |
|-----------|-----------------|------------|
| Anchor | Center-low | Headroom above (for title) |
| Spotlight | Chest-up portrait, center | Headroom above, simple ground plane |
| Story | Action center-right | Headroom above, simple ground plane |
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
- `IMAGE_SAFETY_RULES` - Content restrictions (read from `style/style_config.yaml`)
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
