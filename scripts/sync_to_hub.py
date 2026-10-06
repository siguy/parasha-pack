"""
Publish finished decks to Simon's hub site (simonbrief-hub, /parashapacks).

Think of this as the "shipping department": the Card Designer has already printed
the cards (PNG fronts, PNG backs, a letter PDF). This script packs them up the way
the website wants them and drops them into the hub repo:

  decks/<id>/deck.json             -> HUB/app/parashapacks/decks/<id>.json
  decks/<id>/images/<card>.png     -> HUB/public/parashapacks/<id>/<card>.webp
  decks/<id>/backs/<card>_back.png -> HUB/public/parashapacks/<id>/<card>_back.webp
  decks/<id>/print/<id>-letter.pdf -> HUB/public/parashapacks/<id>/materials/<id>-letter.pdf
  decks/<id>/print/<id>-guide.pdf  -> HUB/public/parashapacks/<id>/materials/<id>-guide.pdf
  decks/<id>/extras/*.pdf          -> HUB/public/parashapacks/<id>/materials/*.pdf
  (all synced decks)               -> HUB/app/parashapacks/decks/index.json

The teacher files ("materials") are listed in the deck JSON as `materials`
(title, description, file, size, pages, category), so the deck page can show a
"Teacher materials" section with download buttons. Whatever PDFs exist get
published; a new activity PDF in extras/ shows up without code changes (it gets a
plain title until it is added to MATERIAL_INFO).

WebP is about 10x smaller than PNG for the same look, so pages load fast.
Archived decks (decks/archive/<id>/) work too.

Usage (from the repo root):
  python3 scripts/sync_to_hub.py bereshit --hub /Users/simonbrief/simonbrief-hub-parashapacks
  python3 scripts/sync_to_hub.py bereshit purim                  # uses HUB_DIR from .env
  python3 scripts/sync_to_hub.py terumah --allow-invalid          # publish a deck that fails validation

Every deck is checked with src/validate_deck.py first. If the validator reports
errors, the sync stops (exit code 1) before anything is written to the hub.
--allow-invalid publishes anyway (with a warning). Terumah needs it for now: it is
a v2 deck migrated to v3 and still fails the v3 checks (see todos/).

The classroom pilot forms (docs/pilot/) are not per-deck, so they are not published.

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
VALIDATOR = REPO / "src" / "validate_deck.py"

WEBP_QUALITY = 82
MAX_HEIGHT = 1600  # px; the exports are 3125 tall, far more than any screen needs

# Card fields the website never uses. Dropping them keeps the site's JSON small.
DROP_CARD_FIELDS = ("image_prompt", "guide")

# Teacher materials: friendly title + one-line description per file, keyed by file stem
# ("letter", "guide" or the extras PDF name). {boards} comes from extras.yaml (bingo.boards).
MATERIAL_INFO = {
    "letter": ("Cards", "The card deck",
               "Every card, kid side and teacher side, on letter paper. Cut along the marks."),
    "guide": ("Teacher guide", "Teacher booklet",
              "The week day by day: what to say, what to ask, and the Hebrew for every card."),
    "coloring": ("Activities", "Coloring + put in order",
                 "Color the story pictures, cut them out and glue them in order. Easy and full versions."),
    "sequencing": ("Activities", "Sequencing game",
                   "Two sets of mini story cards to cut out and put in order, plus the game rules."),
    "bingo": ("Activities", "Bingo: {boards} boards + calling cards",
              "Picture bingo with the week's Hebrew words. Every board is different."),
    "ispy": ("Activities", "I spy",
             "Find and count the hidden pictures. Easy, challenge and coloring pages, plus an answer key."),
    "match": ("Activities", "Match it",
              "Picture-picture and picture-word cards to cut out and pair up, or play as memory."),
    "listen_do": ("Activities", "Listen & do",
                  "Kids listen, then color and draw on the picture. Includes the teacher script."),
}
MATERIAL_CATEGORIES = ("Cards", "Teacher guide", "Activities")

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


def run_validator(deck_json: Path) -> tuple[bool, str]:
    """Run src/validate_deck.py on a deck. Returns (passed?, the validator's output)."""
    result = subprocess.run([sys.executable, str(VALIDATOR), str(deck_json)], capture_output=True, text=True)
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def decks_are_valid(deck_ids: list[str], repo: Path, allow_invalid: bool) -> bool:
    """Validate every deck before anything is copied, so a bad deck never half-publishes.

    Returns False if any deck fails and allow_invalid is off. Decks that can't be
    found are left for sync_deck to warn about.
    """
    all_ok = True
    for deck_id in deck_ids:
        deck_json = find_file(deck_roots(repo, deck_id), "deck.json")
        if deck_json is None:
            continue
        passed, output = run_validator(deck_json)
        if passed:
            logger.info("[%s] validation passed", deck_id)
        elif allow_invalid:
            logger.warning("[%s] validation failed; publishing anyway (--allow-invalid):\n%s", deck_id, output)
        else:
            logger.error("[%s] validation failed:\n%s", deck_id, output)
            all_ok = False
    return all_ok


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


def pdf_pages(pdf: Path) -> int | None:
    """Page count of a PDF, or None if it can't be read."""
    try:
        from pypdf import PdfReader
        return len(PdfReader(pdf).pages)
    except Exception as exc:  # a broken PDF should not stop the sync
        logger.warning("  could not count pages in %s: %s", pdf.name, exc)
        return None


def bingo_boards(roots: list[Path]) -> int:
    """How many bingo boards the deck prints (extras.yaml bingo.boards, default 10)."""
    extras_yaml = find_file(roots, "extras.yaml")
    if extras_yaml is None:
        return 10
    try:
        import yaml
        return int(((yaml.safe_load(extras_yaml.read_text()) or {}).get("bingo") or {}).get("boards", 10))
    except Exception:
        return 10


def find_materials(roots: list[Path], deck_id: str) -> list[tuple[str, Path]]:
    """(key, path) for every teacher PDF the deck has: cards, guide, then each extras/*.pdf."""
    found = []
    for key, relative in (("letter", f"print/{deck_id}-letter.pdf"), ("guide", f"print/{deck_id}-guide.pdf")):
        pdf = find_file(roots, relative)
        if pdf is not None:
            found.append((key, pdf))
    extras_dir = next((r / "extras" for r in roots if (r / "extras").is_dir()), None)
    if extras_dir is not None:
        known = [k for k in MATERIAL_INFO if k not in ("letter", "guide")]
        extras = sorted(extras_dir.glob("*.pdf"),
                        key=lambda p: (known.index(p.stem) if p.stem in known else len(known), p.stem))
        found.extend((p.stem, p) for p in extras)
    return found


def publish_materials(roots: list[Path], deck_id: str, out_dir: Path) -> list[dict]:
    """Copy the teacher PDFs into out_dir and describe each one for the site."""
    materials = []
    boards = bingo_boards(roots)
    for key, pdf in find_materials(roots, deck_id):
        category, title, description = MATERIAL_INFO.get(
            key, ("Activities", key.replace("_", " ").capitalize(), "A printable activity for this deck."))
        out_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf, out_dir / pdf.name)
        materials.append({
            "title": title.format(boards=boards),
            "description": description,
            "file": f"materials/{pdf.name}",
            "size": pdf.stat().st_size,
            "pages": pdf_pages(pdf),
            "category": category,
        })
    order = {c: i for i, c in enumerate(MATERIAL_CATEGORIES)}
    materials.sort(key=lambda m: order.get(m["category"], len(order)))  # stable: keeps file order within a category
    total = sum(m["size"] for m in materials)
    logger.info("  materials: %d PDFs, %.1f MB", len(materials), total / 1e6)
    return materials


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
    """Copy one deck into the hub. Returns its index.json entry, or None if the deck is not found.

    Validation happens earlier, in decks_are_valid().
    """
    roots = deck_roots(repo, deck_id)
    deck_json = find_file(roots, "deck.json")
    if deck_json is None:
        logger.warning("[%s] no deck.json in decks/%s or decks/archive/%s; skipped", deck_id, deck_id, deck_id)
        return None
    logger.info("[%s] deck: %s", deck_id, deck_json.relative_to(repo))

    deck = json.loads(deck_json.read_text())

    data_dir = hub / "app" / "parashapacks" / "decks"
    data_dir.mkdir(parents=True, exist_ok=True)

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

    materials = publish_materials(roots, deck_id, public_dir / "materials")
    has_pdf = any(m["category"] == "Cards" for m in materials)
    if not has_pdf:
        logger.warning("  missing print/%s-letter.pdf (the Print button will be hidden)", deck_id)

    site_deck = slim_deck(deck)
    site_deck["materials"] = materials
    (data_dir / f"{deck_id}.json").write_text(json.dumps(site_deck, ensure_ascii=False, indent=2) + "\n")
    logger.info("  wrote app/parashapacks/decks/%s.json (%d cards, %d materials)", deck_id, len(deck["cards"]), len(materials))

    return index_entry(deck, has_pdf, missing, series_status.get(deck_id, ""))


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
    parser.add_argument("--allow-invalid", action="store_true",
                        help="publish even if src/validate_deck.py reports errors (e.g. terumah)")
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
    if not decks_are_valid(args.deck_ids, REPO, args.allow_invalid):
        logger.error("Stopped before publishing anything. Fix the deck(s) or pass --allow-invalid.")
        return 1

    entries = [e for e in (sync_deck(d, REPO, hub, series_status) for d in args.deck_ids) if e]
    if not entries:
        logger.error("No decks synced")
        return 1
    update_index(hub, entries)
    return 0


if __name__ == "__main__":
    sys.exit(main())
