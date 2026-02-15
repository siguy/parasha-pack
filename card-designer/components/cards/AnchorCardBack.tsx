/**
 * AnchorCardBack - Teacher content for Anchor cards
 *
 * Teacher's Script: teacher_script (grows to fill)
 * Act it Out: emotional_hook_en (read aloud)
 * Ask: discussion_prompts (optional)
 * Tip: teacher_tip
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
        {/* Card Title - 18pt */}
        <div className="flex items-center gap-4 mb-6">
          <h2 className="text-[75px] font-bold text-slate-800 leading-tight">
            {englishTitle}
          </h2>
          {hebrewTitle && (
            <span className="font-hebrew text-[67px] text-slate-500">{hebrewTitle}</span>
          )}
        </div>

        {/* Teacher's Script (grows to fill available space) */}
        <BackSection
          icon="💬"
          label="Teacher's Script"
          borderColor={borderColor}
          grow
        >
          <p className="text-slate-700">{card.teacher_script}</p>
        </BackSection>

        {/* Act it Out - Emotional Hook */}
        {card.emotional_hook_en && (
          <BackSection
            icon="🎭"
            label="Act it Out"
            borderColor={borderColor}
            tintColor={`${borderColor}15`}
          >
            <p className="text-slate-700 font-medium italic">
              Read aloud: &ldquo;{card.emotional_hook_en}&rdquo;
            </p>
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
