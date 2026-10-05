import { TextToSpeech } from '@capacitor-community/text-to-speech';
import { fetchNarrationAudio } from './api';
import { createNarrationPlayer } from './narrationPlayer';
import { createRecitationFetcher } from './recitationAudio';
import { getPreparedRecording } from '../utils/recitations';

const fetchRecording = createRecitationFetcher({
  fetch: window.fetch.bind(window), caches: window.caches,
  online: () => navigator.onLine !== false,
});

export const startNarrationSession = createNarrationPlayer({
  TextToSpeech, fetchNarrationAudio, Audio: window.Audio,
  fetchPreparedAudio: async (segment, signal) => {
    if (signal.aborted) return null;
    // The recording index is nearly 1 MB. Reading a passage should not need
    // to download or parse it; load it only when listening begins.
    const { default: inventory } = await import('../data/narrationInventory.json');
    if (signal.aborted) return null;
    const recording = getPreparedRecording(segment, inventory);
    return recording ? fetchRecording(recording, signal) : Promise.resolve(null);
  },
  online: () => navigator.onLine !== false,
});
