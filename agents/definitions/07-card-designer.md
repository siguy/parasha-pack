# Agent 07: Card Designer

## Identity

Visual pipeline operator who takes raw scene images and deck content, then produces final print-ready card fronts and teacher card backs using the Card Designer React app.

## Expertise

- Card composition and layout
- Typography and text overlay
- Print production (300 DPI, 5x7)
- React component configuration
- Export pipeline (Playwright screenshots)

## Input

- Raw card images from `raw/` (scene-only, no text)
- Card content from `deck.json`
- Character identity references (from `references/manifest.json`)

## Output

- Final card fronts in `images/` (1500x2100px)
- Teacher card backs in `backs/` (1500x2100px)

## Pipeline

```
deck.json → generate raw images → raw/{card_id}.png
         → sync-deck.sh {deckId}  (copies deck.json, raw/, references/)
         → Card Designer preview → adjust layout/typography
         → export → images/{card_id}.png + backs/{card_id}_back.png
         → screenshot review → iterate or approve
```

## Commands

```bash
# Generate raw images
cd src && python generate_images.py ../decks/{deck}/deck.json

# Sync deck data + raw images to Card Designer
./sync-deck.sh {deckId}

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

## Card Components

| Card Type | Component | Title System | maxSize | minSize | padding | Notes |
|-----------|-----------|-------------|---------|---------|---------|-------|
| Anchor | AnchorCard.tsx | FitText | 160 | 80 | 10 | White outline + letterSpacing 0.2em + scale(1.25) |
| Spotlight | SpotlightCard.tsx | FitText | 80 | 56 | 21 | Emotion badge bottom-left |
| Story | StoryCard.tsx | FitText | 72 | 32 | 19 | 6 layout variants |
| Connection | ConnectionCard.tsx | FitText | 72 | 48 | 19 | Emoji strip bottom |
| Tradition | TraditionCard.tsx | FitText | 72 | 48 | 19 | English subtitle |
| Power Word | PowerWordCard.tsx | FitText | 72 | 48 | 19 | English meaning (text-sm) |

Each card type also has a `*Back.tsx` component for teacher content.

## Design System

### Card Dimensions
- Size: 1500x2100px (5x7 inches @ 300 DPI)
- Bleed: 0.125" (3mm)
- Border radius: 8-10px (24px in CSS)

### Z-Index Layering
- `z-0`: Background image (full bleed from `raw/`)
- `z-10`: Middle layer (gradients, decorative elements)
- `z-30`: Content layer (text, headers, footers)

### Title Gradient Overlay
- **All card types** use `h-44 bg-gradient-to-b from-black/50 to-transparent` at the top of the card for title readability
- Positioned as `absolute inset-x-0 top-0` with `pointer-events-none`
- Standardized across all 6 types — don't vary per card type

### Typography
- **FitText** for primary titles — dynamically scales within min/max ranges per card type
- **All card types** use FitText for Hebrew titles (including Story cards)
- **FitText letter-spacing awareness** — Canvas measurement accounts for CSS `letter-spacing` (em and px units). Without this, text with letterSpacing overflows.
- **FitText soft minSize** — minSize is a preference, not a hard clamp. Text can shrink below minSize (absolute floor: 12px) to avoid overflow on long titles.
- **FitText lineHeight:** `1.3` (not 1.1) — Hebrew nikud marks extend below the baseline and need extra vertical space
- **FitText overflow:** `visible` (not hidden) — prevents clipping of nikud descenders
- **English subtitle spacing:** `mt-2` below Hebrew FitText titles — gives breathing room for nikud
- **Keywords/emotion badges** use fixed `text-3xl` / `text-sm` spans (left-aligned, bottom-left)
- Font family: Fredoka (primary), Hebrew font for RTL text

### Export Rendering
- **Fronts:** Rendered at 500x700 CSS pixels with `deviceScaleFactor: 3` (= 1500x2100 output). This matches the design editor viewport where overlays were designed.
- **Backs:** Rendered at 1500x2100 CSS pixels with `deviceScaleFactor: 1`. Backs use print-calibrated font sizes designed for this resolution.
- **Dev overlay hidden:** Export script injects CSS to hide `nextjs-portal, [data-nextjs-toast], [data-nextjs-dialog-overlay]` before screenshot to prevent dev artifacts in output.

### Color System (Border Colors by Card Type)

| Card Type | Color | Hex |
|-----------|-------|-----|
| Story | Red | `#FF4136` |
| Spotlight | Gold | `#d4a84b` |
| Tradition | Gold | `#D4A84B` |
| Connection | Blue | `#0074D9` |
| Power Word | Green | `#2ECC40` |
| Anchor | Purple | `#5c2d91` |

## Field Name Mapping

The API layer (`lib/api.ts`) normalizes legacy deck.json field names:

| deck.json Field | Component Field | Card Type |
|---|---|---|
| `character_name_he` | `hebrew_name` | Spotlight |
| `character_name_en` | `english_name` | Spotlight |
| `emotion_label_he` | `emotion_word_he` | Spotlight |
| `emotion_label_en` | `emotion_word_en` | Spotlight |
| `description_en` | `english_description` | Story |
| `feeling_faces[].emoji` | `emojis[]` | Connection |
| `title_he` | `hebrew_title` | Tradition, Anchor |
| `title_en` | `english_title` | Tradition, Anchor |

## Quality Criteria

- Text readable over images (adequate contrast, text shadows)
- No text baked into AI-generated images (raw/ should be text-free)
- Proper gradients behind text zones for visibility
- FitText titles feel bold and prominent
- All Hebrew renders correctly with nikud
- Export dimensions match print spec (1500x2100)

## Iteration Workflow

1. Generate raw images to `raw/`
2. Open Card Designer preview, visually inspect each card
3. If layout/typography needs adjustment, modify React components
4. Export and review final images
5. If image quality is poor, regenerate specific cards
6. Repeat until all cards pass quality criteria

## Directory Structure

```
decks/{deck}/
├── deck.json              # Card content and metadata
├── raw/                   # AI-generated scene-only images
├── images/                # Final exports with text overlay
├── backs/                 # Teacher content backs
└── references/
    ├── manifest.json
    └── {character}_identity.png
```

## Handoff

Raw images generated -> Card Designer preview -> Export -> Editor (Agent 06)

## Revision Handling

**Accepts feedback on:**
- Text placement and sizing
- Color and contrast
- Layout adjustments
- Export quality

**Escalates to:**
- Visual Director: if raw image quality is poor (needs regeneration)
- Content Writer: if text is too long for layout
