# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Image Generation Pipeline v2 — Cleanup & Variants

Deleted dead code, consolidated duplicates, added multi-variant generation.

#### Added
- **`--variants N` flag** for `generate_images.py` — Generates N images per card, named `{card_id}_v{N}.png`. Each variant logged separately in `generations.jsonl`. Selection is manual: pick the winner, rename to `{card_id}.png`, delete the rest.

#### Changed
- **`CHARACTER_LABELS` → dynamic** — Labels now derived from `manifest.json` at runtime via `get_character_label()`. Adding characters to new decks no longer requires Python code changes.
- **`CHARACTER_DESIGNS` consolidated** — Single source of truth in `schema.py` (merged from both `schema.py` and `config.py`). All fields preserved: `name`, `name_he`, `description`, `key_features`, `style_prompt`.

#### Removed
- **Dead generation functions** — `generate_image_imagen()` (~40 lines) and `generate_image_gemini_flash()` (~46 lines) deleted. `--model` flag removed. nano-banana is the only code path.
- **`--backup` flag** — Git is the versioning tool. Backup directory logic removed (`shutil` import, `backup_dir` setup, per-card copy, summary).
- **Dead reference types** — `generate_references.py` stripped to identity-only generation. Removed expression, turnaround, and pose sheet generation (~170 lines).
- **Net reduction:** ~280 lines removed across all files.

---

### Hebrew Nikud & Anchor Spacing Fix

Fixed nikud clipping, anchor card letter-spacing, and story_3 composition conflict.

#### Fixed
- **FitText overflow:** Changed `overflow: hidden` → `overflow: visible` to stop clipping nikud descenders below the baseline.
- **FitText lineHeight:** Increased from `1.1` → `1.3` — Hebrew with nikud needs more vertical space than Latin text.
- **English subtitle spacing:** `mt-1` → `mt-2` on all cards with English text below Hebrew FitText title.
- **Anchor card shuruq visibility:** `letterSpacing: 0.4em` so dots inside letters (shuruq, dagesh) aren't covered by adjacent letters. maxSize bumped to 160, padding reduced to 12.
- **Story 3 thought bubble:** Moved from "above head" (title zone conflict) to center-right at chest height. Added explicit "top 30% must be EMPTY" in prompt. Added `mordechai` to `characters_in_scene` so his ref is loaded for the thought bubble.
- **Ref-first prompting refined:** "pose only" was too aggressive — 2-3 key identity anchors (hat shape, beard style, clothing colors) needed even when refs are loaded.

---

### Export Pipeline & FitText Overhaul

Fixed export viewport mismatch and unified title sizing across all card types.

#### Fixed
- **Export viewport:** Fronts now render at 500x700 CSS with `deviceScaleFactor: 3` (matches design editor). Previously rendered at 1500x2100 CSS @ 1x, making text 3x too small.
- **sync-deck.sh:** Now copies `raw/` images to Card Designer (was missing, causing stale images in exports).
- **Next.js dev indicator:** Disabled via `devIndicators: false` — no more "N" badge in exports.

#### Changed
- **Story cards:** Switched from hardcoded 28px titles to FitText (dynamic scaling). All 6 card types now use FitText for Hebrew titles.
- **FitText sizing:** Increased maxSize and reduced padding across all card types for bolder titles:

| Card Type | maxSize | minSize | padding |
|-----------|---------|---------|---------|
| Anchor | 160 | 80 | 12 |
| Spotlight | 80 | 56 | 21 |
| Story | 72 | 32 | 19 |
| Connection | 72 | 48 | 19 |
| Tradition | 72 | 48 | 19 |
| Power Word | 80 | 56 | 21 |

- **Keywords/emotion badges:** Story and Spotlight cards now use identical left-aligned `text-3xl` / `text-sm` layout (bottom-left).
- **Backs unchanged:** Still render at 1500x2100 CSS @ 1x with print-calibrated font sizes.

---

### Card Back Redesign

Print-calibrated teacher content backs with clearer labels and layout.

#### Changed
- **Font sizes**: Switched from Tailwind classes to explicit pixel values for 300 DPI print (`text-[50px]` header, `text-[58px]` body, `text-[67px]` labels, `text-[75px]` titles)
- **Section labels**: "Say This" → "Teacher's Script", "Do This" → "Act it Out" (🎯→🎭), "Ask This" → "Ask"
- **BackSection**: `large` prop → `grow` prop (flex-1) — Teacher's Script fills available space
- **CardBackFrame**: Thicker border (8→12px), larger rounding (24→32px), icon badges removed from header
- **Hebrew titles** added to spotlight and connection card backs
- **Deck view** now renders both front and back for each card
- **Tint opacity** slightly increased for better section differentiation
- Re-exported all 16 Purim card backs

---

### Ref-First Prompting

When character identity refs are loaded, verbose appearance descriptions in prompts dilute ref fidelity. Simpler prompts = better character consistency.

#### Changed
- **Visual Director agent**: Scene prompts now use ref-first approach — pose/action/emotion only when refs are loaded, full appearance only when no refs available
- **LESSONS_LEARNED**: Replaced "ref + text both needed" with ref-first rules (less text = better fidelity, attention budget, no spatial stage directions)

---

### Prompt Enrichment & Image Regeneration

All 16 Purim cards regenerated with enriched prompts. Two rounds of fixes based on visual review.

#### Added
- **`--backup` flag** for `generate_images.py` — Creates `raw/backup_{timestamp}/` and copies existing images before overwriting via `shutil.copy2`
- **Composition awareness** section in Visual Director — top 25% of frame is text overlay zone, scene prompts must keep it calm

#### Changed
- All 16 Purim `image_prompt` fields enriched with stage directions, specific actions, visual storytelling devices
- Visual Director agent: added per-card-type prompt guidance (spotlight, story, tradition, connection, anchor, power word)
- LESSONS_LEARNED: added sections for connection cards, anchor cards, power word cards, composition awareness, pipeline cross-reference

#### Fixed
- anchor_1: horizontal line from interior architecture → seamless gradient
- story_1: king missing identity ref → added achashverosh to `characters_in_scene`
- story_2: bowing direction, style drift, missing turban → simplified prompt, swapped character positions
- story_3: cluttered thought cloud → simplified to single Mordechai figure
- story_4: missing Haman in banquet scene → complete rewrite with all 3 characters; stripped appearance blocks for better ref fidelity
- connection_1: boy missing kippah → added explicit kippah to scene description
- tradition_1: megillah text facing wrong way → added scroll direction instruction

---

### Image Generation Pipeline v2 — Phase B

Style hero reference for visual consistency across story-world cards.

#### Added
- **Style hero support** — `load_reference_images()` loads `style_hero` from manifest as the first reference image for story-world cards (anchor, spotlight, story, power_word). Provides a visual anchor for art style, color palette, and rendering quality.
- **`--no-hero` flag** — Skip style hero for A/B comparison during testing.
- **`STORY_WORLD_CARDS` constant** — Defines which card types receive the hero reference.

#### Changed
- `load_reference_images()` accepts `card_type` and `no_hero` parameters
- Non-character manifest entries (`style_hero*`) skipped during character ref loading
- Extracted `_load_image_as_part()` helper for shared image loading logic

---

### Image Generation Pipeline v2 — Phase A

Generation provenance, selective character refs, and lean prompts.

#### Added
- **Generation logging** — `raw/generations.jsonl` records every generation attempt (card_id, timestamp, model, full assembled prompt, character refs used, success/failure). Append-only JSONL.
- **Prompt sidecars** — `raw/prompts/{card_id}.txt` saves the full assembled prompt in human-readable form for quick debugging.
- **`characters_in_scene` field** — Each card in deck.json lists which characters are depicted. Controls which reference images are loaded during generation. Empty list `[]` = no refs (tradition/connection cards).
- **Lean prompt hints** — When character ref images are loaded, `build_generation_prompt()` adds a hint telling the model to prioritize reference images for appearance and use text for pose/action only.

#### Changed
- `generate_image_nano_banana()` returns a dict (`{success, prompt}`) instead of a bool
- `load_reference_images()` returns a tuple `(image_parts, loaded_char_keys)` and accepts `characters_in_scene` filter
- `CHARACTER_LABELS` moved to module-level constant
- `build_generation_prompt()` accepts `character_refs_loaded` parameter for ref hints

#### Fixed
- Villain (Haman) appearing in tradition cards — tradition/connection cards now receive zero character refs via `characters_in_scene: []`

---

### Two-World Visual Consistency System

Cards now exist in one of two visual "worlds," each injected automatically by `build_generation_prompt()`:

| World | Card Types | Source |
|-------|-----------|--------|
| **Story World** | anchor, spotlight, story, power_word | `deck.json "story_world"` field (per-deck) |
| **Modern World** | connection, tradition | `MODERN_WORLD_STYLE` constant (global) |

#### Added
- `MODERN_WORLD_STYLE` constant in `image_prompts.py` — Modern Orthodox Jewish community conventions (men in knit kippot/casual clothes, women without head coverings in modest dresses, co-ed colorful classrooms, welcoming shul with classic elements)
- `story_world` field in `deck.json` — per-deck historical/geographic setting for story-world cards
- Purim `story_world`: ancient Persian Empire, city of Shushan

#### Changed
- `build_generation_prompt()` now accepts `story_world` parameter, 5 layers → 6 layers (new world style layer between style anchors and safety rules)
- Cultural context removed from `STYLE_ANCHORS_V2` (now lives in world-specific blocks where it's more targeted)
- Purim `story_2` image prompt updated: added busy public street scene with market stalls and townspeople
- Torah Scholar definition: now outputs `story_world` as part of research
- Visual Director definition: documents two-world system and which card types belong to which world

#### Fixed
- Tradition cards showing girls with kippot (modern world style now explicitly states "girls do NOT wear kippot")
- Inconsistent settings across cards (Persian palace scenes vs generic backgrounds now unified via story_world)
- Story card 2 (Mordechai refusing to bow) now clearly set in public marketplace

---

### Agent Pipeline Refactor

Cleaned up the entire agent system: consistent numbering, complete definitions, no dead code, no phantom references.

#### Added
- Agent definitions for `01-torah-scholar.md`, `02-curriculum-designer.md`, `03-content-writer.md`, `04-hebrew-expert.md` (previously referenced but never written)
- `sync-deck.sh` — copies `decks/{id}/` to `card-designer/content/{id}/` (establishes `decks/` as single source of truth for deck data)

#### Changed
- Agent numbering: `09-card-designer.md` + `09b-designer-agent.md` merged into `07-card-designer.md`
- Agent roster is now 7 agents (01-07), removed aspirational Print Producer (07) and Web Producer (08)
- `VISUAL_SPECS.md` is now the single visual spec doc (absorbed STYLE_GUIDE.md content)
- `src/CLAUDE.md` rewritten to document only active modules
- `CLAUDE.md` updated with correct directory structure, agent references, sync-deck.sh workflow

#### Removed
- `agents/STYLE_GUIDE.md` — duplicate of VISUAL_SPECS.md (80% overlap)
- `agents/definitions/09-card-designer.md` and `09b-designer-agent.md` — replaced by `07-card-designer.md`
- All references to phantom files: `FRAMEWORK.md`, `YEAR_CONTEXT.yaml`

#### Archived (moved to `src/archive/`)
- `card_prompts.py`, `overlay.py`, `card_back_generator.py`, `card_generator.py`, `generate_with_consistency.py`
- `card-designer/scripts/generate_images.py`, `generate_fresh_art.py`, `prepare_hybrid_prompts.py`

---

### Scene-Only Architecture

All system concerns (style, safety, composition, rules) are now layered automatically at generation time. Content creators only write scene descriptions.

- **`generate_images.py`**: `inject_composition_guidance()` → `build_generation_prompt()` — now layers system concerns onto scene prompts (see Two-World System above for current 6-layer architecture)
- **`image_prompts.py`**: All 7 `build_*_v2()` functions rewritten to return **scene-only** descriptions (stripped style, safety, composition sections that are now injected by `build_generation_prompt()`)
- **`card_prompts.py`**: Deprecated — v1 prompt generator that embeds borders/text/layout in prompts. Kept for reference only.
- **`generate_deck.py`**: Full rewrite to v2 card types:
  - `action` → `story`, `thinker` → `connection`
  - Added `tradition` cards via `--holiday` flag
  - v2 field names throughout (emotion_label_en/he, english_key_word, emojis, etc.)
  - Creates `raw/`, `images/`, `references/` directories
  - Version bumped to "2.0"

### Card Title Sizing Consistency

Narrowed FitText min/max ranges so cards of the same type render at consistent sizes.

| Card Type | maxSize | minSize | padding | Notes |
|-----------|---------|---------|---------|-------|
| Spotlight | 96→56 | 40→46 | 32→40 | |
| Tradition | →48 | →38 | →36 | Matched connection card |
| Power Word | →56 | →46 | →40 | Matched spotlight card |
| Anchor | 120→80 | 48→64 | 48 | |
| Connection | 72→48 | 28→38 | 32→36 | |
| Story | — | — | — | Replaced FitText with fixed 28px wrapping |

Additional layout changes:
- **TraditionCard**: Matched connection card layout (position, fonts), removed separator line
- **PowerWordCard**: Matched spotlight layout, removed pill container for English
- **StoryCard**: Fixed 28px wrapping text replaces FitText (multi-word titles wrap instead of overflowing)

### Fixed

- **Connection card title color**: `borderColor` (blue) → `'white'`
- **Anchor card nikud visibility**: `WebkitTextStroke` 1.5px + `paintOrder: stroke fill` + multi-directional glow
- **Story card title overflow**: Story 3 & 4 Hebrew titles no longer overflow
- **Power Word redundant text**: "Hero / Brave One" → "Hero" in deck.json

### Purim Deck

- Rewrote all 16 `image_prompt` fields to pure scene descriptions
- Regenerated all 16 raw images (no borders, no text)
- Old images backed up to `decks/purim/raw-v1-borders/`

---

### Legacy Code Removal

Removed all v1 artifacts — the codebase is now v2-only.

#### `src/schema.py`
- Removed `OverlayZone` enum and `OVERLAY_SPECS` dict (overlay handled by Card Designer)
- Removed `overlay_zone` field from all Front dataclasses
- Removed legacy card classes: `BaseCard`, `AnchorCard`, `SpotlightCard`, `ActionCard`, `ThinkerCard`, `PowerWordCard`
- Removed old `Deck` class (v1.0 with `mitzvah_connection`); replaced with v2.0 `Deck` accepting `CardV2`
- Removed unused `ConnectionQuestion` dataclass (was `ThinkerQuestion`)
- Removed `ACTION`/`THINKER` legacy aliases from `CardType`

#### `src/image_prompts.py`
- Removed `STYLE_ANCHORS` constant (replaced by `STYLE_ANCHORS_V2`)
- Removed `get_overlay_spec()` function
- Removed 6 legacy prompt builders: `build_anchor_prompt`, `build_spotlight_prompt`, `build_action_prompt`, `build_thinker_prompt`, `build_power_word_prompt`, `build_divine_presence_prompt` (~300 lines)

#### `src/__init__.py`
- Complete rewrite: exports only v2 types (`CardV2`, `Deck`, `build_*_v2()`)
- Version `"1.0.0"` → `"2.0.0"`

#### `src/workflows/deck.py`
- Removed `mitzvah_connection` assignment
- Feedback version `"1.0"` → `"2.0"`

#### `src/generate_deck.py`
- Removed "replaces v1" comments

### Code Quality Improvements

#### Error Handling
- `generate_images.py`: Added warning log for silent manifest load failures (was swallowing exceptions)

#### Documentation Reconciliation

All 3 documentation layers (code-level, agent pipeline, project-level) now consistently describe the v2 scene-only architecture.

- **`agents/AGENT_PIPELINE.md`**: Full rewrite — removed `=== EXACT TEXT TO RENDER ===` section, keyword badge placement, Hebrew spelling notes for image rendering. Added scene-only prompt rules, `build_generation_prompt()` documentation, assembly step, and reference to Yitro pipeline example.
- **`agents/definitions/05-visual-director.md`**: Removed old card type ASCII templates (showed text zones baked into images). Replaced with reference to VISUAL_SPECS.md for composition. Simplified YAML output template to scene-only prompts.
- **`agents/STYLE_GUIDE.md`**: Replaced old prompt structure (`=== STYLE ===`, `=== RESTRICTIONS ===`, etc.) with scene-only prompt format and `build_generation_prompt()` documentation.
- **`agents/definitions/06-editor.md`**: Updated image prompt checklist to reflect scene-only approach.
- **`agents/definitions/09-card-designer.md`**: Updated FitText values to match current implementation, removed "Action" card name.
- **`agents/definitions/09b-designer-agent.md`**: Updated typography and layout zone tables with current FitText ranges.
- Removed dead references to `FRAMEWORK.md` and `YEAR_CONTEXT.yaml` from `agents/AGENTS.md`
- Updated `src/CLAUDE.md` CLI documentation to match actual `generate_images.py` flags
- Updated `decks/CLAUDE.md`: consolidated and verified against actual codebase

---

### Major Refactor: Card Designer as Single Source of Truth

**Eliminated double overlays** by separating raw AI-generated images from final composited output.

#### New Architecture
- **`raw/` directory**: AI generates scene-only images (no text) to `decks/{deck}/raw/`
- **Card Designer React**: All text rendering via React/Tailwind components
- **Export to `images/` and `backs/`**: Final print-ready PNGs with text overlay

#### New Components
- `CardBackFrame.tsx`: Shared 5x7 frame for all card backs
- `StoryCardBack.tsx`: Story card teacher content
- `SpotlightCardBack.tsx`: Character card teacher content
- `ConnectionCardBack.tsx`: Discussion card with questions and feeling faces
- `AnchorCardBack.tsx`: Parasha/Holiday intro card teacher content
- `TraditionCardBack.tsx`: Holiday tradition card teacher content
- `PowerWordCardBack.tsx`: Vocabulary card with explanations and examples

#### Updated Components
- `CardFactory.tsx`: Added `side` prop ('front' | 'back') for routing
- `generate_images.py`: Now outputs to `raw/` directory, removed PIL overlay flags
- `export-deck.ts`: Added `--backs`, `--backs-only`, `--fronts-only` flags

#### Deprecated
- `overlay.py`: PIL text overlay - use Card Designer instead
- `card_back_generator.py`: PIL card backs - use Card Designer instead
- `--with-overlay`, `--overlay-only`, `--backs-only` flags in generate_images.py

#### Workflow
```bash
# 1. Generate raw images (no text)
cd src && python generate_images.py ../decks/purim/deck.json

# 2. Export with Card Designer
cd card-designer && npm run export purim -- --backs
```

---

### Added

#### Card Designer Export Pipeline
- **Playwright export script** (`card-designer/scripts/export-deck.ts`): Headless batch export of all cards
  - Auto-starts dev server if not running
  - Exports 1500x2100 PNG (5x7 @ 300 DPI print-ready)
  - Usage: `cd card-designer && npm run export purim`
- **Dedicated export route** (`card-designer/app/export/[deckId]/[cardId]/page.tsx`): Full-resolution single-card rendering
- **Content symlink**: `card-designer/content/purim` → `../../decks/purim` (prevents stale copies)

#### v2 Card Format (Front/Back Separation)
- **Card Back Generator** (`src/card_back_generator.py`): Generates 5x7 printable teacher-facing card backs
- **Text Overlay System** (`src/overlay.py`): Programmatic text overlay for card fronts using PIL/Pillow
- New deck.json schema with `front` and `back` objects per card
- Support for `--with-overlay`, `--overlay-only`, `--backs-only`, `--no-overlay` flags in generate_images.py

#### Character Reference Labeling
- Reference images now include text labels before each image in API payload
- Labels map character keys to friendly names (e.g., "haman" → "Haman (the villain)")
- Final instruction text added after all references: "Use the above character references for visual consistency. Now generate:"

#### Global Image Prompt Rules
- **Anti-noise requirements**: "Clean digital illustration. Absolutely NO grain, film texture, stippling, noise, or analog artifacts."
- **Anatomy requirements**: "All humans have exactly 2 arms, 2 legs, 5 fingers per hand."
- **Jewish school context**: "Boys wearing kippot. Girls wearing modest skirts or dresses (no kippot for girls)."
- **No Hebrew on surfaces**: "Do NOT render any Hebrew letters on walls, signs, books, or any surface - generated Hebrew is always wrong."

#### Purim Deck (First v2 Deck)
- 16 cards with full v2 structure
- Character references: Esther, Mordechai, Haman, King Achashverosh
- Connection cards with emoji strips rendered in-image (not overlaid)

### Changed

#### Agent Workflow
- **Card Designer** now positioned as Agent 5b (between Visual Director and Editor)
- Workflow diagram updated to show Card Designer as alternative to PIL-based Text Overlay tools

#### ConnectionCard.tsx
- Titles now use dynamic `card.title_he` / `card.title_en` instead of hardcoded "חִבּוּר" / "CONNECTION"

#### Image Prompt Engineering
- Removed all "overlay" language from prompts (was confusing the model into creating gradients)
- Connection card emojis now rendered by AI model in bottom 15% strip rather than programmatic overlay
- Power Word cards now feature story-relevant heroes (e.g., Esther for Purim) instead of generic children
- Updated STYLE_ANCHORS_V2 with cultural context section

#### Documentation Updates
- `CLAUDE.md`: Added v2 card format documentation, character consistency workflow
- `src/CLAUDE.md`: Added overlay.py and card_back_generator.py module docs
- `decks/CLAUDE.md`: Added v2 deck structure documentation
- `agents/CARD_SPECS.md`: Added v2 JSON schema specifications
- `agents/VISUAL_SPECS.md`: Added composition zone guidelines

### Fixed

- Character reference images now properly labeled so model knows which character each image represents
- Removed Muslim-appearing children from classroom scenes (now explicitly Jewish school context)
- Fixed anatomy issues (e.g., king with 3 arms) by adding explicit anatomy requirements
- Fixed villain appearing in celebration scenes (tradition_3: Haman removed from mishloach manot scene)
- Removed image noise/grain artifacts through anti-noise prompt rules

### Technical Details

#### generate_images.py Changes
```python
# New: Character label mapping
character_labels = {
    "esther": "Esther (Queen Esther)",
    "mordechai": "Mordechai",
    "haman": "Haman (the villain)",
    "achashverosh": "King Achashverosh (the king)",
    ...
}

# New: Labeled reference image parts
image_parts.append({"text": f"Character reference for {label}:"})
image_parts.append({"inlineData": {"mimeType": "image/png", "data": image_data}})
image_parts.append({"text": "Use the above character references for visual consistency. Now generate:"})
```

#### image_prompts.py Changes
```python
STYLE_ANCHORS_V2 = """
...
CULTURAL CONTEXT:
- This is for a JEWISH school (preschool/kindergarten ages 4-6)
- Boys wear kippot (head coverings)
- Girls wear modest skirts or dresses (girls do NOT wear kippot)
- Do NOT put any Hebrew letters or text on walls, posters, or signs

TECHNICAL REQUIREMENTS:
- CRITICAL: Clean digital illustration. Absolutely NO grain, film texture, stippling, noise
- CRITICAL ANATOMY: All humans must have exactly 2 arms (one left, one right), 2 legs, 5 fingers per hand
...
"""
```
