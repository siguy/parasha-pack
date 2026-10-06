# Parasha Pack Card Designer

A Next.js app that turns a v3 `deck.json` plus scene-only AI art into finished cards:
the title and badges on the front, the teacher script on the back. It exports PNGs
(for the web) and print-ready PDFs (for printing).

## Getting started

```bash
npm ci                      # first time only
npm run dev                 # http://localhost:3000
```

From the repo root, copy a deck in first:

```bash
./sync-deck.sh bereshit     # decks/bereshit -> card-designer/content/bereshit
```

Then open:

- `/` — list of decks in `content/`
- `/bereshit` — every card, front and back, on letter paper
- `/bereshit?format=5x7` — the same cards on the 5x7 vendor sheet (with bleed)
- `/print/bereshit?format=letter` — one sheet per page (what the export uses)

Only **v3** decks load. Convert an old deck with `python src/migrate_v2_to_v3.py decks/<id>/deck.json`.

## Exporting

```bash
npm run export bereshit                          # PNG fronts, letter
npm run export bereshit -- --backs --pdf         # PNG fronts + backs, and the duplex PDF
npm run export bereshit -- --format 5x7 --pdf    # 5x7 vendor PDF (+ PNG fronts)
npm run export bereshit -- --backs-only
```

| Output | Where |
|---|---|
| PNG fronts / backs (letter) | `decks/<id>/images/<card>.png`, `decks/<id>/backs/<card>_back.png` (2375x3125, 300 DPI, card only) |
| PNG fronts / backs (5x7) | `decks/<id>/images/5x7/`, `decks/<id>/backs/5x7/` (1500x2100) |
| PDF | `decks/<id>/print/<id>-<format>.pdf`, pages front1, back1, front2, back2… |

**Printing the letter PDF:** double-sided, **flip on long edge**, "actual size" (not "fit to page").

The export starts a dev server if none is running. Set `CARD_DESIGNER_PORT=3117` to use another
port (useful when another checkout already runs a server on 3000, which would otherwise be reused).

## Print formats

`print_formats.json` is the single source of truth:

- `letter` (default): 8.5×11 sheet, card inside a 0.3" white margin, no bleed
- `5x7`: 5.25×7.25 sheet = 5×7 trim + 0.125" bleed (filled with the card color), 0.25" safe zone

## How it is built

```
app/
  page.tsx               deck list
  [deckId]/page.tsx      viewer (fronts + backs side by side, ?format=)
  print/[deckId]/page.tsx  one sheet per page; used for PDF and PNG export
  cards.css              all card styles (ported from docs/mockups/bereshit-v3.html)
  api/images/route.ts    serves art from content/<deck>/raw/
components/cards/
  CardFactory.tsx        picks front or back and puts it on a sheet
  CardFrame.tsx          the sheet of paper (letter margin or 5x7 bleed)
  CardFront.tsx          art + title band + type chip + story number + Hebrew badge
  CardBack.tsx           header, goal, SAY / ASK / Hebrew / extras, footer, for all 7 types
  icons.tsx              SVG type icons and feeling faces (no emoji)
lib/
  api.ts                 loads v3 decks, marks which cards have art
  cardTypes.ts           per-type label, color, and back sections
  markup.ts              parses **bold**, [cue] and newlines in `say`
  formats.ts             reads print_formats.json
types/card.ts            v3 types (mirror schemas/deck.v3.schema.json)
scripts/export-deck.ts   Playwright PNG + PDF export
```

All sizes are in `cqw` (1% of the card's width), so one component renders correctly on
letter, on 5x7 and on screen. Cards without art get a gradient placeholder in the deck
palette; the home card draws its own front.

Long text is never clipped. If a back is over budget it visibly spills past the footer.
