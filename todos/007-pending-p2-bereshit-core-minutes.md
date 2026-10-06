---
status: pending
priority: p2
tags: [content, deck, bereshit, curriculum]
---

# Bereshit core cards add up to 26 minutes (target ~15)

## Problem
The core path (the cards a teacher uses when short on time) should take about 15 minutes.
In Bereshit the `core: true` cards total 26 minutes, so the "short version" is not short.

## Where
- `decks/bereshit/pipeline/02-structure.yaml` (`core` and `minutes` per card)
- `decks/bereshit/deck.json` (rebuilt by `assemble_deck.py`)

## Proposed fix
Curriculum Designer pass: mark fewer cards as core (e.g. anchor + 2 story + closing) or cut
minutes on the story cards; keep the week plan consistent. Consider a validator warning when
core minutes exceed ~18.

## Acceptance
- Sum of `minutes` over core cards is 13-17.
- `python3 src/assemble_deck.py decks/bereshit` and `src/validate_deck.py` both pass.
