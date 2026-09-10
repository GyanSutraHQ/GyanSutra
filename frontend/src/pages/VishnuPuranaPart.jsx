import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import SEOHead from '../components/SEO/SEOHead';
import { getVishnuPuranaPart } from '../services/api';

import './VishnuPurana.css';

export default function VishnuPuranaPart() {
  const { partNumber } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    setData(null);
    setError('');
    getVishnuPuranaPart(partNumber).then(setData).catch((failure) => setError(failure.message));
  }, [partNumber]);

  if (error) return <main className="vp-page"><div className="vp-shell"><Link className="vp-back" to="/vishnu-purana">← All six parts</Link><p className="vp-status vp-status--error">{error}</p></div></main>;
  if (!data) return <main className="vp-page"><LoadingSpinner size="medium" text="Opening this part…" /></main>;

  const { part } = data;
  return (
    <main className="vp-page">
      <SEOHead title={`${part.title} — Vishnu Purana`} description={`Read all ${part.sectionCount} sections in Part ${part.roman} of the Vishnu Purana.`} canonical={`/vishnu-purana/${part.number}`} />
      <div className="vp-shell vp-shell--narrow">
        <Link className="vp-back" to="/vishnu-purana">← All six parts</Link>
        <header className="vp-part-hero">
          <div className="vp-part-hero__mark" aria-hidden="true">{part.symbol}</div>
          <p className="vp-kicker">Part {part.roman} · {part.theme}</p>
          <h1>{part.title}</h1>
          <p>{part.sectionCount} source sections in the dialogue of Parāśara and Maitreya.</p>
        </header>

        <section className="vp-trail" aria-label={`Sections in ${part.title}`}>
          <div className="vp-trail__line" aria-hidden="true" />
          {part.sections.map((section) => (
            <article className="vp-story-card" key={section.id}>
              <span className="vp-story-card__node" aria-hidden="true" />
              <div className="vp-story-card__index">Section {String(section.sectionNumber).padStart(2, '0')}</div>
              <h2>{section.title}</h2>
              <p>{section.synopsis}</p>
              <Link to={`/vishnu-purana/${part.number}/${section.sectionNumber}`}>
                Enter this section <span aria-hidden="true">→</span>
              </Link>
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}
