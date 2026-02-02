"""
Sefaria API client for fetching current parasha information.
"""

import json
import urllib.request
import urllib.error
from typing import Optional
from dataclasses import dataclass


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


if __name__ == "__main__":
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
