---
status: pending
priority: p2
tags: [content, deck, terumah, v3]
---

# Terumah is a migrated v2 deck and fails the v3 validator

## Problem
`decks/archive/terumah/deck.json` was converted by `src/migrate_v2_to_v3.py`, not written
through the v3 pipeline. `python3 src/validate_deck.py decks/archive/terumah/deck.json`
reports **17 errors** (and 65 warnings). Because of this, publishing it to the hub needs
`python3 scripts/sync_to_hub.py terumah --allow-invalid`.

## Where
- `decks/archive/terumah/`
- Reference for a full v3 rewrite: `decks/purim/pipeline/`, `decks/bereshit/pipeline/`

## Proposed fix
Rewrite Terumah through the pipeline (00 series -> 06 editor), the same way Purim was:
write the pipeline YAMLs, run `python3 src/assemble_deck.py decks/terumah`, reuse existing
raw art where it still fits, regenerate the rest (drafts first; check the spend budget).

## Acceptance
- `python3 src/validate_deck.py decks/terumah/deck.json` -> `Result: PASS`.
- `python3 scripts/sync_to_hub.py terumah` works without `--allow-invalid`; remove the
  Terumah note from the `sync_to_hub.py` docstring and root `CLAUDE.md`.
