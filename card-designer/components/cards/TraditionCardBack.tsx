/**
 * TraditionCardBack - Teacher content for Tradition cards (holiday decks)
 *
 * SAY: teacher_script
 * DO: child_action_en
 * ASK: discussion_prompts
 * TIP: teacher_tip
 */
'use client';

import React from 'react';
import { TraditionCardData } from '@/types/card';
import { CardBackFrame } from './CardBackFrame';
import { BackSection } from './BackSection';

interface TraditionCardBackProps {
  card: TraditionCardData;
  deckName: string;
}

export function TraditionCardBack({ card, deckName }: TraditionCardBackProps) {
  const borderColor = card.border_color || '#d4a84b';
  const englishTitle = card.english_title || card.title_en;
  const hebrewTerm = card.hebrew_term;
  const termMeaning = card.hebrew_term_meaning;

  return (
    <div id={`card-${card.card_id}-back`} className="w-full h-full">
      <CardBackFrame
        cardType="tradition"
        deckName={deckName}
        borderColor={borderColor}
        transitionLine={card.transition_line}
      >
        {/* Compact Title Line with Hebrew Term */}
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-2xl font-bold text-slate-800 leading-tight">
            {englishTitle}
          </h2>
          {hebrewTerm && (
            <span className="font-hebrew text-xl font-bold text-slate-600">
              {hebrewTerm}
              {termMeaning && (
                <span className="text-base font-normal text-slate-400 ml-1">({termMeaning})</span>
              )}
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

          {/* DO THIS - Child Action */}
          {card.child_action_en && (
            <BackSection
              icon="🎯"
              label="Do This"
              borderColor={borderColor}
              tintColor={`${borderColor}10`}
            >
              <p className="text-slate-700 font-medium">{card.child_action_en}</p>
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
