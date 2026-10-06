---
title: "Deck v3: Letter-Size Cards, Bereshit, Web Present Mode, Extras"
type: feat
date: 2026-10-02
revised: 2026-10-05
status: decisions locked (2 grilling rounds); awaiting Simon's go to execute Phase 1
---

# Deck v3: Letter-Size Cards, Bereshit, Web Present Mode, Extras

## Context

The Purim deck (v2) works, but research found three blockers to scaling to 54 parshiyot plus about 12 holidays:

1. The backs are overloaded: 80–143 words, and some are silently cut off.
2. The art isn't print-ready: 896×1200 px, about 179 DPI.
3. Nothing is checked automatically: no validator and no tests, character data lives in 5 places, and the YAML is merged by hand.

Simon wants these fixed, then **Bereshit** built as the first deck on the new system. He also wants a **web version on simonbrief-hub** that teachers project in class, and a set of **printable extras**.

**Big change since the first draft (2026-10-05):** the **default card is 8.5×11 letter, printed on a school or home printer.** Each card is one sheet printed double-sided, with art on the front and the teacher back on the back. It has a white margin and needs no cutting. **5×7 stays as a second, optional export target** (vendor print, 0.125" bleed, CMYK proof) so the decks can be printed professionally later, with no redesign.

## Decisions (locked)

| # | Decision |
|---|---|
| D1 | 10 cards standard / 12 holiday. A holiday deck replaces 1 story card with 3 tradition cards. |
| D2 | Values spine: `docs/policies/values-spine.md` (draft adopted). Bereshit = **caring for Hashem's world**. |
| D3 | Modern Orthodox. Midrash is introduced as "Our Sages teach…". Adam and Chava wear **simple, modest, full-coverage tunics**. |
| D4 | Hard-text policy: `docs/policies/hard-text-policy.md` (draft adopted). The snake and the fruit appear **only in the guide booklet**. |
| D5 | Printed teacher guide booklet, **8.5×11 letter** (stapled at the corner or hole-punched). Backs show "📖 Guide p.N", with page numbers taken from a fixed page map. |
| D6 | Simon is the only reviewer. |
| D7 | **Default card = 8.5×11 letter, duplex, home printer, no bleed, ~0.3" white margin.** **Optional target = 5×7 vendor print (5.25×7.25" with bleed, 0.25" safe zone, CMYK soft-proof).** Both exported as PDF from the same layouts. |
| D8 | Order: **foundations first → Bereshit → website → extras.** |
| D9 | Back design = refine `docs/mockups/back-v3.html` (bold = say, chips = do, ≤50 words, ★ CORE). |
| D10 | Web: **projector/smartboard Present mode + a separate presenter window** (laptop) that stays in step with it. |
| D11 | Hub: every deck gets its own URL (`/parashapacks/{deck}`). A sync script fills the hub from deck.json, with no hand-copying. |
| D12 | Bereshit stories: ① Days 1–3 ② Days 4–6 ③ Shabbat ④ Adam names the animals and cares for Gan Eden. Power word **טוֹב** (thumbs-up gesture, from "and it was good" ×7). |
| D13 | Bereshit extras v1: coloring + sequence pages, bingo (10 boards), I-spy, match-it, and the following-directions story. Also the booklet and the home card. |

---

## How to resume after a /clear

Read `progress.md`, then `tasks/todo.md`, then this plan. `progress.md` holds the branch and PR table, what works, and **what doesn't work yet**. Update all three files after each completed step, and commit them.

## Version control

- One PR per main feature, on a branch named `<type>/<short-description>` from `main`.
- If a feature depends on an unmerged PR, it branches from that PR's branch, and the PR body says so.
- Squash on merge.
- Every PR body includes: summary, how to verify, tests run, **Known issues / not working**, follow-ups.
- Subagents do the implementation work, one focused task each. The main session reviews, verifies and opens the PRs.

## Phase 1 — New card backs (letter size)

**Goal:** the new back design, a v3 deck format, and one component for all back types. Export a duplex PDF.

- 1.1 Rebuild the mockup at **letter proportions** (8.5:11) with Bereshit content for all 7 back types, plus the front layout at letter size. Show both to Simon side by side.
- 1.2 `schemas/deck.v3.schema.json`. Each card's back holds:
  - `back: {objective, say, ask[{text,type}], hebrew{word,translit,meaning,gesture}, minutes, core, transition, guide_ref}`
  - plus `guide: {pshat{text,refs}, sages[{text,source}], hard_questions[{q,answer,redirect}], adapt{see,do,join}, extend, tip}`
  - No field aliases.
- 1.3 `src/migrate_v2_to_v3.py`: moves fields mechanically. It's for Purim and Terumah so they can appear on the hub; it doesn't rewrite content.
- 1.4 Card Designer:
  - **Fronts:** one `CardBack.tsx` driven by a per-type config replaces the 6 `*CardBack.tsx` files. It parses `**bold**` and `[cue]` markup and has no `overflow-hidden`.
  - **Sizes:** `CardFrame`/`CardBackFrame` change from `aspect-[5/7]` to letter. The px font sizes in `CardBackFrame.tsx`/`BackSection.tsx` are re-calibrated for letter.
  - **Colors:** the v3 palette, which passes AA contrast (WCAG's minimum for readable text): Tradition becomes teal, gold becomes darker, and each type gets its own icon.
- 1.5 `card-designer/scripts/export-deck.ts`:
  - Add `--format letter|5x7` (default `letter`). Sizes and margins come from one `print_formats.json`: letter is 8.5×11 with a 0.3" margin; 5x7 is 5.25×7.25 with 0.125" bleed and a 0.25" safe zone.
  - Layouts use relative units (cqw/%), so the same component renders both formats.
  - Add `--pdf`, which uses Playwright `page.pdf()` at the format's size so text stays sharp.
  - Pages go front₁, back₁, front₂… for duplex printing (flip on long edge).
  - Keep PNG export for the web.

## Phase 2 — Automatic error checks

- 2.1 `src/validate_deck.py` (with pydantic or jsonschema). It runs before image generation, export and hub sync. It checks:
  - word budgets: say ≤50, ask ≤2×12, objective ≤10
  - required fields for each card type, and the card count (D1)
  - `characters_in_scene` ⊆ the character library, and every character named in `image_prompt` is listed
  - Hebrew: nikud is present, and the unpointed text matches the pointed text
  - **grammatical gender against the character's gender**
  - transitions don't refer to card order
  - banned prompt terms
  - every `guide_ref` page exists in the guide page map
- 2.2 Export guard in `export-deck.ts`: any section whose `scrollHeight > clientHeight`, or whose text falls outside the safe zone, **fails the export** and reports the card id.
- 2.3 Tests: pytest for the validator, the migration and `build_generation_prompt()`, plus a parser test for the bold/cue markup.
- 2.4 Logging to `project.log`, with the source name and record count at each step.
- 2.6 **Image model fix (blocks all generation, including Adam and Chava in Phase 3).** The 4K research found:
  - **Model:** the hardcoded `nano-banana-pro-preview` alias most likely points to `gemini-3-pro-image-preview`, which Google shut down on 2026-06-25. **Switch to Nano Banana 2, `gemini-3.1-flash-image`** (Simon, 2026-10-05: cheaper and still very good). Read the model from `GEMINI_IMAGE_MODEL` in `.env`, so Pro (`gemini-3-pro-image`) is a one-line switch for any card that needs it. This applies in `src/generate_images.py` and `src/generate_references.py`.
  - **Size flag:** add `imageConfig.imageSize` and a `--size 512|1K|2K|4K` flag. The value must be uppercase; lowercase `"4k"` is rejected. **Default is 2K.**
  - **Timeout:** raise it from 180s to 300s.
  - **Draft-image bug:** skip parts marked `thought: true`. The model always "thinks" and can return draft images; the current parser saves the first image part, which may be a draft.
  - **Size check:** after saving, read the pixel size with Pillow and log it. 2K at 3:4 should be 1536×2048. Nano Banana 2 allows **up to 4 character references** and 3 style references per image, and the validator enforces that limit.
  - Smoke test: one 1K call. Then update the "nano-banana only" notes in CLAUDE.md and memory.
- 2.5 Housekeeping:
  - `sync-deck.sh` uses `rsync --delete`
  - fix the review-site registry path
  - remove the hard-coded `terumah` from `card-designer/app/page.tsx`
  - delete `raw-v1-borders/`, `*_pre_hero.png`, `deck_v*_backup.json`, `approval_stats.yaml`

## Phase 3 — Shared character library + year plan

- 3.1 `characters/{key}/identity.png` + `character.yaml` holding: canonical flag, version, gender (used by the Hebrew check), and locked visual anchors such as headwear and beard.
  - Migrate Moshe, Yitro, Miriam (archive) and Esther, Mordechai, Haman, Achashverosh (Purim).
  - `load_reference_images()` in `src/generate_images.py` will look characters up here.
  - Retire `CHARACTER_DATABASE` (research.py), `DEFAULT_DESIGNS` (workflows/character.py) and `CHARACTER_DESIGNS` (schema.py).
- 3.2 New identity sheets for **Adam and Chava**, 2 versions each, Simon picks. Each sheet shows a 3-angle turnaround plus an expression row, on a plain background, with **no caption text**, and modest tunics.
- 3.3 `series.yaml`: all 66 entries in skeleton form (name, book, holiday position, status). Fill in middah, power word and characters for Bereshit through Lech Lecha, plus the fall holidays. The rest stay as `TBD`.
- 3.4 `research/{parasha}.yaml` cache from Sefaria, starting with Bereshit: key verses EN/HE plus 1–2 commentaries. Extend `src/sefaria_client.py`.

## Phase 4 — Agent changes

Order: **00 Series Planner** → 01 Torah Scholar (reads the research cache and cites verses) → 02 Curriculum Designer → **02b Sensitivity Reviewer** (★ Simon checkpoint) → **03 Content Writer + Hebrew (merged)** → validate → 05 Visual Director → generate → **05b Image QA (vision)** (★ Simon picks) → 06 Editor (scored rubric) → assemble → export → hub sync.

- 4.1 New `agents/definitions/00-series-planner.md`, `02b-sensitivity-reviewer.md` and `05b-image-qa.md`. Merge 03 and 04 into one file. 06 becomes a scored rubric. 07 moves to `tools/card-designer.md`.
- 4.2 A schema for each agent's YAML output (`schemas/pipeline/*.schema.json`) and an `src/assemble_deck.py` that merges the YAML into deck.json, replacing the hand merge.
- 4.3 Image QA rubric. The checks:
  - title zone clear
  - characters match their identity sheets
  - no stray text
  - hands look right
  - modesty and kippah rules
  - villain posture
  - God shown only as light
  - period accuracy
  - diversity
  - emotion readable at 8% scale

  Start in **flag-only** mode.
- 4.4 Docs pass across all three layers: CLAUDE.md, src/ and decks/ CLAUDE.md, agents/*, CARD_SPECS, VISUAL_SPECS, README, CHANGELOG. **Print specs: letter becomes the default and 5×7 stays documented as the optional vendor target.** Grep the docs for old terms.

## Phase 5 — Print-ready art at letter size

- 5.1 **Nano Banana 2 at 2K** (1536×2048, $0.101/image, $0.050 batch). Draft at 1K ($0.067), final at 2K. About $3–4 per deck including extras.
  - **Resolution:** 2K gives about 282 DPI on 5×7 and **about 195 DPI on letter**. Both look fine from circle-time distance; letter may look a little soft up close.
  - **Decision gate at the 6.4 test print.** If letter looks soft, either upscale 2× locally with Real-ESRGAN (free, illustration model) or switch only the finals to 4K ($0.151).
  - The upscaler is an optional `--upscale` export step.
- 5.1b CMYK soft-proof script for the 5×7 vendor target only (FOGRA39/GRACoL). It flags out-of-gamut purple and blue.
- 5.0 **Styling system v2** (all 10 adopted by Simon, 2026-10-05). **Keep the current art style unchanged** (Simon, 2026-10-05): the existing Purim look worked. The style plates are made *from* the current Purim art so they reproduce it. Leave `STYLE_ANCHORS_V2` as it is, apart from the specific fixes in 5.2. These 10 changes are about consistency and process; none of them changes the look.
  1. **Series style plates**: 3–4 images with no characters (landscape, interior, object close-up, modern classroom), passed with every generation. They replace the per-deck `style_hero`. The text style card shrinks to specifics: line weight, flat color with one soft gradient, eye style, head:body about 1:3, lighting.
  2. **Per-deck 5-color palette** in deck.json. It drives both the prompts and the hub's `web_theme`, so print and web match.
  3. **Crops that work for both sizes**: the top 22% is calm for the title; key subjects sit in the central 90% of the width (letter 0.77 / 5:7 0.714); a simple ground plane replaces the lower-left shadow.
  4. **Draft cheap, then finalize**: 2–3 drafts at 1K, Simon picks one, and the final is made at 2K with the chosen draft passed as a composition reference.
  5. **Locked character anchors** from `characters/{key}/character.yaml`, added to the prompt automatically instead of typed into each deck prompt.
  6. **Labeled references** in the prompt ("Image 1 = style plate, Image 2 = Adam identity…").
  7. **Image QA after every image** (vision rubric, flag-only to start).
  8. **Story continuity**: the previous story card is passed as a reference when the scene is the same. In Bereshit, ①→② show the same landscape filling up.
  9. **Thick clean outlines on purpose**, so the art turns into coloring pages reliably.
  10. **`prompt_version`** written in `generations.jsonl`.
  - Also: move `IMAGE_SAFETY_RULES` out of `schema.py` and the style text out of `image_prompts.py` into one `style/style_config.yaml`, shared by the Visual Director, the prompt builder and Image QA.
- 5.2 `src/image_prompts.py`:
  - drop the "darker lower-left" lines
  - add "top 25% calm for the title", "at most 5 figures in focus"
  - add the named ethnic mix, kippah rules and a villain-posture rule to `MODERN_WORLD_STYLE`
- 5.3 Generate the series style plates (see 5.0.1). Simon picks from 2 versions each.
- 5.4 Fronts at letter size:
  - FitText padding ≥5% and title max-width 85%
  - gradient `from-black/65`
  - subtitles readable from 3 m away
  - one title treatment for every card
  - a type icon in the corner
- 5.5 Licensed SVG feeling-faces instead of Apple emoji.

## Phase 6 — Build Bereshit (first deck on the new pipeline)

- 6.1 Run agents 00→06. Simon checkpoints after 02b and after image QA.
- 6.2 Cards (10):
  - Anchor: "In the beginning", with light as the symbol
  - Spotlight: Adam, Chava
  - Stories ①–④ as in D12
  - Connection: "Taking care of our world"
  - Power word: טוֹב
  - Home card
- 6.3 Expected image cost: about 30 drafts at 1K plus about 15 finals at 2K plus 4 identity sheets plus 4 style plates, **about $4**. Commit a checkpoint first.
- 6.4 Validate, export the duplex PDF, and print a test copy on a real home printer. Check margins, duplex alignment, and legibility at 3 m.
- 6.5 Record human-minutes and generations per card, to compare with Purim (39 generations for 16 cards).

## Phase 7 — Website on simonbrief-hub (`/Users/simonbrief/simonbrief-hub`, Vercel)

Existing: `app/parashapacks/` has `page.tsx` (one page with a DeckPicker), `deck-view.tsx`, `ui.tsx` (FlipCard, CardImage) and a hand-written `data.ts`. The kid-art styling (Fredoka, `.pp-pop` stickers, dotted paper, per-deck `DeckTheme`) lives in `parashapacks.css`. **Next 16 has breaking changes, so read `node_modules/next/dist/docs/` first (from AGENTS.md).**

- 7.1 Sync script in parasha-pack, `scripts/sync_to_hub.py`:
  - runs the validator
  - writes `simonbrief-hub/app/parashapacks/decks/{id}.json`
  - writes compressed WebP images to `public/parashapacks/{id}/`
  - copies the print PDF
  - Each deck.json gains `web_theme {primary, secondary, accent, wash}`.
- 7.2 Routes:
  - `/parashapacks`: gallery of all decks
  - `/parashapacks/[deck]`: deck page that reuses `DeckView`, with ▶ Present and 🖨 Print buttons
  - `/parashapacks/[deck]/present`: full-screen kid view
  - `/parashapacks/[deck]/presenter`: teacher view

  Purim and Terumah move to the new routes via the migration script; `data.ts` is removed.
- 7.3 **Present mode**, the kid-facing screen, in the same kid-art language with the deck's theme colors:
  - Full-screen card art, plus a big title in Fredoka with Hebrew.
  - Clicker or arrow keys move between cards. Optional confetti `Burst` on the power word.
  - Cards are grouped into the 5-day week, and a "Day 1 / Day 2…" picker jumps to that day's cards.
- 7.4 **Presenter window** (opens with P, on the laptop):
  - shows the current card's back: SAY with cues, ASK, Hebrew word and gesture, minutes
  - shows the next card's thumbnail and a circle timer
  - stays in step with the projector through `BroadcastChannel` (a browser feature that lets two windows of the same site exchange messages). No server needed.
- 7.5 Print button: downloads the deck's duplex PDF plus the extras PDFs.
- 7.6 Verify with `next build`, the Present + Presenter pair in two windows, and a check at phone and tablet widths. Open a PR on the hub repo. Simon reviews the Vercel preview before merging.

## Phase 8 — Extras, booklet, home card, pilot

All extras are generated from deck.json plus a few extra images by `src/generate_activities.py`. It renders HTML templates and prints them to letter PDFs with Playwright, the same tool as the card export.

- 8.1 **Item art (shared base).** 12 vocabulary items, each as color + line art on white, about 24 generations:
  - Bereshit's 12: אוֹר light, שָׁמַיִם sky, מַיִם water, עֵץ tree, פֶּרַח flower, שֶׁמֶשׁ sun, יָרֵחַ moon, כּוֹכָב star, דָּג fish, צִפּוֹר bird, אַרְיֵה lion, נָחָשׁ snake (friendly)
  - free space: Shabbat candles
  - Common items such as candles, challah and Torah go in a shared `items/` library.
- 8.2 **Bingo:** 10 boards, 3×3, one per page, with picture + Hebrew. A seeded generator makes sure no two boards share more than 6 items. It simulates games so the first win comes around calls 5–8. Includes calling cards, 4 to a page. Markers: pom-poms, not food.
- 8.3 **I-spy:**
  - built in code: an empty Gan Eden background plus the item cutouts, so the counts are exact and the answer key is generated
  - key strip along the bottom ("🐟 ×4 דָּג")
  - Easy has 15 targets; Challenge has 20–25 plus distractors
  - also a coloring version
- 8.4 **Match-it:** 6 pairs per set, 12 cards of 2.5" per page.
  - Set A: picture ↔ picture
  - Set B: picture ↔ Hebrew word
  - Bonus: day ↔ creation
  - Card backs use a repeating pattern, which tolerates duplex drift.
- 8.5 **Coloring + sequence:**
  - 4 story cards turned into line art with a Gemini **edit** call (thick outlines, ≤12 regions), then thresholded with PIL
  - 2×2 panels with straight cut lines and dot self-check tabs, plus a "story path" glue sheet
  - Bereshit extra: a Days 1–7 strip for 6-year-olds
  - A line-art contact sheet comes to Simon for review.
- 8.6 **Following-directions story:**
  - one line-art scene, with object positions taken from `listen_do.objects`
  - Level 1: single-step and related two-step directions. Level 2: 2-step plus one unrelated 3-step.
  - Hebrew words said, then echoed
  - auto-drawn answer key
- 8.7 **Sequencing game:** the real story cards plus a control strip. Variations for ages 4, 5 and 6.
- 8.8 **Teacher guide booklet:**
  - **8.5×11 letter**, single-sided or duplex, stapled at the corner or hole-punched for a binder. About 12 pages (fewer than half-letter because each page holds more), 14 for a holiday
  - fixed page map in `guide_layout.yaml`; card backs look their page numbers up there
  - `build_guide.py` builds it through Jinja, then Playwright PDF, with the overflow guard
  - p.15 is a photocopiable family letter
- 8.9 **Home card:**
  - fields: parasha, middah, Shabbat-table question in EN/HE, "ask your child to show you…", Hebrew word, try-at-home
  - ≤70 English words, transliteration required, Shabbat-friendly
- 8.10 **Classroom pilot:**
  - 3 classes (day-school gan, shul preschool, light-Hebrew class) × Bereshit + Noach
  - a daily tick grid, a Friday recall check of the gesture and word, and an 8-question form
  - results go to `pilot/`
  - a signal → action table feeds the word budgets, the Editor rubric and LESSONS_LEARNED

## Phase 9 (later) — Retrofit Purim

Purim gets the audit's content fixes:
- Haman's motive
- midrash labels
- Esther's real risk
- the decree ending
- Hebrew gender errors
- the megillah drawn as a Torah scroll
- diversity

It is then cut to 12 cards and regenerated at 4K letter size.

---

## Critical files

- parasha-pack:
  - `card-designer/components/cards/{CardFrame,CardBackFrame,BackSection,*CardBack}.tsx`
  - `card-designer/scripts/export-deck.ts`
  - `src/generate_images.py`, `src/image_prompts.py`, `src/sefaria_client.py`
  - new: `src/validate_deck.py`, `src/assemble_deck.py`, `src/generate_activities.py`, `src/build_guide.py`, `scripts/sync_to_hub.py`
  - `agents/definitions/*`, `characters/`, `series.yaml`, `schemas/`
- simonbrief-hub:
  - `app/parashapacks/{page,deck-view,ui}.tsx`, `data.ts` (removed)
  - new: `[deck]/page.tsx`, `[deck]/present/page.tsx`, `[deck]/presenter/page.tsx`, `decks/*.json`

## Verification

- `pytest` passes. The validator passes Bereshit and **fails** a deliberately broken fixture: an over-budget back, אַמִּיץ used for Chava, a missing character.
- The export guard fails on a fixture with an overflowing script.
- Bereshit duplex PDF (letter): 20 pages, art ≥300 DPI over the printable area. A real home-printer test print, checked for duplex alignment and legibility from 3 m.
- 5×7 export of the same deck renders with no overflow, keeps text inside the safe zone, and the bleed reaches 5.25×7.25".
- Hub: `next build` is clean. Present and presenter stay in step across two windows. Purim, Terumah and Bereshit routes all render. Simon checks the Vercel preview.
- Extras: bingo uniqueness test, I-spy count = answer key, and Hebrew prints in the right direction (RTL) in the PDFs.

## Risks

- **4K generation:** check the pixel size of the first 4K output, because one SDK has been reported to ignore the size setting. Fallback: generate at 2K and upscale with Real-ESRGAN's illustration model. Avoid Gemini edit-upscaling, which redraws faces.
- **Rate and spend caps:** Tier 1 allows $10 per 10 minutes. Batch the final runs.
- **Duplex drift on home printers (±⅛"):** the 0.3" margin absorbs it, and match-it backs use a pattern with no border to line up.
- **Hub on Next 16:** API changes. Read its docs first and keep the changes inside `app/parashapacks/`.
- **Line-art edits may change faces:** the contact-sheet review step catches this.
- **Image QA false positives:** it stays flag-only until it has proven accurate.

## Review

_(fill in when done)_
