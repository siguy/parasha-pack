# Agent 09: Card Designer (Compositor)

**Input:**

- Raw card images from `raw/` directory (scene-only, no text)
- Card content from `deck.json`
- Layout configuration (user preferences via editor UI)

**Output:**

- Final high-resolution composite card fronts (`images/`)
- Final card backs with teacher content (`backs/`)
- React Components (`.tsx`) for each card type

## Overview

The **Card Designer** is a custom Next.js/React application that serves as the final assembly line for the deck. It uses a "Code-as-Design" approach where React components determine the layout, typography, and layering of the final card.

## Process: The "Text Overlay" System

Instead of manual design in tools like Photoshop, we use programmatic layouts:

1.  **Z-Index Layering:**
    - `z-0`: **Background Image** (Full bleed from `raw/`)
    - `z-10`: **Middle Layer** (Gradients, decorative elements)
    - `z-30`: **Content Layer** (Text, Headers, Footers)
2.  **Component Architecture:** Each card type is a separate React component, allowing for unique layouts while sharing a common `CardFrame` and design system (Tailwind CSS).
3.  **Dynamic Config:** The designer allows real-time tweaking of colors, font sizes, and standard/immersive modes.
4.  **FitText System:** Primary titles use the `FitText` component (`components/ui/FitText.tsx`) that dynamically scales text to fill the available container width, ensuring bold prominent titles regardless of text length.

## Card Templates

### Completed (Fronts + Backs)

- **Story / Action Card** (`StoryCard.tsx` / `StoryCardBack.tsx`):
  - Features: Header bar, bottom narrative zone, dynamic keyword badge.
  - Layouts: Standard, Immersive, Immersive-Floating, Immersive-Cinematic, Immersive-Clean, Scrapbook.
  - Title: FitText (72px max in cinematic/clean layouts).
- **Spotlight Card** (`SpotlightCard.tsx` / `SpotlightCardBack.tsx`):
  - Features: FitText Hebrew name (96px max), bottom emotion badge.
  - Style: Full-bleed high impact.
- **Connection Card** (`ConnectionCard.tsx` / `ConnectionCardBack.tsx`):
  - Features: FitText title (72px max), full-width emoji strip.
  - Emojis auto-extracted from `feeling_faces[].emoji` via field mapping.
- **Anchor Card** (`AnchorCard.tsx` / `AnchorCardBack.tsx`):
  - Features: FitText Hebrew title (120px max) with white outline effect.
- **Tradition Card** (`TraditionCard.tsx` / `TraditionCardBack.tsx`):
  - Features: FitText Hebrew title (110px max), English subtitle, separator line.
- **Power Word Card** (`PowerWordCard.tsx` / `PowerWordCardBack.tsx`):
  - Features: FitText Hebrew word (120px max), English meaning pill badge.

## Field Name Mapping

The API layer (`lib/api.ts`) normalizes legacy deck.json field names to match component expectations. See [09b-designer-agent.md](09b-designer-agent.md) for the full mapping table.

## Image Flow

```
raw/{card_id}.png          ← AI-generated scene-only images (no text)
     ↓
Card Designer preview      ← React renders text overlay
     ↓
images/{card_id}.png       ← Exported card fronts (1500x2100)
backs/{card_id}_back.png   ← Exported card backs (1500x2100)
```

The `raw/` directory is the source of truth for AI images. The `images/` and `backs/` directories contain Card Designer exports.

## Local Development Files

To visualize and edit a deck (e.g., Purim) locally:

1.  **Data Source:** `card-designer/content/purim/deck.json`
    - Controls all text, image paths, and card configuration.
2.  **Raw Images:** `card-designer/content/purim/raw/`
    - Scene-only images served by the image API.
3.  **Visualizer Page:** `card-designer/app/[deckId]/page.tsx`
    - Renders the deck at `http://localhost:3000/purim`.

## Export Workflow

### Prerequisites
- Playwright installed: `npx playwright install chromium` (run once)

### Export Commands

```bash
cd card-designer

# Export fronts only (default)
npm run export purim

# Export fronts AND backs
npm run export purim -- --backs

# Export backs only
npm run export purim -- --backs-only
```

This:
1. Auto-starts dev server if not running
2. Screenshots each card element via Playwright
3. Outputs to `../decks/purim/images/{card_id}.png` (1500x2100 @ 300 DPI)
4. Backs output to `../decks/purim/backs/{card_id}_back.png`
5. Auto-stops dev server when done

### Export Single Card (Manual)
1. Run `npm run dev`
2. Visit `http://localhost:3000/{deckId}`
3. Click "Print to PNG" button on individual card
