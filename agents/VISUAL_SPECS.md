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

| Spec | Value |
|------|-------|
| Card Size | 5" x 7" (127 x 178 mm) |
| Resolution | 300 DPI |
| Pixel Size | 1500 x 2100 px |
| Bleed | 0.125" (3mm / 38px) |
| Corner Radius | 8-10px |
| Border Width | 8px |
| Paper | 350gsm cardstock |
| Finish | Matte lamination |

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

1. `load_reference_images()` looks up each key in `characters_in_scene` in `characters/` first,
   falling back to the deck's `references/manifest.json` (with a logged warning)
2. Identity images are base64-encoded and passed to the API (max **4** character refs per image)
3. Card prompts include character descriptions to reinforce visual features; the locked anchors are
   available from `character_library.visual_anchor_text(key)`

### Character Review Checkpoint

Before finalizing a new character identity:

1. Create `characters/{key}/character.yaml` with `identity: null`, `canonical: false`
2. Generate 2+ identity versions (3-angle turnaround + expression row, plain background, **no caption text**)
3. User reviews and selects preferred version
4. Save it as `characters/{key}/identity.png`; set `identity: identity.png`, `canonical: true`

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
| adam | hero | not yet | young adult man, short dark curly hair, short beard, modest oatmeal/clay full-coverage tunic |
| chava | hero | not yet | young adult woman, long dark wavy hair loosely tied, modest sage-green full-coverage tunic dress |
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

1. `STYLE_ANCHORS_V2` — Children's illustration style, anatomy rules
2. **World style** — `MODERN_WORLD_STYLE` for connection/tradition, `story_world` for all others
3. `SAFETY_PROMPT` — Content restrictions (no God in human form, etc.)
4. Scene description — passed through unchanged from deck.json
5. `COMPOSITION_GUIDANCE[card_type]` — Per-card-type cinematography
6. `COMPOSITION_SUFFIX` — No text, no borders rules

### Prompt Gotchas

| Issue | Solution |
|-------|----------|
| Wrong character appears | Only include character refs in manifest for characters IN the deck |
| Scene too busy | Keep to 5-7 visual elements maximum |
| Text appears in image | Check that scene prompt has no `=== STYLE ===` or other system sections |

---

## Reference Files

- Character library: `characters/{key}/character.yaml` + `characters/{key}/identity.png`
- Deck manifest (style hero, legacy character fallback): `decks/{deck}/references/manifest.json`
- Card images: `decks/{deck}/images/{card_id}.png`
