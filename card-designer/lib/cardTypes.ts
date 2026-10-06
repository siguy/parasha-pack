/**
 * Per-card-type settings: label, color, and which sections the back shows.
 *
 * Colors are the v3 palette: every one passes WCAG AA contrast (>= 4.5:1)
 * with white text and on the cream back. Each type also has its own icon,
 * so color is never the only way to tell types apart.
 */
import { CardType } from '@/types/card';

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
