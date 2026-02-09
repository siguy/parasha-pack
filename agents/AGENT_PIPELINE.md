# Parasha Pack Agent Pipeline Documentation

This document defines the agent pipeline for creating card decks. Each agent has specific responsibilities and MUST use data from previous agents rather than guessing.

## Critical Rules

1. **NEVER GUESS** - Each agent must use data from the pipeline YAML files, not assumptions
2. **VERIFY HEBREW SPELLING** - Always double-check Hebrew letter counts and spelling
3. **NO OLD DATA** - Do not reference old deck structures; use only the current pipeline files
4. **EXACT TEXT** - Prompts must specify EXACT text to render, with clear formatting instructions

---

## Agent 01: Parasha Scholar (Research)

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

**Card Type Mapping:**
| Type | Old Names | Purpose |
|------|-----------|---------|
| anchor | anchor | Parasha introduction |
| spotlight | spotlight, character | Character focus |
| action | story, action | Story sequence |
| connection | connection, thinker | Discussion/reflection |
| power_word | power_word, vocabulary | Hebrew vocabulary |

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
- Write discussion questions (3 per thinker card)
- Ensure sentences under 15 words

**Connection Card Questions:**

- DO NOT number questions ("Question 1:", etc.)
- Use simple bullet points or speech bubbles
- Three question types: emotional_empathy, cognitive_empathy, connection

**Must Include:**

- All card content with `card_id` matching structure
- `teacher_script` for each card
- `roleplay_prompt` for action cards
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

- Define character visual specs
- Set style notes for the deck
- Write card-specific composition notes
- Create pre-generation checklist

**Character Specs Must Include:**

- Physical description (face, clothing, props)
- Key features that MUST appear
- Reference sheet path if exists
- Whether new reference is needed

---

## Agent 06: Editor (Final Review)

**Input:** All pipeline files
**Output:** `pipeline/06-editor-review.yaml`

**Responsibilities:**

- Verify all content is complete
- Check Hebrew accuracy
- Confirm safety compliance
- Approve for generation

**Checklist:**

- [ ] All cards have content from previous agents
- [ ] Hebrew spelling verified (letter counts checked)
- [ ] No "Question 1/2/3" labels in connection card prompts
- [ ] Keyword badges positioned correctly in prompts
- [ ] Safety rules included in all relevant prompts

---

## Prompt Generation Rules

When generating image prompts from pipeline data:

### EXACT TEXT TO RENDER Section

**DO:**

```
=== EXACT TEXT TO RENDER ===
Title Bar: "Getting Help" with Hebrew "לְקַבֵּל עֶזְרָה" (include nikud)

Three Questions in speech bubbles (NO numbers, NO labels):
  - "First question text here"
  - "Second question text here"
  - "Third question text here"
```

**DON'T:**

```
Question 1: "First question"
Question 2: "Second question"
```

### Hebrew Spelling Notes

For words that AI commonly misspells, add explicit notes:

```
Large Hebrew Word: "שָׁמַע"
IMPORTANT: Exactly 3 letters: SHIN (ש) + MEM (מ) + AYIN (ע)
Only ONE mem in this word.
```

### Keyword Badge Placement

Specify exact location:

```
Keyword Badge (floating over bottom of illustration, NOT in text box):
  Hebrew: "קוֹל" in red rounded badge
  English: "Voice/Sound" small text below
```

---

## Common Errors to Avoid

1. **Adding "Question 1/2/3" labels** - Never number questions in prompts
2. **Double letters in Hebrew** - Always verify letter count
3. **Keyword in wrong position** - Specify badge vs. text box location
4. **Missing nikud in titles** - Always include vowel marks
5. **Using old card type names** - Use standardized names (action not story)
6. **Guessing content** - Only use data from pipeline files

---

## Regeneration Checklist

Before regenerating cards, verify:

1. [ ] Prompt has `=== EXACT TEXT TO RENDER ===` section
2. [ ] No numbered question labels
3. [ ] Hebrew spelling verified with letter count
4. [ ] Keyword badge location explicitly stated
5. [ ] Title includes "with Hebrew" and "include nikud" note
6. [ ] All text matches pipeline YAML content exactly

---

## Agent 09: Card Designer (Compositor)

**Input:** Raw images, Card Content YAML, Layout Config
**Output:** Final card composites (React Components)

**Responsibilities:**

- Apply programmatic text overlays to raw images
- Manage Z-index layering for readability
- implementations of `StoryCard`, `SpotlightCard`, etc.
- ensure text contrast via dynamic gradients

**Technical Rules:**

- **Header Zone (z-30):** Absolute top positioning for titles/icons
- **Narrative Zone (z-10):** Absolute bottom/flex for descriptions
- **Gradients:** Use `bg-gradient-to-b` (top) and `bg-gradient-to-t` (bottom)
- **Fonts:** `Outfit` (UI), `Frank Ruhl Libre` (Hebrew), `Patrick Hand` (Notes)
