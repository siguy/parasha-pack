# Card Specifications

**Single source of truth for card types, counts, and structure.**

For visual styling, see [VISUAL_SPECS.md](VISUAL_SPECS.md).
For agent responsibilities, see [definitions/](definitions/).

---

## Card Types

### Core Types (All Decks)

> Border colors and icons in these two tables are the **v2** ones. The v3 colors and icons are in
> "Colors and Icons" below (`card-designer/lib/cardTypes.ts`). The home card is v3-only.

| Type | Purpose | Energy | Border | Icon |
|------|---------|--------|--------|------|
| **Anchor** | Emotional entry point, deck theme | Calm | Deck theme | Crown/Symbol |
| **Spotlight** | Character introduction | Medium | Gold `#D4A84B` | Star |
| **Story** | Narrative moments + roleplay | Varies | Red `#FF4136` | Lightning |
| **Connection** | "Have you ever..." discussion | Calm | Blue `#0074D9` | Heart |
| **Power Word** | Hebrew vocabulary | Calm | Green `#2ECC40` | Book |

### Holiday-Only Type

| Type | Purpose | Energy | Border | Icon |
|------|---------|--------|--------|------|
| **Tradition** | Ritual practice + participation | Calm | Gold/Amber `#D4A84B` | Sparkle |

---

## Card Counts (decision D1)

| Card Type | Standard (10 cards) | Holiday (12 cards) |
|-----------|---------------------|--------------------|
| Anchor | 1 | 1 |
| Spotlight | 2 | 2 |
| Story | 4 | 3 |
| Tradition | — | 3 |
| Connection | 1 | 1 |
| Power Word | 1 | 1 |
| Home | 1 | 1 |

A holiday deck swaps one story card for three tradition cards. The home card is part of the count.
`schemas/pipeline/02-structure.schema.json` enforces the total; `src/assemble_deck.py` warns if the mix differs.

---

## Card Structure by Type

> **Note (v3):** the diagrams and "Required fields" lines below are the **v2 (Purim) front layouts**, kept
> for reference. In v3 every card has `card_id, card_type, title_en, title_he, characters_in_scene,
> image_prompt, image_path, back, guide` (`schemas/deck.v3.schema.json`); the teacher text lives in `back`
> (see "Card Back Structure (v3)" below) and the booklet text in `guide`.

### Anchor Card

```
┌─────────────────────────────────────────┐
│      [HEBREW TITLE]                     │  ← Large, centered
│      [English Title]                    │
│                                         │
│         CENTRAL SYMBOL                  │  ← Main illustration
│         (full bleed artwork)            │
│                                         │
│   "[Emotional hook text]"               │  ← Bottom text zone
└─────────────────────────────────────────┘
  ↑ Theme border color
```

**Required fields:** `title_en`, `title_he`, `emotional_hook_en/he`, `symbol_description`, `border_color`

### Spotlight Card

```
┌─────────────────────────────────────────┐
│ ★ [CHARACTER NAME]          [EMOTION]   │  ← Gold title bar
│   [Hebrew Name]             [Hebrew]    │
├─────────────────────────────────────────┤
│                                         │
│         CHARACTER PORTRAIT              │  ← 60% of card
│         (waist up, clear emotion)       │
│                                         │
├─────────────────────────────────────────┤
│  [2-3 sentence character description]   │  ← Cream background
│                                         │
│  [Teaching moment - for villains only]  │
└─────────────────────────────────────────┘
```

**Required fields:** `character_name_en/he`, `emotion_label_en/he`, `character_description_en/he`
**Villain cards add:** `portrayal: "misguided"`, `teaching_moment_en/he`

### Story Card

```
┌─────────────────────────────────────────┐
│ ⚡ [ENGLISH TITLE]                  #[N] │  ← Red title bar
│    [HEBREW TITLE]                       │
├─────────────────────────────────────────┤
│                                         │
│           ILLUSTRATION                  │  ← 60% of card
│           (scene with characters)       │
│                        ┌───────────┐    │
│                        │ [HEBREW]  │    │  ← Keyword badge
│                        │ [English] │    │
│                        └───────────┘    │
├─────────────────────────────────────────┤
│  [Story description - 2-3 sentences]    │  ← Cream background
│                                         │
│  (roleplay cue lives on the back: [cue]) │
└─────────────────────────────────────────┘
```

**Required fields:** `title_en/he`, `sequence_number`, `hebrew_key_word`, `description_en/he`, `roleplay_prompt`

**Roleplay rules:**
- Must be gender-neutral ("give a royal wave" not "wave like a queen")
- Physical and doable in classroom
- Connected to emotional content

### Connection Card

```
┌─────────────────────────────────────────┐
│      [ENGLISH TITLE]                    │  ← Blue title bar
│      [HEBREW TITLE]                     │
├─────────────────────────────────────────┤
│         ILLUSTRATION                    │  ← 35% (smaller)
│         (children thinking/sharing)     │
├─────────────────────────────────────────┤
│  😊    😢    😨    😮                   │  ← Feeling faces
│ [HE]  [HE]  [HE]  [HE]                  │
├─────────────────────────────────────────┤
│ ┌─────┐ ┌─────┐ ┌─────┐                 │  ← Question bubbles
│ │[Q1] │ │[Q2] │ │[Q3] │                 │    NO "Question 1:" labels
│ └─────┘ └─────┘ └─────┘                 │
├─────────────────────────────────────────┤
│   Torah Talk: [instruction]             │
└─────────────────────────────────────────┘
```

**Required fields:** `title_en/he`, `questions[]`, `feeling_faces[]`, `torah_talk_instruction`

**Question rules:**
- NO "Question 1:", "Question 2:" prefixes
- Open-ended, not yes/no
- Mix: personal, empathy, action types

### Tradition Card (Holiday Only)

```
┌─────────────────────────────────────────┐
│      [ENGLISH TITLE]                    │  ← Gold/amber title bar
│      [HEBREW TITLE]                     │
├─────────────────────────────────────────┤
│         ILLUSTRATION                    │  ← 50% of card
│         (community doing practice)      │    Warm, golden lighting
├─────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │ "[Story connection - why we do]"    │ │  ← Story connection box
│ └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ "[Practice description - what we do]"   │
│                                         │
│ ✨ "[Child action invitation]"          │  ← Sparkle, NOT star
└─────────────────────────────────────────┘
│   [HEBREW TERM]  •  [meaning]           │
└─────────────────────────────────────────┘
```

**Required fields:** `title_en/he`, `story_connection_en/he`, `practice_description_en/he`, `child_action_en/he`, `hebrew_term`, `hebrew_term_meaning`

**Tradition card rules:**
- Calm energy (no high-energy roleplay prompts)
- Invitation format ("Can you...?" not commands)
- Always placed at END of deck, after narrative
- Generic characters in illustrations unless story characters are doing the tradition

### Power Word Card

```
┌─────────────────────────────────────────┐
│         [LARGE HEBREW WORD]             │  ← With nikud
│              [meaning]                  │
├─────────────────────────────────────────┤
│         ILLUSTRATION                    │  ← Concept visualization
│         (child demonstrating word)      │
├─────────────────────────────────────────┤
│   "[Kid-friendly explanation]"          │
│                                         │
│   "[Example sentence]"                  │
└─────────────────────────────────────────┘
  ↑ Green border
```

**Required fields:** `hebrew_word`, `hebrew_word_nikud`, `english_meaning`, `example_sentence_en/he`, `kid_friendly_explanation_en/he`

---

## Session Flow (5-day week)

Each deck is taught across a week of short circle times (`week_plan` in deck.json, 5 days, 1–3 cards a
day, home card on day 5). Cards marked **★ core** alone make a complete ~15-minute lesson when time is short.

```
Day 1: Anchor + Story 1 → Day 2: Story 2 + Spotlight → Day 3: Spotlight + Story 4
→ Day 4: Connection → Day 5: Story 3 / Power Word + Home
```

**Energy arc:** calm hook → rising story → reflect (connection) → close (power word) → home.
Holiday decks put the tradition cards after the story, calm and inviting.

---

## Villain Portrayal

Antagonists are **misguided**, not scary:

| Character | Framing | Expression |
|-----------|---------|------------|
| Haman | "Felt jealous, made a bad choice" | Frustrated, pouty |
| Pharaoh | "Wouldn't listen, kept saying no" | Stubborn |
| Achashverosh | "Didn't think carefully" | Confused |

**Visual rules:** See [VISUAL_SPECS.md](VISUAL_SPECS.md#villain-visual-guidelines)

---

## Deck Types

### Parasha Approaches

| Type | Examples | Approach |
|------|----------|----------|
| Narrative | Yitro, Beshalach | Traditional story beats |
| Law-based | Mishpatim, Kedoshim | Rules as scenarios |
| Building | Terumah, Vayakhel | Contribution theme |
| Ritual | Vayikra, Tzav | Connect to modern practice |

### Holiday Approaches

| Type | Examples | Approach |
|------|----------|----------|
| Narrative-driven | Purim, Chanukah | Full story + traditions at end |
| Ritual-centered | Passover, Sukkot | Story context + heavy traditions |
| Thematic | Rosh Hashanah | Concepts + reflection + practices |

---

## JSON Schema Reference

See [/decks/CLAUDE.md](../decks/CLAUDE.md) for full JSON examples of each card type.

---

## Card Back Structure (v3: SAY / ASK / HEBREW)

Design: `docs/mockups/bereshit-v3.html`. One `CardBack` component renders every type.
The teacher reads the back top to bottom:

| Part | Shows | Source field (`back.*`) | Budget |
|------|-------|-------------------------|--------|
| **Header** | type icon + label ("Story 1"), "~5 min", ★ CORE | `minutes`, `core` | |
| **Title** | English title + Hebrew | card `title_en`, `title_he` (or `back.title_he`) | |
| **Goal** | 🎯 objective + the deck value pill | `objective`, deck `value.en` | **≤10 words** |
| **SAY** | what to read aloud. **Bold** = say it; ▸ chips = do it | `say` (`**bold**`, `[cue]`, newline) | **≤50 words** |
| **ASK** | ? questions, ✋ for answers without words | `ask[] {text, type}` | **≤2 questions, ≤12 words each** |
| **HEBREW** | word · translit · "meaning" + ✋ gesture | `hebrew {word, translit, meaning, note?, gesture}` | |
| **Footer** | ▸ transition (left), Guide p.N (right) | `transition`, `guide_ref {page, note?}` | |

`ask[].type` is one of `recall`, `wh`, `open`, `distancing`, `nonverbal`.

### Sections by Card Type

| Card Type | Sections (top to bottom) |
|-----------|--------------------------|
| **Anchor** | SAY, ASK, THIS WEEK strip (deck `week_plan`) |
| **Spotlight** | SAY, ASK, HEBREW |
| **Story** | SAY, ASK, HEBREW |
| **Connection** | SAY, ASK, feeling faces (`back.faces`, drawn SVG, max 4) |
| **Tradition** | SAY, ASK, HEBREW |
| **Power Word** | trio boxes (`back.trio`, exactly 3), SAY, ASK |
| **Home** | AT THE SHABBAT TABLE, ASK (`shabbat_question` EN + HE), HEBREW, TRY AT HOME (`try_at_home`, tagged Shabbat-friendly / before Shabbat) |

Everything else (background, Sages, hard questions, adaptations, extensions, tips) goes in
`card.guide` and is printed in the teacher guide booklet, not on the card.

### Colors and Icons

Every type color passes WCAG AA (≥4.5:1) with white and on the cream back. Each type also has its
own icon so color is never the only cue. Source: `card-designer/lib/cardTypes.ts`.

| Type | Color | Icon |
|------|-------|------|
| Anchor | `#5B2D8E` | crown |
| Spotlight | `#7E601A` | star |
| Story | `#B83227` | open book |
| Connection | `#1F5FA8` | heart |
| Tradition | `#0E7470` | candle |
| Power Word | `#2D7A3A` | speech bubble |
| Home | `#A84B16` | house |

Long text is never clipped silently: the export guard fails when a back's text doesn't fit (shorten it, don't shrink the font).

---

## Card Format

AI generates scene-only images. Card Designer (React) renders text overlays and card backs.

- Image prompts in deck.json are **pure scene descriptions** (no style, no composition, no rules)
- `build_generation_prompt()` layers style, safety, composition, and rules at generation time
- Card Designer renders text overlay on fronts and teacher content on backs

### Output Files

| File | Size | Purpose |
|------|------|---------|
| `raw/{card_id}.png` | 3:4 | Scene-only AI image (no text) |
| `images/{card_id}.png` | 2375x3125 | Card front, letter @ 300 DPI (5x7: `images/5x7/`, 1500x2100) |
| `backs/{card_id}_back.png` | 2375x3125 | Teacher card back, letter @ 300 DPI (5x7: `backs/5x7/`) |
| `print/{deck}-{format}.pdf` | letter / 5x7 pages | Duplex print PDF, front1, back1, front2… |

Default card = **8.5×11 letter** (one sheet per card, duplex, 0.3" white margin). Optional
**5×7 vendor** target: 5.25×7.25" with 0.125" bleed and a 0.25" safe zone.

See [/decks/CLAUDE.md](../decks/CLAUDE.md) for full JSON examples of each card type.
