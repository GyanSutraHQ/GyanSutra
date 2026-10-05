import { test } from 'node:test';
import assert from 'node:assert/strict';
import { gitaChapterVerses, readerPreferences, verseIndex, sargaNumber, readerArrow, assistantPrompt, isReaderQueryNavigation } from './reader.js';

test('Gita chapters exclude other scriptures and retain sorted, unique canonical verses', () => {
  const first = { id: 'bhagavad-gita_1_1', chapterNumber: 1, verseNumber: 1 };
  const second = { id: 'bhagavad-gita_1_2', source_id: 'bhagavad-gita', chapterNumber: 1, verseNumber: 2 };
  assert.deepEqual(gitaChapterVerses([
    second, { id: 'vishnu-purana_1_1', source_id: 'vishnu-purana', chapterNumber: 1, verseNumber: 1 },
    first, first, { ...first, source_id: 'vishnu-purana' },
    { id: 'bhagavad-gita_2_1', chapterNumber: 2, verseNumber: 1 },
  ], 1), [first, second]);
  assert.deepEqual(gitaChapterVerses(null, 1), []);
});

test('reader links resolve actual verse numbers and the last verse of a previous sarga', () => {
  const verses = [{ shlokaNumber: 1 }, { shlokaNumber: 3 }, { shlokaNumber: 4 }];
  assert.equal(verseIndex(verses, '3', 'shlokaNumber'), 1);
  assert.equal(verseIndex(verses, 'last', 'shlokaNumber'), 2);
  for (const input of [null, 'missing', '-2', '2', '1.5']) assert.equal(verseIndex(verses, input, 'shlokaNumber'), 0);
  assert.equal(verseIndex([], 'last'), 0);
});

test('invalid saved preferences and sarga links fall back to usable reader defaults', () => {
  assert.deepEqual(readerPreferences({ size: 100, sanskrit: 'false' }), { size: 1, sanskrit: true });
  assert.deepEqual(readerPreferences({ size: 1.3, sanskrit: false }), { size: 1.3, sanskrit: false });
  for (const input of ['0', '78', '-1', '1.5', 'invalid', null]) assert.equal(sargaNumber(input, 77), 1);
  assert.equal(sargaNumber('77', 77), 77);
});

test('arrow shortcuts never override interactive controls, assistant panels or modifier keys', () => {
  const target = (inReader, interactive) => ({ closest: (selector) => selector === '.chapter-reader' ? inReader : interactive });
  assert.equal(readerArrow({ key: 'ArrowRight', target: target(true, false) }), 1);
  assert.equal(readerArrow({ key: 'ArrowLeft', target: target(true, false) }), -1);
  assert.equal(readerArrow({ key: 'ArrowRight', target: target(true, true) }), null);
  assert.equal(readerArrow({ key: 'ArrowRight', target: target(false, false) }), null);
  const page = { ...target(false, false), tagName: 'BODY' };
  assert.equal(readerArrow({ key: 'ArrowRight', target: page }), 1);
  assert.equal(readerArrow({ key: 'ArrowRight', target: page }, true), null);
  for (const flag of ['defaultPrevented', 'ctrlKey', 'metaKey', 'altKey', 'shiftKey', 'repeat']) {
    assert.equal(readerArrow({ key: 'ArrowRight', target: target(true, false), [flag]: true }), null);
  }
});

test('only query navigation within the same reader preserves its reading position', () => {
  assert.equal(isReaderQueryNavigation('/chapters/chapter_1', '/chapters/chapter_1'), true);
  assert.equal(isReaderQueryNavigation('/ramayana/1', '/ramayana/1'), true);
  assert.equal(isReaderQueryNavigation('/chapters/chapter_1', '/chapters/chapter_2'), false);
  assert.equal(isReaderQueryNavigation('/search', '/search'), false);
  assert.equal(isReaderQueryNavigation('/ramayana', '/ramayana'), false);
});

test('assistant prompts preserve the passage reference and respect the live API limit', () => {
  const options = { reference: 'Valmiki Ramayana 1.1.1', sectionTitle: 'Translation', instruction: 'explain simply', language: 'Hindi' };
  const prompt = assistantPrompt({ ...options, text: 'Source sentence. '.repeat(300) });
  assert.ok(prompt.length <= 500);
  assert.match(prompt, /Valmiki Ramayana 1\.1\.1/);
  assert.match(prompt, /Answer in Hindi/);
  assert.match(prompt, /Partial source excerpt/);
  assert.match(prompt, /Source sentence/);
});
