/**
 * Print view: one sheet per page, exactly the paper size, used by
 * scripts/export-deck.ts for both the PDF and the PNGs.
 *
 * URL: /print/{deckId}?format=letter|5x7&side=both|front|back&card=story_1
 *
 * Page order for "both" is front1, back1, front2, back2... so a duplex
 * printer (flip on long edge) puts each back behind its own front.
 */
import { notFound } from 'next/navigation';
import { getDeck } from '@/lib/api';
import { getFormat } from '@/lib/formats';
import { CardFactory } from '@/components/cards/CardFactory';

interface PageProps {
  params: Promise<{ deckId: string }>;
  searchParams: Promise<{ format?: string; side?: string; card?: string }>;
}

export const dynamic = 'force-dynamic';

export default async function PrintPage({ params, searchParams }: PageProps) {
  const { deckId } = await params;
  const query = await searchParams;
  const { id: format, format: f } = getFormat(query.format);
  const deck = await getDeck(deckId);
  if (!deck) return notFound();

  const sides: ('front' | 'back')[] =
    query.side === 'front' ? ['front'] : query.side === 'back' ? ['back'] : ['front', 'back'];
  const cards = query.card ? deck.cards.filter((c) => c.card_id === query.card) : deck.cards;
  const [w, h] = f.page_in;

  return (
    <div className="pp-print" style={{ width: `${w}in` }}>
      {/* Tell the browser's print engine the exact paper size, with no margins */}
      <style>{`@page { size: ${w}in ${h}in; margin: 0; } html, body { margin: 0; background: #fff; }`}</style>
      {cards.flatMap((card) =>
        sides.map((side) => (
          <div
            key={`${card.card_id}-${side}`}
            className="pp-print-page"
            data-card={card.card_id}
            data-side={side}
            style={{ width: `${w}in`, height: `${h}in` }}
          >
            <CardFactory card={card} deck={deck} side={side} format={format} />
          </div>
        ))
      )}
    </div>
  );
}
