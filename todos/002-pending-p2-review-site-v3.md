---
status: pending
priority: p2
tags: [code, review-site, v3]
---

# Review site reads v2 fields only; regenerate passes unknown flags

## Problem
1. `review-site/` reads v2 card fields (`front`/`back` structure), so v3 decks
   (`title_en`, `back`, `guide`, `hebrew_keyword` at the card's top level) show up blank or broken.
2. `regenerate_card` builds `python generate_images.py <deck> --card <id> --auto-retry --verbose`.
   `generate_images.py` has no `--auto-retry` or `--verbose` flags, so argparse exits with
   an error whenever auto-retry is ticked.

## Where
- `review-site/app.js`, `review-site/index.html`, `review-site/preview.html`
- `review-site/api/handlers.py` (`regenerate_card`, around the `cmd = [...]` list)

## Proposed fix
- Read v3 fields first, fall back to v2 (`card.title_en ?? card.back?.title_en`), like
  `generate_images.py` does with `is_v2_card()`.
- In `regenerate_card`, only pass flags `generate_images.py` accepts (`--card`, `--draft`,
  `--size`, `--variants`). Drop auto-retry or map it to `--variants 2`. Use `sys.executable`
  instead of `"python"`.

## Acceptance
- Bereshit and Purim cards show titles, backs and guide text in the review site.
- A test calls `regenerate_card` with `subprocess.run` mocked and checks the command parses
  with `generate_images.parse_args`.
