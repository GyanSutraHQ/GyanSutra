import { after, before, test } from 'node:test';
import assert from 'node:assert/strict';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { MemoryRouter } from 'react-router-dom';
import { createServer } from 'vite';
import react from '@vitejs/plugin-react';

let server, Card, LanguageContext;
const oldWindow = globalThis.window;

before(async () => {
  // Import the browser-only audio service without starting speech or a request.
  globalThis.window = { fetch: globalThis.fetch, Audio: class {}, addEventListener() {}, removeEventListener() {} };
  server = await createServer({ configFile: false, plugins: [react()], server: { middlewareMode: true, hmr: false, ws: false }, appType: 'custom' });
  Card = (await server.ssrLoadModule('/src/components/IlluminatedVerseCard.jsx')).default;
  LanguageContext = (await server.ssrLoadModule('/src/i18n/languageState.js')).default;
});

after(async () => {
  await server?.close();
  if (oldWindow === undefined) delete globalThis.window; else globalThis.window = oldWindow;
});

const verse = {
  id: 'bhagavad-gita_1_1', book: 'bhagavad-gita', chapterNumber: 1, verseNumber: 1,
  sanskrit: 'धर्मक्षेत्रे कुरुक्षेत्रे', transliteration: 'dharmakṣetre kurukṣetre',
  translationEnglish: 'Thou art reading the published source.',
  translationHindi: 'मूल अनुवाद पढ़ें।',
  translationSources: { english: { author: 'Source translator' }, hindi: { author: 'Hindi translator' } },
  detailedExplanations: [{ author: 'Commentator', language: 'english', explanation: 'A complete source commentary.' }],
};

function render(record = verse, language = 'en', preferences = null, variant = 'full') {
  globalThis.window.localStorage = { getItem: () => JSON.stringify(preferences) };
  return renderToStaticMarkup(React.createElement(MemoryRouter, null,
    React.createElement(LanguageContext.Provider, { value: { language, t: (key) => key } },
      React.createElement(Card, { verse: record, variant }))));
}

test('published wording and named authors remain distinct from optional AI-assisted meanings', () => {
  const html = render();
  assert.match(html, /Thou art reading the published source\./);
  assert.doesNotMatch(html, /You are reading the published source\./);
  assert.match(html, /Translated by Source translator/);
  assert.match(html, /AI-assisted meaning · editorial review pending/);
  assert.match(html, /A complete source commentary\./);
  assert.match(html, /gitasupersite\.iitk\.ac\.in/);
  assert.doesNotMatch(html, /<details[^>]* open/);
});

test('reading preferences enlarge the text and hide Sanskrit without removing translation or listening', () => {
  const html = render(verse, 'en', { size: 1.3, sanskrit: false });
  assert.match(html, /--reader-scale:1.3/);
  assert.doesNotMatch(html, /class="verse-card__sanskrit/);
  assert.match(html, /Thou art reading the published source/);
  assert.match(html, /Listen to this passage/);
  assert.match(html, /aria-pressed="true"/);
});

test('Ramayana uses its own location and reference source; compact cards stay concise', () => {
  const ramayana = { ...verse, id: 'valmiki-ramayana_1_1_1', book: 'ramayana', kanda: 'Bala Kanda', sarga: 1, shlokaNumber: 1, verified: false };
  const full = render(ramayana);
  assert.match(full, /Bala Kanda, Sarga 1, Shloka 1/);
  assert.match(full, /valmikiramayan\.net/);
  assert.match(full, /Independent editorial verification/);
  assert.match(full, /Supporting text · unreviewed/);
  assert.match(full, /AI-generated additions/);
  const matched = render({ ...ramayana, source: 'rahular/itihasa', verificationStatus: 'source-matched' });
  assert.doesNotMatch(matched, /Supporting text · unreviewed/);
  assert.match(matched, /source-matched/);
  const compact = render(verse, 'en', null, 'compact');
  assert.doesNotMatch(compact, /Reading comfort|Listen to this passage|Traditional commentaries/);
});

test('Hindi source translation is correctly labeled for assistive technology', () => {
  const html = render(verse, 'hi');
  assert.match(html, /lang="hi"/);
  assert.match(html, /मूल अनुवाद पढ़ें/);
  assert.match(html, /Hindi translator/);
});

test('an existing generated meaning stays labeled as AI-assisted in its own language', () => {
  const html = render(verse, 'bn');
  assert.match(html, /এআই-সহায়তায় অর্থ · সম্পাদকীয় যাচাই বাকি/);
  assert.match(html, /lang="bn"/);
  assert.doesNotMatch(html, /Translated by Source translator/);
});
