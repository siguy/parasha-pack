/**
 * SpotlightCardBack - Teacher content for Spotlight (character) cards
 *
 * Displays:
 * - Character name (Hebrew + English) with emotion
 * - Character description
 * - Teaching moment (for villain/misguided cards)
 * - Teacher script
 */
'use client';

import React from 'react';
import { SpotlightCardData } from '@/types/card';
import { CardBackFrame } from './CardBackFrame';

interface SpotlightCardBackProps {
  card: SpotlightCardData;
  deckName: string;
}

export function SpotlightCardBack({ card, deckName }: SpotlightCardBackProps) {
  const borderColor = card.border_color || '#d4a84b';

  // Use various field names for compatibility
  const hebrewName = card.hebrew_name || card.character_name_he || card.title_he;
  const englishName = card.english_name || card.character_name_en || card.title_en;
  const emotionHe = card.emotion_word_he || card.emotion_label_he;
  const emotionEn = card.emotion_word_en;
  const description = card.character_description_he || (card as any).character_description_en;
  const teachingMoment = (card as any).teaching_moment_en;

  return (
    <div id={`card-${card.card_id}-back`} className="w-full h-full">
      <CardBackFrame
        cardType="spotlight"
        deckName={deckName}
        borderColor={borderColor}
      >
        {/* Title Section */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex flex-col">
            <h1 className="font-black font-hebrew text-4xl text-slate-800 leading-tight">
              {hebrewName}
            </h1>
            <h2 className="text-xl font-bold text-slate-600">
              {englishName}
            </h2>
          </div>

          {/* Emotion Badge */}
          {(emotionHe || emotionEn) && (
            <div
              className="px-4 py-2 rounded-full text-white font-bold shadow-md flex flex-col items-center"
              style={{ backgroundColor: borderColor }}
            >
              {emotionHe && (
                <span className="font-hebrew text-lg">{emotionHe}</span>
              )}
              {emotionEn && (
                <span className="text-xs uppercase tracking-wide opacity-90">{emotionEn}</span>
              )}
            </div>
          )}
        </div>

        <div className="border-t border-slate-300 mb-4" />

        {/* Character Description */}
        {description && (
          <div className="mb-4">
            <h3 className="font-bold text-slate-500 text-xs uppercase tracking-wider mb-2">
              About This Character
            </h3>
            <p className="text-slate-700 leading-relaxed">
              {description}
            </p>
          </div>
        )}

        {/* Teaching Moment (for misguided characters) */}
        {teachingMoment && (
          <div
            className="rounded-xl p-4 mb-4 border-l-4"
            style={{
              backgroundColor: `${borderColor}10`,
              borderLeftColor: borderColor,
            }}
          >
            <h3 className="font-bold text-slate-700 text-sm mb-2">
              Teaching Moment
            </h3>
            <p className="text-slate-600 italic">
              {teachingMoment}
            </p>
          </div>
        )}

        {/* Teacher Script */}
        <div className="flex-1 flex flex-col min-h-0">
          <h3 className="font-bold text-slate-500 text-xs uppercase tracking-wider mb-2">
            Teacher Script
          </h3>
          <div className="flex-1 bg-white rounded-lg p-4 shadow-inner border border-slate-200 overflow-auto">
            <p className="text-slate-700 leading-relaxed text-sm">
              {card.teacher_script}
            </p>
          </div>
        </div>
      </CardBackFrame>
    </div>
  );
}
