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
| 7 | [Print Producer](definitions/07-print-producer.md) | Print production | Print-ready files |
| 8 | [Web Producer](definitions/08-web-producer.md) | Mobile web | Teacher guide site |

## Workflow

```
[Torah Scholar]
      ↓ research doc (parasha OR holiday)
[Curriculum Designer]
      ↓ deck structure
      ↓ ← CHECKPOINT: Wife reviews direction (visual mockup)
      ↓
[Content Writer] ←→ [Hebrew Expert]
      ↓ complete card text
[Visual Director]
      ↓ character designs + image prompts
      ↓
[Character Identity Generation] (tool)
      ↓ identity reference sheets
      ↓ ← CHECKPOINT: User reviews 2+ identity versions per NEW character
      ↓   (Select preferred version before proceeding)
      ↓
[Card Image Generation] (tool)
      ↓ card images (using identity refs)
[Editor]
      ↓ QA review
      ↓ ← CHECKPOINT: Wife + teachers review cards
      ↓
[Print Producer] ←→ [Web Producer]
      ↓
Physical cards + Teacher guide
```

**Critical:** The Character Identity Checkpoint prevents wasted effort. A poor character identity means ALL cards featuring that character will need regeneration.

## Content Types

The workflow supports two content types:

| Type | Description | Cards | Sessions |
|------|-------------|-------|----------|
| **Parasha** | Weekly Torah portion | 8-11 | 1x 15 min |
| **Holiday** | Jewish holidays | 12-16 | 2x 15 min |

See [FRAMEWORK.md](FRAMEWORK.md) for full details on card types and deck structure.

## Human Checkpoints

1. **After Curriculum Designer:** Wife reviews deck structure via visual mockup
2. **After Editor:** Wife + other teachers review complete deck with images

## Feedback Flow

Currently: Human (you) receives all feedback and routes to appropriate agent.

Future option: Add Feedback Coordinator agent if volume/complexity increases.

## Key Files

- [FRAMEWORK.md](FRAMEWORK.md) - Card types, counts, session design
- [YEAR_CONTEXT.yaml](YEAR_CONTEXT.yaml) - Character/concept/tradition continuity tracking
- [STYLE_GUIDE.md](STYLE_GUIDE.md) - Visual consistency rules

## Updating This Documentation

As you learn from each deck creation:
1. Update individual agent definitions with new learnings
2. Update FRAMEWORK.md if card structure evolves
3. Update YEAR_CONTEXT.yaml after each deck is complete
4. Add notes to STYLE_GUIDE.md for visual consistency

Version this documentation in git alongside the deck files.
