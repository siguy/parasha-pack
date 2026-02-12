'use client';

import React from 'react';
import { TraditionCardData } from '@/types/card';
import { CardFrame } from './CardFrame';
import { cn } from '@/lib/utils';
import { LayoutConfig, DEFAULT_LAYOUT_CONFIG } from '@/types/editor';
import { DraggableElement } from '../editor/DraggableElement';
import { FitText } from '../ui/FitText';

interface TraditionCardProps {
  card: TraditionCardData;
  deckId: string;
  config?: LayoutConfig;
  onConfigChange?: (newConfig: LayoutConfig) => void;
}

export function TraditionCard({ card, deckId, config, onConfigChange }: TraditionCardProps) {
  const activeConfig = config || DEFAULT_LAYOUT_CONFIG;
  const borderColor = card.border_color || '#d4a84b'; // Default Gold for Tradition

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
                alt={card.english_title || "Tradition Card"}
                className="w-full h-full object-cover"
            />
            {/* Gradient Overlay for text visibility at top */}
            <div className="absolute top-0 left-0 right-0 h-40 bg-gradient-to-b from-black/60 to-transparent pointer-events-none" />
        </div>

        {/* Content Layer */}
        <div className="relative z-10 h-full w-full pointer-events-none p-6">
            
            {/* Center Top: Titles */}
            <div className="absolute top-[8%] left-0 right-0 flex justify-center pointer-events-none">
                 <DraggableElement id="tradition-titles" config={activeConfig} onUpdate={handlePositionUpdate} className="pointer-events-auto">
                    <div className="drop-shadow-xl flex flex-col items-center gap-2 w-full">
                         <FitText
                            maxSize={110}
                            minSize={40}
                            padding={40}
                            className="font-black font-hebrew text-white"
                            style={{
                                textShadow: '0px 2px 10px rgba(0,0,0,0.5)',
                            }}
                         >
                            {card.hebrew_title || ''}
                         </FitText>
                         <div className="border-t-2 border-white/50 w-32" />
                         <h2 className="text-2xl font-bold text-white tracking-wide uppercase drop-shadow-md font-serif italic">
                            {card.english_title}
                         </h2>
                    </div>
                </DraggableElement>
            </div>

        </div>
      </CardFrame>
    </div>
  );
}
