#!/bin/bash
# Sync deck data from decks/{id}/ to card-designer/content/{id}/
# Source of truth is always decks/{id}/deck.json
#
# Usage: ./sync-deck.sh purim

set -e

if [ -z "$1" ]; then
  echo "Usage: ./sync-deck.sh <deck-id>"
  echo "Example: ./sync-deck.sh purim"
  exit 1
fi

DECK_ID="$1"
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

# Sync references/ directory if it exists
if [ -d "${SRC}/references" ]; then
  mkdir -p "${DEST}/references"
  cp -r "${SRC}/references/"* "${DEST}/references/" 2>/dev/null || true
fi

echo "Synced ${SRC} → ${DEST}"
