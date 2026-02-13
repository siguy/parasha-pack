/**
 * SpotlightCardBack - Teacher content for Spotlight (character) cards
 *
 * SAY: teacher_script
 * DO: emotion expression + teaching_moment_en
 * ASK: discussion_prompts
 * TIP: teacher_tip
 */
'use client';

import React from 'react';
import { SpotlightCardData } from '@/types/card';
import { CardBackFrame } from './CardBackFrame';
import { BackSection } from './BackSection';

interface SpotlightCardBackProps {
  card: SpotlightCardData;
  deckName: string;
}

export function SpotlightCardBack({ card, deckName }: SpotlightCardBackProps) {
  const borderColor = card.border_color || '#d4a84b';
  const englishName = card.english_name || card.character_name_en || card.title_en;
  const emotionEn = card.emotion_word_en || card.emotion_label_en;

  // Build the DO THIS content
  const doContent: string[] = [];
  if (emotionEn) {
    doContent.push(`Show children a "${emotionEn.toLowerCase()}" expression and have them mirror it.`);
  }
  if (card.teaching_moment_en) {
    doContent.push(card.teaching_moment_en);
  }

  return (
    <div id={`card-${card.card_id}-back`} className="w-full h-full">
      <CardBackFrame
        cardType="spotlight"
        deckName={deckName}
        borderColor={borderColor}
        transitionLine={card.transition_line}
      >
        {/* Compact Title Line with Emotion Badge */}
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-2xl font-bold text-slate-800 leading-tight">
            {englishName}
          </h2>
          {emotionEn && (
            <span
              className="px-3 py-1 rounded-full text-white text-sm font-bold uppercase tracking-wide"
              style={{ backgroundColor: borderColor }}
            >
              {emotionEn}
            </span>
          )}
        </div>

        <div className="flex flex-col gap-4">
          {/* SAY THIS - Teacher Script */}
          <BackSection
            icon="💬"
            label="Say This"
            borderColor={borderColor}
            large
          >
            <p className="text-slate-700">{card.teacher_script}</p>
          </BackSection>

          {/* DO THIS - Emotion + Teaching Moment */}
          {doContent.length > 0 && (
            <BackSection
              icon="🎯"
              label="Do This"
              borderColor={borderColor}
              tintColor={`${borderColor}10`}
            >
              {doContent.map((text, i) => (
                <p key={i} className={`text-slate-700 ${i === 0 ? 'font-medium' : 'italic mt-1.5'}`}>
                  {text}
                </p>
              ))}
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
