import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import SEOHead from '../components/SEO/SEOHead';
import { getVishnuPurana } from '../services/api';

import './VishnuPurana.css';

export default function VishnuPurana() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    getVishnuPurana().then(setData).catch((failure) => setError(failure.message));
  }, []);

  return (
    <main className="vp-page">
      <SEOHead
        title="Complete Vishnu Purana"
        description="Read all six parts and 126 sections of M. N. Dutt's complete public-domain Vishnu Purana translation."
        canonical="/vishnu-purana"
      />
      <div className="vp-shell">
        <Link to="/" className="vp-back">← Scripture library</Link>

        <header className="vp-hero">
          <div className="vp-hero__copy">
            <p className="vp-kicker">A complete source journey · 6 parts · 126 sections</p>
            <h1>The Vishnu Purana</h1>
            <p className="vp-devanagari devanagari">विष्णुपुराण</p>
            <p className="vp-lede">
              Enter the teaching as Maitreya did: through creation, the worlds, sacred duties,
              royal lineages, Krishna’s life, and the path to liberation.
            </p>
            <div className="vp-hero__actions">
              <Link className="vp-button" to="/vishnu-purana/1">Begin the journey <span>→</span></Link>
              <a className="vp-text-link" href="#source-note">Check the sources</a>
            </div>
          </div>
          <div className="vp-mandala" aria-hidden="true">
            <div className="vp-mandala__orbit vp-mandala__orbit--outer" />
            <div className="vp-mandala__orbit vp-mandala__orbit--inner" />
            <span>ॐ</span>
          </div>
        </header>

        {error && <p className="vp-status vp-status--error">The text could not be opened. {error}</p>}
        {!data && !error && <LoadingSpinner size="medium" text="Opening the six-part journey…" />}

        {data && (
          <>
            <section className="vp-journey" aria-labelledby="vp-journey-title">
              <div className="vp-section-heading">
                <p>Story map</p>
                <h2 id="vp-journey-title">Six movements, one teaching</h2>
                <span>The labels below are navigation aids. Each section opens the complete source translation.</span>
              </div>
              <ol className="vp-parts">
                {data.parts.map((part, index) => (
                  <li key={part.number}>
                    <Link to={`/vishnu-purana/${part.number}`} className="vp-part-card">
                      <div className="vp-part-card__number">
                        <span>{part.symbol}</span>
                        <small>{String(index + 1).padStart(2, '0')}</small>
                      </div>
                      <div className="vp-part-card__body">
                        <p>Part {part.roman} · {part.sectionCount} sections</p>
                        <h3>{part.title}</h3>
                        <span className="vp-part-card__theme">{part.theme}</span>
                        {part.sections[0] && <p className="vp-part-card__preview">Begins: {part.sections[0].title}</p>}
                      </div>
                      <span className="vp-part-card__arrow" aria-hidden="true">↗</span>
                    </Link>
                  </li>
                ))}
              </ol>
            </section>

            <aside id="source-note" className="vp-source-note">
              <div>
                <p className="vp-kicker">Source integrity</p>
                <h2>Creative in presentation. Conservative with the text.</h2>
              </div>
              <div>
                <p>{data.authenticityNote}</p>
                <p>
                  Complete English: <a href={data.edition.transcriptionUrl} target="_blank" rel="noreferrer">M. N. Dutt, 1896</a>.
                  {' '}Sanskrit witness: <a href={data.edition.sanskritWitnessUrl} target="_blank" rel="noreferrer">Jīvānanda edition, 1882</a>.
                </p>
                <p className="vp-source-note__caution">{data.edition.sanskritStatus}</p>
              </div>
            </aside>
          </>
        )}
      </div>
    </main>
  );
}
