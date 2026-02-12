
import React from 'react';
import { cn } from '@/lib/utils';

interface CardFrameProps {
  borderColor: string;
  className?: string;
  children: React.ReactNode;
}

/**
 * Card frame with border rendered as an overlay on top of all content.
 * This ensures the image fills edge-to-edge and any borders baked into
 * AI-generated images are hidden behind the overlay border.
 */
export function CardFrame({ borderColor, className, children }: CardFrameProps) {
  return (
    <div
      className={cn(
        "relative w-full overflow-hidden bg-white shadow-2xl",
        "aspect-[5/7] rounded-[24px]",
        className
      )}
    >
      {children}
      {/* Border overlay — rendered on top of everything (including image) */}
      <div
        className="absolute inset-0 rounded-[24px] pointer-events-none z-50"
        style={{
          boxShadow: `inset 0 0 0 8px ${borderColor}`,
        }}
      />
    </div>
  );
}
