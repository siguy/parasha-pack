# Overnight decisions log

Each choice Claude made overnight on Simon's behalf (Simon approved this approach on 2026-10-05). The runners-up are kept in an `alternates/` folder next to each chosen file so Simon can swap one in.

| When | Phase | Decision | Chosen | Why | Alternates |
|---|---|---|---|---|---|
| 2026-10-05 | 1.1 | Bereshit mockup layout | `docs/mockups/bereshit-v3.html` as built | Simon approved the "I pick, you review" approach for checkpoints | — |
| 2026-10-05 | 5.3 | Style plate: landscape | chosen v1 | boldest outlines and color, closest to Purim | `alternates/plate_landscape_v2.png` (thinner, pastel) |
| 2026-10-05 | 5.3 | Style plate: interior | chosen v1 | clean; the alternate has a hard band at the top. Both are paler than Purim, so this is the weakest match | `alternates/plate_interior_v2.png` |
| 2026-10-05 | 5.3 | Style plate: object (candles + challah) | chosen v1 | natural glow; the alternate has a band at the top | `alternates/plate_object_v2.png` |
| 2026-10-05 | 5.3 | Style plate: classroom | chosen v1 | blank posters with no text; the alternate has menorah symbols, no ceiling, and copies the Purim rug | `alternates/plate_classroom_v2.png` |
| 2026-10-05 | 5.3 | Prompt wording | replace "calm upper 22%" | it made the model draw a literal flat band in 2 of 8 images | — |
| 2026-10-05 | 5.3 | Style plates approved by Simon | all 4 chosen plates | Simon: "fine as long as they are style references." No comparison test needed | — |
| 2026-10-05 | 3.2 | Adam identity sheet | v2 | cartoon proportions closest to Purim, big friendly eyes, clear expressions | `characters/adam/alternates/identity_v1.png` (more realistic, flat expressions) |
| 2026-10-05 | 3.2 | Chava identity sheet | **v3** (extra generation, $0.10) | v1 and v2 both looked like a young girl next to adult Adam; I added an "adult proportions matching Adam" anchor | `characters/chava/alternates/identity_v2.png`, `identity_v1.png` |
| 2026-10-05 | 3.2 | Clothing colors | muted earth tones kept (oatmeal / sage) | follows the locked anchors; quieter than Purim's bold palette, so **Simon may want brighter** | — |
| 2026-10-06 | 8.2 | Bingo win rule | "cover the 4 corners" | with a free center, 3-in-a-row wins on call 2–3; corners give a median first win at call 7 with 1.19 winners on average | `win_rule: line` in extras.yaml |
| 2026-10-06 | 8.3 | Snake in games | included as a friendly animal in I-spy and bingo | it's just an animal to find; the snake *story* stays guide-only (hard-text policy). **Simon may prefer to drop it** | remove `snake` from extras.yaml vocab |
| 2026-10-06 | 6 (00) | Bereshit middah gesture (series.yaml had none) | "arms in a big circle: hug the world" | Matches the 00-series example; easy for 4-year-olds; reads as "caring for the world" | "two hands cupped like holding a seedling" |
| 2026-10-06 | 6 (01) | Research cache missing Chava's creation and Genesis 3 | Added Genesis 2:21-23, 3:1-7, 3:20-21 to the bereshit research plan and refetched from Sefaria | The Torah Scholar must cite verses from the cache; the spotlight_2 pshat and the "if they ask" scripts need these verses | Leave refs uncited |
| 2026-10-06 | 6 (02) | Power word card characters | Adam and Chava (story world, landscape plate) giving a joyful thumbs up | Keeps the power word in the same glowing Gan Eden as the stories; both identities exist; modern kids already appear on the connection card | Modern gan children (classroom plate) |
| 2026-10-06 | 6 (02) | Spotlight Chava characters | Chava alone (chest-up portrait) | A spotlight is one character; keeps her identity ref strong; Adam is on spotlight_1 and story_4 | Chava with Adam in the background |
| 2026-10-06 | 6 (02) | ★core total is 26 min, not ~15 | Kept the approved mockup minutes/core | Simon approved the mockup; the week plan spreads core cards over 5 days. Flagged for Simon in 06-editor | Un-star story_2 / story_3 |
| 2026-10-06 | 6 (02b) | ★ Checkpoint 1: sensitivity verdicts | Approved (decided_by: coordinator): 7 ok, 3 reframe (anchor dark = cozy; Chava: only "Hashem made Chava" on the card; story_4 ends with caring for animals, no tree/snake). 5 scripted answers: snake & fruit, leaving the garden, who made Hashem, dinosaurs, how Chava was made | Follows D3, D4 and the hard-text policy; no card needed replacing | — |
| 2026-10-06 | 6 (03) | Changes to the approved back wording | Only: anchor transition "What did Hashem make on Day 1?"; story_2 transition "Who will take care of it all?"; trio 👍 → ✓; keyword badge translit stress in CAPS (OR, DAG, sha-BAT, ar-YEH) | Validator flagged "first"/"now meet" transitions; emoji not licensed for print; CAPS-stress rule | — |
