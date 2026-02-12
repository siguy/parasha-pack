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
      data.cards = data.cards.map((card: any) => {
        const merged = {
          ...card,
          ...(card.front || {}),
          ...(card.back || {}),
          // Normalize image_path to always use raw/ for Card Designer
          // (components render text overlay, export saves to images/)
          image_path: normalizeImagePath(card.image_path, card.card_id),
        };
        return normalizeFieldNames(merged);
      });
    }

    return data as DeckData;
  } catch (error) {
    console.error(`Error loading deck ${deckId}:`, error);
    return null;
  }
}

/**
 * Map legacy deck.json field names to what React components expect.
 * Only sets a field if not already present (front/back data takes priority).
 */
function normalizeFieldNames(card: any): any {
  const normalized = { ...card };

  // Spotlight: character_name → hebrew_name/english_name, emotion_label → emotion_word
  if (card.card_type === 'spotlight') {
    if (!normalized.hebrew_name && normalized.character_name_he) {
      normalized.hebrew_name = normalized.character_name_he;
    }
    if (!normalized.english_name && normalized.character_name_en) {
      normalized.english_name = normalized.character_name_en;
    }
    if (!normalized.emotion_word_he && normalized.emotion_label_he) {
      normalized.emotion_word_he = normalized.emotion_label_he;
    }
    if (!normalized.emotion_word_en && normalized.emotion_label_en) {
      normalized.emotion_word_en = normalized.emotion_label_en;
    }
  }

  // Story: description_en → english_description
  if (card.card_type === 'story') {
    if (!normalized.english_description && normalized.description_en) {
      normalized.english_description = normalized.description_en;
    }
  }

  // Connection: feeling_faces[].emoji → emojis[]
  if (card.card_type === 'connection') {
    if (!normalized.emojis && normalized.feeling_faces) {
      normalized.emojis = normalized.feeling_faces
        .map((f: any) => f.emoji)
        .filter(Boolean);
    }
  }

  // Tradition/Anchor: title_he → hebrew_title, title_en → english_title
  if (card.card_type === 'tradition' || card.card_type === 'anchor') {
    if (!normalized.hebrew_title && normalized.title_he) {
      normalized.hebrew_title = normalized.title_he;
    }
    if (!normalized.english_title && normalized.title_en) {
      normalized.english_title = normalized.title_en;
    }
  }

  return normalized;
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
