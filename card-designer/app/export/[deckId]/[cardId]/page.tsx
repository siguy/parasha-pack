/**
 * Export page for rendering a single card FRONT at print resolution.
 * URL: /export/{deckId}/{cardId}
 *
 * Renders at 500x700 CSS pixels — the Playwright export script captures
 * this with deviceScaleFactor:3 to produce 1500x2100 physical pixels.
 * This matches the design editor viewport where overlays were designed.
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
        width: '500px',
        height: '700px',
        backgroundColor: 'white',
        overflow: 'hidden',
      }}
    >
      <CardFactory card={card} deckId={deckId} deckName={deckName} config={config} side="front" />
    </div>
  );
}
