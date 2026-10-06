"""
Tests for styling system v2: style_config.yaml, plate mapping, labeled reference order,
locked anchors, palette line, prompt fixes, draft/final flags, provenance.

No network. Run from the repo root:  python3 -m pytest tests -q
"""

import json
import logging
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import character_library  # noqa: E402
import generate_images  # noqa: E402
import image_prompts  # noqa: E402
import schema  # noqa: E402
import style_config  # noqa: E402
from generate_images import (assemble_references, build_generation_prompt,  # noqa: E402
                             log_generation, output_path_for, parse_args, resolve_run_mode)


# ---------------------------------------------------------------------------
# style_config.yaml is the single source
# ---------------------------------------------------------------------------

def test_safety_rules_come_from_config():
    assert schema.IMAGE_SAFETY_RULES == style_config.safety_rules()
    assert any("God in human form" in rule for rule in schema.IMAGE_SAFETY_RULES)


def test_image_prompts_reads_config():
    cfg = style_config.load()
    assert image_prompts.STYLE_ANCHORS_V2 == cfg["style_anchors"]
    assert image_prompts.MODERN_WORLD_STYLE == cfg["modern_world"]
    assert set(image_prompts.COMPOSITION_GUIDANCE) == {
        "anchor", "spotlight", "story", "connection", "tradition", "power_word"}


def test_style_anchors_keep_the_purim_look():
    # Hard rule from Simon: the art style text is unchanged
    anchors = image_prompts.STYLE_ANCHORS_V2
    assert anchors.startswith("Style: Vivid, high-contrast cartoon illustration for children ages 4-6.")
    assert "Thick, clean black outlines (2-3px equivalent)" in anchors


def test_prompt_version_and_limits():
    assert style_config.prompt_version() == "v2.0"
    assert style_config.max_character_refs() == 4
    assert style_config.max_style_refs() == 3


def test_all_four_plates_exist():
    for name in ["landscape", "interior", "object", "classroom"]:
        assert style_config.plate_path(name).exists()


# ---------------------------------------------------------------------------
# Prompt fixes (plan 5.2)
# ---------------------------------------------------------------------------

def test_lower_left_shadow_lines_are_gone():
    for card_type, block in image_prompts.COMPOSITION_GUIDANCE.items():
        assert "lower-left" not in block.lower(), card_type
        assert "low-detail ground plane" in block


def test_title_area_wording_has_no_percent_band():
    story = image_prompts.COMPOSITION_GUIDANCE["story"]
    assert "no hard band or border" in story
    assert "22%" not in story and "upper 2" not in story
    assert "central 90% of the width" in story
    assert "At most 5 figures in focus" in story


def test_modern_world_rules():
    world = image_prompts.MODERN_WORLD_STYLE
    assert "Ethiopian" in world and "Sephardi/Mizrahi" in world and "Ashkenazi" in world
    assert "Every boy wears a kippah" in world
    assert "Girls never wear a kippah" in world
    assert "WITHOUT twin wooden rollers" in world


def test_villain_posture_rule():
    rules = " ".join(style_config.safety_rules())
    assert "no pointing" in rules and "no snarling" in rules and "comic" in rules


# ---------------------------------------------------------------------------
# Plate mapping
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("card_type,setting,expected", [
    ("connection", None, ["classroom"]),
    ("tradition", None, ["classroom"]),
    ("anchor", None, ["object"]),
    ("power_word", None, ["object"]),
    ("story", "outdoor", ["landscape"]),
    ("story", "indoor", ["interior"]),
    ("spotlight", "indoor", ["interior"]),
    ("spotlight", None, ["landscape"]),  # default
])
def test_plate_mapping(card_type, setting, expected):
    deck = {"story_world_setting": setting} if setting else {}
    assert style_config.plates_for_card({"card_type": card_type}, deck) == expected


def test_card_style_plate_override_and_cap(caplog):
    assert style_config.plates_for_card({"card_type": "story", "style_plate": "object"}, {}) == ["object"]
    with caplog.at_level(logging.ERROR, logger="style_config"):
        names = style_config.plates_for_card(
            {"card_type": "story", "style_plate": ["landscape", "interior", "object", "classroom"]}, {})
    assert names == ["landscape", "interior", "object"]
    assert "max is 3" in caplog.text


# ---------------------------------------------------------------------------
# Reference assembly: fixed, labeled order
# ---------------------------------------------------------------------------

def _png(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (2, 2), "white").save(path)
    return path


@pytest.fixture
def fake_library(tmp_path, monkeypatch):
    lib = tmp_path / "characters"
    for key in ["anna", "ben", "cara", "dov", "eli"]:
        _png(lib / key / "identity.png")
        (lib / key / "character.yaml").write_text(
            f"key: {key}\nname_en: {key.title()}\nname_he: x\ngender: female\nrole: hero\n"
            f"canonical: true\nversion: 1\nidentity: identity.png\n"
            f"visual_anchors: [{key} anchor one, {key} anchor two]\n",
            encoding="utf-8",
        )
    monkeypatch.setattr(character_library, "LIBRARY_DIR", lib)
    return lib


@pytest.fixture
def deck_path(tmp_path):
    deck_dir = tmp_path / "deck"
    (deck_dir / "references").mkdir(parents=True)
    (deck_dir / "references" / "manifest.json").write_text("{}")
    _png(deck_dir / "raw" / "story_1.png")
    deck = deck_dir / "deck.json"
    deck.write_text("{}")
    return deck


def test_reference_order_and_labels(deck_path, fake_library, tmp_path):
    draft = _png(tmp_path / "story_2_d1.png")
    card = {"card_id": "story_2", "card_type": "story", "continuity_ref": "story_1",
            "characters_in_scene": ["anna", "ben"]}
    refs = assemble_references(deck_path, card, {"story_world_setting": "outdoor"}, draft_path=draft)

    labels = refs["labels"]
    assert labels[0] == "style plate 'landscape' (match art style only, not content)"
    assert labels[1].startswith("chosen draft composition: re-render this exact composition")
    assert labels[2].startswith("continuity reference, earlier card story_1")
    assert labels[3] == "Anna identity sheet — match face, hair, clothing exactly"
    assert labels[4] == "Ben identity sheet — match face, hair, clothing exactly"
    assert refs["characters"] == ["anna", "ben"]

    # Each image is preceded by its "Image N = label:" text part
    texts = [p["text"] for p in refs["parts"] if "text" in p]
    assert texts[0] == f"Image 1 = {labels[0]}:"
    assert texts[4] == f"Image 5 = {labels[4]}:"
    assert len([p for p in refs["parts"] if "inlineData" in p]) == 5
    assert refs["references"][0]["path"].endswith("style/plates/landscape.png")


def test_prompt_gets_reference_block(deck_path, fake_library):
    card = {"card_id": "story_1", "card_type": "story", "characters_in_scene": ["anna"]}
    refs = assemble_references(deck_path, card, {})
    prompt = build_generation_prompt("A garden.", "story", reference_labels=refs["labels"],
                                     character_refs_loaded=refs["characters"])
    assert prompt.startswith("=== REFERENCE IMAGES ===\nImage 1 = style plate 'landscape'")
    assert "Image 2 = Anna identity sheet — match face, hair, clothing exactly" in prompt


def test_four_character_limit(deck_path, fake_library, caplog):
    card = {"card_id": "story_1", "card_type": "story",
            "characters_in_scene": ["anna", "ben", "cara", "dov", "eli"]}
    with caplog.at_level(logging.ERROR, logger="generate_images"):
        refs = assemble_references(deck_path, card, {})
    assert refs["characters"] == ["anna", "ben", "cara", "dov"]
    assert "dropping: eli" in caplog.text


def test_no_hero_skips_plates_and_no_refs_skips_everything(deck_path, fake_library):
    card = {"card_id": "story_1", "card_type": "story", "characters_in_scene": ["anna"]}
    no_style = assemble_references(deck_path, card, {}, no_style=True)
    assert [lbl.split()[0] for lbl in no_style["labels"]] == ["Anna"]
    assert assemble_references(deck_path, card, {}, no_refs=True)["parts"] == []


def test_legacy_style_hero_only_when_no_plates(deck_path, fake_library, monkeypatch):
    _png(deck_path.parent / "references" / "style_hero.png")
    (deck_path.parent / "references" / "manifest.json").write_text(
        json.dumps({"style_hero": {"identity": "style_hero.png"}}))
    card = {"card_id": "story_1", "card_type": "story", "characters_in_scene": []}

    with_plates = assemble_references(deck_path, card, {})
    assert with_plates["labels"] == ["style plate 'landscape' (match art style only, not content)"]

    monkeypatch.setattr(style_config, "any_plates_exist", lambda: False)
    without_plates = assemble_references(deck_path, card, {})
    assert without_plates["labels"] == ["deck style hero (match art style only, not content)"]


def test_missing_continuity_ref_is_logged(deck_path, fake_library, caplog):
    card = {"card_id": "story_3", "card_type": "story", "continuity_ref": "story_9",
            "characters_in_scene": []}
    with caplog.at_level(logging.ERROR, logger="generate_images"):
        refs = assemble_references(deck_path, card, {})
    assert len(refs["labels"]) == 1
    assert "continuity_ref 'story_9' not found" in caplog.text


def test_big_reference_images_are_shrunk(tmp_path):
    big = tmp_path / "big.png"
    Image.new("RGB", (1792, 2400), "white").save(big)
    part = generate_images._load_image_as_part(big)
    assert part["inlineData"]["mimeType"] == "image/jpeg"


# ---------------------------------------------------------------------------
# Locked anchors and palette
# ---------------------------------------------------------------------------

def test_anchor_injection(fake_library):
    prompt = build_generation_prompt("Two friends.", "story", anchor_keys=["anna", "nobody"])
    assert "=== CHARACTER ANCHORS (locked, always keep) ===" in prompt
    assert "- ANNA: anna anchor one; anna anchor two" in prompt
    assert "NOBODY" not in prompt


def test_no_anchor_block_without_characters():
    assert "CHARACTER ANCHORS" not in build_generation_prompt("A sun.", "anchor")


def test_palette_line_in_world_layer():
    palette = ["#2E7D32", "#81C784", "#FFD54F", "#4FC3F7", "#8D6E63"]
    story = build_generation_prompt("A garden.", "story", story_world="Gan Eden", palette=palette)
    world = story.split("=== WORLD: STORY SETTING ===")[1].split("=== SAFETY RULES ===")[0]
    assert "Deck palette accents: #2E7D32, #81C784, #FFD54F, #4FC3F7, #8D6E63." in world

    modern = build_generation_prompt("A class.", "connection", palette=palette)
    assert "Deck palette accents: #2E7D32" in modern.split("=== SAFETY RULES ===")[0]


def test_no_palette_line_without_palette():
    assert "Deck palette accents" not in build_generation_prompt("A garden.", "story", story_world="x")


# ---------------------------------------------------------------------------
# Draft -> final flags
# ---------------------------------------------------------------------------

def test_default_mode_is_2k_single():
    run = resolve_run_mode(parse_args(["deck.json"]))
    assert run == {"mode": "default", "size": "2K", "variants": 1, "draft_path": None, "card": None}


def test_draft_mode_is_1k_two_variants():
    run = resolve_run_mode(parse_args(["deck.json", "--card", "story_1", "--draft"]))
    assert (run["mode"], run["size"], run["variants"]) == ("draft", "1K", 2)
    assert resolve_run_mode(parse_args(["deck.json", "--draft", "--variants", "3"]))["variants"] == 3


def test_final_mode_uses_2k_and_infers_card():
    run = resolve_run_mode(parse_args(["deck.json", "--final", "--from-draft", "raw/drafts/story_1_d2.png"]))
    assert (run["mode"], run["size"], run["card"]) == ("final", "2K", "story_1")
    assert run["draft_path"] == Path("raw/drafts/story_1_d2.png")


@pytest.mark.parametrize("argv", [
    ["deck.json", "--final"],                              # needs --from-draft
    ["deck.json", "--from-draft", "x_d1.png"],             # needs --final
    ["deck.json", "--draft", "--final", "--from-draft", "x_d1.png"],  # mutually exclusive
])
def test_bad_flag_combinations_exit(argv):
    with pytest.raises(SystemExit):
        parse_args(argv)


def test_output_paths(tmp_path):
    assert output_path_for(tmp_path, "story_1", "draft", 2, 2) == tmp_path / "drafts" / "story_1_d2.png"
    assert output_path_for(tmp_path, "story_1", "final", 1, 1) == tmp_path / "story_1.png"
    assert output_path_for(tmp_path, "story_1", "default", 3, 3) == tmp_path / "story_1_v3.png"


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

def test_generation_log_has_prompt_version_and_references(deck_path):
    refs = [{"label": "style plate 'landscape'", "path": "style/plates/landscape.png"}]
    log_generation(deck_path, "story_1", "m", "prompt", ["anna"], True, image_size="1K",
                   references=refs, output_file="raw/drafts/story_1_d1.png")
    record = json.loads((deck_path.parent / "raw" / "generations.jsonl").read_text().splitlines()[-1])
    assert record["prompt_version"] == "v2.0"
    assert record["references"] == refs
    assert record["output_file"] == "raw/drafts/story_1_d1.png"
