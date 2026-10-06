/**
 * Per-card-type settings: label, color, and which sections the back shows.
 *
 * Colors are the v3 palette: every one passes WCAG AA contrast (>= 4.5:1)
 * with white text and on the cream back. Each type also has its own icon,
 * so color is never the only way to tell types apart.
 */
import { CardType, DeckPattern } from '@/types/card';

export type BackSection = 'say' | 'ask' | 'hebrew' | 'week' | 'faces' | 'trio' | 'shabbat' | 'try';

interface TypeConfig {
  label: string;
  color: string;
  /** Back sections, top to bottom. A section is skipped if the card has no data for it. */
  sections: BackSection[];
}

export const CARD_TYPES: Record<CardType, TypeConfig> = {
  anchor: { label: 'Anchor', color: '#5B2D8E', sections: ['say', 'ask', 'week'] },
  spotlight: { label: 'Spotlight', color: '#7E601A', sections: ['say', 'ask', 'hebrew'] },
  story: { label: 'Story', color: '#B83227', sections: ['say', 'ask', 'hebrew'] },
  connection: { label: 'Connection', color: '#1F5FA8', sections: ['say', 'ask', 'faces'] },
  tradition: { label: 'Tradition', color: '#0E7470', sections: ['say', 'ask', 'hebrew'] },
  power_word: { label: 'Power Word', color: '#2D7A3A', sections: ['trio', 'say', 'ask'] },
  home: { label: 'Take Home', color: '#A84B16', sections: ['shabbat', 'hebrew', 'try'] },
};

/**
 * In a sequence deck (deck_pattern: sequence, e.g. the 7 days of creation) every story card is
 * one numbered item of the text, so it reads "Day 3" instead of "Story 3".
 */
type LabelDeck = { deck_pattern?: DeckPattern };
type LabelCard = { card_type: CardType; sequence_number?: number };

const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];

/** The word on a card's type chip (front): "Day" for a sequence deck's story cards. */
export function typeLabel(card: LabelCard, deck: LabelDeck): string {
  if (card.card_type === 'story' && deck.deck_pattern === 'sequence') return 'Day';
  return CARD_TYPES[card.card_type].label;
}

/** The back's header: "Story 2" (standard) or "Day 2" (sequence); other types use their label. */
export function backHeaderLabel(card: LabelCard, deck: LabelDeck): string {
  const label = typeLabel(card, deck);
  return card.card_type === 'story' && card.sequence_number ? `${label} ${card.sequence_number}` : label;
}

/**
 * A teaching day in the week plan. A sequence deck already uses "Day N" for its story cards,
 * so its week plan says Mon..Fri instead of Day 1..5 (no "Day 1: Days 1-2" mix-ups).
 */
export function weekDayLabel(day: number, deck: LabelDeck): string {
  return deck.deck_pattern === 'sequence' ? WEEKDAYS[day - 1] ?? `Day ${day}` : `Day ${day}`;
}
