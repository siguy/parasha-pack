/**
 * PowerWordCardBack - Teacher content for Power Word (vocabulary) cards
 *
 * SAY: teacher_script
 * DO: pronunciation_guide
 * ASK: discussion_prompts
 * TIP: teacher_tip
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
        {/* Compact Title Line with Hebrew Word + Meaning */}
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-bold text-slate-800 leading-tight">
            {card.title_en}
          </h2>
          {hebrewWord && (
            <span className="font-hebrew text-2xl font-bold text-slate-700">
              {hebrewWord}
            </span>
          )}
        </div>

        <div className="flex-1 flex flex-col gap-2.5 min-h-0">
          {/* SAY THIS - Teacher Script */}
          <BackSection
            icon="💬"
            label="Say This"
            borderColor={borderColor}
            large
          >
            <p className="text-slate-700">{card.teacher_script}</p>
          </BackSection>

          {/* DO THIS - Pronunciation Guide */}
          {card.pronunciation_guide && (
            <BackSection
              icon="🎯"
              label="Do This"
              borderColor={borderColor}
              tintColor={`${borderColor}10`}
            >
              <p className="text-slate-700 font-medium text-lg">
                {card.pronunciation_guide}
              </p>
              {englishMeaning && (
                <p className="text-slate-500 text-sm mt-1">
                  Meaning: {englishMeaning}
                </p>
              )}
            </BackSection>
          )}

          {/* ASK THIS - Discussion Prompts */}
          {card.discussion_prompts && card.discussion_prompts.length > 0 && (
            <BackSection
              icon="❓"
              label="Ask This"
              borderColor={borderColor}
              tintColor="#0074d915"
            >
              <ul className="text-slate-700 space-y-1.5">
                {card.discussion_prompts.map((q, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-slate-400 flex-shrink-0">•</span>
                    <span>{q}</span>
                  </li>
                ))}
              </ul>
            </BackSection>
          )}

          {/* TIP */}
          {card.teacher_tip && (
            <BackSection
              icon="💡"
              label="Tip"
              borderColor={borderColor}
              tintColor="#f59e0b15"
            >
              <p className="text-slate-700">{card.teacher_tip}</p>
            </BackSection>
          )}
        </div>
      </CardBackFrame>
    </div>
  );
}
