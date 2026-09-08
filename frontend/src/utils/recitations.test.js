import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { getPreparedRecording, recordingKey } from './recitations.js';
import { originalMeaning } from './originalMeanings.js';
import inventory from '../data/narrationInventory.json' with { type: 'json' };

test('saved narration must match the exact text, language and section', () => {
  const segment = { locale: 'sa-IN', kind: 'verse', text: 'कर्मण्येवाधिकारस्ते,' };
  const entry = { url: `/narration/${'a'.repeat(64)}.wav` };
  const inventory = { [recordingKey(segment)]: entry };
  assert.equal(getPreparedRecording(segment, inventory), entry);
  for (const change of [{ text: 'Another verse' }, { locale: 'hi-IN' }, { kind: 'translation' }]) {
    assert.equal(getPreparedRecording({ ...segment, ...change }, inventory), null);
  }
});

test('external and legacy recordings cannot enter the inventory', () => {
  const segment = { locale: 'sa-IN', kind: 'verse', text: 'Verse' };
  for (const url of ['https://example.org/audio/2.47.m4a', '//example.org/a.wav', '/narration/../a.wav']) {
    assert.equal(getPreparedRecording(segment, { [recordingKey(segment)]: { url } }), null);
  }
  assert.equal(getPreparedRecording(segment, {}), null);
  const m4a = { url: `/narration/${'b'.repeat(64)}.m4a` };
  assert.equal(getPreparedRecording(segment, { [recordingKey(segment)]: m4a }), m4a);
});

test('original meanings are limited to an identified Gita verse and available language', () => {
  const meanings = { '2.47': { en: 'Original project prose' } };
  const verse = { id: 'bhagavad-gita_2_47', chapterNumber: 2, verseNumber: 47 };
  assert.equal(originalMeaning(verse, 'en', meanings).translation, 'Original project prose');
  assert.equal(originalMeaning({ ...verse, book: 'ramayana' }, 'en', meanings), null);
  assert.equal(originalMeaning({ ...verse, chapterNumber: 1 }, 'en', meanings), null);
  assert.equal(originalMeaning(verse, 'hi', meanings), null);
  assert.equal(originalMeaning(null, 'en', meanings), null);
});

test('every imported narration entry has valid bundled audio and commercial text provenance', async () => {
  assert.equal(Object.keys(inventory).length, 1536);
  const locales = new Set();
  for (const [serialized, entry] of Object.entries(inventory)) {
    const [locale, kind, text] = JSON.parse(serialized);
    locales.add(locale);
    assert.equal(getPreparedRecording({ locale, kind, text }, inventory), entry);
    assert.ok(['public-domain', 'project-original', 'permission-granted'].includes(entry.rights));
    assert.ok(entry.rightsNote);
    const bytes = await readFile(new URL(`../../public${entry.url}`, import.meta.url));
    const wav = bytes.subarray(0, 4).toString() === 'RIFF' && bytes.subarray(8, 12).toString() === 'WAVE';
    const m4a = bytes.subarray(4, 8).toString() === 'ftyp';
    assert.ok(wav || m4a);
    assert.ok(bytes.length > 12 && bytes.length <= 4 * 1024 * 1024);
  }
  assert.deepEqual([...locales].sort(), ['bn-IN', 'en-IN', 'hi-IN', 'mr-IN', 'sa-IN', 'ta-IN', 'te-IN']);
});
