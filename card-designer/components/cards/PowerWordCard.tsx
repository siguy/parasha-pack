'use client';

import React from 'react';
import { PowerWordCardData } from '@/types/card';
import { CardFrame } from './CardFrame';
import { cn } from '@/lib/utils';
import { LayoutConfig, DEFAULT_LAYOUT_CONFIG } from '@/types/editor';
import { DraggableElement } from '../editor/DraggableElement';
import { FitText } from '../ui/FitText';

interface PowerWordCardProps {
  card: PowerWordCardData;
  deckId: string;
  config?: LayoutConfig;
  onConfigChange?: (newConfig: LayoutConfig) => void;
}

export function PowerWordCard({ card, deckId, config, onConfigChange }: PowerWordCardProps) {
  const activeConfig = config || DEFAULT_LAYOUT_CONFIG;
  const borderColor = card.border_color || '#2ecc40'; // Default Green for Power Word

  const handlePositionUpdate = (id: string, x: number, y: number) => {
    if (onConfigChange && config) {
      const newPositions = { ...config.elementPositions, [id]: { x, y } };
      onConfigChange({ ...config, elementPositions: newPositions });
    }
  };

  return (
    <div 
      id={`card-${card.card_id}`} 
      className={cn("w-full h-full", activeConfig.fontFamily)}
      style={{ 
        padding: `${activeConfig.containerPadding ?? 4}px`,
        backgroundColor: activeConfig.paddingColor || 'transparent'
      }}
    >
      <CardFrame 
        borderColor={borderColor} 
        className="flex flex-col relative h-full bg-white ring-4 ring-offset-2 ring-white/50 shadow-2xl overflow-hidden"
      >
        {/* Full Bleed Image */ }
         <div className="absolute inset-0 z-0 bg-slate-200">
            <img 
                src={`/api/images?deck=${deckId}&path=${card.image_path}`} 
                alt={card.english_meaning || "Power Word Card"}
                className="w-full h-full object-cover"
            />
            {/* Gradient Overlay for text visibility at top */}
            <div className="absolute top-0 left-0 right-0 h-40 bg-gradient-to-b from-black/50 to-transparent pointer-events-none" />
        </div>

        {/* Content Layer */}
        <div className="relative z-10 h-full w-full pointer-events-none p-6">
            
            {/* Center Top: Word & Meaning */}
            <div className="absolute top-[6%] left-0 right-0 flex justify-center pointer-events-none">
                 <DraggableElement id="power-word-group" config={activeConfig} onUpdate={handlePositionUpdate} className="pointer-events-auto w-full">
                    <div className="drop-shadow-xl flex flex-col items-center w-full">
                         <FitText
                            maxSize={120}
                            minSize={48}
                            padding={40}
                            className="font-black font-hebrew text-white"
                            style={{
                                textShadow: '3px 3px 0px #000',
                            }}
                         >
                            {card.hebrew_word || ''}
                         </FitText>
                         <div className="bg-black/40 backdrop-blur-sm px-4 py-1 rounded-full mt-2">
                             <h2 className="text-xl font-bold text-white uppercase tracking-[0.2em]">
                                {card.english_meaning}
                             </h2>
                         </div>
                    </div>
                </DraggableElement>
            </div>

        </div>
      </CardFrame>
    </div>
  );
}
