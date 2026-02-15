/**
 * TraditionCardBack - Teacher content for Tradition cards (holiday decks)
 *
 * Teacher's Script: teacher_script (grows to fill)
 * Act it Out: child_action_en
 * Ask: discussion_prompts (optional)
 * Tip: teacher_tip
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
        {/* Card Title - 18pt + Hebrew Term */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-[75px] font-bold text-slate-800 leading-tight">
            {englishTitle}
          </h2>
          {hebrewTerm && (
            <span className="font-hebrew text-[67px] font-bold text-slate-600">
              {hebrewTerm}
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

        {/* Act it Out - Child Action */}
        {card.child_action_en && (
          <BackSection
            icon="🎭"
            label="Act it Out"
            borderColor={borderColor}
            tintColor={`${borderColor}15`}
          >
            <p className="text-slate-700 font-medium">{card.child_action_en}</p>
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
