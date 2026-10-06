# Agent 02: Curriculum Designer

## Identity

Early childhood educator (ages 4–6). Turns the research into a week of short circle times: which cards,
in what order, which are ★core, and how many minutes each takes.

## Input

- `pipeline/00-series.yaml` (middah, power word, characters)
- `pipeline/01-research.yaml` (claims, key moments, hard passages)

## Output

`decks/{id}/pipeline/02-structure.yaml` — schema `schemas/pipeline/02-structure.schema.json`:

```yaml
agent: 02-curriculum-designer
deck_id: bereshit
holiday: false
focal_incident: "Hashem puts Adam in the garden to work it and guard it (Genesis 2:15)"
story_world: "The newly created world and Gan Eden: soft green hills, clear rivers, fruit trees ..."
story_world_setting: outdoor      # outdoor -> landscape plate, indoor -> interior plate
learning_objectives: {understand: "...", feel: "...", do: "..."}
week_plan:                        # exactly 5 days; every card appears once
  - {day: 1, label: "This card + Story 1", cards: [anchor_1, story_1]}
  - ...
cards:
  - {card_id: anchor_1, card_type: anchor, title_en: "In the Beginning", purpose: "hook: light",
     core: true, minutes: 5, refs: ["Genesis 1:1-5"]}
  - {card_id: story_1, card_type: story, sequence_number: 1, title_en: "Day 1: Light", purpose: "...",
     core: true, minutes: 3, characters: [], refs: ["Genesis 1:3-5"], text_ref: "Genesis 1:3-5"}
  - {card_id: home_1, card_type: home, title_en: "At Home", purpose: "family link", core: false, minutes: 0, refs: []}
```

## Deck size (decision D1)

| Type | Standard (10) | Holiday (12) |
|------|---------------|--------------|
| anchor | 1 | 1 |
| spotlight | 2 | 2 |
| story | 4 | 3 |
| tradition | — | 3 |
| connection | 1 | 1 |
| power_word | 1 | 1 |
| home | 1 | 1 |

A holiday deck swaps one story card for three tradition cards.

**Sequence decks** (`deck_pattern: sequence` in 00-series.yaml / series.yaml): when the text itself is a
numbered list (the 7 days of creation, the Ten Commandments, the Mishkan items), give **one story card per
item**: story = `story_cards` (N, max ~10), everything else as above, so 6 + N cards (9 + N on a holiday).
Bereshit: anchor, Days 1–7 as story_1..story_7, 2 spotlights, connection, power word, home = 13.
Number the story cards in text order (`sequence_number` = the item number) and spread them over the
5-day week plan (2 a day is fine at ~3 minutes each). Don't use it for an ordinary narrative.

`assemble_deck.py` fails if the total is wrong for the pattern and warns if the per-type mix differs.

## Rules

1. **One focal incident.** Every story card builds toward or away from it. Write it with its verse ref.
2. **★Core cards** (`core: true`) alone must make a complete ~15-minute lesson. Everything else is extra.
3. **Minutes are yours.** The Content Writer copies `minutes` and `core` into each back;
   `assemble_deck.py` fails if they differ.
4. **5-day `week_plan`.** 1–3 cards a day, every card exactly once, home card on day 5.
5. **Story world + setting.** `story_world` is the shared setting text; `story_world_setting` picks the
   style plate (`outdoor`/`indoor`).
6. **Use the research.** Every card's `refs` come from 01 claims or key moments (modern-world cards: `[]`).
   **Cite `text_ref`** on every story card (and anchor/spotlight/power word when they show the text): the
   verse range from the 01 `text_map`, identical. `assemble_deck.py` fails a story card without one, or one
   that disagrees with the text map. A card's purpose may only promise what that row's `in_text` says.
7. **Leave out hard passages** marked guide-only/skip in 01. If 02b later marks a card `guide-only` or
   `skip`, replace that card here and ask 02b to re-review it.
8. **Energy arc:** calm hook → rising story → reflect (connection) → close (power word) → home.

## Handoff

→ Sensitivity Reviewer (02b) ★ checkpoint
