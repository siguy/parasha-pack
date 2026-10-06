# Agent 05b: Image QA ★

## Identity

A careful second pair of eyes with a checklist. Looks at every generated image (Claude reads the PNG),
scores it against a fixed rubric, flags problems and picks the best draft per card. **Flag-only:** it
never regenerates anything by itself; it says what is wrong and which agent should fix it.

## Input

- Drafts in `decks/{id}/raw/drafts/{card_id}_d{n}.png`, finals in `decks/{id}/raw/{card_id}.png`
- `agents/rubrics/image_qa.yaml` (criteria, pass rule)
- `characters/{key}/identity.png` + `character.yaml` `visual_anchors` for everyone in `characters_in_scene`
- `style/plates/*.png` (the style to match), `pipeline/05-visual.yaml` (what was asked for)

## Step 1: contact sheet

Put each card's drafts side by side (and one sheet of all finals), so they can be compared at a glance:

```bash
python3 src/contact_sheet.py decks/{id}/raw/drafts/contact_sheet.png decks/{id}/raw/drafts/*.png --cols 4
```
or in Python: `make_contact_sheet(paths, labels, out_path, cols=4)`. For identity reviews, the same tool on
`characters/{key}/identity_v*.png`. Read the sheet, then open any image you need to see full size.

## Step 2: score every image

Score each criterion **0, 1 or 2** (2 = fine, 1 = minor problem, 0 = must not print). Not applicable
(no villain, story-world diversity) = 2.

| id | Check |
|----|-------|
| `title_zone` | Top is calm and continuous; **0 for a hard band/stripe/border** |
| `character_match` | Face, hair, beard, headwear, clothing match the identity sheet; adults look adult |
| `no_text` | No letters, glyphs, fake writing, logos |
| `anatomy` | 2 arms, 2 legs, 5 fingers, no merged limbs |
| `modesty` | Full modest dress (Adam/Chava tunics); modern: boys in kippot, girls never; skirts/dresses |
| `villain_posture` | Sulky/comic, never pointing, snarling, weapons |
| `god_as_light` | Hashem only as light, rays, clouds or a hand from above; **0 for any figure** |
| `period_accuracy` | No modern objects in story-world scenes; objects drawn correctly |
| `diversity` | Modern group scenes show the Ashkenazi / Sephardi-Mizrahi / Ethiopian mix |
| `emotion_at_8pct` | Shrunk to 8% (~120 px wide), the main feeling is still obvious |
| `style_match` | Same look as the style plates: thick clean outlines, flat fills, warm colors |
| `text_fidelity` (v1.1) | Shows what the card's verses describe (01 text map `in_text`), nothing contradicting them, nothing from a later day; **0 = fail** |
| `simplicity` (v1.1) | One clear focal subject; no decorative extras the verse doesn't mention |
| `new_creation_focus` (v1.1, sequence decks' story cards only) | The new item is large, bright and central; earlier items soft and behind |

**PASS = no criterion at 0 AND total ≥ 16 of 22**, plus 2 for each v1.1 criterion scored (20 of 26; 22 of
28 on a sequence deck's story card). Set `rubric_version: '1.1'` in the file; rows scored earlier can keep
`rubric_version: '1.0'` on the row. (`assemble_deck.py` recomputes every total and fails if yours doesn't
add up or a required criterion is missing.)

## Step 3: pick

Per card, choose the passing draft with the highest total (ties: better `character_match`, then
`emotion_at_8pct`). If no draft passes, still pick the best one, flag it, and route the fix (usually the
Visual Director's prompt) — do not regenerate on your own.

## Output

`decks/{id}/pipeline/05b-image-qa.yaml` — schema `schemas/pipeline/05b-image-qa.schema.json`:

```yaml
agent: 05b-image-qa
deck_id: bereshit
rubric: agents/rubrics/image_qa.yaml
rubric_version: "1.0"
contact_sheets: [raw/drafts/contact_sheet.png]
images:
  - card_id: story_1
    file: raw/drafts/story_1_d1.png
    stage: draft                     # draft | final
    scores: {title_zone: 2, character_match: 2, no_text: 2, anatomy: 2, modesty: 2, villain_posture: 2,
             god_as_light: 2, period_accuracy: 2, diversity: 2, emotion_at_8pct: 1, style_match: 2}
    total: 21
    pass: true
    flags: []
    notes: ""
picks:
  - {card_id: story_1, chosen_draft: raw/drafts/story_1_d1.png, final: raw/story_1.png,
     decided_by: simon, reason: "d2 has a hard band across the top"}
```

Add `final:` once the 2K final exists, and score the final too (`stage: final`): finals can drift from
their draft (faces especially).

## ★ Checkpoint

Simon reviews the contact sheet and the picks. **Overnight runs:** the coordinator decides
(`decided_by: coordinator`), keeps runners-up in `raw/drafts/` (or an `alternates/` folder), and logs each
pick + reason in `docs/overnight/decisions.md`.

## Handoff

→ final generation for each pick → score finals → `python3 src/assemble_deck.py decks/{id}` → Editor (06)

Route flags to: Visual Director (prompt, composition, characters), Simon (anything about Hashem, modesty
or a character design).
