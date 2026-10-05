import { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useSearchParams } from 'react-router-dom';
import IlluminatedVerseCard from '../components/IlluminatedVerseCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { getRamayanaSarga } from '../services/api';
import useLanguage from '../i18n/useLanguage';
import KANDA_NAMES from '../utils/kandaNames';
import { readerArrow, sargaNumber, verseIndex } from '../utils/reader';
import { RETRY_COPY, READER_INTRO_COPY } from '../utils/readerCopy';

import './ChapterReader.css';

const KANDAS = [
  { id: 1, name: 'Bala Kanda', sargas: 77 },
  { id: 2, name: 'Ayodhya Kanda', sargas: 119 },
  { id: 3, name: 'Aranya Kanda', sargas: 75 },
  { id: 4, name: 'Kishkindha Kanda', sargas: 67 },
  { id: 5, name: 'Sundara Kanda', sargas: 68 },
  { id: 6, name: 'Yuddha Kanda', sargas: 128 },
  { id: 7, name: 'Uttara Kanda', sargas: 111 },
];

const KANDA_COPY = {
  en: { all: 'All Kandas', missing: 'Kanda not found.', loading: 'Loading shlokas…', failed: 'Could not load this sarga.', none: 'No verses found for this Sarga.', choose: 'Try selecting a different Sarga above.', unverified: 'Unverified', previous: 'Previous shloka', next: 'Next shloka', navigation: 'Verse navigation', of: 'of' },
  hi: { all: 'सभी काण्ड', missing: 'काण्ड नहीं मिला।', loading: 'श्लोक खुल रहे हैं…', failed: 'यह सर्ग लोड नहीं हो सका।', none: 'इस सर्ग में कोई श्लोक नहीं मिला।', choose: 'ऊपर से कोई दूसरा सर्ग चुनें।', unverified: 'अप्रमाणित', previous: 'पिछला श्लोक', next: 'अगला श्लोक', navigation: 'श्लोक संचालन', of: 'में से' },
  bn: { all: 'সব কাণ্ড', missing: 'কাণ্ড পাওয়া যায়নি।', loading: 'শ্লোক খুলছে…', failed: 'এই সর্গ লোড করা যায়নি।', none: 'এই সর্গে কোনো শ্লোক পাওয়া যায়নি।', choose: 'উপরে অন্য একটি সর্গ বেছে নিন।', unverified: 'যাচাই করা হয়নি', previous: 'আগের শ্লোক', next: 'পরের শ্লোক', navigation: 'শ্লোক পরিচালনা', of: 'এর মধ্যে' },
  mr: { all: 'सर्व कांड', missing: 'कांड सापडले नाही.', loading: 'श्लोक उघडत आहेत…', failed: 'हा सर्ग लोड होऊ शकला नाही.', none: 'या सर्गात श्लोक सापडले नाहीत.', choose: 'वरून वेगळा सर्ग निवडा.', unverified: 'असत्यापित', previous: 'मागील श्लोक', next: 'पुढील श्लोक', navigation: 'श्लोक नेव्हिगेशन', of: 'पैकी' },
  te: { all: 'అన్ని కాండలు', missing: 'కాండ దొరకలేదు.', loading: 'శ్లోకాలు తెరుచుకుంటున్నాయి…', failed: 'ఈ సర్గను లోడ్ చేయలేకపోయాం.', none: 'ఈ సర్గలో శ్లోకాలు దొరకలేదు.', choose: 'పైన మరో సర్గను ఎంచుకోండి.', unverified: 'ధృవీకరించబడలేదు', previous: 'మునుపటి శ్లోకం', next: 'తదుపరి శ్లోకం', navigation: 'శ్లోక నావిగేషన్', of: 'లో' },
  ta: { all: 'அனைத்து காண்டங்கள்', missing: 'காண்டம் கிடைக்கவில்லை.', loading: 'சுலோகங்கள் திறக்கப்படுகின்றன…', failed: 'இந்தச் சர்க்கத்தை ஏற்ற முடியவில்லை.', none: 'இந்தச் சர்க்கத்தில் சுலோகங்கள் கிடைக்கவில்லை.', choose: 'மேலே வேறு சர்க்கத்தைத் தேர்ந்தெடுக்கவும்.', unverified: 'சரிபார்க்கப்படவில்லை', previous: 'முந்தைய சுலோகம்', next: 'அடுத்த சுலோகம்', navigation: 'சுலோக வழிசெலுத்தல்', of: 'இல்' },
};

export default function KandaReader() {
  const { language, t } = useLanguage();
  const labels = KANDA_COPY[language] || KANDA_COPY.en;
  const { kandaNum } = useParams();
  const kandaId = Number(kandaNum);
  const kanda = KANDAS.find(k => k.id === kandaId);
  
  const [searchParams, setSearchParams] = useSearchParams();
  const currentSarga = sargaNumber(searchParams.get('sarga'), kanda?.sargas || 1);
  const requestedVerse = searchParams.get('verse');
  const [verses, setVerses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retry, setRetry] = useState(0);
  const currentIndex = verseIndex(verses, requestedVerse, 'shlokaNumber');
  const changeSarga = useCallback((number, verse = '1') => {
    setSearchParams((params) => { params.set('sarga', number); params.set('verse', verse); return params; }, { replace: true });
  }, [setSearchParams]);

  useEffect(() => {
    if (!kanda) return;
    let active = true;
    
    setLoading(true);
    setError(null);
    setVerses([]);
    
    getRamayanaSarga(kandaId, currentSarga)
      .then(data => {
        if (!active) return;
        setVerses(Array.isArray(data?.verses) ? data.verses : []);
        setError(null);
        setLoading(false);
      })
      .catch(err => {
        if (!active) return;
        setError(err.message);
        setLoading(false);
      });
    return () => { active = false; };
  }, [kandaId, currentSarga, kanda, retry]);

  const goTo = useCallback((newIndex) => {
    if (loading || !verses[newIndex]) return;
    setSearchParams((params) => { params.set('verse', verses[newIndex].shlokaNumber); return params; }, { replace: true });
    document.getElementById('reader-passage')?.scrollIntoView({ block: 'start' });
  }, [loading, verses, setSearchParams]);

  const handlePrev = () => { 
    if (loading) return;
    if (currentIndex > 0) {
      goTo(currentIndex - 1);
    } else if (currentSarga > 1) {
      changeSarga(currentSarga - 1, 'last');
    }
  };
  
  const handleNext = () => {
    if (loading) return;
    if (currentIndex < verses.length - 1) {
      goTo(currentIndex + 1);
    } else if (kanda && currentSarga < kanda.sargas) {
      changeSarga(currentSarga + 1);
    }
  };

  // Keyboard Navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      const direction = readerArrow(e, Boolean(document.querySelector('.sarathi-panel--open')));
      if (!direction || loading || error || !verses.length) return;
      e.preventDefault();
      if (direction === -1) {
        if (currentIndex > 0) {
          goTo(currentIndex - 1);
        } else if (currentSarga > 1) {
          changeSarga(currentSarga - 1, 'last');
        }
      } else if (direction === 1) {
        if (currentIndex < verses.length - 1) {
          goTo(currentIndex + 1);
        } else if (kanda && currentSarga < kanda.sargas) {
          changeSarga(currentSarga + 1);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex, currentSarga, verses, kanda, goTo, changeSarga, loading, error]);

  const currentVerse = verses[currentIndex];

  if (!kanda) return (
    <main className="chapter-reader chapter-reader--error">
      <Link to="/ramayana" className="chapter-reader__back">← {t('ramayana')}</Link>
      <p>{labels.missing}</p>
    </main>
  );

  return (
    <main className="chapter-reader">
      <header className="chapter-reader__header">
        <Link to="/ramayana" className="chapter-reader__back" id="back-to-home-link">
          ← {labels.all}
        </Link>
        <div className="chapter-reader__title-block">
          <span className="chapter-reader__chapter-num">{t('ramayana')} · {t('kanda')} {kanda.id}</span>
          <h1 className="chapter-reader__title devanagari">{KANDA_NAMES[language]?.[kanda.id - 1] || kanda.name}</h1>
          <p className="chapter-reader__summary">{(READER_INTRO_COPY[language] || READER_INTRO_COPY.en).ramayana}</p>
          <div className="chapter-picker">
            <label htmlFor="sarga-select" className="text-[color:var(--text-secondary)] text-sm uppercase tracking-widest">{t('sarga')}</label>
            <select 
              id="sarga-select"
              value={currentSarga}
              onChange={(e) => changeSarga(Number(e.target.value))}
              className="min-h-11 bg-transparent border border-amber-500/20 text-[color:var(--text-primary)] rounded px-3 py-2 outline-none"
            >
              {Array.from({ length: kanda.sargas }, (_, i) => i + 1).map(num => (
                <option key={num} value={num} className="bg-[color:var(--bg-surface)]">
                  {num}
                </option>
              ))}
            </select>
          </div>
        </div>
        <hr className="gold-rule" />
      </header>

      {loading && !error && (
        <LoadingSpinner size="medium" text={labels.loading} />
      )}

      {error && <div className="chapter-reader__empty"><p role="alert">{labels.failed}</p><button type="button" className="chapter-reader__nav-btn" onClick={() => setRetry((value) => value + 1)}>↻ {RETRY_COPY[language] || RETRY_COPY.en}</button></div>}
      
      {!loading && !error && verses.length === 0 && (
        <div className="text-center mt-16 text-[color:var(--text-secondary)]">
          <p>{labels.none}</p>
          <p className="text-sm mt-2">{labels.choose}</p>
        </div>
      )}

      {!loading && verses.length > 0 && currentVerse && (
        <section className="chapter-reader__content" id="reader-passage">
          <div className="chapter-reader__position">
            <p role="status">{t('sarga')} {currentSarga} · {t('shloka')} <strong>{currentVerse.shlokaNumber}</strong> / {verses.length}</p>
            <div className="chapter-reader__progress" role="progressbar" aria-label={labels.navigation} aria-valuemin="0" aria-valuemax={verses.length} aria-valuenow={currentIndex + 1}>
              <div className="chapter-reader__progress-bar" style={{ width: `${(currentIndex + 1) / verses.length * 100}%` }} />
            </div>
          </div>
          
          <IlluminatedVerseCard verse={currentVerse} key={currentVerse.id} />
        </section>
      )}

      {/* ── Floating Navigation Controls ──────────────────────── */}
      {!loading && verses.length > 0 && (
        <nav className="chapter-reader__nav" aria-label={labels.navigation}>
          <button type="button"
            onClick={handlePrev}
            disabled={currentIndex === 0 && currentSarga === 1}
            className="chapter-reader__nav-btn"
            aria-label={labels.previous}
          >
            ← <span>{labels.previous}</span>
          </button>
          
          <label className="chapter-reader__jump-wrap"><span className="sr-only">{t('shloka')}</span>
            <select className="chapter-reader__verse-select" value={currentIndex} onChange={(event) => goTo(Number(event.target.value))}>
              {verses.map((verse, index) => <option key={verse.id} value={index}>{t('shloka')} {verse.shlokaNumber}</option>)}
            </select>
          </label>
          
          <button type="button"
            onClick={handleNext}
            disabled={currentIndex === verses.length - 1 && currentSarga === kanda.sargas}
            className="chapter-reader__nav-btn chapter-reader__nav-btn--next"
            aria-label={labels.next}
          >
            <span>{labels.next}</span> →
          </button>
        </nav>
      )}

    </main>
  );
}
