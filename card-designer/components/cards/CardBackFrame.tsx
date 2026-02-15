/**
 * CardBackFrame - Shared frame for all card backs
 *
 * 5x7 aspect ratio (1500x2100px @ 300 DPI)
 * Font sizes calibrated for print: 1pt ≈ 4.17px at 300 DPI
 */
import React from 'react';
import { cn } from '@/lib/utils';

interface CardBackFrameProps {
  cardType: string;
  deckName: string;
  borderColor: string;
  transitionLine?: string;
  className?: string;
  children: React.ReactNode;
}

const CARD_TYPE_LABELS: Record<string, string> = {
  anchor: 'Anchor',
  spotlight: 'Spotlight',
  story: 'Story',
  connection: 'Connection',
  tradition: 'Tradition',
  power_word: 'Power Word',
};

export function CardBackFrame({
  cardType,
  deckName,
  borderColor,
  transitionLine,
  className,
  children,
}: CardBackFrameProps) {
  const typeLabel = CARD_TYPE_LABELS[cardType] || cardType;

  return (
    <div
      className={cn(
        'relative w-full h-full bg-[#f5f0e8]',
        'aspect-[5/7] rounded-[32px] overflow-hidden',
        'border-[12px] shadow-lg',
        'flex flex-col',
        className
      )}
      style={{ borderColor }}
    >
      {/* Header - 12pt text */}
      <div
        className="flex-none flex items-center justify-between px-12 py-6"
        style={{ backgroundColor: borderColor }}
      >
        <span className="text-white font-bold uppercase tracking-wider text-[50px] leading-none">
          {typeLabel}
        </span>
        <span className="text-white/90 font-medium text-[50px] leading-none">
          {deckName}
        </span>
      </div>

      {/* Content Area */}
      <div className="flex-1 flex flex-col px-10 py-8 overflow-hidden">
        {children}
      </div>

      {/* Footer - Transition line */}
      <div
        className="flex-none flex items-center justify-center px-12"
        style={{ backgroundColor: borderColor, minHeight: transitionLine ? undefined : '16px' }}
      >
        {transitionLine && (
          <p className="text-white/90 text-[42px] italic text-center py-4 leading-tight">
            {transitionLine}
          </p>
        )}
      </div>
    </div>
  );
}
