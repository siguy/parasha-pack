# Parasha Pack Agent Pipeline (v3)

How a deck goes from a parasha name to a printed PDF. Each step's owner, input and output, and the exact
commands. Roles are in [AGENTS.md](AGENTS.md); each agent's full rules are in `definitions/`.

## Critical rules

1. **Never guess.** Each agent uses the earlier pipeline files and the research cache, not memory.
2. **One owner per field.** If two files disagree, the owner wins and `assemble_deck.py` reports it
   (e.g. `minutes`/`core` belong to 02; the Content Writer copies them).
3. **Scene-only prompts.** Style, safety and composition come from `style/style_config.yaml`, added by
   `build_generation_prompt()`.
4. **The AI never renders text.** All text is drawn by the Card Designer.
5. **Every YAML file passes its schema** (`schemas/pipeline/<file>.schema.json`) before the next step.

## Files

All in `decks/{id}/pipeline/`:

| Step | File | Schema | Merged into deck.json |
|------|------|--------|-----------------------|
| 00 Series Planner | `00-series.yaml` | `00-series.schema.json` | `id`, `parasha_en/he`, `holiday`, `ref`, `value` |
| 01 Torah Scholar | `01-research.yaml` | `01-research.schema.json` | (checked, not copied; content cites it) |
| 02 Curriculum Designer | `02-structure.yaml` | `02-structure.schema.json` | card order, `card_type`, `sequence_number`, `story_world`, `story_world_setting`, `week_plan`; owns `minutes`/`core` |
| 02b Sensitivity Reviewer | `02b-sensitivity.yaml` | `02b-sensitivity.schema.json` | `if_they_ask` → `guide.hard_questions`; checkpoint must be approved |
| 03 Content Writer | `03-content.yaml` | `03-content.schema.json` | `title_en/he`, `hebrew_keyword`, `back`, `guide` |
| 05 Visual Director | `05-visual.yaml` | `05-visual.schema.json` | `palette`, `web_theme`, `image_prompt`, `characters_in_scene`, `style_plate`, `continuity_ref` |
| 05b Image QA | `05b-image-qa.yaml` | `05b-image-qa.schema.json` | `image_path` (from `picks[].final`) |
| 06 Editor | `06-editor.yaml` | `06-editor.schema.json` | (checked; a failing review is a warning) |

00–03 are required; 05, 05b and 06 are optional so the deck can be assembled at each stage
(prompts are placeholders until 05 exists).

## The flow, with commands

Run from the repo root unless it says `cd src`.

```bash
# 0. Set the spend guard for this session (every image call is logged; calls refused at the budget)
export PP_SPEND_LEDGER=/path/to/scratchpad/spend_ledger.jsonl
export PP_BUDGET_USD=15
source .env && export GEMINI_API_KEY

# 00 Series Planner: edit series.yaml, write pipeline/00-series.yaml, then
cd src && python3 series.py && cd ..

# 01 Torah Scholar: make sure the research cache exists
ls research/{id}.yaml || (cd src && python3 sefaria_client.py research {id})
#    write pipeline/01-research.yaml

# 02 Curriculum Designer → pipeline/02-structure.yaml
# 02b Sensitivity Reviewer → pipeline/02b-sensitivity.yaml      ★ Simon approves

# 03 Content Writer → pipeline/03-content.yaml, then
python3 src/assemble_deck.py decks/{id}          # also runs src/validate_deck.py

# 05 Visual Director → pipeline/05-visual.yaml, then
python3 src/assemble_deck.py decks/{id}          # deck.json now has the prompts
cd src && python3 generate_images.py ../decks/{id}/deck.json --card story_1 --draft && cd ..   # 2 drafts at 1K; one --card per illustrated card (skip home_1)

# 05b Image QA
python3 src/contact_sheet.py decks/{id}/raw/drafts/contact_sheet.png decks/{id}/raw/drafts/*.png --cols 4
#    score every draft, write pipeline/05b-image-qa.yaml              ★ Simon picks
cd src && python3 generate_images.py ../decks/{id}/deck.json --final --from-draft ../decks/{id}/raw/drafts/story_1_d2.png
#    (one --final per card, in card order so continuity_ref images exist); score the finals too
python3 src/assemble_deck.py decks/{id}

# 06 Editor → pipeline/06-editor.yaml + feedback.json draft (must pass)

# Card Designer tool
./sync-deck.sh {id}
cd card-designer && npm run export {id} -- --backs --pdf     # letter; add --format 5x7 for vendor print
python3 scripts/sync_to_hub.py {id}                          # publish to simonbrief-hub
```

## assemble_deck.py

`python3 src/assemble_deck.py decks/{id} [--dry-run]`

1. Loads each pipeline file and checks it against its schema (errors name the file and the path,
   e.g. `03-content.yaml: cards/3/back: ...`). Any error → stops, nothing written.
2. Cross-file checks: `deck_id` matches the folder; card mix (warning) and total (error) for the deck's
   pattern (D1, or 6 + N for a sequence deck); story cards cite a `text_ref` that matches the 01 text map
   (and 05, if it cites one); every card in
   02 has an `ok`/`reframe` verdict in 02b and the checkpoint is approved; 03 and 05 cover exactly the
   02 cards; `minutes`/`core` in 03 match 02; Image QA totals and pass flags add up.
3. Merges (structure from 02, content from 03, prompts from 05, picks from 05b) in 02's card order.
4. Checks the result: every `characters_in_scene` key is in `characters/`; the deck passes
   `schemas/deck.v3.schema.json` (which includes the optional image fields `story_world_setting`,
   `style_plate`, `continuity_ref`) and carries `text_ref`, `key_hebrew` (from the text map) and `exclude`
   (from 05).
5. Writes `deck.json`, then runs `src/validate_deck.py decks/{id}/deck.json` (a failure is an error).

Exit 0 = written and all checks passed. Errors also go to `project.log`.

## Draft → final

Drafts are cheap (1K, $0.067), finals are print size (2K, $0.101; Nano Banana 2 at 3:4). Make 2 drafts per
card, let Image QA score them, pick one, then make the final with the draft passed as a composition
reference. Expected per deck: ~$3–4 including identity sheets and extras. See `style/README.md`.

## Budgets: the spend ledger

| Env var | Meaning |
|---------|---------|
| `PP_SPEND_LEDGER` | Path of a JSONL file; every real image call appends `{ts, branch, purpose, size, usd}` |
| `PP_BUDGET_USD` | Hard cap. Once the ledger total reaches it, calls are **refused** before any network request |

Check the total before a batch (`python3 -c "import sys; sys.path.insert(0,'src'); import spend_ledger; print(spend_ledger.total_spent())"`).
Prices per size are in `src/config.py` (`IMAGE_PRICE_USD`).

## Reference

- Agent definitions: `agents/definitions/00…06`, tool: `agents/tools/card-designer.md`
- Rubrics: `agents/rubrics/image_qa.yaml`, `agents/rubrics/editor.yaml`
- Schemas: `schemas/pipeline/*.schema.json`, `schemas/deck.v3.schema.json`
- Test fixture (a tiny complete pipeline): `tests/fixtures/pipeline_min/pipeline/`
- Old (v2, 6-step) worked example: `decks/archive/yitro/pipeline/` — different file names and fields; for history only
