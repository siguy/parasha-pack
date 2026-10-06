/**
 * Print formats, read from ../print_formats.json (the single source of truth
 * shared with scripts/export-deck.ts).
 *
 *   letter: 8.5x11 sheet, home printer, 0.3" white margin, no bleed (default)
 *   5x7:    5.25x7.25 sheet for a print shop: 5x7 card + 0.125" bleed, 0.25" safe zone
 */
import formats from '../print_formats.json';

export type FormatId = keyof typeof formats.formats;

export interface PrintFormat {
  page_in: number[]; // [width, height] of the whole sheet, inches
  margin_in?: number; // white paper margin (letter)
  bleed_in: number; // extra card color past the trim line (5x7)
  trim_in?: number[];
  safe_in?: number;
}

export const DEFAULT_FORMAT = formats.default as FormatId;

export function getFormat(id: string | undefined): { id: FormatId; format: PrintFormat } {
  const key = (id && id in formats.formats ? id : DEFAULT_FORMAT) as FormatId;
  return { id: key, format: formats.formats[key] };
}

/** Space between the sheet edge and the card, in inches (margin for letter, bleed for 5x7). */
export function sheetInset(format: PrintFormat): number {
  return format.margin_in ?? format.bleed_in;
}
