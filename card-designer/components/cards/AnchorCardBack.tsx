/**
 * AnchorCardBack - Teacher content for Anchor cards
 *
 * SAY: teacher_script
 * DO: emotional_hook_en (read aloud)
 * ASK: discussion_prompts
 * TIP: teacher_tip
 */
'use client';

import React from 'react';
import { AnchorCardData } from '@/types/card';
import { CardBackFrame } from './CardBackFrame';
import { BackSection } from './BackSection';

interface AnchorCardBackProps {
  card: AnchorCardData;
  deckName: string;
}

export function AnchorCardBack({ card, deckName }: AnchorCardBackProps) {
  const borderColor = card.border_color || '#5c2d91';
  const englishTitle = card.title_en;
  const hebrewTitle = card.hebrew_title || card.title_he;

  return (
    <div id={`card-${card.card_id}-back`} className="w-full h-full">
      <CardBackFrame
        cardType="anchor"
        deckName={deckName}
        borderColor={borderColor}
        transitionLine={card.transition_line}
      >
        {/* Compact Title Line */}
        <div className="flex items-center gap-3 mb-5">
          <h2 className="text-2xl font-bold text-slate-800 leading-tight">
            {englishTitle}
          </h2>
          {hebrewTitle && (
            <span className="font-hebrew text-xl text-slate-500">{hebrewTitle}</span>
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

          {/* DO THIS - Emotional Hook */}
          {card.emotional_hook_en && (
            <BackSection
              icon="🎯"
              label="Do This"
              borderColor={borderColor}
              tintColor={`${borderColor}10`}
            >
              <p className="text-slate-700 font-medium italic">
                Read aloud: &ldquo;{card.emotional_hook_en}&rdquo;
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
