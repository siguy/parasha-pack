# Deck v3 — Todo

Full plan: [docs/plans/2026-10-02-feat-deck-v3-improvements-plan.md](../docs/plans/2026-10-02-feat-deck-v3-improvements-plan.md)

Status: **Phase 1.1 mockups done, waiting for Simon's approval. Phase 2.6 partly done.** After a /clear, read `progress.md` first.

## Version control
- One PR per main feature; branch `<type>/<desc>` from `main`; squash on merge; every PR has a "Known issues" section.
- [x] `docs/deck-v3-plan`: plan, policies, mockups, progress
- [x] `fix/image-model-nano-banana-2` (#4): model fix; issues 1–3 fixed, 18 tests
- [x] `docs/deck-v3-plan` stacked on #4
- [x] `feat/character-library` (#5)
- [ ] `feat/card-back-v3` (Phase 1.2–1.5)
- [ ] `feat/deck-validator` (Phase 2)
- [ ] `feat/character-library` (Phase 3)
- [ ] `feat/agent-pipeline-v3` (Phase 4)
- [ ] `feat/styling-v2` (Phase 5)
- [ ] `feat/bereshit-deck` (Phase 6)
- [ ] hub: `feat/parashapacks-present-mode` (Phase 7, simonbrief-hub repo)
- [ ] `feat/extras-*` (Phase 8, one PR per extra or a small group)

## Decisions
- [x] D1–D6 (card count, values spine, Modern Orthodox, hard-text policy, booklet, Simon reviews)
- [x] D7 Default 8.5×11 letter (home printer, duplex, no bleed); 5×7 vendor print kept as optional export
- [x] D5b Teacher booklet = 8.5×11 letter
- [x] D8 Order: foundations → Bereshit → website → extras
- [x] D9–D13 Back design, projector + presenter window, hub URL per deck, Bereshit scope/טוֹב, extras v1

## Phase 1 — New card backs (letter)
- [x] 1.1 Letter-size mockups done: `docs/mockups/bereshit-v3.html` (10 backs, 3 fronts, 5×7 comparison; verified no overflow). **Waiting for Simon's approval.**
- [x] 1.2 `schemas/deck.v3.schema.json` (#6)
- [x] 1.3 `src/migrate_v2_to_v3.py`: Purim and Terumah migrated, plus `decks/bereshit/deck.json` (#6)
- [x] 1.4 Single `CardBack.tsx` + `CardFront.tsx`; letter frames; v3 palette + icons (#6)
- [x] 1.5 Duplex PDF export: letter 20 pp and 5×7 20 pp (#6)

## Phase 2 — Automatic checks
- [x] 2.1 `src/validate_deck.py` (#8)
- [x] 2.2 Export overflow/safe-zone guard (#8)
- [x] 2.3 Tests (139 pytest + 8 markup)
- [x] 2.4 Logging
- [x] 2.5 Housekeeping (#8)
- [~] 2.6 **Image model fix**: Nano Banana 2 via .env, `--size` (default 2K), skip thought images. Done in e893645: 15 tests pass, smoke call OK.
  - [x] 2.6a The 1K call returned 896×1200, not 768×1024. Run one 2K call to check whether `imageSize` is honored.
  - [x] 2.6b The API returns JPEG saved as `.png`. Save real PNGs.
  - [x] 2.6c Add `project.log` to `.gitignore`.

## Phase 3 — Character library + year plan
- [x] 3.1 `characters/` library (12 characters); duplicates retired or adapted (PR #5)
- [x] 3.2 Adam (v2) + Chava (v3) identity sheets; alternates kept (#7)
- [x] 3.3 `series.yaml`: 66 entries, 8 filled, validated (PR #5)
- [x] 3.4 `research/bereshit.yaml`: 10 verse ranges EN/HE + Rashi/Kohelet Rabbah (PR #5)

## Phase 4 — Agents
- [x] 4.1 00 planner, 02b sensitivity, 05b image QA, merge 03+04, 06 rubric, 07 → tool (#10)
- [x] 4.2 Per-agent schemas + `assemble_deck.py` (#10)
- [x] 4.3 Image QA rubric (flag-only) (#10)
- [ ] 4.4 3-layer docs pass (letter default + 5×7 optional)

## Phase 5 — Print-ready art
- [x] 5.0 Styling system v2 (10 changes + style_config.yaml) (#7)
- [x] 5.1 Draft 1K → final 2K (1792×2400); decide on upscaling or 4K after the test print
- [ ] 5.1b CMYK soft-proof for 5×7 target
- [x] 5.2 Prompt fixes (#7)
- [x] 5.3 Style plates generated; Simon approved (being committed in feat/styling-v2)
- [x] 5.4 Letter fronts (#6)
- [x] 5.5 SVG feeling faces (#6)

## Phase 6 — Bereshit deck
- [x] 6.1 Pipeline run with checkpoints (coordinator-approved, logged) (#12)
- [x] 6.2 10 cards (#12)
- [x] 6.3 Images: 18 drafts + 9 finals, $2.12 (#12)
- [~] 6.4 Validate + PDFs done; **home-printer test print is Simon's**
- [ ] 6.5 Metrics vs Purim

## Phase 7 — Hub website
- [x] 7.1 `scripts/sync_to_hub.py` (#9)
- [x] 7.2 Routes per deck; Purim/Terumah migrated; data.ts dropped (hub#4)
- [x] 7.3 Present mode
- [x] 7.4 Presenter window (BroadcastChannel; tested both ways)
- [x] 7.5 Print button
- [x] 7.6 Verify + hub PR #4 (re-sync after Bereshit art)

## Phase 8 — Extras
- [x] 8.1 Item art (13: 12 + Shabbat candles) (#11)
- [x] 8.2 Bingo ×10 (#11)
- [x] 8.3 I-spy (#11)
- [x] 8.4 Match-it (#11)
- [x] 8.5 Coloring + sequence (+ Days 1–7 strip) (#11)
- [x] 8.6 Following-directions story (#11)
- [x] 8.7 Sequencing game: mini cards + control strip (#11)
- [x] 8.8 Teacher guide booklet: 16 pp letter, page numbers checked (#11)
- [x] 8.9 Home card (in every deck) + family letter in the booklet
- [x] 8.10 Classroom pilot kit: docs/pilot (#11)

## Phase 9 — Purim retrofit (later)
- [x] 9.1 Content + Hebrew fixes, 12 cards, regenerated at 2K (#13); follow-ups: compress PDFs, recompose spotlight_2
