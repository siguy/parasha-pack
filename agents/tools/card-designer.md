# Tool: Card Designer (sync → export → hub)

Not an agent: nobody makes judgment calls here. It is the print shop. Given an assembled `deck.json` and
final raw images, it renders the card fronts (text over the art) and the teacher backs, and writes PNGs
for the web and a duplex PDF for printing. (This was "Agent 07" before pipeline v3.)

## Before you start

- `python3 src/assemble_deck.py decks/{id}` reports 0 errors (and runs `src/validate_deck.py` when it exists).
- Every card has its final image at its `image_path` (usually `raw/{card_id}.png`, from Image QA picks).

## 1. Sync

```bash
./sync-deck.sh {id}        # copies decks/{id}/deck.json + raw/ into card-designer/content/{id}/
```
`decks/{id}/deck.json` is always the source of truth; never edit the copy in `card-designer/content/`.

## 2. Export

```bash
cd card-designer
npm run export {id} -- --backs --pdf                 # letter (default): PNG fronts + backs + duplex PDF
npm run export {id} -- --format 5x7 --backs --pdf    # optional vendor target (bleed + safe zone)
npm run export {id} -- --backs-only                  # PNG backs only
```

| Output | Where |
|--------|-------|
| Letter PNGs (300 DPI, card only) | `decks/{id}/images/{card}.png`, `decks/{id}/backs/{card}_back.png` |
| 5×7 PNGs | `decks/{id}/images/5x7/`, `decks/{id}/backs/5x7/` |
| Duplex PDF | `decks/{id}/print/{id}-letter.pdf` (or `-5x7.pdf`); pages front1, back1, front2… flip on long edge |

After writing a PDF the export runs `scripts/compress_pdf.py` (art re-encoded as JPEG q88, same pixels/DPI, ~57 MB → ~6 MB; best-effort, skip with `--no-compress`).

Formats come from `card-designer/print_formats.json`: **letter** = 8.5×11", 0.3" white margin, no bleed
(default, home/school printer); **5×7** = 5.25×7.25" with 0.125" bleed and a 0.25" safe zone (vendor print).
Every page is rendered from one route, `/print/{id}?format=…&side=…`, using `CardBack.tsx` for all back types.
The export **overflow guard** (plan 2.2, added to `export-deck.ts` on the validator branch) fails the export
when a section's text doesn't fit and names the card — shorten the text (Content Writer), don't shrink the
font. Until that lands, check the backs by eye: over-budget text spills visibly past the footer.

Preview while editing: `cd card-designer && npm run dev`, then `http://localhost:3000/{id}`.
If components changed, `rm -rf card-designer/.next` before exporting.

## 3. Hub sync

```bash
python3 scripts/sync_to_hub.py {id}     # built on a parallel branch (Phase 7.1)
```
Runs the validator, writes `simonbrief-hub/app/parashapacks/decks/{id}.json`, WebP images to
`public/parashapacks/{id}/`, and copies the print PDF. The hub is a separate repo with its own PR.

## Quality checks after export

- Text readable over the art (title gradient at the top, FitText titles, nikud not clipped).
- No text baked into any raw image.
- PDF has 2 pages per card (20 standard / 24 holiday), in duplex order.
- Test-print one sheet double-sided: margins and front/back alignment.

## Escalates to

Visual Director (image problems), Content Writer (text too long), Simon (layout changes).
