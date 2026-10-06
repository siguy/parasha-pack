/**
 * Tests for the card labels (lib/cardTypes.ts): a sequence deck's story cards read "Day N".
 *
 * Run:  npm test
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { backHeaderLabel, typeLabel, weekDayLabel } from './cardTypes';

const standard = {};
const sequence = { deck_pattern: 'sequence' as const };
const story3 = { card_type: 'story' as const, sequence_number: 3 };
const spotlight = { card_type: 'spotlight' as const };

test('standard deck story back says Story N', () => {
  assert.equal(backHeaderLabel(story3, standard), 'Story 3');
  assert.equal(typeLabel(story3, standard), 'Story');
});

test('sequence deck story back and chip say Day N', () => {
  assert.equal(backHeaderLabel(story3, sequence), 'Day 3');
  assert.equal(typeLabel(story3, sequence), 'Day');
});

test('other card types keep their label in a sequence deck', () => {
  assert.equal(backHeaderLabel(spotlight, sequence), 'Spotlight');
});

test('week plan uses weekdays in a sequence deck, Day N otherwise', () => {
  assert.equal(weekDayLabel(1, sequence), 'Mon');
  assert.equal(weekDayLabel(5, sequence), 'Fri');
  assert.equal(weekDayLabel(2, standard), 'Day 2');
});
