import test from 'node:test';
import assert from 'node:assert/strict';
import { getSarathiHistory, saveSarathiHistory, sanitizeStoredMessages } from './localDb.js';

test('sanitizeStoredMessages keeps valid user/sarathi turns and strips welcome/errors', () => {
  const cleaned = sanitizeStoredMessages([
    { id: 'welcome', role: 'sarathi', content: 'Welcome' },
    { id: '1-user', role: 'user', content: 'What is karma?' },
    {
      id: '2-sarathi',
      role: 'sarathi',
      content: 'Karma means action [S1].',
      citations: [{ id: 'bhagavad-gita_2_47', chapterNumber: 2, verseNumber: 47, extraLargeText: 'drop' }],
    },
    { id: '3-error', role: 'sarathi', content: 'Network error' },
  ]);

  assert.equal(cleaned.length, 2);
  assert.equal(cleaned[0].id, '1-user');
  assert.equal(cleaned[1].citations[0].id, 'bhagavad-gita_2_47');
  assert.equal(cleaned[1].citations[0].extraLargeText, undefined);
});

test('IndexedDB helpers degrade gracefully when window.indexedDB is unavailable', async () => {
  const history = await getSarathiHistory();
  assert.deepEqual(history, []);
  const saved = await saveSarathiHistory([{ id: '1-user', role: 'user', content: 'Hello' }]);
  assert.equal(saved, false);
});
