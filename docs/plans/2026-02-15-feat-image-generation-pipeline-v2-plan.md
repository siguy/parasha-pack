---
title: "feat: Image Generation Pipeline v2"
type: feat
date: 2026-02-15
reviewed: true
reviewers: DHH, Kieran (Python), Simplicity
---

# Image Generation Pipeline v2

## Overview

Clean up the image generation system and add multi-variant support. Two workstreams: delete dead code and add one new feature (`--variants N`).

**What this is NOT:** This plan intentionally defers sequential chaining, pipeline orchestration, and enhanced provenance. Those ideas are valid but premature — ship more decks first, then automate what actually hurts.

## Problem Statement

1. **Dead code & duplication** — `generate_image_imagen()` and `generate_image_gemini_flash()` are dead. `CHARACTER_DESIGNS` is duplicated across `schema.py` and `config.py`. `generate_references.py` still generates 4 ref types but only identity is used. `CHARACTER_LABELS` is hardcoded — adding characters for a new deck requires code changes.
2. **No variant exploration** — You get one image per generation. To compare options, you manually edit deck.json, regenerate, and use backup directories. The Purim deck accumulated 16 backup directories from this loop.

## Proposed Solution

Two workstreams, each independently shippable:

1. **Code Cleanup** — Delete dead code, consolidate duplicates, make labels dynamic (~240 LOC removed)
2. **Variant Generation** — Add `--variants N` flag, remove `--backup` (~30 LOC added)

---

## Technical Approach

### Workstream A: Code Cleanup

**Goal:** Smaller, cleaner codebase. Zero risk. Immediate value.

#### A1. Remove Dead Generation Functions

Delete from `src/generate_images.py`:
- `generate_image_imagen()` (lines 349-389) — ~40 lines, never called
- `generate_image_gemini_flash()` (lines 392-438) — ~46 lines, never called
- `--model` choice from argparse (line 447) — nano-banana is the only model
- Model selection branching in `main()` (lines 496-501, 551, 568-572) — collapse to direct `generate_image_nano_banana()` call

#### A2. Dynamic CHARACTER_LABELS from Manifest

Replace the hardcoded `CHARACTER_LABELS` dict (lines 170-178) with a function that reads from `manifest.json`:

```python
def get_character_label(character_key: str, manifest: dict) -> str:
    """Derive human-readable label from manifest entry or key name."""
    if character_key in manifest:
        return manifest[character_key].get("label", character_key.replace("_", " ").title())
    return character_key.replace("_", " ").title()
```

Add an optional `"label"` field to manifest.json entries. Falls back to title-cased key name.

**Guard:** Only call this for keys known to be in the manifest's character entries. Non-character keys (like `style_hero`) must not go through this path.

**Files:** `src/generate_images.py` (CHARACTER_LABELS replacement, load_reference_images)

#### A3. Consolidate CHARACTER_DESIGNS

`schema.py` (line 459) and `config.py` (line 138) have overlapping `CHARACTER_DESIGNS` dicts:
- `schema.py` version: `style_prompt`, `visual_traits`
- `config.py` version: `description`, `key_features`, `villain`

Consolidate into `schema.py` as the single source of truth. Merge both sets of fields.

**Critical:** Update `image_prompts.py:get_character_style()` (line 11) which imports from `schema.py` and accesses `character["style_prompt"]`. If the consolidated schema uses different field names, this breaks silently (returns `""`).

**Files:** `src/schema.py`, `src/config.py`, `src/image_prompts.py`

#### A4. Clean Up generate_references.py

The file still generates 4 reference types (identity, expressions, turnaround, poses) but CLAUDE.md says "We generate ONLY identity sheets." Remove:
- Expression sheet generation (~40 lines)
- Turnaround sheet generation (~40 lines)
- Pose sheet generation (~40 lines)
- Fix manifest format to match what `generate_images.py` expects (relative filenames)

**Files:** `src/generate_references.py`

#### Workstream A Acceptance Criteria

- [ ] `generate_image_imagen()` and `generate_image_gemini_flash()` deleted
- [ ] `--model` flag removed; nano-banana is the only code path
- [ ] Model selection branches in `main()` collapsed to direct call
- [ ] `CHARACTER_LABELS` dict removed; labels derived from manifest.json at runtime
- [ ] `CHARACTER_DESIGNS` consolidated into single location in `schema.py`
- [ ] `image_prompts.py:get_character_style()` updated to use consolidated schema fields
- [ ] `generate_references.py` generates identity-only refs; dead ref types removed
- [ ] Smoke test: full Purim generation still works

---

### Workstream B: Variant Generation

**Goal:** Generate N variants of a card. The filesystem is the UI — user looks at them and picks the winner.

#### B1. `--variants N` Flag

New CLI flag to generate multiple versions of the same card:

```bash
# Generate 3 variants of story_1
python generate_images.py ../decks/purim/deck.json --card story_1 --variants 3
```

Output naming: `raw/story_1_v1.png`, `raw/story_1_v2.png`, `raw/story_1_v3.png`

Each variant gets its own `generations.jsonl` entry (same prompt, different timestamp).

**Implementation:**

```python
# generate_images.py:main() — inside the card loop
num_variants = args.variants or 1
for variant_num in range(1, num_variants + 1):
    if num_variants > 1:
        variant_path = raw_dir / f"{card_id}_v{variant_num}.png"
    else:
        variant_path = raw_dir / f"{card_id}.png"
    # ... generate to variant_path ...
    time.sleep(2)  # Rate limiting between each API call
```

**Selection workflow:** User opens `raw/` in Finder, picks the winner, renames it to `story_1.png` (or tells Claude to `cp raw/story_1_v2.png raw/story_1.png`). Then deletes variant files. No `--select` flag needed — `cp` and `rm` already exist.

#### B2. Remove `--backup` Flag

With variants + git, backup directories are unnecessary. Remove `--backup` outright (this is a personal tool, not a public library — no deprecation period needed).

Clean up the `_create_backup()` function and related backup logic.

**Files:** `src/generate_images.py` (main loop, argparse, backup logic removal)

#### Workstream B Acceptance Criteria

- [ ] `--variants 3` generates 3 images named `{card_id}_v{1,2,3}.png`
- [ ] Each variant logged separately in `generations.jsonl`
- [ ] `--variants` works with `--card` (single card) and without (all cards)
- [ ] Rate limiting: 2s sleep between each API call (including between variants)
- [ ] `--backup` flag removed along with backup logic
- [ ] `--skip-existing` skips cards that already have a canonical `{card_id}.png` (ignores variants)

---

## What Was Cut (and Why)

### Enhanced Provenance (4 new JSONL fields) — YAGNI
The existing 6-field schema (`card_id`, `timestamp`, `model`, `full_prompt`, `character_refs`, `success`) is already sufficient. `card_id` + `timestamp` is unique. `output_path` is deterministic from `card_id`. `image_hash` solves a problem (corruption detection) that hasn't occurred. Add these fields if a concrete debugging scenario demands them.

### `--select` and `--list-variants` — Filesystem is the UI
A `cp` command does selection. `ls raw/{card}_v*.png` does listing. Building CLI subcommands for these adds complexity for a one-person project.

### Sequential Chaining (Phase 3) — Style hero already solves this
The style hero system (`references/style_hero.png` loaded as first reference for story-world cards) already provides cross-deck style consistency. Automating "anchor → chain" adds significant complexity (chain ordering, failure recovery, token limits, `--chain-from` partial regen) to replace a 30-second manual step. If style consistency remains a problem after more decks, add a simple `--style-ref <path>` flag then.

### Pipeline Runner (Phase 4) — Automate after the third time
The 7-agent pipeline has been used for one deck. Building a state file, orchestration script, and YAML assembly tool automates a process that hasn't been done enough manually to know what actually hurts. Ship 2-3 more decks first. If YAML assembly becomes painful, write `pipeline_assemble.py` as a standalone script at that point.

---

## Future Considerations (Deferred)

These are valid ideas to revisit after shipping more decks:

| Idea | When to Revisit |
|------|----------------|
| `--style-ref <path>` flag | If style hero isn't sufficient for consistency after 2+ more decks |
| `--chain` mode (sugar for style-ref + ordering) | If `--style-ref` is used manually every time |
| `pipeline_assemble.py` (YAML → deck.json) | If YAML assembly is painful after 2+ more pipeline runs |
| Enhanced provenance (UUID, hash) | If a debugging scenario actually needs it |
| Separate `provenance.py` module | If `generate_images.py` grows past ~500 lines after cleanup |

---

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| Variant files accumulate in `raw/` | Low — disk space | Delete variants after selecting winner; `.gitignore` `*_v*.png` |
| `CHARACTER_DESIGNS` consolidation breaks `get_character_style()` | Medium — silent prompt degradation | Test with Purim deck after consolidation; verify prompt output matches |
| Removing `--backup` loses safety net | Low | Git provides version history; commit before regenerating |
| `_v1`/`_v2` naming conflicts with CLAUDE.md "avoid manual copies" | Low — convention tension | Update CLAUDE.md to clarify: variants are tool-generated, not manual copies |

---

## Implementation Order

```
Workstream A (cleanup)  →  Workstream B (variants)
```

Start with A — it's pure deletion, zero risk, and makes the codebase smaller before adding new code. B adds one feature on a cleaner foundation.

**Estimated scope:** ~240 lines removed (A), ~30 lines added (B). Net reduction of ~210 lines.

---

## Documentation Plan

After implementation:
1. Update `CLAUDE.md` — remove `--model` references, add `--variants` usage, remove `--backup`
2. Update `src/CLAUDE.md` — updated module overview, removed functions, new variant workflow
3. Update `agents/LESSONS_LEARNED.md` — variant workflow pattern, convention update for `_v` files
4. Update `CHANGELOG.md` — user-facing changes

---

## References

### Internal

| File | Lines | What |
|------|-------|------|
| `src/generate_images.py` | 38-123 | `build_generation_prompt()` — prompt assembly |
| `src/generate_images.py` | 126-152 | `log_generation()` — provenance logging |
| `src/generate_images.py` | 170-178 | `CHARACTER_LABELS` — hardcoded, to be replaced |
| `src/generate_images.py` | 197-287 | `load_reference_images()` — ref loading + filtering |
| `src/generate_images.py` | 290-346 | `generate_image_nano_banana()` — API call |
| `src/generate_images.py` | 349-438 | Dead code to remove (imagen + flash) |
| `src/generate_images.py` | 441-614 | `main()` — CLI + generation loop |
| `src/image_prompts.py` | 11 | `get_character_style()` — uses CHARACTER_DESIGNS |
| `src/schema.py` | 459-518 | `CHARACTER_DESIGNS` — keep & consolidate here |
| `src/config.py` | 138-227 | `CHARACTER_DESIGNS` (extended) — merge into schema.py |
| `src/generate_references.py` | 92-248 | Dead code (expression, turnaround, pose generation) |

### Review History

Plan reviewed 2026-02-15 by three agents:
- **DHH:** "Ship Phase 1. Then go make another deck." Cut Phases 3-4 entirely. Simplify Phase 2 to `--variants N` only.
- **Kieran (Python):** Extract modules if god-module risk grows. Use dataclass for GenerationRecord if provenance expands. Guard `get_character_label()` against non-character keys. Standardize on `Path` not `str`.
- **Simplicity:** Reduce 4 phases to 2 workstreams. Cut ~65% of original plan. All 4 new provenance fields are YAGNI.
