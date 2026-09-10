'use strict';

const express = require('express');
const corpus = require('../../data/vishnu-purana.json');

const router = express.Router();

function publicMetadata() {
  const { parts, ...metadata } = corpus;
  return metadata;
}

function sectionSummary(section) {
  const { paragraphs, footnotes, ...summary } = section;
  return summary;
}

router.get('/', (_req, res) => {
  res.set('Cache-Control', 'public, max-age=3600, stale-while-revalidate=86400');
  res.json({
    ...publicMetadata(),
    parts: corpus.parts.map(({ sections, ...part }) => ({
      ...part,
      sections: sections.slice(0, 3).map(sectionSummary),
    })),
  });
});

router.get('/:partNumber', (req, res) => {
  const partNumber = Number(req.params.partNumber);
  const part = corpus.parts.find((item) => item.number === partNumber);
  if (!part) return res.status(404).json({ error: 'Vishnu Purana part not found.' });

  res.set('Cache-Control', 'public, max-age=3600, stale-while-revalidate=86400');
  return res.json({
    ...publicMetadata(),
    part: {
      ...part,
      sections: part.sections.map(sectionSummary),
    },
  });
});

router.get('/:partNumber/:sectionNumber', (req, res) => {
  const partNumber = Number(req.params.partNumber);
  const sectionNumber = Number(req.params.sectionNumber);
  const part = corpus.parts.find((item) => item.number === partNumber);
  const section = part?.sections.find((item) => item.sectionNumber === sectionNumber);
  if (!part || !section) return res.status(404).json({ error: 'Vishnu Purana section not found.' });

  res.set('Cache-Control', 'public, max-age=86400, stale-while-revalidate=604800');
  return res.json({
    ...publicMetadata(),
    part: {
      number: part.number,
      roman: part.roman,
      title: part.title,
      theme: part.theme,
      sectionCount: part.sectionCount,
    },
    section,
    previous: sectionNumber > 1
      ? sectionSummary(part.sections[sectionNumber - 2])
      : corpus.parts[partNumber - 2]
        ? sectionSummary(corpus.parts[partNumber - 2].sections.at(-1))
        : null,
    next: sectionNumber < part.sections.length
      ? sectionSummary(part.sections[sectionNumber])
      : corpus.parts[partNumber]
        ? sectionSummary(corpus.parts[partNumber].sections[0])
        : null,
  });
});

module.exports = router;
