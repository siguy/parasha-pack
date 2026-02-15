---
title: "Image Generation Pipeline v2"
type: feat
date: 2026-02-13
---

# Image Generation Pipeline v2

## Overview

Fix three real problems in the image generation workflow: **no provenance** (can't trace what prompt produced what image), **wrong character refs** (Haman appears in tradition cards), and **style drift** (cards in the same deck look like they're from different artists).

## Problem Statement

1. **No prompt/image provenance.** `generate_images.py` overwrites `raw/{card_id}.png` every run. No record of the full assembled prompt, model used, or which generation produced which result. When a good image lands, it can't be reproduced.

2. **All character refs passed to every card.** Tradition cards about community gatherings receive Haman's reference, which can cause the villain to appear. Connection cards receive all story characters even though they show generic children.

3. **Style drift within story world.** Even with `story_world` text, nano-banana-pro interprets "ancient Persia, children's illustration" differently each time. Cards in the same deck look like they're from different artists.

## Proposed Solution

Two phases plus documentation:

```
Phase A: BETTER GENERATION
  - JSONL generation log (6 fields)
  - Selective character refs via characters_in_scene
  - Lean prompts when ref images exist

Phase B: STYLE HERO
  - Generate one hero image that nails the deck's visual style
  - Pass as style reference to all story-world cards
  - Test manually before building automation
```

No variant management system (use `--card` to regenerate, git for history). No cheaper model (research it when cost actually hurts). No card chaining (test hero-only first). No gallery page (open the PNGs).

---

## Technical Approach

### Key Files

| File | Changes |
|------|---------|
| `src/generate_images.py` | Add logging, selective refs, style hero loading |
| `src/image_prompts.py` | Lean character blocks when refs exist |
| `decks/{id}/raw/generations.jsonl` | New: generation log |
| `decks/{id}/references/manifest.json` | Add `style_hero` entry |
| `decks/{id}/references/style_hero.png` | New: deck style reference |
| `decks/purim/deck.json` | Add `characters_in_scene` to all 16 cards |
| `agents/definitions/05-visual-director.md` | Add `characters_in_scene` to output |

---

## Implementation Phases

### Phase A: Better Generation

**Goal:** Fix the character ref bug, add provenance, and reduce prompt noise — all in one pass.

#### A1. Generation Logging

- [ ] Add `log_generation()` function to `generate_images.py`
  - Appends one JSONL line per generation to `decks/{id}/raw/generations.jsonl`
  - Schema (6 fields):
    ```json
    {
      "card_id": "story_2",
      "timestamp": "2026-02-13T14:30:00Z",
      "model": "nano-banana-pro",
      "full_prompt": "=== STYLE === ... full assembled prompt ...",
      "character_refs": ["mordechai", "haman"],
      "success": true
    }
    ```
  - Called after every generation attempt (success or failure)

- [ ] Save full assembled prompt as sidecar file
  - Write to `decks/{id}/raw/prompts/{card_id}.txt`
  - Overwritten each run (the JSONL log is the durable record)
  - Human-readable for quick debugging without parsing JSONL

- [ ] Update `generate_image_nano_banana()` to return metadata
  - Currently returns `bool`, change to return a dict with `success` + prompt + refs used

#### A2. Selective Character References

- [ ] Add `characters_in_scene` field to card data in `deck.json`
  ```json
  {
    "card_id": "story_2",
    "card_type": "story",
    "characters_in_scene": ["mordechai", "haman"],
    ...
  }
  ```

- [ ] Update `load_reference_images()` to accept a filter list
  ```python
  def load_reference_images(deck_path, characters_in_scene=None):
      # If characters_in_scene provided, only load those refs
      # If None, load all (backwards compatible)
  ```

- [ ] Update `main()` to pass `characters_in_scene` from card data
  - Falls back to loading all refs if field not present

- [ ] Add `characters_in_scene` to all 16 Purim cards
  - Tradition cards: `[]` (no story characters)
  - Connection cards: `[]` (generic children)
  - Story cards: only characters actually depicted
  - Spotlight cards: just the featured character
  - Anchor card: `[]` (symbol, no characters)
  - Power word card: characters in scene

- [ ] Update Visual Director output spec (`agents/definitions/05-visual-director.md`)
  - Must specify `characters_in_scene` for each card

#### A3. Lean Prompts When Refs Exist

- [ ] When a character has a reference image and is in `characters_in_scene`, shorten inline description
  - With ref: `"MORDECHAI (see reference image): Standing tall, refusing to bow."`
  - Without ref: full appearance description (backwards compatible)
  - This is a small conditional in `build_generation_prompt()`, not a separate helper

#### Acceptance Criteria

- [ ] Every generation attempt logged to `generations.jsonl` with 6 fields
- [ ] Full assembled prompt saved to `prompts/{card_id}.txt`
- [ ] Each card only receives references for characters in the scene
- [ ] Tradition/connection cards receive zero character refs
- [ ] Cards without `characters_in_scene` still load all refs (backwards compatible)
- [ ] Prompts shortened when character ref images are available
- [ ] Existing `python generate_images.py deck.json` workflow still works unchanged

---

### Phase B: Style Hero

**Goal:** Visual anchor that locks in the deck's art style across all story-world cards.

#### Tasks

- [ ] Generate a hero image manually
  - Pick a representative scene from the deck (e.g., Persian palace throne room for Purim)
  - Generate 2-3 options with `--card` and different prompt variations
  - Select the winner manually (rename to `style_hero.png`)

- [ ] Save hero in `references/style_hero.png`

- [ ] Update `references/manifest.json` to include style hero
  ```json
  {
    "style_hero": {
      "identity": "style_hero.png",
      "description": "Persian palace throne room, golden light, ornate arches"
    },
    "esther": { "identity": "esther_identity.png" },
    ...
  }
  ```

- [ ] Update `load_reference_images()` to include style hero
  - Load `style_hero` from manifest if it exists
  - Pass as first reference with label: "Style reference — match this art style, color palette, and rendering quality:"
  - Only for story-world cards (anchor, spotlight, story, power_word)
  - Modern-world cards skip the hero (they already have `MODERN_WORLD_STYLE` constant)

- [ ] Add `--no-hero` flag to skip style hero (for debugging)

- [ ] Test: regenerate 3-4 story cards with hero ref and compare to without
  - If consistency improves, ship it
  - If modern-world cards also drift, consider adding a second hero later

#### Acceptance Criteria

- [ ] Hero image stored in `references/style_hero.png` with manifest entry
- [ ] Story-world cards receive hero as first reference image
- [ ] Modern-world cards do not receive hero reference
- [ ] Cards show measurably more style consistency with hero vs without
- [ ] `--no-hero` flag works for A/B comparison

---

### Documentation (with each phase, not separately)

Update these docs as each feature lands:

| Doc | What to Update |
|-----|---------------|
| `src/CLAUDE.md` | Document logging, selective refs, hero system |
| `decks/CLAUDE.md` | Document `characters_in_scene`, `generations.jsonl`, `style_hero.png` |
| `agents/definitions/05-visual-director.md` | `characters_in_scene` in output spec |
| `agents/LESSONS_LEARNED.md` | New patterns from this work |
| `CHANGELOG.md` | Each phase as it's completed |
| `CLAUDE.md` | New flags (`--no-hero`) |

---

## Alternatives Considered

### Variant management system (selections.json, gallery page)
**Deferred:** At current scale (16 cards, 1 user), use `--card story_1` to regenerate and git for history. Build variant infrastructure if/when managing dozens of variants becomes painful.

### Exploration mode with cheaper model
**Deferred:** No research yet on whether a cheaper Gemini model supports reference images or produces useful previews. Research first. If API costs become a problem, add a `--model` flag.

### Sequential card chaining
**Deferred:** Plan's own assessment: "supplementary, not critical." Test hero-only first. If style drift persists after hero images, run a manual test (pass story_1 output as ref when generating story_2) before building automation.

### Two hero images (story-world + modern-world)
**Deferred:** Start with one hero for story-world cards. Modern-world cards have `MODERN_WORLD_STYLE` constant and are less likely to drift (generic classroom/community scenes). Add a second hero if modern-world consistency proves insufficient.

### Separate generation pipeline agent definition
**Deferred:** The generation workflow is a CLI script, not an agent. Document in CLAUDE.md and existing pipeline docs, not a new agent definition file.

---

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hero image doesn't improve consistency | Medium | Test with 3-4 cards before committing. If it doesn't help, the logging and selective refs are still valuable. |
| `characters_in_scene` missing from old decks | Low | Backwards compatible — loads all refs when field absent |
| Lean prompts cause character regression | Low | Test same card with full vs lean prompt. Keep full prompt as fallback. |
| Generation log grows large | Very low | JSONL, one line per generation. Trivial at current scale. |

---

## Git Strategy

Work on `feat/image-pipeline-v2` branch. Phase A (logging + selective refs) is independently useful — consider merging to main early rather than waiting for Phase B.

```bash
git checkout -b feat/image-pipeline-v2
```

---

## Future Work (from original plan, revisit after shipping 2-3 more decks)

These features were in the [original v2 plan](2026-02-13-feat-image-generation-pipeline-v2-plan-original.md) but deferred based on reviewer feedback. Revisit when the simpler system proves insufficient:

- **Variant storage & gallery UI** — If comparing 2-3 PNGs in Finder becomes painful
- **Exploration mode** — If API costs become a concern at higher volume
- **Sequential card chaining** — If hero-only doesn't solve style drift
- **Modern-world hero** — If connection/tradition cards drift visually
- **Multi-mode CLI** (`--mode style-lock | explore | finalize`) — If the workflow needs formal phases

---

## References

### Internal

- `src/generate_images.py` — Current generation orchestrator (~460 lines)
- `src/image_prompts.py:79-137` — Style anchors + modern world style
- `agents/definitions/05-visual-director.md` — Visual Director output spec
- `agents/LESSONS_LEARNED.md` — Character consistency gotchas (documents the Haman-in-tradition-cards bug)
- `decks/archive/yitro/pipeline/` — Complete pipeline reference example

### Reviewer Feedback

Three parallel reviews (DHH, Kieran, Simplicity) all converged on the same core message: the original 8-phase plan was over-engineered for a project with 1 active deck and 16 cards. This rewrite keeps the three highest-value changes (logging, selective refs, hero image) and defers everything else until the simpler system proves insufficient.
