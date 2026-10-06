/**
 * Deck viewer: every card's front and back side by side, on the chosen paper.
 * URL: /{deckId}            letter (default)
 *      /{deckId}?format=5x7 vendor 5x7 with bleed
 */
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getDeck } from '@/lib/api';
import { getFormat } from '@/lib/formats';
import { CardFactory } from '@/components/cards/CardFactory';
import formats from '@/print_formats.json';

interface PageProps {
  params: Promise<{ deckId: string }>;
  searchParams: Promise<{ format?: string }>;
}

export const dynamic = 'force-dynamic';

export default async function DeckPage({ params, searchParams }: PageProps) {
  const { deckId } = await params;
  const { id: format } = getFormat((await searchParams).format);
  const deck = await getDeck(deckId);
  if (!deck) return notFound();

  return (
    <div className="min-h-screen bg-[#e7e2d9] pb-20 text-slate-800">
      <header className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">{deck.parasha_en} / {deck.parasha_he}</h1>
            <p className="text-sm text-slate-500">{deck.ref} • {deck.value.en} • {deck.cards.length} cards</p>
          </div>
          <nav className="flex gap-2 text-sm font-semibold">
            {Object.keys(formats.formats).map((f) => (
              <Link
                key={f}
                href={`/${deckId}?format=${f}`}
                className={`px-3 py-1 rounded-full ${f === format ? 'bg-slate-800 text-white' : 'bg-slate-100'}`}
              >
                {f}
              </Link>
            ))}
            <Link href={`/print/${deckId}?format=${format}`} className="px-3 py-1 rounded-full bg-slate-100">
              print view
            </Link>
          </nav>
        </div>
      </header>

      <main className="max-w-[1400px] mx-auto p-8 grid gap-10" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(560px, 1fr))' }}>
        {deck.cards.map((card) => (
          <section key={card.card_id}>
            <div className="grid grid-cols-2 gap-3">
              <div className="shadow-md"><CardFactory card={card} deck={deck} side="front" format={format} /></div>
              <div className="shadow-md"><CardFactory card={card} deck={deck} side="back" format={format} /></div>
            </div>
            <p className="text-xs font-mono text-slate-500 mt-2">{card.card_id}</p>
          </section>
        ))}
      </main>
    </div>
  );
}
