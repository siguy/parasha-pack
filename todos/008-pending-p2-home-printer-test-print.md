---
status: pending
priority: p2
tags: [print, manual, simon]
---

# Home-printer test print not done yet

## Problem
The letter PDF (the default format) has not been printed on a real home printer. We don't
yet know if the duplex backs line up, if margins get clipped, or if titles are readable
across a classroom.

## Where
- `decks/bereshit/print/bereshit-letter.pdf` (and `decks/purim/print/purim-letter.pdf`)
- Print settings in `card-designer/print_formats.json` (letter: 0.3 in margin, no bleed)

## Proposed fix
Simon prints one deck: US Letter, **duplex, flip on long edge**, 100% scale (not "fit to
page"). Then checks:
1. Fronts and backs line up after cutting (hold to a window).
2. Nothing important is clipped at the 0.3 in margin.
3. Titles and Hebrew are readable from about 3 m (10 ft).
Note the printer model and any offset; adjust `print_formats.json` if needed.

## Acceptance
- Notes from the test print added to this file (printer, offset, legibility verdict).
- Any fix to margins/sizes merged, or this todo marked done with "no changes needed".
