import { useEffect, useRef, useState } from 'react';
import { Capacitor, registerPlugin } from '@capacitor/core';

const nativeSpeechInput = registerPlugin('SpeechInput');

const SPEECH_LANGUAGES = {
  en: 'en-IN', hi: 'hi-IN', bn: 'bn-IN', mr: 'mr-IN', te: 'te-IN', ta: 'ta-IN',
};

export default function useSpeechInput({ language, onTranscript }) {
  const recognitionRef = useRef(null);
  const transcriptRef = useRef(onTranscript);
  const [listening, setListening] = useState(false);
  const [error, setError] = useState('');
  const native = Capacitor.getPlatform() === 'android';
  const supported = native || (typeof window !== 'undefined'
    && Boolean(window.SpeechRecognition || window.webkitSpeechRecognition));

  useEffect(() => { transcriptRef.current = onTranscript; }, [onTranscript]);
  useEffect(() => () => recognitionRef.current?.abort(), []);

  async function toggle() {
    if (native) {
      if (listening) return;
      setError('');
      setListening(true);
      try {
        const result = await nativeSpeechInput.recognize({ language: SPEECH_LANGUAGES[language] || SPEECH_LANGUAGES.en });
        if (result.transcript?.trim()) transcriptRef.current(result.transcript.trim());
      } catch (cause) {
        setError(cause?.message || 'Speech recognition is unavailable on this device.');
      } finally {
        setListening(false);
      }
      return;
    }
    if (listening) {
      recognitionRef.current?.stop();
      return;
    }
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
      setError('Speech input is unavailable in this browser.');
      return;
    }
    const recognition = new Recognition();
    recognitionRef.current = recognition;
    recognition.lang = SPEECH_LANGUAGES[language] || SPEECH_LANGUAGES.en;
    recognition.interimResults = false;
    recognition.continuous = false;
    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0]?.transcript || '')
        .join(' ').trim();
      if (transcript) transcriptRef.current(transcript);
    };
    recognition.onerror = (event) => {
      if (event.error !== 'aborted') {
        setError(event.error === 'not-allowed'
          ? 'Allow microphone access to dictate a question.'
          : 'Speech could not be recognized. Please try again.');
      }
    };
    recognition.onend = () => {
      setListening(false);
      recognitionRef.current = null;
    };
    setError('');
    try {
      recognition.start();
      setListening(true);
    } catch {
      setError('Speech input could not start. Please try again.');
      setListening(false);
    }
  }

  return { supported, listening, error, toggle };
}
