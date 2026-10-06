/**
 * CardFrame - the sheet of paper one card side is printed on.
 *
 *   letter: white 8.5x11 sheet, the card sits inside a 0.3" margin
 *   5x7:    5.25x7.25 sheet, the card fills the trim and the 0.125" bleed
 *           around it is the card color (so a slightly-off cut still looks right)
 *
 * The sheet keeps the format's exact proportions at any width, so the same
 * frame is used on screen, in PNG export and in the PDF.
 */
import React from 'react';
import { getFormat, sheetInset } from '@/lib/formats';

interface CardFrameProps {
  format?: string;
  color: string; // card-type color (used for the 5x7 bleed)
  children: React.ReactNode;
}

export function CardFrame({ format, color, children }: CardFrameProps) {
  const { id, format: f } = getFormat(format);
  const [pageW, pageH] = f.page_in;
  // cqw = % of the wrapper width, which is the sheet width
  const insetCqw = (sheetInset(f) / pageW) * 100;

  return (
    <div className="pp-sheet-wrap">
      <div
        className="pp-sheet"
        data-format={id}
        style={
          {
            '--c': color,
            aspectRatio: `${pageW} / ${pageH}`,
            padding: `${insetCqw}cqw`,
          } as React.CSSProperties
        }
      >
        {children}
      </div>
    </div>
  );
}
