import { TextToSpeech } from '@capacitor-community/text-to-speech';
import { fetchNarrationAudio } from './api';
import { createNarrationPlayer } from './narrationPlayer';
import { createRecitationFetcher } from './recitationAudio';
import { getPreparedRecording } from '../utils/recitations';
import inventory from '../data/narrationInventory.json';

const fetchRecording = createRecitationFetcher({
  fetch: window.fetch.bind(window), caches: window.caches,
  online: () => navigator.onLine !== false,
});

export const startNarrationSession = createNarrationPlayer({
  TextToSpeech, fetchNarrationAudio, Audio: window.Audio,
  fetchPreparedAudio: (segment, signal) => {
    const recording = getPreparedRecording(segment, inventory);
    return recording ? fetchRecording(recording, signal) : Promise.resolve(null);
  },
  online: () => navigator.onLine !== false,
});
