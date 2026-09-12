import { test } from 'node:test';
import assert from 'node:assert/strict';
import { cleanReadingText, layoutReadingItems, readingParagraphs, scriptureLines } from './readableText.js';

test('turns source prose into complete readable units without losing text', () => {
  const source = 'The first thought cites M. N. Dutt. The second thought is also complete!';
  const paragraphs = readingParagraphs(source);
  assert.deepEqual(paragraphs, ['The first thought cites M. N. Dutt.', 'The second thought is also complete!']);
  assert.equal(paragraphs.join(' '), source);
});

test('removes visible footnote markers while preserving the source words', () => {
  assert.equal(cleanReadingText('A passage [12] continues.', { hideFootnoteMarkers: true }), 'A passage continues.');
});

test('keeps scripture lines but removes trailing verse references', () => {
  assert.deepEqual(scriptureLines('धर्मक्षेत्रे कुरुक्षेत्रे।\nमामकाः किं अकुर्वत ॥१.१॥'), [
    'धर्मक्षेत्रे कुरुक्षेत्रे।',
    'मामकाः किं अकुर्वत',
  ]);
});

test('reading layouts preserve every sentence and its order', () => {
  const sentences = ['First thought.', 'Second thought.', 'Third thought.'];
  assert.deepEqual(layoutReadingItems(sentences, 'comfortable'), [
    'First thought. Second thought.',
    'Third thought.',
  ]);
  assert.deepEqual(layoutReadingItems(sentences, 'short'), sentences);
  assert.deepEqual(layoutReadingItems(sentences, 'points'), sentences);
});
