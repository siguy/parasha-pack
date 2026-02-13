# Card Deck Agent System

This document describes the agent-based workflow for creating Parasha Pack card decks and Holiday decks.

## Overview

The deck creation process is broken into specialized roles (agents), each with specific expertise, inputs, and outputs. This allows for:

- Clear separation of concerns
- Consistent quality
- Flexibility for different content types (parasha, holiday)
- Iterative improvement

## Agent Roster

| #   | Agent                                                        | Expertise                                 | Key Output          |
| --- | ------------------------------------------------------------ | ----------------------------------------- | ------------------- |
| 1   | [Torah Scholar](definitions/01-torah-scholar.md)             | Torah/holiday content, themes, continuity | Research doc        |
| 2   | [Curriculum Designer](definitions/02-curriculum-designer.md) | Early childhood education                 | Deck structure      |
| 3   | [Content Writer](definitions/03-content-writer.md)           | Kid-friendly writing                      | Card text + scripts |
| 4   | [Hebrew Expert](definitions/04-hebrew-expert.md)             | Biblical Hebrew, nikud                    | Hebrew content      |
| 5   | [Visual Director](definitions/05-visual-director.md)         | Art direction, consistency                | Image prompts       |
| 5b  | [Card Designer](definitions/09-card-designer.md)             | Card composition, front/back layout       | Final card images   |
| 5c  | [Designer Agent](definitions/09b-designer-agent.md)          | Visual pipeline orchestration             | Exported cards      |
| 6   | [Editor](definitions/06-editor.md)                           | Quality assurance                         | QA review           |
| 7   | [Print Producer](definitions/07-print-producer.md)           | Print production                          | Print-ready files   |
| 8   | [Web Producer](definitions/08-web-producer.md)               | Mobile web                                | Teacher guide site  |

## Workflow

```
[Torah Scholar]
      ↓ research doc (parasha OR holiday)
[Curriculum Designer]
      ↓ deck structure
      ↓ ← CHECKPOINT: Wife reviews direction (visual mockup)
      ↓
[Content Writer] ←→ [Hebrew Expert]
      ↓ complete card text (v2: front/back separation)
[Visual Director]
      ↓ character designs + image prompts (v2: composition zones, NO text)
      ↓
[Character Identity Generation] (tool)
      ↓ identity reference sheets
      ↓ ← CHECKPOINT: User reviews 2+ identity versions per NEW character
      ↓   (Select preferred version before proceeding)
      ↓
[Card Image Generation] (tool)
      ↓ raw card images (v2: no text rendered)
      ↓
┌─────────────────────────────────────────────────────────────────────┐
│  [Card Designer] (React app)                                        │
│       ↓ React components render text overlay + layout               │
│       ↓ INCLUDES: Card fronts AND card backs                        │
│       ↓ Export via Playwright → decks/<id>/images/                  │
│                                                                     │
│  Alternative: [Text Overlay + Card Back Generator] (PIL tools)      │
│       ↓ programmatic overlay + card back generation                 │
└─────────────────────────────────────────────────────────────────────┘
      ↓ final card images (fronts + backs, 5x7 @ 300 DPI)
      ↓
[Editor]
      ↓ QA review (v2: checks front/back content + overlay zones)
      ↓ ← CHECKPOINT: Wife + teachers review cards
      ↓
[Print Producer] ←→ [Web Producer]
      ↓
Physical cards (front + back) + Teacher guide
```

**Critical:** The Character Identity Checkpoint prevents wasted effort. A poor character identity means ALL cards featuring that character will need regeneration.

## Content Types

The workflow supports two content types:

| Type        | Description          | Cards | Sessions  |
| ----------- | -------------------- | ----- | --------- |
| **Parasha** | Weekly Torah portion | 8-11  | 1x 15 min |
| **Holiday** | Jewish holidays      | 12-16 | 2x 15 min |

See [FRAMEWORK.md](FRAMEWORK.md) for full details on card types and deck structure.

## Human Checkpoints

1. **After Curriculum Designer:** Wife reviews deck structure via visual mockup
2. **After Editor:** Wife + other teachers review complete deck with images

## Feedback Flow

Currently: Human (you) receives all feedback and routes to appropriate agent.

Future option: Add Feedback Coordinator agent if volume/complexity increases.

## Key Files

- [STYLE_GUIDE.md](STYLE_GUIDE.md) - Visual consistency rules
- [CARD_SPECS.md](CARD_SPECS.md) - Card type specifications
- [VISUAL_SPECS.md](VISUAL_SPECS.md) - Visual specs and composition guidance

## Card Format

- AI generates **scene-only images** to `raw/` (no text, no borders)
- `build_generation_prompt()` layers style, safety, composition, and rules at generation time
- **Card Designer (React)** renders text overlay and teacher content
- Card fronts: full-bleed images with React-rendered text
- Card backs: 5x7 printable teacher content (scripts, activities, questions)
- Image prompts in deck.json are **pure scene descriptions**

## Updating This Documentation

As you learn from each deck creation:

1. Update individual agent definitions with new learnings
2. Update FRAMEWORK.md if card structure evolves
3. Update YEAR_CONTEXT.yaml after each deck is complete
4. Add notes to STYLE_GUIDE.md for visual consistency

Version this documentation in git alongside the deck files.
