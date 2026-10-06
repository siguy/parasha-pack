# Progress — Deck v3

**Read this first after a /clear.** Then read `tasks/todo.md` (checklist) and `docs/plans/2026-10-02-feat-deck-v3-improvements-plan.md` (full plan). Corrections Simon has made are in `tasks/lessons.md`. Every judgment call made overnight on Simon's behalf is logged in `docs/overnight/decisions.md`. Open follow-ups are in `todos/` (on the top branch).

_Last updated: 2026-10-06 (morning after the overnight run)_

## Status: all planned phases built, as 13 stacked PRs, none merged

**Spend:** about $11.11 of the $15 cap (Nano Banana 2); Phase 10 day art was $1.75.
| Item | Cost |
|---|---|
| Style plates | $0.81 |
| Adam/Chava identities | $0.50 |
| Bereshit deck | $2.11 |
| Extras | $2.48 |
| Purim | $2.25 |
| Model tests | $0.17 |

### Merge order (bottom to top; squash each, then retarget the next to `main`)
| # | PR | Branch | What |
|---|---|---|---|
| 1 | [#4](https://github.com/siguy/parasha-pack/pull/4) | `fix/image-model-nano-banana-2` | Nano Banana 2 (`gemini-3.1-flash-image`), `--size` (default 2K), real PNG saves, dimension checks |
| 2 | [#3](https://github.com/siguy/parasha-pack/pull/3) | `docs/deck-v3-plan` | Plan, policies (values spine, hard-text), mockups, progress, decisions log |
| 3 | [#6](https://github.com/siguy/parasha-pack/pull/6) | `feat/card-back-v3` | v3 schema + migration, one CardBack/CardFront, letter (default) + 5×7 duplex PDFs |
| 4 | [#5](https://github.com/siguy/parasha-pack/pull/5) | `feat/character-library` | `characters/` library, `series.yaml` (66 decks), Sefaria research cache |
| 5 | [#7](https://github.com/siguy/parasha-pack/pull/7) | `feat/styling-v2` | Style plates, `style_config.yaml`, labeled refs, draft→final, spend ledger, Adam & Chava identities |
| 6 | [#8](https://github.com/siguy/parasha-pack/pull/8) | `feat/deck-validator` | Validator (budgets, Hebrew nikud and gender, characters, guide pages), export overflow/safe-zone guard |
| 7 | [#10](https://github.com/siguy/parasha-pack/pull/10) | `feat/agent-pipeline-v3` | Agents 00/02b/05b, merged 03+04, scored editor, `assemble_deck.py` |
| 8 | [#12](https://github.com/siguy/parasha-pack/pull/12) | `feat/bereshit-deck` | **Bereshit deck**: 10 cards, 2K art (QA 21–22/22), validator 0/0, PDFs (~6 MB, auto-compressed) |
| 9 | [#11](https://github.com/siguy/parasha-pack/pull/11) | `feat/extras` | Bingo ×10, I-spy, match-it, listen & do, coloring + sequence, mini cards, 16-page teacher booklet, pilot kit |
| 10 | [#13](https://github.com/siguy/parasha-pack/pull/13) | `feat/purim-v3` | **Purim v3**: Torah + Hebrew fixes, 12 cards, Persian (Achaemenid) art at 2K, PDFs (~8.5 MB) |
| 11 | [#9](https://github.com/siguy/parasha-pack/pull/9) | `feat/hub-sync` | `scripts/sync_to_hub.py` |
| 12 | [#14](https://github.com/siguy/parasha-pack/pull/14) | `docs/v3-final` | Docs reconciled across all 3 layers + `FOR_SIMON.md` |
| 14 | [#17](https://github.com/siguy/parasha-pack/pull/17) | `feat/bereshit-seven-days` | **Bereshit: a card for each day (13 cards)**, sequence-deck type, text-fidelity rules in every agent; 7-day extras (7-panel + easy 4-panel sequencing, mini cards, Days strip), a 19-page booklet, "Day N" backs, Day 5 sky softened, hub re-synced; 243 tests |
| 13 | [#15](https://github.com/siguy/parasha-pack/pull/15) | `fix/v3-followups` | Skip home-card art, block invalid hub sync, dead code; `todos/` |
| hub | [simonbrief-hub#4](https://github.com/siguy/simonbrief-hub/pull/4) | `feat/parashapacks-present-mode` | Per-deck pages, projector Present + presenter window, Print PDF. [Vercel preview](https://simonbrief-git-feat-parashapa-c7b7f9-simon-bs-projects-95643937.vercel.app/parashapacks) (needs a login) |

**Tests at the top of the stack:** 206 pytest + 8 markup tests pass. Bereshit and Purim both validate with 0 errors and 0 warnings.

## What Simon should check (morning review)
1. **Look at the art:**
   - Bereshit finals (PR #12) and Purim finals (PR #13).
   - Swap any pick from `alternates/` or `raw/drafts/`. Every pick is in `docs/overnight/decisions.md`.
2. **Hebrew review:**
   - Bereshit home-card question ״מָה הַדָּבָר הָאָהוּב עֲלֵיכֶם שֶׁה׳ בָּרָא?״
   - עוֹזְרִים, שׁוֹמְרִים
   - the Bereshit `value.he` שְׁמִירָה עַל הָעוֹלָם
   - Purim backs
3. **Test print:**
   - `decks/bereshit/print/bereshit-letter.pdf` on a home printer, double-sided, flip on the long edge.
   - Check margins, back alignment and legibility from about 3 m.
   - Then decide whether 2K is sharp enough on letter (about 230 DPI) or whether finals should upscale or move to 4K.
4. **Hub:** open the Vercel preview, try ▶ Present + the teacher window, and merge the hub PR when happy.
5. **Decisions to confirm:**
   - Bingo uses the 4-corners win rule.
   - The friendly snake appears in the games.
   - Adam and Chava wear muted clothing colors.
   - Purim spotlights are Esther and Mordechai; Haman and the king appear only in stories.
   - Bereshit's core cards total 26 minutes.

## Known issues / not working (details in each PR and in `todos/`)
- **Not test-printed:** cards, booklet and extras. Duplex alignment and printer margins (some extras use 0.35") are unverified.
- **Terumah:** still a v2 migration. It fails the v3 validator (17 errors), so the hub keeps its old v1 images and it has no PDF. The hub sync needs `--allow-invalid` for it.
- **Old templates:** `generate_deck.py` and `python -m workflows deck` still write v2 templates. The v3 path is pipeline 00→06 plus `assemble_deck.py`.
- **Review site:** still reads v2 fields.
- **Coloring line art:** busier than the spec (16–29 regions to color, target ≤12).
- **Titles:** faint gradient banding behind front titles.
- **Fonts:** PDFs load Google Fonts when built; offline they fall back to system fonts.
- **Purim art notes:** Haman's brow is a bit stern; the tradition_1 scroll curls at both ends; the tradition_3 coins show a "1"; one boy in connection_1 has no visible kippah.

## Where things live
- **Repo:** `siguy/parasha-pack`. Each PR has its own worktree under `.claude/worktrees/` (they can be cleaned up after merging). The coordinator worktree is `torah-deck-improvements-40976f` (branch `docs/deck-v3-plan`).
- **Hub:** `/Users/simonbrief/simonbrief-hub` (worktree `simonbrief-hub-parashapacks`).
- **Mockup preview:** `.claude/launch.json` defines a "mockups" server on port 8765.

## Rules that held overnight
- One PR per feature, stacked; squash on merge; every PR body has a "Known issues / not working" section.
- Subagents worked in their own worktrees; only the coordinator edited progress.md and tasks/todo.md.
- Hard budget through the spend ledger (`PP_SPEND_LEDGER`, `PP_BUDGET_USD`).
