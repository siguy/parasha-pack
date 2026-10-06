"""
Teacher guide booklet: one letter-size PDF per deck, laid out page by page from guide_layout.yaml.

Think of guide_layout.yaml as the booklet's table of contents written in stone: "Story 2 is
always on p.7". Card backs print "Guide p.7", so the booklet MUST put Story 2 on p.7. This
script builds the pages in that exact order, prints them, and then checks the PDF to prove it.

Where the words come from (nothing is typed twice):
    deck.json                         each card's guide block, week_plan, value (middah)
    pipeline/01-research.yaml         the parasha in brief, learning objectives
    pipeline/02-structure.yaml        learning objectives
    pipeline/02b-sensitivity.yaml     the "if they ask" scripts (hard questions)
    research/{id}.yaml                which translations the verses come from
    decks/{id}/guide.yaml             booklet-only bits: how to use, family letter, extras index
    guide_layout.yaml                 which page holds what

Steps:
    1. Gather the content above into one list of pages (page 1 .. N, none missing, none twice).
    2. Fill templates/guide/booklet.html (Jinja2), one fixed-size 8.5x11 box per page.
    3. Print to PDF with Playwright (same helper as the extras). If any page's content is taller
       than its box, the build FAILS: an overflowing page would push every later page number off.
    4. Check the PDF with pypdf: page count == the layout, and every card's guide_ref.page has
       that card's footer on that page.
    5. Compress the pictures (scripts/compress_pdf.py) and save PNG previews of every page.

Usage (from the repo root or src/):
    python3 src/build_guide.py decks/bereshit
    python3 src/build_guide.py decks/bereshit --no-previews
"""

import argparse
import json
import logging
import re
import subprocess
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_activities import hebrew_html, html_to_pdf  # noqa: E402
from generate_items import setup_logging  # noqa: E402
import deck_pattern  # noqa: E402

logger = logging.getLogger("build_guide")

REPO_ROOT = Path(__file__).resolve().parent.parent
LAYOUT_PATH = REPO_ROOT / "guide_layout.yaml"
TEMPLATES = REPO_ROOT / "templates" / "guide"
COMPRESS = REPO_ROOT / "scripts" / "compress_pdf.py"
PREVIEW_DPI = 80
THUMB_PX = 640

SLOT_NAMES = {"anchor": "Anchor", "spotlight": "Spotlight", "story": "Story", "connection": "Connection",
              "power_word": "Power word", "home": "Home card", "tradition": "Tradition"}
FIXED_NAMES = {"cover": "How to use", "overview": "Bereshit in brief", "hard_questions": "If they ask",
               "adaptations": "Adaptations", "extras_index": "Extras", "family_letter": "Family letter",
               "sources": "Sources"}


class GuideError(Exception):
    """The booklet can't be built correctly (missing page, overflow, page map mismatch)."""


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def script_html(text: str) -> str:
    """Card-back script to HTML: **say** -> bold, [do] -> stage direction, Hebrew -> RTL span."""
    out = hebrew_html(text)
    out = re.sub(r"\*\*(.+?)\*\*", r'<b class="say">\1</b>', out)
    out = re.sub(r"\[(.+?)\]", r'<span class="do">[\1]</span>', out)
    return out.replace("\n", "<br>")


def slot_label(card_id: str, deck: dict = None) -> str:
    """story_2 -> 'Story 2' ('Day 2' in a sequence deck), anchor_1 -> 'Anchor' (numbered only when a deck can have several)."""
    kind, _, number = card_id.rpartition("_")
    name = deck_pattern.story_word(deck) if kind == "story" else SLOT_NAMES.get(kind, kind.replace("_", " ").title())
    return f"{name} {number}" if kind in ("spotlight", "story", "tradition") else name


def load_yaml(path: Path, required: bool = True) -> dict:
    if not path.exists():
        if required:
            raise GuideError(f"Missing {path}")
        logger.warning(f"  {path} not found; that part of the booklet will be thinner")
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


# ---------------------------------------------------------------------------
# 1. The page plan
# ---------------------------------------------------------------------------

def layout_for(deck: dict, layout: dict = None) -> dict:
    """This deck's page map {'cards': {...}, 'fixed': {...}}: one page per story card (see deck_pattern.py)."""
    layout = layout or load_yaml(LAYOUT_PATH)
    return deck_pattern.deck_page_map(deck, layout)


def page_plan(deck: dict, layout: dict) -> list:
    """
    One entry per page, 1..N: {'n', 'fixed': [...], 'cards': [...]}.

    Raises GuideError if a page is missing, if a layout card isn't in the deck, or if a deck
    card has no page. (Two things may share a page on purpose: home_1 + family_letter.)
    """
    by_page = {}
    for name, n in layout["fixed"].items():
        by_page.setdefault(n, {"n": n, "fixed": [], "cards": []})["fixed"].append(name)
    deck_ids = [c["card_id"] for c in deck["cards"]]
    for card_id, n in layout["cards"].items():
        if card_id not in deck_ids:
            raise GuideError(f"guide_layout.yaml has {card_id} on p.{n}, but the deck has no {card_id}")
        by_page.setdefault(n, {"n": n, "fixed": [], "cards": []})["cards"].append(card_id)
    missing_cards = [c for c in deck_ids if c not in layout["cards"]]
    if missing_cards:
        raise GuideError(f"Cards with no guide page in guide_layout.yaml: {missing_cards}")
    total = max(by_page)
    gaps = [n for n in range(1, total + 1) if n not in by_page]
    if gaps:
        raise GuideError(f"guide_layout.yaml leaves pages {gaps} empty")
    return [by_page[n] for n in range(1, total + 1)]


def check_guide_refs(deck: dict, layout: dict) -> list:
    """Every card back's guide_ref.page must equal its page in the layout. Returns problems."""
    problems = []
    for card in deck["cards"]:
        ref = (card.get("back") or {}).get("guide_ref")
        if ref is None:
            continue
        expected = layout["cards"].get(card["card_id"])
        if ref.get("page") != expected:
            problems.append(f"{card['card_id']}: back says Guide p.{ref.get('page')}, layout says p.{expected}")
    return problems


# ---------------------------------------------------------------------------
# 2. Content for each page
# ---------------------------------------------------------------------------

class Guide:
    def __init__(self, deck_dir: Path):
        self.deck_dir = deck_dir
        self.deck = json.loads((deck_dir / "deck.json").read_text(encoding="utf-8"))
        self.deck_id = self.deck["id"]
        self.cards = {c["card_id"]: c for c in self.deck["cards"]}
        self.layout = layout_for(self.deck)
        pipeline = deck_dir / "pipeline"
        self.research = load_yaml(pipeline / "01-research.yaml", required=False)
        self.structure = load_yaml(pipeline / "02-structure.yaml", required=False)
        self.sensitivity = load_yaml(pipeline / "02b-sensitivity.yaml", required=False)
        self.series = load_yaml(pipeline / "00-series.yaml", required=False)
        self.extra = load_yaml(deck_dir / "guide.yaml")
        self.sefaria = load_yaml(REPO_ROOT / "research" / f"{self.deck_id}.yaml", required=False)
        self.out_dir = deck_dir / "print"
        self.build_dir = self.out_dir / "build" / "guide"
        (self.build_dir / "thumbs").mkdir(parents=True, exist_ok=True)

    # ---- small lookups -------------------------------------------------------

    def slot(self, card_id: str) -> str:
        """'Day 3' in a sequence deck, 'Story 3' otherwise (see slot_label)."""
        return slot_label(card_id, self.deck)

    def title(self, card_id: str) -> str:
        """The card's English title without a leading 'Day 3: ' when the slot already says it."""
        title, prefix = self.cards[card_id]["title_en"], f"{self.slot(card_id)}: "
        return title[len(prefix):] if title.startswith(prefix) else title

    def cards_label(self, card_ids: list) -> str:
        """['story_1', ..., 'story_7', 'home_1'] -> 'Days 1–7, Home card' (runs of 3+ story cards become a range)."""
        nums = [int(c.rpartition("_")[2]) for c in card_ids if c.startswith("story_")]
        parts = []
        if nums:
            word = deck_pattern.story_word(self.deck)
            if len(nums) == 1:
                parts.append(f"{word} {nums[0]}")
            elif len(nums) > 2 and nums == list(range(nums[0], nums[-1] + 1)):
                parts.append(f"{word}s {nums[0]}–{nums[-1]}")
            else:
                parts.append(f"{word}s " + ", ".join(str(n) for n in nums))
        return ", ".join(parts + [self.slot(c) for c in card_ids if not c.startswith("story_")])

    def teaching_day(self, day):
        """'Tue' (sequence deck) or 'Day 2' (standard) for a week_plan day; None stays None."""
        return deck_pattern.teaching_day_label(day, self.deck) if day else None

    def day_of(self, card_id: str):
        for day in self.deck.get("week_plan", []):
            if card_id in day["cards"]:
                return day["day"]
        return None

    def thumb(self, card_id: str):
        """The exported card front (letter), shrunk to a JPEG; raw art if not exported. None if neither."""
        card = self.cards[card_id]
        target = self.build_dir / "thumbs" / f"{card_id}.jpg"
        for source in (self.deck_dir / "images" / f"{card_id}.png", self.deck_dir / card.get("image_path", "")):
            if source.is_file():
                if not target.exists():
                    pic = Image.open(source).convert("RGB")
                    pic.thumbnail((THUMB_PX, THUMB_PX * 2))
                    pic.save(target, quality=85)
                return f"thumbs/{card_id}.jpg"
        logger.warning(f"  no picture for {card_id} (export the deck to get thumbnails)")
        return None

    def if_they_ask(self, card_id: str = None) -> list:
        """The 02b scripts (the single source for hard-question answers), optionally for one card."""
        items = list(self.sensitivity.get("if_they_ask", []))
        known = {(q["card_id"], q["q"]) for q in items}
        # deck.json may hold a few extra, milder ones (e.g. "Is the dark scary?"): add those too
        for card in self.deck["cards"]:
            for q in (card.get("guide") or {}).get("hard_questions", []):
                if (card["card_id"], q["q"]) not in known:
                    items.append(dict(q, card_id=card["card_id"]))
        items.sort(key=lambda q: self.layout["cards"].get(q["card_id"], 99))  # booklet order (stable)
        return [q for q in items if card_id is None or q["card_id"] == card_id]

    def rendered_questions(self, card_id: str = None) -> list:
        return [{"q": hebrew_html(q["q"]), "answer": hebrew_html(q["answer"]),
                 "redirect": hebrew_html(q["redirect"]), "refs": q.get("refs", []),
                 "topic": q.get("topic", ""), "card": self.slot(q["card_id"]),
                 "title": self.title(q["card_id"])} for q in self.if_they_ask(card_id)]

    # ---- page builders -------------------------------------------------------

    def card_page(self, card_id: str) -> dict:
        card = self.cards[card_id]
        guide, back = card.get("guide") or {}, card.get("back") or {}
        hebrew = back.get("hebrew") or card.get("hebrew_keyword")
        power = self.series.get("power_word")
        if not hebrew and card["card_type"] == "power_word" and power:
            hebrew = {"word": power["he"], "translit": power["translit"], "meaning": power["en"],
                      "gesture": power.get("gesture")}
        return {
            "card_id": card_id, "slot": self.slot(card_id), "type": card["card_type"],
            "title_en": self.title(card_id), "title_he": card["title_he"], "thumb": self.thumb(card_id),
            "objective": hebrew_html(re.sub(r"\*\*", "", back.get("objective", ""))),
            "minutes": back.get("minutes"), "core": back.get("core"),
            "day": self.teaching_day(self.day_of(card_id)),
            # sequence decks: the verses this card shows and their key Hebrew words (01 text map)
            "text_ref": card.get("text_ref", ""), "key_hebrew": card.get("key_hebrew", ""),
            "hebrew": hebrew,
            "pshat": hebrew_html(guide.get("pshat", {}).get("text", "")),
            "refs": guide.get("pshat", {}).get("refs", []),
            "sages": [{"text": hebrew_html(s["text"]), "source": s["source"]} for s in guide.get("sages", [])],
            "questions": self.rendered_questions(card_id),
            "adapt": {k: hebrew_html(v) for k, v in (guide.get("adapt") or {}).items()},
            "extend": hebrew_html(guide.get("extend", "")), "tip": hebrew_html(guide.get("tip", "")),
            "transition": hebrew_html(back.get("transition", "")),
        }

    def week(self) -> list:
        extras_by_day = {}
        for extra in self.extra.get("extras", []):
            extras_by_day.setdefault(extra["best_day"], []).append(extra["name"])
        days = []
        for day in self.deck.get("week_plan", []):
            cards = [{"slot": self.slot(c), "title": self.title(c),
                      "minutes": (self.cards[c].get("back") or {}).get("minutes"),
                      "core": (self.cards[c].get("back") or {}).get("core"),
                      "page": self.layout["cards"][c]} for c in day["cards"]]
            minutes = sum(c["minutes"] or 0 for c in cards)
            days.append({"day": day["day"], "day_label": self.teaching_day(day["day"]), "label": day["label"], "cards": cards, "minutes": minutes,
                         "extras": extras_by_day.get(day["day"], [])})
        return days

    def cover(self) -> dict:
        toc = []
        for page in page_plan(self.deck, self.layout):
            names = [FIXED_NAMES.get(f, f) for f in page["fixed"]]
            names += [f"{self.slot(c)}: {self.title(c)}" for c in page["cards"]
                      if not page["fixed"] or c != "home_1"]
            toc.append({"n": page["n"], "name": " · ".join(names)})
        return {"how_to_use": [script_html(t) for t in self.extra.get("how_to_use", [])], "toc": toc,
                "value": self.deck["value"]}

    def overview(self) -> dict:
        moments = [{"text": hebrew_html(m["moment"]), "refs": m["refs"]} for m in self.research.get("key_moments", [])]
        objectives = self.structure.get("learning_objectives", {})
        power = self.series.get("power_word") or {}
        return {"summary": hebrew_html(self.research.get("summary", "").strip()),
                "emotional_core": hebrew_html(self.research.get("emotional_core", "")),
                "moments": moments, "objectives": {k: hebrew_html(v) for k, v in objectives.items()},
                "power": power, "characters": self.series.get("characters", []),
                "skipped": [p for p in self.research.get("hard_passages", [])
                            if p.get("suggested_handling") in ("guide-only", "skip")]}

    def adaptations(self) -> list:
        rows = []
        for card_id in self.layout["cards"]:
            guide = self.cards[card_id].get("guide") or {}
            adapt = guide.get("adapt") or {}
            rows.append({"slot": self.slot(card_id), "title": self.title(card_id),
                         "see": hebrew_html(adapt.get("see", "")), "do": hebrew_html(adapt.get("do", "")),
                         "join": hebrew_html(adapt.get("join", "")), "extend": hebrew_html(guide.get("extend", "")),
                         "page": self.layout["cards"][card_id]})
        return rows

    def extras_index(self) -> list:
        rows = []
        for extra in self.extra.get("extras", []):
            file_path = (self.deck_dir / "extras" / extra["file"]).resolve()
            if not file_path.exists():
                logger.warning(f"  extras index: {extra['file']} not found (build it with generate_activities.py)")
            rows.append({**extra, "cards": [self.cards_label(extra["cards"])],
                         "best_day_label": self.teaching_day(extra["best_day"]),
                         "file_label": Path(extra["file"]).name + (f" p.{extra['pages']}" if extra.get("pages") else "")})
        return rows

    def family_letter(self) -> dict:
        letter = self.extra["family_letter"]
        home = self.cards.get("home_1", {}).get("back", {})
        wanted = letter["hard_question"]
        matches = [q for q in self.if_they_ask(wanted["card_id"]) if q.get("topic") == wanted["topic"]]
        if not matches:
            raise GuideError(f"family letter: no if_they_ask script for {wanted}")
        question = matches[0]
        activities = home.get("try_at_home", [])
        activity = activities[letter.get("activity_from_home_card", 0)] if activities else None
        return {"learned": [hebrew_html(t) for t in letter["learned"]], "value": self.deck["value"],
                "word": home.get("hebrew") or self.series.get("power_word"),
                "review": letter.get("review_words", []), "song": hebrew_html(letter["song"]),
                "activity": activity and {"text": hebrew_html(activity["text"]), "tag": activity.get("tag", "")},
                "shabbat_question": home.get("shabbat_question"),
                "question": {"q": hebrew_html(question["q"]), "answer": hebrew_html(question["answer"]),
                             "redirect": hebrew_html(question["redirect"])},
                "question_raw": question}

    def sources(self) -> dict:
        refs = []
        for card_id in self.layout["cards"]:
            guide = self.cards[card_id].get("guide") or {}
            refs.append({"slot": self.slot(card_id), "title": self.title(card_id),
                         "refs": guide.get("pshat", {}).get("refs", []),
                         "sages": [s["source"] for s in guide.get("sages", [])]})
        commentaries = sorted({s["source"] for c in self.deck["cards"] for s in (c.get("guide") or {}).get("sages", [])})
        hard = sorted({r for q in self.if_they_ask() for r in q.get("refs", [])})
        versions = self.sefaria.get("versions", {})
        return {"cards": refs, "commentaries": commentaries, "hard_refs": hard,
                "texts": [f"{v['title']} ({v.get('license', '')})" for v in versions.values()],
                "fetched": self.sefaria.get("source", "")}

    # ---- all pages -----------------------------------------------------------

    def pages(self) -> list:
        out = []
        for page in page_plan(self.deck, self.layout):
            fixed, cards = page["fixed"], page["cards"]
            entry = {"n": page["n"]}
            if "family_letter" in fixed:
                entry.update(kind="family_letter", letter=self.family_letter(),
                             footer=" · ".join([self.slot(c) for c in cards] + [FIXED_NAMES["family_letter"]]))
            elif fixed:
                kind = fixed[0]
                builder = {"cover": self.cover, "overview": self.overview, "hard_questions": self.rendered_questions,
                           "adaptations": self.adaptations, "extras_index": self.extras_index,
                           "sources": self.sources}[kind]
                entry.update(kind=kind, data=builder(), footer=FIXED_NAMES[kind])
            else:
                card_id = cards[0]
                entry.update(kind="card", card=self.card_page(card_id), footer=self.slot(card_id))
                if card_id == "anchor_1":
                    entry["week"] = self.week()
            entry["slots"] = [self.slot(c) for c in cards]
            out.append(entry)
        return out


# ---------------------------------------------------------------------------
# 3-5. Render, print, verify, compress, preview
# ---------------------------------------------------------------------------

def render(guide: Guide) -> Path:
    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html"]))
    palette = guide.deck.get("palette") or ["#1E3A5F", "#E0A526", "#4F9A4A", "#9BD7F5", "#FFF4D6"]
    pages = guide.pages()
    html_text = env.get_template("booklet.html").render(deck=guide.deck, palette=palette, pages=pages,
                                                        total=len(pages), fixed=guide.layout["fixed"])
    path = guide.build_dir / "booklet.html"
    path.write_text(html_text, encoding="utf-8")
    return path


def pdf_page_texts(pdf_path: Path) -> list:
    from pypdf import PdfReader
    return [page.extract_text() or "" for page in PdfReader(str(pdf_path)).pages]


def verify_pdf(pdf_path: Path, deck: dict, layout: dict) -> list:
    """Page count == layout, and each card's footer sits on its guide_ref page. Returns problems."""
    texts = pdf_page_texts(pdf_path)
    total = max(list(layout["cards"].values()) + list(layout["fixed"].values()))
    problems = []
    if len(texts) != total:
        problems.append(f"PDF has {len(texts)} pages, guide_layout.yaml has {total}")
    for card in deck["cards"]:
        page = (card.get("back") or {}).get("guide_ref", {}).get("page") or layout["cards"].get(card["card_id"])
        if not page or page > len(texts):
            problems.append(f"{card['card_id']}: page {page} is not in the PDF")
            continue
        marker = f"p.{page} · {slot_label(card['card_id'], deck)}"
        if marker not in " ".join(texts[page - 1].split()):
            problems.append(f"{card['card_id']}: footer '{marker}' not found on PDF page {page}")
    return problems


def save_previews(pdf_path: Path, out_dir: Path, prefix: str = "guide") -> list:
    import fitz  # PyMuPDF
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    with fitz.open(pdf_path) as doc:
        for number, page in enumerate(doc, 1):
            pix = page.get_pixmap(dpi=PREVIEW_DPI)
            path = out_dir / f"{prefix}_p{number:02d}.png"
            Image.frombytes("RGB", (pix.width, pix.height), pix.samples).quantize(256).save(path, optimize=True)
            paths.append(path)
    return paths


def compress(pdf_path: Path) -> None:
    if not COMPRESS.exists():
        return
    result = subprocess.run([sys.executable, str(COMPRESS), str(pdf_path)], capture_output=True, text=True)
    if result.returncode != 0:
        logger.warning(f"  compress_pdf failed: {result.stderr.strip()[:300]}")


def build(deck_dir: Path, previews: bool = True) -> Path:
    guide = Guide(deck_dir)
    problems = check_guide_refs(guide.deck, guide.layout)
    if problems:
        raise GuideError("Card backs and guide_layout.yaml disagree:\n  " + "\n  ".join(problems))
    letter = guide.family_letter()["question_raw"]
    logger.info(f"Building the {guide.deck['parasha_en']} guide: {len(page_plan(guide.deck, guide.layout))} pages")
    html_path = render(guide)
    pdf_name = f"{guide.deck_id}-guide"
    reports = html_to_pdf({pdf_name: html_path}, guide.out_dir)
    report = reports[pdf_name]
    if report["problems"]:
        raise GuideError("Pages overflow (fix the content or the template):\n  " + "\n  ".join(report["problems"]))
    pdf_path = report["pdf"]
    problems = verify_pdf(pdf_path, guide.deck, guide.layout)
    if problems:
        raise GuideError("PDF check failed:\n  " + "\n  ".join(problems))
    compress(pdf_path)
    logger.info(f"  verified: {report['pages']} pages, every guide_ref matches; family letter uses the "
                f"'{letter['topic']}' script; {pdf_path.stat().st_size // 1024} KB")
    if previews:
        paths = save_previews(pdf_path, guide.out_dir / "previews")
        logger.info(f"  previews: {len(paths)} PNGs in {paths[0].parent}")
    return pdf_path


def main(argv=None) -> int:
    setup_logging()
    parser = argparse.ArgumentParser(description="Build the teacher guide booklet PDF for a deck")
    parser.add_argument("deck_dir")
    parser.add_argument("--no-previews", action="store_true")
    args = parser.parse_args(argv)
    try:
        build(Path(args.deck_dir).resolve(), previews=not args.no_previews)
    except GuideError as error:
        logger.error(str(error))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
