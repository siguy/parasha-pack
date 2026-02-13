/**
 * BackSection - Shared presentational component for card back sections
 *
 * Used by all card back components for consistent SAY/DO/ASK/TIP rendering.
 * Each section has a left border accent, icon + label header, and tinted background.
 */
import React from 'react';

interface BackSectionProps {
  icon: string;
  label: string;
  borderColor: string;
  tintColor?: string;
  large?: boolean;
  children: React.ReactNode;
}

export function BackSection({
  icon,
  label,
  borderColor,
  tintColor = 'transparent',
  large = false,
  children,
}: BackSectionProps) {
  return (
    <div
      className="rounded-lg border-l-4 overflow-hidden"
      style={{
        borderLeftColor: borderColor,
        backgroundColor: tintColor,
      }}
    >
      {/* Section Header */}
      <div className="flex items-center gap-2 px-5 pt-4 pb-1">
        <span className="text-lg leading-none">{icon}</span>
        <span
          className="font-bold text-sm uppercase tracking-wider"
          style={{ color: borderColor }}
        >
          {label}
        </span>
      </div>
      {/* Section Content */}
      <div className={`px-5 pb-4 ${large ? 'text-xl leading-relaxed' : 'text-lg leading-relaxed'}`}>
        {children}
      </div>
    </div>
  );
}
