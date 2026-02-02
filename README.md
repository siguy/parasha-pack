# Parasha Pack

Educational weekly Torah portion card decks for preschool/kindergarten classrooms (ages 4-6).

## Project Structure

```
parasha-pack/
├── decks/                    # Card deck data
│   └── yitro/               # Example: Parshat Yitro deck
│       ├── deck.json        # All card metadata & content
│       ├── feedback.json    # Review comments
│       └── images/          # Generated card images
├── review-site/             # Web-based review interface
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── src/                     # Python source code
│   ├── __init__.py
│   ├── sefaria_client.py    # Sefaria API integration
│   ├── schema.py            # Data structures & schemas
│   ├── image_prompts.py     # Gemini prompt templates
│   ├── card_generator.py    # Print layout generation
│   └── generate_deck.py     # Deck template generator
├── exports/                 # Exported PDFs and feedback
├── templates/               # Card layout templates
└── requirements.txt
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate a New Deck Template

```bash
cd src
python generate_deck.py
```

This fetches the current parasha from Sefaria API and creates a deck template.

Or specify a parasha:
```bash
python generate_deck.py --parasha "Yitro"
```

### 3. Review Cards

Open `review-site/index.html` in a web browser to use the review interface.

### 4. Generate Print Layouts

```bash
python card_generator.py ../decks/yitro/deck.json ../exports/yitro_layouts
```

## Card Types

| Type | Purpose | Per Deck |
|------|---------|----------|
| **Anchor** | Weekly "big idea" | 1 |
| **Spotlight** | Character intro | 2-4 |
| **Action** | Plot moments with roleplay | 3-6 |
| **Thinker** | Discussion questions | 2-3 |
| **Power Word** | Hebrew vocabulary | 2 |

## Print Specifications

- **Card Size:** 5" x 7" (127 x 178 mm)
- **Orientation:** Portrait
- **Bleed:** 0.125" (3mm) on all sides
- **Resolution:** 300 DPI
- **Paper:** 350gsm cardstock
- **Finish:** Matte lamination

## Review Workflow

1. Load a deck in the review site
2. Click cards to view details
3. Add feedback (Visual, Text, Hebrew, Educational, Layout)
4. Export feedback as JSON for Claude revisions
5. Iterate until approved

## Image Generation

Use the prompts in `image_prompts.py` with Google Gemini:

```python
from src.image_prompts import build_spotlight_prompt

prompt = build_spotlight_prompt(
    character_key="moshe",
    emotion="happy",
    scene_context="reuniting with family"
)
# Use this prompt with Gemini to generate the image
```

## API Reference

### Sefaria Client

```python
from src.sefaria_client import fetch_current_parasha

parasha = fetch_current_parasha()
print(parasha.title_en)  # e.g., "Yitro"
print(parasha.border_color)  # e.g., "#5c2d91"
```

### Deck Schema

```python
from src.schema import Deck, ActionCard

deck = Deck(
    parasha_en="Yitro",
    parasha_he="יִתְרוֹ",
    ref="Exodus 18:1-20:23",
    border_color="#5c2d91",
    theme="covenant"
)
```

## Thematic Border Colors

| Theme | Color | Parshiyot |
|-------|-------|-----------|
| Creation | Deep blue (#1e3a5f) | Bereshit, Noach |
| Desert | Sandy gold (#c9a227) | Bamidbar series |
| Water | Teal (#2d8a8a) | Noach, Beshalach |
| Family | Warm amber (#d4a84b) | Patriarchs/Matriarchs |
| Covenant | Royal purple (#5c2d91) | Yitro, Mishpatim |
| Redemption | Crimson (#a52a2a) | Shemot, Va'era |

## Safety Rules

- NEVER depict God in human form (use light rays, clouds, hands from above)
- No graphic violence or death
- No scary monsters
- All characters dressed modestly
- Age-appropriate for 4-6 year olds

## License

Educational use only.
