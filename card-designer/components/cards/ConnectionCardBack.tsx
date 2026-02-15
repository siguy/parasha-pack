/**
 * ConnectionCardBack - Teacher content for Connection (discussion) cards
 *
 * Teacher's Script: torah_talk_instruction + teacher_script (grows to fill)
 * Act it Out: feeling_faces (emoji grid)
 * Ask: questions[] (EN only)
 * Tip: teacher_tip
 */
'use client';

import React from 'react';
import { ConnectionCardData } from '@/types/card';
import { CardBackFrame } from './CardBackFrame';
import { BackSection } from './BackSection';

interface ConnectionCardBackProps {
  card: ConnectionCardData;
  deckName: string;
}

export function ConnectionCardBack({ card, deckName }: ConnectionCardBackProps) {
  const borderColor = card.border_color || '#0074d9';
  const questions = card.questions || [];
  const feelingFaces = card.feeling_faces || [];

  return (
    <div id={`card-${card.card_id}-back`} className="w-full h-full">
      <CardBackFrame
        cardType="connection"
        deckName={deckName}
        borderColor={borderColor}
        transitionLine={card.transition_line}
      >
        {/* Card Title - English left, Hebrew right */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-[75px] font-bold text-slate-800 leading-tight">
            {card.title_en}
          </h2>
          {card.title_he && (
            <span className="font-hebrew text-[67px] text-slate-500 text-right">{card.title_he}</span>
          )}
        </div>

        {/* Teacher's Script (grows to fill) */}
        <BackSection
          icon="💬"
          label="Teacher's Script"
          borderColor={borderColor}
          grow
        >
          <p className="text-slate-700">
            {card.torah_talk_instruction || card.teacher_script}
          </p>
          {card.torah_talk_instruction && card.teacher_script && (
            <p className="text-slate-600 mt-3">
              {card.teacher_script}
            </p>
          )}
        </BackSection>

        {/* Act it Out - Feeling Faces */}
        {feelingFaces.length > 0 && (
          <BackSection
            icon="🎭"
            label="Act it Out"
            borderColor={borderColor}
            tintColor={`${borderColor}15`}
          >
            <p className="text-slate-600 text-[50px] mb-4">Point to each face and ask children how it feels:</p>
            <div className="flex gap-6 justify-center">
              {feelingFaces.map((face, idx) => (
                <div key={idx} className="flex flex-col items-center">
                  <span className="text-[72px]">{face.emoji}</span>
                  <span className="text-[42px] text-slate-600 mt-1">{face.label_en}</span>
                </div>
              ))}
            </div>
          </BackSection>
        )}

        {/* Ask - Discussion Questions */}
        {questions.length > 0 && (
          <BackSection
            icon="❓"
            label="Ask"
            borderColor={borderColor}
            tintColor="#0074d920"
          >
            <ul className="text-slate-700 space-y-2">
              {questions.map((q, i) => (
                <li key={i} className="flex gap-3">
                  <span className="text-slate-400 flex-shrink-0">•</span>
                  <span>{q.question_en || (typeof q === 'string' ? q : '')}</span>
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
