
export interface BaseCardData {
  card_id: string;
  title_en?: string; // Made optional as some cards might not use it directly in the same way
  title_he?: string; // Made optional
  border_color?: string;
  image_path?: string;
  teacher_script?: string;
  sequence_number?: number;
}

export interface AnchorCardData extends BaseCardData {
  card_type: 'anchor';
  hebrew_title?: string; // From CARD_DESIGN.md
  title_he?: string; // Keep for backward compatibility if needed, or prefer hebrew_title
  // Back fields
  emotional_hook_he?: string;
}

export interface SpotlightCardData extends BaseCardData {
  card_type: 'spotlight';
  hebrew_name?: string;
  english_name?: string;
  emotion_word_en?: string;
  emotion_word_he?: string;
  // Back fields
  character_name_he?: string;
  character_name_en?: string;
  emotion_label_he?: string;
  character_description_he?: string;
  teaching_moment_en?: string;
}

export interface StoryCardData extends BaseCardData {
  card_type: 'story';
  hebrew_key_word?: string;
  hebrew_key_word_nikud?: string;
  english_key_word?: string;
  english_description?: string;
  roleplay_prompt?: string;
  // Back fields
  description_he?: string;
}

export interface ConnectionCardData extends BaseCardData {
  card_type: 'connection';
  emojis?: string[];
  // Back fields
  questions?:Array<{
      question_he: string;
      question_en?: string;
  }>;
  feeling_faces?: any[]; // details not fully specified in snippet
}

export interface PowerWordCardData extends BaseCardData {
  card_type: 'power_word';
  hebrew_word?: string;
  english_meaning?: string;
  // Back fields
  hebrew_word_nikud?: string;
  transliteration?: string;
  kid_friendly_explanation_he?: string;
  kid_friendly_explanation_en?: string;
  example_sentence_he?: string;
  example_sentence_en?: string;
}

export interface TraditionCardData extends BaseCardData {
  card_type: 'tradition';
  hebrew_title?: string;
  english_title?: string;
  // Back fields
  story_connection_he?: string;
  practice_description_he?: string;
  child_action_he?: string;
  hebrew_term?: string;
}

export type CardData = 
  | AnchorCardData 
  | SpotlightCardData 
  | StoryCardData 
  | ConnectionCardData 
  | PowerWordCardData 
  | TraditionCardData;

export interface DeckData {
  parasha_en: string;
  parasha_he: string;
  ref: string;
  border_color: string;
  emotional_core?: string;
  cards: CardData[];
}
