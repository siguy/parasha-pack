"""Tests for the Sefaria research cache. HTTP is mocked; nothing touches the network."""

import sys
import urllib.error
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import sefaria_client  # noqa: E402
from sefaria_client import clean_text, fetch_parasha_research, fetch_text_v3  # noqa: E402


def _fake_response(ref, en, he):
    return {"ref": ref, "heRef": "בראשית", "warnings": [], "versions": [
        {"language": "en", "versionTitle": "Test EN", "license": "CC-BY", "text": en},
        {"language": "he", "versionTitle": "Test HE", "license": "Public Domain", "text": he},
    ]}


def test_clean_text_strips_tags_and_footnotes():
    html = ('When God began<sup class="footnote-marker">a</sup><i class="footnote"><b>When</b> '
            'a <i>nested</i> note<br></i> to create &amp; <b>heaven</b><br>and earth')
    assert clean_text(html) == "When God began to create & heaven and earth"


def test_fetch_text_v3_flattens_and_cleans(monkeypatch):
    calls = []

    def fake_get(url, timeout=30):
        calls.append(url)
        return _fake_response("Genesis 1:1-2", ["<b>In</b> the beginning", "The earth"], ["בְּרֵאשִׁית", "וְהָאָרֶץ"])

    monkeypatch.setattr(sefaria_client, "_get_json", fake_get)
    result = fetch_text_v3("Genesis 1:1-2", "Test EN", "Test HE")
    assert result["en"] == ["In the beginning", "The earth"]
    assert result["he"] == ["בְּרֵאשִׁית", "וְהָאָרֶץ"]
    assert result["en_version"] == {"title": "Test EN", "license": "CC-BY"}
    assert "Genesis%201%3A1-2" in calls[0] and "version=english%7CTest+EN" in calls[0]


def test_single_verse_string_becomes_list(monkeypatch):
    monkeypatch.setattr(sefaria_client, "_get_json",
                        lambda url, timeout=30: _fake_response("Genesis 2:15", "to work it", "לְעָבְדָהּ"))
    assert fetch_text_v3("Genesis 2:15")["en"] == ["to work it"]


def test_research_cache_is_written_then_reused(tmp_path, monkeypatch):
    calls = []

    def fake_get(url, timeout=30):
        calls.append(url)
        return _fake_response("X", ["english"], ["עִבְרִית"])

    monkeypatch.setattr(sefaria_client, "_get_json", fake_get)
    commentaries = [{"ref": "Rashi on Genesis 1:1:1", "fetch": True, "note": "why start here"},
                    {"ref": "Sanhedrin 37a", "fetch": False, "note": "ref only"}]
    research = fetch_parasha_research("bereshit", verses=["Genesis 1:1-5", "Genesis 2:15"],
                                      commentaries=commentaries, research_dir=tmp_path)

    cache = tmp_path / "bereshit.yaml"
    assert cache.exists()
    saved = yaml.safe_load(cache.read_text(encoding="utf-8"))
    assert saved["incomplete"] is False
    assert len(saved["verses"]) == 2
    assert saved["commentaries"][0]["en"] == "english"
    assert "en" not in saved["commentaries"][1]  # ref only, not fetched
    assert research["verses"] == saved["verses"]
    assert len(calls) == 3  # 2 verses + 1 commentary

    # Second call uses the cache: no new HTTP requests
    fetch_parasha_research("bereshit", verses=["Genesis 1:1-5"], research_dir=tmp_path)
    assert len(calls) == 3


def test_network_failure_logs_warning_and_writes_nothing(tmp_path, monkeypatch, caplog):
    def broken(url, timeout=30):
        raise urllib.error.URLError("no network")

    monkeypatch.setattr(sefaria_client, "_get_json", broken)
    result = fetch_parasha_research("bereshit", verses=["Genesis 1:1-5"], commentaries=[],
                                    research_dir=tmp_path)
    assert result is None
    assert not (tmp_path / "bereshit.yaml").exists()
    assert "Sefaria fetch failed" in caplog.text


def test_partial_failure_marks_cache_incomplete_and_retries(tmp_path, monkeypatch):
    def flaky(url, timeout=30):
        if "2%3A15" in url:
            raise urllib.error.URLError("timeout")
        return _fake_response("Genesis 1:1-5", ["light"], ["אוֹר"])

    monkeypatch.setattr(sefaria_client, "_get_json", flaky)
    research = fetch_parasha_research("bereshit", verses=["Genesis 1:1-5", "Genesis 2:15"],
                                      commentaries=[], research_dir=tmp_path)
    assert research["incomplete"] is True
    assert research["missing"] == ["Genesis 2:15"]

    # Incomplete cache is fetched again next time
    monkeypatch.setattr(sefaria_client, "_get_json",
                        lambda url, timeout=30: _fake_response("Y", ["ok"], ["כֵּן"]))
    again = fetch_parasha_research("bereshit", verses=["Genesis 1:1-5", "Genesis 2:15"],
                                   commentaries=[], research_dir=tmp_path)
    assert again["incomplete"] is False


def test_bereshit_plan_has_the_key_verses():
    verses = sefaria_client.RESEARCH_PLANS["bereshit"]["verses"]
    assert verses[0] == "Genesis 1:1-5" and "Genesis 2:15" in verses and "Genesis 2:21-23" in verses and len(verses) == 13


def test_committed_bereshit_cache_is_complete():
    cache = Path(__file__).resolve().parent.parent / "research" / "bereshit.yaml"
    data = yaml.safe_load(cache.read_text(encoding="utf-8"))
    assert data["incomplete"] is False
    assert len(data["verses"]) == 13
    assert all(v["en"] and v["he"] for v in data["verses"])
