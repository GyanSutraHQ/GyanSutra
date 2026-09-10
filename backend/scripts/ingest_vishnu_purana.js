'use strict';

const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../.env') });

const { FieldValue } = require('@google-cloud/firestore');
const { embedText } = require('../src/services/embedding');
const corpus = require('../data/vishnu-purana.json');

const DRY_RUN = process.argv.includes('--dry-run');
const SKIP_EMBED = process.argv.includes('--skip-embed');
const MAX_CHUNK_CHARS = 2_400;

function makeChunks(paragraphs) {
  const chunks = [];
  let current = '';
  for (const paragraph of paragraphs) {
    if (current && current.length + paragraph.length + 2 > MAX_CHUNK_CHARS) {
      chunks.push(current);
      current = '';
    }
    if (paragraph.length > MAX_CHUNK_CHARS) {
      if (current) chunks.push(current);
      for (let offset = 0; offset < paragraph.length; offset += MAX_CHUNK_CHARS) {
        chunks.push(paragraph.slice(offset, offset + MAX_CHUNK_CHARS));
      }
      continue;
    }
    current = current ? `${current}\n\n${paragraph}` : paragraph;
  }
  if (current) chunks.push(current);
  return chunks;
}

async function main() {
  const items = [];

  for (const part of corpus.parts) {
    for (const section of part.sections) {
      const base = {
        source_id: corpus.id,
        book: 'vishnu-purana',
        partNumber: part.number,
        partTitle: part.title,
        sectionNumber: section.sectionNumber,
        storyTitle: section.title,
        storySummary: section.synopsis,
        chapterNumber: part.number,
        verseNumber: section.sectionNumber,
        sanskrit: '',
        transliteration: '',
        translationHindi: '',
        explanationEnglish: section.synopsis,
        sourceText: corpus.edition.translation,
        translationSources: {
          english: {
            author: 'Manmatha Nath Dutt',
            publicationYear: 1896,
            corpus: 'Project Gutenberg eBook #66208',
            type: 'complete public-domain translation',
          },
        },
        sanskritWitness: corpus.edition.sanskritWitness,
        verificationStatus: 'canonical-translation-source-locked',
        verified: true,
        tags: [part.theme.toLowerCase(), 'vishnu purana'],
      };

      // The stable section record powers direct references such as
      // “Vishnu Purana Part 5 Section 3”. Vectorized passages live beside it.
      items.push({
        id: section.id,
        data: {
          ...base,
          translationEnglish: section.paragraphs.join('\n\n'),
          footnotes: section.footnotes,
          passageCount: makeChunks(section.paragraphs).length,
          ragOnly: false,
          embedding: null,
        },
      });

      const chunks = makeChunks(section.paragraphs);
      for (let index = 0; index < chunks.length; index += 1) {
        const passageNumber = index + 1;
        const passage = chunks[index];
        const embeddingText = [
          `Vishnu Purana, Part ${part.number}, Section ${section.sectionNumber}`,
          section.title,
          section.synopsis,
          passage,
        ].join('\n');
        const vector = SKIP_EMBED
          ? null
          : await embedText(embeddingText, { inputType: 'passage' });

        items.push({
          id: `${section.id}_${passageNumber}`,
          data: {
            ...base,
            passageNumber,
            passageCount: chunks.length,
            translationEnglish: passage,
            ragOnly: true,
            embedding: vector ? FieldValue.vector(vector) : null,
          },
        });
      }
    }
  }

  console.log(`Prepared ${items.length} records from ${corpus.sectionCount} complete sections.`);
  if (DRY_RUN) {
    console.log('Dry run complete; Firestore was not changed.');
    return;
  }
  const { batchWrite } = require('../src/services/firestore');
  await batchWrite('verses', items);
  console.log('Vishnu Purana is now available to Sarathi retrieval.');
}

main().catch((error) => {
  console.error('[FATAL] Vishnu Purana ingestion failed:', error.message);
  process.exitCode = 1;
});
