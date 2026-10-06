#!/bin/bash
# Sync deck data from decks/{id}/ to card-designer/content/{id}/
# Source of truth is always decks/{id}/deck.json
# Works from any directory (paths are relative to this script).
#
# Usage: ./sync-deck.sh purim

set -e

if [ -z "$1" ]; then
  echo "Usage: ./sync-deck.sh <deck-id>"
  echo "Example: ./sync-deck.sh purim"
  exit 1
fi

DECK_ID="$1"
cd "$(dirname "$0")"
SRC="decks/${DECK_ID}"
DEST="card-designer/content/${DECK_ID}"

if [ ! -f "${SRC}/deck.json" ]; then
  echo "Error: ${SRC}/deck.json not found"
  exit 1
fi

mkdir -p "${DEST}"

# Sync deck.json
cp "${SRC}/deck.json" "${DEST}/deck.json"

# Sync feedback.json if it exists
[ -f "${SRC}/feedback.json" ] && cp "${SRC}/feedback.json" "${DEST}/feedback.json"

# Sync raw/ images and references/. --delete removes files that were
# deleted from the deck, so stale images don't linger in the Card Designer.
# (raw/ copies only the PNGs, like before; prompts and logs stay in decks/.)
if [ -d "${SRC}/raw" ]; then
  rsync -a --delete --include='*.png' --exclude='*' "${SRC}/raw/" "${DEST}/raw/"
fi
if [ -d "${SRC}/references" ]; then
  rsync -a --delete "${SRC}/references/" "${DEST}/references/"
fi

echo "Synced ${SRC} → ${DEST}"
