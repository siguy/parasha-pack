"""
Tests for the shared character library (characters/) and how generate_images uses it.

No network, no image generation. Run from the repo root:  python3 -m pytest tests -q
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
from generate_images import MAX_CHARACTER_REFS, load_reference_images  # noqa: E402


# ---------------------------------------------------------------------------
# The real library in characters/
# ---------------------------------------------------------------------------

MIGRATED = ["moses", "yitro", "miriam", "esther", "mordechai", "haman", "achashverosh"]


def test_every_character_yaml_is_valid():
    keys = character_library.list_characters()
    assert keys, "characters/ library is empty"
    for key in keys:
        character = character_library.load_character(key)
        assert character["key"] == key
        assert character_library.validate_character(character) == []


@pytest.mark.parametrize("key", MIGRATED)
def test_migrated_characters_have_identity_images(key):
    path = character_library.identity_path(key)
    assert path is not None and path.exists()
    assert character_library.load_character(key)["canonical"] is True


@pytest.mark.parametrize("key", ["adam", "chava"])
def test_adam_and_chava_exist_without_identity_yet(key):
    character = character_library.load_character(key)
    assert character["identity"] is None
    assert character_library.identity_path(key) is None
    anchors = " ".join(character["visual_anchors"]).lower()
    assert "modest" in anchors and "full coverage" in anchors


def test_aliases_resolve_to_library_keys():
    assert character_library.resolve_key("Abraham") == "avraham"
    assert character_library.resolve_key("moshe") == "moses"
    assert character_library.resolve_key("Jethro") == "yitro"  # alias from yitro's yaml
    assert character_library.load_character("abraham")["key"] == "avraham"


def test_unknown_character_returns_none():
    assert character_library.load_character("nobody") is None
    assert character_library.identity_path("nobody") is None
    assert character_library.visual_anchor_text("nobody") == ""


def test_visual_anchor_text_includes_locked_headwear():
    text = character_library.visual_anchor_text("achashverosh")
    assert text.startswith("KING ACHASHVEROSH:")
    assert "blue turban" in text


def test_validate_character_catches_bad_fields():
    problems = character_library.validate_character({"key": "x", "gender": "other", "role": "boss"})
    assert any("gender" in p for p in problems)
    assert any("role" in p for p in problems)
    assert any("visual_anchors" in p for p in problems)


def test_legacy_helpers_read_from_library():
    import schema
    from image_prompts import get_character_style
    assert schema.CHARACTER_DESIGNS["moshe"] is schema.CHARACTER_DESIGNS["moses"]
    assert "three-cornered hat" in get_character_style("haman")


def test_workflows_research_reads_library():
    from workflows import list_available_characters, research_character
    assert "adam" in list_available_characters()
    research = research_character("Abraham")
    assert research.name_he == "אַבְרָהָם"
    assert research.key_stories


# ---------------------------------------------------------------------------
# load_reference_images: library first, deck manifest as fallback, max 4
# ---------------------------------------------------------------------------

def _png(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (2, 2), "white").save(path)
    return path


def _make_library(root: Path, keys: list) -> Path:
    for key in keys:
        folder = root / key
        _png(folder / "identity.png")
        (folder / "character.yaml").write_text(
            f"key: {key}\nname_en: {key.title()}\nname_he: x\ngender: male\nrole: hero\n"
            f"canonical: true\nversion: 1\nidentity: identity.png\nvisual_anchors: [a]\n",
            encoding="utf-8",
        )
    return root


@pytest.fixture
def fake_library(tmp_path, monkeypatch):
    lib = _make_library(tmp_path / "characters", ["anna", "ben", "cara", "dov", "eli"])
    monkeypatch.setattr(character_library, "LIBRARY_DIR", lib)
    return lib


def _make_deck(tmp_path: Path, manifest: dict) -> Path:
    deck_dir = tmp_path / "deck"
    (deck_dir / "references").mkdir(parents=True)
    (deck_dir / "references" / "manifest.json").write_text(json.dumps(manifest))
    deck = deck_dir / "deck.json"
    deck.write_text("{}")
    return deck


def test_library_image_is_used_before_manifest(tmp_path, fake_library):
    deck = _make_deck(tmp_path, {"anna": {"identity": "anna_identity.png"}})
    _png(deck.parent / "references" / "anna_identity.png")
    parts, loaded = load_reference_images(deck, ["anna"], card_type="story")
    assert loaded == ["anna"]
    assert any("Anna identity sheet" in part.get("text", "") for part in parts)


def test_falls_back_to_manifest_with_warning(tmp_path, fake_library, caplog):
    deck = _make_deck(tmp_path, {"zev": {"identity": "zev_identity.png"}})
    _png(deck.parent / "references" / "zev_identity.png")
    with caplog.at_level(logging.WARNING, logger="generate_images"):
        _, loaded = load_reference_images(deck, ["zev"], card_type="story")
    assert loaded == ["zev"]
    assert "not in characters/ library" in caplog.text


def test_more_than_four_refs_is_capped_and_logged(tmp_path, fake_library, caplog):
    deck = _make_deck(tmp_path, {})
    with caplog.at_level(logging.ERROR, logger="generate_images"):
        _, loaded = load_reference_images(deck, ["anna", "ben", "cara", "dov", "eli"], card_type="story")
    assert loaded == ["anna", "ben", "cara", "dov"]
    assert len(loaded) == MAX_CHARACTER_REFS == 4
    assert "dropping: eli" in caplog.text


def test_empty_list_loads_no_characters(tmp_path, fake_library):
    deck = _make_deck(tmp_path, {})
    parts, loaded = load_reference_images(deck, [], card_type="connection", no_hero=True)
    assert parts == [] and loaded == []


def test_none_loads_manifest_characters_from_library(tmp_path, fake_library):
    # Works even when the manifest's own file paths are broken (like the archived Yitro deck)
    deck = _make_deck(tmp_path, {"ben": {"identity": "characters/ben/missing.png"}})
    _, loaded = load_reference_images(deck, None, card_type="story")
    assert loaded == ["ben"]
