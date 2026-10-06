"""
I-spy placement: where each little picture goes on the Gan Eden background.

The I-spy page is NOT one AI picture. AI can't count ("draw exactly 4 fish" gives 3 or
6), so the answer key would be wrong. Instead we stick cut-out pictures onto an empty
background in code, like stickers on a poster. Because the code places every sticker,
it knows the exact count, and the answer key comes for free.

Placement rules (sizes in inches, on a 7.5" square scene):
  Easy       1.0-1.3" items, upright, no overlap at all (with a small gap)
  Challenge  0.6-1.2" items, turned up to ±30°, at most 15% overlap with any neighbour
Each kind of item stays in its zone: fish in the pond, birds and stars in the sky,
flowers and the snake on the grass.
"""

import logging
import math
import random

logger = logging.getLogger("ispy")

LEVELS = {
    "easy": {"size_in": (1.0, 1.3), "max_rotation": 0, "max_overlap": 0.0, "gap_in": 0.08},
    "challenge": {"size_in": (0.6, 1.2), "max_rotation": 30, "max_overlap": 0.15, "gap_in": 0.0},
}


def rotated_size(width: float, height: float, degrees: float) -> tuple:
    """Width and height of the box that holds a w×h rectangle after turning it."""
    a = math.radians(abs(degrees))
    return (width * math.cos(a) + height * math.sin(a), width * math.sin(a) + height * math.cos(a))


def overlap_fraction(a: dict, b: dict) -> float:
    """Overlap of two boxes as a share of the SMALLER box (0 = apart, 1 = one covers the other)."""
    left, right = max(a["x"], b["x"]), min(a["x"] + a["w"], b["x"] + b["w"])
    top, bottom = max(a["y"], b["y"]), min(a["y"] + a["h"], b["y"] + b["h"])
    if right <= left or bottom <= top:
        return 0.0
    return (right - left) * (bottom - top) / min(a["w"] * a["h"], b["w"] * b["h"])


def _too_close(box: dict, other: dict, gap: float, max_overlap: float) -> bool:
    if max_overlap > 0:
        return overlap_fraction(box, other) > max_overlap
    grown = {"x": box["x"] - gap, "y": box["y"] - gap, "w": box["w"] + 2 * gap, "h": box["h"] + 2 * gap}
    return overlap_fraction(grown, other) > 0


def place_items(counts: dict, zones: dict, item_zones: dict, aspects: dict, level: str,
                scene_in: float = 7.5, seed: int = 0, tries_per_item: int = 400,
                restarts: int = 60) -> list:
    """
    Place counts[item] copies of each item. Returns a list of placements:
        {"id", "x", "y", "w", "h", "angle", "art_w", "art_h", "role"}  (inches, top-left origin)
    x/y/w/h is the box AFTER rotation; art_w/art_h is the picture size before turning.
    aspects[item] = picture width / height. Raises RuntimeError if it can't fit them.
    """
    rules = LEVELS[level]
    rng = random.Random(seed)
    margin = 0.08
    for attempt in range(restarts):
        instances = [item for item, n in counts.items() for _ in range(n)]
        rng.shuffle(instances)
        placed = []
        for item in instances:
            spot = _find_spot(item, zones[item_zones[item]], aspects.get(item, 1.0), rules,
                              placed, scene_in, margin, rng, tries_per_item)
            if spot is None:
                break
            placed.append(spot)
        if len(placed) == len(instances):
            logger.info(f"I-spy {level}: placed {len(placed)} items (attempt {attempt + 1})")
            return placed
    raise RuntimeError(f"I-spy {level}: could not fit {sum(counts.values())} items after {restarts} restarts")


def _find_spot(item, zone, aspect, rules, placed, scene_in, margin, rng, tries):
    low, high = rules["size_in"]
    for _ in range(tries):
        longest = rng.uniform(low, high)
        art_w, art_h = (longest, longest / aspect) if aspect >= 1 else (longest * aspect, longest)
        angle = rng.uniform(-rules["max_rotation"], rules["max_rotation"]) if rules["max_rotation"] else 0.0
        w, h = rotated_size(art_w, art_h, angle)
        center_y = rng.uniform(zone[0] * scene_in, zone[1] * scene_in)
        center_x = rng.uniform(margin + w / 2, scene_in - margin - w / 2)
        box = {"id": item, "x": center_x - w / 2, "y": center_y - h / 2, "w": w, "h": h,
               "angle": angle, "art_w": art_w, "art_h": art_h}
        if box["y"] < margin or box["y"] + h > scene_in - margin:
            continue
        if any(_too_close(box, other, rules["gap_in"], rules["max_overlap"]) for other in placed):
            continue
        return box
    return None


def count_by_item(placements: list) -> dict:
    """{item_id: how many were placed} — this IS the answer key."""
    counts = {}
    for p in placements:
        counts[p["id"]] = counts.get(p["id"], 0) + 1
    return counts
