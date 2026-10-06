/**
 * Loads v3 decks from content/{deckId}/deck.json (copied there by ../sync-deck.sh).
 *
 * Image flow:
 *   - AI generates scene-only art to raw/{card_id}.png
 *   - The Card Designer draws the title, badges and back on top in React
 *   - The export script saves PNGs to decks/{id}/images|backs and PDFs to decks/{id}/print
 */
import fs from 'fs/promises';
import path from 'path';
import { Deck, LoadedDeck } from '@/types/card';

const CONTENT_DIR = path.join(process.cwd(), 'content');

async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

/** Returns the deck, or null if it does not exist. Throws if it is not a v3 deck. */
export async function getDeck(deckId: string): Promise<LoadedDeck | null> {
  const deckDir = path.join(CONTENT_DIR, deckId.replace(/[^a-zA-Z0-9_-]/g, ''));
  const filePath = path.join(deckDir, 'deck.json');
  if (!(await fileExists(filePath))) return null;

  const deck: Deck = JSON.parse(await fs.readFile(filePath, 'utf-8'));
  if (deck.version !== '3.0') {
    throw new Error(
      `${deckId}/deck.json is version ${deck.version ?? '?'}; the Card Designer only reads v3. ` +
        `Run: python src/migrate_v2_to_v3.py decks/${deckId}/deck.json`
    );
  }

  // Attach an image URL only when the art file really exists, so cards
  // without art can show a placeholder instead of a broken image.
  const cards = await Promise.all(
    deck.cards.map(async (card) => {
      const hasImage = await fileExists(path.join(deckDir, card.image_path));
      return { ...card, image_url: hasImage ? imageUrl(deckId, card.image_path) : null };
    })
  );
  return { ...deck, cards };
}

/** Deck ids that have a deck.json in content/. */
export async function listDecks(): Promise<string[]> {
  const entries = await fs.readdir(CONTENT_DIR, { withFileTypes: true });
  const ids: string[] = [];
  for (const entry of entries) {
    if (entry.isDirectory() && (await fileExists(path.join(CONTENT_DIR, entry.name, 'deck.json')))) {
      ids.push(entry.name);
    }
  }
  return ids.sort();
}

export function imageUrl(deckId: string, imagePath: string): string {
  return `/api/images?${new URLSearchParams({ deck: deckId, path: imagePath })}`;
}
