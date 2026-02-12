'use client';

import React from 'react';
import { ConnectionCardData } from '@/types/card';
import { CardFrame } from './CardFrame';
import { cn } from '@/lib/utils';
import { LayoutConfig, DEFAULT_LAYOUT_CONFIG } from '@/types/editor';
import { DraggableElement } from '../editor/DraggableElement';
import { FitText } from '../ui/FitText';

interface ConnectionCardProps {
  card: ConnectionCardData;
  deckId: string;
  config?: LayoutConfig;
  onConfigChange?: (newConfig: LayoutConfig) => void;
}

export function ConnectionCard({ card, deckId, config, onConfigChange }: ConnectionCardProps) {
  const activeConfig = config || DEFAULT_LAYOUT_CONFIG;
  const borderColor = card.border_color || '#0074d9'; // Default Blue for Connection

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
                alt="Connection Card"
                className="w-full h-full object-cover"
            />
            {/* Gradient overlays for text visibility */}
            <div className="absolute inset-x-0 top-0 h-24 bg-gradient-to-b from-black/40 to-transparent pointer-events-none" />
            <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-black/50 to-transparent pointer-events-none" />
        </div>

        {/* Top: Title */}
        <div className="absolute top-3 left-0 right-0 z-10 flex justify-center pointer-events-none">
            <DraggableElement id="title-group" config={activeConfig} onUpdate={handlePositionUpdate} className="pointer-events-auto w-full">
                <div className="drop-shadow-lg flex flex-col items-center">
                    <FitText
                        maxSize={72}
                        minSize={28}
                        padding={32}
                        className="font-black font-hebrew"
                        style={{
                            color: borderColor,
                            textShadow: '2px 2px 4px rgba(0,0,0,0.5), -1px -1px 0 rgba(255,255,255,0.3)',
                        }}
                    >
                        {card.title_he || 'חִבּוּר'}
                    </FitText>
                    <h2 className="text-sm font-bold text-white uppercase tracking-widest mt-1 opacity-90 drop-shadow-md">
                        {card.title_en || 'CONNECTION'}
                    </h2>
                </div>
            </DraggableElement>
        </div>

        {/* Bottom: Large Emojis Strip spanning full width */}
        <div className="absolute bottom-4 left-4 right-4 z-10 pointer-events-none">
             <DraggableElement id="emoji-strip" config={activeConfig} onUpdate={handlePositionUpdate} className="pointer-events-auto w-full">
                <div 
                    className="bg-white/40 backdrop-blur-sm rounded-2xl shadow-lg p-4 flex justify-around items-center w-full"
                >
                    {card.emojis && card.emojis.map((emoji, idx) => (
                        <span key={idx} className="text-5xl drop-shadow-md hover:scale-110 transition-transform cursor-default">
                            {emoji}
                        </span>
                    ))}
                    {(!card.emojis || card.emojis.length === 0) && (
                        <span className="text-slate-400 italic text-sm w-full text-center">No emojis defined</span>
                    )}
                </div>
            </DraggableElement>
        </div>

      </CardFrame>
    </div>
  );
}

