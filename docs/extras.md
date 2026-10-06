# Printable extras (bingo, I-spy, match-it, Listen & Do)

Four classroom activities that go with each deck. They're made from the same words as
the cards, so children see the same pictures and hear the same Hebrew all week.
Everything prints on **US letter paper, 8.5×11"**, with 0.5" margins, so a home or
school printer can print right to the edges of the content.

For Bereshit the PDFs are in `decks/bereshit/extras/`:

| File | Pages | What it is |
|------|-------|-----------|
| `bingo.pdf` | 13 | 10 bingo boards (one per page) + 3 pages of calling cards |
| `ispy.pdf` | 4 | I-spy Easy, I-spy Challenge, coloring version, answer key |
| `match.pdf` | 6 | 3 sets of 12 match cards, each followed by its back page |
| `listen_do.pdf` | 2 | picture page for children + teacher script with answer keys |

A picture of page 1 of each is in `decks/bereshit/extras/previews/`.

---

## For teachers: how to print and play

**Printer settings for all of them:** letter paper, "Actual size" or 100% (not "Fit to
page"), color. Cardstock (65–110 lb) makes the cards last much longer.

### Bingo
- Print `bingo.pdf`. Pages 1–10 are the boards, pages 11–13 the calling cards.
- Each board has 8 pictures with their Hebrew word, plus the free space in the middle
  (Shabbat candles, נֵרוֹת שַׁבָּת).
- Cut the calling cards on the dashed lines and shuffle them.
- Show one card and say the Hebrew word. The children say it back, then cover that
  picture with a **pom-pom or a counter (not food)**.
- **Cover all 4 corners = BINGO!** The little picture under each board shows this.
  Keep playing for a full board if you like.
- Why corners and not "3 in a row"? With a free middle square, a row through the middle
  needs only two pictures, so someone wins on the 2nd or 3rd card. We checked this by
  playing 2000 pretend games on a computer: with "4 corners" the first BINGO comes
  on about card 7, and usually only one child wins at a time.

### I-spy in Gan Eden
- Page 1 (Easy, 15 things to find), page 2 (Challenge, 23 things + some extras that
  aren't counted), page 3 (black-and-white coloring version of Easy), page 4 (answer key,
  for you).
- The strip at the bottom shows what to find: "🐟 ×4 דָּג" means find 4 fish.
- Say the Hebrew word together each time a child finds one: "דָּג, דָּג, דָּג…".

### Match-it
- Print **double-sided** ("flip on long edge"). Each card page is followed by its back.
  The back is an all-over star pattern, so it still looks right if your printer shifts
  the back a little.
- Cut on the grid lines: 12 square cards (2.5") per page. The small letter in the
  corner (A, B, C) tells you which set a card belongs to.
  - **Set A**: picture ↔ same picture (memory game or snap)
  - **Set B**: picture ↔ Hebrew word (the word card has a faint picture hint)
  - **Set C** (bonus): day of creation (number + dots + יוֹם א׳) ↔ what was made that day

### Listen & Do
- Print page 1 for each child, page 2 for yourself.
- Read one direction at a time. When you say a Hebrew word the children echo it, then
  you say the English. At each **⏸ wait** stop until everyone is done.
- Level 1 is for younger children; Level 2 adds a 3-step direction. Use a fresh copy
  for each level. The answer keys at the bottom of your page show what each picture
  should look like.

---

## For Simon: how it's built

```
decks/{id}/extras.yaml          the words, counts and directions (checked by
                                schemas/extras.schema.json + src/extras_data.py)
        │
        ├─ src/generate_items.py      item art: color.png, line.png, cutout.png
        │                             items/shared/{id}/  or  decks/{id}/extras/items/{id}/
        │
        └─ src/generate_activities.py
              bingo.py   boards + the 2000-game simulation
              ispy.py    places the stickers, so the counts are exact
              templates/activities/*.html  (Jinja2)  →  Playwright (headless Chrome)
              → decks/{id}/extras/*.pdf + previews/*_p1.png
```

### Item art (one picture per word)
For each word the generator makes:
1. `color.png`: the item alone on white, 1K, with `style/plates/object.png` as the
   style reference (labeled "match art style only, not content").
2. `line.png`: a Gemini **edit** call redraws `color.png` as a coloring page, then
   Pillow cleans it up: grayscale → everything darker than 200 is black, the rest
   white → lines thickened by 1px each side. Exactly two colors, so it photocopies cleanly.
3. `cutout.png`: `color.png` with the outside white made transparent (a flood fill
   from the edges, so the white of an eye stays white), cropped to the item.

Generic items (sun, fish, Shabbat candles…) go in `items/shared/` so every deck can reuse
them for free. Items marked `deck_specific: true` (Bereshit's snake) go in the deck folder.
Existing files are never regenerated unless you ask with `--redo`.

### Two AI pictures per deck
`decks/{id}/extras/art/ispy_background.png` (empty landscape, 2K, landscape plate as
style reference) and `listen_do_scene.png` (line-art scene, 2K, then cleaned to black and
white). Each is made once, then reused. **If you regenerate the Listen & Do scene, re-measure
the `pos` boxes in extras.yaml** so the answer key lines up with the new picture.

### Making extras for a new deck
```bash
set -a; source .env; set +a                       # GEMINI_API_KEY (never print it)
export PP_SPEND_LEDGER=/path/to/spend_ledger.jsonl PP_BUDGET_USD=14   # optional spend cap
cp decks/bereshit/extras.yaml decks/noach/extras.yaml   # then edit words, prompts, counts
cd src
python generate_items.py ../decks/noach --dry-run         # see which calls it would make
python generate_items.py ../decks/noach --contact-sheet /tmp/items.png   # look at every item!
python generate_items.py ../decks/noach --redo dove:color # remake a bad one
python generate_activities.py ../decks/noach              # all four PDFs
python generate_activities.py ../decks/noach --only bingo --no-ai --all-previews /tmp/pages
```
Cost: about $0.067 per item picture (×2 per new item) and $0.10 per 2K scene. Bereshit's
first run was 30 calls, $2.08. A deck that reuses shared items costs much less.

The PDF step logs a warning when something doesn't fit (a page taller than the paper, a
card whose text overflows) or the web fonts (Heebo, Fredoka, Assistant from Google Fonts)
didn't load. It needs internet for the fonts; offline it falls back to system fonts.

### Tests
`tests/test_extras.py`: schema checks, bingo uniqueness + ≤6 shared + game length,
I-spy counts = answer key (and zones, sizes, rotation, overlap), line-art binarization,
cutouts, Hebrew wrapped in RTL spans.
