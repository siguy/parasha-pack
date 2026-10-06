---
status: pending
priority: p2
tags: [extras, coloring, images]
---

# Coloring pages have too many regions for small hands

## Problem
The spec for coloring pages is at most 12 large, closed regions a 4-6 year old can fill
with a crayon. The current line art measures 16-29 regions (`count_regions` in
`src/coloring.py`), so pages are busier than intended.

## Where
- `src/coloring.py` (prompt text "Use at most 12 large, simple, closed regions...",
  `count_regions()`)
- Generated line art: `decks/<id>/extras/art/coloring/<card_id>.png`

## Proposed fix
- Simplify after generation: close small gaps and merge regions under a minimum area
  (morphological close + drop specks) before counting.
- Tighten the prompt (fewer objects, "no background details", thicker lines).
- Have the build warn (or regenerate a draft) when `count_regions` > 12.

## Acceptance
- Every coloring page in Bereshit and Purim measures <= 12 regions with `count_regions`.
- A test feeds a synthetic busy image and checks the warning fires.
