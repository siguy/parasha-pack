/**
 * Tiny parser for the card-back markup used in deck.json:
 *
 *   **words**   -> bold: the teacher reads these aloud
 *   [action]    -> cue chip: the teacher or children do this
 *   newline     -> line break
 *
 * Example: 'Day 1: **light!** [Open hands wide]'
 *   -> text "Day 1: ", bold "light!", text " ", cue "Open hands wide"
 */

export type Token =
  | { kind: 'text'; text: string }
  | { kind: 'bold'; text: string }
  | { kind: 'cue'; text: string }
  | { kind: 'break' };

// One alternation per markup kind. The capture group keeps the matches in split().
const MARKUP = /(\*\*[^*]+\*\*|\[[^\]]+\]|\n)/;

export function parseMarkup(source: string): Token[] {
  const tokens: Token[] = [];
  for (const part of source.split(MARKUP)) {
    if (!part) continue;
    if (part === '\n') tokens.push({ kind: 'break' });
    else if (part.startsWith('**') && part.endsWith('**')) tokens.push({ kind: 'bold', text: part.slice(2, -2) });
    else if (part.startsWith('[') && part.endsWith(']')) tokens.push({ kind: 'cue', text: part.slice(1, -1).trim() });
    else tokens.push({ kind: 'text', text: part });
  }
  return tokens;
}

