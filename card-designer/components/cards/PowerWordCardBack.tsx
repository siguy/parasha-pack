/**
 * PowerWordCardBack - Teacher content for Power Word (vocabulary) cards
 *
 * Teacher's Script: teacher_script (grows to fill)
 * Act it Out: pronunciation_guide
 * Ask: discussion_prompts (optional)
 * Tip: teacher_tip
 */
'use client';

import React from 'react';
import { PowerWordCardData } from '@/types/card';
import { CardBackFrame } from './CardBackFrame';
import { BackSection } from './BackSection';

interface PowerWordCardBackProps {
  card: PowerWordCardData;
  deckName: string;
}

export function PowerWordCardBack({ card, deckName }: PowerWordCardBackProps) {
  const borderColor = card.border_color || '#2ecc40';
  const hebrewWord = card.hebrew_word_nikud || card.hebrew_word;
  const englishMeaning = card.english_meaning;

  return (
    <div id={`card-${card.card_id}-back`} className="w-full h-full">
      <CardBackFrame
        cardType="power_word"
        deckName={deckName}
        borderColor={borderColor}
        transitionLine={card.transition_line}
      >
        {/* Card Title - 18pt + Hebrew Word */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-[75px] font-bold text-slate-800 leading-tight">
            {card.title_en}
          </h2>
          {hebrewWord && (
            <span className="font-hebrew text-[100px] font-bold text-slate-700">
              {hebrewWord}
            </span>
          )}
        </div>

        {/* Teacher's Script (grows to fill) */}
        <BackSection
          icon="💬"
          label="Teacher's Script"
          borderColor={borderColor}
          grow
        >
          <p className="text-slate-700">{card.teacher_script}</p>
        </BackSection>

        {/* Act it Out - Pronunciation Guide */}
        {card.pronunciation_guide && (
          <BackSection
            icon="🎭"
            label="Act it Out"
            borderColor={borderColor}
            tintColor={`${borderColor}15`}
          >
            <p className="text-slate-700 font-bold text-[67px]">
              {card.pronunciation_guide}
            </p>
            {englishMeaning && (
              <p className="text-slate-500 text-[50px] mt-2">
                Meaning: {englishMeaning}
              </p>
            )}
          </BackSection>
        )}

        {/* Discussion Prompts (optional) */}
        {card.discussion_prompts && card.discussion_prompts.length > 0 && (
          <BackSection
            icon="❓"
            label="Ask"
            borderColor={borderColor}
            tintColor="#0074d920"
          >
            <ul className="text-slate-700 space-y-2">
              {card.discussion_prompts.map((q, i) => (
                <li key={i} className="flex gap-3">
                  <span className="text-slate-400 flex-shrink-0">•</span>
                  <span>{q}</span>
                </li>
              ))}
            </ul>
          </BackSection>
        )}

        {/* Tip */}
        {card.teacher_tip && (
          <BackSection
            icon="💡"
            label="Tip"
            borderColor={borderColor}
            tintColor="#f59e0b20"
          >
            <p className="text-slate-700">{card.teacher_tip}</p>
          </BackSection>
        )}
      </CardBackFrame>
    </div>
  );
}
