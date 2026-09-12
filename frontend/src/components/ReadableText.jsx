import { useMemo } from 'react';
import { layoutReadingItems, readingParagraphs } from '../utils/readableText';
import './ReadableText.css';

const DEFAULT_HEADINGS = [
  'Opening',
  'The account continues',
  'Further teaching',
  'Concluding passage',
];

export default function ReadableText({
  text,
  paragraphs,
  className = '',
  paragraphClassName = '',
  hideFootnoteMarkers = false,
  sectionSize = 8,
  subheadings = false,
  headings = DEFAULT_HEADINGS,
  layout = 'comfortable',
}) {
  const items = useMemo(
    () => readingParagraphs(paragraphs || text, { hideFootnoteMarkers }),
    [hideFootnoteMarkers, paragraphs, text],
  );
  const showHeadings = subheadings && layout !== 'points' && items.length > sectionSize + 2;
  const groups = [];

  if (!items.length) return null;

  if (layout === 'points') {
    return (
      <ul className={`readable-text readable-text--points ${className}`.trim()}>
        {items.map((item, index) => (
          <li className={paragraphClassName} key={`${item}-${index}`}>{item}</li>
        ))}
      </ul>
    );
  }

  const displayItems = layoutReadingItems(items, layout);

  for (let index = 0; index < displayItems.length; index += sectionSize) {
    groups.push(displayItems.slice(index, index + sectionSize));
  }

  return (
    <div className={`readable-text readable-text--${layout} ${className}`.trim()}>
      {groups.map((group, groupIndex) => (
        <div className="readable-text__group" key={`${group[0]}-${groupIndex}`}>
          {showHeadings && (() => {
            const headingIndex = Math.min(
              headings.length - 1,
              Math.floor((groupIndex * headings.length) / groups.length),
            );
            const previousIndex = groupIndex === 0 ? -1 : Math.min(
              headings.length - 1,
              Math.floor(((groupIndex - 1) * headings.length) / groups.length),
            );
            return headingIndex !== previousIndex ? (
            <h3 className="readable-text__heading">
              {headings[headingIndex] || DEFAULT_HEADINGS[1]}
            </h3>
            ) : null;
          })()}
          {group.map((paragraph, paragraphIndex) => (
            <p className={paragraphClassName} key={`${paragraph}-${paragraphIndex}`}>{paragraph}</p>
          ))}
        </div>
      ))}
    </div>
  );
}
