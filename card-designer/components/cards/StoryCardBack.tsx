/**
 * StoryCardBack - Teacher content for Story cards
 *
 * Teacher's Script: teacher_script (grows to fill)
 * Act it Out: roleplay_prompt
 * Ask: discussion_prompts (optional)
 * Tip: teacher_tip
 */
'use client';

import React from 'react';
import { StoryCardData } from '@/types/card';
import { CardBackFrame } from './CardBackFrame';
import { BackSection } from './BackSection';

interface StoryCardBackProps {
  card: StoryCardData;
  deckName: string;
}

export function StoryCardBack({ card, deckName }: StoryCardBackProps) {
  const borderColor = card.border_color || '#FF4136';

  return (
    <div id={`card-${card.card_id}-back`} className="w-full h-full">
      <CardBackFrame
        cardType="story"
        deckName={deckName}
        borderColor={borderColor}
        transitionLine={card.transition_line}
      >
        {/* Card Title - English + number left, Hebrew right */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4 min-w-0">
            <h2 className="text-[75px] font-bold text-slate-800 leading-tight">
              {card.title_en}
            </h2>
            {card.sequence_number && (
              <span
                className="w-[80px] h-[80px] rounded-full flex items-center justify-center text-white font-bold text-[50px] flex-shrink-0"
                style={{ backgroundColor: borderColor }}
              >
                #{card.sequence_number}
              </span>
            )}
          </div>
          {card.title_he && (
            <span className="font-hebrew text-[58px] text-slate-500 flex-shrink-0 text-right">{card.title_he}</span>
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

        {/* Act it Out - Roleplay Prompt */}
        {card.roleplay_prompt && (
          <BackSection
            icon="🎭"
            label="Act it Out"
            borderColor={borderColor}
            tintColor={`${borderColor}15`}
          >
            <p className="text-slate-700 font-medium">
              {card.roleplay_prompt.replace(/^Act it out:\s*/i, '')}
            </p>
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
