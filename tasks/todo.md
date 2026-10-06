# Deck v3 — Todo

Full plan: [docs/plans/2026-10-02-feat-deck-v3-improvements-plan.md](../docs/plans/2026-10-02-feat-deck-v3-improvements-plan.md)

Status: **All phases built overnight (2026-10-05/06) as 13 stacked PRs (#3–#15) plus hub#4. Nothing merged.** After a /clear, read `progress.md` first.

## Version control
- One PR per main feature; branch `<type>/<desc>` from `main`; squash on merge; every PR has a "Known issues" section.
- [x] `docs/deck-v3-plan`: plan, policies, mockups, progress
- [x] `fix/image-model-nano-banana-2` (#4): model fix; issues 1–3 fixed, 18 tests
- [x] `docs/deck-v3-plan` stacked on #4
- [x] `feat/character-library` (#5)
- [x] `feat/card-back-v3` (#6)
- [x] `feat/deck-validator` (#8)
- [x] `feat/character-library` (#5)
- [x] `feat/agent-pipeline-v3` (#10)
- [x] `feat/styling-v2` (#7)
- [x] `feat/bereshit-deck` (#12)
- [x] hub: `feat/parashapacks-present-mode` (hub#4) + `feat/hub-sync` (#9)
- [x] `feat/extras` (#11), `feat/purim-v3` (#13), `docs/v3-final` (#14), `fix/v3-followups` (#15)

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
- [x] 2.6 **Image model fix**: Nano Banana 2 via .env, `--size` (default 2K), skip thought images. Done in e893645: 15 tests pass, smoke call OK.
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
- [x] 4.4 3-layer docs pass (#14)

## Phase 5 — Print-ready art
- [x] 5.0 Styling system v2 (10 changes + style_config.yaml) (#7)
- [x] 5.1 Draft 1K → final 2K (1792×2400); decide on upscaling or 4K after the test print
- [ ] 5.1b CMYK soft-proof for 5×7 target (not done; only matters for vendor print)
- [x] 5.2 Prompt fixes (#7)
- [x] 5.3 Style plates generated; Simon approved (being committed in feat/styling-v2)
- [x] 5.4 Letter fronts (#6)
- [x] 5.5 SVG feeling faces (#6)

## Phase 6 — Bereshit deck
- [x] 6.1 Pipeline run with checkpoints (coordinator-approved, logged) (#12)
- [x] 6.2 10 cards (#12)
- [x] 6.3 Images: 18 drafts + 9 finals, $2.12 (#12)
- [~] 6.4 Validate + PDFs done; **home-printer test print is Simon's**
- [x] 6.5 Metrics: Bereshit took 27 calls for 10 cards (2.7 per card, half of them cheap drafts) vs Purim v2's 39 for 16; no redos

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

## Review (2026-10-06)
- **Built:** every phase in this list except the CMYK soft-proof (5.1b) and the Year-2 question bank / Hebrew word wall / packaging / AI-disclosure items (7.4–7.7), which were never in tonight's scope. 2 decks (Bereshit new, Purim retrofit), 8 extras, a teacher booklet, the hub present mode.
- **Quality bar:** 206 tests; both decks validate with 0 errors; every image went through the QA rubric (Bereshit 21–22/22, Purim 19–22/22); PDFs pass the overflow/safe-zone guard; hub build is clean and the Vercel deploy passed.
- **Cost:** $8.33 of the $15 cap.
- **Not verified:** physical test print; the Vercel preview behind its login (checked locally only); classroom use.
- **Lessons:** recorded in `agents/LESSONS_LEARNED.md` and `FOR_SIMON.md` (#14), plus `tasks/lessons.md`.

## Phase 10 — A card for each day of creation (Simon, 2026-10-06)
Decisions: fold "Adam names the animals" into Adam's spotlight; **art: regenerate all 7 days with the new creation as the focal hero** (cumulative scenes are too busy; reuse didn't show the build-up); add a general "sequence deck" type (the story count comes from series.yaml).
Branch `feat/bereshit-seven-days` on top of `fix/v3-followups` (#15). **PR #17.** Art: Days 1–7 scored 26–28/28 on QA; $1.75. Extras, a 19-page booklet, "Day N" backs, Day 5 sky softened, and the hub re-synced are all done ($1.04).
- [x] 10.1 series.yaml `deck_pattern: sequence` + `story_cards: N`; schema/validator/assemble/guide_layout read the count from there (normal decks stay at 10/12)
- [x] 10.2 Bereshit deck: 13 cards (anchor, Days 1–7 as story_1..7, Adam, Chava, connection, טוֹב, home); cumulative gestures; new week plan (Fri = Day 7 + טוֹב + home)
- [x] 10.3 Art (final, Simon): each day's NEW creation is the large hero, with earlier creations soft in the background (setting kept consistent via continuity refs); Days 1–2 drawn concretely; Day 7 = the whole world resting (the only cumulative scene); cap $2.30
- [x] 10.4 Booklet one page per day; extras: 7-panel + easy 4-panel sequencing, 7 mini cards
- [x] 10.5 PDFs (letter + 5×7), validator 0/0, hub re-sync, PR with known issues
- [x] 10.6 Text fidelity in the pipeline: Torah Scholar text map (text_ref, key_hebrew, in_text, not_in_text, midrash); 02/03/05 draw only from in_text; 02b/06/05b check it; schema + validator require text_ref/key_hebrew on story cards
