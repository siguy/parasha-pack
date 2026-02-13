# Card Deck Agent System

This document describes the agent-based workflow for creating Parasha Pack card decks and Holiday decks.

## Overview

The deck creation process is broken into specialized roles (agents), each with specific expertise, inputs, and outputs. This allows for:

- Clear separation of concerns
- Consistent quality
- Flexibility for different content types (parasha, holiday)
- Iterative improvement

## Agent Roster

| # | Agent | Expertise | Key Output |
|---|-------|-----------|------------|
| 1 | [Torah Scholar](definitions/01-torah-scholar.md) | Torah/holiday content, themes, continuity | Research doc |
| 2 | [Curriculum Designer](definitions/02-curriculum-designer.md) | Early childhood education | Deck structure |
| 3 | [Content Writer](definitions/03-content-writer.md) | Kid-friendly writing | Card text + scripts |
| 4 | [Hebrew Expert](definitions/04-hebrew-expert.md) | Biblical Hebrew, nikud | Hebrew content |
| 5 | [Visual Director](definitions/05-visual-director.md) | Art direction, consistency | Image prompts |
| 6 | [Editor](definitions/06-editor.md) | Quality assurance | QA review |
| 7 | [Card Designer](definitions/07-card-designer.md) | Card composition, export | Final card images |

## Workflow

```
[Torah Scholar]
      ↓ research doc (parasha OR holiday)
[Curriculum Designer]
      ↓ deck structure
      ↓ ← CHECKPOINT: Wife reviews direction
      ↓
[Content Writer] ←→ [Hebrew Expert]
      ↓ complete card text (front/back content)
[Visual Director]
      ↓ character designs + scene-only image prompts
      ↓
[Character Identity Generation] (tool)
      ↓ identity reference sheets
      ↓ ← CHECKPOINT: User reviews 2+ identity versions per NEW character
      ↓
[Card Image Generation] (tool)
      ↓ raw card images (no text rendered)
      ↓
[Card Designer] (React app)
      ↓ text overlay + teacher card backs
      ↓ export via Playwright → decks/<id>/images/ + backs/
      ↓
[Editor]
      ↓ QA review (checks front/back content + overlay)
      ↓ ← CHECKPOINT: Wife + teachers review cards
      ↓
Final cards (front + back, 5x7 @ 300 DPI)
```

**Critical:** The Character Identity Checkpoint prevents wasted effort. A poor character identity means ALL cards featuring that character will need regeneration.

## Content Types

| Type | Description | Cards | Sessions |
|------|-------------|-------|----------|
| **Parasha** | Weekly Torah portion | 8-11 | 1x 15 min |
| **Holiday** | Jewish holidays | 12-16 | 2x 15 min |

See [CARD_SPECS.md](CARD_SPECS.md) for card type details and deck structure.

## Human Checkpoints

1. **After Curriculum Designer:** Wife reviews deck structure via visual mockup
2. **After Character Identity Generation:** User reviews 2+ identity versions, selects best
3. **After Editor:** Wife + other teachers review complete deck with images

## Feedback Flow

Currently: Human (you) receives all feedback and routes to appropriate agent.

## Card Format

- AI generates **scene-only images** to `raw/` (no text, no borders)
- `build_generation_prompt()` layers style, safety, composition, and rules at generation time
- **Card Designer (React)** renders text overlay and teacher content
- Card fronts: full-bleed images with React-rendered text
- Card backs: 5x7 printable teacher content (scripts, activities, questions)
- Image prompts in deck.json are **pure scene descriptions**

## Key Files

- [CARD_SPECS.md](CARD_SPECS.md) - Card type specifications
- [VISUAL_SPECS.md](VISUAL_SPECS.md) - Visual specs and composition guidance
- [AGENT_PIPELINE.md](AGENT_PIPELINE.md) - Detailed pipeline with YAML schemas
- [LESSONS_LEARNED.md](LESSONS_LEARNED.md) - Patterns and gotchas

## Updating This Documentation

As you learn from each deck creation:

1. Update individual agent definitions with new learnings
2. Update CARD_SPECS.md if card structure evolves
3. Add notes to LESSONS_LEARNED.md for patterns discovered
4. Add new character designs to VISUAL_SPECS.md

Version this documentation in git alongside the deck files.
