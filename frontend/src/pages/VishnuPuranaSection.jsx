import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import ReadAloudControls from '../components/ReadAloudControls';
import ReadableText from '../components/ReadableText';
import SEOHead from '../components/SEO/SEOHead';
import { getVishnuPuranaSection } from '../services/api';

import './VishnuPurana.css';

function sectionPath(section) {
  return section ? `/vishnu-purana/${section.partNumber}/${section.sectionNumber}` : '';
}

export default function VishnuPuranaSection() {
  const { partNumber, sectionNumber } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    setData(null);
    setError('');
    getVishnuPuranaSection(partNumber, sectionNumber).then(setData).catch((failure) => setError(failure.message));
  }, [partNumber, sectionNumber]);

  useEffect(() => {
    const update = () => {
      const maximum = document.documentElement.scrollHeight - window.innerHeight;
      setProgress(maximum > 0 ? Math.min(100, (window.scrollY / maximum) * 100) : 0);
    };
    update();
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    return () => {
      window.removeEventListener('scroll', update);
      window.removeEventListener('resize', update);
    };
  }, []);

  const completeText = useMemo(() => data?.section.paragraphs.join('\n\n') || '', [data]);

  if (error) return <main className="vp-page"><div className="vp-shell"><Link className="vp-back" to="/vishnu-purana">← Vishnu Purana</Link><p className="vp-status vp-status--error">{error}</p></div></main>;
  if (!data) return <main className="vp-page"><LoadingSpinner size="medium" text="Opening the complete source text…" /></main>;

  const { part, section, edition } = data;
  const askPrompt = `Explain Vishnu Purana Part ${part.number}, Section ${section.sectionNumber}, using only the source text.`;

  return (
    <main className="vp-page vp-reading-page">
      <SEOHead title={`${section.title} — Vishnu Purana`} description={section.synopsis} canonical={`/vishnu-purana/${part.number}/${section.sectionNumber}`} />
      <div className="vp-reading-progress" style={{ '--progress': `${progress}%` }} aria-hidden="true" />
      <div className="vp-shell vp-shell--reading">
        <Link className="vp-back" to={`/vishnu-purana/${part.number}`}>← {part.title}</Link>

        <header className="vp-reading-header">
          <p className="vp-kicker">Vishnu Purana · Source passage</p>
          <h1>{section.title}</h1>
          <p className="vp-reading-header__dialogue">Parāśara <span aria-hidden="true">→</span> Maitreya</p>
        </header>

        <aside className="vp-story-lens">
          <div className="vp-story-lens__label"><span aria-hidden="true">✦</span> Source reading guide</div>
          <p>{section.synopsis}</p>
          <small>Adapted only by removing line breaks from the 1896 edition’s contents; it is not a replacement for the text below.</small>
        </aside>

        <section className="vp-listen-block" aria-labelledby="vp-listen-title">
          <div>
            <p className="vp-kicker">Listen your way</p>
            <h2 id="vp-listen-title">Choose one layer</h2>
            <p>The complete text and short reading guide play independently. Nothing is repeated first.</p>
          </div>
          <ReadAloudControls
            verseKey={section.id}
            book="vishnu-purana"
            chapterNumber={part.number}
            verseNumber={section.sectionNumber}
            translation={completeText}
            explanation={section.synopsis}
            language="en"
            contentLanguage="english"
            targetLabels={{ translation: 'Complete source text', explanation: 'Short reading guide' }}
            helpText="Select exactly what you want to hear; each option starts directly."
          />
        </section>

        <article className="vp-canonical" aria-labelledby="vp-source-text-title">
          <div className="vp-canonical__heading">
            <div>
              <p className="vp-kicker">Complete source text</p>
              <h2 id="vp-source-text-title">M. N. Dutt’s translation</h2>
            </div>
            <span>Public-domain edition</span>
          </div>
          <ReadableText
            paragraphs={section.paragraphs}
            hideFootnoteMarkers
            subheadings
            className="vp-canonical__text"
          />
        </article>

        {section.footnotes.length > 0 && (
          <details className="vp-footnotes">
            <summary>Translator’s notes</summary>
            <div className="vp-footnotes__list">
              {section.footnotes.map((note) => (
                <article key={note.number}>
                  <h3>Translator’s note</h3>
                  <ReadableText text={note.text} />
                </article>
              ))}
            </div>
          </details>
        )}

        <section className="vp-sarathi-invite">
          <div><p className="vp-kicker">Continue the dialogue</p><h2>Ask Sarathi about this section</h2></div>
          <button type="button" onClick={() => window.dispatchEvent(new CustomEvent('open-sarathi', { detail: { prompt: askPrompt } }))}>Ask with this source <span>→</span></button>
        </section>

        <nav className="vp-section-nav" aria-label="Section navigation">
          {data.previous ? <Link to={sectionPath(data.previous)}><small>Previous</small><span>← {data.previous.title}</span></Link> : <span />}
          {data.next ? <Link to={sectionPath(data.next)}><small>Next</small><span>{data.next.title} →</span></Link> : <span />}
        </nav>

        <p className="vp-edition-line">
          Text: <a href={edition.transcriptionUrl} target="_blank" rel="noreferrer">M. N. Dutt edition</a> · Sanskrit scan: <a href={edition.sanskritWitnessUrl} target="_blank" rel="noreferrer">Jīvānanda edition</a>
        </p>
      </div>
    </main>
  );
}
