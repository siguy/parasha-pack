# Progress — Deck v3

**Read this first after a /clear.** Then read `tasks/todo.md` (checklist) and `docs/plans/2026-10-02-feat-deck-v3-improvements-plan.md` (full plan). Corrections Simon has made are in `tasks/lessons.md`.

_Last updated: 2026-10-05_

## Where things live
- **Repo:** `siguy/parasha-pack`. Work happens in the worktree `/Users/simonbrief/parasha-pack/.claude/worktrees/torah-deck-improvements-40976f`.
- **Hub site (Phase 7):** `/Users/simonbrief/simonbrief-hub` (`siguy/simonbrief-hub`, Next 16, deployed on Vercel). The parasha pages are in `app/parashapacks/`.
- **Mockup preview:** `.claude/launch.json` defines a "mockups" server (python http.server on port 8765). Open `http://localhost:8765/docs/mockups/bereshit-v3.html`.

## Version control (one PR per main feature)
| Branch | PR | Status |
|---|---|---|
| `docs/deck-v3-plan` | [#3](https://github.com/siguy/parasha-pack/pull/3): plan, policies, mockups, progress | open, docs only |
| `fix/image-model-nano-banana-2` | [#4](https://github.com/siguy/parasha-pack/pull/4): Nano Banana 2 + `--size` flag | open; follow-up fixes for issues 1–3 in progress (separate worktree `.claude/worktrees/fix-image-model`) |
| `feat/character-library` | [#5](https://github.com/siguy/parasha-pack/pull/5): character library, series.yaml (66 entries), Sefaria cache | open; 58 tests pass; built in parallel, will be rebased onto the card-back PR |
| `feat/card-back-v3` | [#6](https://github.com/siguy/parasha-pack/pull/6): v3 schema, migration, single CardBack/CardFront, letter + 5×7 duplex PDF | open; build + lint clean; Bereshit fits both formats; Purim backs overflow (expected); title text-stroke fixed (18446af) |
| `feat/deck-validator` | [#8](https://github.com/siguy/parasha-pack/pull/8): validator, Hebrew gender check, export overflow/safe-zone guard, guide_layout.yaml, housekeeping | open; rebased onto #7; 139 tests; Bereshit PASS (0 errors, 13 TODO warnings); Purim 19 errors and Terumah 17 (expected; the gender check caught גִּבּוֹר on Esther's card) |
| `feat/extras` | [#11](https://github.com/siguy/parasha-pack/pull/11): **now also part B**: coloring + sequence pages, a Days 1–7 strip, sequencing mini cards + control strip, a 16-page letter teacher booklet (page numbers checked against guide_layout), and a pilot kit (docs/pilot); rebased onto #12; 197 tests; part B spent $0.40. Part A: 13 item pictures (color + line + cutout), bingo ×10 + calling cards, I-spy (easy 15 / challenge 23 + answer keys + coloring version), match-it (2 sets + bonus), listen & do (2 levels + answer key) | open; 153 tests; $2.08 spent; base #8, to be restacked onto bereshit; part B (coloring + sequence, mini cards, booklet) waits for Bereshit art |
| `feat/hub-sync` | [#9](https://github.com/siguy/parasha-pack/pull/9): `scripts/sync_to_hub.py` (+4 tests) | open; base #6, so it needs restacking onto the top of the chain |
| hub `feat/parashapacks-present-mode` | [siguy/simonbrief-hub#4](https://github.com/siguy/simonbrief-hub/pull/4): gallery, per-deck pages, Present + presenter (BroadcastChannel), Print PDF; `data.ts` removed | open; lint and build clean; Vercel preview builds (login required): https://simonbrief-git-feat-parashapa-c7b7f9-simon-bs-projects-95643937.vercel.app/parashapacks. Sync verified in both directions. Re-run the sync after the Bereshit and Purim PRs. Terumah has no PDF (no scene-only art). |
| `feat/styling-v2` | [#7](https://github.com/siguy/parasha-pack/pull/7): style plates, style_config.yaml, labeled refs, draft→final, spend ledger, Adam & Chava identities | open; 113 tests; rebased onto #5 |
| `feat/agent-pipeline-v3` | [#10](https://github.com/siguy/parasha-pack/pull/10): agents 00, 02b, 05b; 03+04 merged; 06 scored rubric; 07 moved to tools; pipeline schemas; assemble_deck.py; contact_sheet.py | open; rebased onto #8; 165 tests (fixture got the power-word trio the validator requires) |
| `feat/bereshit-deck` | [#12](https://github.com/siguy/parasha-pack/pull/12): Bereshit, 10 cards through pipeline 00→06, 9 finals at 2K (QA 21–22/22, no redos), validator 0 errors / 0 warnings, editor 93.2%, letter + 5×7 PDFs | open; $2.12; PDF compression being added (they were 57 MB); faint gradient banding behind titles; core cards total 26 min; not test-printed |
| `feat/purim-v3` | [#13](https://github.com/siguy/parasha-pack/pull/13): Purim v3: all audit Torah + Hebrew fixes, 12 cards, Persian (Achaemenid) art at 2K (QA 19–22), validator 0/0, editor 97.5%, letter + 5×7 PDFs (24 pp) | open; $2.02; PDFs 76 MB (compress after restacking onto #12/#11); spotlight_2 still has domes/arch (recompose); see the PR for minor art notes |
| `claude/torah-deck-improvements-40976f` | Original session branch (holds everything). Superseded by the two branches above; do not open a PR from it. | — |

Rules: branch from `main` as `<type>/<short-description>`. When a feature depends on an unmerged PR, branch from that PR's branch and say so in the PR body. Squash on merge (Simon's default). Every PR body has a **Known issues / not working** section.

## Overnight run (started 2026-10-05, Simon asleep)
**Decisions Simon made before the run:**
- **Checkpoints:** I make each pick that would normally wait for Simon, using the image QA rubric. The runners-up go in an `alternates/` folder next to each chosen file, and each pick and its reason is logged in `docs/overnight/decisions.md`. The mockup is treated as approved.
- **Image budget:** a hard cap of **$15**. Every API call is appended to the spend ledger `/private/tmp/claude-501/-Users-simonbrief-parasha-pack--claude-worktrees-torah-deck-improvements-40976f/2d123642-4920-472e-bfd5-1e929b9f21d4/scratchpad/spend_ledger.jsonl` (`{ts, branch, purpose, size, usd}`). Check the total before every call, and stop generating at $14.
  - Prices for Nano Banana 2: 512 $0.045 (est.), 1K $0.067, 2K $0.101, 4K $0.151.
  - Priority order for the money: style plates → Adam/Chava → Bereshit → extras → Purim.
- **PRs:** stacked and **not merged**. Simon merges them in order in the morning.
- **Scope:** a simonbrief-hub PR with a Vercel preview (not merged); Purim and Terumah moved to the new hub pages; the Purim content fixes (Phase 9); keep the Mac awake.

**PR chain (each branches from the one before):**
`main ← #4 fix/image-model-nano-banana-2 ← #3 docs/deck-v3-plan ← feat/card-back-v3 ← feat/deck-validator ← feat/character-library ← feat/styling-v2 ← feat/agent-pipeline-v3 ← feat/bereshit-deck ← feat/extras ← feat/purim-v3`
- Hub: `siguy/simonbrief-hub` branch `feat/parashapacks-present-mode`, a separate PR.
- Branches built in parallel are rebased onto the chain when they finish.

**Chain now:** #4 ← #3 ← #6 ← #5 ← #7 ← #8 ← #10 ← #12 ← #11 ← #13 (Purim restack in progress) ← #9 hub-sync (to restack) ← final docs. The agent-pipeline branch (built on #7) is rebased onto #8 when it finishes; extras (on #8) is rebased onto bereshit.
**Re-stacking (2026-10-05 23:20):** #5 rebased onto #6, #7 onto #5. Still to do at the end of the night: rebase #6 onto the #3 tip (it gained decision-log commits) and cascade up; rebase the validator onto #7 and hub-sync onto the validator. Original note: #5 and styling-v2 were built on `docs/deck-v3-plan`. Rebase them onto `feat/card-back-v3` (#6), and the validator onto styling-v2. The final chain is #4 ← #3 ← #6 ← #5 ← styling ← validator ← agents ← bereshit ← extras ← purim; hub-sync is rebased onto bereshit later.

**Waves:**
1. card-back-v3 ‖ character-library (code only, no image generation yet)
2. deck-validator ‖ styling-v2 (style plates and Adam/Chava identity sheets generated here)
3. agent-pipeline-v3 ‖ hub (Purim and Terumah on the new routes)
4. bereshit-deck (content from agents 00→06, then images, QA, PDF)
5. extras ‖ hub (adds Bereshit) ‖ purim-v3
6. Final: docs pass, FOR_SIMON.md, morning summary

**Rules for subagents:** use your own worktree; don't edit progress.md or tasks/todo.md (the main session owns them); every PR body has a Known issues section; tests must pass.

## Done
- **Research (2026-10-02/05):**
  - audits: deck and backs, pipeline, imagery
  - outside research: education standards, competitor products, 4K / Nano Banana
  - designs for the extras: bingo, I-spy, match-it, coloring + sequence, following directions, booklet, home card, pilot
  - All findings are summarized in the plan.
- **Decisions D1–D13** (see plan). Key ones:
  - letter is the default card, with 5×7 as an optional export
  - Modern Orthodox framing
  - the teacher booklet is letter size
  - Nano Banana 2 at 2K
  - all 10 styling changes adopted (process and consistency only; **the art style stays the same as Purim**)
- **Policies (drafts adopted):** `docs/policies/values-spine.md`, `docs/policies/hard-text-policy.md`.
- **Mockups:**
  - `docs/mockups/back-v3.html`: Purim, 7 back types at 5×7, before/after comparison.
  - `docs/mockups/bereshit-v3.html`: all 10 Bereshit backs at letter size, 3 fronts with title-zone and 5:7-crop guides, and the same design at 5×7. Checked in the browser: no overflow; aspect ratios 1.294 (letter) and 1.381 (5×7 with bleed) are correct. **Waiting for Simon's approval.**
- **Step 2.6, image model fix (PR #4, commit 15090e8):**
  - The model now comes from `GEMINI_IMAGE_MODEL`, defaulting to `gemini-3.1-flash-image`.
  - `--size 512|1K|2K|4K`, default 2K.
  - Skips the model's interim "thought" images; timeout raised to 300s.
  - Dimensions are logged; `model` and `image_size` are recorded in generations.jsonl.
  - 15 pytest tests pass. The smoke call succeeded.

## Known issues / NOT working
0. From PR #7:
   - Chava v1 and v2 looked childlike, so v3 was generated with an adult anchor.
   - Adam and Chava wear muted earth tones (Simon may want brighter).
   - Adam's hands look slightly mitten-like.
   - Hex palette codes could be drawn as text; watch the first drafts.
   - Purim needs `story_world_setting: indoor` before it is regenerated.
   - Spend so far: $1.48.
   From PR #5:
   - Esther's identity image has caption text (styling-v2 is cleaning it).
   - `noach` has no character entry yet.
   - avraham, sarah and pharaoh are drafts (`canonical: false`).
   - `python workflows.py` is replaced by `python -m workflows`.
1. **The image size setting may be ignored.** The 1K smoke call returned **896×1200**, but the docs say Nano Banana 2 at 1K and 3:4 should be 768×1024. Either `imageSize` is ignored, or the expected-size table is wrong. Next step: one 2K call (~$0.10) to tell which. If 2K also returns 896×1200, the field is ignored and needs debugging.
2. **Image files are mislabeled.** The API returns JPEG data, which we save with a `.png` name. This has probably always been the case. Fix: convert to real PNG with Pillow on save, or save as `.jpg`.
3. **`project.log` is not in `.gitignore`.**
4. Old issues from the audits, not yet fixed:
   - backs overflow and are silently truncated (spotlight_3, connection_1)
   - `review-site` registry path is broken
   - `sync-deck.sh` never deletes stale files
   - Purim content and Hebrew errors (see plan Phase 9)

## Next steps (in order)
1. Simon reviews `docs/mockups/bereshit-v3.html` (and checks the Hebrew flagged on the page).
2. Fix the known issues 1–3 on the `fix/image-model-nano-banana-2` branch (a subagent is working on this; check PR #4 for status).
3. Phase 1.2–1.5: v3 schema, migration script, single `CardBack.tsx`, letter/5×7 PDF export. New branch `feat/card-back-v3`.
4. Phase 2: validator, export guard, tests (`feat/deck-validator`).
5. Then Phase 3 → 9 as in `tasks/todo.md`.
