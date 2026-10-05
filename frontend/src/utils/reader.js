export const READER_PREFERENCES_KEY = 'gyansutra-reading-preferences-v1';

export function gitaChapterVerses(records, chapter) {
  const prefix = `bhagavad-gita_${Number(chapter)}_`;
  const seen = new Set();
  return (Array.isArray(records) ? records : []).filter((verse) => {
    if (!verse?.id?.startsWith(prefix) || Number(verse.chapterNumber) !== Number(chapter)
      || (verse.source_id && verse.source_id !== 'bhagavad-gita') || seen.has(verse.id)) return false;
    seen.add(verse.id);
    return true;
  }).sort((a, b) => Number(a.verseNumber) - Number(b.verseNumber));
}

export function readerPreferences(value) {
  return {
    size: [1, 1.15, 1.3].includes(value?.size) ? value.size : 1,
    sanskrit: typeof value?.sanskrit === 'boolean' ? value.sanskrit : true,
  };
}

export function verseIndex(verses, requested, field = 'verseNumber') {
  if (!verses.length) return 0;
  if (requested === 'last') return verses.length - 1;
  const number = Number(requested);
  const index = Number.isSafeInteger(number) && number > 0
    ? verses.findIndex((verse) => Number(verse[field]) === number) : -1;
  return index < 0 ? 0 : index;
}

export function sargaNumber(value, maximum) {
  const number = Number(value);
  return Number.isSafeInteger(number) && number >= 1 && number <= maximum ? number : 1;
}

export function readerArrow(event, overlayOpen = false) {
  if (overlayOpen) return null;
  if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || event.repeat) return null;
  if (event.target?.tagName !== 'BODY' && !event.target?.closest?.('.chapter-reader')) return null;
  if (event.target.closest('input, textarea, select, button, a, summary, [contenteditable], [role="dialog"], [role="slider"]')) return null;
  return event.key === 'ArrowLeft' ? -1 : event.key === 'ArrowRight' ? 1 : null;
}

export function isReaderQueryNavigation(previousPath, currentPath) {
  return previousPath === currentPath && /^\/(?:chapters\/|ramayana\/)/.test(currentPath);
}

export function assistantPrompt({ reference, sectionTitle, text, instruction, language }) {
  // Keep the source excerpt inside the backend question limit; do not imply
  // that the assistant can see the page or that this excerpt is complete.
  const prompt = `For ${reference}, ${instruction} (${sectionTitle}). Answer in ${language}. Distinguish interpretation from translation; do not invent details. Partial source excerpt:\n`;
  return (prompt + String(text || '').slice(0, Math.max(0, 500 - prompt.length))).slice(0, 500);
}
