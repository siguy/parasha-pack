"""
Sefaria API client: current parasha info, plus a research cache of key verses.

Research cache:
    cd src && python3 sefaria_client.py research bereshit
    -> writes research/bereshit.yaml (skipped if it already exists; add --refresh to refetch)
"""

import json
import logging
import sys
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import yaml

logger = logging.getLogger("sefaria_client")


@dataclass
class Parasha:
    """Represents a weekly Torah portion."""
    title_en: str
    title_he: str
    ref: str
    description: str
    aliyot: list[str]
    book: str

    @property
    def border_color(self) -> str:
        """Get thematic border color based on parasha theme."""
        return get_border_color(self.title_en, self.book)


# Thematic border color mapping
THEME_COLORS = {
    # Creation/Bereshit theme - Deep blue
    "creation": "#1e3a5f",
    # Desert/Wilderness theme - Sandy gold
    "desert": "#c9a227",
    # Water stories theme - Teal
    "water": "#2d8a8a",
    # Family narratives theme - Warm amber
    "family": "#d4a84b",
    # Covenant/Law theme - Royal purple
    "covenant": "#5c2d91",
    # Redemption theme - Crimson red
    "redemption": "#a52a2a",
}

# Map parshiyot to themes
PARASHA_THEMES = {
    # Bereshit
    "Bereshit": "creation",
    "Noach": "water",
    "Lech Lecha": "family",
    "Vayera": "family",
    "Chayei Sara": "family",
    "Toldot": "family",
    "Vayetzei": "family",
    "Vayishlach": "family",
    "Vayeshev": "family",
    "Miketz": "family",
    "Vayigash": "family",
    "Vayechi": "family",
    # Shemot
    "Shemot": "redemption",
    "Vaera": "redemption",
    "Bo": "redemption",
    "Beshalach": "water",
    "Yitro": "covenant",
    "Mishpatim": "covenant",
    "Terumah": "covenant",
    "Tetzaveh": "covenant",
    "Ki Tisa": "covenant",
    "Vayakhel": "covenant",
    "Pekudei": "covenant",
    # Vayikra
    "Vayikra": "covenant",
    "Tzav": "covenant",
    "Shmini": "covenant",
    "Tazria": "covenant",
    "Metzora": "covenant",
    "Achrei Mot": "covenant",
    "Kedoshim": "covenant",
    "Emor": "covenant",
    "Behar": "covenant",
    "Bechukotai": "covenant",
    # Bamidbar
    "Bamidbar": "desert",
    "Nasso": "desert",
    "Beha'alotcha": "desert",
    "Sh'lach": "desert",
    "Korach": "desert",
    "Chukat": "desert",
    "Balak": "desert",
    "Pinchas": "desert",
    "Matot": "desert",
    "Masei": "desert",
    # Devarim
    "Devarim": "desert",
    "Vaetchanan": "covenant",
    "Eikev": "covenant",
    "Re'eh": "covenant",
    "Shoftim": "covenant",
    "Ki Teitzei": "covenant",
    "Ki Tavo": "covenant",
    "Nitzavim": "covenant",
    "Vayeilech": "covenant",
    "Ha'Azinu": "covenant",
    "V'Zot HaBerachah": "covenant",
}


def get_border_color(parasha_name: str, book: str = "") -> str:
    """
    Get the thematic border color for a parasha.

    Args:
        parasha_name: English name of the parasha
        book: Book of Torah (for fallback theming)

    Returns:
        Hex color code for the border
    """
    # Try exact match first
    theme = PARASHA_THEMES.get(parasha_name)

    # Fallback based on book
    if not theme:
        book_themes = {
            "Genesis": "family",
            "Exodus": "redemption",
            "Leviticus": "covenant",
            "Numbers": "desert",
            "Deuteronomy": "covenant",
        }
        theme = book_themes.get(book, "covenant")

    return THEME_COLORS.get(theme, THEME_COLORS["covenant"])


def fetch_current_parasha(diaspora: bool = True) -> Optional[Parasha]:
    """
    Fetch the current week's parasha from Sefaria API.

    Args:
        diaspora: If True, use diaspora calendar (default)

    Returns:
        Parasha object or None if fetch fails
    """
    url = "https://www.sefaria.org/api/calendars"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"Error fetching from Sefaria API: {e}")
        return None

    # Find the Parashat Hashavua entry
    parasha_entry = None
    for item in data.get("calendar_items", []):
        if item.get("title", {}).get("en") == "Parashat Hashavua":
            parasha_entry = item
            break

    if not parasha_entry:
        print("Could not find Parashat Hashavua in calendar")
        return None

    # Extract parasha information
    title = parasha_entry.get("displayValue", {})
    ref = parasha_entry.get("ref", "")
    description = parasha_entry.get("description", {}).get("en", "")

    # Get aliyot if available
    aliyot = []
    extra_details = parasha_entry.get("extraDetails", {})
    if "aliyot" in extra_details:
        aliyot = extra_details["aliyot"]

    # Determine the book from the reference
    book = ""
    if ref:
        book_name = ref.split()[0] if ref else ""
        book_map = {
            "Genesis": "Genesis",
            "Exodus": "Exodus",
            "Leviticus": "Leviticus",
            "Numbers": "Numbers",
            "Deuteronomy": "Deuteronomy",
        }
        book = book_map.get(book_name, "")

    return Parasha(
        title_en=title.get("en", ""),
        title_he=title.get("he", ""),
        ref=ref,
        description=description,
        aliyot=aliyot,
        book=book,
    )


def fetch_parasha_text(ref: str) -> Optional[dict]:
    """
    Fetch the full text of a parasha from Sefaria.

    Args:
        ref: Sefaria reference (e.g., "Exodus 18:1-20:23")

    Returns:
        Dictionary with Hebrew and English text, or None
    """
    # URL encode the reference
    encoded_ref = urllib.parse.quote(ref)
    url = f"https://www.sefaria.org/api/texts/{encoded_ref}"

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"Error fetching text from Sefaria: {e}")
        return None

    return {
        "hebrew": data.get("he", []),
        "english": data.get("text", []),
        "ref": data.get("ref", ref),
    }


# =============================================================================
# RESEARCH CACHE (research/{parasha}.yaml)
# =============================================================================

REPO_ROOT = Path(__file__).resolve().parent.parent
RESEARCH_DIR = REPO_ROOT / "research"
PROJECT_LOG = REPO_ROOT / "project.log"

SEFARIA_V3_TEXTS = "https://www.sefaria.org/api/v3/texts/"

# Openly licensed versions (checked on Sefaria 2026-10-05):
#   Metsudah Chumash is an Orthodox translation, CC-BY.
#   "Tanach with Nikkud" has vowels but no cantillation marks, Public Domain.
DEFAULT_EN_VERSION = "Metsudah Chumash, Metsudah Publications, 2009"
DEFAULT_HE_VERSION = "Tanach with Nikkud"

# Commentary text can be long; keep the cache readable
MAX_COMMENTARY_CHARS = 1500

# What to fetch for each parasha. Add a new entry to cache another parasha.
RESEARCH_PLANS = {
    "bereshit": {
        "verses": [
            "Genesis 1:1-5",    # Day 1: light
            "Genesis 1:6-8",    # Day 2: sky
            "Genesis 1:9-13",   # Day 3: land, seas, plants
            "Genesis 1:14-19",  # Day 4: sun, moon, stars
            "Genesis 1:20-23",  # Day 5: fish and birds
            "Genesis 1:24-31",  # Day 6: animals and people
            "Genesis 2:1-3",    # Shabbat
            "Genesis 2:7",      # Adam formed from the earth
            "Genesis 2:15",     # to work it and guard it
            "Genesis 2:18-20",  # not good to be alone; naming the animals
        ],
        "commentaries": [
            {"ref": "Rashi on Genesis 1:1:1", "fetch": True,
             "note": "Why the Torah begins with creation: the whole world belongs to Hashem."},
            {"ref": "Kohelet Rabbah 7:13:1", "fetch": True,
             "note": "Hashem shows Adam the trees: 'do not ruin My world' (caring for the world)."},
            {"ref": "Sanhedrin 37a", "fetch": False,
             "note": "One person was created alone, so each person is like a whole world "
                     "(also Mishnah Sanhedrin 4:5). Ref only: the daf is long and mostly about courts."},
        ],
    },
}


class _TextOnly(HTMLParser):
    """Collect plain text from Sefaria HTML, dropping footnotes entirely."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0  # >0 while inside a footnote

    def handle_starttag(self, tag, attrs):
        classes = dict(attrs).get("class") or ""
        if tag in ("br", "img", "hr"):  # void tags: no end tag, so don't count depth
            if not self.skip_depth:
                self.parts.append(" ")
        elif self.skip_depth:
            self.skip_depth += 1
        elif "footnote" in classes:  # <sup class="footnote-marker"> and <i class="footnote">
            self.skip_depth = 1

    def handle_endtag(self, tag):
        if self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth:
            self.parts.append(data)


def clean_text(html_text: str) -> str:
    """Strip HTML tags and footnotes; collapse whitespace."""
    parser = _TextOnly()
    parser.feed(html_text or "")
    parser.close()
    return " ".join("".join(parser.parts).split())


def _flatten(text) -> list:
    """Sefaria returns a string for one verse and (nested) lists for ranges."""
    if isinstance(text, str):
        return [text]
    flat = []
    for item in text or []:
        flat.extend(_flatten(item))
    return flat


def _get_json(url: str, timeout: int = 30) -> dict:
    """Fetch a URL and parse JSON. Tests replace this function."""
    request = urllib.request.Request(url, headers={"User-Agent": "parasha-pack"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_text_v3(ref: str, en_version: str = None, he_version: str = None) -> Optional[dict]:
    """Fetch one ref (EN + HE) from Sefaria's v3 texts API.

    en_version / he_version are version titles; None means Sefaria's default.
    Returns a dict, or None (with a logged warning) if the request fails.
    """
    params = [("version", f"english|{en_version}" if en_version else "english"),
              ("version", f"hebrew|{he_version}" if he_version else "hebrew")]
    url = SEFARIA_V3_TEXTS + urllib.parse.quote(ref) + "?" + urllib.parse.urlencode(params)
    try:
        data = _get_json(url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as e:
        logger.warning(f"Sefaria fetch failed for {ref}: {e}")
        return None

    result = {"ref": data.get("ref", ref), "he_ref": data.get("heRef", "")}
    for version in data.get("versions", []):
        lang = version.get("language")
        if lang in ("en", "he") and lang not in result:
            result[lang] = [clean_text(t) for t in _flatten(version.get("text"))]
            result[f"{lang}_version"] = {"title": version.get("versionTitle", ""),
                                         "license": version.get("license", "")}
    if "en" not in result and "he" not in result:
        logger.warning(f"Sefaria returned no text for {ref} (warnings: {data.get('warnings')})")
        return None
    return result


def _shorten(lines: list) -> tuple:
    """Join commentary lines and cut at MAX_COMMENTARY_CHARS. Returns (text, truncated)."""
    text = " ".join(lines)
    if len(text) <= MAX_COMMENTARY_CHARS:
        return text, False
    return text[:MAX_COMMENTARY_CHARS].rsplit(" ", 1)[0] + " …", True


def fetch_parasha_research(parasha: str, verses: list = None, commentaries: list = None,
                           research_dir: Path = RESEARCH_DIR, refresh: bool = False) -> Optional[dict]:
    """Build (or load) the research cache for one parasha: key verses EN/HE + commentary pointers.

    Args:
        parasha: Parasha id, e.g. "bereshit" (cache file is research/{parasha}.yaml)
        verses: Refs like "Genesis 1:1-5". Defaults to RESEARCH_PLANS[parasha].
        commentaries: [{ref, note, fetch}] dicts. Defaults to RESEARCH_PLANS[parasha].
        research_dir: Where the cache lives
        refresh: Refetch even if a complete cache file exists

    Returns:
        The research dict, or None if nothing could be fetched (network down).
    """
    parasha = parasha.lower().strip()
    cache_path = Path(research_dir) / f"{parasha}.yaml"

    # Don't refetch if we already have a complete cache
    if cache_path.exists() and not refresh:
        with open(cache_path, "r", encoding="utf-8") as f:
            cached = yaml.safe_load(f)
        if not cached.get("incomplete"):
            logger.info(f"Using cached research: {cache_path}")
            return cached
        logger.info(f"Cache {cache_path.name} is incomplete; fetching again")

    plan = RESEARCH_PLANS.get(parasha, {})
    verses = verses if verses is not None else plan.get("verses", [])
    commentaries = commentaries if commentaries is not None else plan.get("commentaries", [])
    if not verses:
        logger.warning(f"No verses given or planned for {parasha}; nothing to fetch")
        return None

    missing = []
    verse_entries = []
    for ref in verses:
        text = fetch_text_v3(ref, DEFAULT_EN_VERSION, DEFAULT_HE_VERSION)
        if text is None:
            missing.append(ref)
            continue
        verse_entries.append({"ref": text["ref"], "he_ref": text["he_ref"],
                              "en": text.get("en", []), "he": text.get("he", [])})
        versions = {"en": text.get("en_version"), "he": text.get("he_version")}
    logger.info(f"Sefaria: fetched {len(verse_entries)}/{len(verses)} verse refs for {parasha}")

    if not verse_entries:
        logger.warning(f"Sefaria: no verses fetched for {parasha}; cache not written")
        return None

    commentary_entries = []
    for item in commentaries:
        entry = {"ref": item["ref"], "note": item.get("note", "")}
        if item.get("fetch"):
            text = fetch_text_v3(item["ref"])
            if text is None:
                missing.append(item["ref"])
            else:
                for lang in ("en", "he"):
                    if text.get(lang):
                        entry[lang], truncated = _shorten(text[lang])
                        if truncated:
                            entry[f"{lang}_truncated"] = True
                        entry[f"{lang}_version"] = text.get(f"{lang}_version")
        commentary_entries.append(entry)
    logger.info(f"Sefaria: {len(commentary_entries)} commentary pointers for {parasha}")

    research = {
        "parasha": parasha,
        "source": "Sefaria (https://www.sefaria.org), v3 texts API",
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "versions": versions,
        "incomplete": bool(missing),
        "missing": missing,
        "verses": verse_entries,
        "commentaries": commentary_entries,
    }

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(f"# Research cache for {parasha}, generated by src/sefaria_client.py. "
                f"Refetch with: python3 sefaria_client.py research {parasha} --refresh\n")
        yaml.safe_dump(research, f, allow_unicode=True, sort_keys=False, width=100)
    logger.info(f"Wrote {cache_path}")
    return research


def _setup_logging() -> None:
    """INFO to the console, ERROR+ to project.log."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    error_file = logging.FileHandler(PROJECT_LOG, delay=True)
    error_file.setLevel(logging.ERROR)
    error_file.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    logging.getLogger().addHandler(error_file)


if __name__ == "__main__" and len(sys.argv) >= 3 and sys.argv[1] == "research":
    _setup_logging()
    fetch_parasha_research(sys.argv[2], refresh="--refresh" in sys.argv)

elif __name__ == "__main__":
    # Test the API
    parasha = fetch_current_parasha()
    if parasha:
        print(f"Current Parasha: {parasha.title_en} ({parasha.title_he})")
        print(f"Reference: {parasha.ref}")
        print(f"Book: {parasha.book}")
        print(f"Border Color: {parasha.border_color}")
        print(f"Description: {parasha.description[:200]}...")
    else:
        print("Could not fetch parasha")
