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
    ├── print/          # Print PDFs (from Card Designer --pdf)
    │   ├── purim-letter.pdf
    │   └── purim-5x7.pdf
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
4. **Export to `images/`, `backs/` and `print/`** — PNGs for the web, PDFs for printing

```bash
# Generate raw images (system layers added automatically)
cd src && python generate_images.py ../decks/purim/deck.json

# Sync deck data + raw images to Card Designer
./sync-deck.sh purim

# Export with Card Designer (PNGs + duplex PDF, letter by default)
cd card-designer && npm run export purim -- --backs --pdf
cd card-designer && npm run export purim -- --format 5x7 --backs --pdf
```

## Creating a New Deck

```bash
cd src
python generate_deck.py --parasha "Beshalach"              # Standard parasha deck (10 cards)
python generate_deck.py --parasha "Purim" --holiday         # Holiday deck (13 cards)
python generate_deck.py --output ../decks/beshalach         # Custom output path
```

> **Note:** `generate_deck.py` still writes a **v2** template. Until it is updated, start a new
> deck by copying `decks/bereshit/deck.json` (v3), or run `python src/migrate_v2_to_v3.py` on the template.

This creates:
- `deck.json` — Template with placeholder cards
- `feedback.json` — Empty feedback structure
- `raw/` — Directory for AI-generated scene images
- `images/` — Directory for final exports
- `references/` — Directory for character sheets

## deck.json Structure (v3)

The full rules live in [`schemas/deck.v3.schema.json`](../schemas/deck.v3.schema.json).
`decks/bereshit/deck.json` is the reference example. Older v2 decks are converted with
`python src/migrate_v2_to_v3.py decks/<id>/deck.json` (a mechanical move of fields; it lists
everything it could not map). The Card Designer only reads v3.

```json
{
  "id": "bereshit",
  "version": "3.0",
  "parasha_en": "Bereshit",
  "parasha_he": "בְּרֵאשִׁית",
  "holiday": false,
  "ref": "Genesis 1:1–6:8",
  "value": { "en": "Caring for the world", "he": "…", "kid_phrase": "caring for Hashem's world", "gesture": "…" },
  "palette": ["#1E3A5F", "#E0A526", "#4F9A4A", "#9BD7F5", "#FFF4D6"],
  "web_theme": { "primary": "#1E3A5F", "secondary": "#4F9A4A", "accent": "#E0A526", "wash": "#FFF8E7" },
  "story_world": "The newly created world and Gan Eden…",
  "week_plan": [ { "day": 1, "label": "This card + Story 1", "cards": ["anchor_1", "story_1"] } ],
  "cards": [ … ]
}
```

- `value.en` is printed in the pill on every back. `value.kid_phrase` is how we say it to children.
- `palette` (5 colors) colors the placeholder fronts and, later, the art prompts. `web_theme` is for the hub.
- `week_plan` is printed as the THIS WEEK strip on the anchor back.

## Card Structure (v3)

Every card has the same shape. Card types: `anchor`, `spotlight`, `story`, `connection`,
`tradition`, `power_word`, `home`.

```json
{
  "card_id": "story_1",
  "card_type": "story",
  "title_en": "Light, Sky & Land",
  "title_he": "אוֹר, שָׁמַיִם וַאֲדָמָה",
  "characters_in_scene": [],
  "image_prompt": "Scene only: no style, text or layout rules",
  "image_path": "raw/story_1.png",
  "sequence_number": 1,
  "hebrew_keyword": { "word": "אוֹר", "translit": "or", "meaning": "light" },
  "back": {
    "objective": "Days 1–3: light, sky, land and plants",
    "title_he": "יָמִים א׳–ג׳",
    "say": "**Day 1: light!** [Open hands wide]\n**And Hashem saw it was… TOV!** [Thumbs up!]",
    "ask": [ { "text": "What did Hashem make first?", "type": "recall" },
             { "text": "Show me how a tree grows!", "type": "nonverbal" } ],
    "hebrew": { "word": "אוֹר", "translit": "OR", "meaning": "light", "gesture": "fists, then open wide" },
    "minutes": 5,
    "core": true,
    "transition": "But the sky was still empty…",
    "guide_ref": { "page": 6 }
  },
  "guide": {
    "pshat": { "text": "…", "refs": ["Genesis 1:3"] },
    "sages": [ { "text": "Our Sages teach…", "source": "…" } ],
    "hard_questions": [ { "q": "…", "answer": "…", "redirect": "…" } ],
    "adapt": { "see": "…", "do": "…", "join": "…" },
    "extend": "…",
    "tip": "…"
  }
}
```

**`back`** is what is printed on the teacher side:

| Field | Printed as | Budget |
|---|---|---|
| `objective` | 🎯 goal line (may use `**bold**`) | ≤10 words |
| `say` | **SAY** block. `**bold**` = read aloud, `[cue]` = action chip, newline = line break | ≤50 words |
| `ask[]` | **ASK** list. `type`: `recall`, `wh`, `open`, `distancing`, `nonverbal` (nonverbal gets a ✋ marker) | ≤2 questions, ≤12 words each |
| `hebrew` | Hebrew strip: word, translit, "meaning" (note), ✋ gesture | |
| `minutes`, `core` | header: "~5 min", "★ CORE" | |
| `transition` | footer, left ("▸ …") | |
| `guide_ref` | footer, right ("Guide p.6 · note") | |
| `title_he` | optional: Hebrew beside the back title when it differs from the front | |

Type-specific extras inside `back`:

- **power_word:** `trio` — exactly 3 boxes `{big, line1, line2}` (word / gesture / fact)
- **connection:** `faces` — up to 4 of `happy, proud, calm, excited, scared, brave, sad, surprised` (drawn as SVG)
- **story:** `sequence_number` (card level, required) and `hebrew_keyword` (card level, front badge)
- **home:** the back is different: `objective`, `shabbat_question {en, he}`, `hebrew`, `try_at_home [{text, tag: "shabbat-friendly" | "before-shabbat"}]`, `transition`. No art needed: if `raw/home_1.png` is missing the Card Designer draws its own front.

**`guide`** is never printed on the card; it feeds the teacher guide booklet (Phase 8).

Word budgets are not enforced by the JSON schema; the validator checks them.
The migrated Purim and Terumah decks are over budget on purpose (content gets rewritten later),
so they fail validation until rewritten.

Optional fields used by the image pipeline: deck `story_world_setting` (`outdoor`|`indoor`),
card `style_plate` (`landscape`|`interior`|`object`|`classroom`) and card `continuity_ref`
(the card_id of an earlier card whose image is passed as a reference, e.g. story_2 → story_1).

## Validating a Deck

```bash
python3 src/validate_deck.py decks/bereshit/deck.json   # from the repo root
```

Errors must be fixed before export; warnings are worth a look. See `src/CLAUDE.md` for the full
list of checks. Bereshit passes with 0 errors (its warnings are the TODO stubs).

## Teacher Guide Page Map (`guide_layout.yaml`)

`guide_layout.yaml` (repo root) fixes the letter-size guide booklet's page for every card slot,
so "Guide p.N" on a back is the same for every deck of that kind. Each card's
`back.guide_ref.page` must match it (the validator checks).

| Slot | Standard (10 cards) | Holiday (12 cards) |
|---|---|---|
| cover / overview | p.1 / p.3 | p.1 / p.3 |
| anchor_1 (+ week plan) | p.2 | p.2 |
| spotlight_1–2 | p.4–5 | p.4–5 |
| story_1… | p.6–9 (4 stories) | p.6–8 (3 stories) |
| tradition_1–3 | — | p.9–11 |
| connection_1 | p.10 | p.12 |
| power_word_1 | p.11 | p.13 |
| hard questions / adaptations / extras index | p.12 / 13 / 14 | p.14 / 15 / 16 |
| family letter (+ home_1) | p.15 | p.17 |
| sources | p.16 | p.18 |

## Print Formats

Defined once in `card-designer/print_formats.json`:

| Format | Sheet | Card | Notes |
|---|---|---|---|
| `letter` (default) | 8.5×11" | 7.9×10.4" inside a 0.3" white margin | home/school printer, duplex, no cutting |
| `5x7` | 5.25×7.25" | 5×7" trim | print shop: 0.125" bleed in the card color, keep text 0.25" inside the trim |

The same components render both; all sizes are relative to the card width (`cqw`).

**Export guard.** `npm run export <id>` first runs the deck validator, then renders
`/print/<id>?format=…` and measures every card side. It stops (exit 1) and lists
card id / side / format / px when a back's text section overflows
(`.pp-card .body` taller than its box) or any text sits outside the safe zone
(letter: 0.3" from the sheet edge; 5x7: 0.25" inside the trim, i.e. 0.375" from the sheet edge).

| Flag | Effect |
|---|---|
| `--skip-validate` | don't run the Python validator |
| `--allow-overflow` | print the layout problems but export anyway |

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
| `images/{card_id}.png` | 2375x3125 | Card front, letter card area @ 300 DPI (no paper margin) |
| `backs/{card_id}_back.png` | 2375x3125 | Teacher card back, letter @ 300 DPI |
| `images/5x7/…`, `backs/5x7/…` | 1500x2100 | Same, 5x7 trim size (`--format 5x7`) |
| `print/{id}-letter.pdf` | 8.5x11 pages | Duplex PDF: front1, back1, front2, back2… (flip on long edge) |
| `print/{id}-5x7.pdf` | 5.25x7.25 pages | Vendor PDF with 0.125" bleed |

PDFs are auto-shrunk after export by `scripts/compress_pdf.py` (JPEG q88, same pixel size; `--no-compress` to skip, or run it by hand on any PDF).

## Generating Cards

```bash
# Generate raw scene images
cd src && python generate_images.py ../decks/purim/deck.json

# Generate specific card
python generate_images.py ../decks/purim/deck.json --card story_1

# Generate 3 variants of a card (pick winner, rename to {card_id}.png)
python generate_images.py ../decks/purim/deck.json --card story_1 --variants 3

# Skip existing images
python generate_images.py ../decks/purim/deck.json --skip-existing

# Without character references (debugging)
python generate_images.py ../decks/purim/deck.json --no-refs

# Sync + export with Card Designer
./sync-deck.sh purim
cd card-designer && npm run export purim -- --backs
```

**Export rendering:** Fronts render at 500x700 CSS with 3x device scale (matches design editor where overlays were designed). Backs render at 1500x2100 CSS with 1x scale (print-calibrated fonts).

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
