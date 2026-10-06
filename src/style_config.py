"""
Loader for style/style_config.yaml — the single source for how images are drawn
(style anchors, safety rules, modern-world rules, composition, style plates, limits).

Think of the yaml file as the art teacher's rule sheet, and this module as the
helper who reads it out loud to whoever asks.

Usage:
    import style_config
    cfg = style_config.load()
    style_config.safety_rules()                     # list of strings
    style_config.composition_for("story")          # full COMPOSITION block
    style_config.plates_for_card(card, deck)       # ["landscape"]
"""

import logging
from functools import lru_cache
from pathlib import Path

import yaml

logger = logging.getLogger("style_config")

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "style" / "style_config.yaml"


@lru_cache(maxsize=None)
def load(path: str = None) -> dict:
    """Read style_config.yaml once and cache it (pass a path only in tests)."""
    config_path = Path(path) if path else CONFIG_PATH
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def prompt_version() -> str:
    return load()["prompt_version"]


def safety_rules() -> list:
    return list(load()["safety_rules"])


def max_character_refs() -> int:
    return load()["limits"]["max_character_refs"]


def max_style_refs() -> int:
    return load()["limits"]["max_style_refs"]


def composition_for(card_type: str) -> str:
    """Build the === COMPOSITION === block for one card type ('' for unknown types)."""
    cfg = load()
    body = cfg["composition"].get(card_type)
    if not body:
        return ""
    lines = ["=== COMPOSITION ===", body.strip()]
    if card_type in cfg["title_on_top"]:
        lines.append(cfg["title_area"].strip())
    lines.append(cfg["framing_rules"].strip())
    return "\n".join(lines)


def plate_path(name: str):
    """Return the Path of a style plate by name, or None if unknown or missing on disk."""
    relative = load()["plates"].get(name)
    if not relative:
        logger.error(f"Unknown style plate '{name}'. Known: {', '.join(load()['plates'])}")
        return None
    path = REPO_ROOT / relative
    if not path.exists():
        logger.warning(f"Style plate '{name}' is listed but missing: {path}")
        return None
    return path


def any_plates_exist() -> bool:
    """True if at least one plate image is on disk (otherwise the deck style_hero is the fallback)."""
    return any((REPO_ROOT / p).exists() for p in load()["plates"].values())


def plates_for_card(card: dict, deck: dict) -> list:
    """
    Pick which style plate(s) a card gets, as a list of plate names.

    1. card["style_plate"] (a name or a list of names) wins.
    2. Otherwise plate_mapping by card type. "story_world" means: look at the
       deck's story_world_setting ("outdoor" -> landscape, "indoor" -> interior).
    """
    cfg = load()
    override = card.get("style_plate")
    if override:
        names = [override] if isinstance(override, str) else list(override)
    else:
        mapped = cfg["plate_mapping"].get(card.get("card_type", ""))
        if mapped == "story_world":
            setting = (deck.get("story_world_setting") or "").lower()
            mapped = cfg["story_world_setting_plates"].get(setting, cfg["default_story_world_plate"])
        names = [mapped] if mapped else []

    limit = max_style_refs()
    if len(names) > limit:
        logger.error(f"{card.get('card_id', '?')}: {len(names)} style plates requested, max is {limit}; "
                     f"keeping the first {limit}")
        names = names[:limit]
    return names


def reference_label(kind: str, name: str = "") -> str:
    """Return the prompt label for one reference image, e.g. reference_label('character', 'Adam')."""
    return load()["reference_labels"][kind].format(name=name)
