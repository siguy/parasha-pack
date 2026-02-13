# Parasha Pack Agent Pipeline Documentation

This document defines the agent pipeline for creating card decks. Each agent has specific responsibilities and MUST use data from previous agents rather than guessing.

## Critical Rules

1. **NEVER GUESS** - Each agent must use data from the pipeline YAML files, not assumptions
2. **VERIFY HEBREW SPELLING** - Always double-check Hebrew letter counts and spelling
3. **NO OLD DATA** - Do not reference old deck structures; use only the current pipeline files
4. **SCENE-ONLY PROMPTS** - Image prompts are pure scene descriptions. Style, safety, composition, and rules are injected automatically by `build_generation_prompt()`
5. **TEXT RENDERED BY CARD DESIGNER** - AI never renders text. All text overlay is done by React components in the Card Designer

---

## Agent 01: Torah Scholar (Research)

**Input:** Torah portion name
**Output:** `pipeline/01-parasha-research.yaml`

**Responsibilities:**

- Research parasha themes, characters, key moments
- Identify emotional core and connection hooks
- List Hebrew vocabulary with correct nikud
- Document safety restrictions (no God depiction, etc.)
- Track character continuity (new vs. returning)

**Must Include:**

- `emotional_core`: Primary emotion/theme
- `key_moments`: Ranked list with visual potential
- `main_character` and `secondary_character`: With Hebrew names
- `hebrew_words`: Primary, secondary, and story keywords with nikud
- `avoid`: Safety restrictions list
- `continuity`: Character tracking

---

## Agent 02: Curriculum Designer (Structure)

**Input:** `01-parasha-research.yaml`
**Output:** `pipeline/02-deck-structure.yaml`

**Responsibilities:**

- Decide deck approach (narrative vs. thematic)
- Set card count (8-12) with rationale
- Assign card types and purposes
- Design session flow with timing
- Plan energy arc

**Card Types:**
| Type | Purpose |
|------|---------|
| anchor | Parasha introduction |
| spotlight | Character focus |
| story | Story sequence |
| connection | Discussion/reflection |
| tradition | Holiday practices (holiday decks only) |
| power_word | Hebrew vocabulary |

**Must Include:**

- `card_count` with rationale
- `session_flow.required_cards` with minutes
- `card_assignments` for each card with specific content

---

## Agent 03: Content Writer (English Content)

**Input:** `02-deck-structure.yaml`, `01-parasha-research.yaml`
**Output:** `pipeline/03-card-content.yaml`

**Responsibilities:**

- Write all English text: titles, descriptions, teacher scripts
- Create roleplay prompts (physical, doable for 18 kids)
- Write discussion questions (2 per connection card)
- Ensure sentences under 15 words

**Connection Card Questions:**

- DO NOT number questions ("Question 1:", etc.)
- Open-ended, not yes/no
- Mix: personal, empathy, action types

**Roleplay Rules:**

- Gender-neutral language ("give a royal wave" not "wave like a queen")
- Physical and doable in classroom
- Connected to emotional content

**Must Include:**

- All card content with `card_id` matching structure
- `teacher_script` for each card
- `roleplay_prompt` for story cards
- `questions` array for connection cards (no numbering!)

---

## Agent 04: Hebrew Expert (Hebrew Content)

**Input:** `03-card-content.yaml`, `01-parasha-research.yaml`
**Output:** `pipeline/04-hebrew-content.yaml`

**Responsibilities:**

- Add Hebrew translations with ACCURATE nikud
- Verify Torah quotes
- Set feeling face labels (Hebrew only on cards)
- Double-check word spelling

**Hebrew Spelling Verification:**

- Count letters in each word
- Verify nikud placement
- Check for common errors (double letters, wrong finals)

**Example - שָׁמַע (shama):**

- 3 letters ONLY: shin (ש) + mem (מ) + ayin (ע)
- NOT 4 letters, NOT double mem

**Must Include:**

- `*_he` fields for all text
- `hebrew_word_nikud` with verified spelling
- `feeling_faces` with Hebrew labels

---

## Agent 05: Visual Director (Art Direction)

**Input:** All previous YAML files
**Output:** `pipeline/05-visual-direction.yaml`

**Responsibilities:**

- Define character visual specs (appearance, clothing, props)
- Write **scene-only** image prompts for each card
- Manage character identity references
- Create pre-generation checklist

**Scene-Only Prompts:** The Visual Director writes what to draw, not how to draw it. `build_generation_prompt()` automatically layers style, safety, composition, and rules at generation time.

**Character Specs Must Include:**

- Physical description (face, clothing, props)
- Key features that MUST appear
- Reference sheet path if exists
- Whether new reference is needed

**Image Prompts Must Be:**

- Pure scene descriptions (what is happening, who is there, emotional tone)
- Character appearance details (reinforces reference images)
- 5-7 visual elements maximum per scene
- NO style instructions, NO safety rules, NO composition guidance, NO text rendering instructions

---

## Agent 06: Editor (Final Review)

**Input:** All pipeline files
**Output:** `pipeline/06-editor-review.yaml`

**Responsibilities:**

- Verify all content is complete
- Check Hebrew accuracy
- Confirm safety compliance
- Verify image prompts are scene-only (no style/composition/rules)
- Approve for generation

**Checklist:**

- [ ] All cards have content from previous agents
- [ ] Hebrew spelling verified (letter counts checked)
- [ ] No "Question 1/2/3" labels in connection card questions
- [ ] Image prompts are scene-only (no `=== STYLE ===` or similar sections)
- [ ] Safety compliance (no God in human form, no violence, modest dress)
- [ ] Roleplay prompts are gender-neutral and classroom-doable

---

## Assembly: Pipeline YAML → deck.json

After all 6 agents complete, assemble the pipeline outputs into `deck.json`:

1. Metadata from Agent 01 (name, ref, border_color, theme)
2. Card structure from Agent 02 (card types, sessions)
3. English content from Agent 03 (titles, descriptions, scripts)
4. Hebrew content from Agent 04 (translations, nikud)
5. Image prompts from Agent 05 (scene-only descriptions)

The resulting `deck.json` has all card content and scene-only `image_prompt` fields.

---

## Image Generation

```bash
# Generate raw scene-only images (no text, no borders)
cd src && python generate_images.py ../decks/{deck}/deck.json

# build_generation_prompt() automatically layers:
# 1. Style anchors (children's illustration)
# 2. Safety rules (no God in human form, etc.)
# 3. Scene description (from deck.json — passed through unchanged)
# 4. Per-card-type composition (cinematography language)
# 5. Critical rules (no text, no borders)
```

Character reference images from `references/manifest.json` are automatically included.

---

## Agent 09: Card Designer (Compositor)

**Input:** Raw images from `raw/`, card content from `deck.json`
**Output:** Final card images in `images/` and `backs/`

**Responsibilities:**

- Render text overlay on raw scene images (React components)
- Generate teacher content card backs
- Export print-ready 1500x2100 PNGs

**Technical Details:**

- **Z-index layering:** z-0 (background image), z-10 (gradients), z-30 (text)
- **FitText:** Dynamic title scaling within min/max size ranges per card type
- **Fonts:** Fredoka (UI), Hebrew font (RTL), Patrick Hand (notes)
- **Gradients:** `bg-gradient-to-b` (top) and `bg-gradient-to-t` (bottom) for text readability

```bash
# Export fronts and backs
cd card-designer && npm run export {deckId} -- --backs
```

---

## Common Errors to Avoid

1. **Adding style/composition to image prompts** - `build_generation_prompt()` handles this
2. **Double letters in Hebrew** - Always verify letter count
3. **Missing nikud** - Always include vowel marks in deck.json
4. **Numbering connection card questions** - Never use "Question 1:", etc.
5. **Guessing content** - Only use data from pipeline files

---

## Regeneration Checklist

Before regenerating card images, verify:

1. [ ] Image prompt in deck.json is scene-only (no style/safety/composition sections)
2. [ ] Character descriptions in prompt match reference sheet
3. [ ] Hebrew content in deck.json has correct nikud (for Card Designer to render)
4. [ ] Character reference images exist in `references/manifest.json`
5. [ ] All content fields populated (for Card Designer text overlay)

---

## Reference

- Working pipeline example: `decks/archive/yitro/pipeline/` (6 YAML files)
- Agent definitions: `agents/definitions/`
- Card type specs: `agents/CARD_SPECS.md`
- Visual specs: `agents/VISUAL_SPECS.md`
- Style guide: `agents/STYLE_GUIDE.md`
