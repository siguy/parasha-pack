"""
Tests for image generation request building and response parsing.

These run without network access — they only check the pure helper functions.
Run from the repo root:  python -m pytest tests -q
"""

import io
import json
import logging
import sys
from pathlib import Path

import pytest
from PIL import Image

# The scripts in src/ import each other by plain module name, so put src/ on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import generate_images  # noqa: E402
from generate_images import (build_image_request, extract_final_image, get_image_model,  # noqa: E402
                             save_image_as_png)
from config import EXPECTED_DIMENSIONS_3_4  # noqa: E402


# ---------------------------------------------------------------------------
# Model selection
# ---------------------------------------------------------------------------

def test_default_model_is_nano_banana_2(monkeypatch):
    monkeypatch.delenv("GEMINI_IMAGE_MODEL", raising=False)
    assert get_image_model() == "gemini-3.1-flash-image"


def test_model_can_be_overridden_from_env(monkeypatch):
    monkeypatch.setenv("GEMINI_IMAGE_MODEL", "gemini-3-pro-image")
    assert get_image_model() == "gemini-3-pro-image"


# ---------------------------------------------------------------------------
# Request building
# ---------------------------------------------------------------------------

def test_request_uses_model_in_url_and_sets_image_size(monkeypatch):
    monkeypatch.delenv("GEMINI_IMAGE_MODEL", raising=False)
    url, payload = build_image_request("a sun", "FAKEKEY", get_image_model(), "3:4", "2K")

    assert "/models/gemini-3.1-flash-image:generateContent" in url
    assert payload["generationConfig"]["imageConfig"] == {"aspectRatio": "3:4", "imageSize": "2K"}
    assert payload["contents"][0]["parts"][-1] == {"text": "a sun"}


def test_request_default_size_is_2k():
    _, payload = build_image_request("a sun", "FAKEKEY", "some-model")
    assert payload["generationConfig"]["imageConfig"]["imageSize"] == "2K"


def test_reference_images_come_before_prompt():
    ref = {"inlineData": {"mimeType": "image/png", "data": "abc"}}
    _, payload = build_image_request("a sun", "FAKEKEY", "some-model", reference_images=[ref])
    parts = payload["contents"][0]["parts"]
    assert parts == [ref, {"text": "a sun"}]


@pytest.mark.parametrize("bad_size", ["2k", "1k", "3K", "2048", "", None])
def test_invalid_size_raises(bad_size):
    with pytest.raises(ValueError, match="Invalid image size"):
        build_image_request("a sun", "FAKEKEY", "some-model", "3:4", bad_size)


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------

def _image_part(data, thought=False):
    part = {"inlineData": {"mimeType": "image/png", "data": data}}
    if thought:
        part["thought"] = True
    return part


def test_parser_skips_thought_parts_and_picks_last_image():
    result = {"candidates": [{"content": {"parts": [
        {"text": "thinking...", "thought": True},
        _image_part("DRAFT_1", thought=True),
        _image_part("FIRST_FINAL"),
        _image_part("DRAFT_2", thought=True),
        {"text": "Here is your image"},
        _image_part("LAST_FINAL"),
        _image_part("DRAFT_3", thought=True),
    ]}}]}
    assert extract_final_image(result) == "LAST_FINAL"


def test_parser_returns_none_when_only_thought_images():
    result = {"candidates": [{"content": {"parts": [_image_part("DRAFT", thought=True)]}}]}
    assert extract_final_image(result) is None


def test_parser_returns_none_for_empty_response():
    assert extract_final_image({}) is None


# ---------------------------------------------------------------------------
# Config sanity
# ---------------------------------------------------------------------------

def test_timeout_is_300_seconds():
    assert generate_images.REQUEST_TIMEOUT_SECONDS == 300


def test_expected_3_4_dimensions_match_google_table():
    # 1K and 2K were confirmed by real API calls; 512 and 4K are from Google's docs
    assert EXPECTED_DIMENSIONS_3_4 == {
        "512": (448, 600),
        "1K": (896, 1200),
        "2K": (1792, 2400),
        "4K": (3584, 4800),
    }


# ---------------------------------------------------------------------------
# Saving: JPEG from the API becomes a real PNG on disk
# ---------------------------------------------------------------------------

def _tiny_image_bytes(fmt):
    buffer = io.BytesIO()
    Image.new("RGB", (4, 3), "yellow").save(buffer, format=fmt)
    return buffer.getvalue()


def test_jpeg_is_reencoded_to_real_png(tmp_path):
    out = tmp_path / "story_1.png"
    original_mime = save_image_as_png(_tiny_image_bytes("JPEG"), str(out))

    assert original_mime == "image/jpeg"
    assert out.read_bytes().startswith(b"\x89PNG")  # PNG file signature
    with Image.open(out) as img:
        assert img.format == "PNG"
        assert img.size == (4, 3)


def test_png_is_saved_untouched(tmp_path):
    png_bytes = _tiny_image_bytes("PNG")
    out = tmp_path / "story_1.png"
    assert save_image_as_png(png_bytes, str(out)) == "image/png"
    assert out.read_bytes() == png_bytes


# ---------------------------------------------------------------------------
# Which cards get art: home cards and prompt-less cards are skipped
# ---------------------------------------------------------------------------

def test_no_art_reason():
    assert generate_images.no_art_reason({"card_type": "story", "image_prompt": "a garden"}) is None
    assert "home" in generate_images.no_art_reason({"card_type": "home", "image_prompt": "No art: ..."})
    assert generate_images.no_art_reason({"card_type": "story", "image_prompt": "  "}) == "no image_prompt"
    assert generate_images.no_art_reason({"card_type": "story"}) == "no image_prompt"


def test_full_run_skips_home_and_promptless_cards(tmp_path, monkeypatch, caplog):
    """Run main() over a whole deck with the API call mocked out: only story_1 is generated."""
    deck = {"deck_id": "demo", "cards": [
        {"card_id": "story_1", "card_type": "story", "image_prompt": "a garden at dawn"},
        {"card_id": "home_1", "card_type": "home", "image_prompt": "No art: drawn by the Card Designer."},
        {"card_id": "story_2", "card_type": "story", "image_prompt": ""},
    ]}
    deck_path = tmp_path / "demo" / "deck.json"
    deck_path.parent.mkdir()
    deck_path.write_text(json.dumps(deck))

    generated = []
    monkeypatch.setattr(generate_images, "generate_image_nano_banana",
                        lambda prompt, api_key, output_path, **kw: generated.append(output_path) or {"success": True})
    monkeypatch.setattr(generate_images, "assemble_references",
                        lambda *a, **kw: {"characters": [], "labels": [], "parts": [], "references": []})
    monkeypatch.setattr(generate_images, "build_generation_prompt", lambda *a, **kw: "PROMPT")
    monkeypatch.setattr(generate_images, "save_prompt_sidecar", lambda *a, **kw: None)
    monkeypatch.setattr(generate_images, "log_generation", lambda *a, **kw: None)
    monkeypatch.setattr(generate_images.time, "sleep", lambda s: None)

    with caplog.at_level(logging.INFO, logger="generate_images"):
        generate_images.main([str(deck_path), "--api-key", "FAKEKEY"])

    assert [Path(p).name for p in generated] == ["story_1.png"]
    assert "[SKIP] home_1 - home card" in caplog.text
    assert "[SKIP] story_2 - no image_prompt" in caplog.text
