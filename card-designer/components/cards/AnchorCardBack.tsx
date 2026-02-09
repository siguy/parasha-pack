/**
 * AnchorCardBack - Teacher content for Anchor cards
 *
 * Displays:
 * - Parasha/Holiday name (Hebrew + English)
 * - Emotional hook (Hebrew + English)
 * - Teacher script (gathering prompt)
 */
'use client';

import React from 'react';
import { AnchorCardData } from '@/types/card';
import { CardBackFrame } from './CardBackFrame';

interface AnchorCardBackProps {
  card: AnchorCardData;
  deckName: string;
}

export function AnchorCardBack({ card, deckName }: AnchorCardBackProps) {
  const borderColor = card.border_color || '#5c2d91';

  // Get title from various fields
  const hebrewTitle = card.hebrew_title || card.title_he;
  const englishTitle = card.title_en;

  // Get emotional hook from various fields
  const emotionalHookEn = (card as any).emotional_hook_en;
  const emotionalHookHe = card.emotional_hook_he || (card as any).emotional_hook_he;

  return (
    <div id={`card-${card.card_id}-back`} className="w-full h-full">
      <CardBackFrame
        cardType="anchor"
        deckName={deckName}
        borderColor={borderColor}
      >
        {/* Title Section - Large and Prominent */}
        <div className="text-center mb-6">
          <h1 className="font-black font-hebrew text-5xl text-slate-800 leading-tight mb-2">
            {hebrewTitle}
          </h1>
          <h2 className="text-2xl font-bold text-slate-600 uppercase tracking-wide">
            {englishTitle}
          </h2>
        </div>

        <div className="border-t border-slate-300 mb-6" />

        {/* Emotional Hook */}
        {(emotionalHookEn || emotionalHookHe) && (
          <div
            className="rounded-xl p-6 mb-6 text-center"
            style={{ backgroundColor: `${borderColor}15` }}
          >
            <h3 className="font-bold text-slate-700 text-sm uppercase tracking-wider mb-3">
              Emotional Hook
            </h3>
            {emotionalHookEn && (
              <p className="text-slate-800 text-lg font-medium leading-relaxed mb-3">
                "{emotionalHookEn}"
              </p>
            )}
            {emotionalHookHe && (
              <p className="text-slate-600 font-hebrew text-base leading-relaxed" dir="rtl">
                "{emotionalHookHe}"
              </p>
            )}
          </div>
        )}

        {/* Teacher Script */}
        <div className="flex-1 flex flex-col min-h-0">
          <h3 className="font-bold text-slate-500 text-xs uppercase tracking-wider mb-2">
            Gathering Script
          </h3>
          <div className="flex-1 bg-white rounded-lg p-5 shadow-inner border border-slate-200 overflow-auto">
            <p className="text-slate-700 leading-relaxed">
              {card.teacher_script}
            </p>
          </div>
        </div>
      </CardBackFrame>
    </div>
  );
}
