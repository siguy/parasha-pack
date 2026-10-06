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
| `docs/deck-v3-plan` | Plan, policies, research decisions, mockups, progress | open (see PR list) |
| `fix/image-model-nano-banana-2` | Nano Banana 2 + `--size` flag | open, with known issues (below) |
| `claude/torah-deck-improvements-40976f` | Original session branch (holds everything). Superseded by the two branches above; do not open a PR from it. | — |

Rules: branch from `main` as `<type>/<short-description>`. When a feature depends on an unmerged PR, branch from that PR's branch and say so in the PR body. Squash on merge (Simon's default). Every PR body has a **Known issues / not working** section.

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
  - all 10 styling changes adopted
- **Policies (drafts adopted):** `docs/policies/values-spine.md`, `docs/policies/hard-text-policy.md`.
- **Mockups:**
  - `docs/mockups/back-v3.html`: Purim, 7 back types at 5×7, before/after comparison.
  - `docs/mockups/bereshit-v3.html`: all 10 Bereshit backs at letter size, 3 fronts with title-zone and 5:7-crop guides, and the same design at 5×7. Checked in the browser: no overflow; aspect ratios 1.294 (letter) and 1.381 (5×7 with bleed) are correct. **Waiting for Simon's approval.**
- **Step 2.6, image model fix (commit e893645):**
  - The model now comes from `GEMINI_IMAGE_MODEL`, defaulting to `gemini-3.1-flash-image`.
  - `--size 512|1K|2K|4K`, default 2K.
  - Skips the model's interim "thought" images; timeout raised to 300s.
  - Dimensions are logged; `model` and `image_size` are recorded in generations.jsonl.
  - 15 pytest tests pass. The smoke call succeeded.

## Known issues / NOT working
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
2. Fix the known issues 1–3 on the `fix/image-model-nano-banana-2` branch.
3. Phase 1.2–1.5: v3 schema, migration script, single `CardBack.tsx`, letter/5×7 PDF export. New branch `feat/card-back-v3`.
4. Phase 2: validator, export guard, tests (`feat/deck-validator`).
5. Then Phase 3 → 9 as in `tasks/todo.md`.
