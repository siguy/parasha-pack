/**
 * ConnectionCardBack - Teacher content for Connection (discussion) cards
 *
 * SAY: torah_talk_instruction
 * DO: feeling_faces (emoji grid)
 * ASK: questions[] (EN only)
 * TIP: teacher_tip
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
        {/* Compact Title Line */}
        <div className="mb-5">
          <h2 className="text-2xl font-bold text-slate-800 leading-tight">
            {card.title_en}
          </h2>
        </div>

        <div className="flex flex-col gap-4">
          {/* SAY THIS - Torah Talk Instruction + Teacher Script */}
          <BackSection
            icon="💬"
            label="Say This"
            borderColor={borderColor}
            large
          >
            <p className="text-slate-700">
              {card.torah_talk_instruction || card.teacher_script}
            </p>
            {card.torah_talk_instruction && card.teacher_script && (
              <p className="text-slate-600 mt-2 text-base">
                {card.teacher_script}
              </p>
            )}
          </BackSection>

          {/* DO THIS - Feeling Faces */}
          {feelingFaces.length > 0 && (
            <BackSection
              icon="🎯"
              label="Do This"
              borderColor={borderColor}
              tintColor={`${borderColor}10`}
            >
              <p className="text-slate-600 text-sm mb-2">Point to each face and ask children how it feels:</p>
              <div className="flex gap-3 justify-center">
                {feelingFaces.map((face, idx) => (
                  <div key={idx} className="flex flex-col items-center">
                    <span className="text-2xl">{face.emoji}</span>
                    <span className="text-xs text-slate-600 mt-0.5">{face.label_en}</span>
                  </div>
                ))}
              </div>
            </BackSection>
          )}

          {/* ASK THIS - Discussion Questions */}
          {questions.length > 0 && (
            <BackSection
              icon="❓"
              label="Ask This"
              borderColor={borderColor}
              tintColor="#0074d915"
            >
              <ul className="text-slate-700 space-y-1.5">
                {questions.map((q, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-slate-400 flex-shrink-0">•</span>
                    <span>{q.question_en || (typeof q === 'string' ? q : '')}</span>
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
