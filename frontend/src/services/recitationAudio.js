const CACHE_NAME = 'gyansutra-recitations-v2';
const MAX_RECORDING_BYTES = 4 * 1024 * 1024;
const MAX_RECORDINGS = 32; // At most 128 MiB, typically much less.

export function createRecitationFetcher({ fetch: fetchAudio, caches, online }) {
  // Purge the old noncommercial audio cache, even on offline app launch.
  const migrated = Promise.resolve().then(() => caches?.delete?.('gyansutra-recitations-v1')).catch(() => {});
  return async function fetchRecitationAudio(recording, signal) {
    const checkAbort = () => { if (signal.aborted) throw new DOMException('Stopped', 'AbortError'); };
    checkAbort();
    await migrated;
    const cache = await caches?.open?.(CACHE_NAME).catch(() => null);
    const cached = await cache?.match(recording.url).catch(() => null);
    checkAbort();
    if (cached) return cached.blob();
    // Same-origin files may be bundled in an offline Capacitor application.
    if (!online() && !recording.url.startsWith('/narration/')) throw new Error('Recording is not downloaded');

    const controller = new AbortController();
    const abort = () => controller.abort();
    signal.addEventListener('abort', abort, { once: true });
    const timeout = setTimeout(abort, 12_000);
    try {
      checkAbort();
      const response = await fetchAudio(recording.url, { signal: controller.signal, credentials: 'omit' });
      if (!response.ok) throw new Error('Recording unavailable');
      if (Number(response.headers.get('content-length')) > MAX_RECORDING_BYTES) throw new Error('Recording too large');
      const reader = response.body.getReader();
      const chunks = [];
      let size = 0;
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        size += value.byteLength;
        if (size > MAX_RECORDING_BYTES) { await reader.cancel(); throw new Error('Recording too large'); }
        chunks.push(value);
      }
      const raw = new Blob(chunks);
      const header = new TextDecoder().decode(await raw.slice(0, 12).arrayBuffer());
      const type = header.startsWith('RIFF') && header.slice(8, 12) === 'WAVE'
        ? 'audio/wav' : header.slice(4, 8) === 'ftyp' ? 'audio/mp4' : null;
      if (!type) throw new Error('Invalid recording');
      const blob = new Blob(chunks, { type });
      checkAbort();
      // Cache failures must not interrupt otherwise playable audio.
      if (cache) {
        try {
          await cache.put(recording.url, new Response(blob, { headers: { 'Content-Type': type } }));
          const keys = await cache.keys();
          for (const key of keys.slice(0, Math.max(0, keys.length - MAX_RECORDINGS))) await cache.delete(key);
        } catch { /* Storage may be disabled or full. */ }
      }
      checkAbort();
      return blob;
    } finally {
      clearTimeout(timeout);
      signal.removeEventListener('abort', abort);
    }
  };
}
