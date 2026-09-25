import fs from 'fs';
import path from 'path';
import { SEO_TOPICS, SEO_TOPIC_BY_SLUG } from '../src/data/seoTopics.js';

const DIST_DIR = path.resolve(process.cwd(), 'dist');
const TEMPLATE_PATH = path.join(DIST_DIR, 'index.html');
const CORPUS_PATH = path.resolve(process.cwd(), '../backend/data/vishnu-purana.json');
const CANONICAL_ORIGIN = 'https://gyansutraapp.com';
const rawBasePath = process.env.VITE_BASE_PATH || '/';
const basePath = rawBasePath.endsWith('/') ? rawBasePath : `${rawBasePath}/`;

if (!fs.existsSync(TEMPLATE_PATH)) {
  throw new Error('dist/index.html is missing. Run this script after Vite builds.');
}

const rawTemplate = fs.readFileSync(TEMPLATE_PATH, 'utf8');
// The generator may be run more than once against the same dist directory.
// Restore the Vite root placeholder when a prior run has already inserted a
// crawlable snapshot, so every route starts from the same application shell.
const template = rawTemplate.replace(
  /<div id="root"><main class="seo-snapshot"[\s\S]*?<\/main><\/div>/,
  '<div id="root"></div>',
);
if (!template.includes('<div id="root"></div>')) {
  throw new Error('Could not find the Vite root placeholder in dist/index.html.');
}
const corpus = JSON.parse(fs.readFileSync(CORPUS_PATH, 'utf8'));

function escapeHtml(value) {
  return String(value || '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function hrefFor(route) {
  const clean = route === '/' ? '' : route.replace(/^\//, '');
  return `${basePath}${clean}`.replace(/\/{2,}/g, '/');
}

function anchor(route, label) {
  return `<a href="${escapeHtml(hrefFor(route))}">${escapeHtml(label)}</a>`;
}

function metadata(html, { route, title, description, type = 'website', schema }) {
  const canonical = `${CANONICAL_ORIGIN}${route === '/' ? '/' : route}`;
  const fullTitle = `${title} | Gyan Sutra`;
  const metaTitle = fullTitle.length > 68 ? `${fullTitle.slice(0, 67).trim()}…` : fullTitle;
  const normalizedDescription = String(description).replace(/\s+/g, ' ').trim();
  const metaDescription = normalizedDescription.length > 158
    ? `${normalizedDescription.slice(0, 157).trim()}…`
    : normalizedDescription;
  let result = html
    .replace(/<title>[\s\S]*?<\/title>/i, `<title>${escapeHtml(metaTitle)}</title>`)
    .replace(/<meta name="description" content="[^"]*"\s*\/>/i, `<meta name="description" content="${escapeHtml(metaDescription)}" />`)
    .replace(/<link rel="canonical" href="[^"]*"\s*\/>/i, `<link rel="canonical" href="${canonical}" />`)
    .replace(/<meta property="og:type" content="[^"]*"\s*\/>/i, `<meta property="og:type" content="${type}" />`)
    .replace(/<meta property="og:url" content="[^"]*"\s*\/>/i, `<meta property="og:url" content="${canonical}" />`)
    .replace(/<meta property="og:title" content="[^"]*"\s*\/>/i, `<meta property="og:title" content="${escapeHtml(metaTitle)}" />`)
    .replace(/<meta property="og:description" content="[^"]*"\s*\/>/i, `<meta property="og:description" content="${escapeHtml(metaDescription)}" />`)
    .replace(/<meta name="twitter:title" content="[^"]*"\s*\/>/i, `<meta name="twitter:title" content="${escapeHtml(metaTitle)}" />`)
    .replace(/<meta name="twitter:description" content="[^"]*"\s*\/>/i, `<meta name="twitter:description" content="${escapeHtml(metaDescription)}" />`);

  result = result.replace(
    '</head>',
    `    <meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large" />\n`
      + `    <style data-seo-snapshot-style>.seo-snapshot{max-width:76rem;margin:0 auto;padding:2rem 1.25rem;font-family:serif;line-height:1.7;color:#241b18}.seo-snapshot nav,.seo-snapshot header,.seo-snapshot article{margin-bottom:2rem}.seo-snapshot li{margin:.45rem 0}.seo-snapshot a{color:#8a531a}.seo-snapshot__text{max-width:48rem}.seo-snapshot__text p{margin:0 0 1.2rem}</style>\n`
      + (schema ? `    <script type="application/ld+json">${JSON.stringify(schema).replaceAll('<', '\\u003c')}</script>\n` : '')
      + '  </head>',
  );
  return result;
}

function page({ route, title, description, content, type, schema }) {
  const snapshot = `<main class="seo-snapshot" data-seo-snapshot>\n`
    + `  <nav>${anchor('/', 'Gyan Sutra scripture library')}</nav>\n`
    + `  <header><h1>${escapeHtml(title)}</h1><p>${escapeHtml(description)}</p></header>\n`
    + `${content}\n`
    + `</main>`;
  const withContent = template.replace('<div id="root"></div>', `<div id="root">${snapshot}</div>`);
  const output = metadata(withContent, { route, title, description, type, schema });
  const outputPath = route === '/'
    ? TEMPLATE_PATH
    : path.join(DIST_DIR, `${route.replace(/^\//, '')}.html`);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, output, 'utf8');
}

const bookSchema = {
  '@context': 'https://schema.org',
  '@type': 'Book',
  name: 'The Vishnu Purana',
  inLanguage: 'en',
  translator: { '@type': 'Person', name: 'Manmatha Nath Dutt' },
  datePublished: '1896',
  isAccessibleForFree: true,
  url: `${CANONICAL_ORIGIN}/vishnu-purana`,
};

page({
  route: '/',
  title: 'Gita, Ramayana and Vishnu Purana',
  description: 'Read the Bhagavad Gita, Valmiki Ramayana, and complete Vishnu Purana with source-grounded translations, notes, audio, and Sarathi guidance.',
  content: `<section><h2>Scripture library</h2><ul><li>${anchor('/bhagavad-gita', 'Bhagavad Gita')}</li><li>${anchor('/ramayana', 'Valmiki Ramayana')}</li><li>${anchor('/vishnu-purana', 'The complete Vishnu Purana')}</li></ul></section><section><h2>Bhagavad Gita study guides</h2><ul>${SEO_TOPICS.map((topic) => `<li>${anchor(`/topics/${topic.slug}`, topic.h1)} — ${escapeHtml(topic.description)}</li>`).join('')}</ul></section>`,
});

for (const topic of SEO_TOPICS) {
  const route = `/topics/${topic.slug}`;
  const content = `<article><p>${anchor('/bhagavad-gita', 'Bhagavad Gita')}</p>${topic.sections.map((section) => `<section><h2>${escapeHtml(section.heading)}</h2><p>${escapeHtml(section.body)}</p></section>`).join('')}<section><h2>Read the source passages</h2><p>These passages provide the textual basis for this guide.</p><ul>${topic.sources.map((source) => `<li>${anchor(source.path, source.label)}</li>`).join('')}</ul></section><section><h2>Related guides</h2><ul>${topic.related.map((relatedSlug) => { const related = SEO_TOPIC_BY_SLUG[relatedSlug]; return `<li>${anchor(`/topics/${relatedSlug}`, related.h1)}</li>`; }).join('')}</ul></section></article>`;
  page({
    route,
    title: topic.title,
    description: topic.description,
    content,
    type: 'article',
    schema: {
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline: topic.title,
      description: topic.description,
      mainEntityOfPage: `${CANONICAL_ORIGIN}${route}`,
      isAccessibleForFree: true,
      about: ['Bhagavad Gita', 'Hindu philosophy'],
    },
  });
}

page({
  route: '/bhagavad-gita',
  title: 'Bhagavad Gita',
  description: 'Read all 18 chapters of the Bhagavad Gita with Sanskrit, transliteration, translations, commentary, and independent audio controls.',
  content: '<article><h2>All 18 chapters</h2><p>Krishna and Arjuna discuss duty, action, devotion, self-knowledge, and liberation.</p></article>',
  type: 'book',
});

page({
  route: '/ramayana',
  title: 'Valmiki Ramayana',
  description: 'Read the Valmiki Ramayana across its seven kandas, from Rama’s early life through exile, war, return, and final departure.',
  content: '<article><h2>Seven kandas</h2><p>Bala, Ayodhya, Aranya, Kishkindha, Sundara, Yuddha, and Uttara Kanda.</p></article>',
  type: 'book',
});

page({
  route: '/vishnu-purana',
  title: 'The Complete Vishnu Purana',
  description: 'Read all six parts and 126 sections of Manmatha Nath Dutt’s complete 1896 public-domain translation of the Vishnu Purana.',
  content: `<article><h2>Six-part source journey</h2><ol>${corpus.parts.map((part) => `<li>${anchor(`/vishnu-purana/${part.number}`, `Part ${part.roman}: ${part.title}`)} — ${escapeHtml(part.theme)}, ${part.sectionCount} sections</li>`).join('')}</ol></article>`,
  type: 'book',
  schema: bookSchema,
});

for (const part of corpus.parts) {
  const route = `/vishnu-purana/${part.number}`;
  const description = `Read all ${part.sectionCount} source sections in Part ${part.roman}, ${part.title}, of the Vishnu Purana.`;
  page({
    route,
    title: `Part ${part.roman}: ${part.title} — Vishnu Purana`,
    description,
    content: `<article><p>${anchor('/vishnu-purana', 'All six parts')}</p><h2>${escapeHtml(part.theme)}</h2><ol>${part.sections.map((section) => `<li>${anchor(`${route}/${section.sectionNumber}`, `Section ${section.sectionNumber}: ${section.title}`)}<p>${escapeHtml(section.synopsis)}</p></li>`).join('')}</ol></article>`,
    type: 'book',
    schema: { ...bookSchema, name: `Vishnu Purana, Part ${part.roman}: ${part.title}`, url: `${CANONICAL_ORIGIN}${route}`, isPartOf: bookSchema },
  });

  for (const section of part.sections) {
    const sectionRoute = `${route}/${section.sectionNumber}`;
    const sectionTitle = `${section.title} — Vishnu Purana ${part.roman}.${section.sectionNumber}`;
    page({
      route: sectionRoute,
      title: sectionTitle,
      description: section.synopsis,
      content: `<article><p>${anchor(route, `Part ${part.roman}: ${part.title}`)}</p><h2>Source reading guide</h2><p>${escapeHtml(section.synopsis)}</p><h2>Complete M. N. Dutt translation</h2><div class="seo-snapshot__text">${section.paragraphs.map((paragraph) => `<p>${escapeHtml(paragraph)}</p>`).join('')}</div>${section.footnotes.length > 0 ? `<h2>Translator’s notes</h2><ol>${section.footnotes.map((note) => `<li value="${note.number}">${escapeHtml(note.text)}</li>`).join('')}</ol>` : ''}</article>`,
      type: 'article',
      schema: {
        '@context': 'https://schema.org',
        '@type': 'Article',
        headline: sectionTitle,
        description: section.synopsis,
        inLanguage: 'en',
        isAccessibleForFree: true,
        url: `${CANONICAL_ORIGIN}${sectionRoute}`,
        translator: { '@type': 'Person', name: 'Manmatha Nath Dutt' },
        isPartOf: bookSchema,
      },
    });
  }
}

const sitemap = fs.readFileSync(path.resolve(process.cwd(), 'public/sitemap.xml'), 'utf8');
const sitemapRoutes = [...sitemap.matchAll(/<loc>https:\/\/gyansutraapp\.com([^<]*)<\/loc>/g)]
  .map((match) => match[1] || '/');
for (const route of sitemapRoutes) {
  const outputPath = route === '/'
    ? TEMPLATE_PATH
    : path.join(DIST_DIR, `${route.replace(/^\//, '')}.html`);
  if (!fs.existsSync(outputPath)) throw new Error(`Sitemap route has no static HTML: ${route}`);
  const html = fs.readFileSync(outputPath, 'utf8');
  const canonical = `${CANONICAL_ORIGIN}${route}`;
  if (!html.includes(`<link rel="canonical" href="${canonical}"`)) {
    throw new Error(`Incorrect canonical for ${route}`);
  }
}

console.log(`Generated and verified ${sitemapRoutes.length} indexable HTML pages in ${DIST_DIR}.`);
