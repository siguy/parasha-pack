/**
 * StoryCardBack - Teacher content for Story cards
 *
 * SAY: teacher_script
 * DO: roleplay_prompt
 * ASK: discussion_prompts
 * TIP: teacher_tip
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
        {/* Compact Title Line with Sequence Badge */}
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-2xl font-bold text-slate-800 leading-tight">
            {card.title_en}
          </h2>
          {card.sequence_number && (
            <span
              className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-lg flex-shrink-0"
              style={{ backgroundColor: borderColor }}
            >
              #{card.sequence_number}
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

          {/* DO THIS - Roleplay Prompt */}
          {card.roleplay_prompt && (
            <BackSection
              icon="🎯"
              label="Do This"
              borderColor={borderColor}
              tintColor={`${borderColor}10`}
            >
              <p className="text-slate-700 font-medium">
                {card.roleplay_prompt.replace(/^Act it out:\s*/i, '')}
              </p>
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
