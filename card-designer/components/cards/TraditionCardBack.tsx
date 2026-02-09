/**
 * TraditionCardBack - Teacher content for Tradition cards (holiday decks)
 *
 * Displays:
 * - Tradition name (Hebrew + English)
 * - Story connection text
 * - Practice description
 * - Child action prompt
 * - Hebrew term with meaning
 * - Teacher script
 */
'use client';

import React from 'react';
import { TraditionCardData } from '@/types/card';
import { CardBackFrame } from './CardBackFrame';

interface TraditionCardBackProps {
  card: TraditionCardData;
  deckName: string;
}

export function TraditionCardBack({ card, deckName }: TraditionCardBackProps) {
  const borderColor = card.border_color || '#d4a84b';

  // Get fields from various names
  const hebrewTitle = card.hebrew_title || card.title_he;
  const englishTitle = card.english_title || card.title_en;
  const storyConnection = (card as any).story_connection_en || card.story_connection_he;
  const practiceDesc = (card as any).practice_description_en || card.practice_description_he;
  const childAction = (card as any).child_action_en || card.child_action_he;
  const hebrewTerm = card.hebrew_term;
  const termMeaning = (card as any).hebrew_term_meaning;

  return (
    <div id={`card-${card.card_id}-back`} className="w-full h-full">
      <CardBackFrame
        cardType="tradition"
        deckName={deckName}
        borderColor={borderColor}
      >
        {/* Title Section */}
        <div className="text-center mb-4">
          <h1 className="font-black font-hebrew text-4xl text-slate-800 leading-tight mb-1">
            {hebrewTitle}
          </h1>
          <h2 className="text-xl font-bold text-slate-600">
            {englishTitle}
          </h2>
        </div>

        <div className="border-t border-slate-300 mb-4" />

        {/* Story Connection */}
        {storyConnection && (
          <div className="mb-4">
            <h3 className="font-bold text-slate-500 text-xs uppercase tracking-wider mb-2">
              Story Connection
            </h3>
            <p className="text-slate-700 leading-relaxed text-sm italic">
              {storyConnection}
            </p>
          </div>
        )}

        {/* Practice Description */}
        {practiceDesc && (
          <div className="mb-4">
            <h3 className="font-bold text-slate-500 text-xs uppercase tracking-wider mb-2">
              What We Do
            </h3>
            <p className="text-slate-700 leading-relaxed">
              {practiceDesc}
            </p>
          </div>
        )}

        {/* Child Action */}
        {childAction && (
          <div
            className="rounded-xl p-4 mb-4"
            style={{ backgroundColor: `${borderColor}15` }}
          >
            <div className="flex items-start gap-3">
              <span className="text-2xl">+</span>
              <div>
                <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wide mb-1">
                  Try It!
                </h3>
                <p className="text-slate-700 font-medium">
                  {childAction}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Hebrew Term */}
        {hebrewTerm && (
          <div className="text-center mb-4 py-3 bg-white rounded-lg shadow-sm border border-slate-200">
            <span className="font-hebrew text-2xl font-bold text-slate-800">
              {hebrewTerm}
            </span>
            {termMeaning && (
              <span className="text-slate-500 ml-3">
                ({termMeaning})
              </span>
            )}
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
