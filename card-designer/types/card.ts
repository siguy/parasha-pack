
export interface BaseCardData {
  card_id: string;
  title_en?: string;
  title_he?: string;
  border_color?: string;
  image_path?: string;
  teacher_script?: string;
  sequence_number?: number;
  // SAY/DO/ASK/TIP back fields
  teacher_tip?: string;
  transition_line?: string;
  discussion_prompts?: string[];
}

export interface AnchorCardData extends BaseCardData {
  card_type: 'anchor';
  hebrew_title?: string;
  title_he?: string;
  emotional_hook_en?: string;
  emotional_hook_he?: string;
}

export interface SpotlightCardData extends BaseCardData {
  card_type: 'spotlight';
  hebrew_name?: string;
  english_name?: string;
  emotion_word_en?: string;
  emotion_word_he?: string;
  character_name_he?: string;
  character_name_en?: string;
  emotion_label_en?: string;
  emotion_label_he?: string;
  character_description_en?: string;
  character_description_he?: string;
  teaching_moment_en?: string;
}

export interface StoryCardData extends BaseCardData {
  card_type: 'story';
  hebrew_key_word?: string;
  hebrew_key_word_nikud?: string;
  english_key_word?: string;
  english_description?: string;
  description_en?: string;
  roleplay_prompt?: string;
  description_he?: string;
}

export interface ConnectionCardData extends BaseCardData {
  card_type: 'connection';
  emojis?: string[];
  torah_talk_instruction?: string;
  questions?: Array<{
    question_he?: string;
    question_en?: string;
    question_type?: string;
  }>;
  feeling_faces?: Array<{
    emoji: string;
    label_en?: string;
    label_he?: string;
  }>;
}

export interface PowerWordCardData extends BaseCardData {
  card_type: 'power_word';
  hebrew_word?: string;
  english_meaning?: string;
  hebrew_word_nikud?: string;
  transliteration?: string;
  kid_friendly_explanation_he?: string;
  kid_friendly_explanation_en?: string;
  example_sentence_he?: string;
  example_sentence_en?: string;
  pronunciation_guide?: string;
}

export interface TraditionCardData extends BaseCardData {
  card_type: 'tradition';
  hebrew_title?: string;
  english_title?: string;
  story_connection_en?: string;
  story_connection_he?: string;
  practice_description_en?: string;
  practice_description_he?: string;
  child_action_en?: string;
  child_action_he?: string;
  hebrew_term?: string;
  hebrew_term_meaning?: string;
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
