import { readFile, writeFile } from 'node:fs/promises';
import { buildNarration } from '../../frontend/src/utils/narration.js';
import { recordingKey } from '../../frontend/src/utils/recitations.js';

const verses = JSON.parse(await readFile(new URL('../data/gita.json', import.meta.url)));
const originals = JSON.parse(await readFile(new URL('../../frontend/src/data/originalMeanings.json', import.meta.url)));
const selected = process.argv.includes('--all-gita') ? verses : verses.filter((v) =>
  (v.chapter_number === 2 && v.verse_number === 47) || (v.chapter_number === 1 && v.verse_number === 1));
const items = new Map();
for (const verse of selected) {
  for (const part of buildNarration({ sanskrit: verse.sanskrit, labels: {} })) {
    items.set(recordingKey(part), { ...part, label: `Gita ${verse.chapter_number}.${verse.verse_number}`,
      rights: 'public-domain', rightsNote: 'Ancient Sanskrit Bhagavad Gita verse; no modern translation or commentary included.' });
  }
}
const examples = [
  ['en-IN', 'Now, the meaning.', 'Take care with the work that is yours to do. You cannot control every result.'],
  ['hi-IN', 'अब इसका अर्थ सुनिए.', 'अपने काम को ध्यान और ईमानदारी से कीजिए। हर परिणाम आपके नियंत्रण में नहीं होता।'],
  ['bn-IN', 'এবার এর অর্থ শুনুন.', 'নিজের কাজ মন দিয়ে করুন। সব ফল আপনার নিয়ন্ত্রণে থাকে না।'],
  ['mr-IN', 'आता याचा अर्थ ऐकूया.', 'आपले काम मनापासून करा. प्रत्येक परिणाम आपल्या हातात नसतो.'],
  ['te-IN', 'ఇప్పుడు దీని అర్థం వినండి.', 'మీ పనిని శ్రద్ధగా చేయండి. ప్రతి ఫలితం మీ చేతిలో ఉండదు.'],
  ['ta-IN', 'இப்போது இதன் பொருளைக் கேளுங்கள்.', 'உங்கள் வேலையை அக்கறையுடன் செய்யுங்கள். எல்லா முடிவுகளும் உங்கள் கட்டுப்பாட்டில் இருப்பதில்லை.'],
];
if (!process.argv.includes('--all-gita')) {
  for (const [locale, heading, example] of examples) {
    for (const [text, demoOnly] of [[heading, false], [example, true]]) {
      const part = { text, locale, kind: 'translation', pause: 950,
        label: `${locale} ${demoOnly ? 'voice sample' : 'meaning introduction'}`, demoOnly,
        rights: 'project-original', rightsNote: 'Original demonstration prose / app section heading, written for GyanSutra. Not a published scripture translation.' };
      items.set(recordingKey(part), part);
    }
  }
  const languageNames = { en: 'english', hi: 'hindi', bn: 'bengali', mr: 'marathi', te: 'telugu', ta: 'tamil' };
  for (const [reference, translations] of Object.entries(originals)) {
    for (const [language, translation] of Object.entries(translations)) {
      const heading = examples.find(([locale]) => locale.startsWith(`${language}-`))[1].replace(/\.$/, '');
      for (const part of buildNarration({ translation, contentLanguage: languageNames[language], labels: { meaningIntro: heading } })) {
        items.set(recordingKey(part), { ...part, label: `Gita ${reference} — ${language} meaning`,
          rights: 'project-original', rightsNote: 'Original AI-assisted GyanSutra meaning of the ancient Sanskrit verse; independent editorial review pending.' });
      }
    }
  }
}
const output = process.argv.find((arg) => arg.startsWith('--output='))?.slice(9);
if (!output) throw new Error('Pass --output=/path/to/queue.json');
await writeFile(output, JSON.stringify([...items.values()], null, 2) + '\n');
console.log(`Prepared ${items.size} narration segments in ${output}`);
