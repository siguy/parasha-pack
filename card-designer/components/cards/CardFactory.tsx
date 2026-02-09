'use client';

import React from 'react';
import { CardData } from '@/types/card';
import { AnchorCard } from './AnchorCard';
import { SpotlightCard } from './SpotlightCard';
import { ConnectionCard } from './ConnectionCard';
import { PowerWordCard } from './PowerWordCard';
import { TraditionCard } from './TraditionCard';
import { StoryCard } from './StoryCard';
import { CardFrame } from './CardFrame';
import { LayoutConfig } from '@/types/editor';

// Card Back components
import { AnchorCardBack } from './AnchorCardBack';
import { SpotlightCardBack } from './SpotlightCardBack';
import { StoryCardBack } from './StoryCardBack';
import { ConnectionCardBack } from './ConnectionCardBack';
import { PowerWordCardBack } from './PowerWordCardBack';
import { TraditionCardBack } from './TraditionCardBack';

interface CardFactoryProps {
  card: CardData;
  deckId: string;
  deckName?: string;
  config?: LayoutConfig;
  side?: 'front' | 'back';
}

export function CardFactory({ card, deckId, deckName, config, side = 'front' }: CardFactoryProps) {
  const resolvedDeckName = deckName || deckId;

  // Render back side
  if (side === 'back') {
    switch (card.card_type) {
      case 'anchor':
        return <AnchorCardBack card={card} deckName={resolvedDeckName} />;
      case 'spotlight':
        return <SpotlightCardBack card={card} deckName={resolvedDeckName} />;
      case 'story':
        return <StoryCardBack card={card} deckName={resolvedDeckName} />;
      case 'connection':
        return <ConnectionCardBack card={card} deckName={resolvedDeckName} />;
      case 'power_word':
        return <PowerWordCardBack card={card} deckName={resolvedDeckName} />;
      case 'tradition':
        return <TraditionCardBack card={card} deckName={resolvedDeckName} />;
      default:
        return (
          <div className="flex flex-col items-center justify-center h-full p-6 text-center bg-gray-100 rounded-lg">
            <h3 className="font-bold text-xl mb-2 capitalize">{(card as any).card_type}</h3>
            <p className="text-sm text-gray-500">Unknown Card Type (back)</p>
          </div>
        );
    }
  }

  // Render front side (default)
  switch (card.card_type) {
    case 'anchor':
      return <AnchorCard card={card} deckId={deckId} config={config} />;
    case 'spotlight':
      return <SpotlightCard card={card} deckId={deckId} config={config} />;
    case 'story':
      return <StoryCard card={card} deckId={deckId} config={config} />;
    case 'connection':
      return <ConnectionCard card={card} deckId={deckId} config={config} />;
    case 'power_word':
      return <PowerWordCard card={card} deckId={deckId} config={config} />;
    case 'tradition':
      return <TraditionCard card={card} deckId={deckId} config={config} />;
    default:
      const unknownCard = card as any;
      return (
        <CardFrame borderColor={unknownCard.border_color || '#ccc'}>
           <div className="flex flex-col items-center justify-center h-full p-6 text-center">
             <h3 className="font-bold text-xl mb-2 capitalize">{unknownCard.card_type}</h3>
             <p className="text-sm text-gray-500">Unknown Card Type</p>
           </div>
        </CardFrame>
      );
  }
}
