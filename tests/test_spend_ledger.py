"""
Tests for the spend ledger and the budget refusal. No network: urlopen is replaced.
"""

import base64
import io
import json
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import generate_images  # noqa: E402
import spend_ledger  # noqa: E402
from config import IMAGE_PRICE_USD  # noqa: E402


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    path = tmp_path / "spend_ledger.jsonl"
    monkeypatch.setenv("PP_SPEND_LEDGER", str(path))
    monkeypatch.setenv("PP_BRANCH", "test-branch")
    monkeypatch.delenv("PP_BUDGET_USD", raising=False)
    return path


def _lines(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def test_prices_match_plan():
    assert IMAGE_PRICE_USD == {"512": 0.045, "1K": 0.067, "2K": 0.101, "4K": 0.151}


def test_record_appends_all_fields(ledger):
    spend_ledger.record("bereshit story_1 draft 1", "1K", 0.067)
    spend_ledger.record("adam identity v1", "2K", 0.101)
    rows = _lines(ledger)
    assert len(rows) == 2
    assert set(rows[0]) == {"ts", "branch", "purpose", "size", "usd"}
    assert rows[0]["branch"] == "test-branch"
    assert spend_ledger.total_spent() == pytest.approx(0.168)


def test_nothing_written_when_ledger_off(tmp_path, monkeypatch):
    monkeypatch.delenv("PP_SPEND_LEDGER", raising=False)
    spend_ledger.record("x", "2K", 0.101)  # must not raise
    assert spend_ledger.total_spent() == 0.0
    spend_ledger.check_budget()  # no budget, no ledger: never refuses


def test_check_budget_refuses_at_or_over(ledger, monkeypatch):
    monkeypatch.setenv("PP_BUDGET_USD", "0.2")
    spend_ledger.record("a", "2K", 0.101)
    spend_ledger.check_budget()  # 0.101 < 0.2: fine
    spend_ledger.record("b", "2K", 0.099)
    with pytest.raises(spend_ledger.BudgetExceeded):
        spend_ledger.check_budget()  # 0.200 >= 0.2


class _FakeResponse:
    def __init__(self, payload):
        self._data = json.dumps(payload).encode()

    def read(self):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _fake_image_response():
    buffer = io.BytesIO()
    Image.new("RGB", (4, 3), "blue").save(buffer, format="PNG")
    data = base64.b64encode(buffer.getvalue()).decode()
    return {"candidates": [{"content": {"parts": [{"inlineData": {"mimeType": "image/png", "data": data}}]}}]}


def test_successful_call_is_recorded(ledger, tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(generate_images.urllib.request, "urlopen",
                        lambda req, timeout: calls.append(req) or _FakeResponse(_fake_image_response()))
    result = generate_images.generate_image_nano_banana(
        "a sun", "FAKEKEY", str(tmp_path / "out.png"), image_size="1K", purpose="test draft")
    assert result["success"] and len(calls) == 1
    assert _lines(ledger)[-1]["usd"] == 0.067
    assert _lines(ledger)[-1]["purpose"] == "test draft"


def test_call_refused_when_budget_reached(ledger, tmp_path, monkeypatch):
    monkeypatch.setenv("PP_BUDGET_USD", "14.0")
    ledger.write_text(json.dumps({"usd": 14.0}) + "\n")

    def must_not_call(*args, **kwargs):
        raise AssertionError("network called despite budget")

    monkeypatch.setattr(generate_images.urllib.request, "urlopen", must_not_call)
    result = generate_images.generate_image_nano_banana(
        "a sun", "FAKEKEY", str(tmp_path / "out.png"), image_size="2K")
    assert result == {"success": False, "prompt": "a sun", "refused": True}
    assert len(_lines(ledger)) == 1  # refusal adds no spend line
    assert not (tmp_path / "out.png").exists()
