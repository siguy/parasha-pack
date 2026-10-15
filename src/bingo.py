"""
Bingo boards that are fair and fun: the maths part of the bingo printable.

A board is 3×3 = 9 squares. The middle square is the free space (Shabbat candles),
so each board shows 8 of the deck's 12 vocabulary pictures.

Two rules make a good classroom game:
  1. Boards must look different. Any two boards share at most 6 pictures.
  2. The game should last a little while, but not too long. We "play" 2000 pretend
     games with a computer and check that the first BINGO usually happens on call
     5–8, and that usually only one child (not half the class) wins at once.

Why "four corners" and not "three in a row"? With a free middle square, every line
through the middle needs only TWO pictures. With 10 boards in play, someone gets
two-in-a-line almost at once: the simulation says the first win comes on call 2-3.
Covering the four corners needs four pictures, and the first win lands around call 7,
with about 1.3 winners at a time. (Try it: `win_rule: line` in extras.yaml.)

We make many candidate sets of boards (each from the same seeded random generator,
so the result is the same every time for the same deck) and keep the best one.
"""

import hashlib
import logging
import random
import statistics

import numpy as np

logger = logging.getLogger("bingo")

FREE = "FREE"
CENTER = 4
# Cell numbers 0-8, left-to-right, top-to-bottom. A board wins when ANY one pattern
# of its win rule is fully covered.
LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
WIN_RULES = {
    "corners": [(0, 2, 6, 8)],          # cover the 4 corner pictures (default)
    "line": LINES,                      # classic: any row, column or diagonal
    "blackout": [(0, 1, 2, 3, 5, 6, 7, 8)],  # cover the whole board
}
WIN_RULE_TEXT = {
    "corners": "Cover all 4 corners = BINGO!",
    "line": "3 in a row = BINGO!",
    "blackout": "Cover the whole board = BINGO!",
}


def seed_for(deck_id: str) -> int:
    """A stable number from the deck id (Python's hash() changes between runs; sha256 doesn't)."""
    return int(hashlib.sha256(f"{deck_id}-bingo".encode()).hexdigest()[:12], 16)


def shared_items(board_a: list, board_b: list) -> int:
    """How many pictures two boards have in common (the free space doesn't count)."""
    return len((set(board_a) - {FREE}) & (set(board_b) - {FREE}))


def make_boards(item_ids: list, n_boards: int, max_shared: int, rng: random.Random,
                max_tries: int = 5000) -> list:
    """
    Make n_boards boards. Each is a list of 9 cells with FREE in the middle.
    Every pair of boards shares at most max_shared items. Raises ValueError if impossible.
    """
    per_board = 8
    if len(item_ids) < per_board:
        raise ValueError(f"Need at least {per_board} items, got {len(item_ids)}")
    chosen_sets = []
    tries = 0
    while len(chosen_sets) < n_boards:
        tries += 1
        if tries > max_tries:
            raise ValueError(f"Could not make {n_boards} boards sharing <= {max_shared} items")
        candidate = set(rng.sample(item_ids, per_board))
        if all(len(candidate & other) <= max_shared for other in chosen_sets):
            chosen_sets.append(candidate)
    boards = []
    for items in chosen_sets:
        cells = sorted(items)
        rng.shuffle(cells)
        boards.append(cells[:CENTER] + [FREE] + cells[CENTER:])
    return boards


def simulate(boards: list, item_ids: list, games: int, seed: int, win_rule: str = "corners") -> dict:
    """
    Play `games` pretend games. The caller draws all items in a random order.

    For each board, it wins at the call number when its first win pattern is complete.
    Returns the first-win call numbers and how many boards won on that same call.
    """
    rng = np.random.default_rng(seed)
    index = {item: i for i, item in enumerate(item_ids)}
    # call_number[g, i] = on which call (1, 2, ...) item i is drawn in game g
    order = np.argsort(rng.random((games, len(item_ids))), axis=1)
    call_number = np.empty_like(order)
    rows = np.arange(games)[:, None]
    call_number[rows, order] = np.arange(1, len(item_ids) + 1)

    board_win = np.empty((games, len(boards)), dtype=int)
    for b, board in enumerate(boards):
        line_times = []
        for line in WIN_RULES[win_rule]:
            cells = [index[board[c]] for c in line if board[c] != FREE]
            line_times.append(call_number[:, cells].max(axis=1))
        board_win[:, b] = np.min(np.stack(line_times, axis=1), axis=1)

    first_win = board_win.min(axis=1)
    winners = (board_win == first_win[:, None]).sum(axis=1)
    return {
        "games": games,
        "median_first_win": float(statistics.median(first_win.tolist())),
        "mean_first_win": float(first_win.mean()),
        "avg_simultaneous_winners": float(winners.mean()),
        "share_single_winner": float((winners == 1).mean()),
    }


def choose_boards(item_ids: list, deck_id: str, n_boards: int = 10, max_shared: int = 6,
                  games: int = 2000, candidates: int = 300,
                  target_median=(5, 8), max_avg_winners: float = 2.0,
                  win_rule: str = "corners") -> tuple:
    """
    Try `candidates` board sets and return (boards, stats) for the best one.

    "Best" = passes both targets (median first win inside target_median, average
    simultaneous winners below max_avg_winners) with the fewest simultaneous winners.
    If none passes, the closest one is returned and stats["passed"] is False.
    """
    rng = random.Random(seed_for(deck_id))
    best = None
    for number in range(candidates):
        boards = make_boards(item_ids, n_boards, max_shared, rng)
        stats = simulate(boards, item_ids, games, seed_for(deck_id) + number, win_rule)
        passed = (target_median[0] <= stats["median_first_win"] <= target_median[1]
                  and stats["avg_simultaneous_winners"] < max_avg_winners)
        # Lower score is better; failing sets always rank below passing ones
        score = (0 if passed else 1, stats["avg_simultaneous_winners"],
                 abs(stats["median_first_win"] - sum(target_median) / 2))
        if best is None or score < best[0]:
            best = (score, boards, dict(stats, passed=passed, candidate=number,
                                        candidates=candidates, win_rule=win_rule))
    _, boards, stats = best
    logger.info(f"Bingo: candidate {stats['candidate']}/{candidates} chosen — median first win "
                f"{stats['median_first_win']}, avg simultaneous winners "
                f"{stats['avg_simultaneous_winners']:.2f}, passed={stats['passed']}")
    return boards, stats
