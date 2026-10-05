import { useState } from 'react';
import { readerPreferences, READER_PREFERENCES_KEY } from '../utils/reader';

export default function useReaderPreferences() {
  const [preferences, setPreferences] = useState(() => {
    try { return readerPreferences(JSON.parse(window.localStorage.getItem(READER_PREFERENCES_KEY))); }
    catch { return readerPreferences(); }
  });
  const update = (patch) => {
    const next = readerPreferences({ ...preferences, ...patch });
    setPreferences(next);
    try { window.localStorage.setItem(READER_PREFERENCES_KEY, JSON.stringify(next)); } catch { /* Storage can be unavailable in private mode. */ }
  };
  return [preferences, update];
}
