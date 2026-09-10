'use strict';

/**
 * Build the app's complete Vishnu Purana reading dataset from M. N. Dutt's
 * public-domain English translation. The table-of-contents descriptions are
 * retained as source-authored reading guides; no generative summaries are
 * inserted into the canonical text.
 *
 * Usage: node scripts/prepare_vishnu_purana.js
 */

const fs = require('fs');
const path = require('path');

const inputPath = path.resolve(__dirname, '../data/raw/vishnu-purana/dutt-1894.txt');
const outputPath = path.resolve(__dirname, '../data/vishnu-purana.json');

const EXPECTED_SECTIONS = [22, 16, 18, 24, 38, 8];
const PARTS = [
  { number: 1, roman: 'I', title: 'Origins of the Cosmos', theme: 'Creation', symbol: '✦' },
  { number: 2, roman: 'II', title: 'The Shape of the Worlds', theme: 'Cosmology', symbol: '◎' },
  { number: 3, roman: 'III', title: 'Sacred Order and Duties', theme: 'Dharma', symbol: '❋' },
  { number: 4, roman: 'IV', title: 'The Rivers of Kings', theme: 'Dynasties', symbol: '♜' },
  { number: 5, roman: 'V', title: 'The Life of Krishna', theme: 'Krishna', symbol: '♢' },
  { number: 6, roman: 'VI', title: 'Dissolution and Freedom', theme: 'Liberation', symbol: '◌' },
];

function cleanWrappedText(value) {
  return String(value || '')
    .replace(/\r/g, '')
    .split(/\n\s*\n/)
    .map((paragraph) => paragraph.replace(/\s*\n\s*/g, ' ').replace(/\s+/g, ' ').trim())
    .filter(Boolean);
}

function titleFromSynopsis(synopsis, sectionNumber) {
  const firstClause = synopsis.split(/(?<=[.!?])\s|;|:\s/)[0].replace(/[.]+$/, '').trim();
  if (!firstClause) return `Section ${sectionNumber}`;
  return firstClause.length <= 92 ? firstClause : `${firstClause.slice(0, 89).trim()}…`;
}

function parseToc(text, bodyStart) {
  const tocText = text.slice(text.indexOf('PART I.'), bodyStart);
  const lines = tocText.split('\n');
  const entries = [];
  let current = null;

  const flush = () => {
    if (!current) return;
    current.synopsis = current.lines.join(' ').replace(/\s+/g, ' ').trim();
    delete current.lines;
    entries.push(current);
    current = null;
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();
    const match = line.match(/^Section\s+[IVXLC]+(?:\.?[—:-]|\.)\s*(.*)$/i);
    if (match) {
      flush();
      current = { lines: [match[1]] };
      continue;
    }
    if (current && line && !/^PART\s+[IVXLC]+[.:]?$/i.test(line)) current.lines.push(line);
  }
  flush();

  const expectedTotal = EXPECTED_SECTIONS.reduce((sum, count) => sum + count, 0);
  if (entries.length !== expectedTotal) {
    throw new Error(`Expected ${expectedTotal} contents entries, found ${entries.length}.`);
  }

  let cursor = 0;
  return EXPECTED_SECTIONS.map((count) => {
    const result = entries.slice(cursor, cursor + count);
    cursor += count;
    return result;
  });
}

function parseFootnotes(text) {
  const notes = {};
  const matches = [...text.matchAll(/^\[(\d+)\]\s+([\s\S]*?)(?=^\[\d+\]\s+|^\*\*\* END OF THE PROJECT GUTENBERG EBOOK)/gm)];
  for (const match of matches) {
    notes[match[1]] = cleanWrappedText(match[2]).join('\n\n');
  }
  return notes;
}

function parseBody(text, bodyStart, tocByPart, footnotes) {
  const footnoteStart = text.indexOf('\n[1] This mystic monosyllable', bodyStart);
  const body = text.slice(bodyStart, footnoteStart > bodyStart ? footnoteStart : undefined);
  const partMatches = [...body.matchAll(/^PART\s+([IVXLC]+)\.\s*$/gm)];

  if (partMatches.length !== PARTS.length) {
    throw new Error(`Expected ${PARTS.length} parts, found ${partMatches.length}.`);
  }

  return PARTS.map((part, partIndex) => {
    const partStart = partMatches[partIndex].index + partMatches[partIndex][0].length;
    const partEnd = partMatches[partIndex + 1]?.index ?? body.length;
    const partText = body.slice(partStart, partEnd).replace(/^\s+/, '');
    const sectionMatches = [...partText.matchAll(/^SECTION\s+([IVXLC]+)\.\s*$/gm)];

    if (sectionMatches.length !== EXPECTED_SECTIONS[partIndex]) {
      throw new Error(`Part ${part.number}: expected ${EXPECTED_SECTIONS[partIndex]} sections, found ${sectionMatches.length}.`);
    }

    const sections = sectionMatches.map((match, sectionIndex) => {
      const start = match.index + match[0].length;
      const end = sectionMatches[sectionIndex + 1]?.index ?? partText.length;
      const raw = partText.slice(start, end)
        .replace(/^\s+/, '')
        .replace(/\s*THE END OF PART [IVXLC]+\.\s*$/i, '')
        .replace(/\s*FINIS\.\s*$/i, '')
        .trim();
      const paragraphs = cleanWrappedText(raw);
      const sectionNumber = sectionIndex + 1;
      const synopsis = tocByPart[partIndex][sectionIndex].synopsis;
      const noteNumbers = [...new Set((raw.match(/\[(\d+)\]/g) || []).map((ref) => ref.slice(1, -1)))];

      return {
        id: `vishnu-purana_${part.number}_${sectionNumber}`,
        partNumber: part.number,
        sectionNumber,
        title: titleFromSynopsis(synopsis, sectionNumber),
        synopsis,
        paragraphs,
        footnotes: noteNumbers
          .filter((number) => footnotes[number])
          .map((number) => ({ number: Number(number), text: footnotes[number] })),
      };
    });

    return { ...part, sectionCount: sections.length, sections };
  });
}

function main() {
  const text = fs.readFileSync(inputPath, 'utf8').replace(/\r/g, '');
  const bodyMarker = '\nPART I.\n\nSECTION I.\n';
  const bodyStart = text.indexOf(bodyMarker, text.indexOf('PART I.') + 1) + 1;
  if (bodyStart <= 0) throw new Error('Could not locate the canonical body.');

  const tocByPart = parseToc(text, bodyStart);
  const footnotes = parseFootnotes(text.slice(bodyStart));
  const parts = parseBody(text, bodyStart, tocByPart, footnotes);
  const sectionCount = parts.reduce((sum, part) => sum + part.sections.length, 0);

  const data = {
    id: 'vishnu-purana',
    title: 'The Vishnu Purana',
    devanagari: 'विष्णुपुराण',
    originalLanguage: 'Sanskrit',
    dialogue: 'Parāśara teaches Maitreya',
    sectionCount,
    partCount: parts.length,
    edition: {
      translation: 'The Vishnu Purana, translated by Manmatha Nath Dutt',
      publicationYear: 1896,
      copyrightStatus: 'Public domain',
      transcriptionSource: 'Project Gutenberg eBook #66208',
      transcriptionUrl: 'https://www.gutenberg.org/ebooks/66208',
      sanskritWitness: 'Jīvānanda Vidyāsāgara edition with Śrīdhara commentary (1882)',
      sanskritWitnessUrl: 'https://archive.org/details/in.ernet.dli.2015.486983',
      sanskritStatus: 'Scan available; OCR transcription withheld pending page-level verification.',
    },
    authenticityNote: 'Story titles and reading guides come from the printed edition’s table of contents. The complete translation is preserved separately and is not rewritten.',
    parts,
  };

  fs.writeFileSync(outputPath, `${JSON.stringify(data, null, 2)}\n`);
  console.log(`Wrote ${sectionCount} sections across ${parts.length} parts to ${outputPath}.`);
}

main();
