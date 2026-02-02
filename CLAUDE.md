# Parasha Pack - Claude Project Documentation

Educational Torah portion card decks for preschool/kindergarten (ages 4-6).

## Project Overview

This project creates illustrated card decks for each weekly Torah portion (parasha). Each deck contains 12 cards that teach the story through characters, actions, discussion questions, and Hebrew vocabulary.

## Directory Structure

```
parasha-pack/
├── CLAUDE.md              # This file - project overview
├── src/                   # Python source code (see src/CLAUDE.md)
├── decks/                 # Deck data and images (see decks/CLAUDE.md)
├── review-site/           # Web review interface (see review-site/CLAUDE.md)
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
- Generate 4 reference sheets (identity, expressions, turnaround, poses)
- Update references/manifest.json

### 3. Generate Card Images

```bash
cd src
python generate_images.py ../decks/yitro/deck.json
```

### 4. Review Cards

Open `review-site/index.html` in a browser to:
- View all cards with images
- Add feedback by category
- Export feedback for revision requests

## Card Types (12 per deck)

| Type | Count | Purpose |
|------|-------|---------|
| Anchor | 1 | Parasha introduction with emotional hook |
| Spotlight | 2 | Character introductions |
| Action | 5 | Story sequence with roleplay prompts |
| Thinker | 2 | Discussion questions with feeling faces |
| Power Word | 2 | Hebrew vocabulary |

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

```bash
GEMINI_API_KEY=your_api_key_here  # Required for image generation
```

## Print Specifications

- Card Size: 5" x 7" (127 x 178 mm)
- Resolution: 300 DPI
- Bleed: 0.125" (3mm)
- Paper: 350gsm cardstock
- Finish: Matte lamination
