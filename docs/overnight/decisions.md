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
| 2026-10-06 | 10 | Simon: a card for each day of creation | 13-card Bereshit; "Adam names the animals" folded into Adam's spotlight; reuse 3 images + 4 new; general "sequence deck" type | blending days didn't make sense to Simon | — |
| 2026-10-06 | 10.3 | Simon: reused art did not show the days building | regenerate all 7 from one master Day 6 scene using subtractive edits | each day is the same frame, filling up | old raws moved to raw/archive/ |
| 2026-10-06 | 10.3 | Simon: cumulative scenes distract; focus on what is new | each day: new creation is the large hero, earlier days soft behind; Days 1–2 concrete and simple; Day 7 = whole world resting | children need one clear focal subject; the build-up is carried by gestures and the Day 7 payoff | master + edits approach dropped |
| 2026-10-06 | 11 | Go live | hub#4 merged; teacher link emailed to adinabeth@gmail.com (cc Simon) | Simon asked for the materials on the site plus a link explaining them | — |
