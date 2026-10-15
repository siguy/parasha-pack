"""
Publish finished decks to Simon's hub site (simonbrief-hub, /parashapacks).

Think of this as the "shipping department": the Card Designer has already printed
the cards (PNG fronts, PNG backs, a letter PDF). This script packs them up the way
the website wants them and drops them into the hub repo:

  decks/<id>/deck.json             -> HUB/app/parashapacks/decks/<id>.json
  decks/<id>/images/<card>.png     -> HUB/public/parashapacks/<id>/<card>.webp
  decks/<id>/backs/<card>_back.png -> HUB/public/parashapacks/<id>/<card>_back.webp
  decks/<id>/print/<id>-letter.pdf -> HUB/public/parashapacks/<id>/<id>-letter.pdf
  (all synced decks)               -> HUB/app/parashapacks/decks/index.json

WebP is about 10x smaller than PNG for the same look, so pages load fast.
Archived decks (decks/archive/<id>/) work too.

Usage (from the repo root):
  python3 scripts/sync_to_hub.py bereshit --hub /Users/simonbrief/simonbrief-hub-parashapacks
  python3 scripts/sync_to_hub.py bereshit purim terumah          # uses HUB_DIR from .env

Missing images or a missing PDF are logged as warnings; the sync carries on.
Run the Card Designer export first:  cd card-designer && npm run export <id> -- --backs --pdf
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
PROJECT_LOG = REPO / "project.log"

WEBP_QUALITY = 82
MAX_HEIGHT = 1600  # px; the exports are 3125 tall, far more than any screen needs

# Card fields the website never uses. Dropping them keeps the site's JSON small.
DROP_CARD_FIELDS = ("image_prompt", "guide")

logger = logging.getLogger("sync_to_hub")


def setup_logging() -> None:
    """Print INFO+ to the console and append WARNING+ to project.log."""
    if logger.handlers:
        return
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter("%(message)s"))
    log_file = logging.FileHandler(PROJECT_LOG, delay=True)  # file created only on first warning
    log_file.setLevel(logging.WARNING)
    log_file.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    logger.setLevel(logging.INFO)
    logger.addHandler(console)
    logger.addHandler(log_file)


def read_env_hub() -> str | None:
    """HUB_DIR from the environment, or from the repo's .env file."""
    if os.environ.get("HUB_DIR"):
        return os.environ["HUB_DIR"]
    env_file = REPO / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("HUB_DIR="):
                return line.split("=", 1)[1].strip().strip('"')
    return None


def deck_roots(repo: Path, deck_id: str) -> list[Path]:
    """Folders that may hold a deck's files, in order of preference.

    The export always writes to decks/<id>/, even for an archived deck, so we look
    there first and then in decks/archive/<id>/.
    """
    return [repo / "decks" / deck_id, repo / "decks" / "archive" / deck_id]


def find_file(roots: list[Path], relative: str) -> Path | None:
    for root in roots:
        candidate = root / relative
        if candidate.exists():
            return candidate
    return None


def run_validator(repo: Path, deck_json: Path) -> None:
    """Run src/validate_deck.py if it exists. Problems are warnings, not stops."""
    validator = repo / "src" / "validate_deck.py"
    if not validator.exists():
        logger.warning("  validate_deck.py not found; skipping validation")
        return
    result = subprocess.run([sys.executable, str(validator), str(deck_json)], capture_output=True, text=True)
    if result.returncode == 0:
        logger.info("  validation passed")
    else:
        logger.warning("  validation reported problems (continuing):\n%s", (result.stdout + result.stderr).strip())


def to_webp(src: Path, dest: Path) -> None:
    """Save a PNG as WebP, shrunk to MAX_HEIGHT if it is taller."""
    with Image.open(src) as img:
        img = img.convert("RGB")
        if img.height > MAX_HEIGHT:
            width = round(img.width * MAX_HEIGHT / img.height)
            img = img.resize((width, MAX_HEIGHT), Image.LANCZOS)
        img.save(dest, "WEBP", quality=WEBP_QUALITY, method=6)


def slim_deck(deck: dict) -> dict:
    """The deck as the site needs it: everything except the fields in DROP_CARD_FIELDS."""
    slim = dict(deck)
    slim["cards"] = [{k: v for k, v in card.items() if k not in DROP_CARD_FIELDS} for card in deck["cards"]]
    return slim


def load_series_status(repo: Path) -> dict[str, str]:
    """{deck id: status} from series.yaml, or {} if there is no series.yaml."""
    series_file = repo / "series.yaml"
    if not series_file.exists():
        return {}
    try:
        import yaml
    except ImportError:
        logger.warning("  PyYAML not installed; skipping series.yaml status")
        return {}
    data = yaml.safe_load(series_file.read_text()) or {}
    status = {}
    # Every top-level list (fall_holidays, parshiyot, holidays...) holds entries with id + status
    for value in data.values():
        if isinstance(value, list):
            for entry in value:
                if isinstance(entry, dict) and "id" in entry:
                    status[entry["id"]] = entry.get("status", "")
    return status


def index_entry(deck: dict, has_pdf: bool, missing: int, status: str) -> dict:
    """One deck's row in index.json: just enough for the gallery on /parashapacks."""
    cards = deck["cards"]
    cover = next((c["card_id"] for c in cards if c["card_type"] == "anchor"), cards[0]["card_id"])
    return {
        "id": deck["id"],
        "parasha_en": deck["parasha_en"],
        "parasha_he": deck["parasha_he"],
        "holiday": deck.get("holiday", False),
        "ref": deck.get("ref", ""),
        "value_en": deck.get("value", {}).get("en", ""),
        "web_theme": deck["web_theme"],
        "card_count": len(cards),
        "cover": cover,
        "has_pdf": has_pdf,
        "missing_images": missing,
        "status": status,
    }


def sync_deck(deck_id: str, repo: Path, hub: Path, series_status: dict[str, str]) -> dict | None:
    """Copy one deck into the hub. Returns its index.json entry, or None if the deck is not found."""
    roots = deck_roots(repo, deck_id)
    deck_json = find_file(roots, "deck.json")
    if deck_json is None:
        logger.warning("[%s] no deck.json in decks/%s or decks/archive/%s; skipped", deck_id, deck_id, deck_id)
        return None
    logger.info("[%s] deck: %s", deck_id, deck_json.relative_to(repo))
    run_validator(repo, deck_json)

    deck = json.loads(deck_json.read_text())

    data_dir = hub / "app" / "parashapacks" / "decks"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / f"{deck_id}.json").write_text(json.dumps(slim_deck(deck), ensure_ascii=False, indent=2) + "\n")
    logger.info("  wrote app/parashapacks/decks/%s.json (%d cards)", deck_id, len(deck["cards"]))

    # Start from an empty folder so cards removed from the deck don't linger on the site
    public_dir = hub / "public" / "parashapacks" / deck_id
    if public_dir.exists():
        shutil.rmtree(public_dir)
    public_dir.mkdir(parents=True)

    copied, missing = 0, 0
    for card in deck["cards"]:
        cid = card["card_id"]
        for relative, out_name in ((f"images/{cid}.png", f"{cid}.webp"), (f"backs/{cid}_back.png", f"{cid}_back.webp")):
            src = find_file(roots, relative)
            if src is None:
                logger.warning("  missing %s", relative)
                missing += 1
                continue
            to_webp(src, public_dir / out_name)
            copied += 1
    logger.info("  images: %d copied as WebP, %d missing", copied, missing)

    pdf = find_file(roots, f"print/{deck_id}-letter.pdf")
    if pdf is None:
        logger.warning("  missing print/%s-letter.pdf (the Print button will be hidden)", deck_id)
    else:
        shutil.copy2(pdf, public_dir / f"{deck_id}-letter.pdf")
        logger.info("  copied %s-letter.pdf", deck_id)

    return index_entry(deck, pdf is not None, missing, series_status.get(deck_id, ""))


def update_index(hub: Path, entries: list[dict]) -> list[dict]:
    """Merge new entries into index.json, keeping decks synced earlier."""
    index_file = hub / "app" / "parashapacks" / "decks" / "index.json"
    existing = json.loads(index_file.read_text()) if index_file.exists() else []
    by_id = {e["id"]: e for e in existing}
    order = [e["id"] for e in existing]
    for entry in entries:
        if entry["id"] not in by_id:
            order.append(entry["id"])  # brand-new decks go at the end
        by_id[entry["id"]] = entry
    merged = [by_id[i] for i in order]
    index_file.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n")
    logger.info("index.json: %d decks (%s)", len(merged), ", ".join(order))
    return merged


def main(argv: list[str] | None = None) -> int:
    setup_logging()
    parser = argparse.ArgumentParser(description="Publish decks to the simonbrief-hub site.")
    parser.add_argument("deck_ids", nargs="+", help="deck ids, e.g. bereshit purim")
    parser.add_argument("--hub", help="path to the simonbrief-hub checkout (default: HUB_DIR in .env)")
    args = parser.parse_args(argv)

    hub_dir = args.hub or read_env_hub()
    if not hub_dir:
        logger.error("No hub path. Pass --hub /path/to/simonbrief-hub or set HUB_DIR in .env")
        return 1
    hub = Path(hub_dir).expanduser().resolve()
    if not (hub / "app").is_dir():
        logger.error("%s does not look like the simonbrief-hub repo (no app/ folder)", hub)
        return 1

    series_status = load_series_status(REPO)
    entries = [e for e in (sync_deck(d, REPO, hub, series_status) for d in args.deck_ids) if e]
    if not entries:
        logger.error("No decks synced")
        return 1
    update_index(hub, entries)
    return 0


if __name__ == "__main__":
    sys.exit(main())
