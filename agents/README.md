# Agent System Documentation

Quick navigation for the Parasha Pack agent-based workflow.

---

## Quick Links

| I want to... | Go to... |
|--------------|----------|
| Understand the workflow | [AGENTS.md](AGENTS.md) |
| See card types and structure | [CARD_SPECS.md](CARD_SPECS.md) |
| Find visual/character specs | [VISUAL_SPECS.md](VISUAL_SPECS.md) |
| See what each agent does | [definitions/](definitions/) |
| Track cross-deck continuity | [YEAR_CONTEXT.yaml](YEAR_CONTEXT.yaml) |
| Review lessons learned | [LESSONS_LEARNED.md](LESSONS_LEARNED.md) |

---

## Agent Roster

| # | Agent | Role | Definition |
|---|-------|------|------------|
| 1 | Torah Scholar | Research parasha/holiday content | [01-torah-scholar.md](definitions/01-torah-scholar.md) |
| 2 | Curriculum Designer | Structure deck, choose card types | [02-curriculum-designer.md](definitions/02-curriculum-designer.md) |
| 3 | Content Writer | Write card text, teacher scripts | [03-content-writer.md](definitions/03-content-writer.md) |
| 4 | Hebrew Expert | Hebrew text, nikud, translations | [04-hebrew-expert.md](definitions/04-hebrew-expert.md) |
| 5 | Visual Director | Character design, image prompts | [05-visual-director.md](definitions/05-visual-director.md) |
| 6 | Editor | QA, safety, consistency | [06-editor.md](definitions/06-editor.md) |
| 7 | Print Producer | Print-ready files | [07-print-producer.md](definitions/07-print-producer.md) |
| 8 | Web Producer | Teacher guide site | [08-web-producer.md](definitions/08-web-producer.md) |

---

## Workflow Overview

```
[Torah Scholar] → research doc
      ↓
[Curriculum Designer] → deck structure
      ↓ ← CHECKPOINT: Review direction
[Content Writer] ←→ [Hebrew Expert] → card text
      ↓
[Visual Director] → image prompts
      ↓
[Character Identity Generation] → identity refs
      ↓ ← CHECKPOINT: Review 2+ identity versions
[Card Image Generation] → card images
      ↓
[Editor] → QA review
      ↓ ← CHECKPOINT: Review complete deck
[Print Producer] + [Web Producer] → final outputs
```

---

## Key Concepts

### Card Types
5 core types (Anchor, Spotlight, Story, Connection, Power Word) + 1 holiday-only (Tradition).
See [CARD_SPECS.md](CARD_SPECS.md) for full details.

### Character Consistency
Single identity image per character, passed to all card generations.
See [VISUAL_SPECS.md](VISUAL_SPECS.md#character-identity-system).

### Villain Portrayal
Antagonists are **misguided**, not scary. Frame with emotions kids understand.
See [VISUAL_SPECS.md](VISUAL_SPECS.md#villain-visual-guidelines).

### Checkpoints
Three human review points in the workflow:
1. After deck structure (direction check)
2. After character identity generation (select best version)
3. After complete deck (approve for print)

---

## File Structure

```
agents/
├── README.md           # This file - start here
├── AGENTS.md           # Workflow details
├── CARD_SPECS.md       # Card types (single source of truth)
├── VISUAL_SPECS.md     # Visual specs (single source of truth)
├── FRAMEWORK.md        # Extended framework details
├── STYLE_GUIDE.md      # Brief style reference
├── YEAR_CONTEXT.yaml   # Cross-deck continuity
├── LESSONS_LEARNED.md  # Patterns and gotchas
└── definitions/        # Individual agent specs
    ├── 01-torah-scholar.md
    ├── 02-curriculum-designer.md
    ├── 03-content-writer.md
    ├── 04-hebrew-expert.md
    ├── 05-visual-director.md
    ├── 06-editor.md
    ├── 07-print-producer.md
    └── 08-web-producer.md
```

---

## Common Tasks

| Task | Steps |
|------|-------|
| Create new deck | Start with Torah Scholar → follow workflow |
| Add new character | Visual Director designs → generate 2+ identities → user selects |
| Fix card issue | Check Editor checklist → route to appropriate agent |
| Update continuity | Edit YEAR_CONTEXT.yaml after deck completion |

---

## Maintenance

- **After each deck:** Update YEAR_CONTEXT.yaml with new characters/concepts
- **After discovering patterns:** Add to LESSONS_LEARNED.md
- **If specs change:** Update CARD_SPECS.md or VISUAL_SPECS.md (single source of truth)
