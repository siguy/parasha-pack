'use client';

import React from 'react';
import { AnchorCardData } from '@/types/card';
import { CardFrame } from './CardFrame';
import { cn } from '@/lib/utils';
import { LayoutConfig, DEFAULT_LAYOUT_CONFIG } from '@/types/editor';
import { DraggableElement } from '../editor/DraggableElement';
import { FitText } from '../ui/FitText';

interface AnchorCardProps {
  card: AnchorCardData;
  deckId: string;
  config?: LayoutConfig;
  onConfigChange?: (newConfig: LayoutConfig) => void;
}

export function AnchorCard({ card, deckId, config, onConfigChange }: AnchorCardProps) {
  const activeConfig = config || DEFAULT_LAYOUT_CONFIG;
  const borderColor = card.border_color || '#5c2d91'; // Default Purple for Anchor

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
        className="flex flex-col relative h-full bg-white ring-4 ring-offset-2 ring-white/50 shadow-2xl"
      >
        {/* Full Bleed Image Background */}
         <div className="absolute inset-0 z-0 bg-slate-200">
            <img 
                src={`/api/images?deck=${deckId}&path=${card.image_path}`} 
                alt={card.hebrew_title || "Anchor Card"}
                className="w-full h-full object-cover"
            />
             {/* Optional Overlay to help text readability if needed, though design doc says minimal text */}
        </div>

        {/* Content Layer */}
        <div className="relative z-10 h-full pointer-events-none">
            
            {/* Top Centered Hebrew Title */}
            <div className="absolute top-[10%] left-0 right-0 flex justify-center">
                <DraggableElement id="anchor-title" config={activeConfig} onUpdate={handlePositionUpdate} className="pointer-events-auto w-full">
                    <div className="drop-shadow-[0_2px_4px_rgba(255,255,255,0.8)]">
                         <FitText
                            maxSize={120}
                            minSize={48}
                            padding={48}
                            className="font-black font-hebrew"
                            style={{
                                color: borderColor,
                                textShadow: '2px 2px 0px white, -2px -2px 0px white, 2px -2px 0px white, -2px 2px 0px white',
                            }}
                         >
                            {card.hebrew_title || card.title_he || ''}
                         </FitText>
                    </div>
                </DraggableElement>
            </div>

        </div>
      </CardFrame>
    </div>
  );
}
