"""
Tests for scripts/sync_to_hub.py, using a tiny fake repo and fake hub in tmp_path.
Run from the repo root:  python -m pytest tests -q
"""

import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import sync_to_hub  # noqa: E402


def make_deck(root: Path, deck_id: str, card_ids: list[str]) -> dict:
    deck = {
        "id": deck_id,
        "version": "3.0",
        "parasha_en": "Test",
        "parasha_he": "טֶסְט",
        "holiday": False,
        "value": {"en": "Kindness"},
        "web_theme": {"primary": "#111111", "secondary": "#222222", "accent": "#333333", "wash": "#ffffff"},
        "cards": [
            {"card_id": cid, "card_type": "anchor" if cid.startswith("anchor") else "story",
             "image_prompt": "a long prompt", "guide": {"tip": "x"}, "back": {"say": "hi"}}
            for cid in card_ids
        ],
    }
    root.mkdir(parents=True, exist_ok=True)
    (root / "deck.json").write_text(json.dumps(deck))
    return deck


def make_png(path: Path, size=(500, 2000)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, "orange").save(path)


def test_sync_copies_json_webp_pdf_and_index(tmp_path):
    repo, hub = tmp_path / "repo", tmp_path / "hub"
    (hub / "app").mkdir(parents=True)
    deck_dir = repo / "decks" / "demo"
    make_deck(deck_dir, "demo", ["anchor_1", "story_1"])
    for cid in ("anchor_1", "story_1"):
        make_png(deck_dir / "images" / f"{cid}.png")
        make_png(deck_dir / "backs" / f"{cid}_back.png")
    (deck_dir / "print").mkdir()
    (deck_dir / "print" / "demo-letter.pdf").write_bytes(b"%PDF-1.4 fake")

    entry = sync_to_hub.sync_deck("demo", repo, hub, {"demo": "done"})
    sync_to_hub.update_index(hub, [entry])

    site_deck = json.loads((hub / "app/parashapacks/decks/demo.json").read_text())
    assert "image_prompt" not in site_deck["cards"][0] and "guide" not in site_deck["cards"][0]
    assert site_deck["cards"][0]["back"] == {"say": "hi"}

    out = hub / "public/parashapacks/demo"
    with Image.open(out / "story_1_back.webp") as img:
        assert img.format == "WEBP"
        assert img.height == sync_to_hub.MAX_HEIGHT  # shrunk from 2000
    assert (out / "demo-letter.pdf").exists()

    index = json.loads((hub / "app/parashapacks/decks/index.json").read_text())
    assert index == [entry]
    assert entry["card_count"] == 2 and entry["has_pdf"] and entry["status"] == "done"
    assert entry["cover"] == "anchor_1" and entry["missing_images"] == 0


def test_missing_images_warn_and_archive_decks_are_found(tmp_path):
    repo, hub = tmp_path / "repo", tmp_path / "hub"
    (hub / "app").mkdir(parents=True)
    archive_dir = repo / "decks" / "archive" / "old"
    make_deck(archive_dir, "old", ["anchor_1", "story_1"])
    make_png(archive_dir / "images" / "anchor_1.png")  # only one of four images

    entry = sync_to_hub.sync_deck("old", repo, hub, {})
    assert entry["missing_images"] == 3
    assert entry["has_pdf"] is False
    assert (hub / "public/parashapacks/old/anchor_1.webp").exists()


def test_index_keeps_earlier_decks(tmp_path):
    hub = tmp_path / "hub"
    (hub / "app/parashapacks/decks").mkdir(parents=True)
    sync_to_hub.update_index(hub, [{"id": "a", "n": 1}, {"id": "b", "n": 1}])
    merged = sync_to_hub.update_index(hub, [{"id": "b", "n": 2}, {"id": "c", "n": 1}])
    assert [e["id"] for e in merged] == ["a", "b", "c"]
    assert merged[1]["n"] == 2


def test_unknown_deck_is_skipped(tmp_path):
    assert sync_to_hub.sync_deck("nope", tmp_path, tmp_path, {}) is None
