const REPLACEMENTS = [
  [/\bart thou\b/gi, 'are you'], [/\bhast thou\b/gi, 'have you'], [/\bdost thou\b/gi, 'do you'],
  [/\bwilt thou\b/gi, 'will you'], [/\bshalt thou\b/gi, 'shall you'], [/\bthou art\b/gi, 'you are'],
  [/\bthou hast\b/gi, 'you have'], [/\bthou dost\b/gi, 'you do'], [/\bthou wilt\b/gi, 'you will'],
  [/\bthou shalt\b/gi, 'you shall'], [/\bthou shouldst\b/gi, 'you should'], [/\bthou wouldst\b/gi, 'you would'],
  [/\bthou couldst\b/gi, 'you could'], [/\bdo thou\b/gi, 'do'], [/\bbe thou\b/gi, 'be'],
  [/\bthou\b/gi, 'you'], [/\bthee\b/gi, 'you'], [/\bthy\b/gi, 'your'], [/\bthine\b/gi, 'your'],
  [/\bye\b/gi, 'you'], [/\bhath\b/gi, 'has'], [/\bdoth\b/gi, 'does'], [/\bsaith\b/gi, 'says'],
  [/\bmaketh\b/gi, 'makes'], [/\bknoweth\b/gi, 'knows'], [/\bthinketh\b/gi, 'thinks'],
  [/\bthinkest\b/gi, 'think'],
  [/\bspeaketh\b/gi, 'speaks'], [/\bspeakest\b/gi, 'speak'], [/\basketh\b/gi, 'asks'], [/\baskest\b/gi, 'ask'],
  [/\btelleth\b/gi, 'tells'], [/\bgiveth\b/gi, 'gives'], [/\bcometh\b/gi, 'comes'], [/\bgoeth\b/gi, 'goes'],
  [/\bunto\b/gi, 'to'], [/\bwherefore\b/gi, 'why'], [/\bwherein\b/gi, 'in which'],
  [/\bwhereof\b/gi, 'of which'], [/\bthereof\b/gi, 'of it'], [/\bherein\b/gi, 'in this'], [/\bwhilst\b/gi, 'while'],
];

function preserveInitialCase(value, replacement) {
  return value[0] === value[0]?.toUpperCase()
    ? `${replacement[0].toUpperCase()}${replacement.slice(1)}`
    : replacement;
}

export function modernizeEnglish(value) {
  if (typeof value !== 'string') return value;
  return REPLACEMENTS.reduce(
    (text, [pattern, replacement]) => text.replace(pattern, (match) => preserveInitialCase(match, replacement)),
    value,
  );
}
