# Visual Specifications

**Single source of truth for art style, colors, characters, and print specs.**

For card types and structure, see [CARD_SPECS.md](CARD_SPECS.md).
For agent responsibilities, see [definitions/](definitions/).

---

## Art Style

**Overall:** Vivid, high-contrast cartoon style suitable for ages 4-6.

Think: Colorful children's book illustration meets educational flashcard.

| Element | Specification |
|---------|---------------|
| Characters | Rounded, friendly shapes. Large expressive eyes (20% of face) |
| Forms | Simple shapes, no fine details or complex patterns |
| Lines | Thick, clean black outlines (2-3px equivalent) |
| Contrast | High contrast between foreground and background |
| Emotion | Big, clear facial expressions visible from across classroom |
| Complexity | Maximum 5-7 distinct visual elements per scene |

---

## Color Palette

### Primary Colors (main elements)
| Name | Hex | Use |
|------|-----|-----|
| Red | `#FF4136` | Story card borders, action elements |
| Blue | `#0074D9` | Connection card borders, water |
| Yellow | `#FFDC00` | Highlights, joy |
| Green | `#2ECC40` | Power Word borders, nature |

### Background Colors (soft pastels)
| Name | Hex | Use |
|------|-----|-----|
| Pink | `#FFE5E5` | Warm scenes |
| Light Blue | `#E5F0FF` | Sky, calm scenes |
| Cream | `#FFFBE5` | Text zones, warmth |
| Mint | `#E5FFE5` | Nature scenes |

### Card Type Borders
| Card Type | Color | Hex |
|-----------|-------|-----|
| Anchor | Deck theme | Varies |
| Spotlight | Gold | `#D4A84B` |
| Story | Red | `#FF4136` |
| Connection | Blue | `#0074D9` |
| Power Word | Green | `#2ECC40` |
| Tradition | Gold/Amber | `#D4A84B` |

### Theme Colors (deck borders)
| Theme | Hex | Parshiyot |
|-------|-----|-----------|
| Creation | `#1E3A5F` | Bereishit |
| Desert | `#C9A227` | Bamidbar |
| Water | `#2D8A8A` | Beshalach |
| Family | `#D4A84B` | Vayera, Toldot |
| Covenant | `#5C2D91` | Yitro |
| Redemption | `#A52A2A` | Bo, Shemot |
| Courage | `#8B5CF6` | Purim |

---

## Print Specifications

| Spec | Value |
|------|-------|
| Card Size | 5" x 7" (127 x 178 mm) |
| Resolution | 300 DPI |
| Pixel Size | 1500 x 2100 px |
| Bleed | 0.125" (3mm / 38px) |
| Corner Radius | 8-10px |
| Border Width | 8px |
| Paper | 350gsm cardstock |
| Finish | Matte lamination |

---

## Safety Rules (CRITICAL)

### Never Depict
- God in any human or physical form
- God's name in Hebrew (יהוה)
- Graphic violence, blood, or injury
- Death shown explicitly
- Scary monsters or frightening creatures
- Weapons causing harm
- Dark, shadowy, threatening environments
- QR codes or transliterations on card images

### Divine Presence (allowed representations)
- Warm golden/white light rays from above
- Glowing soft clouds with radiance
- Environmental effects (gentle wind, soft fire)
- Hands reaching from clouds (no body visible)

### Ten Commandments Tablets
- NEVER write God's name or actual commandment text
- Show exactly 5 letters on each tablet
- Use first 10 Hebrew letters as placeholders:
  - Left: א ב ג ד ה
  - Right: ו ז ח ט י

---

## Character Identity System

### Single Source of Truth

Each character has ONE identity reference image (`{character}_identity.png`) that serves as the visual anchor for all card generations.

**Why identity-only?** Multiple reference sheets generated independently from text produced inconsistent character interpretations.

### How It Works

1. Identity image is base64-encoded and passed to API with each card generation
2. Card prompts include character descriptions to reinforce visual features
3. The API uses both image reference AND text description for consistency

### Character Review Checkpoint

Before finalizing a new character identity:

1. Generate 2+ identity versions with variations
2. User reviews and selects preferred version
3. Rename selected to canonical: `{character}_identity.png`
4. Update `references/manifest.json`

### manifest.json Structure

```json
{
  "moses": {
    "identity": "decks/yitro/references/moses_identity.png"
  },
  "esther": {
    "identity": "decks/purim/references/esther_identity.png"
  }
}
```

---

## Established Character Designs

### Moses (מֹשֶׁה)
| Feature | Description |
|---------|-------------|
| Age | Middle-aged |
| Skin | Warm brown |
| Eyes | Kind, gentle |
| Beard | Short dark with some gray |
| Head | ALWAYS wears covering (cloth wrap/turban) |
| Clothing | Blue and cream robes |
| Props | Wooden shepherd's staff |
| Expression | Calm, patient, caring |

### Yitro (יִתְרוֹ)
| Feature | Description |
|---------|-------------|
| Age | Elderly |
| Skin | Warm tones |
| Eyes | Twinkling, wise |
| Beard | Long flowing white/gray |
| Clothing | Earth-toned desert robes (browns, tans, red/gold accents) |
| Props | Walking stick |
| Expression | Grandfatherly warm smile |

### Esther (אֶסְתֵּר)
| Feature | Description |
|---------|-------------|
| Age | Young woman |
| Skin | Warm olive |
| Eyes | Large, kind, brown |
| Hair | Long dark with elegant modest head covering |
| Clothing | Royal purple and blue flowing dress, simple gold tiara |
| Expression | Gentle, determined |

### Mordechai (מׇרְדְּכַי)
| Feature | Description |
|---------|-------------|
| Age | Older man |
| Skin | Warm brown |
| Eyes | Kind, wise |
| Beard | Full gray-brown |
| Head | Jewish head covering (kippah or cloth wrap) |
| Clothing | Modest robes in earth tones (browns, creams, subtle blues) |
| Expression | Dignified, grandfatherly warmth |

### Haman (הָמָן) - Villain
| Feature | Description |
|---------|-------------|
| Facial Hair | DARK POINTED GOATEE WITH CONNECTED MUSTACHE |
| Hat | DISTINCTIVE THREE-CORNERED HAT (hamantaschen shape) |
| Expression | Pouty, frustrated, jealous (NOT scary) |
| Clothing | Persian style, MUTED dusty purple and gray-brown |
| Posture | Arms crossed, shoulders hunched, turned away |

### Achashverosh (אֲחַשְׁוֵרוֹשׁ) - Misguided
| Feature | Description |
|---------|-------------|
| Crown | Large, ornate |
| Clothing | Royal Persian robes in golds and reds |
| Expression | Confused, bewildered, distracted |
| Style | Somewhat cartoonish, comedic |

---

## Villain Visual Guidelines

Antagonists are **misguided**, not scary.

### DO
| Element | Approach |
|---------|----------|
| Expression | Frustrated, jealous, confused, pouty |
| Colors | Muted purples, grays, dusty browns |
| Posture | Crossed arms, turned away, hunched shoulders |
| Eyes | Narrowed with frustration, looking away jealously |
| Overall | "Kid who made a bad choice" |

### DON'T
| Element | Avoid |
|---------|-------|
| Expression | Angry, menacing, sneering, evil grin |
| Colors | Black, blood red, dark shadows |
| Posture | Aggressive stance, pointing, looming |
| Eyes | Glaring, red/glowing, malice |
| Imagery | Skulls, shadows, dark clouds, scary backgrounds |

---

## Overlay Zones (v2 Cards)

For v2 cards, text is overlaid programmatically using PIL/Pillow after image generation.
The image must leave designated zones uncluttered.

| Card Type | Overlay Zone | Content | Background Treatment |
|-----------|--------------|---------|---------------------|
| Anchor | Top 20-25% | Hebrew parasha/holiday title | Simple gradient/sky |
| Spotlight | Top 30% | Hebrew name + English name + emotion | Simple gradient |
| Story | Bottom-left corner | Hebrew/English keyword badge | Scene continues, less detail |
| Connection | Bottom 20% | 4 emojis (no labels) | Simple gradient |
| Power Word | Top 30% | Hebrew word + English meaning | Simple gradient |
| Tradition | Top 25% | Hebrew/English title | Simple gradient |

### v2 Prompt Composition Instructions

Each card type has specific composition instructions:

- **Anchor**: "Compose the scene in the lower 70-80%. Keep top 20-25% uncluttered for Hebrew title overlay."
- **Spotlight**: "Compose the portrait in the lower 70%. Keep top 30% uncluttered for name and emotion overlay."
- **Story**: "Full-bleed scene. Keep bottom-left corner relatively simple for keyword badge overlay."
- **Connection**: "Compose the illustration in the upper 80%. Keep bottom 20% simple for emoji row overlay."
- **Power Word**: "Compose the illustration in the lower 70%. Keep top 30% uncluttered for Hebrew word overlay."
- **Tradition**: "Compose the scene in the lower 75%. Keep top 25% uncluttered for title overlay."

---

## Image Prompt Structure

### v1 Template (Legacy - Text in Image)

```
A vertical children's educational card in 5:7 aspect ratio (1500x2100 pixels).

=== STYLE ===
[Art style specifications]

=== RESTRICTIONS ===
[Safety rules - what NOT to show]

=== CARD TYPE: [TYPE] ===
[Card-specific requirements]

=== CHARACTERS ===
[Character descriptions - MUST match this document]

=== EXACT TEXT TO RENDER ===
[Precise text that will appear on card]

=== COMPOSITION ===
[Layout - NO percentages like "(12%)" - they render as text]

=== FRAME ===
[Border color, corners, icons]

=== MOOD ===
[Emotional tone]
```

### v2 Template (New - Programmatic Overlay)

```
A vertical children's educational card in 5:7 aspect ratio (1500x2100 pixels).

=== STYLE ===
[Art style specifications]

CRITICAL: Do NOT render any text in the image. No Hebrew, no English, no titles,
no labels, no badges. Text will be added programmatically after generation.

=== RESTRICTIONS ===
[Safety rules - what NOT to show]

=== CARD TYPE: [TYPE] ===
[Card-specific requirements]

=== CHARACTERS ===
[Character descriptions - MUST match this document]

=== COMPOSITION ZONES ===
[Specify which areas to keep uncluttered for overlay]
Compose the scene in the lower [X]% of the image.
Keep the top [Y]% uncluttered with simple gradient/sky for text overlay.

=== FRAME ===
[Border color, corners, icons]

=== MOOD ===
[Emotional tone]
```

### Prompt Gotchas

| Issue | Solution |
|-------|----------|
| Percentages render as text | Use words: "top third", "center", "bottom quarter" |
| Question labels render | NO "Question 1:" prefixes |
| Duplicate text appears twice | Check for repeated phrases in EXACT TEXT section |
| Wrong character appears | Only include refs for characters IN the scene |

---

## Reference Files

- Character identities: `decks/{deck}/references/{character}_identity.png`
- Manifest: `decks/{deck}/references/manifest.json`
- Card images: `decks/{deck}/images/{card_id}.png`
