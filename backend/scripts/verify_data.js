'use strict';

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.resolve(__dirname, '../data');
const expectedGitaVerseCount = 701;
const expectedVishnuPartCount = 6;
const expectedVishnuSectionCount = 126;

function readJson(filename) {
  return JSON.parse(fs.readFileSync(path.join(DATA_DIR, filename), 'utf8'));
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function verifyGita(gita) {
  assert(Array.isArray(gita), 'gita.json must be an array.');
  assert(gita.length === expectedGitaVerseCount,
    `gita.json must contain ${expectedGitaVerseCount} verses; found ${gita.length}.`);

  const coordinates = new Set();
  const chapters = new Set();

  for (const verse of gita) {
    const chapter = verse?.chapter_number;
    const number = verse?.verse_number;
    assert(Number.isInteger(chapter) && chapter >= 1 && chapter <= 18,
      `Invalid Gita chapter number: ${chapter}.`);
    assert(Number.isInteger(number) && number >= 1,
      `Invalid Gita verse number in chapter ${chapter}: ${number}.`);
    assert(typeof verse.sanskrit === 'string' && verse.sanskrit.trim(),
      `Gita ${chapter}.${number} is missing Sanskrit text.`);
    assert(typeof verse.english === 'string' && verse.english.trim(),
      `Gita ${chapter}.${number} is missing an English translation.`);
    assert(typeof verse.hindi === 'string' && verse.hindi.trim(),
      `Gita ${chapter}.${number} is missing a Hindi translation.`);

    const coordinate = `${chapter}.${number}`;
    assert(!coordinates.has(coordinate), `Duplicate Gita verse: ${coordinate}.`);
    coordinates.add(coordinate);
    chapters.add(chapter);
  }

  assert(chapters.size === 18, `Expected 18 Gita chapters; found ${chapters.size}.`);
}

function verifyVishnuPurana(corpus) {
  assert(corpus && typeof corpus === 'object' && !Array.isArray(corpus),
    'vishnu-purana.json must be an object.');
  assert(Array.isArray(corpus.parts), 'Vishnu Purana corpus must contain parts.');
  assert(corpus.partCount === expectedVishnuPartCount,
    `Vishnu Purana must declare ${expectedVishnuPartCount} parts.`);
  assert(corpus.parts.length === corpus.partCount,
    'Vishnu Purana partCount does not match the parts array.');

  let sectionTotal = 0;
  corpus.parts.forEach((part, partIndex) => {
    const expectedPartNumber = partIndex + 1;
    assert(part.number === expectedPartNumber,
      `Expected Vishnu Purana part ${expectedPartNumber}; found ${part.number}.`);
    assert(Array.isArray(part.sections), `Part ${part.number} must contain sections.`);
    assert(part.sectionCount === part.sections.length,
      `Part ${part.number} sectionCount does not match its sections array.`);

    part.sections.forEach((section, sectionIndex) => {
      const expectedSectionNumber = sectionIndex + 1;
      assert(section.sectionNumber === expectedSectionNumber,
        `Part ${part.number} has an invalid section number at position ${expectedSectionNumber}.`);
      assert(typeof section.title === 'string' && section.title.trim(),
        `Part ${part.number}, section ${section.sectionNumber} is missing a title.`);
      assert(Array.isArray(section.paragraphs) && section.paragraphs.length > 0,
        `Part ${part.number}, section ${section.sectionNumber} is missing paragraphs.`);
    });

    sectionTotal += part.sections.length;
  });

  assert(corpus.sectionCount === expectedVishnuSectionCount,
    `Vishnu Purana must declare ${expectedVishnuSectionCount} sections.`);
  assert(sectionTotal === corpus.sectionCount,
    'Vishnu Purana sectionCount does not match the total number of sections.');
}

try {
  verifyGita(readJson('gita.json'));
  verifyVishnuPurana(readJson('vishnu-purana.json'));
  console.log('Scripture data contract passed: 701 Gita verses and 126 Vishnu Purana sections.');
} catch (error) {
  console.error(`Scripture data contract failed: ${error.message}`);
  process.exitCode = 1;
}
