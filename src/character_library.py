"""
Shared character library: one folder per character in characters/{key}/.

Each folder holds:
  - character.yaml  the locked design (name, gender, role, visual anchors, research notes)
  - identity.png    the identity sheet passed to the image model (may be missing for new characters)

Think of it like a school's class photo album: every deck looks up the same
photo of Moses instead of keeping its own copy.

Usage:
    from character_library import load_character, identity_path
    esther = load_character("esther")
    path = identity_path("esther")       # Path or None
"""

import logging
from pathlib import Path

import yaml

logger = logging.getLogger("character_library")

# characters/ lives at the repo root, next to src/
LIBRARY_DIR = Path(__file__).resolve().parent.parent / "characters"

REQUIRED_FIELDS = ["key", "name_en", "name_he", "gender", "role", "canonical",
                   "version", "identity", "visual_anchors"]
VALID_GENDERS = {"male", "female"}
VALID_ROLES = {"hero", "villain", "neutral"}

# Old or English spellings -> library key. Each character.yaml can add more via "aliases".
ALIASES = {
    "abraham": "avraham",
    "moshe": "moses",
}


def _library_dir(library_dir=None) -> Path:
    return Path(library_dir) if library_dir else LIBRARY_DIR


def _read_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_all(library_dir=None) -> list:
    """Read every characters/*/character.yaml (skips broken files with an error log)."""
    characters = []
    folder = _library_dir(library_dir)
    if not folder.exists():
        logger.warning(f"Character library not found: {folder}")
        return characters
    for yaml_path in sorted(folder.glob("*/character.yaml")):
        try:
            characters.append(_read_yaml(yaml_path))
        except yaml.YAMLError as e:
            logger.error(f"Could not read {yaml_path}: {e}")
    return characters


def resolve_key(key: str, library_dir=None) -> str:
    """Turn any spelling ("Abraham", "moshe") into the library key ("avraham", "moses")."""
    key = key.lower().strip().replace(" ", "_")
    if key in ALIASES:
        return ALIASES[key]
    if (_library_dir(library_dir) / key / "character.yaml").exists():
        return key
    # Aliases declared inside character.yaml files
    for character in _load_all(library_dir):
        if key in [a.lower() for a in character.get("aliases", [])]:
            return character["key"]
    return key


def list_characters(library_dir=None) -> list:
    """Return the keys of every character in the library, sorted."""
    return sorted(c["key"] for c in _load_all(library_dir) if c.get("key"))


def load_character(key: str, library_dir=None):
    """Return the character.yaml contents as a dict, or None if the character isn't in the library."""
    key = resolve_key(key, library_dir)
    yaml_path = _library_dir(library_dir) / key / "character.yaml"
    if not yaml_path.exists():
        return None
    try:
        return _read_yaml(yaml_path)
    except yaml.YAMLError as e:
        logger.error(f"Could not read {yaml_path}: {e}")
        return None


def identity_path(key: str, library_dir=None):
    """Return the Path to the character's identity image, or None if it has none yet."""
    character = load_character(key, library_dir)
    if not character or not character.get("identity"):
        return None
    path = _library_dir(library_dir) / character["key"] / character["identity"]
    if not path.exists():
        logger.warning(f"{key}: character.yaml lists {character['identity']} but the file is missing")
        return None
    return path


def visual_anchor_text(key: str, library_dir=None) -> str:
    """Return the locked visual anchors as one prompt-ready line, e.g.
    'MORDECHAI: older man...; full gray-brown beard; ...'. Empty string if unknown."""
    character = load_character(key, library_dir)
    if not character:
        return ""
    anchors = "; ".join(character.get("visual_anchors", []))
    return f"{character['name_en'].upper()}: {anchors}"


def validate_character(character: dict) -> list:
    """Return a list of problems with one character.yaml (empty list = OK)."""
    problems = []
    key = character.get("key", "?")
    for field in REQUIRED_FIELDS:
        if field not in character:
            problems.append(f"{key}: missing field '{field}'")
    if character.get("gender") not in VALID_GENDERS:
        problems.append(f"{key}: gender must be one of {sorted(VALID_GENDERS)}")
    if character.get("role") not in VALID_ROLES:
        problems.append(f"{key}: role must be one of {sorted(VALID_ROLES)}")
    if not character.get("visual_anchors"):
        problems.append(f"{key}: needs at least one visual anchor")
    return problems


def legacy_design(key: str, library_dir=None):
    """Build an old-style CHARACTER_DESIGNS dict (name, description, key_features,
    style_prompt) from the library, so older helpers keep working without a second
    copy of the character data."""
    character = load_character(key, library_dir)
    if not character:
        return None
    anchors = character.get("visual_anchors", [])
    design = {
        "name": character["name_en"],
        "name_he": character["name_he"],
        "description": ". ".join(a[0].upper() + a[1:] for a in anchors) + ".",
        "key_features": list(anchors),
        "style_prompt": f"{character['name_en']}: {', '.join(anchors)}",
    }
    if character.get("role") == "villain":
        design["villain"] = True
    return design
