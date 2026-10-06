"""
Tests for image generation request building and response parsing.

These run without network access — they only check the pure helper functions.
Run from the repo root:  python -m pytest tests -q
"""

import sys
from pathlib import Path

import pytest

# The scripts in src/ import each other by plain module name, so put src/ on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import generate_images  # noqa: E402
from generate_images import build_image_request, extract_final_image, get_image_model  # noqa: E402


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
