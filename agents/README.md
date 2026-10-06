# Agent System Documentation

Quick navigation for the Parasha Pack agent pipeline (v3).

## Quick links

| I want to... | Go to... |
|--------------|----------|
| Understand the roles and checkpoints | [AGENTS.md](AGENTS.md) |
| Run the pipeline (files, commands, assemble, budgets) | [AGENT_PIPELINE.md](AGENT_PIPELINE.md) |
| See card types, back fields, word budgets | [CARD_SPECS.md](CARD_SPECS.md) |
| Find art style, characters, safety | [VISUAL_SPECS.md](VISUAL_SPECS.md) |
| See what one agent does | [definitions/](definitions/) |
| Export cards / PDFs | [tools/card-designer.md](tools/card-designer.md) |
| See scoring rules | [rubrics/](rubrics/) |
| Review lessons learned | [LESSONS_LEARNED.md](LESSONS_LEARNED.md) |

## Agent roster

| # | Agent | Role | Definition |
|---|-------|------|------------|
| 00 | Series Planner | Year plan: middah, power word, characters, sensitivities | [00-series-planner.md](definitions/00-series-planner.md) |
| 01 | Torah Scholar | Cited research from the Sefaria cache | [01-torah-scholar.md](definitions/01-torah-scholar.md) |
| 02 | Curriculum Designer | Cards, ★core, minutes, week plan | [02-curriculum-designer.md](definitions/02-curriculum-designer.md) |
| 02b | Sensitivity Reviewer ★ | Verdicts + "if they ask" answers | [02b-sensitivity-reviewer.md](definitions/02b-sensitivity-reviewer.md) |
| 03 | Content Writer | Backs, guide, home card (English + Hebrew) | [03-content-writer.md](definitions/03-content-writer.md) |
| 05 | Visual Director | Palette + scene-only prompts | [05-visual-director.md](definitions/05-visual-director.md) |
| 05b | Image QA ★ | Rubric scores + draft picks (flag-only) | [05b-image-qa.md](definitions/05b-image-qa.md) |
| 06 | Editor | Scored deck review, routes issues | [06-editor.md](definitions/06-editor.md) |
| — | Card Designer (tool) | Sync, export, hub sync | [tools/card-designer.md](tools/card-designer.md) |

## Workflow overview

```
00 → 01 → 02 → 02b ★ → 03 → assemble + validate → 05 → assemble → drafts → 05b ★ → finals
   → assemble → 06 → sync → export (letter PDF) → hub sync ★ test print
```

## Key concepts

- **One YAML per agent** in `decks/{id}/pipeline/`, each with a schema in `schemas/pipeline/`.
- **`src/assemble_deck.py`** merges them into `deck.json` (no hand merging) and runs the validator.
- **Rubrics** (`rubrics/image_qa.yaml`, `rubrics/editor.yaml`) make "is it good enough?" a number.
- **Character consistency:** one identity sheet per character in `characters/{key}/`, passed with every card.
- **Villains** are misguided, not scary. **Hashem** is only ever light.

## File structure

```
agents/
├── README.md, AGENTS.md, AGENT_PIPELINE.md
├── CARD_SPECS.md, VISUAL_SPECS.md, LESSONS_LEARNED.md
├── definitions/   00-series-planner … 06-editor (8 agents)
├── tools/         card-designer.md
└── rubrics/       image_qa.yaml, editor.yaml
```

## Maintenance

- After a deck: add gotchas to LESSONS_LEARNED.md and fix the agent definition that missed them.
- If specs change: update CARD_SPECS.md / VISUAL_SPECS.md (single sources of truth) and the matching schema.
