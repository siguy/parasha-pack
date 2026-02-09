# Card Specifications

**Single source of truth for card types, counts, and structure.**

For visual styling, see [VISUAL_SPECS.md](VISUAL_SPECS.md).
For agent responsibilities, see [definitions/](definitions/).

---

## Card Types

### Core Types (All Decks)

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

## Card Counts

| Card Type | Parasha (8-11 total) | Holiday (12-16 total) |
|-----------|---------------------|----------------------|
| Anchor | 1 | 1 |
| Spotlight | 0-2 | 2-4 |
| Story | 3-4 | 5-6 |
| Connection | 2-3 | 2-3 |
| Tradition | — | 1-2 |
| Power Word | 0-1 | 0-1 |

---

## Card Structure by Type

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
│  ★ Act it out: [Roleplay prompt]        │  ← Gender-neutral!
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
- Calm energy (NOT "Act it out!" style)
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

## Session Flow

### Parasha (1 session, 15 min)

```
[Anchor] → [Spotlight] → [Story 1-2] → [Connection] → (optional)
```

**Core (10-12 min):** Anchor + Spotlight + 2 Story + 1 Connection = 5 cards

### Holiday (2+ sessions, 15 min each)

| Session | Cards | Focus |
|---------|-------|-------|
| 1 | Anchor + Spotlights + Story 1-3 | Meet characters, begin narrative |
| 2 | Story 4-6 + Connection + Tradition | Complete story, reflect, practice |

**Energy arc:**
```
Session 1: Calm → Meet heroes → Rising action
Session 2: Climax → Resolution → Reflection → Traditions (calm close)
```

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

## Card Format: v1 vs v2

### v1 (Legacy) - All Content on Front

Text is rendered in the generated image. All content visible on card front.

```json
{
  "card_id": "story_1",
  "card_type": "story",
  "title_en": "Esther Becomes Queen",
  "title_he": "אֶסְתֵּר נַעֲשֵׂית מַלְכָּה",
  "description_en": "The king chose Esther...",
  "roleplay_prompt": "Act it out: Put an imaginary crown...",
  "teacher_script": "The king needed a new queen...",
  "image_prompt": "... === EXACT TEXT TO RENDER === ...",
  "image_path": "images/story_1.png"
}
```

### v2 (New) - Front/Back Separation

Text is overlaid programmatically. Content separated for children (front) and teachers (back).

```json
{
  "card_id": "story_1",
  "card_type": "story",
  "front": {
    "overlay_zone": "bottom_left",
    "hebrew_keyword": "מַלְכָּה",
    "english_keyword": "Queen"
  },
  "back": {
    "title_en": "Esther Becomes Queen",
    "title_he": "אֶסְתֵּר נַעֲשֵׂית מַלְכָּה",
    "description_en": "The king chose Esther to be his new queen...",
    "description_he": "הַמֶּלֶךְ בָּחַר בְּאֶסְתֵּר...",
    "roleplay_prompt": "Act it out: Put an imaginary crown on your head...",
    "teacher_script": "The king needed a new queen..."
  },
  "image_prompt": "... === COMPOSITION ZONES === ...",
  "image_path": "images/story_1.png"
}
```

### v2 Front Fields by Card Type

| Card Type | Front Fields |
|-----------|--------------|
| Anchor | `hebrew_title` |
| Spotlight | `hebrew_name`, `english_name`, `emotion_word_en`, `emotion_word_he` |
| Story | `hebrew_keyword`, `english_keyword` |
| Connection | `emojis` (list of 4 emoji characters) |
| Power Word | `hebrew_word`, `english_meaning` |
| Tradition | `hebrew_title`, `english_title` |

### v2 Output Files

| File | Size | Purpose |
|------|------|---------|
| `images/{card_id}.png` | 1500x2100 | Raw generated image (no text) |
| `images/{card_id}_front.png` | 1500x2100 | Image with overlaid text |
| `backs/{card_id}_back.png` | 1500x2100 | 5x7 teacher card back |
