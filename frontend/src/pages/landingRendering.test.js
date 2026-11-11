import { after, before, test } from 'node:test';
import assert from 'node:assert/strict';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { MemoryRouter } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { createServer } from 'vite';
import react from '@vitejs/plugin-react';
import { LANDING_FAQS, LANDING_SCHEMA } from '../data/landing.js';
import { SCRIPTURE_TRADITIONS } from '../data/scriptureTraditions.js';

let server, Home, LanguageContext, renderLanding;
before(async () => {
  server = await createServer({ configFile: false, plugins: [react()], server: { middlewareMode: true, hmr: false, ws: false }, appType: 'custom' });
  Home = (await server.ssrLoadModule('/src/pages/Home.jsx')).default;
  LanguageContext = (await server.ssrLoadModule('/src/i18n/languageState.js')).default;
  renderLanding = (await server.ssrLoadModule('/src/landing-entry.jsx')).renderLanding;
});
after(async () => { await server?.close(); });

function render(language = 'en') {
  return renderToStaticMarkup(React.createElement(HelmetProvider, { context: {} },
    React.createElement(MemoryRouter, null,
      React.createElement(LanguageContext.Provider, { value: { language, t: (key) => key } },
        React.createElement(Home)))));
}

test('homepage is meaningful without JavaScript or an API response', () => {
  const html = renderLanding();
  assert.match(html, /Many scriptures\./);
  assert.match(html, /One living thread\./);
  assert.equal((html.match(/<h1\b/g) || []).length, 1);
  for (const path of ['/bhagavad-gita', '/ramayana', '/vishnu-purana', '/topics/karma-yoga']) assert.ok(html.includes(`href="${path}"`));
  assert.match(html, /Swami Sivananda/);
  assert.match(html.replace(/<!--[\s\S]*?-->/g, ''), /Bhagavad Gita 2\.47/);
  assert.doesNotMatch(html, /<title>|<meta |application\/ld\+json/);
  assert.match(html, /id="main-content"/);
  assert.doesNotMatch(html, /language-welcome/);
  assert.equal((html.match(/<details\b/g) || []).length, LANDING_FAQS.length);
});

test('all six interface languages render and mark the Sanskrit and fallback English', () => {
  for (const language of ['en', 'hi', 'bn', 'mr', 'te', 'ta']) {
    const html = render(language);
    assert.match(html, /lang="sa"/);
    assert.match(html, language === 'hi' ? /translation" lang="hi"/ : /translation" lang="en"/);
    assert.match(html, /aria-pressed="false"/);
    assert.doesNotMatch(html, /undefined/);
  }
});

test('static landing links respect deployments under a base path', () => {
  const html = renderLanding('/library/');
  assert.match(html, /href="\/library\/bhagavad-gita"/);
  assert.match(html, /href="\/library\/topics\/karma-yoga"/);
  assert.match(html, /href="\/library\/vedas"/);
  assert.match(html, /href="\/library\/upanishads"/);
});

test('real cinematic imagery is rendered for hero, traditions, books, and companion', () => {
  const html = renderLanding();
  for (const image of [
    'images/landing/hero-landscape.jpg',
    'images/landing/gita-card.jpg',
    'images/landing/ramayana-card.jpg',
    'images/landing/purana-card.jpg',
    'images/landing/tradition-vedas.jpg',
    'images/landing/tradition-upanishads.jpg',
    'images/landing/tradition-itihasas.jpg',
    'images/landing/tradition-puranas.jpg',
    'images/landing/sarathi-companion.jpg',
  ]) {
    assert.ok(html.includes(image), `Missing landing artwork: ${image}`);
  }
});

test('structured data describes real texts without fabricated ratings or traffic', () => {
  const collection = LANDING_SCHEMA['@graph'].find((entry) => entry['@type'] === 'ItemList');
  assert.equal(collection.itemListElement.length, 3);
  assert.equal(new Set(collection.itemListElement.map((entry) => entry.url)).size, 3);
  assert.doesNotMatch(JSON.stringify(LANDING_SCHEMA), /aggregateRating|reviewCount/);
});

test('wider scripture identity is clearly separated from published collections', () => {
  const html = renderLanding();
  assert.equal(SCRIPTURE_TRADITIONS.length, 4);
  for (const tradition of SCRIPTURE_TRADITIONS) assert.ok(html.includes(tradition.name));
  const upcoming = SCRIPTURE_TRADITIONS.filter(({ status }) => status === 'In preparation');
  assert.deepEqual(upcoming.map(({ id }) => id), ['vedas', 'upanishads']);
  assert.ok(upcoming.every(({ path }) => path === '/faq'));
  assert.match(html, /Explore the scripture landscape/);
  assert.match(html, /data-world="itihasas"/);
  assert.equal((html.match(/class="gs-scene__flag"/g) || []).length, 10);
});
