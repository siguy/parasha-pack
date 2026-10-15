# Character Library

One folder per character, shared by every deck. This is the **single source of truth**
for how a character looks. Before this library existed, each deck kept its own copy of
Moses in `decks/{deck}/references/`, and four Python dicts described characters in
slightly different ways.

```
characters/
├── moses/
│   ├── character.yaml     # locked design + research notes
│   ├── identity.png       # identity sheet passed to the image model
│   └── expressions.png    # optional extra sheets (also poses.png, turnaround.png)
├── adam/
│   └── character.yaml     # identity: null — sheet not generated yet
└── ...
```

## character.yaml fields

| Field | Meaning |
|-------|---------|
| `key` | Folder name and the key used in deck.json `characters_in_scene` |
| `name_en`, `name_he` | Display names (Hebrew with nikud) |
| `aliases` | Other spellings that resolve to this key (e.g. `abraham` → `avraham`) |
| `gender` | `male` or `female` (the Hebrew check uses it for verb/adjective agreement) |
| `role` | `hero`, `villain` or `neutral` (villains follow the "misguided, not scary" rules) |
| `canonical` | `true` once Simon has approved the design; `false` for drafts |
| `version` | Bump when the design changes on purpose |
| `identity` | Identity image file name in this folder, or `null` |
| `extra_sheets` | Optional expressions/poses/turnaround sheets |
| `visual_anchors` | Short locked phrases: age, skin, hair, beard, headwear, clothing colors |
| `personality`, `props`, `signature_poses` | Used by the character workflow |
| `appears_in` | Deck ids that use this character |
| `source_notes` | Where the design came from |
| `research` | Biblical refs, key stories, relationships, kid-friendly summary |

## How it is used

- `src/generate_images.py` → `load_reference_images()` looks up each key in a card's
  `characters_in_scene` here first. If a character is missing, it falls back to the deck's
  `references/manifest.json` and logs a warning. At most **4** character images are sent
  per request (Nano Banana 2 limit); extras are dropped with an error in `project.log`.
- `src/character_library.py` has the helpers: `load_character`, `list_characters`,
  `identity_path`, `visual_anchor_text`, `validate_character`.
- `schema.CHARACTER_DESIGNS` and `workflows` research are built from these files. Edit the
  yaml, not Python.

## Adding a character

1. Make `characters/{key}/character.yaml` (copy one that exists). Start with `identity: null`
   and `canonical: false`.
2. Generate 2+ identity sheets, Simon picks one, save it as `identity.png`.
3. Set `identity: identity.png`, `canonical: true`, and run `python3 -m pytest tests -q`.

## Current status

| Character | Identity sheet | Canonical |
|-----------|----------------|-----------|
| moses, yitro, miriam | yes (+ expressions, poses, turnaround) | yes |
| esther, mordechai, haman, achashverosh | yes | yes |
| adam, chava | not yet (Phase 3.2) | yes (anchors locked) |
| avraham, sarah, pharaoh | no | no (drafts from the old databases) |

The archived decks still keep their own copies in `decks/archive/*/references/`, so they
keep working unchanged.
