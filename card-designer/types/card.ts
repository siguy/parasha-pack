/**
 * Deck v3 types. These mirror schemas/deck.v3.schema.json exactly.
 * If you change one, change the other.
 */

export type CardType = 'anchor' | 'spotlight' | 'story' | 'connection' | 'tradition' | 'power_word' | 'home';

export type AskType = 'recall' | 'wh' | 'open' | 'distancing' | 'nonverbal';

export type FaceKey = 'happy' | 'proud' | 'calm' | 'excited' | 'scared' | 'brave' | 'sad' | 'surprised';

export interface Hebrew {
  word: string;
  translit: string;
  meaning: string;
  note?: string;
  gesture?: string;
}

export interface Ask {
  text: string;
  type: AskType;
}

export interface GuideRef {
  page: number;
  note?: string;
}

export interface TrioItem {
  big: string;
  line1: string;
  line2: string;
}

export interface TryAtHome {
  text: string;
  tag: 'shabbat-friendly' | 'before-shabbat';
}

/** The teacher side of every card except the home card. */
export interface StandardBack {
  objective: string;
  title_he?: string;
  say: string; // **bold** = read aloud, [cue] = action chip, \n = line break
  ask: Ask[];
  hebrew?: Hebrew;
  minutes: number;
  core: boolean;
  transition: string;
  guide_ref?: GuideRef;
  trio?: TrioItem[]; // power_word
  faces?: FaceKey[]; // connection
}

export interface HomeBack {
  objective: string;
  shabbat_question: { en: string; he: string };
  hebrew?: Hebrew;
  try_at_home: TryAtHome[];
  transition: string;
}

/** Teacher-guide booklet content. Not printed on the card itself. */
export interface Guide {
  pshat: { text: string; refs: string[] };
  sages: { text: string; source: string }[];
  hard_questions: { q: string; answer: string; redirect: string }[];
  adapt: { see: string; do: string; join: string };
  extend: string;
  tip: string;
}

interface CardBase {
  card_id: string;
  title_en: string;
  title_he: string;
  characters_in_scene: string[];
  image_prompt: string;
  image_path: string;
  sequence_number?: number;
  hebrew_keyword?: { word: string; translit: string; meaning: string };
  guide: Guide;
}

export type StandardCard = CardBase & { card_type: Exclude<CardType, 'home'>; back: StandardBack };
export type HomeCard = CardBase & { card_type: 'home'; back: HomeBack };
export type Card = StandardCard | HomeCard;

export interface WeekDay {
  day: number;
  label: string;
  cards: string[];
}

/** standard = 4 story cards (3 holiday); sequence = one story card per item (src/deck_pattern.py) */
export type DeckPattern = 'standard' | 'sequence';

export interface Deck {
  id: string;
  version: '3.0';
  parasha_en: string;
  parasha_he: string;
  holiday?: boolean;
  ref?: string;
  deck_pattern?: DeckPattern;
  story_cards?: number;
  value: { en: string; he: string; kid_phrase: string; gesture: string };
  palette: string[];
  web_theme: { primary: string; secondary: string; accent: string; wash: string };
  story_world: string;
  week_plan: WeekDay[];
  cards: Card[];
}

/** A card as the app uses it: plus the URL of its art, or null if no art exists yet. */
export type LoadedCard = Card & { image_url: string | null };

export interface LoadedDeck extends Omit<Deck, 'cards'> {
  cards: LoadedCard[];
}
