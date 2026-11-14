const DB_NAME = 'gyansutra-local';
const DB_VERSION = 1;
const SARATHI_STORE = 'sarathi';
const CHAT_KEY = 'messages';
const MAX_SAVED_MESSAGES = 40;

const CITATION_KEYS = [
  'id',
  'source_id',
  'book',
  'chapterNumber',
  'verseNumber',
  'kanda',
  'kandaNumber',
  'sarga',
  'shlokaNumber',
  'partNumber',
  'sectionNumber',
  'storyTitle',
  'similarity',
];

function compactCitation(citation) {
  if (!citation || typeof citation !== 'object') return null;
  const slim = {};
  for (const key of CITATION_KEYS) {
    if (citation[key] !== undefined && citation[key] !== null) {
      slim[key] = citation[key];
    }
  }
  return Object.keys(slim).length ? slim : null;
}

export function sanitizeStoredMessages(messages) {
  if (!Array.isArray(messages)) return [];
  return messages
    .filter(
      (msg) => msg
        && typeof msg === 'object'
        && msg.id !== 'welcome'
        && !String(msg.id || '').endsWith('-error')
        && (msg.role === 'user' || msg.role === 'sarathi')
        && typeof msg.content === 'string'
        && msg.content.trim().length > 0,
    )
    .slice(-MAX_SAVED_MESSAGES)
    .map((msg) => ({
      id: String(msg.id),
      role: msg.role,
      content: msg.content,
      citations: Array.isArray(msg.citations)
        ? msg.citations.map(compactCitation).filter(Boolean).slice(0, 6)
        : undefined,
    }));
}

function openDatabase() {
  if (typeof window === 'undefined' || !('indexedDB' in window)) {
    return Promise.resolve(null);
  }
  return new Promise((resolve) => {
    try {
      const request = window.indexedDB.open(DB_NAME, DB_VERSION);
      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains(SARATHI_STORE)) {
          db.createObjectStore(SARATHI_STORE);
        }
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => resolve(null);
      request.onblocked = () => resolve(null);
    } catch {
      resolve(null);
    }
  });
}

export async function getSarathiHistory() {
  const db = await openDatabase();
  if (!db) return [];
  return new Promise((resolve) => {
    try {
      const tx = db.transaction(SARATHI_STORE, 'readonly');
      const req = tx.objectStore(SARATHI_STORE).get(CHAT_KEY);
      req.onsuccess = () => resolve(sanitizeStoredMessages(req.result));
      req.onerror = () => resolve([]);
      tx.oncomplete = () => db.close();
      tx.onerror = () => db.close();
    } catch {
      db.close();
      resolve([]);
    }
  });
}

export async function saveSarathiHistory(messages) {
  const clean = sanitizeStoredMessages(messages);
  const db = await openDatabase();
  if (!db) return false;
  return new Promise((resolve) => {
    try {
      const tx = db.transaction(SARATHI_STORE, 'readwrite');
      const store = tx.objectStore(SARATHI_STORE);
      if (clean.length === 0) {
        store.delete(CHAT_KEY);
      } else {
        store.put(clean, CHAT_KEY);
      }
      tx.oncomplete = () => { db.close(); resolve(true); };
      tx.onerror = () => { db.close(); resolve(false); };
    } catch {
      db.close();
      resolve(false);
    }
  });
}

export async function clearSarathiHistory() {
  return saveSarathiHistory([]);
}
