# Parasha Pack - Claude Project Documentation

Educational Torah portion card decks for preschool/kindergarten (ages 4-6).

## Project Overview

This project creates illustrated card decks for each weekly Torah portion (parasha). Each deck contains 12 cards that teach the story through characters, actions, discussion questions, and Hebrew vocabulary.

## Directory Structure

```
parasha-pack/
├── CLAUDE.md              # This file - project overview
├── agents/                # Agent system documentation (see agents/AGENTS.md)
│   ├── AGENTS.md          # Agent roster and workflow
│   ├── FRAMEWORK.md       # Card framework v2
│   ├── YEAR_CONTEXT.yaml  # Continuity tracking across decks
│   ├── STYLE_GUIDE.md     # Visual consistency rules
│   └── definitions/       # Individual agent specifications
├── src/                   # Python source code (see src/CLAUDE.md)
├── decks/                 # Deck data and images (see decks/CLAUDE.md)
├── review-site/           # Web review interface (see review-site/CLAUDE.md)
├── review-site-v2/        # V2 review site with front/back support
├── exports/               # Generated PDFs and print files
├── templates/             # Card layout templates
├── requirements.txt       # Python dependencies
└── README.md              # User-facing documentation
```

## Key Workflows

### 1. Create a New Deck

```bash
cd src
python workflows.py deck "Beshalach" --output ../decks/beshalach
```

This will:
- Research the parasha (themes, characters, events)
- Create deck.json with 12 card templates
- Create feedback.json for review tracking
- Create images/ and references/ directories

### 2. Create a New Character

```bash
cd src
python workflows.py character miriam --deck ../decks/beshalach --generate
```

This will:
- Research the character (stories, traits, relationships)
- Design visual appearance (clothing, features, poses)
- Generate identity reference sheet (single source of truth for character appearance)
- Update references/manifest.json

**Character Review Checkpoint:** For new characters, generate 2+ identity versions and have user select the best one before proceeding. This prevents wasted effort regenerating cards due to poor character design.

### 3. Generate Card Images

```bash
cd src
# Generate raw images (scene only, no text) to raw/ directory
python generate_images.py ../decks/purim/deck.json
```

### 3b. Export Final Cards with Card Designer

Card Designer renders text overlay using React components:

```bash
cd card-designer

# Start dev server (if not running)
npm run dev

# Export fronts only (default)
npm run export purim

# Export fronts AND backs
npm run export purim -- --backs

# Export backs only
npm run export purim -- --backs-only
```

Output:
- `decks/purim/images/{card_id}.png` - Final card fronts with text overlay
- `decks/purim/backs/{card_id}_back.png` - Teacher content backs

### 4. Review Cards

Open `review-site/index.html` in a browser to:
- View all cards with images
- Add feedback by category
- Export feedback for revision requests

## Card Types (8-11 per deck)

See [agents/FRAMEWORK.md](agents/FRAMEWORK.md) for full details.

| Type | Count | Purpose |
|------|-------|---------|
| Anchor | 1 | Parasha introduction with emotional hook |
| Spotlight | 0-2 | Character introductions (new or returning) |
| Story | 3-4 | Key narrative moments with roleplay prompts |
| Connection | 2-3 | "Have you ever..." discussion questions |
| Power Word | 0-1 | Hebrew vocabulary |

**Note:** Deck composition is flexible based on parasha type (narrative, law-based, building, ritual).

## Agent-Based Workflow

Deck creation uses a multi-agent workflow. See [agents/AGENTS.md](agents/AGENTS.md) for:
- Agent roster and responsibilities
- Workflow diagram
- Human checkpoint process
- Continuity tracking

## Safety Rules for Image Generation

- NEVER depict God in human form (use light rays, clouds, hands from above)
- No graphic violence or death
- No scary monsters
- All characters dressed modestly
- Age-appropriate for 4-6 year olds

## Adding New Research Data

To add a new character or parasha to the research database:

1. Open `src/workflows.py`
2. Add entry to `CHARACTER_DATABASE` or `PARASHA_DATABASE`
3. Include: biblical refs, key stories, traits, emotional moments

## Common Tasks

| Task | Command |
|------|---------|
| Research a character | `python workflows.py research character moses` |
| Research a parasha | `python workflows.py research parasha yitro` |
| List available research | `python workflows.py list characters` |
| Generate deck template | `python workflows.py deck Yitro` |
| Create character refs | `python workflows.py character yitro -d ../decks/yitro -g` |
| Generate all images | `python generate_images.py ../decks/yitro/deck.json` |
| Generate single image | `python generate_images.py ../decks/yitro/deck.json --card spotlight_1` |

## Environment Variables

The `GEMINI_API_KEY` is stored in `.env` in the project root. Load it before running image generation:

```bash
source .env && export GEMINI_API_KEY
```

Or set directly:
```bash
export GEMINI_API_KEY=your_api_key_here
```

## Image Generation Model

**ALWAYS use nano-banana-pro** (the default). Never use imagen or other models.

```bash
# Correct (default)
python generate_images.py ../decks/purim/deck.json

# Also correct (explicit)
python generate_images.py ../decks/purim/deck.json --model nano-banana

# WRONG - never use these
# python generate_images.py --model imagen  # DON'T USE
# python generate_images.py --model flash   # DON'T USE
```

Character reference images are automatically included from `references/manifest.json` when generating cards. Use `--no-refs` to disable if needed.

## Character Consistency System

Character consistency is achieved through **identity references**:

1. **Single Source of Truth:** Each character has ONE identity image (`{character}_identity.png`)
2. **Automatic Reference Passing:** When generating cards, the identity image is base64-encoded and passed to the API alongside the text prompt
3. **Prompt Reinforcement:** Card prompts should still include character descriptions to reinforce visual features

**Why identity-only?** Previously we generated 4 reference types (identity, expressions, turnaround, poses). Each was generated independently from text, producing inconsistent interpretations of the same character. Now we generate ONE identity and use it as the reference for ALL card generations.

**Character Review Workflow:**
1. Generate 2+ identity versions for new characters
2. User reviews and selects preferred version
3. Rename selected version to canonical name (e.g., `haman_identity.png`)
4. Generate all cards using that identity as reference

## Version Control

**Use git as the single source of truth.** Commit before major changes (e.g., before regenerating all images).

```bash
# Before regenerating images
git add -A && git commit -m "Pre-regeneration checkpoint: [deck name]"

# After successful generation
git add -A && git commit -m "Regenerate [deck name] images with [change description]"
```

Avoid manual `_v1`, `_v2` file copies. If you need to compare versions, use `git diff` or check out previous commits.

## Print Specifications

- Card Size: 5" x 7" (127 x 178 mm)
- Resolution: 300 DPI
- Bleed: 0.125" (3mm)
- Paper: 350gsm cardstock
- Finish: Matte lamination

## Card Format Versions

### v1 (Legacy)
- All content rendered in the generated image
- Text included in image prompts via `=== EXACT TEXT TO RENDER ===`
- Single-sided cards

### v2 (Current - Card Designer)
- **AI generates scene-only images** to `raw/` directory (no text in image)
- **Card Designer (React)** renders text overlays and teacher content
- **Card Front**: Full-bleed image with React-rendered text overlay
- **Card Back**: 5x7 printable teacher content (scripts, activities, questions)
- Image prompts use `=== COMPOSITION ZONES ===` for layout guidance
- Supports double-sided printing

**Directory Structure:**
```
decks/purim/
├── deck.json
├── raw/               # AI-generated images (no text)
│   ├── story_1.png
│   └── ...
├── images/            # Final exports with text overlay
│   ├── story_1.png
│   └── ...
├── backs/             # Teacher content backs
│   ├── story_1_back.png
│   └── ...
└── references/
```

**Workflow:**
```bash
# 1. Generate raw images
cd src && python generate_images.py ../decks/purim/deck.json

# 2. Export with Card Designer
cd card-designer && npm run export purim -- --backs
```

See [agents/CARD_SPECS.md](agents/CARD_SPECS.md) for full v2 schema.
