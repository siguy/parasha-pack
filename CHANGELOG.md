# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Agent Pipeline v3 (Deck v3 Phase 4)

#### Added
- **New agents:** `00-series-planner` (owns `series.yaml`: middah, power word, review words, characters, sensitivities, holiday placement), `02b-sensitivity-reviewer` (★ checkpoint: per-card ok / reframe / guide-only / skip verdicts and scripted "if they ask" answers), `05b-image-qa` (★ vision rubric, flag-only, draft picks, contact sheets).
- **Rubrics:** `agents/rubrics/image_qa.yaml` (11 criteria scored 0–2; pass = no 0s and ≥16/22) and `agents/rubrics/editor.yaml` (content 30, Torah accuracy 25, Hebrew 20, art 15, print 10; pass ≥80% with no blocking 0s or critical issues).
- **Per-step schemas** `schemas/pipeline/{00-series,01-research,02-structure,02b-sensitivity,03-content,05-visual,05b-image-qa,06-editor}.schema.json`. 03 reuses the `back`/`guide` definitions from `deck.v3.schema.json`.
- **`src/assemble_deck.py`**: merges `decks/{id}/pipeline/*.yaml` into `deck.json` (structure from 02, content from 03, prompts from 05, picks from 05b), after schema and cross-file checks (D1 card count, approved 02b checkpoint, minutes/core owned by 02, library characters, Image QA totals). Runs `src/validate_deck.py` when it exists.
- **`src/contact_sheet.py`**: `make_contact_sheet(paths, labels, out_path, cols)` for Image QA and identity reviews.
- Tests: `tests/test_assemble_deck.py` (fixture `tests/fixtures/pipeline_min/`), `tests/test_contact_sheet.py`. `jsonschema` added to requirements.txt.

#### Changed
- **01 Torah Scholar** reads `research/{parasha}.yaml` (fetches it if missing), cites a verse for every claim, labels pshat vs midrash ("Our Sages teach…"), flags hard passages.
- **02 Curriculum Designer**: D1 (10 standard / 12 holiday, home card included), one focal incident, ★core cards, 5-day `week_plan`, `story_world_setting`.
- **03 Content Writer** now writes English **and** Hebrew (v3 backs, guide blocks, home card; nikud, gender agreement, plural second person, CAPS stress). `04-hebrew-expert.md` removed.
- **05 Visual Director** updated for styling v2 (plates, `continuity_ref`, library keys ≤4, natural title zone, central 90%, villain posture, modern diversity, Hashem only as light, draft → final).
- **06 Editor** is a scored rubric; it must run the validator and drafts `feedback.json`.
- `07-card-designer.md` moved to `agents/tools/card-designer.md` (sync → export letter / `--format 5x7` / `--pdf` → `scripts/sync_to_hub.py`).
- Docs: `agents/AGENTS.md`, `AGENT_PIPELINE.md`, `README.md` rewritten for v3; `CARD_SPECS.md` card counts (10/12) and week flow; `LESSONS_LEARNED.md` overnight lessons; root and `src/` CLAUDE.md.

### Deck Validator, Hebrew Gender Check, Export Overflow Guard (Phase 2)

#### Added
- **`src/validate_deck.py`** — checks a v3 deck: JSON Schema, word budgets (objective ≤10, say ≤50 spoken words, cues ≤25, ask ≤2×12), card count and types (10 standard / 12 holiday), characters vs. the library (≤4 per card, named characters listed), nikud, unpointed/pointed match, **Hebrew grammatical gender vs. character gender**, deck-order words in transitions, non-scene prompt terms, God depiction, guide page numbers. `--strict`, `--json`; exit 1 on errors; failures logged to `project.log`.
- **`src/hebrew_gender.yaml`** — 12 masculine/feminine pairs (אַמִּיץ/אַמִּיצָה …) plus fallback character genders.
- **`guide_layout.yaml`** — fixed letter-size teacher-guide page map for standard and holiday decks (D5).
- **Export guard** in `card-designer/scripts/export-deck.ts` — runs the validator first (`--skip-validate`), then fails the export on any `.pp-card .body` overflow or text outside the safe zone, listing card/side/format/px (`--allow-overflow`).
- Schema: optional deck `story_world_setting`, card `style_plate` and `continuity_ref`.
- Tests: `tests/test_validate_deck.py` + fixtures (valid deck, broken deck, tiny character library); `card-designer/lib/markup.test.ts` (`npm test`, Node's built-in runner via tsx).
- `jsonschema` and `PyYAML` in `requirements.txt`.

#### Changed
- 5×7 front titles start at 5% (were 3.5%): the guard found them 2px above the safe line. `decks/bereshit/print/bereshit-5x7.pdf` re-exported.
- review-site deck registry moved to `decks/registry.json` (where `app.js` looks), paths relative to `decks/`, Bereshit added.
- review-site `/api/resume` returns a clear "not supported" error instead of launching the nonexistent `workflows deck --auto --resume`.

#### Removed
- `decks/purim/raw-v1-borders/`, `*_pre_hero.png` (decks + card-designer content), `decks/archive/yitro/deck_v1_backup.json`, `decks/archive/approval_stats.yaml`.

---

### Styling System v2: Style Plates, Labeled References, Draft → Final (Deck v3 Phase 5.0–5.3, 3.2)

The art style is unchanged (Simon: keep the Purim look). These changes are about consistency and process.

#### Added
- **Series style plates** in `style/plates/` (landscape, interior, object, classroom, made from the Purim art and approved by Simon), with alternates and `style/README.md`.
- **`style/style_config.yaml`**: one source for the style anchors (old `STYLE_ANCHORS_V2`, word for word), safety rules (moved from `schema.IMAGE_SAFETY_RULES`), modern-world rules, composition per card type, plate mapping, limits (4 character refs, 3 style refs) and `prompt_version: "v2.0"`. Loader: `src/style_config.py`.
- **`assemble_references()`**: reference images go in a fixed, labeled order (style plates → draft → `continuity_ref` → character identity sheets, max 4), and the prompt opens with a `=== REFERENCE IMAGES ===` block naming each one. Big references are shrunk to 1536px JPEG.
- **Locked character anchors** from `characters/{key}/character.yaml` are added to the prompt automatically.
- **Deck palette**: `palette` (5 hex colors) in deck.json adds a "Deck palette accents" line.
- **Draft → final**: `--draft` (1K, 2 variants, `raw/drafts/{card_id}_d{n}.png`) and `--final --from-draft` (2K, draft passed as a composition reference).
- **Spend ledger** (`src/spend_ledger.py`): with `PP_SPEND_LEDGER` set, every image call is recorded; with `PP_BUDGET_USD`, calls are refused once the total reaches the budget. Prices: `config.IMAGE_PRICE_USD`.
- **Identity sheets in the library**: `generate_references.py --character {key} --versions 2` writes `characters/{key}/identity_vN.png` (turnaround + expression row, no text, style plate as Image 1); `--accept vN` promotes one to `identity.png` and moves the rest to `alternates/`.
- **Adam and Chava identity sheets** (4 calls at 2K, $0.40). The chosen sheets are v2; v1 is in `alternates/`.
- Tests: `tests/test_styling_v2.py`, `tests/test_spend_ledger.py`, `tests/test_generate_references.py`.

#### Changed
- Composition (plan 5.2): the "darker lower-left" lines are gone. In their place: a simple ground plane, a natural title area at the top ("no hard band or border", with no percentages), key subjects in the central 90% of the width, and at most 5 figures in focus.
- Modern world now spells out:
  - a named diverse Jewish mix: Ashkenazi, Sephardi/Mizrahi and Ethiopian
  - every boy wears a kippah; girls never do
  - a megillah is drawn without twin rollers
- Safety now adds a villain-posture rule: no pointing, no snarling; sulky or comic instead.
- `generations.jsonl` gains `prompt_version`, `references` and `output_file`.
- The per-deck `style_hero.png` is now only a fallback for when no plates exist.
- `workflows/character.py` now writes identity sheets to `characters/{key}/`.
- Esther's identity sheet had a caption strip, now cropped off. The original is in `characters/esther/alternates/`.

### Shared Character Library, Year Plan, Sefaria Research Cache (Deck v3 Phase 3)

#### Added
- **`characters/` library** — one folder per character with `character.yaml` (gender, role, canonical, version, locked `visual_anchors`, research notes) and `identity.png`. Migrated Moses, Yitro, Miriam (with expressions/poses/turnaround sheets), Esther, Mordechai, Haman, Achashverosh. Adam and Chava have locked modest-tunic anchors but no identity sheet yet. Avraham, Sarah and Pharaoh are drafts (`canonical: false`).
- **`src/character_library.py`** — `load_character`, `list_characters`, `identity_path`, `visual_anchor_text`, `validate_character`, alias map (`abraham` → `avraham`, `moshe` → `moses`).
- **`series.yaml`** — all 66 decks (54 parshiyot by book + 12 holidays). Filled: Rosh Hashanah, Yom Kippur, Sukkot, Simchat Torah, Bereshit, Noach, Lech Lecha, Purim. **`src/series.py`** validates ids, statuses, middot (read from `docs/policies/values-spine.md`) and the no-repeat-within-4 rule.
- **Sefaria research cache** — `sefaria_client.fetch_parasha_research()` writes `research/{parasha}.yaml` (EN Metsudah CC-BY, HE Tanach with Nikkud PD). `research/bereshit.yaml` holds 10 key verse ranges plus Rashi 1:1, Kohelet Rabbah 7:13 and a Sanhedrin 37a pointer.
- `python -m workflows ...` entry point (the old `python workflows.py` stopped working when it became a package).
- PyYAML in `requirements.txt`. Tests: `tests/test_character_library.py`, `tests/test_series.py`, `tests/test_sefaria_research.py`.

#### Changed
- **`load_reference_images()`** looks up each character in `characters/` first, falls back to the deck manifest with a warning, and sends at most 4 character refs (extras logged as an error).
- **Retired duplicate character data** — `CHARACTER_DATABASE` (workflows/research.py) and `DEFAULT_DESIGNS` (workflows/character.py) removed; workflows read the library. `schema.CHARACTER_DESIGNS` is now built from the library (the `israelites` group entry was dropped).
- Docs: CLAUDE.md, src/CLAUDE.md, agents/VISUAL_SPECS.md, AGENT_PIPELINE.md, 05-visual-director.md, 07-card-designer.md point at `characters/`.

### Deck v3 — Letter-Size Cards, Single CardBack, Duplex PDF Export (Phase 1)

#### Added
- **`schemas/deck.v3.schema.json`** — v3 deck format: deck `value`, `palette`, `web_theme`, `week_plan`; each card has a `back` (objective, say with `**bold**`/`[cue]` markup, ask with types, hebrew, minutes, core, transition, guide_ref, plus trio/faces/home extras) and a `guide` (pshat, sages, hard questions, adapt, extend, tip). No field aliases.
- **`src/migrate_v2_to_v3.py`** — mechanical v2 → v3 migration (rewrites in place, lists every field it could not map). Run on Purim and Terumah; both are over the v3 word budgets until rewritten.
- **`decks/bereshit/deck.json`** — first v3 deck (10 cards incl. home card), content from `docs/mockups/bereshit-v3.html`. Guide fields and image prompts are TODO stubs.
- **`card-designer/print_formats.json`** — `letter` (default, 8.5×11, 0.3" margin) and `5x7` (5.25×7.25 with 0.125" bleed, 0.25" safe zone).
- **Export `--format letter|5x7` and `--pdf`** — duplex PDF (front1, back1, front2…) to `decks/<id>/print/<id>-<format>.pdf` via Playwright `page.pdf()`; PNGs at 300 DPI.
- **`/print/[deckId]`** page (one sheet per page) used by both PDF and PNG export.
- SVG type icons and feeling faces; drawn home-card front; palette placeholder for cards without art.

#### Changed
- **One `CardBack.tsx` and one `CardFront.tsx`** replace the 12 per-type components; per-type differences live in `lib/cardTypes.ts`. v3 palette (AA contrast; Tradition is now teal).
- All card sizes in container units (`cqw`) so one layout serves letter, 5×7 and screen.
- Card text is never clipped (`overflow-hidden` removed); over-budget backs spill visibly.
- `types/card.ts` / `lib/api.ts` read v3 only; the home page lists decks from `content/` (no hardcoded `terumah`).
- `sync-deck.sh` uses `rsync -a --delete` for `raw/` and `references/` and runs from any directory.
- Title shadows on fronts have no blur (blurred shadows print as black boxes in macOS Preview).

#### Removed
- v2-only design editor (`app/design/*`, `components/editor/*`, `app/api/config`, `layout_settings.json`), `FitText`, `ExportControls`, `ScaledBack`, `CardBackFrame`, `BackSection`, `app/export/*`.

---

### Card Front Gradient & FitText Overhaul

Standardized title readability gradients, fixed FitText measurement for letter-spacing, and cleaned up export pipeline.

#### Added
- **ScaledBack component** (`card-designer/components/layout/ScaledBack.tsx`) — Responsive wrapper that scales 1500x2100 back cards to fit any container width using ResizeObserver + CSS transform.

#### Changed
- **Title gradient standardized** — All 6 card types now use `h-44 bg-gradient-to-b from-black/50 to-transparent` at the top for title readability. Previously inconsistent (Anchor had none, others ranged from h-24/black40 to h-40/black60).
- **PowerWord title matched to Tradition** — Position `top-3`, FitText maxSize 72, minSize 48, padding 19, English subtitle `text-sm` (was top-[5%], 80/56/21, text-xl).
- **Anchor card title tuning** — letterSpacing 0.4em → 0.2em, padding 12 → 10, added `scale(1.25)` wrapper for larger title presence.

#### Fixed
- **FitText letter-spacing awareness** — Canvas measurement now accounts for CSS `letter-spacing` (em and px units). Previously ignored it, causing text to overflow when letterSpacing was set.
- **FitText soft minSize** — Removed hard minSize floor that caused overflow on long titles. Now uses absolute floor of 12px, letting text shrink as far as needed to fit.
- **Export dev overlay artifact** — Next.js error overlay ("1 issue" badge) captured in Playwright screenshots. Fixed by injecting CSS to hide `nextjs-portal` and related elements before screenshot.

---

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
