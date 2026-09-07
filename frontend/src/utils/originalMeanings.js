// Original project prose, not copied from a named modern translation.
export function originalMeaning(verse, language, meanings) {
  const book = verse?.source_id || verse?.book || (verse?.id?.startsWith('bhagavad-gita_') ? 'bhagavad-gita' : undefined);
  if (book !== 'bhagavad-gita' || verse?.kanda) return null;
  const translation = meanings[`${verse.chapterNumber}.${verse.verseNumber}`]?.[language];
  return translation ? { translation, basedOn: { author: 'GyanSutra (original AI-assisted meaning)' } } : null;
}
