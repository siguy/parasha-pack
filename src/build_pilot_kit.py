"""
Classroom pilot kit (plan 8.10): print the daily tick grid and the teacher feedback form.

The words live in docs/pilot/kit.yaml (columns, Friday check, the 8 questions); the card
rows come from a deck's week plan (Bereshit by default), so the grid matches the order a
teacher actually uses the cards. Same HTML -> PDF pipeline as the extras (Playwright).

Output:
    docs/pilot/daily_tick_grid.pdf
    docs/pilot/teacher_feedback_form.pdf
    docs/pilot/previews/*.png

Usage (from the repo root):
    python3 src/build_pilot_kit.py
    python3 src/build_pilot_kit.py --deck decks/noach
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_guide import save_previews, slot_label  # noqa: E402
from generate_activities import html_to_pdf  # noqa: E402
from generate_items import setup_logging  # noqa: E402

logger = logging.getLogger("build_pilot_kit")

REPO_ROOT = Path(__file__).resolve().parent.parent
PILOT_DIR = REPO_ROOT / "docs" / "pilot"
TEMPLATE_DIRS = [REPO_ROOT / "templates" / "pilot", REPO_ROOT / "templates" / "activities"]
HEADER = {"parasha_en": "Parasha Pack", "parasha_he": "פָּרָשַׁת הַשָּׁבוּעַ"}
FEEDBACK_QUESTIONS = 8


def load_kit(path: Path = PILOT_DIR / "kit.yaml") -> dict:
    kit = yaml.safe_load(path.read_text(encoding="utf-8"))
    if len(kit["feedback"]) != FEEDBACK_QUESTIONS:
        raise ValueError(f"kit.yaml has {len(kit['feedback'])} feedback questions, the protocol needs {FEEDBACK_QUESTIONS}")
    return kit


def grid_rows(deck: dict) -> list:
    """One row per card in week-plan order; the first row of each day carries the day cell."""
    rows = []
    for day in deck["week_plan"]:
        for i, card_id in enumerate(day["cards"]):
            rows.append({"day": f"Day {day['day']}", "slot": slot_label(card_id), "first": i == 0,
                         "span": len(day["cards"])})
    return rows


def build(deck_dir: Path, out_dir: Path = PILOT_DIR) -> dict:
    kit = load_kit()
    deck = json.loads((deck_dir / "deck.json").read_text(encoding="utf-8"))
    env = Environment(loader=FileSystemLoader([str(d) for d in TEMPLATE_DIRS]), autoescape=select_autoescape(["html"]))
    build_dir = out_dir / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    palette = deck.get("palette") or ["#1E3A5F", "#E0A526", "#4F9A4A", "#9BD7F5", "#FFF4D6"]
    html_paths = {}
    for name, which in (("daily_tick_grid", "grid"), ("teacher_feedback_form", "feedback")):
        text = env.get_template("forms.html").render(deck=HEADER, palette=palette, title=name, which=which,
                                                     grid=kit["tick_grid"], rows=grid_rows(deck),
                                                     feedback=kit["feedback"])
        html_paths[name] = build_dir / f"{name}.html"
        html_paths[name].write_text(text, encoding="utf-8")
    reports = html_to_pdf(html_paths, out_dir)
    problems = [p for r in reports.values() for p in r["problems"]]
    if problems:
        raise RuntimeError("Pilot forms overflow:\n  " + "\n  ".join(problems))
    for name, report in reports.items():
        save_previews(report["pdf"], out_dir / "previews", prefix=name)
    return reports


def main(argv=None) -> int:
    setup_logging()
    parser = argparse.ArgumentParser(description="Print the classroom pilot forms")
    parser.add_argument("--deck", default=str(REPO_ROOT / "decks" / "bereshit"), help="Deck whose week plan sets the rows")
    args = parser.parse_args(argv)
    try:
        build(Path(args.deck).resolve())
    except Exception as error:
        logger.error(str(error))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
