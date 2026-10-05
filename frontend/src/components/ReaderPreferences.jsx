import { READER_TOOLS_COPY } from '../utils/readerCopy';

export default function ReaderPreferences({ language, preferences, onChange, hasSanskrit = true }) {
  const labels = READER_TOOLS_COPY[language] || READER_TOOLS_COPY.en;
  return (
    <div className="reader-preferences" role="group" aria-label={labels.settings}>
      <span className="reader-preferences__label">{labels.settings}</span>
      <div className="reader-preferences__sizes" role="group" aria-label={labels.size}>
        {[1, 1.15, 1.3].map((size, index) => <button type="button" key={size} aria-label={`${labels.size} ${Math.round(size * 100)}%`} aria-pressed={preferences.size === size} onClick={() => onChange({ size })}><span style={{ fontSize: `${0.85 + index * 0.15}rem` }} aria-hidden="true">A</span></button>)}
      </div>
      {hasSanskrit && <label className="reader-preferences__original"><input type="checkbox" checked={preferences.sanskrit} onChange={(event) => onChange({ sanskrit: event.target.checked })} />{labels.original}</label>}
    </div>
  );
}
