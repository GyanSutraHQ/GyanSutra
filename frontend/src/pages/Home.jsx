import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getDailyVerse } from '../services/api';
import useLanguage from '../i18n/useLanguage';
import useLocalizedVerse, { GENERATED_LANGUAGES } from '../hooks/useLocalizedVerse';
import useLandingMotion from '../hooks/useLandingMotion';
import { modernizeEnglish } from '../utils/modernEnglish';
import { SEO_TOPICS } from '../data/seoTopics';
import { FEATURED_VERSE, LANDING_COPY, LANDING_FAQS, LANDING_META, LANDING_SCHEMA } from '../data/landing';
import { BookArtwork, Lotus, SarathiArtwork } from '../components/landing/ScriptureArt';
import ScriptureLandscape, { TraditionEmblem } from '../components/landing/ScriptureLandscape';
import { CINEMATIC_HERO_COPY, SCRIPTURE_TRADITIONS } from '../data/scriptureTraditions';
import SEOHead from '../components/SEO/SEOHead';
import './Home.css';
import './CinematicScene.css';

const Arrow = ({ down = false }) => <span className="gs-landing-arrow" aria-hidden="true">{down ? '↓' : '↗'}</span>;

function openSarathi(prompt) {
  window.dispatchEvent(new CustomEvent('open-sarathi', { detail: { prompt } }));
}

export default function Home() {
  const { language, t } = useLanguage();
  const copy = { ...(LANDING_COPY[language] || LANDING_COPY.en), ...(CINEMATIC_HERO_COPY[language] || CINEMATIC_HERO_COPY.en) };
  const [world, setWorld] = useState('itihasas');
  const motion = useLandingMotion();
  const [dailyVerse, setDailyVerse] = useState(null);
  // The homepage displays existing translations only; simply visiting it must
  // not trigger on-demand AI translation work.
  const dailyLocalization = useLocalizedVerse(dailyVerse, language, { enabled: false });

  useEffect(() => {
    let active = true;
    getDailyVerse().then((res) => {
      if (active && res.verse) setDailyVerse(res.verse);
    }).catch(() => { /* The source-attributed featured verse stays available. */ });
    return () => { active = false; };
  }, []);

  const verse = dailyVerse || FEATURED_VERSE;
  const generatedMeaning = GENERATED_LANGUAGES.has(language) && dailyLocalization.content?.translation;
  const dailyMeaning = modernizeEnglish(generatedMeaning || (language === 'hi'
    ? verse.translationHindi || verse.translationEnglish
    : verse.translationEnglish || verse.translationHindi));
  const meaningLanguage = generatedMeaning ? language : language === 'hi' && verse.translationHindi ? 'hi' : 'en';
  const versePath = '/chapters/chapter_' + verse.chapterNumber + '?verse=' + verse.verseNumber;
  const sources = [
    { id: 'bhagavad-gita', kind: 'gita', number: '01', title: language === 'en' ? 'Bhagavad Gita' : t('heroTitleHighlight'), count: t('chapters18'), description: t('gitaDescription'), category: 'The conversation' },
    { id: 'ramayana', kind: 'ramayana', number: '02', title: language === 'en' ? 'Valmiki Ramayana' : t('ramayana'), count: t('kandas7'), description: t('ramayanaDescription'), category: 'The journey' },
    { id: 'vishnu-purana', kind: 'purana', number: '03', title: copy.purana, count: copy.parts, description: copy.puranaDescription, category: 'The universe' },
  ];

  return (
    <main ref={motion.rootRef} id="main-content" className="gs-landing" data-world={world} data-motion={motion.paused ? 'paused' : 'running'}>
      <SEOHead title={LANDING_META.title} description={LANDING_META.description} canonical="/" ogImage={LANDING_META.image} schemaData={LANDING_SCHEMA} />
      <section className="gs-landing-hero" aria-labelledby="landing-title">
        <ScriptureLandscape world={world} />
        <div className="gs-landing-hero__copy">
          <div className="gs-hero-invocation" aria-hidden="true">
            <span className="gs-hero-invocation__line" />
            <span className="gs-hero-invocation__gem" />
            <span className="gs-hero-invocation__medallion">
              <span className="gs-hero-invocation__om" lang="sa">ॐ</span>
            </span>
            <span className="gs-hero-invocation__gem" />
            <span className="gs-hero-invocation__line" />
          </div>
          <h1 id="landing-title">{copy.title}<em>{copy.accent}</em></h1>
        </div>
        <div className="gs-landing-hero__bottom">
          <a href="#text-library" className="gs-hero-scroll" lang="en"><span aria-hidden="true">↓</span>Enter the library</a>
          <button className="gs-motion-toggle" type="button" onClick={motion.toggleMotion} aria-pressed={motion.paused} disabled={motion.reduced}>
            <span aria-hidden="true">{motion.paused ? '▷' : 'Ⅱ'}</span>{motion.paused ? copy.motionOff : copy.motionOn}
          </button>
        </div>
      </section>

      <section id="text-library" className="gs-landing-library gs-landing-shell" aria-labelledby="library-title">
        <div className="gs-landing-section-head" data-reveal>
          <div><p className="gs-landing-kicker">{copy.collection}<span className="gs-landing-index" aria-hidden="true">/ 01</span></p><h2 id="library-title">{copy.library}</h2></div>
          <p>{copy.libraryIntro}</p>
        </div>
        <div className="gs-landing-books">
          {sources.map((source, idx) => (
            <Link to={'/' + source.id} key={source.id} className={'gs-landing-book gs-tilt-card gs-landing-book--' + source.kind} style={{ '--stagger-idx': idx }} data-reveal>
              <div className="gs-landing-book__picture gs-motion-zone"><span className="gs-landing-book__category" lang="en">{source.category}</span><BookArtwork kind={source.kind} /><span className="gs-landing-book__number" aria-hidden="true">{source.number}</span></div>
              <div className="gs-landing-book__text"><p className="gs-landing-book__count">{source.count}</p><h3>{source.title}<Arrow /></h3><p>{source.description}</p><span className="gs-landing-book__read">{t('read')}<span aria-hidden="true"> →</span></span></div>
            </Link>
          ))}
        </div>
      </section>

      <section id="scripture-traditions" className="gs-traditions gs-landing-shell" aria-labelledby="traditions-title" lang="en" aria-label="Explore the scripture landscape">
        <div className="gs-landing-section-head" data-reveal><div><p className="gs-landing-kicker">The world of Gyan Sutra<span className="gs-landing-index" aria-hidden="true">/ 02</span></p><h2 id="traditions-title">An entire tradition.<br />A growing library.</h2></div><p>Vedas, Upanishads, Itihasas, and Puranas belong to the wider world we are building for. Explore the collections available today.</p></div>
        <div className="gs-traditions__grid">{SCRIPTURE_TRADITIONS.map((tradition, idx) => <article key={tradition.id} className={`gs-tradition gs-tradition--${tradition.id} gs-tilt-card`} style={{ '--stagger-idx': idx }} data-reveal onMouseEnter={() => setWorld(tradition.id)}><div className="gs-tradition__art gs-motion-zone">{tradition.image && <img src={`${import.meta.env.BASE_URL}${tradition.image}`} srcSet={`${import.meta.env.BASE_URL}${tradition.image.replace('.jpg', '-sm.jpg')} 720w, ${import.meta.env.BASE_URL}${tradition.image} 1376w`} sizes="(max-width: 767px) 46vw, 290px" alt="" width="480" height="268" loading="lazy" decoding="async" fetchPriority="low" className="gs-tradition__photo" />}<div className="gs-tradition__vignette" /><div className="gs-tradition__halo" /><TraditionEmblem kind={tradition.id} /><span lang="sa">{tradition.sanskrit}</span></div><div className="gs-tradition__body"><span className={`gs-tradition__status${tradition.path === '/faq' ? ' gs-tradition__status--future' : ''}`}>{tradition.status}</span><h3>{tradition.name}</h3><p>{tradition.note}</p><div className="gs-tradition__actions"><Link className="gs-landing-link" to={tradition.path}>{tradition.action}<Arrow /></Link>{tradition.previewPath && <Link className="gs-tradition__preview-link" to={tradition.previewPath}>Preview edition</Link>}</div></div></article>)}</div>
      </section>

      <section className="gs-landing-verse-band" aria-labelledby="daily-verse-title">
        <div className="gs-landing-verse gs-landing-shell">
          <div className="gs-landing-verse__intro" data-reveal><Lotus /><p className="gs-landing-kicker">{dailyVerse ? t('dailyDarshan') : copy.verse}<span className="gs-landing-index" aria-hidden="true">/ 03</span></p><h2 id="daily-verse-title">{copy.quiet}</h2><p>{copy.quietIntro}</p><Link className="gs-landing-link" to={versePath}>{t('readFullVerse')}<Arrow /></Link></div>
          <article className="gs-landing-verse__paper" data-reveal>
            <span className="gs-landing-verse__bookmark" aria-hidden="true" />
            <p className="gs-landing-verse__sanskrit" lang="sa">{verse.sanskrit}</p>
            <p className="gs-landing-verse__translation" lang={meaningLanguage}>{dailyMeaning}</p>
            <div className="gs-landing-verse__source">
              <Link to={versePath}>Bhagavad Gita {verse.chapterNumber}.{verse.verseNumber}<Arrow /></Link>
              {generatedMeaning ? <span lang="en">AI-assisted meaning · editorial review pending</span>
                : meaningLanguage === 'en' && <span lang="en">{verse.translationSources?.english?.author || 'Swami Sivananda'} · modernized English</span>}
            </div>
          </article>
        </div>
      </section>

      <section className="gs-landing-practice gs-landing-shell" aria-labelledby="practice-title" lang="en">
        <div className="gs-landing-section-head" data-reveal><div><p className="gs-landing-kicker">Make it your own<span className="gs-landing-index" aria-hidden="true">/ 04</span></p><h2 id="practice-title">Not a race to finish.<br />A reason to return.</h2></div><p>Five quiet minutes can be a beginning.<br />There is no perfect place to start.</p></div>
        <div className="gs-landing-steps">
          {[
            ['01', 'Read with context.', 'Original Sanskrit where available, translations, and commentary. Follow the chapter, not just the quote.', '/bhagavad-gita', 'Find your first chapter'],
            ['02', 'Give the words a voice.', 'Explore recitation and meaning audio where available, with separate controls for each part.', '/chapters/chapter_2?verse=47', 'Explore a verse'],
            ['03', 'Follow your questions.', 'Search for an idea across the library, or ask Sarathi to help you understand a difficult passage.', '/search', 'Search the texts'],
          ].map(([number, title, description, path, action]) => (
            <article key={number} className="gs-landing-step" data-reveal><span className="gs-landing-step__number" aria-hidden="true">{number}</span><h3>{title}</h3><p>{description}</p><Link className="gs-landing-link" to={path}>{action}<Arrow /></Link></article>
          ))}
        </div>
      </section>

      <section className="gs-landing-companion" aria-labelledby="companion-title" lang="en">
        <div className="gs-landing-companion__inner gs-landing-shell">
          <div className="gs-landing-companion__art gs-motion-zone"><SarathiArtwork /><span className="gs-landing-companion__handnote">good questions<br />open doors.</span></div>
          <div className="gs-landing-companion__copy" data-reveal><p className="gs-landing-kicker">Meet Sarathi<span className="gs-landing-index" aria-hidden="true">/ 05</span></p><h2 id="companion-title">A companion<br />for your curiosity.</h2><p>An AI study guide, grounded in the texts you are reading. Ask a question, explore an explanation, and follow the references back to the source.</p><div className="gs-landing-prompts" lang={language}>{[t('promptDuty'), t('promptDetachment')].map((prompt) => <button type="button" key={prompt} onClick={() => openSarathi(prompt)}>{prompt}<Arrow /></button>)}</div><p className="gs-landing-companion__disclosure">A guide to study, not a final authority. Always read the cited passages.</p></div>
        </div>
      </section>

      <section className="gs-landing-topics gs-landing-shell" aria-labelledby="topic-library-title" lang="en">
        <div className="gs-landing-section-head" data-reveal><div><p className="gs-landing-kicker">Follow a thread<span className="gs-landing-index" aria-hidden="true">/ 06</span></p><h2 id="topic-library-title">Big questions.<br />Thoughtful beginnings.</h2></div><p>English study guides to ideas in the Bhagavad Gita. Every guide leads back to the passages that inform it.</p></div>
        <div className="gs-landing-topic-grid">{SEO_TOPICS.map((topic, index) => <Link key={topic.slug} to={'/topics/' + topic.slug} className="gs-landing-topic" data-reveal><span className="gs-landing-topic__number" aria-hidden="true">{String(index + 1).padStart(2, '0')}</span><div><h3>{topic.h1}</h3><p>{topic.description}</p></div><Arrow /></Link>)}</div>
      </section>

      <section className="gs-landing-questions gs-landing-shell" aria-labelledby="landing-faq-title" lang="en">
        <div data-reveal><p className="gs-landing-kicker">Before you begin<span className="gs-landing-index" aria-hidden="true">/ 07</span></p><h2 id="landing-faq-title">A few useful answers.</h2><Link to="/faq" className="gs-landing-link">About Gyan Sutra<Arrow /></Link></div>
        <div className="gs-landing-faqs">{LANDING_FAQS.map((faq) => <details key={faq.question} data-reveal><summary>{faq.question}<span aria-hidden="true">+</span></summary><p>{faq.answer}</p></details>)}</div>
      </section>

      <section className="gs-landing-invitation gs-landing-shell" lang="en" data-reveal><Lotus /><p className="gs-landing-kicker">Your next page is waiting</p><h2>Let curiosity lead.</h2><Link to="/bhagavad-gita" className="gs-landing-button">Open the Bhagavad Gita<Arrow /></Link><p>No sign-up. Just you and the text.</p></section>
    </main>
  );
}
