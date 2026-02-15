# Lessons Learned

Patterns and gotchas discovered during deck creation. Check this before starting any new deck.

## Image Generation

### Character References
- **`characters_in_scene` controls ref loading** — Each card has a `characters_in_scene` list in deck.json. Only listed characters' refs are loaded. Empty list `[]` means no character refs (tradition/connection cards). `null`/absent = load all (backwards compatible).
- **Solved: villain in tradition cards** — Previously all refs were passed to every card. Now tradition_1 gets `characters_in_scene: []` so Haman's ref is never loaded.
- **Lean prompts with refs** — When character ref images are loaded, the system tells the model to prioritize them for appearance and use text for pose/action only.
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

### Character Consistency
- **Identity reference + text description together** - Both are needed; reference image alone isn't enough
- **Specific features in every prompt** - "dark pointed goatee with connected mustache" not just "beard"
- **Pose can affect consistency** - Unusual poses (sitting vs standing) may cause appearance drift

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
