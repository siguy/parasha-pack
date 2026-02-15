---
title: "Image Generation Pipeline v2"
type: feat
date: 2026-02-13
---

# Image Generation Pipeline v2

## Overview

Overhaul the image generation system to solve three problems: **style inconsistency** across cards in a deck, **no provenance tracking** (can't trace what prompt produced what image), and **expensive blind iteration** (every generation costs the same whether exploring or finalizing).

The solution introduces a multi-phase generation workflow with provenance logging, exploration mode, style reference images, sequential card chaining, and selective character references — all integrated into the existing 7-agent pipeline.

## Problem Statement

1. **Style drift within story world.** Even with `story_world` text, nano-banana-pro interprets "ancient Persia, children's illustration" differently each time. Cards in the same deck look like they're from different artists.

2. **No prompt/image provenance.** `generate_images.py` overwrites `raw/{card_id}.png` every run. No record of the full assembled prompt, model used, or which generation produced which result. When a good image lands, it can't be reproduced or built upon.

3. **Expensive blind iteration.** nano-banana-pro costs the same whether you're exploring styles or producing final art. No way to cheaply test compositions before committing to the expensive model.

4. **All character refs passed to every card.** Tradition cards about community gatherings receive Haman's reference, which can cause the villain to appear. No selectivity.

5. **No card-to-card visual continuity.** Each card is generated independently. Story cards 1-5 should feel like consecutive frames but they're generated in isolation.

## Proposed Solution

### Multi-Phase Generation Workflow

```
Phase 1: STYLE LOCK
  Generate 2-3 "hero" images that nail the deck's visual style.
  Human selects the winner. This becomes the style reference for all cards.

Phase 2: EXPLORE
  Cheaper/faster model generates 2-3 variants per card.
  All variants logged with full prompts.
  Human reviews and selects winners.

Phase 3: FINALIZE
  nano-banana-pro regenerates selected compositions.
  Hero image passed as style reference.
  Previous card passed as chain reference (sequential generation).
  Selective character refs (only characters in scene).

Phase 4: VERIFY
  Review all finalized images side-by-side for consistency.
  Flag any that need re-generation.
```

### Supporting Infrastructure

- **Generation log** — JSONL file tracking every generation attempt with full prompt, model, refs, result
- **Variant storage** — `raw/variants/{card_id}/` directories with timestamped filenames
- **Selection manifest** — Tracks which variant was selected for each card
- **Style reference** — Hero image stored in `references/style_hero.png`, passed alongside character refs

---

## Technical Approach

### Architecture

The current `generate_images.py` is a single-pass script. It becomes a multi-mode tool:

```bash
# Phase 1: Generate hero/style reference
python generate_images.py deck.json --mode style-lock --variants 3

# Phase 2: Explore variants (cheaper model)
python generate_images.py deck.json --mode explore --variants 3

# Phase 3: Finalize selected variants
python generate_images.py deck.json --mode finalize

# Legacy: Single-pass (backwards compatible)
python generate_images.py deck.json
```

### Key Files

| File | Changes |
|------|---------|
| `src/generate_images.py` | Add modes, chaining, selective refs, logging |
| `src/image_prompts.py` | Leaner prompt mode, style ref integration |
| `src/schema.py` | Add `characters_in_scene` field to card types |
| `decks/{id}/raw/generations.jsonl` | New: generation log |
| `decks/{id}/raw/variants/` | New: variant storage |
| `decks/{id}/raw/selections.json` | New: selected variants per card |
| `decks/{id}/references/style_hero.png` | New: deck style reference |
| `agents/definitions/05-visual-director.md` | Add `characters_in_scene` to output |
| `agents/AGENT_PIPELINE.md` | Document multi-phase generation workflow |

---

## Implementation Phases

### Phase 1: Generation Log & Provenance

**Goal:** Never lose track of what produced an image.

#### Tasks

- [ ] Create `GenerationRecord` dataclass in `schema.py`
  ```python
  @dataclass
  class GenerationRecord:
      card_id: str
      timestamp: str           # ISO 8601
      model: str               # "nano-banana-pro", "gemini-flash", etc.
      mode: str                # "single", "style-lock", "explore", "finalize"
      full_prompt: str         # Complete assembled prompt (all 6 layers)
      scene_prompt: str        # Scene-only prompt from deck.json
      story_world: str         # story_world used
      character_refs: list     # Character keys whose refs were passed
      style_ref_used: bool     # Whether hero image was passed
      chain_ref_card: str      # card_id of previous card (if chaining)
      output_file: str         # Filename of generated image
      success: bool
      variant_id: str          # "a", "b", "c" for multi-variant
  ```

- [ ] Add `log_generation()` function to `generate_images.py`
  - Appends JSONL to `decks/{id}/raw/generations.jsonl`
  - Called after every generation attempt (success or failure)

- [ ] Save full assembled prompt alongside image
  - Write to `decks/{id}/raw/prompts/{card_id}.txt` (or `{card_id}_{variant}.txt`)
  - Always written, not just in debug mode

- [ ] Update `generate_image_nano_banana()` to return generation metadata
  - Currently returns `bool`, change to return `GenerationResult` with success + metadata

#### Acceptance Criteria

- [ ] Every generation attempt logged to `generations.jsonl`
- [ ] Full assembled prompt saved to `prompts/` directory
- [ ] Log includes all 6 prompt layers, character refs used, model, timestamp
- [ ] Existing single-pass workflow still works unchanged (backwards compatible)

---

### Phase 2: Variant Storage & Selection

**Goal:** Generate multiple options per card, pick winners.

#### Tasks

- [ ] Add `--variants N` flag to `generate_images.py`
  - Generates N variants per card: `raw/variants/{card_id}/{card_id}_a.png`, `_b.png`, `_c.png`
  - Each variant logged separately in `generations.jsonl`

- [ ] Create `selections.json` schema
  ```json
  {
    "anchor_1": {
      "selected_variant": "b",
      "selected_file": "variants/anchor_1/anchor_1_b.png",
      "notes": "Best Persian palace feel"
    }
  }
  ```

- [ ] Add variant gallery page to Card Designer
  - New route: `/gallery/[deckId]` showing all cards with their variants side-by-side
  - Click to select winner, button to mark "none — regenerate"
  - Writes to `selections.json` via API route
  - Accessible from dev server during review workflow

- [ ] Add `--select` CLI fallback
  - For terminal-only workflows: opens variants folder, prompts for selection
  - Updates `selections.json`

- [ ] Add `--apply-selections` flag
  - Copies selected variants to `raw/{card_id}.png` (the canonical location)
  - Updates deck.json `image_path` field

#### Acceptance Criteria

- [ ] Can generate 2-4 variants per card in a single run
- [ ] Variants stored in organized directory structure
- [ ] Selection state persisted in `selections.json`
- [ ] Selected variants can be promoted to canonical `raw/{card_id}.png`

---

### Phase 3: Exploration Mode (Cheaper Model)

**Goal:** Iterate cheaply before committing to nano-banana-pro.

#### Tasks

- [ ] Research which Gemini models are cheaper/faster for exploration
  - Candidates: `gemini-2.0-flash-exp-image-generation`, or lower-res nano-banana settings
  - Key question: does gemini-flash support reference images? (currently no refs in `generate_image_gemini_flash()`)

- [ ] Add `--mode explore` flag
  - Uses cheaper model
  - Generates variants
  - Lower resolution acceptable for review (can use smaller aspect ratio or resolution)
  - Logged as `mode: "explore"` in generation log

- [ ] Add `--mode finalize` flag
  - Uses nano-banana-pro
  - Only generates for cards with selections (from `selections.json`)
  - Full resolution, full refs
  - Logged as `mode: "finalize"`

#### Acceptance Criteria

- [ ] Exploration mode demonstrably cheaper per image than finalize mode
- [ ] Explore → Select → Finalize workflow works end-to-end
- [ ] Both modes produce images with full provenance logging

---

### Phase 4: Style Reference (Hero Image)

**Goal:** Visual anchor that locks in the deck's art style.

#### Tasks

- [ ] Add `--mode style-lock` flag
  - Generates 2-3 hero images using a representative scene prompt
  - The prompt should combine the deck's `story_world` with a rich, representative scene
  - User selects winner → saved as `references/style_hero.png`

- [ ] Update `references/manifest.json` schema to include style hero
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

- [ ] Update `load_reference_images()` to include style heroes
  - Load appropriate hero from manifest based on card type
  - Story-world cards get `style_hero_story.png`
  - Modern-world cards get `style_hero_modern.png`
  - Pass as first reference with label: "Style reference — match this art style, color palette, and rendering quality:"

- [ ] Update `references/manifest.json` schema
  ```json
  {
    "style_hero_story": {
      "identity": "style_hero_story.png",
      "description": "Persian palace throne room, golden light, ornate arches"
    },
    "style_hero_modern": {
      "identity": "style_hero_modern.png",
      "description": "Warm Jewish preschool classroom, colorful rug, cubbies"
    },
    "esther": { "identity": "esther_identity.png" },
    ...
  }
  ```

- [ ] Visual Director output includes `hero_scene` prompt suggestions
  - Story-world hero: representative scene in the historical setting
  - Modern-world hero: representative classroom or community scene

#### Acceptance Criteria

- [ ] Two hero images generated: `style_hero_story.png` and `style_hero_modern.png`
- [ ] Story-world cards receive story hero as style reference
- [ ] Modern-world cards receive modern hero as style reference
- [ ] Cards show measurably more style consistency with hero refs vs without

---

### Phase 5: Selective Character References

**Goal:** Only pass reference images for characters that appear in the scene.

#### Tasks

- [ ] Add `characters_in_scene` field to card schema
  ```json
  {
    "card_id": "story_2",
    "card_type": "story",
    "characters_in_scene": ["mordechai", "haman"],
    ...
  }
  ```

- [ ] Update Visual Director output spec (`agents/definitions/05-visual-director.md`)
  - Visual Director must specify `characters_in_scene` for each card
  - Must include explicit exclusions for mentioned-but-not-shown characters

- [ ] Update `load_reference_images()` to accept filter list
  ```python
  def load_reference_images(deck_path, characters_in_scene=None):
      # If characters_in_scene provided, only load those refs
      # If None, load all (backwards compatible)
  ```

- [ ] Update `main()` to pass `characters_in_scene` from card data
  - Falls back to loading all refs if field not present (backwards compatible)

- [ ] Add `characters_in_scene` to Purim deck.json for all 16 cards
  - Tradition cards: `[]` (no story characters)
  - Connection cards: `[]` (generic children)
  - Story cards: only characters actually in scene
  - Spotlight cards: just the featured character

#### Acceptance Criteria

- [ ] Each card only receives references for characters actually in the scene
- [ ] Tradition/connection cards receive zero character refs
- [ ] Cards with `characters_in_scene: []` generate without any character refs
- [ ] Cards without the field still load all refs (backwards compatible)

---

### Phase 6: Sequential Card Chaining

**Goal:** Each card inherits the visual style of the previous card.

#### Tasks

- [ ] Define generation order
  - Story-world cards generated in narrative order: anchor → spotlight_1 → spotlight_2 → ... → story_1 → story_2 → ... → power_word
  - Modern-world cards generated together (connection + tradition) in their own batch
  - Order stored in deck.json or derived from `session` + `sequence_number` fields

- [ ] Add chain reference support to `generate_image_nano_banana()`
  - After generating card N, load its output image
  - Pass as additional reference to card N+1 with label: "Previous card in sequence — match this visual style and color palette:"
  - Chain ref is in ADDITION to character refs and style hero ref

- [ ] Add `--chain` flag to enable sequential chaining
  - Without flag: parallel-safe generation (no dependencies between cards)
  - With flag: sequential generation with chain refs
  - Implies no parallelization (each card depends on previous)

- [ ] Handle chain breaks
  - If a card fails to generate, skip chain ref for next card (use style hero only)
  - Log chain breaks in generation log

#### Acceptance Criteria

- [ ] Cards generated in narrative order when `--chain` flag used
- [ ] Each card receives previous card's image as style reference
- [ ] Chain breaks handled gracefully (fallback to style hero)
- [ ] Non-chained mode still works for parallel/independent generation

---

### Phase 7: Leaner Text Prompts

**Goal:** Reduce prompt noise for characters with reference images.

#### Tasks

- [ ] Add `--lean-prompts` flag (or make it default when refs are available)
  - When a character has a reference image, replace inline description with:
    ```
    MORDECHAI (see reference image):
    Standing tall and dignified, refusing to bow.
    ```
    Instead of:
    ```
    MORDECHAI:
    Older Jewish man, warm brown skin, kind wise eyes.
    Full gray-brown beard, dignified posture.
    Jewish head covering. Modest robes in earth tones.
    Standing tall and dignified, refusing to bow.
    ```

- [ ] Create `build_lean_character_block()` helper
  - Input: character key, action/pose description
  - Output: short reference to character ref + action only
  - Falls back to full description if no ref image exists

- [ ] Update documentation: Visual Director should write prompts assuming refs exist
  - Scene prompts focus on ACTION and EMOTION, not appearance
  - Character appearance is the reference image's job

#### Acceptance Criteria

- [ ] Prompts with character refs are significantly shorter
- [ ] Character appearance still maintained via reference images
- [ ] Prompts without refs still include full descriptions (backwards compatible)
- [ ] Generated images maintain character consistency (no regression)

---

### Phase 8: Agentic Workflow Integration

**Goal:** The multi-phase generation workflow fits cleanly into the 7-agent pipeline.

#### Tasks

- [ ] Update Agent Pipeline to include generation phases
  ```
  Agent 05 (Visual Director)
    → Outputs: image prompts, characters_in_scene, generation order
  Agent 06 (Editor)
    → Reviews prompts, approves for generation

  === GENERATION PIPELINE (new) ===
  Step G1: Style Lock
    → Generate hero image, human reviews
  Step G2: Explore
    → Cheap model, variants per card, logged
  Step G3: Curate
    → Human selects winners
  Step G4: Finalize
    → nano-banana-pro, full refs, chaining
  Step G5: Verify
    → Review consistency, flag re-generations
  === END GENERATION PIPELINE ===

  Agent 07 (Card Designer)
    → Text overlay + export
  ```

- [ ] Update `agents/AGENT_PIPELINE.md`
  - Add generation pipeline section between Editor and Card Designer
  - Document each step with inputs/outputs
  - Document human checkpoints (style lock review, variant selection, consistency review)

- [ ] Update Visual Director definition (`agents/definitions/05-visual-director.md`)
  - Output now includes `characters_in_scene` per card
  - Output includes recommended generation order
  - Output includes hero image prompt suggestion (representative scene for style lock)

- [ ] Update Torah Scholar definition (`agents/definitions/01-torah-scholar.md`)
  - Already outputs `story_world` (done in previous work)
  - Consider: should Torah Scholar also suggest a "representative scene" for the hero image?

- [ ] Create `agents/definitions/generation-pipeline.md`
  - Document the 5-step generation pipeline (G1-G5)
  - CLI commands for each step
  - Human checkpoint expectations
  - Cost implications (explore vs finalize)

- [ ] Update `LESSONS_LEARNED.md` with new patterns
  - "Always style-lock before generating cards"
  - "Use explore mode for first pass, finalize for selected"
  - "Chain refs smooth out style between sequential story cards"

#### Acceptance Criteria

- [ ] Agent pipeline docs clearly show where generation phases fit
- [ ] Visual Director output schema includes `characters_in_scene` and generation order
- [ ] Generation pipeline has its own definition doc
- [ ] Human checkpoints clearly documented (what to review, when)

---

## Alternative Approaches Considered

### 1. ControlNet / img2img for style consistency
**Rejected:** nano-banana-pro API doesn't support ControlNet. Would require switching to a different model/provider.

### 2. Fine-tuning a model on approved images
**Rejected:** Not enough training data yet (one deck). Could revisit after 5+ decks.

### 3. Generating all cards in one API call (multi-image)
**Rejected:** nano-banana-pro generates one image per call. Would require different architecture.

### 4. Using a separate style transfer step
**Rejected:** Adds complexity and potential quality loss. Style reference images are simpler.

---

## Resolved Design Decisions

### 1. Exploration model
**Decision:** Research alternatives first. Before committing to architecture, investigate Gemini model pricing, capabilities, and reference image support. This is a Phase 3 prerequisite task.

### 2. Hero image prompt authorship
**Decision:** Visual Director suggests. The Visual Director includes a `hero_scene` prompt in their output YAML — a representative scene that captures the story world's look. User can override during style-lock. Fits naturally into the agent workflow.

### 3. Chaining strictness
**Decision:** Hero does the heavy lifting. Chaining is supplementary, not critical. The hero image is the primary style anchor. Regenerating one card does NOT cascade to downstream cards. This keeps the system simple and avoids stale-chain complexity.

### 4. Selection UI
**Decision:** Card Designer gallery page. Add a variant review page to the Card Designer dev server (localhost). Side-by-side comparison of variants per card. More effort to build but significantly better UX for the core workflow of reviewing and selecting images.

### 5. Modern-world style anchor
**Decision:** Separate modern-world hero. Generate a dedicated modern-world style reference image (warm classroom or community scene). This anchors connection + tradition cards the same way the story-world hero anchors story cards. Two heroes per deck: one story-world, one modern-world.

### 6. Mode flexibility
**Decision:** Recommended order, soft enforcement. Warn if style-lock hasn't been run before explore/finalize, but allow overrides. Each mode should work independently for quick fixes. Best balance of guidance and flexibility.

---

## Risk Analysis & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Style hero doesn't improve consistency | Medium | Test with 2-3 hero variants before committing to full pipeline |
| Cheaper explore model produces misleading results | Medium | Validate that explore model's style broadly matches finalize model |
| Sequential chaining propagates errors | Medium | Chain breaks fallback to style hero; can regenerate single card without breaking chain |
| `characters_in_scene` field missing from old decks | Low | Backwards compatible — loads all refs when field absent |
| Generation log grows large | Low | JSONL format, one line per generation. Can rotate/archive |

---

## Git Worktree Strategy

This work should happen on a feature branch via git worktree to avoid blocking main:

```bash
git worktree add ../parasha-pack-image-pipeline-v2 -b feat/image-pipeline-v2
```

**Branch:** `feat/image-pipeline-v2`
**Merge strategy:** Squash merge to main after all phases complete

Phases can be merged incrementally if they're independently useful:
- Phase 1 (logging) is useful standalone
- Phases 2-3 (variants + explore) are useful together
- Phases 4-7 (hero, selective refs, chaining, lean prompts) build on each other
- Phase 8 (docs) goes with each code phase

---

## Documentation Plan

| Doc | What to Update |
|-----|---------------|
| `CLAUDE.md` | Add generation pipeline workflow, new CLI flags |
| `src/CLAUDE.md` | Document new generation modes, logging, variant storage |
| `decks/CLAUDE.md` | Document `characters_in_scene`, `selections.json`, `generations.jsonl`, `style_hero.png` |
| `agents/AGENT_PIPELINE.md` | Add generation pipeline between Editor and Card Designer |
| `agents/definitions/05-visual-director.md` | `characters_in_scene` output, generation order |
| `agents/definitions/generation-pipeline.md` | New: document the 5-step generation pipeline |
| `agents/VISUAL_SPECS.md` | Style hero reference system |
| `agents/LESSONS_LEARNED.md` | New patterns from this work |
| `CHANGELOG.md` | Each phase as it's completed |

---

## References

### Internal

- `src/generate_images.py` — Current generation orchestrator
- `src/image_prompts.py:79-137` — Style anchors + modern world style
- `src/schema.py:127-139` — Connection card front/back schemas
- `agents/AGENT_PIPELINE.md:206-221` — Current generation step
- `agents/definitions/05-visual-director.md` — Visual Director output spec
- `agents/LESSONS_LEARNED.md` — Character consistency gotchas
- `decks/archive/yitro/pipeline/` — Complete pipeline reference example

### Conversation Context

- Two-world system (story world + modern world) implemented in commits `016fb3f` and `b8bd45b`
- User confirmed Modern Orthodox conventions: knit kippot on men/boys, no head covering on women, casual modest dress, co-ed warm classrooms
