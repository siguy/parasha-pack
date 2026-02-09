/**
 * StoryCardBack - Teacher content for Story cards
 *
 * Displays:
 * - Title (Hebrew + English) with sequence number
 * - Description
 * - Roleplay prompt box
 * - Teacher script
 */
'use client';

import React from 'react';
import { StoryCardData } from '@/types/card';
import { CardBackFrame } from './CardBackFrame';

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
      >
        {/* Title Section */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex flex-col">
            <h1 className="font-black font-hebrew text-3xl text-slate-800 leading-tight">
              {card.title_he}
            </h1>
            <h2 className="text-lg font-bold text-slate-600">
              {card.title_en}
            </h2>
          </div>
          {/* Sequence Badge */}
          {card.sequence_number && (
            <div
              className="w-14 h-14 rounded-full flex items-center justify-center text-white font-black text-2xl shadow-md"
              style={{ backgroundColor: borderColor }}
            >
              #{card.sequence_number}
            </div>
          )}
        </div>

        <div className="border-t border-slate-300 mb-4" />

        {/* Description */}
        <div className="mb-4">
          <p className="text-slate-700 text-base leading-relaxed">
            {card.english_description}
          </p>
          {card.description_he && (
            <p className="text-slate-600 text-sm font-hebrew mt-2 leading-relaxed" dir="rtl">
              {card.description_he}
            </p>
          )}
        </div>

        {/* Roleplay Prompt */}
        {card.roleplay_prompt && (
          <div
            className="rounded-xl p-4 mb-4"
            style={{ backgroundColor: `${borderColor}15` }}
          >
            <div className="flex items-start gap-3">
              <span className="text-2xl">*</span>
              <div>
                <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wide mb-1">
                  Act it Out!
                </h3>
                <p className="text-slate-700 font-medium italic">
                  {card.roleplay_prompt.replace(/^Act it out:\s*/i, '')}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Teacher Script */}
        <div className="flex-1 flex flex-col min-h-0">
          <h3 className="font-bold text-slate-500 text-xs uppercase tracking-wider mb-2">
            Teacher Script
          </h3>
          <div className="flex-1 bg-white rounded-lg p-4 shadow-inner border border-slate-200 overflow-auto">
            <p className="text-slate-700 leading-relaxed text-sm">
              {card.teacher_script}
            </p>
          </div>
        </div>
      </CardBackFrame>
    </div>
  );
}
