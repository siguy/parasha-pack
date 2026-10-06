# Card Deck Agent System (pipeline v3)

Each "agent" is a role Claude plays, defined in one Markdown file in `definitions/`. Each writes one YAML
file into `decks/{id}/pipeline/`, checked against a schema in `schemas/pipeline/`. `src/assemble_deck.py`
then merges the YAML into `deck.json` — no hand merging.

## Agent roster

| # | Agent | Owns | Writes |
|---|-------|------|--------|
| 00 | [Series Planner](definitions/00-series-planner.md) | middah, power word, characters, sensitivities, holiday placement (`series.yaml`) | `00-series.yaml` |
| 01 | [Torah Scholar](definitions/01-torah-scholar.md) | cited claims (pshat vs midrash), key moments, hard passages | `01-research.yaml` |
| 02 | [Curriculum Designer](definitions/02-curriculum-designer.md) | card list, ★core, minutes, 5-day week plan, story world | `02-structure.yaml` |
| 02b | [Sensitivity Reviewer](definitions/02b-sensitivity-reviewer.md) ★ | per-card verdicts, "if they ask" answers | `02b-sensitivity.yaml` |
| 03 | [Content Writer](definitions/03-content-writer.md) | backs, guide blocks, home card — English **and Hebrew** | `03-content.yaml` |
| 05 | [Visual Director](definitions/05-visual-director.md) | palette, scene-only prompts, characters in scene | `05-visual.yaml` |
| 05b | [Image QA](definitions/05b-image-qa.md) ★ | rubric scores, draft picks (flag-only) | `05b-image-qa.yaml` |
| 06 | [Editor](definitions/06-editor.md) | scored review, routed issues, feedback.json draft | `06-editor.yaml` |
| — | [Card Designer](tools/card-designer.md) (tool) | sync → export → hub sync | `images/`, `backs/`, `print/` |

The old **04 Hebrew Expert** is merged into 03 Content Writer (one writer owns a card's words in both languages).

## Workflow

```
[00 Series Planner]       series.yaml entry + 00-series.yaml
        ↓
[01 Torah Scholar]        reads research/{parasha}.yaml (Sefaria cache)
        ↓
[02 Curriculum Designer]  10 cards (12 holiday), ★core, week_plan
        ↓
[02b Sensitivity Reviewer]
        ↓  ★ CHECKPOINT 1: Simon approves verdicts + framing
[03 Content Writer]       backs + guide + home card (EN + HE)
        ↓  assemble_deck.py → validate_deck.py
[05 Visual Director]      scene-only prompts
        ↓  (new character? identity sheets, 2 versions → ★ pick)
        ↓  assemble_deck.py → generate_images.py --draft (1K)
[05b Image QA]            contact sheet, rubric scores, picks
        ↓  ★ CHECKPOINT 2: Simon picks drafts
        ↓  generate_images.py --final --from-draft (2K) → score finals
        ↓  assemble_deck.py
[06 Editor]               scored rubric; validator must pass
        ↓
[Card Designer tool]      sync-deck.sh → export (letter PDF) → scripts/sync_to_hub.py
        ↓  ★ CHECKPOINT 3: Simon reviews the printed test copy
```

Details, file names and commands: [AGENT_PIPELINE.md](AGENT_PIPELINE.md).

## Human checkpoints (★)

Simon is the only reviewer (D6).

1. **After 02b** — approve the sensitivity verdicts before any content is written.
2. **After 05b** — pick drafts (and any new character identity sheet).
3. **After export** — the test print.

**Overnight runs** (Simon asleep and he has said so): the coordinator makes each ★ decision using the
rubrics, keeps runners-up in an `alternates/` folder (or `raw/drafts/`), and logs every decision
(what, chosen, why, alternates) in `docs/overnight/decisions.md`. In the YAML, `decided_by: coordinator`.
Simon reviews the log in the morning.

## Card format (short)

- 10 cards standard / 12 holiday, home card included (D1). See [CARD_SPECS.md](CARD_SPECS.md).
- AI draws **scene-only** images to `raw/`; the Card Designer adds all text.
- Default print = **8.5×11 letter**, duplex, one card per sheet; optional 5×7 vendor export.

## Key files

- [AGENT_PIPELINE.md](AGENT_PIPELINE.md) — v3 flow, commands, assemble step, budgets
- [CARD_SPECS.md](CARD_SPECS.md) — card types, back fields, word budgets
- [VISUAL_SPECS.md](VISUAL_SPECS.md) — art style, characters, safety
- [LESSONS_LEARNED.md](LESSONS_LEARNED.md) — gotchas (the Editor reads this first)
- `rubrics/image_qa.yaml`, `rubrics/editor.yaml` — machine-readable scoring rules
- `schemas/pipeline/*.schema.json` — the shape of each agent's YAML

## Updating this documentation

After each deck: add new gotchas to LESSONS_LEARNED.md, fix the agent definition that let the mistake
through, and if a rubric criterion was missing, add it to `rubrics/` (and bump its `version`).
