const express = require('express');
const router = express.Router();

router.get('/sitemap.xml', (req, res) => {
  const today = new Date().toISOString().split('T')[0];
  let xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n`;

  const addUrl = (path, priority, changefreq) => {
    xml += `  <url>\n    <loc>https://gyansutraapp.com${path}</loc>\n    <lastmod>${today}</lastmod>\n    <changefreq>${changefreq}</changefreq>\n    <priority>${priority}</priority>\n  </url>\n`;
  };

  // Static pages
  const statics = ['/', '/bhagavad-gita', '/ramayana', '/vishnu-purana'];
  statics.forEach(p => addUrl(p, '0.8', 'monthly'));

  [22, 16, 18, 24, 38, 8].forEach((sectionCount, index) => {
    const part = index + 1;
    addUrl(`/vishnu-purana/${part}`, '0.9', 'monthly');
    for (let section = 1; section <= sectionCount; section++) {
      addUrl(`/vishnu-purana/${part}/${section}`, '0.7', 'yearly');
    }
  });

  xml += `</urlset>`;

  res.header('Content-Type', 'application/xml');
  res.send(xml);
});

module.exports = router;
