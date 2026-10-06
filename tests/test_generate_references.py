"""
Tests for identity sheets in the character library: prompt, version numbers, --accept.
No network.
"""

import sys
from pathlib import Path

import pytest
import yaml
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import generate_references  # noqa: E402
from generate_references import (accept_version, get_identity_prompt, next_version,  # noqa: E402
                                 set_yaml_identity)

YAML = """# Comment that must survive
key: zara
name_en: Zara
name_he: x
gender: female
role: hero
canonical: true
version: 1
identity: null
visual_anchors:
  - young woman with olive skin
  - simple modest sage-green tunic dress, full coverage
personality: [curious, kind]
"""


@pytest.fixture
def library(tmp_path):
    folder = tmp_path / "characters" / "zara"
    folder.mkdir(parents=True)
    (folder / "character.yaml").write_text(YAML, encoding="utf-8")
    return tmp_path / "characters"


def _png(path, color="white"):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (2, 2), color).save(path)


def test_prompt_uses_anchors_and_forbids_text(library):
    prompt = get_identity_prompt("zara", library)
    assert "- young woman with olive skin" in prompt
    assert "front view, three-quarter view, side view" in prompt
    assert "happy, curious, caring, surprised" in prompt
    assert "NO text, captions, labels" in prompt
    assert "No leaves" in prompt
    assert prompt.startswith("Image 1 is a style plate")


def test_prompt_unknown_character_raises(library):
    with pytest.raises(ValueError):
        get_identity_prompt("nobody", library)


def test_next_version_counts_alternates(library):
    folder = library / "zara"
    assert next_version(folder) == 1
    _png(folder / "identity_v1.png")
    _png(folder / "alternates" / "identity_v3.png")
    assert next_version(folder) == 4


def test_accept_promotes_and_moves_others(library):
    folder = library / "zara"
    _png(folder / "identity_v1.png", "red")
    _png(folder / "identity_v2.png", "blue")

    accept_version("zara", "v2", library)

    assert (folder / "identity.png").exists()
    assert not (folder / "identity_v2.png").exists()
    assert (folder / "alternates" / "identity_v1.png").exists()
    with Image.open(folder / "identity.png") as img:
        assert img.getpixel((0, 0)) == (0, 0, 255)
    text = (folder / "character.yaml").read_text()
    assert "# Comment that must survive" in text
    assert yaml.safe_load(text)["identity"] == "identity.png"


def test_accept_keeps_old_identity_as_alternate(library):
    folder = library / "zara"
    _png(folder / "identity.png", "green")
    _png(folder / "identity_v1.png", "red")
    accept_version("zara", 1, library)
    assert (folder / "alternates" / "identity_previous.png").exists()


def test_accept_missing_version_raises(library):
    with pytest.raises(FileNotFoundError):
        accept_version("zara", "v9", library)


def test_set_yaml_identity_needs_line(tmp_path):
    path = tmp_path / "c.yaml"
    path.write_text("key: x\n")
    with pytest.raises(ValueError):
        set_yaml_identity(path, "identity.png")


def test_generate_versions_saves_to_library(library, monkeypatch):
    calls = []

    def fake_generate(prompt, api_key, output_path, aspect_ratio, image_size, reference_images, purpose):
        calls.append((output_path, aspect_ratio, image_size, purpose, len(reference_images)))
        _png(Path(output_path))
        return True

    monkeypatch.setattr(generate_references, "generate_image", fake_generate)
    monkeypatch.setattr(generate_references.time, "sleep", lambda s: None)
    saved = generate_references.generate_identity_versions("zara", "KEY", versions=2, library_dir=library)

    assert [p.name for p in saved] == ["identity_v1.png", "identity_v2.png"]
    assert calls[0][1:] == ("16:9", "2K", "zara identity v1", 2)  # label text + plate image
    assert (library / "zara" / "identity_prompt.txt").exists()
