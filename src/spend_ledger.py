"""
Spend ledger: a running receipt of every real image API call.

Like a till receipt taped to the fridge — each call adds a line, and before a
new call we add up the receipt. If we're at the budget, we don't buy.

Turned on by environment variables (nothing happens if they are not set):
    PP_SPEND_LEDGER=/path/to/spend_ledger.jsonl   where to append records
    PP_BUDGET_USD=14.0                            refuse calls once the total reaches this

Each line: {"ts", "branch", "purpose", "size", "usd"} (+ optional "note").
"""

import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path

from config import IMAGE_PRICE_USD

logger = logging.getLogger("spend_ledger")

REPO_ROOT = Path(__file__).resolve().parent.parent


class BudgetExceeded(Exception):
    """Raised when the ledger total has reached PP_BUDGET_USD."""


def ledger_path():
    """Return the ledger Path from PP_SPEND_LEDGER, or None if spend tracking is off."""
    value = os.environ.get("PP_SPEND_LEDGER")
    return Path(value) if value else None


def budget_usd():
    """Return PP_BUDGET_USD as a float, or None if no budget is set."""
    value = os.environ.get("PP_BUDGET_USD")
    return float(value) if value else None


def price_for(size: str) -> float:
    return IMAGE_PRICE_USD[size]


def total_spent(path=None) -> float:
    """Add up the usd column of the ledger (0.0 if the file doesn't exist)."""
    path = Path(path) if path else ledger_path()
    if not path or not path.exists():
        return 0.0
    total = 0.0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                total += float(json.loads(line).get("usd", 0))
            except (ValueError, json.JSONDecodeError):
                logger.error(f"Unreadable spend ledger line skipped: {line[:80]}")
    return total


def check_budget() -> None:
    """Raise BudgetExceeded if the ledger total is at or above the budget."""
    budget = budget_usd()
    if budget is None or not ledger_path():
        return
    spent = total_spent()
    if spent >= budget:
        raise BudgetExceeded(f"Spend ledger total ${spent:.3f} has reached the budget ${budget:.2f}; "
                             f"refusing the API call")


def current_branch() -> str:
    """Git branch of this checkout (env PP_BRANCH overrides), or 'unknown'."""
    if os.environ.get("PP_BRANCH"):
        return os.environ["PP_BRANCH"]
    try:
        result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_ROOT,
                                capture_output=True, text=True, timeout=5)
        return result.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def record(purpose: str, size: str, usd: float, note: str = "") -> None:
    """Append one call to the ledger (does nothing when PP_SPEND_LEDGER is not set)."""
    path = ledger_path()
    if not path:
        return
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "branch": current_branch(),
        "purpose": purpose,
        "size": size,
        "usd": round(usd, 3),
    }
    if note:
        entry["note"] = note
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
