/**
 * CardFactory - renders one side of one card on its sheet of paper.
 * Every card type uses the same CardFront / CardBack; the per-type
 * differences live in lib/cardTypes.ts.
 */
import React from 'react';
import { LoadedCard, LoadedDeck } from '@/types/card';
import { CARD_TYPES } from '@/lib/cardTypes';
import { CardFrame } from './CardFrame';
import { CardFront } from './CardFront';
import { CardBack } from './CardBack';

interface CardFactoryProps {
  card: LoadedCard;
  deck: LoadedDeck;
  side?: 'front' | 'back';
  format?: string; // 'letter' (default) or '5x7'
}

export function CardFactory({ card, deck, side = 'front', format }: CardFactoryProps) {
  return (
    <CardFrame format={format} color={CARD_TYPES[card.card_type].color}>
      {side === 'front' ? <CardFront card={card} deck={deck} /> : <CardBack card={card} deck={deck} />}
    </CardFrame>
  );
}
