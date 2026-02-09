/**
 * ConnectionCardBack - Teacher content for Connection (discussion) cards
 *
 * Displays:
 * - Title (Hebrew + English)
 * - Questions list
 * - Feeling faces grid with emoji + Hebrew labels
 * - Torah Talk instruction
 * - Teacher script
 */
'use client';

import React from 'react';
import { ConnectionCardData } from '@/types/card';
import { CardBackFrame } from './CardBackFrame';

interface ConnectionCardBackProps {
  card: ConnectionCardData;
  deckName: string;
}

export function ConnectionCardBack({ card, deckName }: ConnectionCardBackProps) {
  const borderColor = card.border_color || '#0074d9';

  // Get questions from various field formats
  const questions = card.questions || [];

  // Get feeling faces
  const feelingFaces = card.feeling_faces || [];

  return (
    <div id={`card-${card.card_id}-back`} className="w-full h-full">
      <CardBackFrame
        cardType="connection"
        deckName={deckName}
        borderColor={borderColor}
      >
        {/* Title Section */}
        <div className="mb-4">
          <h1 className="font-black font-hebrew text-3xl text-slate-800 leading-tight">
            {card.title_he}
          </h1>
          <h2 className="text-lg font-bold text-slate-600">
            {card.title_en}
          </h2>
        </div>

        <div className="border-t border-slate-300 mb-4" />

        {/* Questions */}
        {questions.length > 0 && (
          <div className="mb-4">
            <h3 className="font-bold text-slate-500 text-xs uppercase tracking-wider mb-3">
              Discussion Questions
            </h3>
            <div className="space-y-3">
              {questions.map((q: any, idx: number) => (
                <div
                  key={idx}
                  className="flex gap-3 items-start"
                >
                  <div
                    className="w-6 h-6 rounded-full flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
                    style={{ backgroundColor: borderColor }}
                  >
                    {idx + 1}
                  </div>
                  <div>
                    <p className="text-slate-700 font-medium">
                      {q.question_en || q}
                    </p>
                    {q.question_he && (
                      <p className="text-slate-500 text-sm font-hebrew mt-1" dir="rtl">
                        {q.question_he}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Feeling Faces Grid */}
        {feelingFaces.length > 0 && (
          <div className="mb-4">
            <h3 className="font-bold text-slate-500 text-xs uppercase tracking-wider mb-3">
              Feeling Faces
            </h3>
            <div className="grid grid-cols-4 gap-2">
              {feelingFaces.map((face: any, idx: number) => (
                <div
                  key={idx}
                  className="flex flex-col items-center p-2 bg-white rounded-lg shadow-sm border border-slate-100"
                >
                  <span className="text-3xl mb-1">{face.emoji}</span>
                  <span className="text-xs font-hebrew text-slate-600">{face.label_he}</span>
                  {face.label_en && (
                    <span className="text-[10px] text-slate-400 uppercase">{face.label_en}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Torah Talk */}
        <div
          className="rounded-xl p-4 mb-4 text-center"
          style={{ backgroundColor: `${borderColor}15` }}
        >
          <h3 className="font-bold text-slate-700 text-sm mb-1">Torah Talk</h3>
          <p className="text-slate-600 italic text-sm">
            {(card as any).torah_talk_instruction || 'Sit in a circle and share!'}
          </p>
        </div>

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
