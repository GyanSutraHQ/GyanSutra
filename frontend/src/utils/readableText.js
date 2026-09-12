const FOOTNOTE_MARKER = /\s*\[(?:\d+|[०-९]+)\]/gu;

export function cleanReadingText(value, { hideFootnoteMarkers = false } = {}) {
  let text = String(value || '')
    .replace(/\r\n?/g, '\n')
    .replace(/[^\S\n]+/g, ' ')
    .trim();

  if (hideFootnoteMarkers) text = text.replace(FOOTNOTE_MARKER, '');
  return text;
}

function sentenceUnits(value) {
  const protectedText = value.replace(
    /\b(?:[A-Z]|Mr|Mrs|Ms|Dr|Prof|Sr|Jr|St|vs|etc|e\.g|i\.e)\./gu,
    (match) => match.replaceAll('.', '\uE000'),
  );
  const matches = protectedText.match(/[^.!?।॥]+(?:[.!?।॥]+["'’”)]*|$)/gu);
  return (matches || [protectedText])
    .map((item) => item.replaceAll('\uE000', '.').trim())
    .filter(Boolean);
}

function splitLongUnit(value, maximum) {
  if (value.length <= maximum) return [value];

  const clauses = value.match(/[^;:]+(?:[;:]+|$)/gu)?.map((item) => item.trim()).filter(Boolean) || [];
  if (clauses.length < 2) return [value];

  const result = [];
  let current = '';
  clauses.forEach((clause) => {
    const candidate = current ? `${current} ${clause}` : clause;
    if (current && candidate.length > maximum) {
      result.push(current);
      current = clause;
    } else {
      current = candidate;
    }
  });
  if (current) result.push(current);
  return result;
}

// Reflows source prose without paraphrasing, truncating, or changing its order.
// Each paragraph is a complete sentence, or a complete punctuation-bound clause
// when a Victorian-era source sentence is exceptionally long.
export function readingParagraphs(input, options = {}) {
  const { hideFootnoteMarkers = false, maximum = 210 } = options;
  const source = Array.isArray(input) ? input : [input];

  return source.flatMap((block) => cleanReadingText(block, { hideFootnoteMarkers })
    .split(/\n{2,}/u)
    .flatMap((paragraph) => sentenceUnits(paragraph))
    .flatMap((sentence) => splitLongUnit(sentence, maximum)))
    .map((paragraph) => paragraph.trim())
    .filter(Boolean);
}

// Layout changes presentation only: no sentence is paraphrased, removed, or reordered.
export function layoutReadingItems(items, layout = 'comfortable') {
  if (!Array.isArray(items) || layout === 'short' || layout === 'points') return items || [];

  return items.reduce((result, item, index) => {
    if (index % 2 === 0) result.push(item);
    else result[result.length - 1] = `${result[result.length - 1]} ${item}`;
    return result;
  }, []);
}

export function scriptureLines(value) {
  return cleanReadingText(value)
    .replace(/\s*(?:॥|।|\|){0,2}\s*[०-९\d]+(?:[.।:|-][०-९\d]+)*\s*(?:॥|।|\|){0,2}\s*$/gmu, '')
    .split(/\n+/u)
    .map((line) => line.trim())
    .filter(Boolean);
}
