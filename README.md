# Parasha Pack

Illustrated weekly Torah portion (parasha) and holiday card decks for preschool and kindergarten
classrooms (ages 4-6). Each deck has a picture front for the children and a short teacher script on
the back, plus printable extras (bingo, I-spy, coloring, ...) and a letter-size teacher guide booklet.

- **Standard deck:** 10 cards. **Holiday deck:** 12 cards. Both include a home card for families.
- **Default print:** 8.5x11 letter, one card per sheet, double-sided (flip on long edge) on a home or school printer.
- **Optional print:** 5x7 cards with bleed for a print shop.

Current decks: `decks/bereshit/` (with extras and guide) and `decks/purim/`. Older decks are in `decks/archive/`.

## Quick start: make a new deck

```bash
# 0. Setup (once)
pip install -r requirements.txt && python -m playwright install chromium
(cd card-designer && npm ci)
source .env && export GEMINI_API_KEY                  # .env holds GEMINI_API_KEY (and HUB_DIR)
export PP_SPEND_LEDGER=/tmp/spend_ledger.jsonl PP_BUDGET_USD=5   # receipt + hard spending cap

# 1. Plan + research (agents 00, 01): add the deck to series.yaml, then
(cd src && python3 series.py)                          # check the year plan
(cd src && python3 sefaria_client.py research noach)   # cache key verses → research/noach.yaml
#    (first add a RESEARCH_PLANS["noach"] entry in src/sefaria_client.py: which verses to fetch)

# 2. Write decks/noach/pipeline/00-series … 03-content.yaml (agents 00-03; Simon approves 02b), then
python3 src/assemble_deck.py decks/noach               # merge → deck.json + run the validator

# 3. Write pipeline/05-visual.yaml (agent 05), assemble, then 2 cheap 1K drafts per card (repeat --card)
python3 src/assemble_deck.py decks/noach
(cd src && python3 generate_images.py ../decks/noach/deck.json --card story_1 --draft)
python3 src/contact_sheet.py decks/noach/raw/drafts/contact_sheet.png decks/noach/raw/drafts/*.png --cols 4

# 4. Pick drafts (agent 05b, Simon approves), make the 2K finals, assemble again
(cd src && python3 generate_images.py ../decks/noach/deck.json --final --from-draft ../decks/noach/raw/drafts/story_1_d2.png)
python3 src/assemble_deck.py decks/noach

# 5. Editor review (agent 06), then check, export and publish
python3 src/validate_deck.py decks/noach/deck.json
./sync-deck.sh noach
(cd card-designer && npm run export noach -- --backs --pdf)               # letter PDF
(cd card-designer && npm run export noach -- --format 5x7 --backs --pdf)  # optional 5x7
python3 scripts/sync_to_hub.py noach

# 6. Extras + guide (needs decks/noach/extras.yaml and guide.yaml)
(cd src && python3 generate_items.py ../decks/noach && python3 coloring.py ../decks/noach && python3 generate_activities.py ../decks/noach)
python3 src/build_guide.py decks/noach
```

Each agent's rules are in `agents/definitions/`; the full pipeline with every command is in
[agents/AGENT_PIPELINE.md](agents/AGENT_PIPELINE.md). `decks/bereshit/pipeline/` is a complete worked example.
New characters need an identity sheet first (see `characters/README.md`).

## How it fits together

```
series.yaml ─► decks/{id}/pipeline/*.yaml ─► assemble_deck.py ─► deck.json
                                                                   │
            style/plates + characters/ ─► generate_images.py ─► raw/*.png
                                                                   │
                         sync-deck.sh ─► card-designer (Next.js) ─► images/, backs/, print/*.pdf
                                                                   │
                                              scripts/sync_to_hub.py ─► simonbrief-hub
```

## Project structure

```
parasha-pack/
├── series.yaml          # year plan: every deck, its middah and power word
├── guide_layout.yaml    # teacher-guide page map ("Guide p.N" on each back)
├── characters/          # shared character library (one identity sheet per character)
├── style/               # style rules + style plates (the series look)
├── research/            # Sefaria verse cache
├── schemas/             # JSON Schemas: deck v3, extras, each pipeline step
├── agents/              # agent roles, pipeline, card/visual specs, rubrics, lessons
├── src/                 # Python: assemble, validate, images, extras, guide
├── scripts/             # compress_pdf.py, sync_to_hub.py
├── card-designer/       # Next.js app: draws the cards, exports PNG + PDF
├── templates/           # HTML templates for extras, guide and pilot forms
├── items/shared/        # item art reused by every deck's extras
├── decks/               # deck data, art and PDFs
├── docs/                # extras guide, policies, pilot kit, plans, mockups
├── review-site/         # old review UI (v2 fields only)
└── tests/               # pytest suite
```

## Card types

| Type | Standard | Holiday | Purpose |
|------|----------|---------|---------|
| Anchor | 1 | 1 | The week's big idea + week plan |
| Spotlight | 2 | 2 | A character with a clear emotion |
| Story | 4 | 3 | Key moments, told with gestures |
| Tradition | — | 3 | Holiday practices |
| Connection | 1 | 1 | "Have you ever...?" |
| Power Word | 1 | 1 | One Hebrew word with a gesture |
| Home | 1 | 1 | A Shabbat-table question for families |

## Printing

| | Letter (default) | 5x7 (vendor) |
|---|---|---|
| File | `decks/{id}/print/{id}-letter.pdf` | `decks/{id}/print/{id}-5x7.pdf` |
| Sheet | 8.5x11", card inside a 0.3" margin | 5.25x7.25" (0.125" bleed, 0.25" safe zone) |
| How | double-sided, **flip on long edge**, "actual size" | send to a print shop |

The teacher guide (`print/{id}-guide.pdf`) and the extras (`extras/*.pdf`) are letter size.
How to print and play each extra: [docs/extras.md](docs/extras.md).

## Image generation

Nano Banana 2 (`gemini-3.1-flash-image`) at 2K by default, 1K for drafts. Override the model with
`GEMINI_IMAGE_MODEL` in `.env`. Every call can be logged and capped with `PP_SPEND_LEDGER` and
`PP_BUDGET_USD`. Details: root `CLAUDE.md` and `src/CLAUDE.md`.

## Tests

```bash
python3 -m pytest tests -q
cd card-designer && npm test
```

## Safety rules

- NEVER depict God in human form (Hashem is only ever light)
- No graphic violence or death
- No scary monsters; villains are sulky or comic
- All characters dressed modestly
- Age-appropriate for 4-6 year olds

## License

Educational use only.
