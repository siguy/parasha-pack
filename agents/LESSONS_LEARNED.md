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
