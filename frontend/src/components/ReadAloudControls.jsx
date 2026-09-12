import { useEffect, useMemo, useRef, useState } from 'react';
import { Capacitor } from '@capacitor/core';
import { TextToSpeech } from '@capacitor-community/text-to-speech';

import { buildNarration, LANGUAGE_LOCALES, rankedVoices } from '../utils/narration';
import { startNarrationSession } from '../services/readAloud';
import './ReadAloudControls.css';

const COPY = {
  en: {
    meaningIntro: 'Now, the meaning', explanationIntro: 'Let us understand this further', contextIntro: 'Here is the context',
    verse: 'Shloka', fallback: 'Natural voice unavailable. Using a device voice.', sequence: 'Shloka first, then its meaning, with pauses between sections.',
    listen: 'Listen', stop: 'Stop', speed: 'Speed', voice: 'Voice', deviceDefault: 'Natural narration (automatic)',
    reading: 'Listen to', meaning: 'Meaning', full: 'Full explanation', guruExplanations: 'Guru explanations',
    chooseSection: 'Choose any section. It will play independently without repeating the shloka.',
    preparing: 'Preparing the reading…', playing: 'Reading aloud', error: 'Read aloud could not start on this device.',
    missingVoice: 'A reading voice for this language is not installed.', installVoice: 'Install a voice',
    translation: 'Translation', explanation: 'Explanation', context: 'Context', quality: 'Voice quality depends on the speech voices installed on this device.',
    studio: 'Listening studio', indianOnly: 'Indian pronunciation only', ready: 'Ready to listen',
  },
  hi: {
    meaningIntro: 'अब इसका अर्थ सुनिए', explanationIntro: 'आइए इसे विस्तार से समझें', contextIntro: 'अब इसका प्रसंग सुनिए',
    verse: 'श्लोक', fallback: 'सहज आवाज़ उपलब्ध नहीं है। डिवाइस की आवाज़ से वाचन हो रहा है।', sequence: 'पहले श्लोक, फिर अर्थ, हर भाग के बीच विराम के साथ।',
    listen: 'सुनें', stop: 'रोकें', speed: 'गति', voice: 'आवाज़', deviceDefault: 'सहज वाचन (स्वचालित)',
    reading: 'क्या सुनें', meaning: 'अर्थ', full: 'पूरी व्याख्या', guruExplanations: 'गुरु व्याख्याएँ',
    chooseSection: 'कोई भी भाग चुनें। श्लोक दोबारा सुनाए बिना वही भाग चलेगा।',
    preparing: 'पाठ तैयार हो रहा है…', playing: 'पाठ सुनाया जा रहा है', error: 'इस डिवाइस पर वाचन शुरू नहीं हो सका।',
    missingVoice: 'इस भाषा की वाचन आवाज़ इंस्टॉल नहीं है।', installVoice: 'आवाज़ इंस्टॉल करें',
    translation: 'अनुवाद', explanation: 'व्याख्या', context: 'प्रसंग', quality: 'आवाज़ की गुणवत्ता इस डिवाइस पर इंस्टॉल की गई वाचन आवाज़ों पर निर्भर करती है।',
    studio: 'श्रवण कक्ष', indianOnly: 'केवल भारतीय उच्चारण', ready: 'सुनने के लिए तैयार',
  },
  bn: {
    meaningIntro: 'এবার এর অর্থ শুনুন', explanationIntro: 'আসুন আরও বিস্তারিতভাবে বুঝি', contextIntro: 'এবার এর প্রসঙ্গ শুনুন',
    verse: 'শ্লোক', fallback: 'স্বাভাবিক কণ্ঠ উপলব্ধ নেই। ডিভাইসের কণ্ঠ ব্যবহার করা হচ্ছে।', sequence: 'প্রথমে শ্লোক, তারপর অর্থ, প্রতিটি অংশের মাঝে বিরতি দিয়ে।',
    listen: 'শুনুন', stop: 'বন্ধ করুন', speed: 'গতি', voice: 'কণ্ঠ', deviceDefault: 'স্বাভাবিক পাঠ (স্বয়ংক্রিয়)',
    reading: 'যা শুনবেন', meaning: 'অর্থ', full: 'সম্পূর্ণ ব্যাখ্যা', guruExplanations: 'গুরুর ব্যাখ্যা',
    chooseSection: 'যেকোনো অংশ বেছে নিন। শ্লোক আবার না পড়ে শুধু সেই অংশটি চলবে।',
    preparing: 'পাঠ প্রস্তুত হচ্ছে…', playing: 'পাঠ শোনানো হচ্ছে', error: 'এই ডিভাইসে পাঠ শোনানো শুরু করা যায়নি।',
    missingVoice: 'এই ভাষার পাঠকণ্ঠ ইনস্টল করা নেই।', installVoice: 'কণ্ঠ ইনস্টল করুন',
    translation: 'অনুবাদ', explanation: 'ব্যাখ্যা', context: 'প্রসঙ্গ', quality: 'কণ্ঠের স্বাভাবিকতা এই ডিভাইসে ইনস্টল করা কণ্ঠগুলির উপর নির্ভর করে।',
    studio: 'শ্রবণ কক্ষ', indianOnly: 'শুধু ভারতীয় উচ্চারণ', ready: 'শোনার জন্য প্রস্তুত',
  },
  mr: {
    meaningIntro: 'आता याचा अर्थ ऐकूया', explanationIntro: 'चला हे अधिक सविस्तर समजून घेऊया', contextIntro: 'आता याचा संदर्भ ऐकूया',
    verse: 'श्लोक', fallback: 'सहज आवाज उपलब्ध नाही. डिवाइसचा आवाज वापरत आहे.', sequence: 'प्रथम श्लोक, नंतर अर्थ, प्रत्येक भागात विरामासह.',
    listen: 'ऐका', stop: 'थांबवा', speed: 'गती', voice: 'आवाज', deviceDefault: 'सहज वाचन (स्वयंचलित)',
    reading: 'काय ऐकायचे', meaning: 'अर्थ', full: 'संपूर्ण स्पष्टीकरण', guruExplanations: 'गुरूंची भाष्ये',
    chooseSection: 'कोणताही भाग निवडा. श्लोक पुन्हा न वाचता तो स्वतंत्रपणे ऐकता येईल.',
    preparing: 'वाचन तयार होत आहे…', playing: 'वाचन सुरू आहे', error: 'या डिवाइसवर वाचन सुरू करता आले नाही.',
    missingVoice: 'या भाषेचा वाचन आवाज इंस्टॉल केलेला नाही.', installVoice: 'आवाज इंस्टॉल करा',
    translation: 'अनुवाद', explanation: 'स्पष्टीकरण', context: 'संदर्भ', quality: 'आवाजाची नैसर्गिकता या डिवाइसवर इंस्टॉल केलेल्या आवाजांवर अवलंबून असते.',
    studio: 'श्रवण कक्ष', indianOnly: 'फक्त भारतीय उच्चार', ready: 'ऐकण्यासाठी तयार',
  },
  te: {
    meaningIntro: 'ఇప్పుడు దీని అర్థం వినండి', explanationIntro: 'దీన్ని మరింత వివరంగా తెలుసుకుందాం', contextIntro: 'ఇప్పుడు దీని సందర్భం వినండి',
    verse: 'శ్లోకం', fallback: 'సహజ స్వరం అందుబాటులో లేదు. పరికరం స్వరం ఉపయోగిస్తోంది.', sequence: 'ముందుగా శ్లోకం, తర్వాత అర్థం, భాగాల మధ్య విరామంతో.',
    listen: 'వినండి', stop: 'ఆపండి', speed: 'వేగం', voice: 'స్వరం', deviceDefault: 'సహజ పఠనం (స్వయంచాలకం)',
    reading: 'ఏది వినాలి', meaning: 'అర్థం', full: 'పూర్తి వివరణ', guruExplanations: 'గురువుల వ్యాఖ్యానాలు',
    chooseSection: 'ఏ భాగాన్నైనా ఎంచుకోండి. శ్లోకాన్ని మళ్లీ చదవకుండా ఆ భాగమే వినిపిస్తుంది.',
    preparing: 'పఠనం సిద్ధమవుతోంది…', playing: 'చదివి వినిపిస్తోంది', error: 'ఈ పరికరంలో చదివి వినిపించడం ప్రారంభించలేకపోయాం.',
    missingVoice: 'ఈ భాషకు సంబంధించిన పఠన స్వరం ఇన్‌స్టాల్ కాలేదు.', installVoice: 'స్వరాన్ని ఇన్‌స్టాల్ చేయండి',
    translation: 'అనువాదం', explanation: 'వివరణ', context: 'సందర్భం', quality: 'స్వరం సహజంగా వినిపించడం ఈ పరికరంలో ఇన్‌స్టాల్ చేసిన స్వరాలపై ఆధారపడి ఉంటుంది.',
    studio: 'శ్రవణ కేంద్రం', indianOnly: 'భారతీయ ఉచ్చారణ మాత్రమే', ready: 'వినడానికి సిద్ధం',
  },
  ta: {
    meaningIntro: 'இப்போது இதன் பொருளைக் கேளுங்கள்', explanationIntro: 'இதை மேலும் விரிவாகப் புரிந்துகொள்வோம்', contextIntro: 'இப்போது இதன் சூழலைக் கேளுங்கள்',
    verse: 'சுலோகம்', fallback: 'இயல்பான குரல் கிடைக்கவில்லை. சாதனத்தின் குரல் பயன்படுத்தப்படுகிறது.', sequence: 'முதலில் சுலோகம், பின்னர் பொருள், பகுதிகளுக்கு இடையே இடைவெளியுடன்.',
    listen: 'கேளுங்கள்', stop: 'நிறுத்தவும்', speed: 'வேகம்', voice: 'குரல்', deviceDefault: 'இயல்பான வாசிப்பு (தானியங்கி)',
    reading: 'எதைக் கேட்க', meaning: 'பொருள்', full: 'முழு விளக்கம்', guruExplanations: 'குரு விளக்கங்கள்',
    chooseSection: 'எந்தப் பகுதியையும் தேர்ந்தெடுக்கவும். சுலோகம் மீண்டும் ஒலிக்காமல் அந்தப் பகுதி மட்டும் இயங்கும்.',
    preparing: 'வாசிப்பு தயாராகிறது…', playing: 'வாசித்துக் கொண்டிருக்கிறது', error: 'இந்தச் சாதனத்தில் வாசிப்பைத் தொடங்க முடியவில்லை.',
    missingVoice: 'இந்த மொழிக்கான வாசிப்புக் குரல் நிறுவப்படவில்லை.', installVoice: 'குரலை நிறுவவும்',
    translation: 'மொழிபெயர்ப்பு', explanation: 'விளக்கம்', context: 'சூழல்', quality: 'குரலின் இயல்பான தன்மை இந்தச் சாதனத்தில் நிறுவப்பட்டுள்ள குரல்களைப் பொறுத்தது.',
    studio: 'கேட்பகுதி', indianOnly: 'இந்திய உச்சரிப்பு மட்டும்', ready: 'கேட்கத் தயார்',
  },
};

const CONTENT_LANGUAGE_CODES = {
  english: 'en', hindi: 'hi', bengali: 'bn', marathi: 'mr', telugu: 'te', tamil: 'ta',
};
const RECITATION_COPY = {
  en: { voice: 'Meaning voice', device: 'Device voice' },
  hi: { voice: 'अर्थ की आवाज़', device: 'डिवाइस की आवाज़' },
  bn: { voice: 'অর্থের কণ্ঠ', device: 'ডিভাইসের কণ্ঠ' },
  mr: { voice: 'अर्थाचा आवाज', device: 'डिवाइसचा आवाज' },
  te: { voice: 'అర్థం చదివే స్వరం', device: 'పరికరం స్వరం' },
  ta: { voice: 'பொருளை வாசிக்கும் குரல்', device: 'சாதனத்தின் குரல்' },
};
const SPEEDS = [
  { value: 0.8, label: '0.8×' },
  { value: 0.95, label: '0.95×' },
  { value: 1.1, label: '1.1×' },
];

export default function ReadAloudControls({
  verseKey,
  book,
  chapterNumber,
  verseNumber,
  sanskrit,
  translation,
  explanation,
  context,
  commentaries = [],
  language,
  contentLanguage,
  disabled = false,
  targetLabels = {},
  helpText = '',
}) {
  const labels = COPY[language] || COPY.en;
  const audioLabels = RECITATION_COPY[language] || RECITATION_COPY.en;
  const generatedLabel = ({ en: 'AI narration', hi: 'एआई वाचन', bn: 'এআই কণ্ঠ', mr: 'एआय वाचन', te: 'ఏఐ పఠనం', ta: 'AI வாசிப்பு' })[language] || 'AI narration';
  const automaticLabel = ({ en: 'Automatic natural voice', hi: 'स्वचालित सहज आवाज़', bn: 'স্বয়ংক্রিয় স্বাভাবিক কণ্ঠ', mr: 'स्वयंचलित सहज आवाज', te: 'స్వయంచాలక సహజ స్వరం', ta: 'தானியங்கி இயல்பான குரல்' })[language] || 'Automatic natural voice';
  const spokenLabels = COPY[CONTENT_LANGUAGE_CODES[contentLanguage]] || COPY.en;
  const preferredLocale = LANGUAGE_LOCALES[contentLanguage] || 'en-IN';
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState('');
  const [rate, setRate] = useState(0.95);
  const [selectedTarget, setSelectedTarget] = useState('translation');
  const [activeTarget, setActiveTarget] = useState('');
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState('');
  const [progress, setProgress] = useState(null);
  const [fallback, setFallback] = useState(false);
  const [audioSource, setAudioSource] = useState('device');
  const sessionRef = useRef(null);

  const matchingVoices = useMemo(() => rankedVoices(voices, preferredLocale), [preferredLocale, voices]);
  const narrationTargets = useMemo(() => {
    const targets = [];
    if (sanskrit?.trim()) targets.push({ id: 'verse', label: targetLabels.verse || labels.verse, scope: 'verse', contentLanguage });
    if (translation?.trim()) targets.push({ id: 'translation', label: targetLabels.translation || labels.meaning, scope: 'translation', contentLanguage });
    if (explanation?.trim() && explanation.trim() !== translation?.trim()) {
      targets.push({ id: 'explanation', label: targetLabels.explanation || labels.full, scope: 'explanation', contentLanguage });
    }
    if (context?.trim() && ![translation, explanation].some((text) => text?.trim() === context.trim())) {
      targets.push({ id: 'context', label: labels.context, scope: 'context', contentLanguage });
    }
    commentaries.forEach((item, index) => {
      if (!item?.explanation?.trim()) return;
      targets.push({
        id: `commentary-${index}`,
        label: item.author || `${labels.explanation} ${index + 1}`,
        scope: 'explanation',
        explanation: item.explanation,
        contentLanguage: String(item.language || contentLanguage).toLowerCase(),
        guru: true,
      });
    });
    return targets;
  }, [sanskrit, translation, explanation, context, contentLanguage, commentaries, labels, targetLabels]);

  useEffect(() => {
    let active = true;
    const refresh = () => {
      TextToSpeech.getSupportedVoices().then((result) => {
        if (active) setVoices(result.voices || []);
      }).catch(() => {});
    };
    refresh();
    window.speechSynthesis?.addEventListener('voiceschanged', refresh);
    window.addEventListener('focus', refresh);
    return () => {
      active = false;
      window.speechSynthesis?.removeEventListener('voiceschanged', refresh);
      window.removeEventListener('focus', refresh);
    };
  }, []);

  useEffect(() => { setSelectedVoice(''); }, [contentLanguage]);

  useEffect(() => {
    sessionRef.current?.stop();
    sessionRef.current = null;
    setStatus('idle');
    setError('');
    setProgress(null);
    setActiveTarget('');
    setFallback(false);
    setAudioSource('device');
    return () => { sessionRef.current?.stop(); sessionRef.current = null; };
  }, [verseKey, book, chapterNumber, verseNumber, sanskrit, translation, explanation, context, contentLanguage, language, disabled]);

  useEffect(() => {
    if (!narrationTargets.some((target) => target.id === selectedTarget)) {
      setSelectedTarget(narrationTargets[0]?.id || '');
    }
  }, [narrationTargets, selectedTarget]);

  const listen = async () => {
    if (sessionRef.current) {
      sessionRef.current.stop();
      sessionRef.current = null;
      return;
    }
    const target = narrationTargets.find((item) => item.id === selectedTarget) || narrationTargets[0];
    if (!target) { setError(labels.error); setStatus('error'); return; }
    const segments = buildNarration({
      sanskrit, translation,
      explanation: target.explanation || explanation,
      context,
      contentLanguage: target.contentLanguage,
      scope: target.scope,
      labels: spokenLabels,
    });
    if (!segments.length) { setError(labels.error); setStatus('error'); return; }
    setError('');
    setFallback(false);
    setStatus('preparing');
    setAudioSource('device');
    setActiveTarget(target.label);
    const session = startNarrationSession(() => {
      if (sessionRef.current === session) {
        sessionRef.current = null;
        setStatus('idle');
        setProgress(null);
        setActiveTarget('');
      }
    });
    sessionRef.current = session;
    try {
      await session.play(segments, {
        voices, selectedVoice, rate, mode: 'neural',
        onSource: setAudioSource,
        onSegment: (segment, index, total, phase) => {
          if (sessionRef.current !== session) return;
          setStatus(phase);
          setProgress({ kind: segment.kind, index: index + 1, total });
        },
        onFallback: (reason) => setFallback(reason),
      });
      if (sessionRef.current === session) session.stop();
    } catch (failure) {
      if (session.signal.aborted || sessionRef.current !== session) return;
      session.stop();
      setError(failure.message === 'MISSING_VOICE' ? labels.missingVoice : labels.error);
      setStatus('error');
    }
  };

  const installVoice = async () => {
    try {
      await TextToSpeech.openInstall();
    } catch {
      setError(labels.error);
    }
  };

  const active = status === 'playing' || status === 'preparing';
  const progressValue = progress ? Math.round((progress.index / progress.total) * 100) : 0;
  const statusMessage = status === 'preparing'
    ? labels.preparing
    : status === 'playing' ? labels.playing : error;

  return (
    <section className="read-aloud" aria-label={labels.listen}>
      <div className="read-aloud__header">
        <div className="read-aloud__identity">
          <span className="read-aloud__identity-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24"><path d="M5 9v6h4l5 4V5L9 9H5Z" /><path d="M17 9a4 4 0 0 1 0 6M19.5 6.5a7.5 7.5 0 0 1 0 11" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></svg>
          </span>
          <div><strong>{labels.studio || 'Listening studio'}</strong><small>{labels.indianOnly || 'Indian pronunciation only'}</small></div>
        </div>
      </div>

      <label className="read-aloud__section-picker">
        <span>{labels.reading}</span>
        <select value={selectedTarget} onChange={(event) => setSelectedTarget(event.target.value)} disabled={active}>
          {narrationTargets.map((target) => (
            <option key={target.id} value={target.id}>{target.label}</option>
          ))}
        </select>
      </label>

      <div className="read-aloud__primary-row">

        <button
          type="button"
          className={`read-aloud__button${active ? ' read-aloud__button--active' : ''}`}
          onClick={listen}
          disabled={disabled && !active}
          aria-pressed={active}
        >
          {active ? (
            <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="6" width="12" height="12" rx="1" /></svg>
          ) : (
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m8 5 11 7-11 7V5Z" /></svg>
          )}
          <span>{active ? labels.stop : labels.listen}</span>
        </button>

        <label className="read-aloud__field">
          <span>{labels.speed}</span>
          <select value={rate} onChange={(event) => setRate(Number(event.target.value))} disabled={active}>
            {SPEEDS.map((speed) => <option key={speed.value} value={speed.value}>{speed.label}</option>)}
          </select>
        </label>

        {matchingVoices.length > 0 && (
          <label className="read-aloud__field read-aloud__field--voice">
            <span>{contentLanguage === 'english' ? 'Indian English voice' : audioLabels.voice}</span>
            <select value={selectedVoice} onChange={(event) => setSelectedVoice(event.target.value)} disabled={active}>
              <option value="">{automaticLabel}</option>
              {matchingVoices.map((voice) => (
                <option key={`${voice.voiceURI}-${voice.index}`} value={voice.voiceURI}>{voice.name}</option>
              ))}
            </select>
          </label>
        )}
      </div>

      <div
        className={`read-aloud__progress${active ? ' read-aloud__progress--active' : ''}`}
        role="progressbar"
        aria-label={statusMessage || labels.ready || 'Ready to listen'}
        aria-valuemin="0"
        aria-valuemax="100"
        aria-valuenow={progressValue}
      >
        <span style={{ width: `${progressValue}%` }} />
      </div>

      <p className="read-aloud__status" aria-live="polite">
        {active && activeTarget ? `${statusMessage} · ${activeTarget}` : statusMessage || helpText || labels.chooseSection}
        {active && progress && ` · ${audioSource === 'neural' ? generatedLabel : audioLabels.device}`}
        {active && fallback && ` ${labels.fallback}`}
      </p>

      {audioSource === 'neural' && (
        <p className="read-aloud__credit">
          {generatedLabel} · <a href="/narration-notices.html" target="_blank" rel="noopener noreferrer">Svara-TTS · Built with Llama</a>
        </p>
      )}

      {status === 'error' && Capacitor.getPlatform() === 'android' && (
        <button type="button" className="read-aloud__install" onClick={installVoice}>
          {labels.installVoice}
        </button>
      )}
    </section>
  );
}
