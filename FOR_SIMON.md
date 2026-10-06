# For Simon: How Parasha Pack Works (and What We Learned Building It)

This isn't the manual. The manual lives in `CLAUDE.md` and `README.md`. This is the version I'd tell
you over coffee: what we built, why it's shaped the way it is, what broke, and what's worth carrying
into your next project. Whenever a technical word comes up, I define it the first time.

---

## 1. What this project does, and why

Parasha Pack turns a weekly Torah portion (or a holiday) into a **classroom kit for 4-to-6-year-olds**:

- **10 cards** (12 for a holiday). Each has a picture side for the children and a teacher side with a
  short script: what to **SAY**, what to **ASK**, one **Hebrew word** with a hand gesture.
- **A home card** that goes home on Friday with one Shabbat-table question.
- **A 16-page teacher guide booklet**: background, "Our Sages teach…", scripted answers to hard questions.
- **Printable extras**: bingo, I-spy, match-it, Listen & Do, coloring pages, a story-order game.

The *why* is something you know better than I do. A preschool teacher has about 15 minutes, a room
full of short attention spans, and often no time to prepare. The teacher should be able to pick up the
card, read the bold words aloud, do the action in brackets, and have taught a good lesson. Every design
choice in this project serves that teacher.

---

## 2. How it's built: the school analogy

The easiest way to picture the whole system is as **a small school putting together a lesson unit**.

### `deck.json` is the lesson plan

Every deck has one file, `decks/{id}/deck.json`, that holds every word on every card: titles, scripts,
questions, Hebrew, and the description of each picture. **JSON** (JavaScript Object Notation) is just a
tidy text format for structured data, like a very strict form with labeled boxes.

There's one rule: **deck.json is the single source of truth.** That means it is the *one* place the
truth lives. Everything else (the printed cards, the website, the booklet) is *made from* it and
never edited by hand. If the lesson plan says "Story 2 is about the sun and fish," every copy agrees,
because every copy was printed from the same master.

### The 8 agents are a teaching team

An **agent** here is just a role I (Claude) play, with a written job description in
`agents/definitions/`. Think of it as a curriculum team where each person has one job and hands their
work, in writing, to the next:

| Role | Like a… | Job |
|---|---|---|
| 00 Series Planner | department head | Picks the value (middah) and power word for the year |
| 01 Torah Scholar | the rabbi on staff | Finds the verses; every claim gets a citation |
| 02 Curriculum Designer | lead teacher | Picks the 10 moments and plans the 5-day week |
| 02b Sensitivity Reviewer ★ | school counselor | "How do we handle the snake? Haman's ending?" |
| 03 Content Writer | the writer | Writes every word, in English **and** Hebrew |
| 05 Visual Director | art director | Describes each picture (the scene only) |
| 05b Image QA ★ | the picky art teacher | Scores each draft picture against a checklist |
| 06 Editor | principal | Scores the whole deck before it goes out |

Each one writes **one YAML file** into `decks/{id}/pipeline/`. **YAML** is another plain-text data
format, friendlier for humans to read than JSON. The ★ roles are **checkpoints** where you get the
final say.

Then a script called `assemble_deck.py` acts as **the stapler**: it checks each person's pages and
staples them into deck.json. Nobody copies and pastes between files by hand. That's where mistakes
used to creep in.

### The validator is a proofreading colleague

`src/validate_deck.py` reads a deck and lists every problem it finds, the way a careful colleague
would: "this script is 58 words, the budget is 50," "this card names Haman but doesn't list him," "this
guide page number is wrong." My favorite thing it catches is **Hebrew grammatical gender**: it knows
that Esther is female, so a masculine adjective on her card is an error. It caught **גִּבּוֹר**
("hero," masculine) on Esther's card in the old Purim deck. It should have been **גִּבּוֹרָה**, and it had
slipped past every read-through by eye.

### Style plates are the art teacher's sample board

The pictures are drawn by an AI image model. Left alone, every picture comes out in a slightly
different style. So we made four **style plates** (`style/plates/`): a landscape, an interior, an
object close-up and a classroom, all painted *from* the existing Purim art and with no people in them.
One is sent along with every picture request, labeled "match the art style only, not the content."
It's the sample board pinned up at the front of the art room: "this is what our pictures look like."

### The character library is the cast list with headshots

`characters/{name}/` holds one **identity sheet** per character (the same face from three angles plus
four expressions) and a `character.yaml` with **locked anchors**: "striped cream-and-brown headwrap,
full gray-brown beard." Every picture of Mordechai is drawn while looking at the same headshot. Before
this, each deck kept its own copy of Moses, and the Moseses didn't match.

### The PDFs are a double-sided worksheet

The default card is a full **8.5×11 letter page**, because every school has a printer that takes letter
paper. The PDF goes front 1, back 1, front 2, back 2… so when you print **double-sided, flip on long
edge**, each sheet is one card: picture on one side, script on the other. Same idea as photocopying a
worksheet with the answer key on the back. There's also a 5×7 version for a print shop, with
**bleed** (the picture runs 1/8" past the cut line, so a slightly crooked cut doesn't leave a white edge).

---

## 3. How the pieces connect: the data flow

Follow one deck from idea to classroom:

```
series.yaml           the year plan: which deck, which value, which power word
    ↓
pipeline/*.yaml       the 8 agents' written work, one file each
    ↓ assemble_deck.py   (the stapler; checks each file, then runs the validator)
deck.json             the lesson plan
    ↓ generate_images.py   (style plate + character sheets + scene → AI picture)
raw/*.png             pictures with NO text in them
    ↓ sync-deck.sh → Card Designer (a small website that lays out cards)
images/, backs/, print/*.pdf
    ↓ scripts/sync_to_hub.py
simonbrief-hub        your website, where teachers can view and download
```

One detail matters a lot: **the AI never draws text.** Image models are bad at spelling, and terrible
at Hebrew with nikud. So the AI paints only the scene, and the Card Designer adds every word on top
with real fonts. It's the difference between asking a painter to letter a sign freehand and handing
them a stencil.

---

## 4. The technologies, and why we chose them

- **Python** for all the "back office" work: assembling, validating, calling the image model, building
  the extras. It's readable and it's what you're learning.
- **Next.js / React** for the Card Designer. **React** builds a page out of reusable pieces
  ("components"). We have one `CardFront` and one `CardBack` for all seven card types, configured by
  type. **Next.js** is a framework that runs React as a website. We use a website as the layout engine
  because browsers are excellent at text: Hebrew right-to-left, nikud, wrapping.
- **Playwright** is a robot that drives a real (invisible) Chrome browser. It opens each card page and
  "prints to PDF" or takes a screenshot. Same robot prints the extras and the booklet.
- **Gemini "Nano Banana 2"** (`gemini-3.1-flash-image`) draws the pictures. We considered **Nano
  Banana Pro**: it's better at some things but slower and pricier, and the old Pro preview model we
  depended on was **shut down** by Google. Switching models is now one line in `.env`.
- **pypdf** reads PDFs back, so the booklet builder can *prove* that Story 2 really landed on page 7.
- **BroadcastChannel** (used in the hub's present mode) is a browser feature that lets two windows of
  the same site talk to each other: the projector window and your laptop's presenter window stay in
  step with no server in between.

**Things we considered and rejected:**

- **4K vs 2K pictures.** 4K costs 50% more per picture ($0.151 vs $0.101) and files are huge. 2K
  (1792×2400) is about 230 DPI at letter card size, which is fine for a classroom card viewed from
  across the room. 4K stays available as an upgrade if a test print looks soft.
- **Edge detection vs AI line art for coloring pages.** The obvious shortcut for a coloring page is a
  filter that traces edges in the color picture. But that traces *everything*: every shadow, every
  texture, so you get a scribbly mess. Instead, one AI "edit" call redraws the picture as thick clean
  outlines, then Pillow (a Python image library) cleans it to pure black and white.
- **One AI I-spy picture vs code-composed.** AI can't count. Ask for "exactly 4 fish" and you get 3, or
  6, and now your answer key is wrong. So the background is AI, and the fish, stars and birds are
  stuck on by code like stickers. The code placed every sticker, so it knows the exact count.
- **QR codes vs a printed booklet.** The teacher material lives in a printed letter booklet, not behind
  a QR code. A teacher in the middle of circle time shouldn't need a phone. The card back just says
  "Guide p.7."
- **5×7 vs letter as the default.** 5×7 looks lovely but needs a print shop and cutting. Letter prints
  anywhere. We made letter the default and **kept** 5×7 as an option, because when you pick a new
  default, the old ability should stay available unless you say to delete it.

---

## 5. Bugs we hit, and how we fixed them

This is the most useful section. Real engineering is mostly this.

**1. The model that wasn't there.** Image generation suddenly stopped working. The code had a
hard-coded name, `nano-banana-pro-preview`, pointing to a preview model Google had shut down. *Fix:* the
model name moved into one setting (`GEMINI_IMAGE_MODEL`), defaulting to Nano Banana 2. *Lesson:* never
bury a name that might change deep inside code.

**2. "1K returned 896×1200, so the size setting must be broken."** We asked for 1K and got 896×1200.
Our table said 1K should be 768×1024, so we assumed the API was ignoring us. We spent one 10-cent test
call at 2K and got 1792×2400, exactly Google's own published table. **Our table was wrong, not the
API.** *Lesson:* when the data disagrees with your expectation, check the expectation too.

**3. JPEG wearing a PNG name tag.** The API sends back JPEG data. We were saving it with a `.png`
name. That's like putting a "decaf" label on regular coffee: everything looks fine until something
relies on the label. *Fix:* re-encode to a real PNG on save.

**4. Backs silently cut off.** The old card backs used a CSS setting (`overflow: hidden`) that quietly
hides any text that doesn't fit. Long scripts just lost their last line, and nobody noticed. *Fix:* the
**export guard**. Before exporting, a robot measures every back. If text overflows, or sits too close
to the paper edge, the export **stops** and names the card and how many pixels it's over. Later it
caught Purim's story 3 at 43 pixels over, even though the script was under the word budget: inline cues
add lines. *Lesson:* a loud failure is a gift; a silent one is a trap.

**5. Lines inside the letters.** Titles used `-webkit-text-stroke` to get an outline. It also drew the
font's internal construction lines *inside* the letters. *Fix:* a crisp offset shadow instead (blurry
shadows printed as black boxes in macOS Preview, so they were out too).

**6. "Calm upper 22%" drew literal stripes.** We told the model to keep the top 22% of the picture calm,
for the title. In 2 of 8 style plates, it painted a hard flat band across the top. AI takes you very
literally. *Fix:* describe it the way an artist would: the sky "continues naturally… with no hard band."

**7. Chava looked like a child.** Both first identity sheets drew Chava as a young girl next to an
adult Adam. *Fix:* an explicit anchor: "grown-up young woman, about 25, adult proportions matching
Adam." Now every adult's anchors say "adult," and Image QA checks it.

**8. Version numbers colliding.** After you *accept* identity version 2, it gets renamed and the others
move to `alternates/`. If the next run counted only what was left in the folder, it would make a new
"v1" and collide with the old v1 sitting in `alternates/`. *Fix:* count the alternates too, so version
numbers never repeat.

**9. 57 MB PDFs.** With 2K art stored losslessly, each deck PDF was 57 MB, too big to email or put on a
website. *Fix:* `scripts/compress_pdf.py` re-saves the pictures inside the PDF as JPEG at the **same
pixel size**, so print sharpness is unchanged: **57 MB → 6 MB**. The export runs it automatically.

**10. Turbopack refused to start.** Turbopack (the Next.js build tool) wouldn't accept a shortcut link
("symlink") to `node_modules` (the folder of downloaded JavaScript libraries) that pointed outside the
project. *Fix:* copy the folder instead (`cp -cR`, which on a Mac makes a fast copy that shares disk space).

**11. Bingo ended on call 2.** With a free middle square, any row through the middle needs only two
pictures. With 10 boards in the room, someone shouts BINGO almost immediately. We **simulated 2,000
games** in code to check. *Fix:* the win rule became "cover the 4 corners," and the first win now
lands around call 7, usually with one winner.

**12. Hebrew gender errors.** Already mentioned: the validator caught גִּבּוֹר on Esther's card. The
Purim rebuild uses אַמִּיצָה (brave, feminine) for Esther and gives the class plural forms.

---

## 6. Potential pitfalls (for future you)

- **Editing the copy instead of the master.** Never edit `card-designer/content/{id}/deck.json` or a
  PNG in `images/`. They're overwritten on the next sync/export. Edit the pipeline YAML, then assemble.
- **Forgetting the spend ledger.** Set `PP_SPEND_LEDGER` and `PP_BUDGET_USD` before generating images.
  Without them, nothing stops a loop from spending real money.
- **Generating the home card.** `generate_images.py` doesn't skip the home card yet. Always use `--card`.
- **Old tools still around.** `generate_deck.py` and `python -m workflows deck` still make the old v2
  format, which the Card Designer can't read. Use the pipeline.
- **The review site** still shows v2 fields, so v3 decks look blank there. Use the Card Designer.
- **Regenerating art changes measurements.** The Listen & Do answer key boxes were measured by hand on
  one picture. A new picture means re-measuring.
- **Nothing has been test-printed on a real printer yet.** Duplex alignment is the first thing to check.

---

## 7. What good engineers think about

- **Stacked pull requests.** A **pull request (PR)** is a proposed change waiting for review. We built
  eleven of them, each on top of the last, like floors of a building: the image fix, then the plan,
  then card backs, characters, styling, validator, agents, Bereshit, extras, Purim, hub. Each one is
  small enough to review in one sitting. Merge them bottom-up.
- **Version control as a time machine.** Git remembers every saved version. That's why we commit
  before regenerating art and keep runners-up in `alternates/` instead of `final_v2_REAL.png`.
- **Tests before features.** There are about 200 automated tests (`python3 -m pytest tests -q`). They
  check things like "any two bingo boards share at most 6 pictures" and "Story 2 is really on page 7."
  They're the fire drill you run before the fire.
- **Budgets and ledgers.** Every image call writes a receipt line. The overnight run had a hard $15 cap
  and finished around $10 for two complete decks plus extras.
- **"Known issues" honesty.** Every PR has a **Known issues / not working** section. Hiding problems
  doesn't make them go away; it just moves the discovery to a worse moment (like in front of a class).
- **Single source of truth.** Said it before; it's that important.

---

## 8. Best practices demonstrated (name them, reuse them)

1. **Single source of truth**: deck.json, `characters/`, `style_config.yaml`, `print_formats.json`.
2. **Fail loudly**: validator errors and the export guard stop the line instead of shipping a bad card.
3. **Separation of concerns**: AI draws scenes; code draws text; each agent owns specific fields.
4. **Schemas as contracts**: a **schema** is a written rule for a file's shape. Each pipeline file has one.
5. **Cheap drafts, expensive finals**: 1K drafts at 6.7¢ to choose, 2K finals at 10.1¢ to keep.
6. **Determinism**: bingo uses a fixed random "seed," so the same deck always gets the same boards.
7. **Let code do what AI can't**: counting (I-spy), page numbers (booklet), measuring (overflow).
8. **Human checkpoints at the judgment calls**: sensitivity, picture picks, the test print.
9. **Log decisions with reasons**: `docs/overnight/decisions.md` lists every choice made for you, and why.

---

## 9. The one or two most important concepts

If you remember only two things, make them these.

**★ Single source of truth.** Almost every bug in the old version came from the same fact living in
two places and drifting apart: four different descriptions of Moses, scripts typed into both the card
and the website, page numbers guessed in two files. The fix every time was the same: pick one master,
make everything else *generated from* it. When you start any project, ask: "Where does each fact live,
and is it only one place?"

**★ Make the computer check the boring things, loudly.** Word counts, Hebrew gender, page numbers,
text that doesn't fit, money spent. Humans are bad at these and good at judgment. The validator, the
export guard and the spend ledger free your attention for what matters: is this a good lesson for a
four-year-old?

---

## 10. What to build next

**A "teacher feedback loop" app.** The pilot kit in `docs/pilot/` already has a daily tick grid and an
8-question feedback form, but on paper. Build a tiny web form (or a Google Form read by a Python
script) where pilot teachers log "used it / skipped it / kids loved it" per card. Then a script reads
the results and writes a short report: which cards get skipped, which scripts run long, which Hebrew
words stick.

It would reinforce everything here: a single source of truth (one results file), validation (reject a
form with no deck id), tests, and turning messy human input into a clean summary. And it closes the
loop: right now the project knows a lot about making cards and nothing yet about how they land in a
real classroom. That's the next thing worth learning.
