
import React from 'react';
import { cn } from '@/lib/utils';
import { CardData } from '@/types/card';

interface CardFrameProps {
  borderColor: string;
  className?: string;
  children: React.ReactNode;
}

export function CardFrame({ borderColor, className, children }: CardFrameProps) {
  return (
    <div 
      className={cn(
        "relative w-full overflow-hidden bg-white shadow-2xl",
        "aspect-[5/7] rounded-[24px]", 
        "border-[8px]",
        className
      )}
      style={{
        borderColor: borderColor
      }}
    >
      {children}
    </div>
  );
}
