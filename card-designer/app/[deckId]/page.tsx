
import { getDeck } from '@/lib/api';
import { CardFactory } from '@/components/cards/CardFactory';
import { CardGrid } from '@/components/layout/CardGrid';
import { ExportControls } from '@/components/ui/ExportControls';
import { notFound } from 'next/navigation';

interface PageProps {
  params: Promise<{ deckId: string }>;
}

import fs from 'fs';
import path from 'path';
import { DEFAULT_LAYOUT_CONFIG, LayoutConfig } from '@/types/editor';

// ... imports

export default async function DeckPage({ params }: PageProps) {
  const { deckId } = await params;
  const deck = await getDeck(deckId);
  
  // Read Layout Config from disk
  let config: LayoutConfig = DEFAULT_LAYOUT_CONFIG;
  try {
    const configPath = path.join(process.cwd(), 'layout_settings.json');
    if (fs.existsSync(configPath)) {
      config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    }
  } catch (e) {
    console.error("Failed to load layout config", e);
  }

  if (!deck) {
    return notFound();
  }

  return (
    <div className="min-h-screen bg-slate-100 pb-20">
      <header className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between">
           <div>
             <h1 className="text-2xl font-bold text-slate-900">{deck.parasha_en} / {deck.parasha_he}</h1>
             <p className="text-sm text-slate-500">{deck.ref} • {deck.emotional_core}</p>
           </div>
           <div className="text-sm font-medium px-3 py-1 bg-slate-100 rounded-full">
             {deck.cards.length} Cards
           </div>
        </div>
      </header>
      
      <main className="max-w-[1920px] mx-auto p-8">
        <CardGrid>
          {deck.cards.map((card) => (
             <div key={card.card_id} className="flex flex-col gap-3 items-center">
                <CardFactory card={card} deckId={deckId} config={config} />
                <div className="text-center w-full flex items-center justify-between px-2">
                  <span className="text-xs font-mono text-gray-400">{card.card_id}</span>
                  <ExportControls cardId={card.card_id} />
                </div>
             </div>
          ))}
        </CardGrid>
      </main>
    </div>
  );
}
