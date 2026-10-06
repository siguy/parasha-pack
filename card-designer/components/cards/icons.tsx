/**
 * Inline SVG icons and feeling faces for the cards.
 * Drawn shapes (not emoji) so they print the same everywhere with no licensing worries.
 */
import React from 'react';
import { CardType, FaceKey } from '@/types/card';

const TYPE_PATHS: Record<CardType, string> = {
  anchor: 'M3 18h18l-1.5-10-4.5 4-3-7-3 7-4.5-4z', // crown
  spotlight: 'M12 2l2.9 6.3 6.9.7-5.2 4.6 1.5 6.8L12 17l-6.1 3.4 1.5-6.8L2.2 9l6.9-.7z', // star
  story: 'M3 5c3-1 6-1 9 1 3-2 6-2 9-1v14c-3-1-6-1-9 1-3-2-6-2-9-1z', // open book
  connection: 'M12 21s-8-5.2-8-11a4.5 4.5 0 018-2.8A4.5 4.5 0 0120 10c0 5.8-8 11-8 11z', // heart
  tradition: 'M11 2c-1.5 2-1.5 3.5 0 4.5h2C14.5 5.5 14.5 4 13 2c0 1-1 1.5-1 2s-1-1-1-2zM10 8h4v12h3v2H7v-2h3z', // candle
  power_word: 'M4 4h16v11H9l-5 4z', // speech bubble
  home: 'M12 3l9 8h-3v9h-5v-6h-2v6H6v-9H3z', // house
};

export function TypeIcon({ type }: { type: CardType }) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d={TYPE_PATHS[type]} />
    </svg>
  );
}

/** Goal line marker (a target). */
export function TargetIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2.4">
      <circle cx="12" cy="12" r="9.5" />
      <circle cx="12" cy="12" r="5" />
      <circle cx="12" cy="12" r="1.2" fill="currentColor" />
    </svg>
  );
}

/** Marks things children can do without words. */
export function HandIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M8 12V5.5a1.5 1.5 0 013 0V11V3.5a1.5 1.5 0 013 0V11V4.5a1.5 1.5 0 013 0V12V7.5a1.5 1.5 0 013 0V15a7 7 0 01-7 7h-.6a7 7 0 01-5.9-3.2l-3-4.6a1.6 1.6 0 012.6-1.8z" />
    </svg>
  );
}

/** Teacher guide reference in the footer. */
export function BookIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d={TYPE_PATHS.story} />
    </svg>
  );
}

// ---------- Feeling faces (40x40, yellow circle + features) ----------

const INK = '#1e293b';
const line = { fill: 'none', stroke: INK, strokeWidth: 2.2, strokeLinecap: 'round' as const };

const FACE_FEATURES: Record<FaceKey, React.ReactNode> = {
  happy: (
    <>
      <circle cx="14" cy="16" r="2" fill={INK} />
      <circle cx="26" cy="16" r="2" fill={INK} />
      <path d="M12 24q8 8 16 0" {...line} />
    </>
  ),
  proud: (
    <>
      <path d="M11 16q3-3 6 0M23 16q3-3 6 0" {...line} strokeWidth={2} />
      <path d="M13 25q7 6 14 0" {...line} />
    </>
  ),
  calm: (
    <>
      <path d="M11 17h6M23 17h6" {...line} strokeWidth={2} />
      <path d="M15 26q5 3 10 0" {...line} />
    </>
  ),
  excited: (
    <>
      <circle cx="14" cy="15" r="2.6" fill={INK} />
      <circle cx="26" cy="15" r="2.6" fill={INK} />
      <path d="M11 23h18q-1 9-9 9t-9-9z" fill={INK} />
    </>
  ),
  scared: (
    <>
      <path d="M10 11l6 2M30 11l-6 2" {...line} strokeWidth={2} />
      <circle cx="14" cy="17" r="2.2" fill={INK} />
      <circle cx="26" cy="17" r="2.2" fill={INK} />
      <path d="M12 28q2-2.5 4 0t4 0t4 0t4 0" {...line} strokeWidth={2} />
    </>
  ),
  brave: (
    <>
      <path d="M10 12l6 2.5M30 12l-6 2.5" {...line} strokeWidth={2.4} />
      <circle cx="14" cy="17.5" r="2" fill={INK} />
      <circle cx="26" cy="17.5" r="2" fill={INK} />
      <path d="M13 26q7 4 14 0" {...line} />
    </>
  ),
  sad: (
    <>
      <circle cx="14" cy="16" r="2" fill={INK} />
      <circle cx="26" cy="16" r="2" fill={INK} />
      <path d="M13 29q7-6 14 0" {...line} />
    </>
  ),
  surprised: (
    <>
      <path d="M10 10q4-3 8 0M22 10q4-3 8 0" {...line} strokeWidth={2} />
      <circle cx="14" cy="16" r="2.6" fill={INK} />
      <circle cx="26" cy="16" r="2.6" fill={INK} />
      <ellipse cx="20" cy="27" rx="3.6" ry="4.4" fill={INK} />
    </>
  ),
};

export function FeelingFace({ face }: { face: FaceKey }) {
  return (
    <svg viewBox="0 0 40 40" aria-hidden="true">
      <circle cx="20" cy="20" r="18" fill="#FDE68A" stroke={INK} strokeWidth="1.5" />
      {FACE_FEATURES[face]}
    </svg>
  );
}
