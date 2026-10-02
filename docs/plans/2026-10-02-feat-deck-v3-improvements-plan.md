---
title: "Deck v3: Focused Backs, Print-Ready Art, Scalable Pipeline"
type: feat
date: 2026-10-02
status: approved decisions D1/D3/D5/D6 (2026-10-02); D2/D4 drafts pending
---

# Deck v3: Focused Backs, Print-Ready Art, Scalable Pipeline

## Overview

Five research passes (deck/back audit, pipeline audit, education-standards research,
competitor research, imagery audit) found that the Purim deck is a strong v2, but
three things block scaling to 54 parshiyot + ~12 holidays:

1. **Backs are overloaded, and some are cut off.** 80–143 words in 4–5 boxes of equal
   weight, with about 40% repetition. `overflow-hidden` silently cuts text
   (spotlight_3 and connection_1 end mid-sentence in the printed PNGs).
2. **Art isn't print-ready.** Raw images are 896×1200, about 179 DPI at 5×7, against a
   300 DPI target. There's no bleed, cards have rounded corners and white padding,
   and colors are RGB only.
3. **Nothing is enforced.** There's no validator and no tests. Character data lives in 5
   places, and identity images are trapped inside individual decks. YAML is merged by
   hand, and the research database covers 2 parshiyot.

On top of that, there are Torah-accuracy and Hebrew errors in Purim, and the agent
pipeline has gaps: no series planner, no sensitivity review, no image QA.

**The market gap we're aiming at:** no parsha product found gives preschool teachers a
5×7 illustrated deck with a speak-aloud scripted back (the Second Step model). Jewish
products are wall displays, 54-card one-per-parsha Q&A decks, or worksheets. Mid-price
($20–35/deck) is empty.

## Research Summary (sources in session; key ones cited)

| Source | Finding that drives this plan |
|---|---|
| Second Step Early Learning | **Bold = spoken, plain = direction.** One card per week; 5–7 min daily steps (Day 1 intro → 2 story → 3–4 practice → 5 review). Home link kept off the card. |
| Picture the Bible / TableTopics | 1 verse + 1 question beats 4 equal boxes. |
| Barefoot Books (5×7) | Numbered, picture-led action steps; reviewers want the "how to end/transition" step. Color = category. |
| Montessori 3-part cards | Control card = self-check. Cheap way to make a sequencing game. |
| NAEYC DAP 2020 | Group time matched to attention span (~5–10 min single-purpose circle). |
| Dialogic reading (PEER/CROWD) | Ages 4–6: completion, wh-, open-ended questions. "Have you ever" (distancing) sparingly. |
| Vocabulary research | 2–6 exposures; same story repeated > more stories. |
| Embodied learning | Gesture/acting improves recall and retelling. |
| Sheva (JCC), Jewish LearningWorks | One middah per lesson; families as partners; "At-Home Challenge"; D'rash (interpretation) as a value → label midrash. |
| PJ Library, Sasso | Character-first warmth; God as wonder, not a figure. |

Unverified: Chabad/Torah Umesorah preschool card back layouts (pages blocked); NAEYC "5–10 min" is via secondary source.

---

## Phase 0 — Decisions Simon must make (blocks everything)

**Decided 2026-10-02:** D1 = 10 standard / 12 holiday. D3 = Modern Orthodox. D5 = printed booklet (no QR). D6 = Simon is the only human checkpoint. D2 and D4: Claude drafts, Simon edits.

These are product/values calls, not engineering calls. I'll draft options; Simon picks.

- **D1. Card count standard.** Recommend: **10 standard / 12 holiday** (1 anchor, 2 spotlight,
  4 story, 1 connection, 1 power word, +1 "Shabbat table"/home card; holiday: 3 tradition
  cards replace 1 story → 12). Today: docs say 10/13, 8–16, 8–12; Purim has 16.
- **D2. Values spine.** A fixed list of ~12–15 middot that rotate through the year
  (e.g. chesed, ometz lev, emunah, hakarat hatov, anavah, shalom, tzedakah, kavod, achrayut,
  emet, savlanut, hachnasat orchim, simcha). Each deck gets exactly one.
- **D3. Denominational stance.** Modern-world cards currently depict Modern Orthodox norms
  (kippot on boys). Keep that, or go pluralist? This affects imagery rules and the midrash wording.
- **D4. Hard-text policy.** One written policy for Akedah, Flood, plagues, Korach, deaths,
  Amalek, Haman's fate. Recommend the "feeling + choice" framing, plus a scripted
  answer to "what happened to X?" in the teacher guide, never on the card.
- **D5. Teacher guide medium.** QR → web page (review-site can host), or printed booklet
  insert, or both.
- **D6. Rabbinic/educator reviewer.** Is there a human (rabbi, gan teacher) who signs off
  each deck? The pipeline will have a checkpoint for it either way.

---

## Phase 1 — Back v3 template + schema (design first, then build)

**Why first:** the validator, the agents and the Purim rewrite all depend on the shape of
the new data.

### New back structure (~60–70 words, read top to bottom)

```
┌───────────────────────────────────────┐
│ STORY 2 · ~5 min · ★ CORE    [icon]   │ header: type, time, core flag
│ 🎯 Mordechai stands tall    COURAGE   │ objective (≤10 words) + deck value
├───────────────────────────────────────┤
│ SAY                                    │ ≤50 words. **Bold = spoken.**
│ **Haman wanted EVERYONE to bow.**      │ [Brackets] = action cues, inline.
│ [Everyone bow!]                        │ Movement lives HERE, not in a box.
│ **But Mordechai... stood... TALL.**    │
│ [Stand up tall!]                       │
├───────────────────────────────────────┤
│ ASK  (max 2: concrete → open)          │ typed: recall | wh | open | distancing
│ • What did Mordechai do?               │ (distancing only on connection/home)
│ • Show me your brave body!             │ non-verbal answer allowed (UDL)
├───────────────────────────────────────┤
│ 🗣 עוֹמֵד  o-MED · "standing" ✋gesture │ optional Hebrew word + fixed gesture
├───────────────────────────────────────┤
│ ▸ Next: "What will Haman do now?"      │ transition — must not assume order
│ 📖 Guide p.4 · midrash notes           │
└───────────────────────────────────────┘
```

### Schema changes (deck.json `back` object per card)

| New field | Rule | Replaces |
|---|---|---|
| `objective` | ≤10 words | — |
| `say` | ≤50 words; `**bold**` spoken, `[brackets]` actions | `teacher_script`, `roleplay_prompt`, spotlight auto "Act it Out" |
| `ask[]` | ≤2, each ≤12 words, `{text, type}` | `discussion_prompts`, connection `questions[]` |
| `hebrew` | `{word, translit, meaning, gesture}` optional | story `hebrew_key_word*` on back |
| `minutes`, `core` | int, bool | — |
| `transition` | must not reference card order | `transition_line` |
| `guide` | free-form: `sources`, `pshat_vs_midrash`, `hard_questions`, `adaptations`, `extensions`, `tip` | `teacher_tip`, `teaching_moment_en`, `story_connection_*` |

`guide` content is **never** rendered on the back. It goes to the teacher guide (Phase 7).

Per-type variants:
- **Anchor:** adds the week routine strip (Sun–Fri: Day 1 anchor + spotlights → Day 2–3 story
  → Day 4 connection → Day 5 power word + home card).
- **Connection:** feeling-faces strip (SVG, not emoji).
- **Power word:** picture/word/gesture as a Montessori-style trio.
- **Home card (new):** written to families. One Shabbat-table question, the Hebrew word,
  bilingual EN/HE.

### Tasks
- [ ] 1.1 Mock the v3 back for each of the 6 types as static HTML. Simon approves the look.
- [ ] 1.2 Write the v3 JSON Schema (`schemas/deck.v3.schema.json`), with no field aliases.
- [ ] 1.3 Write a migration script `src/migrate_v2_to_v3.py` (mechanical moves; content rewrites are Phase 3).
- [ ] 1.4 Rebuild the back components: one `CardBack.tsx` driven by type config instead of 6 near-duplicates.
      Remove `overflow-hidden`; bold/bracket parser; SVG icons; gold headings → #8A6A1F (WCAG AA).
- [ ] 1.5 Update `agents/CARD_SPECS.md` (SAY/ASK/HEBREW labels match the code).

---

## Phase 2 — Safety net (validation + tests + housekeeping)

- [ ] 2.1 `src/validate_deck.py` (pydantic or jsonschema), run before generation and before export:
  - required fields per type; word budgets (say ≤50, ask ≤2×12, objective ≤10)
  - `characters_in_scene` ⊆ manifest; every character named in `image_prompt` is listed
  - Hebrew: every `*_he` has nikud; the stripped-nikud form matches its unpointed twin
  - **Hebrew gender check:** adjective/noun gender vs the character's gender (catches אַמִּיץ/גִּבּוֹר for Esther)
  - banned prompt content (`=== STYLE`, percentages, "Star of David" in story-world decks, etc.)
  - transitions don't contain order words ("first", "begins", "one more")
  - card count matches D1
- [ ] 2.2 **Export overflow guard:** `export-deck.ts` measures every section (`scrollHeight > clientHeight`)
      and fails the export with the card id. Also checks title safe-zone bounding boxes.
- [ ] 2.3 pytest: `build_generation_prompt()`, validator rules, migration. `npm` test for the bold/bracket parser.
- [ ] 2.4 Housekeeping:
  - `sync-deck.sh` → `rsync --delete`
  - fix the `review-site` registry path
  - delete or repair the `review-site/api` `--auto --resume` call
  - remove the hardcoded `terumah` in `card-designer/app/page.tsx`
  - remove `raw-v1-borders/`, `*_pre_hero.png`, `deck_v*_backup.json`, `approval_stats.yaml`
- [ ] 2.5 Logging to `project.log` in Python tools, per Simon's code standards.

---

## Phase 3 — Purim content rewrite (proves v3 end to end)

- [ ] 3.1 **Torah accuracy:**
  - Haman's motive = pride/anger (3:5); "jealous" only if labeled as interpretation
  - "only bows to God" labeled as midrash in a Modern Orthodox voice ("Our Sages teach us…")
  - Esther's courage = going uninvited at risk, after a 3-day fast (4:11–16), plus "who knows… for such a time" (4:14)
  - story_5 ending: the decree couldn't be undone, so the Jews were allowed to defend themselves (gently framed)
  - prepared "what happened to Haman?" answer in the guide
  - God's hidden name in the Megillah = the "hidden" theme
  - add verse refs
- [ ] 3.2 **Hebrew:**
  - קַנַּאי → מְקַנֵּא (or drop it with the motive change)
  - story_4 keyword → אַמִּיצָה
  - power word: teach gibor/giborah explicitly
  - fix the stress ("gee-BOR"; drop "dinosaur")
  - gender-inclusive second-person forms (אַתָּה/אַתְּ or plural)
- [ ] 3.3 **Structure to D1:**
  - cut from 16 cards to 12
  - 4 mitzvot coverage: megillah, mishloach manot, matanot la'evyonim, seudah (merge into 3 tradition cards)
  - add the home card
  - grogger card: explain "blotting out" gently, or reframe it as "making noise so Haman's name can't be heard"
- [ ] 3.4 Rewrite all backs to v3 budgets. Run the validator to green. Export. Simon and teachers review.

---

## Phase 4 — Imagery & front design

### 4A Print-readiness (blocks printing)
- [ ] 4A.1 `generate_images.py`: set `imageConfig.imageSize` to "2K" (or "4K") and verify the output is ≥1575×2205.
      Choose an aspect ratio that covers 5.25×7.25 with bleed (crop, not stretch).
- [ ] 4A.2 Print export mode: 1575×2175 (5.25×7.25 @300), full-bleed, square corners, no white padding or shadow,
      a border ≥4 mm inside trim, text ≥5 mm inside trim, 300 DPI metadata. Keep a "screen" mode for the review site.
- [ ] 4A.3 CMYK soft-proof step (FOGRA39/GRACoL) and tune the out-of-gamut purple #8B5CF6 and blue #0074D9.
- [ ] 4A.4 Replace Apple emoji with licensed SVGs (Twemoji/Noto, or custom feeling faces).

### 4B Prompt system (`src/image_prompts.py`)
- [ ] 4B.1 Remove the "darker lower-left" lines (cause black ink puddles) and replace them with a "simple low-detail ground plane".
- [ ] 4B.2 COMPOSITION: "top 25% calm/empty for title"; "max 5 figures in focus; background figures simplified".
- [ ] 4B.3 MODERN_WORLD_STYLE:
  - name the ethnic mix per scene (Ashkenazi, Sephardi/Mizrahi, Ethiopian)
  - kippah rules by gender (per D3)
  - megillah = single scroll, no twin rollers
- [ ] 4B.4 Villain rules: no pointing, no snarling; "misguided, sulky, comic" posture.
- [ ] 4B.5 Purim story_world → Achaemenid (bull-capital columns, glazed brick friezes, rosettes);
      negative list: no pointed Islamic arches, zellige, domes, or Star of David.

### 4C Series style + references
- [ ] 4C.1 **Series style bible:** one `series/style_bible.png` (character-free) plus a written style card, used by every deck.
      This replaces per-deck style heroes that contain characters.
- [ ] 4C.2 Identity sheets v2: 3-angle turnaround plus an expression row (happy, worried, brave, surprised),
      plain background, **no caption text**, headwear locked in the text anchor.

### 4D Card Designer fronts
- [ ] 4D.1 FitText padding ≥40, max-width 85%; one title treatment everywhere (the anchor too).
- [ ] 4D.2 Gradient `from-black/65` over h-56; English subtitles ≥ text-2xl (readable at 2–3 m).
- [ ] 4D.3 Color coding: Tradition gets its own color (no longer shares Spotlight gold); separate red and green.
      Add a **type icon** in the corner so color isn't the only cue (color-blind safe).
- [ ] 4D.4 Story fronts: a small sequence number (1–4), so the deck doubles as a sequencing game.
- [ ] 4D.5 Connection emoji bar: solid white 85% or no panel.

---

## Phase 5 — Agent pipeline v3

New roster (8 agents + tools):

```
00 Series Planner ──► series.yaml (value, power word, characters, sensitivities per deck)
01 Torah Scholar ───► reads research cache (Sefaria) — cites verses, flags pshat vs midrash
02 Curriculum Designer ─► picks 1 focal incident, core cards, week routine
02b Sensitivity Reviewer ─► child-dev + halachic/community + D4 policy  ◄── CHECKPOINT (human)
03 Content Writer + Hebrew (merged) ─► v3 backs within budgets; Hebrew with nikud
   └─ validate_deck.py (deterministic: budgets, nikud, gender, refs)
05 Visual Director ─► scene-only prompts, characters from shared library
   └─ generate_images.py (2K, retries, variants=2 for story)
05b Image QA (vision) ─► rubric scores; auto-regenerate failures ≤N; flags the rest  ◄── CHECKPOINT (human picks)
06 Editor ─► scored rubric across content + art + Torah; outputs a feedback.json draft
   └─ assemble → sync → export (overflow guard) → print proof
   ◄── CHECKPOINT (Simon)
```

- [ ] 5.1 `00-series-planner.md`: owns `series.yaml`; rotates the values spine; Hebrew word progression with review words; recurring characters; holiday calendar.
- [ ] 5.2 `02b-sensitivity-reviewer.md`: checklist per D3/D4; runs *before* content writing (cheap to change direction).
- [ ] 5.3 Merge `03` + `04` into `03-content-writer.md` with a Hebrew section; Hebrew mechanics move to the validator.
- [ ] 5.4 `05b-image-qa.md` vision rubric:
  - title zone clear (top 25%)
  - characters match the identity image (headwear, beard, colors)
  - no stray text
  - anatomy (hands)
  - modesty/kippah rules
  - villain posture
  - God only as light/clouds/hands
  - period accuracy
  - diversity count in modern scenes
  - emotion readable at 8% scale
- [ ] 5.5 `06-editor.md` → a scored rubric (from LESSONS_LEARNED); track first-pass acceptance per card type.
- [ ] 5.6 `07-card-designer.md` → demote to a tool doc (`tools/card-designer.md`).
- [ ] 5.7 Per-agent output schemas (`schemas/pipeline/0X.schema.json`), so each YAML is validated before the next agent runs.
- [ ] 5.8 **Docs reconciliation pass** across all 3 layers (per memory): CLAUDE.md, src/CLAUDE.md, decks/CLAUDE.md,
      agents/*.md, CARD_SPECS, VISUAL_SPECS, README, CHANGELOG. Grep for the old terms (`teacher_tip`, `Act it Out`, `04-hebrew`, `13 cards`).

---

## Phase 6 — Scaling infrastructure

- [ ] 6.1 **Shared character library:** `characters/{key}/identity.png` + `character.yaml` (canonical flag, version,
      locked visual anchors, gender for the Hebrew check). Retire CHARACTER_DATABASE, DEFAULT_DESIGNS, schema.py
      CHARACTER_DESIGNS and per-deck research JSON. `load_reference_images()` resolves from the library.
      Migrate Moshe, Yitro, Esther, Mordechai, Haman, Achashverosh, etc.
- [ ] 6.2 **Research cache:** `research/{parasha}.yaml` fetched once from Sefaria (text, key verses, a couple of
      commentaries). Torah Scholar reads it, so quotes are checkable. Delete PARASHA_DATABASE.
- [ ] 6.3 **`series.yaml`:** all 66 entries (54 parshiyot + holidays), status, value, power word, characters, sensitivity notes.
      The review site lists decks from it.
- [ ] 6.4 **`assemble_deck.py`:** merges pipeline YAML into deck.json (no hand merge); one `pipeline/` layout for every deck.
- [ ] 6.5 **Orchestrator:** `python workflows.py run <deck>` steps through the stages and stops at each checkpoint with a summary;
      `--from <stage>` resumes. Image gen in parallel with retries and backoff.
- [ ] 6.6 Cost/attention tracking: generations per card and first-pass acceptance rate, logged from generations.jsonl.

---

## Phase 7 — "What else" (product extensions)

- [ ] 7.1 **Teacher guide booklet per deck** (printed insert; backs reference page numbers): week routine, sources, pshat/midrash notes, hard-question scripts,
      adaptations (UDL), extensions, tips. Generated from the `guide` fields, so there's no extra writing.
- [ ] 7.2 **Home card / family page:** bilingual Shabbat-table question, Hebrew word, song suggestion. Printable.
- [ ] 7.3 **Sequencing game:** story cards numbered on the back; a Montessori-style "control" strip.
- [ ] 7.4 **Spiral year 2:** the same art, with harder `ask` sets (year-2 question bank), so the decks get reused annually.
- [ ] 7.5 **Hebrew word wall:** power words collected across decks into a printable year-long word wall, with review words returning.
- [ ] 7.6 **Packaging & print vendor:** tuck box or ring-bound; a 1–2 deck proof print before scaling.
- [ ] 7.7 **AI-art disclosure + licensing review** (fonts, emoji, Gemini output terms) before selling.
- [ ] 7.8 **Pilot & feedback loop:** 2–3 classrooms; a short teacher survey (which cards got used, time, engagement);
      results feed LESSONS_LEARNED and the Editor rubric.
- [ ] 7.9 `FOR_SIMON.md` learning doc (required by global CLAUDE.md; doesn't exist yet).

---

## Phase 8 — Prove it: build deck #7 on the new pipeline

- [ ] 8.1 Pick a parasha with a recurring character (e.g. a Moshe parasha) to test the shared library.
- [ ] 8.2 Run the full orchestrator; record human-minutes and generations per card against Purim (39 gens / 16 cards).
- [ ] 8.3 Retro: update LESSONS_LEARNED and the plan before decks 8+.

---

## Ordering & Dependencies

```
Phase 0 (decisions) ──► Phase 1 (template+schema) ──► Phase 2 (validator/guard)
                                                     └─► Phase 3 (Purim rewrite)
Phase 4A/4B/4D can run in parallel with Phase 3 (different files)
Phase 4C + 6.1 (character library) together — both touch references
Phase 5 (agents) after Phases 1–2, since agents target the v3 schema + validator
Phase 6 after Phase 5 docs exist
Phase 7 items mostly independent; 7.1 depends on Phase 1 `guide` field
Phase 8 last
```

Each phase ends with: commit, update `progress.md`, update `tasks/todo.md`, and a check-in with Simon.

## Risks

- **Regenerating Purim at 2K** costs about 16–30 Gemini calls. Commit a checkpoint first (CLAUDE.md rule).
- **Schema migration breaks archived decks.** Archive decks stay on v2; the Card Designer keeps reading v2 for them, or we migrate only on demand.
- **Over-trimming backs.** If 50 words proves too tight in the pilot, raise the budget in one place (the validator config).
- **Image QA false positives.** Start the vision rubric in "flag only" mode, and auto-regenerate only once it's shown to be accurate.

## Review

_(fill in when done)_
