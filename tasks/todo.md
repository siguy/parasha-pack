# Deck v3 — Todo

Full plan: [docs/plans/2026-10-02-feat-deck-v3-improvements-plan.md](../docs/plans/2026-10-02-feat-deck-v3-improvements-plan.md)

Status: **Decisions made — Phase 1 ready to start**

## Phase 0 — Decisions (Simon)
- [x] D1 Card count: 10 standard / 12 holiday
- [ ] D2 Values spine list (~12–15 middot) — Claude drafts
- [x] D3 Modern Orthodox (midrash voiced as "Our Sages teach…")
- [ ] D4 Hard-text policy — Claude drafts
- [x] D5 Printed booklet
- [x] D6 Simon is sole checkpoint

## Phase 1 — Back v3 template + schema
- [ ] 1.1 HTML mockups of v3 backs (6 types) → Simon approves
- [ ] 1.2 `schemas/deck.v3.schema.json`
- [ ] 1.3 `src/migrate_v2_to_v3.py`
- [ ] 1.4 Single config-driven `CardBack.tsx`; remove overflow-hidden; bold/bracket parser; AA contrast
- [ ] 1.5 Update CARD_SPECS.md

## Phase 2 — Safety net
- [ ] 2.1 `src/validate_deck.py` (budgets, refs, nikud, Hebrew gender, banned terms, transitions, count)
- [ ] 2.2 Export overflow + safe-zone guard in `export-deck.ts`
- [ ] 2.3 Tests (pytest + parser test)
- [ ] 2.4 Housekeeping (rsync --delete, review-site paths, hardcoded terumah, stale files)
- [ ] 2.5 Logging to project.log

## Phase 3 — Purim rewrite
- [ ] 3.1 Torah accuracy fixes (motive, midrash labels, Esther's risk, ending, Haman Q, hidden God, verse refs)
- [ ] 3.2 Hebrew fixes (מְקַנֵּא, אַמִּיצָה, gibor/giborah, stress, inclusive forms)
- [ ] 3.3 Restructure to D1 count; cover 4 mitzvot; add home card; grogger framing
- [ ] 3.4 Rewrite backs to v3 → validate → export → review

## Phase 4 — Imagery & design
- [ ] 4A Print: 2K generation, bleed export, CMYK proof, licensed emoji/SVG
- [ ] 4B Prompts: drop lower-left shadow, title zone, figure cap, diversity, kippah, megillah, villain posture, Achaemenid
- [ ] 4C Series style bible + identity sheets v2 (turnaround + expressions, no captions)
- [ ] 4D Fronts: FitText padding, gradient, subtitle size, distinct colors + type icons, sequence numbers, emoji bar

## Phase 5 — Agent pipeline v3
- [ ] 5.1 00 Series Planner
- [ ] 5.2 02b Sensitivity Reviewer (+ human checkpoint)
- [ ] 5.3 Merge 03 + 04
- [ ] 5.4 05b Image QA (vision rubric)
- [ ] 5.5 06 Editor → scored rubric
- [ ] 5.6 07 → tool doc
- [ ] 5.7 Per-agent output schemas
- [ ] 5.8 Docs reconciliation across all 3 layers

## Phase 6 — Scaling infra
- [ ] 6.1 Shared character library (retire 4 duplicate sources)
- [ ] 6.2 Sefaria research cache
- [ ] 6.3 series.yaml (66 entries)
- [ ] 6.4 assemble_deck.py
- [ ] 6.5 Orchestrator with checkpoints + resume
- [ ] 6.6 Cost/acceptance tracking

## Phase 7 — Extensions
- [ ] 7.1 Teacher guide booklet generated from `guide` fields
- [ ] 7.2 Home/family card
- [ ] 7.3 Sequencing game
- [ ] 7.4 Year-2 question bank
- [ ] 7.5 Hebrew word wall
- [ ] 7.6 Packaging + proof print
- [ ] 7.7 AI disclosure + licensing review
- [ ] 7.8 Classroom pilot + survey
- [ ] 7.9 FOR_SIMON.md

## Phase 8 — Deck #7 on new pipeline
- [ ] 8.1 Pick a recurring-character parasha
- [ ] 8.2 Run orchestrator; measure vs Purim
- [ ] 8.3 Retro
