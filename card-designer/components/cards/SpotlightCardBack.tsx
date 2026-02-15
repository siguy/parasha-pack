/**
 * SpotlightCardBack - Teacher content for Spotlight (character) cards
 *
 * Teacher's Script: teacher_script (grows to fill)
 * Act it Out: emotion expression + teaching_moment_en
 * Ask: discussion_prompts (optional)
 * Tip: teacher_tip
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

  // Build the Act it Out content
  const actContent: string[] = [];
  if (emotionEn) {
    actContent.push(`Show children a "${emotionEn.toLowerCase()}" expression and have them mirror it.`);
  }
  if (card.teaching_moment_en) {
    actContent.push(card.teaching_moment_en);
  }

  return (
    <div id={`card-${card.card_id}-back`} className="w-full h-full">
      <CardBackFrame
        cardType="spotlight"
        deckName={deckName}
        borderColor={borderColor}
        transitionLine={card.transition_line}
      >
        {/* Card Title - English + badge left, Hebrew right */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <h2 className="text-[75px] font-bold text-slate-800 leading-tight">
              {englishName}
            </h2>
            {emotionEn && (
              <span
                className="px-6 py-2 rounded-full text-white text-[42px] font-bold uppercase tracking-wide"
                style={{ backgroundColor: borderColor }}
              >
                {emotionEn}
              </span>
            )}
          </div>
          {card.title_he && (
            <span className="font-hebrew text-[67px] text-slate-500 text-right">{card.title_he}</span>
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

        {/* Act it Out - Emotion + Teaching Moment */}
        {actContent.length > 0 && (
          <BackSection
            icon="🎭"
            label="Act it Out"
            borderColor={borderColor}
            tintColor={`${borderColor}15`}
          >
            {actContent.map((text, i) => (
              <p key={i} className={`text-slate-700 ${i === 0 ? 'font-medium' : 'italic mt-2'}`}>
                {text}
              </p>
            ))}
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
