# Agent 09b: Designer Agent (Visual Pipeline)

**Input:**
- deck.json with card content and image prompts
- Character identity references (from `references/manifest.json`)
- Card Designer React components and layout configuration

**Output:**
- Raw scene-only images in `raw/`
- Final exported card fronts in `images/`
- Final exported card backs in `backs/`

## Overview

The **Designer Agent** owns the full visual pipeline from scene-only image generation through final exported cards. It orchestrates the generation tool, Card Designer components, and export process, iterating until cards meet quality criteria.

## Pipeline

```
deck.json → generate raw images → raw/{card_id}.png
         → Card Designer preview → adjust layout/typography
         → export → images/{card_id}.png + backs/{card_id}_back.png
         → screenshot review → iterate or approve
```

## Capabilities

1. **Generate scene-only images** via `python generate_images.py`
2. **Configure Card Designer components** (typography, layout, colors)
3. **Export cards** via `npm run export`
4. **Take screenshots** to evaluate quality
5. **Iterate on design** until cards meet quality criteria

## Design System Knowledge

### Card Dimensions
- Size: 1500x2100px (5x7 inches @ 300 DPI)
- Bleed: 0.125" (3mm)
- Border radius: 8-10px (24px in CSS for round corners)

### Typography
- **FitText** for primary titles — dynamically scales within narrow min/max ranges per card type
- **Story cards** use fixed 28px with line wrapping (not FitText — titles are multi-word phrases)
- Font family: Fredoka (primary), Hebrew font for RTL text
- Title sizes: 38-80px (FitText auto-scales within range per card type)
- Subtitle/body: 14-24px fixed sizes

### Color System (Border Colors by Card Type)

| Card Type | Color | Hex |
|-----------|-------|-----|
| Story | Red | `#FF4136` |
| Spotlight | Gold | `#d4a84b` |
| Tradition | Gold | `#D4A84B` |
| Connection | Blue | `#0074D9` |
| Power Word | Green | `#2ECC40` |
| Anchor | Purple | `#5c2d91` |

### Layout Zones by Card Type

| Card Type | Title Zone | Content Zone | Notes |
|-----------|-----------|--------------|-------|
| Anchor | Top 10-15% | Full bleed image | FitText 80/64px, white outline effect |
| Spotlight | Top 5% | Full bleed | FitText 56/46px, emotion badge bottom-left |
| Story (Cinematic/Clean) | Top 3% | Full bleed | Fixed 28px wrapping, keyword bottom-left |
| Story (Standard) | Header bar | Split image/text | Header bar, keyword badge, description zone |
| Connection | Top 3% | Full bleed | FitText 48/38px white title, emoji strip bottom |
| Tradition | Top 3% | Full bleed | FitText 48/38px, English subtitle |
| Power Word | Top 6% | Full bleed | FitText 56/46px Hebrew word, English meaning |

### Hebrew Text Handling
- Always use `font-hebrew` class for Hebrew text
- RTL rendering handled automatically by FitText (centered, `text-align: center`)
- Nikud (vowel marks) render correctly at large sizes
- Text shadow for readability over images

### Quality Criteria
- Text must be readable over images (adequate contrast, text shadows)
- No text baked into AI-generated images (raw/ should be text-free)
- Proper gradients behind text zones for visibility
- FitText titles should feel bold and prominent
- All Hebrew renders correctly with nikud
- Export dimensions match print spec (1500x2100)

## Commands

```bash
# Generate raw images
cd src && python generate_images.py ../decks/{deck}/deck.json

# Start Card Designer dev server
cd card-designer && npm run dev

# Preview in browser
open http://localhost:3000/{deckId}

# Export fronts only
cd card-designer && npm run export {deckId}

# Export fronts AND backs
cd card-designer && npm run export {deckId} -- --backs

# Export backs only
cd card-designer && npm run export {deckId} -- --backs-only
```

## Iteration Workflow

1. Generate raw images to `raw/`
2. Open Card Designer preview, visually inspect each card
3. If layout/typography needs adjustment, modify React components
4. Export and review final images
5. If image quality is poor, regenerate specific cards:
   ```bash
   python generate_images.py ../decks/{deck}/deck.json --card story_3
   ```
6. Repeat until all cards pass quality criteria

## Field Name Mapping

The API layer (`lib/api.ts`) normalizes legacy deck.json field names:

| Legacy (deck.json) | Component Field | Card Type |
|---|---|---|
| `character_name_he` | `hebrew_name` | Spotlight |
| `character_name_en` | `english_name` | Spotlight |
| `emotion_label_he` | `emotion_word_he` | Spotlight |
| `emotion_label_en` | `emotion_word_en` | Spotlight |
| `description_en` | `english_description` | Story |
| `feeling_faces[].emoji` | `emojis[]` | Connection |
| `title_he` | `hebrew_title` | Tradition, Anchor |
| `title_en` | `english_title` | Tradition, Anchor |

## Directory Structure

```
decks/{deck}/
├── deck.json              # Card content and metadata
├── raw/                   # AI-generated scene-only images (no text)
│   ├── anchor_1.png
│   └── ...
├── images/                # Final exports with text overlay
│   ├── anchor_1.png
│   └── ...
├── backs/                 # Teacher content backs
│   ├── anchor_1_back.png
│   └── ...
└── references/
    ├── manifest.json
    └── {character}_identity.png
```
