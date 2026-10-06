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
- **Series style plates replaced the per-deck style hero (Oct 2026)** — 4 character-free plates in `style/plates/` (landscape, interior, object, classroom), made from the Purim art, are passed first with every card (modern-world cards get `classroom`). A deck `style_hero.png` is only a fallback when no plates exist. See `style/README.md`.
- **A/B test with `--no-hero`** — Turns the plates off, to check they help.
- **Never ask for a "calm upper N%"** — In the plate run the model drew a literal flat band across the top in 2 of 8 images. Say the top of the scene "continues naturally ... with no hard band or border" instead.
- **Label every reference image** — The prompt names each one ("Image 1 = style plate (match art style only, not content)", "Image 3 = Adam identity sheet — match face, hair, clothing exactly") so the model doesn't copy a plate's content or mix up characters.

### Overnight run lessons (Oct 2026)
- **"Calm top 22%" drew bands** — Asking for a calm upper N% made the model paint a literal flat band across the top in 2 of 8 style plates. Describe the top as sky/ceiling/soft light that "continues naturally ... with no hard band or border". Image QA scores a band as `title_zone: 0`.
- **Chava looked childlike until an explicit adult anchor** — The first identity sheet read as a girl. Fixed by an explicit adult anchor in `character.yaml` ("young adult woman", adult proportions). Every adult character's anchors should say so; Image QA checks "adults look adult" under `character_match`.
- **JPEG saved as PNG** — The image API returns JPEG bytes; we were saving them with a `.png` name. Convert with Pillow on save (or name them `.jpg`) and never trust the extension when checking a file.
- **Nano Banana 2 at 3:4 is 896x1200 at 1K and 1792x2400 at 2K** — not the 768x1024 / 1536x2048 the docs suggested. Log and check the real pixel size after every save; plan DPI math from the real numbers.

### Bereshit v3 run lessons (Oct 2026, first deck on pipeline v3)
- **Check the research cache covers every card before writing 01** — The Bereshit cache had no verse for Chava's creation or Genesis 3, so the spotlight and the "if they ask" scripts had nothing to cite. Add the refs to `RESEARCH_PLANS` in `src/sefaria_client.py` and refetch with `--refresh`.
- **Watch for anachronisms inside the creation order** — A Days 1-3 draft drew a sun disc (the sun is made on Day 4). Image QA scores that `period_accuracy: 1`; say "glowing sky, no sun" in early-creation prompts.
- **Hanging fruit in the title zone reads as "the fruit"** — On Bereshit, a branch with fruit dangling across the top looked like the forbidden fruit. Keep fruit on trees at the sides; nothing hanging into the title area.
- **Adam's trousers can vanish** — One story draft drew Adam with bare legs under the tunic. Image QA checks modesty against the identity sheet (tunic + trousers), not just "a tunic".
- **Draft compositions copy the landscape plate** — With the landscape plate as Image 1, several outdoor drafts reused its winding river and flower foreground. It keeps the deck consistent, but ask for a distinct focal action per card so the scenes don't blur together.
- **Make the gesture the picture** — For the power word, the draft where the characters' thumbs-up was large and close to the camera read instantly at thumbnail size; small hands lost `emotion_at_8pct`.
- **Emoji in the power-word trio** — Emoji aren't licensed for print. Use a plain glyph (✓) or a word; it renders crisply in the back font.
- **Generate concurrently, but in continuity order** — The 1K drafts for cards without `continuity_ref` and the 2K finals can run in parallel shells; only the card with `continuity_ref` must wait for the referenced final.
- **Exports are big** — Letter and 5x7 PDFs with 2K art are ~57 MB each and the exported PNGs ~60 MB; commit the PDFs + raw art and regenerate the PNGs.
- **`generate_images.py` would draw the home card** — It generates any card with an `image_prompt`, including home_1's "no art" note. Always pass `--card`, or skip home cards in the script.

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
- **Visual Director must read the story text (v2 `teacher_script`, v3 `back.say`)** — Story_4 was missing Haman because the Visual Director wrote "Esther approaches the king" without checking the teacher script, which describes the banquet reveal scene where Haman is present. Always cross-reference the Content Writer's narrative when composing scene prompts.
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
- **(v3) Overflow must fail loudly** — v2 backs used `overflow: hidden`, so long text was silently cut off (spotlight_3, connection_1). The v3 export guard measures every back and fails with card/side/px instead.
- **(v3) No `-webkit-text-stroke` on titles** — it draws the font's internal contour lines inside the letters. Use a crisp offset `text-shadow` (blurred shadows print as black boxes in macOS Preview).
- **(v3) Compress PDFs** — 2K art embedded as PNG made 57 MB PDFs; JPEG re-encoding at the same pixel size gives ~6 MB (`scripts/compress_pdf.py`, run by the export).

The bullets below marked v2 describe the old per-type React components (FitText, 500x700 fronts). Those were
removed in v3 (one `CardFront`/`CardBack`, sizes in `cqw`); keep them as history.
- **(v2 PNG export) Front/back viewport mismatch by design** — Fronts render at 500x700 CSS @ 3x device scale (matches design editor). Backs render at 1500x2100 CSS @ 1x (print-calibrated fonts). Don't unify them — they were designed at different resolutions.
- **(v2) All card types use FitText for titles** — Including Story cards. No hardcoded pixel font sizes for titles. Keywords/emotion badges use fixed Tailwind classes (`text-3xl` / `text-sm`).
- **Clear `.next` cache after component changes** — `rm -rf card-designer/.next` before re-exporting, or the old compiled components may be served.
- **Hebrew nikud needs lineHeight ≥ 1.3** (still true in v3) — Nikud marks sit below the baseline. `lineHeight: 1.1` clips them; `1.3` gives enough room. Also use `overflow: visible` on the FitText container, never `hidden`.
- **English subtitle gap mt-2 minimum** — `mt-1` (4px) crowds nikud from below. Use `mt-2` (8px) on all English text that appears directly below Hebrew FitText titles.
- **Anchor card letter-spacing for nikud dots** — Hebrew characters with internal dots (shuruq/vav, dagesh) get covered by adjacent letters when displayed large with heavy stroke/shadow effects. Use `letterSpacing: 0.2em` on AnchorCard to give each letter breathing room. Other card types at smaller sizes don't need this.
- **(v2) FitText accounts for CSS letter-spacing** — Canvas API measurement ignores CSS `letter-spacing` by default. FitText now reads `style.letterSpacing` (em and px units) and adds it to the Canvas measurement. Without this, text with letter-spacing overflows its container.
- **(v2) FitText minSize is a soft floor** — The `minSize` prop is a preference, not a hard clamp. Text can shrink below minSize (absolute floor: 12px) to avoid overflow. Long Hebrew titles with nikud need room to breathe.
- **(v2) Title gradient: h-44 from-black/50** — All card types use the same gradient spec at the top of the card for title readability. Standardized to `h-44 bg-gradient-to-b from-black/50 to-transparent`. Don't vary per card type — consistency makes the deck feel unified.
- **Hide Next.js dev overlay in exports** — Playwright screenshots capture the dev error overlay ("1 issue" badge). The export script injects CSS to hide `nextjs-portal, [data-nextjs-toast], [data-nextjs-dialog-overlay]` before screenshotting.

### Variant Exploration
- **`--variants N` for comparison** — `python generate_images.py --card story_1 --variants 3` generates `story_1_v1.png`, `story_1_v2.png`, `story_1_v3.png`. Compare in Finder, pick the winner.
- **Selection is manual** — Rename winner to `story_1.png`, delete variant files. No CLI command needed — `cp` and `rm` already exist.
- **Works with `--card` for targeted exploration** — Generate variants of one problem card without re-running the whole deck.
- **Git over backups** — Commit before regenerating. The `--backup` flag was removed because git provides better version history.

### Generation Provenance
- **Every generation is logged** — `raw/generations.jsonl` records card_id, timestamp, model, full assembled prompt, character refs used, and success/failure. Append-only.
- **Prompt sidecars for debugging** — `raw/prompts/{card_id}.txt` saves the full prompt in human-readable form. Overwritten each run (JSONL is the durable record).
- **To reproduce an image** — Find the generation in `generations.jsonl`, copy the `full_prompt` value, and re-run with the same character refs.
- **Variants each get a log entry** — Same prompt, different timestamps. Useful for tracking which variant was generated when.

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
- **Calm energy** - no high-energy roleplay prompts
- **Invitation format** - "Can you...?" not commands
- **Generic characters in illustrations** - Unless story characters are doing the tradition

## Purim v3 retrofit (Oct 2026)

- **Re-rendering old art with `--final --from-draft` also updates the setting** — the 2K re-render of the v2
  Purim art picked up the new Achaemenid story world on its own (bull capitals, glazed-brick rosettes, lions)
  while keeping the composition and faces. Big architectural shapes from the old draft (a pointed arch, domes)
  survive, though: to remove them you need a new composition, not a re-render.
- **A re-render can drop a character's expression** — Mordechai lost his smile on the first 2K re-render.
  Score finals separately from drafts (faces drift); naming the expression in the prompt ("warm,
  grandfatherly smile") fixed it on the second try.
- **The letter overflow guard measures lines, not words** — story_3's SAY was 48 words (under budget) and
  still 43 px too tall: inline [cue] chips and a long Hebrew title add lines. Cutting a whole line of SAY
  fixed it; cutting a few words didn't change the number at all.
- **Put the transliteration before the Hebrew in `hebrew.note`** — "boy: אַמִּיץ a-MEETZ" broke across lines
  with the bidi order scrambled ("a-" / "MEETZ"). "for a boy: a-MEETZ אַמִּיץ" renders cleanly.
- **Megillat Esther isn't in the Metsudah Chumash** — `RESEARCH_PLANS` entries can set `en_version: None` to use
  Sefaria's default English (JPS) for non-Torah books.
- **Villain posture: "arms crossed" isn't enough** — Haman came out with crossed arms but a stern, glaring brow.
  Ask for the comic cues too (puffed cheeks, pout, nose in the air) and score the brow in Image QA.
- **Costume crowns hide kippot** — a dad dressed as a king in a crown, or a boy in a firefighter helmet, loses
  the kippah. Ask for "a kippah under a paper crown" in modern Purim scenes.

## Bereshit: a card for each day (Phase 10, Oct 2026)

- **Stick to the text.** The first art brief put deep water on Day 1 (from 1:2, which is *before* the days)
  and it confused children; an old card said "every time Hashem made something, it was tov", but tov
  appears exactly 7 times (1:4, 10, 12, 18, 21, 25, 31): **none on Day 2, twice on Day 3**, and "very
  good" on Day 6. Rule: the Torah Scholar writes a **text map** (in_text / not_in_text per card), and
  content and pictures show only `in_text`. Keep it simple: one clear subject per card.
- **Busy cumulative scenes hide what's new.** The 10-card deck blended Days 1–3 and 4–6 into one picture
  each; Simon couldn't see what each day added. Each day's NEW creation is now the large hero, earlier
  days small and soft behind it, and only Day 7 shows everything together.
- **The composition rule's "ground plane" can contradict the text.** Day 1 came back with a ground strip
  (land on Day 1). Exclusions in the prompt weren't enough for the from-draft final; one `--edit-from`
  pass removed it for $0.10. Score text fidelity on finals, not only drafts.
- **A sequence deck shifts every guide page after the stories.** Don't hand-edit page numbers:
  `src/deck_pattern.py` computes them from `story_cards`, and the validator checks the backs.

