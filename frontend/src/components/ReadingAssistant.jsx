import './ReadingAssistant.css';
import { assistantPrompt } from '../utils/reader';
import { LANGUAGES } from '../i18n/languageConfig';

const COPY = {
  en: { label: 'Help me understand · Sarathi AI', simplify: 'Explain simply', summary: 'Summarize', points: 'Key points' },
  hi: { label: 'सारथि से रूपांतरित करें', simplify: 'सरल करें', summary: 'सारांश', points: 'मुख्य बिंदु' },
  bn: { label: 'সারথির সাহায্যে রূপান্তর', simplify: 'সহজ করুন', summary: 'সারাংশ', points: 'মূল বিষয়' },
  mr: { label: 'सारथीसह रूपांतरित करा', simplify: 'सोपे करा', summary: 'सारांश', points: 'मुख्य मुद्दे' },
  te: { label: 'సారథితో మార్చండి', simplify: 'సరళీకరించండి', summary: 'సారాంశం', points: 'ముఖ్యాంశాలు' },
  ta: { label: 'சாரதியுடன் மாற்றவும்', simplify: 'எளிமையாக்கு', summary: 'சுருக்கம்', points: 'முக்கிய குறிப்புகள்' },
};

const INSTRUCTIONS = {
  simplify: 'explain it in plain, simple language in two or three short sentences',
  summary: 'give a concise summary',
  points: 'list the key ideas as brief bullet points',
};

export default function ReadingAssistant({ language = 'en', sectionTitle, reference, text = '', verseId }) {
  const labels = COPY[language] || COPY.en;

  const transform = (event) => {
    const action = event.target.value;
    if (!action) return;
    event.target.value = '';
    window.dispatchEvent(new CustomEvent('open-sarathi', {
      detail: {
        prompt: assistantPrompt({ reference, sectionTitle, text, instruction: INSTRUCTIONS[action], language: LANGUAGES.find((item) => item.code === language)?.name || language }),
        submit: true,
        contextIds: verseId ? [verseId] : [],
      },
    }));
  };

  return (
    <label className="reading-assistant" title={labels.label}>
      <span className="reading-assistant__sparkle" aria-hidden="true">✦</span>
      <span className="sr-only">{labels.label}</span>
      <select defaultValue="" onChange={transform} aria-label={labels.label}>
        <option value="" disabled>{labels.label}</option>
        <option value="simplify">{labels.simplify}</option>
        <option value="summary">{labels.summary}</option>
        <option value="points">{labels.points}</option>
      </select>
    </label>
  );
}
