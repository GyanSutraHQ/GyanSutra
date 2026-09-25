import fs from 'fs';
import path from 'path';
import { SEO_TOPICS } from '../src/data/seoTopics.js';

// This script generates a sitemap.xml for the Gyansutra app.
// It statically maps known routes for the SPA.
const DOMAIN = 'https://gyansutraapp.com';

const routes = [
  { url: '/' },
  { url: '/bhagavad-gita' },
  { url: '/ramayana' },
  { url: '/vishnu-purana' },
  // Verse and chapter readers use client-fetched content. The fully static
  // Vishnu Purana routes below are included because the build emits complete,
  // crawlable HTML for each one.
];

[22, 16, 18, 24, 38, 8].forEach((sectionCount, index) => {
  const part = index + 1;
  routes.push({ url: `/vishnu-purana/${part}` });
  for (let section = 1; section <= sectionCount; section += 1) {
    routes.push({ url: `/vishnu-purana/${part}/${section}` });
  }
});

SEO_TOPICS.forEach(({ slug }) => routes.push({ url: `/topics/${slug}` }));

const generateSitemap = () => {
  let xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`;

  routes.forEach(route => {
    xml += `
  <url>
    <loc>${DOMAIN}${route.url}</loc>
  </url>`;
  });

  xml += `
</urlset>`;

  const publicDir = path.resolve(process.cwd(), 'public');
  
  if (!fs.existsSync(publicDir)) {
    fs.mkdirSync(publicDir, { recursive: true });
  }

  const sitemapPath = path.join(publicDir, 'sitemap.xml');
  fs.writeFileSync(sitemapPath, xml, 'utf8');
  console.log(`Generated sitemap.xml at ${sitemapPath}`);
};

generateSitemap();
