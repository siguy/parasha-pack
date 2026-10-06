---
status: pending
priority: p2
tags: [card-designer, print, visual]
---

# Visible banding in the dark shade behind front titles

## Problem
On exported fronts, the dark gradient behind the title shows horizontal steps
("banding") instead of a smooth fade. It is most visible in print and in compressed PDFs.

## Where
- `card-designer/app/cards.css`: `.pp-front .shade` (a two-stop
  `linear-gradient(to bottom, rgba(0,0,0,.65), rgba(0,0,0,0))`)
- Possibly made worse by `scripts/compress_pdf.py`

## Proposed fix
- Use an eased gradient (many stops following an ease-out curve) instead of two stops.
- Add a faint noise/dither layer over the shade (tiny tiled noise PNG or SVG
  `feTurbulence` at ~3% opacity) so the 8-bit steps break up.
- Check that PDF compression does not reintroduce the steps.

## Acceptance
- Zoomed export of a dark-title card (e.g. Purim anchor) shows no visible steps at 100%.
- Same check on the compressed letter PDF and on a home print.
