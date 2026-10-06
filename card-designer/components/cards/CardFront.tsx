/**
 * CardFront - what the children see (v3), for every card type.
 *
 *   full-bleed art (or a palette placeholder while the art doesn't exist yet)
 *   dark gradient band at the top with the title (Fredoka) + Hebrew (Heebo)
 *   type chip bottom-left, story number top-right, Hebrew keyword bottom-right
 *
 * The home card has no AI art: if raw/home_1.png is missing it gets its own
 * simple themed design (HomeFront).
 */
/* eslint-disable @next/next/no-img-element -- plain <img> so Playwright export captures the full-size art */
import React from 'react';
import { LoadedCard, LoadedDeck } from '@/types/card';
import { CARD_TYPES } from '@/lib/cardTypes';
import { TypeIcon } from './icons';

/** Soft gradient in the deck's own colors, shown until the real art is generated. */
function placeholderBackground(palette: string[]): string {
  const [deep, gold, green, sky, cream] = palette;
  return [
    `radial-gradient(ellipse 60% 40% at 50% 62%, ${cream} 0%, ${gold} 30%, transparent 70%)`,
    `linear-gradient(to bottom, ${deep} 0%, ${deep} 35%, ${sky} 75%, ${green} 100%)`,
  ].join(', ');
}

function HomeFront({ card, deck, color }: { card: LoadedCard; deck: LoadedDeck; color: string }) {
  return (
    <div className="pp-front home" id={`card-${card.card_id}`} style={{ '--c': color } as React.CSSProperties}>
      <div className="house"><TypeIcon type="home" /></div>
      <div className="big">Take Home</div>
      <div className="deck">This week: {deck.parasha_en}</div>
      <div className="deck-he">{deck.parasha_he}</div>
      <div className="foot">PARASHA PACK · SHABBAT SHALOM</div>
    </div>
  );
}

export function CardFront({ card, deck }: { card: LoadedCard; deck: LoadedDeck }) {
  const type = CARD_TYPES[card.card_type];
  if (card.card_type === 'home' && !card.image_url) {
    return <HomeFront card={card} deck={deck} color={type.color} />;
  }

  const number = card.card_type === 'story' ? card.sequence_number : undefined;

  return (
    <div
      className={`pp-front${number ? ' has-num' : ''}`}
      id={`card-${card.card_id}`}
      style={{ '--c': type.color } as React.CSSProperties}
    >
      {card.image_url ? (
        <img className="art" src={card.image_url} alt={card.title_en} />
      ) : (
        <>
          <div className="art" style={{ background: placeholderBackground(deck.palette) }} />
          <div className="placeholder-note">art coming soon</div>
        </>
      )}
      <div className="shade" />
      <div className="ttl">
        <div className="en">{card.title_en}</div>
        <div className="he">{card.title_he}</div>
      </div>
      {number && <div className="num">{number}</div>}
      <div className="chip">
        <TypeIcon type={card.card_type} />
        {type.label}
      </div>
      {card.card_type === 'story' && card.hebrew_keyword && (
        <div className="kw">
          {card.hebrew_keyword.word}
          <small>
            {card.hebrew_keyword.translit ? `${card.hebrew_keyword.translit} · ` : ''}
            {card.hebrew_keyword.meaning}
          </small>
        </div>
      )}
    </div>
  );
}
