/**
 * Tests for the card-back markup parser (lib/markup.ts).
 *
 * Run:  npm test   (uses Node's built-in test runner through tsx, no extra packages)
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseMarkup } from './markup';

test('plain text is one text token', () => {
  assert.deepEqual(parseMarkup('Hello class'), [{ kind: 'text', text: 'Hello class' }]);
});

test('bold, cue and text mixed in one line', () => {
  assert.deepEqual(parseMarkup('Day 1: **light!** [Open hands wide]'), [
    { kind: 'text', text: 'Day 1: ' },
    { kind: 'bold', text: 'light!' },
    { kind: 'text', text: ' ' },
    { kind: 'cue', text: 'Open hands wide' },
  ]);
});

test('newline becomes a break token', () => {
  assert.deepEqual(parseMarkup('**One**\n**Two**'), [
    { kind: 'bold', text: 'One' },
    { kind: 'break' },
    { kind: 'bold', text: 'Two' },
  ]);
});

test('cue text is trimmed', () => {
  assert.deepEqual(parseMarkup('[  Roar!  ]'), [{ kind: 'cue', text: 'Roar!' }]);
});

test('quotes and punctuation inside bold are kept', () => {
  assert.deepEqual(parseMarkup('**Hashem said, "Let there be light!"**'), [
    { kind: 'bold', text: 'Hashem said, "Let there be light!"' },
  ]);
});

test('unclosed markup stays as plain text', () => {
  assert.deepEqual(parseMarkup('**not closed [nor this'), [{ kind: 'text', text: '**not closed [nor this' }]);
});

test('empty string gives no tokens', () => {
  assert.deepEqual(parseMarkup(''), []);
});

test('Hebrew inside bold', () => {
  assert.deepEqual(parseMarkup('**טוֹב!** [Thumbs up!]'), [
    { kind: 'bold', text: 'טוֹב!' },
    { kind: 'text', text: ' ' },
    { kind: 'cue', text: 'Thumbs up!' },
  ]);
});
