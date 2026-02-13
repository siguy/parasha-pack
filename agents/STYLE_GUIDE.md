# Parasha Packs Visual Style Guide

## Art Style

**Overall:** Vivid, high-contrast cartoon style suitable for ages 4-6.

**Characteristics:**
- **Characters:** Rounded, friendly shapes. Large expressive eyes (20% of face).
- **Forms:** Simple shapes, no fine details or complex patterns.
- **Lines:** Thick, clean black outlines (2-3px equivalent).
- **Contrast:** High contrast between foreground and background.
- **Complexity:** Maximum 5-7 distinct visual elements per scene.

**Think:** Colorful children's book illustration meets educational flashcard.

## Color Palette

### Primary Colors (for main elements)
- Red: #FF4136
- Blue: #0074D9
- Yellow: #FFDC00
- Green: #2ECC40

### Background Colors (soft pastels)
- Pink: #FFE5E5
- Light Blue: #E5F0FF
- Cream: #FFFBE5
- Mint: #E5FFE5

### Card Type Border Colors
- Anchor: #1e3a5f (dark blue)
- Spotlight: #d4a84b (gold)
- Story: #FF4136 (red)
- Connection: #0074D9 (blue)
- Power Word: #2ECC40 (green)

### Theme Colors (deck borders)
- Creation: #1e3a5f (deep blue)
- Desert: #c9a227 (sandy gold)
- Water: #2d8a8a (teal)
- Family: #d4a84b (warm amber)
- Covenant: #5c2d91 (royal purple)
- Redemption: #a52a2a (crimson)

## Card Specifications

- **Size:** 5" x 7" (1500 x 2100 pixels at 300 DPI)
- **Corners:** Rounded (8-10px radius)
- **Border:** 8px width, color based on card type
- **Bleed:** 0.125" (additional 38px on each side for print)

## Card Back Design

**Elements:**
- Parasha Packs logo (centered)
- Parasha name in Hebrew + English (variable per deck)
- Card type indicator (optional)
- Consistent border treatment matching card type
- Background pattern or color (TBD)

**Rendered by:** Card Designer React components (see `card-designer/components/cards/*Back.tsx`)

## Character Design Principles

### General Rules
- All characters dressed modestly
- Warm, approachable expressions
- Clear silhouettes (recognizable at small size)
- Consistent proportions across all appearances

### Character Identity Reference (Single Source of Truth)

Each major character has ONE identity reference sheet:
- **Identity sheet:** Portrait + full body side by side (16:9 aspect ratio)

**Why identity-only?** Multiple reference sheets (expressions, turnaround, poses) generated independently from text produced inconsistent character interpretations. A single identity image serves as the visual anchor for ALL card generations.

**How it works:**
1. Identity image is base64-encoded and passed to the API with each card generation
2. Card prompts include character descriptions to reinforce visual features
3. The API uses both the image reference AND text description for consistency

**Character Review Checkpoint:**
Before finalizing a new character identity:
1. Generate 2+ identity versions with variations
2. User reviews and selects preferred version
3. Rename selected version to canonical name: `{character}_identity.png`
4. Only then proceed to card generation

### Existing Character Designs

**Moses (מֹשֶׁה):**
- Friendly middle-aged man
- Warm brown skin, kind gentle eyes
- Short dark beard with some gray
- **Always wears head covering** (cloth wrap or turban)
- Blue and cream robes
- Wooden shepherd's staff

**Yitro (יִתְרוֹ):**
- Wise elderly man
- Long flowing white/gray beard
- Twinkling wise eyes
- Colorful earth-toned robes (Midianite style: browns, tans, red/gold accents)
- Walking stick
- Grandfatherly warm smile

## Safety Rules (CRITICAL)

### Never Depict
- God in any human or physical form
- God's name in Hebrew (יהוה)
- Graphic violence or death
- Scary monsters or frightening imagery
- Immodestly dressed characters

### How to Show Divine Presence
- Warm golden/white light rays from above
- Glowing soft clouds with radiance
- Hands reaching from clouds (if necessary, but prefer light)

### Ten Commandments Tablets
- Always show exactly 5 letters on each tablet
- Use first 10 letters of Hebrew alphabet: א ב ג ד ה | ו ז ח ט י
- **Never** use God's name or actual commandment text

## Typography

### Hebrew Text
- Always include nikud (vowel marks)
- Clear, readable font
- Large enough to read from across a classroom

### English Text
- Simple, friendly sans-serif font
- Age-appropriate language
- High contrast against background

## Image Prompt Structure

Image prompts in `deck.json` are **pure scene descriptions** — what to draw, not how to draw it.

`build_generation_prompt()` in `generate_images.py` automatically layers:
1. Style anchors (children's illustration, cultural context, anatomy rules)
2. Safety rules (no God in human form, no violence, modest dress)
3. Scene description (from deck.json — passed through unchanged)
4. Per-card-type composition guidance (cinematography language for subject placement)
5. Critical rules (no text, no borders)

**Scene prompt format:**
```
[Character name/description]
[Visual appearance — reinforces reference images]

[Scene description — what is happening, where, who is involved]
[Key visual elements — 5-7 maximum]
[Character emotions and body language]

[Emotional tone — what viewers should feel]
```

**Example:**
```
Esther standing before the king's throne, hand raised to speak.
Young Jewish woman, warm olive skin, large kind brown eyes.
Royal purple dress, simple gold tiara.

Tall stone pillars frame the scene. Golden light from high windows.
Courtiers watch with surprise. Rich tapestries on walls.

Brave and determined. A quiet courage that changes everything.
```

## Cross-Deck Consistency Checklist

Before finalizing any deck:
- [ ] Characters match their reference sheets
- [ ] Art style consistent with previous decks
- [ ] Color palette follows this guide
- [ ] Border colors correct for card types
- [ ] Safety rules followed in all images
- [ ] Hebrew text has nikud
- [ ] Card backs use consistent template

## Updating This Guide

As you create more decks:
1. Add new character designs to "Existing Character Designs" section
2. Note any style refinements that work well
3. Add examples of successful/unsuccessful approaches
4. Update color palette if new themes are added
