/**
 * Export page for rendering a single card FRONT at full print resolution.
 * URL: /export/{deckId}/{cardId}
 *
 * Renders the card front at exactly 1500x2100 pixels (5x7 @ 300 DPI).
 */

import { getDeck } from '@/lib/api';
import { CardFactory } from '@/components/cards/CardFactory';
import { notFound } from 'next/navigation';
import fs from 'fs';
import path from 'path';
import { DEFAULT_LAYOUT_CONFIG, LayoutConfig } from '@/types/editor';

interface PageProps {
  params: Promise<{ deckId: string; cardId: string }>;
}

export default async function ExportCardPage({ params }: PageProps) {
  const { deckId, cardId } = await params;
  const deck = await getDeck(deckId);

  if (!deck) {
    return notFound();
  }

  const card = deck.cards.find((c) => c.card_id === cardId);
  if (!card) {
    return notFound();
  }

  // Read Layout Config from disk
  let config: LayoutConfig = DEFAULT_LAYOUT_CONFIG;
  try {
    const configPath = path.join(process.cwd(), 'layout_settings.json');
    if (fs.existsSync(configPath)) {
      config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    }
  } catch (e) {
    console.error('Failed to load layout config', e);
  }

  // Get deck display name
  const deckName = (deck as any).parasha_en || (deck as any).holiday_en || deckId;

  return (
    <div
      style={{
        width: '1500px',
        height: '2100px',
        backgroundColor: 'white',
        overflow: 'hidden',
      }}
    >
      <CardFactory card={card} deckId={deckId} deckName={deckName} config={config} side="front" />
    </div>
  );
}
