# Series style (style plates + style_config.yaml)

This folder holds everything that makes every Parasha Pack deck look like **one series**.
Think of it like a school uniform: each deck has its own story, but they all wear the
same clothes.

```
style/
├── style_config.yaml      # the single source for style text, safety rules, composition, limits
├── plates/
│   ├── landscape.png      # outdoor story world (garden, hills, river, open sky)
│   ├── interior.png       # indoor story world (stone arch, rugs, clay lamps)
│   ├── object.png         # object close-up (Shabbat candles + challah)
│   ├── classroom.png      # modern gan classroom (connection + tradition cards)
│   ├── contact_sheet.png  # all 8 plates side by side (chosen on top, alternates below)
│   └── alternates/        # runner-up versions, kept so Simon can swap one in
└── README.md
```

**Hard rule (Simon, 2026-10-05): keep the current Purim art style.** The plates were
made *from* the Purim deck art so they reproduce it. `style_anchors` in
`style_config.yaml` is the old `STYLE_ANCHORS_V2` text, word for word.

## Style plates

Four images with **no characters** in the existing Purim style. One (sometimes two) is
passed as the first reference image with every card generation, labeled
"style plate (match art style only, not content)". They replace the old per-deck
`references/style_hero.png`. A deck's `style_hero` is now only used as a fallback when
`style/plates/` has no plates at all.

How they were made (plan step 5.3, 8 calls at 2K, $0.81):
- Model `gemini-3.1-flash-image`, 2K, aspect 3:4.
- Style references: Purim `raw/story_1.png` (warm palace interior), `raw/story_2.png`
  (outdoor, blue sky), `raw/connection_1.png` (modern gan), downscaled to 1024px.
- Prompt template ({scene} changes per plate):
  > STYLE REFERENCE IMAGES 1-3 show the exact art style to match: same line weight (thick
  > clean dark outlines), same flat color fills with soft gradients, same warm saturated
  > palette, same rendering and lighting. Do NOT copy their subjects or characters.
  > Create: {scene}. NO people, NO animals with faces, NO characters. NO text, letters, or
  > symbols anywhere. Calm, simple upper 22% of the frame (sky/ceiling/soft light) where a
  > title will be placed. Main subject within the central 90% of the width. Children's
  > educational card illustration for ages 4-6.

| Plate | Chosen because | Alternate (in `alternates/`) |
|-------|----------------|------------------------------|
| landscape | boldest outlines and most saturated colors, closest to Purim; open sky on top | `landscape_v2.png`: thinner lines, more pastel, fussy flowers |
| interior | clean arch + skylight as a calm top; clay lamps, rugs, no glyphs | `interior_v2.png`: **do not use**, a hard flat band across the top |
| object | stone wall, warm candle glow, no artifacts | `object_v2.png`: **do not use**, same hard band across the top |
| classroom | blank posters/labels, ceiling as a calm top, no text | `classroom_v2.png`: menorah posters (symbols), no ceiling, copies Purim's rug |

Known weakness: `interior.png` is paler and less golden than the Purim palace.

**Lesson:** asking for a "calm upper 22%" made the model draw a literal band in 2 of 8
images. The card prompts now say the top of the scene "continues naturally ... with no
hard band or border" instead.

## Which plate a card gets

Set in `style_config.yaml` → `plate_mapping`:

| Card type | Plate |
|-----------|-------|
| connection, tradition | classroom |
| anchor, power_word | object |
| spotlight, story | the deck's `story_world_setting`: `"outdoor"` → landscape, `"indoor"` → interior (default landscape) |

A card can override this with `style_plate`.

## Reference image order (always the same)

`generate_images.py` → `assemble_references()` sends images in this fixed order, and the
prompt gets a `=== REFERENCE IMAGES ===` block naming each one:

1. **Style plates** (1–2, max 3): "match art style only, not content"
2. **Draft composition** (only with `--final --from-draft`): "re-render this exact composition"
3. **Continuity reference** (optional `continuity_ref`): an earlier card's raw image
4. **Character identity sheets** from `characters/` (max 4): "match face, hair, clothing exactly"

Large images (over 1536px on the long side) are shrunk to 1536px JPEG before sending, so
six 2K references stay well under the API's 20 MB request limit.

## deck.json fields read by the image pipeline

These are optional. The deck validator/schema must accept them.

| Field | Where | Type | Meaning |
|-------|-------|------|---------|
| `story_world_setting` | deck | `"outdoor"` or `"indoor"` | Picks the plate for spotlight + story cards. Default outdoor (landscape). |
| `palette` | deck | list of 5 hex strings, e.g. `["#2E7D32", ...]` | Adds "Deck palette accents: …" to the WORLD layer of every prompt. (Plan: also drives the hub `web_theme`.) |
| `style_plate` | card | plate name (`"landscape"`) or list of up to 3 names | Overrides the plate mapping for one card. |
| `continuity_ref` | card | a card_id (`"story_1"` → `raw/story_1.png`) or a path relative to the deck folder | Passes an earlier image so the same place carries over (Bereshit: ① → ② the same landscape filling up). |
| `characters_in_scene` | card | list of library keys | Unchanged. Also drives the locked anchor text now. |

## Draft → final

```bash
cd src
# Cheap drafts: 1K, 2 variants -> decks/{id}/raw/drafts/{card_id}_d1.png, _d2.png
python generate_images.py ../decks/bereshit/deck.json --card story_1 --draft
# Simon picks one; final at 2K with the draft passed as a composition reference
python generate_images.py ../decks/bereshit/deck.json --final --from-draft ../decks/bereshit/raw/drafts/story_1_d2.png
```

`--final` works out the card from the draft file name (`story_1_d2.png` → `story_1`).
With no flag, generation works as before: one 2K image to `raw/{card_id}.png`.

## Spend ledger

When `PP_SPEND_LEDGER` is set to a file path, every real image API call appends one JSON
line `{"ts","branch","purpose","size","usd"}`. When `PP_BUDGET_USD` is also set, a call is
**refused** (no network request) once the ledger total is at or above the budget. Prices
per size live in `src/config.py` (`IMAGE_PRICE_USD`).
