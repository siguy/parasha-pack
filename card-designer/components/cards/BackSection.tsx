/**
 * BackSection - Shared presentational component for card back sections
 *
 * Used by all card back components for consistent section rendering.
 * Font sizes calibrated for 300 DPI print (1pt ≈ 4.17px).
 *
 * Section labels: 16pt (67px), body text: 14pt (58px)
 */
import React from 'react';

interface BackSectionProps {
  icon: string;
  label: string;
  borderColor: string;
  tintColor?: string;
  grow?: boolean;
  children: React.ReactNode;
}

export function BackSection({
  icon,
  label,
  borderColor,
  tintColor = 'transparent',
  grow = false,
  children,
}: BackSectionProps) {
  return (
    <div
      className={`rounded-xl border-l-[8px] overflow-hidden ${grow ? 'flex-1' : ''}`}
      style={{
        borderLeftColor: borderColor,
        backgroundColor: tintColor,
      }}
    >
      {/* Section Header - 16pt */}
      <div className="flex items-center gap-3 px-8 pt-6 pb-2">
        <span className="text-[58px] leading-none">{icon}</span>
        <span
          className="font-bold text-[67px] uppercase tracking-wider leading-none"
          style={{ color: borderColor }}
        >
          {label}
        </span>
      </div>
      {/* Section Content - 14pt */}
      <div className="px-8 pb-6 text-[58px] leading-[1.4]">
        {children}
      </div>
    </div>
  );
}
