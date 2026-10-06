# Deck v3 — Todo

Full plan: [docs/plans/2026-10-02-feat-deck-v3-improvements-plan.md](../docs/plans/2026-10-02-feat-deck-v3-improvements-plan.md)

Status: **Decisions locked 2026-10-05 — awaiting go for Phase 1**

## Decisions
- [x] D1–D6 (card count, values spine, Modern Orthodox, hard-text policy, booklet, Simon reviews)
- [x] D7 Default 8.5×11 letter (home printer, duplex, no bleed); 5×7 vendor print kept as optional export
- [x] D5b Teacher booklet = 8.5×11 letter
- [x] D8 Order: foundations → Bereshit → website → extras
- [x] D9–D13 Back design, projector + presenter window, hub URL per deck, Bereshit scope/טוֹב, extras v1

## Phase 1 — New card backs (letter)
- [ ] 1.1 Letter-size mockups (fronts + 7 backs) with Bereshit content → Simon approves
- [ ] 1.2 `schemas/deck.v3.schema.json`
- [ ] 1.3 `src/migrate_v2_to_v3.py` (Purim, Terumah)
- [ ] 1.4 Single `CardBack.tsx`; letter frames; v3 palette + icons
- [ ] 1.5 Duplex PDF export, `--format letter|5x7` from `print_formats.json`

## Phase 2 — Automatic checks
- [ ] 2.1 `src/validate_deck.py`
- [ ] 2.2 Export overflow/safe-zone guard
- [ ] 2.3 Tests
- [ ] 2.4 Logging
- [ ] 2.5 Housekeeping

## Phase 3 — Character library + year plan
- [ ] 3.1 `characters/` library; migrate 7 characters; retire 3 duplicate sources
- [ ] 3.2 Adam + Chava identity sheets (2 versions each) → Simon picks
- [ ] 3.3 `series.yaml` (66 skeleton, first ~5 filled)
- [ ] 3.4 Sefaria research cache (Bereshit)

## Phase 4 — Agents
- [ ] 4.1 00 planner, 02b sensitivity, 05b image QA, merge 03+04, 06 rubric, 07 → tool
- [ ] 4.2 Per-agent schemas + `assemble_deck.py`
- [ ] 4.3 Image QA rubric (flag-only)
- [ ] 4.4 3-layer docs pass (letter default + 5×7 optional)

## Phase 5 — Print-ready art
- [ ] 5.1 4K 3:4 generation (crop-safe for letter + 5:7)
- [ ] 5.1b CMYK soft-proof for 5×7 target
- [ ] 5.2 Prompt fixes
- [ ] 5.3 Series style bible
- [ ] 5.4 Letter fronts
- [ ] 5.5 SVG feeling faces

## Phase 6 — Bereshit deck
- [ ] 6.1 Pipeline run with checkpoints
- [ ] 6.2 10 cards
- [ ] 6.3 Images (~25 gens)
- [ ] 6.4 Validate, PDF, home-printer test print
- [ ] 6.5 Metrics vs Purim

## Phase 7 — Hub website
- [ ] 7.1 `scripts/sync_to_hub.py`
- [ ] 7.2 Routes per deck; migrate Purim/Terumah; drop data.ts
- [ ] 7.3 Present mode
- [ ] 7.4 Presenter window (BroadcastChannel)
- [ ] 7.5 Print button
- [ ] 7.6 Verify + hub PR

## Phase 8 — Extras
- [ ] 8.1 Item art (12 + shared)
- [ ] 8.2 Bingo ×10
- [ ] 8.3 I-spy
- [ ] 8.4 Match-it
- [ ] 8.5 Coloring + sequence
- [ ] 8.6 Following-directions story
- [ ] 8.7 Sequencing game
- [ ] 8.8 Teacher guide booklet
- [ ] 8.9 Home card
- [ ] 8.10 Classroom pilot kit

## Phase 9 — Purim retrofit (later)
- [ ] 9.1 Content + Hebrew fixes, 12 cards, regenerate at letter
