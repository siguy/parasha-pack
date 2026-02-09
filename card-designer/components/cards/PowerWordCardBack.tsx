/**
 * PowerWordCardBack - Teacher content for Power Word (vocabulary) cards
 *
 * Displays:
 * - Hebrew word with nikud (large)
 * - Transliteration
 * - English meaning
 * - Kid-friendly explanation (Hebrew + English)
 * - Example sentence (Hebrew + English)
 * - Teacher script
 */
'use client';

import React from 'react';
import { PowerWordCardData } from '@/types/card';
import { CardBackFrame } from './CardBackFrame';

interface PowerWordCardBackProps {
  card: PowerWordCardData;
  deckName: string;
}

export function PowerWordCardBack({ card, deckName }: PowerWordCardBackProps) {
  const borderColor = card.border_color || '#2ecc40';

  // Get fields
  const hebrewWord = card.hebrew_word_nikud || card.hebrew_word;
  const transliteration = card.transliteration;
  const englishMeaning = card.english_meaning;
  const explanationEn = card.kid_friendly_explanation_en;
  const explanationHe = card.kid_friendly_explanation_he;
  const exampleEn = card.example_sentence_en;
  const exampleHe = card.example_sentence_he;

  return (
    <div id={`card-${card.card_id}-back`} className="w-full h-full">
      <CardBackFrame
        cardType="power_word"
        deckName={deckName}
        borderColor={borderColor}
      >
        {/* Large Hebrew Word */}
        <div className="text-center mb-4">
          <h1 className="font-black font-hebrew text-6xl text-slate-800 leading-tight mb-2">
            {hebrewWord}
          </h1>
          {transliteration && (
            <p className="text-2xl text-slate-500 italic mb-1">
              {transliteration}
            </p>
          )}
          <div
            className="inline-block px-6 py-2 rounded-full text-white font-bold text-xl"
            style={{ backgroundColor: borderColor }}
          >
            {englishMeaning}
          </div>
        </div>

        <div className="border-t border-slate-300 mb-4" />

        {/* Kid-Friendly Explanation */}
        {(explanationEn || explanationHe) && (
          <div className="mb-4">
            <h3 className="font-bold text-slate-500 text-xs uppercase tracking-wider mb-2">
              What Does It Mean?
            </h3>
            {explanationEn && (
              <p className="text-slate-700 leading-relaxed mb-2">
                {explanationEn}
              </p>
            )}
            {explanationHe && (
              <p className="text-slate-600 font-hebrew leading-relaxed text-sm" dir="rtl">
                {explanationHe}
              </p>
            )}
          </div>
        )}

        {/* Example Sentence */}
        {(exampleEn || exampleHe) && (
          <div
            className="rounded-xl p-4 mb-4"
            style={{ backgroundColor: `${borderColor}15` }}
          >
            <h3 className="font-bold text-slate-700 text-sm mb-2">
              Use It In A Sentence
            </h3>
            {exampleEn && (
              <p className="text-slate-700 italic mb-2">
                "{exampleEn}"
              </p>
            )}
            {exampleHe && (
              <p className="text-slate-600 font-hebrew italic text-sm" dir="rtl">
                "{exampleHe}"
              </p>
            )}
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
