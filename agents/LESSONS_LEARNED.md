# Lessons Learned

Patterns and gotchas discovered during deck creation. Check this before starting any new deck.

## Image Generation

### Character References
- **`characters_in_scene` controls ref loading** — Each card has a `characters_in_scene` list in deck.json. Only listed characters' refs are loaded. Empty list `[]` means no character refs (tradition/connection cards). `null`/absent = load all (backwards compatible).
- **Solved: villain in tradition cards** — Previously all refs were passed to every card. Now tradition_1 gets `characters_in_scene: []` so Haman's ref is never loaded.
- **Lean prompts with refs** — When character ref images are loaded, use text for pose/action + 2-3 identity anchors (see "Ref-First Prompting" section below). Don't include full appearance blocks.
- **One identity per character** - Multiple reference sheets generated from text produce inconsistent results
- **Character review checkpoint** - Always generate 2+ identity versions for new characters and have user select before proceeding

### Prompt Text Rendering
- **NO percentages in COMPOSITION sections** - "(12%)" renders as visible text on the card
- **NO question labels** - "Question 1:", "Question 2:" render as text
- **Check for duplicate phrases** - Same phrase appearing twice in prompt may render twice on image
- **Exact text matters** - The AI renders EXACTLY what you specify; vague instructions cause invented text

### Style Consistency
- **Style hero anchors the deck's look** — A single representative image (`references/style_hero.png`) passed as the first reference to all story-world cards. Locks in art style, color palette, and rendering quality.
- **Story-world only** — Modern-world cards (connection, tradition) don't get the hero. They use `MODERN_WORLD_STYLE` text constant.
- **A/B test with `--no-hero`** — Compare with and without hero to verify it helps before relying on it.
- **Hero creation** — Generate 2-3 representative scenes, pick the one with the best style for the deck. Save as `references/style_hero.png` and add to manifest.

### Prompt Detail Level
- **Stage directions, not descriptions** — "He shakes his head NO" produces better results than "refusing to bow." Write prompts like a movie director, not a caption writer.
- **Background characters need actions** — "Other people in the crowd ARE bowing low to the ground" not just "people in background." Scenes with crowd energy look more alive.
- **Visual storytelling devices work** — Thought bubbles, dramatic size contrast (one person standing while others bow), symbolic props (crumpled papers, broken seals) add narrative depth to static images.
- **Emotional punch lines in ALL-CAPS** — "PURE JOY!" and "THE CLIMAX!" at the end of prompts produce more energetic images than flat descriptions.
- **v1 prompts were richer than v2** — When moving to scene-only architecture, prompts got stripped too aggressively. System layers handle style/safety/composition, but scene descriptions still need maximum detail and energy.

### Anchor Card Prompts
- **Material detail, not generic objects** — "delicate gold filigree with tiny purple amethyst gems" not "a golden crown." Rich textures make the symbol feel real and precious.
- **Dramatic lighting sells the moment** — A single beam of light, golden dust motes, soft sparkles. The symbol should feel like a treasure being revealed.
- **Mystery and narrative hook** — A hidden Star of David = hidden identity. The image should make kids ask "what IS that?"
- **Keep upper frame atmospheric** — Warm gradient, soft glow, scattered stars above. Title text overlays there. Push architectural detail to the sides.

### Power Word Card Prompts
- **A heroic MOMENT, not a pose** — "takes a brave step forward, hand pressed to heart" not "standing tall and brave." The character must be DOING the word.
- **Light transition as visual metaphor** — Character walking from shadow into golden light embodies courage/growth better than static radiance.
- **Scale contrast** — Character looks small against a vast environment (tall corridor, open sky) but posture says STRENGTH. Visual tension embodies the concept.
- **Keep upper frame luminous** — The Hebrew word and English meaning overlay at the top. Warm radiance, not detailed architecture.

### Composition Awareness (All Card Types)
- **Top 25-30% of frame is text overlay zone** — Title, Hebrew, emotion labels all go here. Scene prompts must keep this area CALM: gradients, glow, sky, atmospheric light. Never put detailed architecture or busy elements there.
- **Floating elements (thought bubbles, banners, speech balloons) must stay BELOW the title zone** — Position them at chest/belly height or lower. If the prompt says "thought bubble above his head," it WILL overlap the title text overlay. Explicit constraint: "The entire TOP 30% of the frame must be EMPTY."
- **Push detail to sides and below** — Columns, archways, furniture, props go to left/right edges and lower frame. The model can still show rich environments without cluttering the text zone.
- **Scene prompts should COMPLEMENT composition guidance, not fight it** — `build_generation_prompt()` injects composition per card type. If your scene describes "tall columns filling the frame" and the system says "generous headroom," they conflict.

### Tradition Card Prompts (Modern World)
- **Specific people doing specific things** — "dad arranging fruit in a basket" not "family gathered." Name the actions.
- **Props must be identifiable** — hamantaschen, groggers, megillah scroll, masks, gift baskets. The viewer should be able to name 4+ objects in the scene.
- **Children participate, not watch** — Kids shaking groggers, packing baskets, twirling in costumes. Active verbs.
- **Domestic/community detail sells the world** — Kitchen items, wall calendars, children's drawings, pendant lights. These small details make the Modern World feel real.

### Spotlight Card Prompts
- **Signature gesture, not just expression** — "hands clasped peacefully in front" or "scratching his head" gives the model a physical action to anchor.
- **Background tells the world** — Through an archway: palm trees, market stalls, domed buildings. The background should place the character in Shushan (or whatever story world).
- **Personality line in the mood section** — "like a favorite grandfather" or "a princess with a secret" gives the model character direction beyond visual appearance.

### Connection Card Prompts (Modern World)
- **Every child needs a role** — One is TALKING (leaning forward), one LISTENING (chin on hands), one THINKING (looking up). Generic "children sitting in a circle" produces stock illustrations.
- **The classroom must be lived-in** — Children's drawings taped to walls, picture books on shelves, a teddy bear, a plant on the windowsill. These details sell "their classroom" vs. any classroom.
- **Never show a child truly alone** — Connection_2 (intimate) should have a friend nearby or comfort object + warm setting. "Safe to share" not "lonely child."
- **Warm golden afternoon light** — Not bright overhead. The lighting should feel like the coziest part of the school day.
- **The rug/nook is their SPECIAL SPOT** — Describe specific colors and textures. A braided rug with red/blue/yellow rings, or big floor cushions in warm colors. It should feel familiar.

### Pipeline Cross-Reference (CRITICAL)
- **Visual Director must read teacher_script** — Story_4 was missing Haman because the Visual Director wrote "Esther approaches the king" without checking the teacher script, which describes the banquet reveal scene where Haman is present. Always cross-reference the Content Writer's narrative when composing scene prompts.
- **characters_in_scene must match the prompt** — If the prompt mentions King Achashverosh placing a crown, his identity ref must be loaded. Story_1 had the king in the prompt but only `["esther"]` in characters_in_scene, so the model invented a generic king.
- **characters_in_scene includes thought bubble characters** — If a character appears inside a thought bubble, dream sequence, or any secondary visual element, they MUST be in `characters_in_scene`. Story_3 had Mordechai in Haman's thought bubble but only `["haman"]` in the list — the model invented a generic figure for the thought bubble.
- **Every boy in Modern World cards needs a kippah** — MODERN_WORLD_STYLE says "Boys: kippot" but this is a general instruction. Scene prompts must explicitly specify "wearing a kippah" for each boy described, or the model may skip some.
- **Megillah/scroll direction** — AI models render text on scrolls facing the viewer by default. Add "scroll faces TOWARD the reader, text NOT visible to viewer" to prevent backwards text.
- **No hard horizontal lines in anchor cards** — Describing rooms with walls/ceilings creates visible edges in the upper frame. Use "floating in darkness" or "seamless gradient" instead of interior architecture.

### Character Consistency (Ref-First Prompting)
- **Less text = better ref fidelity** — When character refs are loaded, verbose appearance descriptions DILUTE the ref rather than reinforcing it. The model tries to reconcile text + image and lands somewhere generic.
- **Refs loaded → pose + 2-3 identity anchors** — Strip character blocks to action/emotion PLUS 2-3 key visual anchors (most distinctive features). "THREE-CORNERED HAT, dark pointed goatee, dusty purple robes — sitting hunched, arms crossed tight." Pure "pose only" was too aggressive — identity drifted without reinforcement.
- **Identity anchors = most distinctive features** — Hat shape, beard style, clothing colors. Pick the 2-3 things that make this character instantly recognizable. Skip generic traits (skin tone, eye color) that the ref already communicates.
- **No refs → full appearance description needed** — Without a ref image, the text IS the only guide. Be specific: "dark pointed goatee with connected mustache" not just "beard."
- **More characters = simpler each** — With 3 refs in one scene, the model has less attention per character. Keep scene text lean so the refs get priority.
- **Scene complexity competes with character fidelity** — Simpler environments (fewer market stalls, crowd members, architectural details) = better character matching. The model has a fixed attention budget.
- **Spatial directions are unreliable** — LEFT/RIGHT/SEPARATE consume model attention without reliable results. Describe the story relationship ("crowd bowing before Haman, Mordechai the only one standing") and let the model compose.
- **Pose can affect consistency** — Unusual poses (sitting vs standing) may cause appearance drift

### Export Pipeline
- **sync-deck.sh must run before export** — Copies deck.json, raw/ images, and references/ to `card-designer/content/`. Without this, exports use stale images.
- **Front/back viewport mismatch by design** — Fronts render at 500x700 CSS @ 3x device scale (matches design editor). Backs render at 1500x2100 CSS @ 1x (print-calibrated fonts). Don't unify them — they were designed at different resolutions.
- **All card types use FitText for titles** — Including Story cards. No hardcoded pixel font sizes for titles. Keywords/emotion badges use fixed Tailwind classes (`text-3xl` / `text-sm`).
- **Clear `.next` cache after component changes** — `rm -rf card-designer/.next` before re-exporting, or the old compiled components may be served.
- **Hebrew nikud needs lineHeight ≥ 1.3** — Nikud marks sit below the baseline. `lineHeight: 1.1` clips them; `1.3` gives enough room. Also use `overflow: visible` on the FitText container, never `hidden`.
- **English subtitle gap mt-2 minimum** — `mt-1` (4px) crowds nikud from below. Use `mt-2` (8px) on all English text that appears directly below Hebrew FitText titles.
- **Anchor card letter-spacing for nikud dots** — Hebrew characters with internal dots (shuruq/vav, dagesh) get covered by adjacent letters when displayed large with heavy stroke/shadow effects. Use `letterSpacing: 0.4em` on AnchorCard to give each letter breathing room. Other card types at smaller sizes don't need this.

### Generation Provenance
- **Every generation is logged** — `raw/generations.jsonl` records card_id, timestamp, model, full assembled prompt, character refs used, and success/failure. Append-only.
- **Prompt sidecars for debugging** — `raw/prompts/{card_id}.txt` saves the full prompt in human-readable form. Overwritten each run (JSONL is the durable record).
- **To reproduce an image** — Find the generation in `generations.jsonl`, copy the `full_prompt` value, and re-run with the same character refs.

## Content Writing

### Roleplay Prompts
- **Gender-neutral language required** - "give a royal wave" not "wave like a queen"
- **Physical and doable** - Must work in a classroom setting
- **Connected to emotion** - Should reinforce the emotional content of the card

### Connection Cards
- **No question labels** - List questions directly without "Question 1:" prefixes
- **Open-ended questions** - Avoid yes/no questions

## Feedback Tracking

### Session-to-Session
- **Always update feedback.json** during review
- **Check feedback.json BEFORE regeneration** - Don't lose previous session's notes
- **Global feedback for patterns** that affect multiple cards

### What to Capture
- Card-specific issues with exact fix instructions
- Global patterns that should become agent rules
- Investigation notes for unclear issues

## Holiday-Specific

### Villain Characters
- **Misguided, not evil** - jealous, frustrated, careless - NOT scary
- **Include teaching moment** - connect to kids' own feelings
- **Visual: frustrated face, crossed arms** - NOT angry or menacing

### Tradition Cards
- **Calm energy** - NOT "Act it out!" style
- **Invitation format** - "Can you...?" not commands
- **Generic characters in illustrations** - Unless story characters are doing the tradition
