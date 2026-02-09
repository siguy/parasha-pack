/**
 * CardBackFrame - Shared frame for all card backs
 *
 * 5x7 aspect ratio (1500x2100px @ 300 DPI)
 * Consistent header/footer across all card types
 */
import React from 'react';
import { cn } from '@/lib/utils';

interface CardBackFrameProps {
  cardType: string;
  deckName: string;
  borderColor: string;
  className?: string;
  children: React.ReactNode;
}

const CARD_TYPE_LABELS: Record<string, { label: string; icon: string }> = {
  anchor: { label: 'Anchor', icon: '!' },
  spotlight: { label: 'Spotlight', icon: '*' },
  story: { label: 'Story', icon: '*' },
  connection: { label: 'Connection', icon: '?' },
  tradition: { label: 'Tradition', icon: '+' },
  power_word: { label: 'Power Word', icon: '#' },
};

export function CardBackFrame({
  cardType,
  deckName,
  borderColor,
  className,
  children,
}: CardBackFrameProps) {
  const typeInfo = CARD_TYPE_LABELS[cardType] || { label: cardType, icon: '*' };

  return (
    <div
      className={cn(
        'relative w-full h-full bg-[#f5f0e8]', // Warm cream background
        'aspect-[5/7] rounded-[24px] overflow-hidden',
        'border-[8px] shadow-lg',
        'flex flex-col',
        className
      )}
      style={{ borderColor }}
    >
      {/* Header */}
      <div
        className="flex-none flex items-center justify-between px-6 py-4"
        style={{ backgroundColor: borderColor }}
      >
        {/* Card Type Badge */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-white/30 flex items-center justify-center text-white font-bold text-lg">
            {typeInfo.icon}
          </div>
          <span className="text-white font-bold uppercase tracking-wider text-sm">
            {typeInfo.label}
          </span>
        </div>

        {/* Deck Name */}
        <span className="text-white/90 font-medium text-sm">
          {deckName}
        </span>
      </div>

      {/* Content Area */}
      <div className="flex-1 flex flex-col px-6 py-4 overflow-hidden">
        {children}
      </div>

      {/* Footer - Decorative bottom bar */}
      <div
        className="flex-none h-3"
        style={{ backgroundColor: borderColor }}
      />
    </div>
  );
}
