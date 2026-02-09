'use client';

import React from 'react';
import { SpotlightCardData } from '@/types/card';
import { CardFrame } from './CardFrame';
import { cn } from '@/lib/utils';
import { LayoutConfig, DEFAULT_LAYOUT_CONFIG } from '@/types/editor';
import { DraggableElement } from '../editor/DraggableElement';

interface SpotlightCardProps {
  card: SpotlightCardData;
  deckId: string;
  config?: LayoutConfig;
  onConfigChange?: (newConfig: LayoutConfig) => void;
}

export function SpotlightCard({ card, deckId, config, onConfigChange }: SpotlightCardProps) {
  const activeConfig = config || DEFAULT_LAYOUT_CONFIG;
  const borderColor = card.border_color || '#d4a84b'; // Default Gold for Spotlight

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
                alt={card.english_name || "Spotlight Card"}
                className="w-full h-full object-cover"
            />
            {/* Gradient Overlay for text visibility at top */}
            <div className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-black/40 to-transparent pointer-events-none" />
        </div>

        {/* Content Layer */}
        <div className="relative z-10 h-full w-full pointer-events-none p-6">
            
            {/* Center Top: Character Names */}
            <div className="absolute top-3 left-0 right-0 flex justify-center pointer-events-none">
                 <DraggableElement id="spotlight-names" config={activeConfig} onUpdate={handlePositionUpdate} className="pointer-events-auto">
                    <div className="text-center drop-shadow-lg flex flex-col items-center">
                         <h1 
                            className="font-black font-hebrew text-4xl text-white leading-none"
                            style={{ 
                                textShadow: '2px 2px 0px #000, -1px -1px 0px #000, 1px -1px 0px #000, -1px 1px 0px #000, 1px 1px 0px #000' 
                            }}
                         >
                            {card.hebrew_name}
                         </h1>
                         <h2 className="text-xl font-bold text-white uppercase tracking-widest mt-1 opacity-90 drop-shadow-md">
                            {card.english_name}
                         </h2>
                    </div>
                </DraggableElement>
            </div>

            {/* Gradient Overlay for text visibility at bottom */}
            <div className="absolute bottom-0 left-0 right-0 h-40 bg-gradient-to-t from-black/50 to-transparent pointer-events-none" />

            {/* Bottom Left: Emotion Badge (no container, Story-card style) */}
            <div className="absolute bottom-6 left-6 pointer-events-none">
                 <DraggableElement id="emotion-badge" config={activeConfig} onUpdate={handlePositionUpdate} className="pointer-events-auto">
                    <div className="flex flex-col items-start">
                        <span 
                            className="font-black text-3xl leading-none font-hebrew drop-shadow-lg"
                            style={{ 
                                color: borderColor,
                                textShadow: '2px 2px 4px rgba(0,0,0,0.5), -1px -1px 0 rgba(255,255,255,0.3)'
                            }}
                        >
                            {card.emotion_word_he}
                        </span>
                        <span 
                            className="text-sm uppercase font-extrabold tracking-widest mt-1 drop-shadow-md"
                            style={{ 
                                color: 'white',
                                textShadow: '1px 1px 3px rgba(0,0,0,0.5)'
                            }}
                        >
                            {card.emotion_word_en}
                        </span>
                    </div>
                </DraggableElement>
            </div>

        </div>
      </CardFrame>
    </div>
  );
}
