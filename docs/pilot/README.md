# Classroom pilot (plan 8.10)

Before we make 50 more decks, we try two of them in real classrooms and let the numbers
tell us what to change. Think of it as a dress rehearsal with three different audiences.

## The protocol

| | |
|---|---|
| **Classes** | 3: **A** day-school gan (strong Hebrew), **B** shul preschool (some Hebrew), **C** light-Hebrew class (little Hebrew at home) |
| **Decks** | Bereshit, then Noach the next week (2 weeks per class, 6 class-weeks in all) |
| **Teacher gets** | the printed deck (letter, duplex), the teacher guide booklet, the extras PDFs, one tick grid per deck, one feedback form per deck |
| **Daily** | teach the week plan (about 15 minutes a day); tick the grid as you go |
| **Friday** | the 2-minute recall check at the bottom of the tick grid, *before* the home card goes out |
| **End of week** | the 8-question feedback form (about 10 minutes) |
| **Simon** | copies each sheet into `docs/pilot/results/{class}-{deck}.yaml` (from `results_template.yaml`) and fills `signals_fired` |

### Privacy rules (non-negotiable)
- **No child's name, photo, voice or drawing leaves the classroom.** Every number is a count ("12 of 15 did the gesture").
- Teachers are a code (`T1`, `T2`, `T3`), classes are A / B / C. The school's name is not written in the repo.
- No photos of children. If a teacher wants to share a photo of a finished craft, it must show no faces, no names and no handwriting.
- Paper sheets stay with the teacher or go back to Simon by hand; they are not scanned into the repo.
- The school agrees to the pilot in writing first and tells families what is being tried (the family letter already goes home every week).

### What we measure

| Measure | Where it comes from | Good sign |
|---|---|---|
| Real minutes per card vs the minutes on its back | tick grid "Real minutes" | within ±2 minutes |
| Engagement per card | tick grid "most / some / few" | "most" on core cards |
| Gesture recall, no hint (Friday) | Friday check, item 2 | ≥ 60% of children present |
| Power word recall (Friday) | Friday check, item 3 | ≥ 50% unprompted, ≥ 80% after a hint |
| Story order (Friday) | Friday check, item 4 | ≥ 60% |
| Back readable in the moment | form Q3 (1–5) | ≥ 4 |
| Hebrew load | form Q6 | "right" in all three class types |
| Hard questions | grid tick + form Q7 | the script was enough (no teacher improvising) |
| Extras used again | form Q8 | each extra chosen again by ≥ 2 of 3 teachers |

## Signal → action

Each row says: if we see this, change that. The change goes in the place named, so every
future deck gets it automatically.

| Signal (from the results) | Action | Where the change goes |
|---|---|---|
| A card runs ≥ 3 min over its back's minutes in 2+ classes | lower the spoken-word budget for that card type | `MAX_SAY_WORDS` / `MAX_CUE_WORDS` in `src/validate_deck.py`, word budgets in `agents/CARD_SPECS.md` |
| Readability (Q3) < 4 | bigger SAY text or fewer cues per back | card back templates in `card-designer/`; Editor rubric "back is scannable" criterion |
| Gesture recall < 40% | one gesture per deck only (drop per-card gestures), repeat it on every card back | `agents/definitions/03-content-writer.md`; `docs/policies/values-spine.md` |
| Word recall < 30% unprompted in class C | fewer Hebrew words for light-Hebrew classes; power word only on story backs | word budgets in `agents/CARD_SPECS.md`; Editor rubric Hebrew-load criterion |
| Hebrew load "too many" from 2+ teachers | cut to the power word + 2 card words per deck | `agents/definitions/00-series-planner.md`, `agents/rubrics/editor.yaml` |
| Story order < 40% | add the sequencing game to Day 5 by default, number dots on story fronts | `decks/{id}/guide.yaml` extras + week plan; `agents/definitions/02-curriculum-designer.md` |
| A teacher improvised a hard-question answer | add that question and a script to the sensitivity step | `agents/definitions/02b-sensitivity-reviewer.md`; `docs/policies/hard-text-policy.md` |
| An extra is not chosen again by 2 of 3 teachers | drop it from the default extras set | `decks/{id}/guide.yaml` extras index; `docs/extras.md` |
| Engagement "few" on the same card type in 2+ classes | rework that card type's prompt or roleplay pattern | `agents/CARD_SPECS.md` |
| Anything surprising | write it down as a rule | `agents/LESSONS_LEARNED.md` |

## Files

| File | What it is |
|---|---|
| `daily_tick_grid.pdf` | 1 page per class per deck: one row per card (week-plan order) + the Friday recall check |
| `teacher_feedback_form.pdf` | the 8 questions, one page |
| `results_template.yaml` | copy one per class per deck into `results/` |
| `kit.yaml` | the words on both forms (edit here, then rebuild) |
| `previews/` | PNG pictures of both forms |

Rebuild the forms after editing `kit.yaml`:

```bash
python3 src/build_pilot_kit.py                 # rows from the Bereshit week plan
python3 src/build_pilot_kit.py --deck decks/noach
```
