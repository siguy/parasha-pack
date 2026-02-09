# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Code Quality Improvements

#### Error Handling
- `generate_images.py`: Added warning log for silent manifest load failures (was swallowing exceptions)

#### Documentation Fixes
- Removed dead references to deleted `FRAMEWORK.md` and `YEAR_CONTEXT.yaml` from `agents/AGENTS.md`
- Updated `src/CLAUDE.md` CLI documentation to match actual `generate_images.py` flags
- Added deprecation comments to legacy `CardType` aliases (`ACTION`, `THINKER`) in `schema.py`

---

### Major Refactor: Card Designer as Single Source of Truth

**Eliminated double overlays** by separating raw AI-generated images from final composited output.

#### New Architecture
- **`raw/` directory**: AI generates scene-only images (no text) to `decks/{deck}/raw/`
- **Card Designer React**: All text rendering via React/Tailwind components
- **Export to `images/` and `backs/`**: Final print-ready PNGs with text overlay

#### New Components
- `CardBackFrame.tsx`: Shared 5x7 frame for all card backs
- `StoryCardBack.tsx`: Story card teacher content
- `SpotlightCardBack.tsx`: Character card teacher content
- `ConnectionCardBack.tsx`: Discussion card with questions and feeling faces
- `AnchorCardBack.tsx`: Parasha/Holiday intro card teacher content
- `TraditionCardBack.tsx`: Holiday tradition card teacher content
- `PowerWordCardBack.tsx`: Vocabulary card with explanations and examples

#### Updated Components
- `CardFactory.tsx`: Added `side` prop ('front' | 'back') for routing
- `generate_images.py`: Now outputs to `raw/` directory, removed PIL overlay flags
- `export-deck.ts`: Added `--backs`, `--backs-only`, `--fronts-only` flags

#### Deprecated
- `overlay.py`: PIL text overlay - use Card Designer instead
- `card_back_generator.py`: PIL card backs - use Card Designer instead
- `--with-overlay`, `--overlay-only`, `--backs-only` flags in generate_images.py

#### Workflow
```bash
# 1. Generate raw images (no text)
cd src && python generate_images.py ../decks/purim/deck.json

# 2. Export with Card Designer
cd card-designer && npm run export purim -- --backs
```

---

### Added

#### Card Designer Export Pipeline
- **Playwright export script** (`card-designer/scripts/export-deck.ts`): Headless batch export of all cards
  - Auto-starts dev server if not running
  - Exports 1500x2100 PNG (5x7 @ 300 DPI print-ready)
  - Usage: `cd card-designer && npm run export purim`
- **Dedicated export route** (`card-designer/app/export/[deckId]/[cardId]/page.tsx`): Full-resolution single-card rendering
- **Content symlink**: `card-designer/content/purim` → `../../decks/purim` (prevents stale copies)

#### v2 Card Format (Front/Back Separation)
- **Card Back Generator** (`src/card_back_generator.py`): Generates 5x7 printable teacher-facing card backs
- **Text Overlay System** (`src/overlay.py`): Programmatic text overlay for card fronts using PIL/Pillow
- New deck.json schema with `front` and `back` objects per card
- Support for `--with-overlay`, `--overlay-only`, `--backs-only`, `--no-overlay` flags in generate_images.py

#### Character Reference Labeling
- Reference images now include text labels before each image in API payload
- Labels map character keys to friendly names (e.g., "haman" → "Haman (the villain)")
- Final instruction text added after all references: "Use the above character references for visual consistency. Now generate:"

#### Global Image Prompt Rules
- **Anti-noise requirements**: "Clean digital illustration. Absolutely NO grain, film texture, stippling, noise, or analog artifacts."
- **Anatomy requirements**: "All humans have exactly 2 arms, 2 legs, 5 fingers per hand."
- **Jewish school context**: "Boys wearing kippot. Girls wearing modest skirts or dresses (no kippot for girls)."
- **No Hebrew on surfaces**: "Do NOT render any Hebrew letters on walls, signs, books, or any surface - generated Hebrew is always wrong."

#### Purim Deck (First v2 Deck)
- 16 cards with full v2 structure
- Character references: Esther, Mordechai, Haman, King Achashverosh
- Connection cards with emoji strips rendered in-image (not overlaid)

### Changed

#### Agent Workflow
- **Card Designer** now positioned as Agent 5b (between Visual Director and Editor)
- Workflow diagram updated to show Card Designer as alternative to PIL-based Text Overlay tools

#### ConnectionCard.tsx
- Titles now use dynamic `card.title_he` / `card.title_en` instead of hardcoded "חִבּוּר" / "CONNECTION"

#### Image Prompt Engineering
- Removed all "overlay" language from prompts (was confusing the model into creating gradients)
- Connection card emojis now rendered by AI model in bottom 15% strip rather than programmatic overlay
- Power Word cards now feature story-relevant heroes (e.g., Esther for Purim) instead of generic children
- Updated STYLE_ANCHORS_V2 with cultural context section

#### Documentation Updates
- `CLAUDE.md`: Added v2 card format documentation, character consistency workflow
- `src/CLAUDE.md`: Added overlay.py and card_back_generator.py module docs
- `decks/CLAUDE.md`: Added v2 deck structure documentation
- `agents/CARD_SPECS.md`: Added v2 JSON schema specifications
- `agents/VISUAL_SPECS.md`: Added composition zone guidelines

### Fixed

- Character reference images now properly labeled so model knows which character each image represents
- Removed Muslim-appearing children from classroom scenes (now explicitly Jewish school context)
- Fixed anatomy issues (e.g., king with 3 arms) by adding explicit anatomy requirements
- Fixed villain appearing in celebration scenes (tradition_3: Haman removed from mishloach manot scene)
- Removed image noise/grain artifacts through anti-noise prompt rules

### Technical Details

#### generate_images.py Changes
```python
# New: Character label mapping
character_labels = {
    "esther": "Esther (Queen Esther)",
    "mordechai": "Mordechai",
    "haman": "Haman (the villain)",
    "achashverosh": "King Achashverosh (the king)",
    ...
}

# New: Labeled reference image parts
image_parts.append({"text": f"Character reference for {label}:"})
image_parts.append({"inlineData": {"mimeType": "image/png", "data": image_data}})
image_parts.append({"text": "Use the above character references for visual consistency. Now generate:"})
```

#### image_prompts.py Changes
```python
STYLE_ANCHORS_V2 = """
...
CULTURAL CONTEXT:
- This is for a JEWISH school (preschool/kindergarten ages 4-6)
- Boys wear kippot (head coverings)
- Girls wear modest skirts or dresses (girls do NOT wear kippot)
- Do NOT put any Hebrew letters or text on walls, posters, or signs

TECHNICAL REQUIREMENTS:
- CRITICAL: Clean digital illustration. Absolutely NO grain, film texture, stippling, noise
- CRITICAL ANATOMY: All humans must have exactly 2 arms (one left, one right), 2 legs, 5 fingers per hand
...
"""
```
