---
status: pending
priority: p2
tags: [card-designer, fonts, pdf, offline]
---

# PDF export depends on Google Fonts at build time

## Problem
The Card Designer loads Heebo, Assistant, Fredoka, Mali, Patrick Hand (and Geist) through
`next/font/google`, which downloads them when the app builds. Offline, or if Google is
slow, Next falls back to system fonts and the PDFs silently get the wrong Hebrew font and
different text sizes (text may overflow).

## Where
- `card-designer/app/layout.tsx` (`import { ... } from "next/font/google"`)

## Proposed fix
Download the font files once into `card-designer/public/fonts/` (check each license allows
it; these are all OFL) and switch to `next/font/local`. Keep the same CSS variable names so
nothing else changes.

## Acceptance
- With networking off, `npm run export bereshit -- --backs --pdf` produces the same PDF as online.
- `grep -r "next/font/google" card-designer/app` returns nothing.
