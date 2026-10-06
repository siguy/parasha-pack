# Visual Specifications

**Single source of truth for art style, colors, characters, and print specs.**

For card types and structure, see [CARD_SPECS.md](CARD_SPECS.md).
For agent responsibilities, see [definitions/](definitions/).

---

## Art Style

**Overall:** Vivid, high-contrast cartoon style suitable for ages 4-6.

Think: Colorful children's book illustration meets educational flashcard.

| Element | Specification |
|---------|---------------|
| Characters | Rounded, friendly shapes. Large expressive eyes (20% of face) |
| Forms | Simple shapes, no fine details or complex patterns |
| Lines | Thick, clean black outlines (2-3px equivalent) |
| Contrast | High contrast between foreground and background |
| Emotion | Big, clear facial expressions visible from across classroom |
| Complexity | Maximum 5-7 distinct visual elements per scene |

---

## Color Palette

### Primary Colors (main elements)
| Name | Hex | Use |
|------|-----|-----|
| Red | `#FF4136` | Story card borders, action elements |
| Blue | `#0074D9` | Connection card borders, water |
| Yellow | `#FFDC00` | Highlights, joy |
| Green | `#2ECC40` | Power Word borders, nature |

### Background Colors (soft pastels)
| Name | Hex | Use |
|------|-----|-----|
| Pink | `#FFE5E5` | Warm scenes |
| Light Blue | `#E5F0FF` | Sky, calm scenes |
| Cream | `#FFFBE5` | Text zones, warmth |
| Mint | `#E5FFE5` | Nature scenes |

### Card Type Borders
| Card Type | Color | Hex |
|-----------|-------|-----|
| Anchor | Deck theme | Varies |
| Spotlight | Gold | `#D4A84B` |
| Story | Red | `#FF4136` |
| Connection | Blue | `#0074D9` |
| Power Word | Green | `#2ECC40` |
| Tradition | Gold/Amber | `#D4A84B` |

### Theme Colors (deck borders)
| Theme | Hex | Parshiyot |
|-------|-----|-----------|
| Creation | `#1E3A5F` | Bereishit |
| Desert | `#C9A227` | Bamidbar |
| Water | `#2D8A8A` | Beshalach |
| Family | `#D4A84B` | Vayera, Toldot |
| Covenant | `#5C2D91` | Yitro |
| Redemption | `#A52A2A` | Bo, Shemot |
| Courage | `#8B5CF6` | Purim |

---

## Print Specifications

Defined once in `card-designer/print_formats.json`.

| Spec | Letter (default) | 5x7 (optional vendor) |
|------|------------------|-----------------------|
| Sheet | 8.5" x 11" | 5.25" x 7.25" (5x7 trim + 0.125" bleed) |
| Margin / safe zone | 0.3" white margin, no bleed | bleed in the card color, text 0.25" inside the trim |
| Printer | home/school, duplex, flip on long edge, "actual size" | print shop (cardstock, matte) |
| Card PNG @ 300 DPI | 2375 x 3125 px | 1500 x 2100 px |
| Raw AI art | 1792 x 2400 px (2K, 3:4) | same art, cropped |

Keep key subjects in the central 90% of the width so the art works for both crops.

---

## Safety Rules (CRITICAL)

### Never Depict
- God in any human or physical form
- God's name in Hebrew (יהוה)
- Graphic violence, blood, or injury
- Death shown explicitly
- Scary monsters or frightening creatures
- Weapons causing harm
- Dark, shadowy, threatening environments
- QR codes or transliterations on card images

### Divine Presence (allowed representations)
- Warm golden/white light rays from above
- Glowing soft clouds with radiance
- Environmental effects (gentle wind, soft fire)
- Hands reaching from clouds (no body visible)

### Ten Commandments Tablets
- NEVER write God's name or actual commandment text
- Show exactly 5 letters on each tablet
- Use first 10 Hebrew letters as placeholders:
  - Left: א ב ג ד ה
  - Right: ו ז ח ט י

---

## Character Identity System

### Single Source of Truth: `characters/`

Every character lives in the shared library at **`characters/{key}/`** (see `characters/README.md`):

- `character.yaml`: gender, role (hero/villain/neutral), canonical flag, version, and the
  **locked `visual_anchors`** (age, skin, hair, beard, headwear, clothing colors)
- `identity.png`: the ONE identity image used as the visual anchor for all card generations

The tables that used to live here are now the `visual_anchors` in each `character.yaml`.
**Edit the yaml, not this doc.**

**Why identity-only?** Multiple reference sheets generated independently from text produced inconsistent character interpretations.

### How It Works

1. `assemble_references()` looks up each key in `characters_in_scene` in `characters/` first,
   falling back to the deck's `references/manifest.json` (with a logged warning)
2. Identity images are passed to the API after the style plates (max **4** character refs per image),
   each labeled "{Name} identity sheet — match face, hair, clothing exactly"
3. The locked anchors (`character_library.visual_anchor_text(key)`) are **added to the prompt
   automatically** for every character in `characters_in_scene`. Scene prompts only need pose,
   action and emotion.

### Character Review Checkpoint

Before finalizing a new character identity:

1. Create `characters/{key}/character.yaml` with `identity: null`, `canonical: false`
2. Generate 2+ identity versions (3-angle turnaround + expression row, plain background, **no caption text**):
   `cd src && python generate_references.py --character {key} --versions 2` → `identity_v1.png`, `identity_v2.png`
3. User reviews and selects preferred version
4. `python generate_references.py --character {key} --accept vN` → `identity.png` (others to `alternates/`,
   `character.yaml` updated); then set `canonical: true`

### Library contents

| Key | Role | Identity sheet | Headline anchors |
|-----|------|----------------|------------------|
| moses | hero | yes | blue flowing head covering, short dark beard with gray, blue robe over cream, shepherd's staff |
| yitro | hero | yes | elderly, long white-gray beard, olive-tan head covering, rust vest with geometric trim, staff |
| miriam | hero | yes | light-blue head scarf, long dark wavy hair, blue dress with purple zigzag trim, tambourine |
| esther | hero | yes | royal-blue modest head covering, thin gold tiara, royal purple gown |
| mordechai | hero | yes | striped cream-and-brown headwrap, full gray-brown beard, brown striped robe, cream shawl |
| haman | villain | yes | three-cornered hat, pointed goatee, muted dusty purple/gray, arms crossed (not scary) |
| achashverosh | neutral | yes | blue turban under gold crown with red jewel, bushy beard, red robe with gold trim |
| adam | hero | yes | young adult man, short dark curly hair, short beard, modest oatmeal/clay full-coverage tunic |
| chava | hero | yes | young adult woman, long dark wavy hair loosely tied, modest sage-green full-coverage tunic dress |
| avraham, sarah, pharaoh | — | not yet | drafts (`canonical: false`) |

**Modesty (decision D3, Modern Orthodox):** all characters fully covered; Adam and Chava wear simple
modest tunics, never leaves or anything revealing.

---

## Villain Visual Guidelines

Antagonists are **misguided**, not scary.

### DO
| Element | Approach |
|---------|----------|
| Expression | Frustrated, jealous, confused, pouty |
| Colors | Muted purples, grays, dusty browns |
| Posture | Crossed arms, turned away, hunched shoulders |
| Eyes | Narrowed with frustration, looking away jealously |
| Overall | "Kid who made a bad choice" |

### DON'T
| Element | Avoid |
|---------|-------|
| Expression | Angry, menacing, sneering, evil grin |
| Colors | Black, blood red, dark shadows |
| Posture | Aggressive stance, pointing, looming |
| Eyes | Glaring, red/glowing, malice |
| Imagery | Skulls, shadows, dark clouds, scary backgrounds |

---

## Composition Zones

Card Designer (React) renders text overlay on raw images. The AI-generated image must leave designated zones uncluttered for text readability.

All card types use a standardized title gradient: `h-44 bg-gradient-to-b from-black/50 to-transparent` at the top of the card. This ensures consistent title readability across the deck.

| Card Type | Overlay Zone | Content | Background Treatment |
|-----------|--------------|---------|---------------------|
| Anchor | Top 20-25% | Hebrew parasha/holiday title | Gradient overlay + simple sky |
| Spotlight | Top 30% | Hebrew name + English name + emotion | Gradient overlay |
| Story | Bottom-left corner | Hebrew/English keyword badge | Gradient overlay (top) + scene |
| Connection | Bottom 20% | 4 emojis (no labels) | Gradient overlay (top) |
| Power Word | Top 30% | Hebrew word + English meaning | Gradient overlay |
| Tradition | Top 25% | Hebrew/English title | Gradient overlay |

### Composition Guidance (injected automatically)

`build_generation_prompt()` adds per-card-type composition guidance using cinematography language. The Visual Director does NOT include these in scene prompts — they are layered automatically at generation time.

---

## Image Prompt Structure

Image prompts in deck.json are **pure scene descriptions** — what to draw, not how to draw it. System concerns (style, safety, composition, rules) are layered automatically by `build_generation_prompt()` in `generate_images.py`.

### deck.json prompt (scene-only)

```
Esther in the palace throne room, being crowned by King Achashverosh.
She looks calm but determined. Golden light streams through tall arched windows.
Courtiers watch from the sides. Rich fabrics and royal furnishings.

Warm, hopeful. A new chapter begins.
```

### Two Visual Worlds

Cards exist in one of two visual "worlds":

| World | Card Types | Source | Description |
|-------|-----------|--------|-------------|
| **Story World** | anchor, spotlight, story, power_word | `deck.json "story_world"` | Historical/holiday setting (per-deck). E.g., ancient Persia for Purim, Sinai desert for Yitro. |
| **Modern World** | connection, tradition | `MODERN_WORLD_STYLE` constant | Modern Orthodox Jewish community. Same across all decks. |

The Torah Scholar determines the story world setting as part of research. It is stored in `deck.json` as the `story_world` field.

### What `build_generation_prompt()` adds automatically

All of this text lives in **`style/style_config.yaml`** (one source for the prompt builder, this
agent pipeline and Image QA). Bump its `prompt_version` when you change it on purpose.

0. `=== REFERENCE IMAGES ===` — one numbered label per reference image (see below)
1. `STYLE_ANCHORS_V2` — Children's illustration style, anatomy rules (the Purim look, unchanged)
2. **World style** — `MODERN_WORLD_STYLE` for connection/tradition, `story_world` for all others,
   plus `Deck palette accents: …` when deck.json has a 5-color `palette`
3. `SAFETY_PROMPT` — Content restrictions (no God in human form, villains sulky/comic, etc.)
4. Scene description — passed through unchanged from deck.json
4a. Locked character anchors for each key in `characters_in_scene`
5. `COMPOSITION_GUIDANCE[card_type]` — Per-card-type cinematography, plus: the top of the scene
   continues naturally with no hard band (title area), key subjects in the central 90% of the width,
   at most 5 figures in focus, a simple low-detail ground plane. (No more "darker lower-left".)
6. `COMPOSITION_SUFFIX` — No text, no borders rules

Modern-world rules now name the mix explicitly: Ashkenazi, Sephardi/Mizrahi (olive to brown skin)
and Ethiopian people in every group scene; every boy wears a kippah, girls never do; a megillah is
a single scroll without twin wooden rollers.

---

## Style Plates and Reference Order

**Style plates** (`style/plates/`, see `style/README.md`) are 4 character-free images made from the
Purim art: `landscape`, `interior`, `object`, `classroom`. One is sent first with every card, labeled
"style plate (match art style only, not content)". They replace the per-deck `style_hero.png`
(now only a fallback when no plates exist).

| Card type | Plate |
|-----------|-------|
| connection, tradition | classroom |
| anchor, power_word | object |
| spotlight, story | deck `story_world_setting`: outdoor → landscape, indoor → interior (default landscape) |

A card can override with `style_plate` (a name or a list, max 3).

**Reference images are always sent in this order**, each named in the prompt:

1. Style plate(s)
2. Chosen draft composition (only for `--final --from-draft`)
3. Continuity reference (`continuity_ref`: an earlier card's raw image, for the same place)
4. Character identity sheets (max 4)

### Draft → final

1. `generate_images.py --card story_1 --draft` → two 1K drafts in `raw/drafts/story_1_d1.png`, `_d2.png` ($0.067 each)
2. Simon picks one.
3. `generate_images.py --final --from-draft raw/drafts/story_1_d2.png` → the 2K final at `raw/story_1.png`
   ($0.101), with the draft labeled "re-render this exact composition at full detail in the same style".

Every call goes to `raw/generations.jsonl` with `prompt_version` and the labeled `references`,
and (when `PP_SPEND_LEDGER` is set) to the spend ledger, which refuses calls past `PP_BUDGET_USD`.

### Prompt Gotchas

| Issue | Solution |
|-------|----------|
| Wrong character appears | List only the characters actually in the scene in `characters_in_scene` |
| Scene too busy | Keep to 5-7 visual elements maximum |
| Text appears in image | Check that scene prompt has no `=== STYLE ===` or other system sections |

---

## Reference Files

- Character library: `characters/{key}/character.yaml` + `characters/{key}/identity.png`
- Style plates + style config: `style/plates/*.png`, `style/style_config.yaml`
- Deck manifest (legacy style hero, legacy character fallback): `decks/{deck}/references/manifest.json`
- Raw art: `decks/{deck}/raw/{card_id}.png`; card images: `decks/{deck}/images/{card_id}.png`
