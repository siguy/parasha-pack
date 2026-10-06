---
status: pending
priority: p2
tags: [code, pipeline, v3, legacy]
---

# New-deck commands still write v2 templates

## Problem
`python src/generate_deck.py` and `python -m workflows deck "<Name>"` still create a v2
`deck.json` (13 placeholder cards with `front`/`back`). v3 decks are 10 cards (12 with
the holiday set) and are built from `decks/<id>/pipeline/*.yaml` by `assemble_deck.py`.
Anyone following the old commands starts from the wrong shape and fails the validator.

## Where
- `src/generate_deck.py`
- `src/workflows/` (the `deck` subcommand)
- `src/CLAUDE.md` (currently marks both as "legacy v2")

## Proposed fix
Make `workflows deck <id>` create `decks/<id>/pipeline/` with empty-but-schema-valid
`00-series.yaml` ... `03-content.yaml` (copy the shape of `tests/fixtures/pipeline_min/`),
then tell the user to fill them via the agents and run `assemble_deck.py`. Retire
`generate_deck.py` (move to `src/archive/`) or make it call the same code.

## Acceptance
- `python -m workflows deck demo --output <tmp>` writes a pipeline folder, not a v2 deck.json.
- A test checks every written YAML passes its `schemas/pipeline/*.schema.json`.
- No command in the repo writes a 13-card v2 template.
