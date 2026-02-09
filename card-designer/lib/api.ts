/**
 * API utilities for loading deck data and image paths.
 *
 * Image flow:
 *   - AI generates images to raw/{card_id}.png (no text)
 *   - Card Designer loads raw images and renders text overlay in React
 *   - Export saves final composited images to images/{card_id}.png
 */
import fs from 'fs/promises';
import path from 'path';
import { DeckData } from '@/types/card';

const DECKS_DIR = path.join(process.cwd(), 'content');

export async function getDeck(deckId: string): Promise<DeckData | null> {
  try {
    const filePath = path.join(DECKS_DIR, deckId, 'deck.json');
    const fileContent = await fs.readFile(filePath, 'utf-8');
    const data = JSON.parse(fileContent);

    // Flatten front/back data for easier consumption in components
    if (data.cards) {
      data.cards = data.cards.map((card: any) => ({
        ...card,
        ...(card.front || {}),
        ...(card.back || {}),
        // Normalize image_path to always use raw/ for Card Designer
        // (components render text overlay, export saves to images/)
        image_path: normalizeImagePath(card.image_path, card.card_id),
      }));
    }

    return data as DeckData;
  } catch (error) {
    console.error(`Error loading deck ${deckId}:`, error);
    return null;
  }
}

/**
 * Normalize image path to use raw/ directory.
 * Handles legacy images/ paths and missing paths.
 */
function normalizeImagePath(imagePath: string | undefined, cardId: string): string {
  if (!imagePath) {
    return `raw/${cardId}.png`;
  }
  // Convert images/{id}.png to raw/{id}.png
  if (imagePath.startsWith('images/')) {
    return imagePath.replace('images/', 'raw/');
  }
  return imagePath;
}

/**
 * Get the API URL for serving an image.
 * @param deckId - The deck identifier
 * @param imagePath - The image path (e.g., raw/story_1.png)
 * @param source - Optional source override ('raw' or 'images')
 */
export async function getDeckImage(
  deckId: string,
  imagePath: string,
  source?: 'raw' | 'images'
): Promise<string> {
  const params = new URLSearchParams({ deck: deckId, path: imagePath });
  if (source) {
    params.set('source', source);
  }
  return `/api/images?${params.toString()}`;
}
