/**
 * Export page for rendering a single card BACK at full print resolution.
 * URL: /export/{deckId}/{cardId}/back
 *
 * Renders the card back at exactly 1500x2100 pixels (5x7 @ 300 DPI).
 */

import { getDeck } from '@/lib/api';
import { CardFactory } from '@/components/cards/CardFactory';
import { notFound } from 'next/navigation';

interface PageProps {
  params: Promise<{ deckId: string; cardId: string }>;
}

export default async function ExportCardBackPage({ params }: PageProps) {
  const { deckId, cardId } = await params;
  const deck = await getDeck(deckId);

  if (!deck) {
    return notFound();
  }

  const card = deck.cards.find((c) => c.card_id === cardId);
  if (!card) {
    return notFound();
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
      <CardFactory card={card} deckId={deckId} deckName={deckName} side="back" />
    </div>
  );
}
