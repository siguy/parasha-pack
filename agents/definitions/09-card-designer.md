# Agent 09: Card Designer (Compositor)

**Input:**

- Raw card images (from Visual Director/Midjourney)
- Card Content YAML (from Content Writer)
- Layout Configuration (User preferences via valid text/color settings)

**Output:**

- Final high-resolution composite card images
- React Components (`.tsx`) for each card type

## Overview

The **Card Designer** is a custom React application that serves as the final assembly line for the deck. It uses a "Code-as-Design" approach where React components determine the layout, typography, and layering of the final card.

## Process: The "Text Overlay" System

Instead of manual design in tools like Photoshop, we use programmatic layouts:

1.  **Z-Index Layering:**
    - `z-0`: **Background Image** (Full bleed)
    - `z-10`: **Middle Layer** (Gradients, decorative elements)
    - `z-30`: **Content Layer** (Text, Headers, Footers)
2.  **Component Architecture:** Each card type is a separate React component, allowing for unique layouts while sharing a common `CardFrame` and design system (Tailwind CSS).
3.  **Dynamic Config:** The designer allows real-time tweaking of colors, font sizes, and standard/immersive modes.

## Card Templates Status

We have established React templates for the following card types:

### ✅ Completed (Fronts)

- **Story / Action Card** (`StoryCard.tsx`):
  - Features: Header bar, bottom narrative zone, dynamic keyword badge.
  - Layouts: Standard, Immersive, Scrapbook.
- **Spotlight Card** (`SpotlightCard.tsx`):
  - Features: Large centered Hebrew title, bottom emotion keyword.
  - Style: Full-bleed high impact.
- **Connection Card** (`ConnectionCard.tsx`):
  - Features: Story-style Header Bar (Hebrew top / English bottom), full-width emoji strip.
  - Status: **Front Design Finalized**.
- **Anchor Card** (`AnchorCard.tsx`):
  - Features: Central title focus.
  - Status: Functional template exists.
- **Tradition Card** (`TraditionCard.tsx`):
  - Features: Image-first layout.
  - Status: Functional template exists.
- **Power Word Card** (`PowerWordCard.tsx`):
  - Features: Large typography focus.
  - Status: Functional template exists.

## 🚧 To Be Done

1.  **Back-of-Card Designs:**
    - **ALL Cards:** We need to implement the reverse side logic.
    - _Constraint:_ Must support double-sided printing alignment.
    - _Content:_ Teacher scripts, discussion questions (Connection), full text translations.

2.  **Refinement:**
    - **Anchor/Tradition:** Review specific layout details to ensure they match the "Vibe" (Modern Luxury).
    - **Print Export:** Verify that the React implementation exports vertically to high-res suitable for print (300 DPI equivalent).

## Local Development Files

To visualize and edit a deck (e.g., Purim) locally:

1.  **Data Source:** `card-designer/content/purim` → symlink to `decks/purim`
    - Controls all text, image paths, and card configuration.
2.  **Raw Images:** `decks/purim/images/`
    - Place full resolution images here.
3.  **Visualizer Page:** `card-designer/app/[deckId]/page.tsx`
    - The React code that renders the deck at `http://localhost:3000/purim`.

## Export Workflow

### Prerequisites
- Playwright installed: `npx playwright install chromium` (run once)

### Export All Cards

```bash
cd card-designer
npm run export purim
```

This:
1. Auto-starts dev server if not running
2. Screenshots each card element via Playwright
3. Outputs to `../decks/purim/images/{card_id}.png` (1500x2100 @ 300 DPI)
4. Auto-stops dev server when done

### Export Single Card (Manual)
1. Run `npm run dev`
2. Visit `http://localhost:3000/{deckId}`
3. Click "Print to PNG" button on individual card

## Card Backs (TODO)

Card back components need to be implemented:
- `StoryCardBack.tsx` - Teacher script, roleplay prompt
- `ConnectionCardBack.tsx` - Discussion questions, feeling faces
- `SpotlightCardBack.tsx` - Character description, teaching moment
- etc.

Once implemented, the export script can be extended to export backs:
```bash
npm run export purim --with-backs
```
