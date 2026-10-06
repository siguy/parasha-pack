# Parasha Pack - Claude Project Documentation

Educational Torah portion card decks for preschool/kindergarten (ages 4-6).

## Project Overview

This project creates illustrated card decks for each weekly Torah portion (parasha) and holiday.
A standard deck has **10 cards**, a holiday deck **12** (both include the home card). Each card has
a picture front and a teacher back (SAY / ASK / Hebrew). Decks also get printable extras and a
letter-size teacher guide booklet. The deck format is **v3** (`schemas/deck.v3.schema.json`).

## Directory Structure

```
parasha-pack/
├── CLAUDE.md              # This file - project overview
├── FOR_SIMON.md           # Plain-language learning doc: how and why this was built
├── series.yaml            # Year plan: 54 parshiyot + 12 holidays, middah per deck
├── guide_layout.yaml      # Fixed teacher-guide page map (card → "Guide p.N")
├── characters/            # Shared character library: {key}/character.yaml + identity.png
├── style/                 # style_config.yaml + style plates (see style/README.md)
├── research/              # Sefaria research cache: {parasha}.yaml (key verses EN/HE)
├── schemas/               # deck.v3, extras, and one schema per pipeline step (pipeline/)
├── agents/                # Agent system documentation (see agents/AGENTS.md)
│   ├── AGENTS.md          # Agent roster, checkpoints, workflow
│   ├── AGENT_PIPELINE.md  # Files, commands, assemble step, budgets
│   ├── CARD_SPECS.md      # Card types, back fields, word budgets
│   ├── VISUAL_SPECS.md    # Art style, characters, safety rules
│   ├── LESSONS_LEARNED.md # Patterns and gotchas
│   ├── definitions/       # Agent specs (00, 01, 02, 02b, 03, 05, 05b, 06)
│   ├── tools/             # card-designer.md (sync, export, hub sync)
│   └── rubrics/           # image_qa.yaml, editor.yaml
├── src/                   # Python source code (see src/CLAUDE.md)
│   └── archive/           # Deprecated v1 code (do not use)
├── scripts/               # compress_pdf.py, sync_to_hub.py
├── card-designer/         # Next.js app: renders fronts/backs, exports PNG + PDF
├── templates/             # Jinja2 HTML for extras, guide booklet, pilot forms
├── items/shared/          # Reusable item art for extras (color, line, cutout)
├── decks/                 # Deck data and images (see decks/CLAUDE.md)
│   ├── bereshit/          # Active deck (v3, reference example, with extras + guide)
│   ├── purim/             # v3 holiday deck (12 cards)
│   └── archive/           # Older decks (beshalach, mishpatim, terumah, tetzaveh, yitro)
├── docs/                  # extras.md, policies/, pilot/, plans/, mockups/
├── review-site/           # Web review interface (still reads v2 fields)
├── tests/                 # pytest suite
├── sync-deck.sh           # Copy a deck into card-designer/content/
├── requirements.txt       # Python dependencies
└── README.md              # User-facing documentation + quick start
```

## Key Workflows

### 1. Create a New Deck (pipeline v3)

Decks are written by 8 agent roles (all played by Claude), each writing one YAML file in
`decks/{id}/pipeline/`, then merged by a script. No hand-editing of deck.json.

```
00-series → 01-research → 02-structure → 02b-sensitivity ★ → 03-content
  → assemble → 05-visual → assemble → drafts → 05b-image-qa ★ → finals → assemble → 06-editor
```

```bash
python3 src/assemble_deck.py decks/{id}            # merge pipeline/*.yaml → deck.json, then validate
python3 src/assemble_deck.py decks/{id} --dry-run  # check only
```

Full commands: [agents/AGENT_PIPELINE.md](agents/AGENT_PIPELINE.md). `decks/bereshit/pipeline/` is the
worked example. (`python -m workflows deck` and `src/generate_deck.py` still write the old **v2**
template; don't use them for new decks.)

### 2. Create a New Character

```bash
# 1. Write characters/{key}/character.yaml (copy one; identity: null, canonical: false)
cd src
python generate_references.py --character miriam --versions 2   # identity_v1.png, identity_v2.png
python generate_references.py --character miriam --accept v2    # → identity.png, others → alternates/
```

**Character Review Checkpoint:** Simon picks between 2+ versions before any card uses the character.
Then set `canonical: true`. See `characters/README.md`.

### 3. Generate Card Images

```bash
cd src
python generate_images.py ../decks/bereshit/deck.json --card story_1 --draft     # 2 drafts at 1K
python generate_images.py ../decks/bereshit/deck.json --final --from-draft ../decks/bereshit/raw/drafts/story_1_d2.png  # 2K final
```

Always pass `--card` (or `--final`) so the home card, which has no art, is not generated.

### 4. Export Final Cards with Card Designer

```bash
./sync-deck.sh bereshit                                # copy deck.json + raw/ into card-designer/content/
cd card-designer
npm run export bereshit -- --backs --pdf               # letter (default): PNG fronts + backs + duplex PDF
npm run export bereshit -- --format 5x7 --backs --pdf  # optional 5x7 vendor print
```

The export first runs the **deck validator**, then an **overflow guard** that fails if any back's
text doesn't fit or any text sits outside the safe zone (`--skip-validate`, `--allow-overflow` to
bypass). PDFs are then shrunk by `scripts/compress_pdf.py` (`--no-compress` to skip).

Output:
- `decks/{id}/images/{card_id}.png` - card fronts (letter: 2375x3125 @ 300 DPI; 5x7 in `images/5x7/`, 1500x2100)
- `decks/{id}/backs/{card_id}_back.png` - teacher backs (same sizes)
- `decks/{id}/print/{id}-letter.pdf` - duplex PDF: front1, back1, front2… (flip on long edge)
- `decks/{id}/print/{id}-5x7.pdf` - vendor PDF with bleed

Everything renders from `/print/{deckId}?format=…`, one sheet per page at the exact paper size from
`card-designer/print_formats.json`. The Card Designer only reads **v3** decks; convert old ones with
`python src/migrate_v2_to_v3.py decks/{id}/deck.json`.

### 5. Extras and Teacher Guide

```bash
cd src
python generate_items.py ../decks/bereshit        # item art (color, line, cutout)
python coloring.py ../decks/bereshit              # story line art for coloring pages
python generate_activities.py ../decks/bereshit   # bingo, I-spy, match, listen_do, coloring, sequencing PDFs
cd .. && python3 src/build_guide.py decks/bereshit  # 16-page letter guide → print/{id}-guide.pdf
```

Data lives in `decks/{id}/extras.yaml` and `decks/{id}/guide.yaml`. Full guide: `docs/extras.md`.

### 6. Publish to the Hub

```bash
python3 scripts/sync_to_hub.py bereshit purim      # uses HUB_DIR from .env, or --hub PATH
python3 scripts/sync_to_hub.py terumah --allow-invalid   # terumah still fails the v3 validator
```

Writes the deck JSON, WebP images and the letter PDF into the `simonbrief-hub` repo (`/parashapacks`).
Every deck runs through `src/validate_deck.py` first; any validator error stops the sync (exit 1) before
anything is written, unless you pass `--allow-invalid`.

### 7. Review Cards

`review-site/index.html` lists decks from `decks/registry.json`. It still renders v2 card fields, so
v3 decks show blanks; review v3 decks in the Card Designer (`cd card-designer && npm run dev`).

## Card Types (decision D1)

| Type | Standard | Holiday | Purpose |
|------|----------|---------|---------|
| Anchor | 1 | 1 | Parasha/holiday introduction + week plan |
| Spotlight | 2 | 2 | Character portraits with emotion |
| Story | 4 | 3 | Key narrative moments |
| Tradition | — | 3 | Holiday practices |
| Connection | 1 | 1 | "Have you ever..." discussion |
| Power Word | 1 | 1 | Hebrew vocabulary |
| Home | 1 | 1 | Shabbat-table question + try at home (no AI art) |
| **Total** | **10** | **12** | |

## Agent-Based Workflow (pipeline v3)

8 agent roles: 00 Series Planner, 01 Torah Scholar, 02 Curriculum Designer, 02b Sensitivity Reviewer ★,
03 Content Writer (English + Hebrew), 05 Visual Director, 05b Image QA ★, 06 Editor, plus the Card
Designer tool. Each writes `decks/{id}/pipeline/<step>.yaml` (schemas in `schemas/pipeline/`).

- Roles, checkpoints, overnight rule: [agents/AGENTS.md](agents/AGENTS.md)
- Files, commands, assemble step, budgets: [agents/AGENT_PIPELINE.md](agents/AGENT_PIPELINE.md)

## Safety Rules for Image Generation

- NEVER depict God in human form (Hashem is only ever shown as light)
- No graphic violence or death
- No scary monsters; villains are sulky or comic, never scary
- All characters dressed modestly
- Age-appropriate for 4-6 year olds

Full rules: `style/style_config.yaml` (read by the prompt builder) and `agents/VISUAL_SPECS.md`.

## Common Tasks

| Task | Command |
|------|---------|
| Check the year plan | `cd src && python3 series.py` |
| Fetch research for a parasha | `cd src && python3 sefaria_client.py research bereshit` (`--refresh` to refetch) |
| Assemble a deck from pipeline YAML | `python3 src/assemble_deck.py decks/bereshit` |
| Check a deck for mistakes | `python3 src/validate_deck.py decks/bereshit/deck.json` (`--strict`, `--json`) |
| Cheap drafts, then final | `python generate_images.py ../decks/bereshit/deck.json --card story_1 --draft`, then `--final --from-draft ../decks/bereshit/raw/drafts/story_1_d2.png` |
| Generate one card at 2K | `python generate_images.py ../decks/bereshit/deck.json --card spotlight_1` |
| Generate without style plates | `python generate_images.py ../decks/bereshit/deck.json --card story_1 --no-hero` |
| Contact sheet of drafts | `python3 src/contact_sheet.py out.png decks/bereshit/raw/drafts/*.png --cols 4` |
| Identity sheet versions | `python generate_references.py --character adam --versions 2`, then `--accept v2` |
| List characters / research | `cd src && python -m workflows list characters` |
| Sync deck to Card Designer | `./sync-deck.sh bereshit` |
| Export final cards + PDF | `cd card-designer && npm run export bereshit -- --backs --pdf` |
| Compress any PDF | `python3 scripts/compress_pdf.py file.pdf` (`--quality 88`) |
| Build extras / guide | see "Extras and Teacher Guide" above |
| Publish to the hub | `python3 scripts/sync_to_hub.py bereshit` |
| Card Designer unit tests | `cd card-designer && npm test` |
| Python tests | `python3 -m pytest tests -q` |

## Environment Variables

All live in `.env` in the project root (never commit it):

| Variable | Meaning |
|----------|---------|
| `GEMINI_API_KEY` | Image API key (required for generation) |
| `GEMINI_IMAGE_MODEL` | Override the image model (default `gemini-3.1-flash-image`) |
| `PP_SPEND_LEDGER` | Path of a JSONL file; every real image call is appended |
| `PP_BUDGET_USD` | Hard cap: calls are refused once the ledger total reaches it |
| `HUB_DIR` | Path to the `simonbrief-hub` checkout for `sync_to_hub.py` |
| `CARD_DESIGNER_PORT` | Dev server port for the export (default 3000) |

```bash
source .env && export GEMINI_API_KEY
```

## Image Generation Model

**Nano Banana 2 (`gemini-3.1-flash-image`)** is the default. To use another model, set
`GEMINI_IMAGE_MODEL` in `.env` (e.g. `gemini-3-pro-image` for Nano Banana Pro). There is no `--model` flag.

- **Sizes:** `--size 512|1K|2K|4K` (uppercase K). Default **2K** (3:4 = 1792x2400); `--draft` uses **1K** (896x1200).
- **Draft → final:** `--draft` writes 2 cheap 1K drafts to `raw/drafts/{card}_d{n}.png`; `--final --from-draft <file>`
  makes the 2K final with the chosen draft as a composition reference.
- **Prices** (`src/config.py` `IMAGE_PRICE_USD`): 1K $0.067, 2K $0.101, 4K $0.151.
- **Spend ledger:** set `PP_SPEND_LEDGER` and `PP_BUDGET_USD` before a session; over-budget calls are refused before any network request.
- The API returns JPEG; it is re-encoded to a real PNG on save.
- Each run logs model, size, prompt version and references to `raw/generations.jsonl`. Errors go to `project.log`.

**References sent with every card, in this order:** style plate(s) from `style/plates/`, the chosen draft
(`--from-draft` only), a `continuity_ref` image, then up to 4 character identity sheets. A deck's
`references/style_hero.png` is only a legacy fallback when no plates exist. `--no-hero` turns plates off,
`--no-refs` sends no references.

## Character Consistency System

The **shared character library** (`characters/`, see `characters/README.md`) is the single source of truth:

1. Each character has ONE folder, `characters/{key}/`, with `character.yaml` (gender, role, locked
   `visual_anchors` such as headwear, beard, clothing colors, and "adult" for grown-ups) and `identity.png`.
2. When generating a card, each key in `characters_in_scene` is looked up there (the deck's
   `references/manifest.json` is a fallback with a warning) and the identity sheet is sent as a labeled reference.
3. The locked anchors are added to the prompt automatically. Scene prompts only need pose, action and emotion.

## Version Control

**Use git as the single source of truth.** Commit before major changes (e.g., before regenerating images).

```bash
git add -A && git commit -m "Pre-regeneration checkpoint: [deck name]"
git add -A && git commit -m "Regenerate [deck name] images with [change description]"
```

Avoid manual `_v1`, `_v2` file copies. Draft runners-up live in `raw/drafts/` and `alternates/` by design.

## Workflow

When implementing multi-step plans, break work into smaller commits and provide progress summaries after each major step.

## Planning

Before starting implementation tasks, confirm the workflow ordering and dependencies with the user.

## Code Review

For code reviews, output findings incrementally as files are read rather than waiting until all files are processed.

## Print Specifications

Defined once in `card-designer/print_formats.json`:

| | Letter (default) | 5x7 (optional vendor) |
|---|---|---|
| Sheet | 8.5x11" | 5.25x7.25" (5x7" trim + 0.125" bleed) |
| Card area | inside a 0.3" white margin | full bleed in the card color |
| Safe zone | 0.3" from the sheet edge | 0.25" inside the trim |
| Printer | home/school, duplex, **flip on long edge**, "actual size" | print shop |
| Card PNG @ 300 DPI | 2375x3125 | 1500x2100 |

- One card per sheet; PDF pages run front1, back1, front2, back2…
- PDFs are auto-compressed (art re-encoded as JPEG q88 at the same pixel size, ~57 MB → ~6 MB).
- The teacher guide booklet and all extras are letter size too.

## Card Format

- **AI generates scene-only images** to `raw/` (no text, no borders)
- **`build_generation_prompt()`** layers style, world, safety and composition from `style/style_config.yaml`
- Image prompts in deck.json are **pure scene descriptions**
- **Card Front**: art + title band + type chip + story number + Hebrew badge (drawn by the Card Designer)
- **Card Back**: teacher side (SAY / ASK / Hebrew), one `CardBack` component for all 7 types
- `card.guide` is never printed on the card; it feeds the teacher guide booklet

**Deck Data Flow:**
```
decks/{id}/pipeline/*.yaml → assemble_deck.py → decks/{id}/deck.json  (single source of truth)
        ↓ generate_images.py → decks/{id}/raw/
        ↓ ./sync-deck.sh {id} → card-designer/content/{id}/
        ↓ npm run export {id} → images/, backs/, print/*.pdf
        ↓ scripts/sync_to_hub.py {id} → simonbrief-hub
```

Deck folder layout: see `decks/CLAUDE.md`.
