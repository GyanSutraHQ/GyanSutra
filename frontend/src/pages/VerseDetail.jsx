/**
 * VerseDetail - full single-verse page with recommendations.
 */

import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getVerse } from '../services/api';
import IlluminatedVerseCard from '../components/IlluminatedVerseCard';
import RecommendationsRail from '../components/RecommendationsRail';
import LoadingSpinner from '../components/LoadingSpinner';
import useLanguage from '../i18n/useLanguage';
import './VerseDetail.css';

export default function VerseDetail() {
  const { t } = useLanguage();
  const { id } = useParams();
  const [verse, setVerse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    setVerse(null);
    getVerse(id)
      .then((value) => { if (active) setVerse(value); })
      .catch((e) => { if (active) setError(e.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [id]);

  if (error) return (
    <main className="verse-detail">
      <Link to="/" className="verse-detail__back">← {t('home')}</Link>
      <p>{t('translationUnavailable')}</p>
    </main>
  );

  const chapterId = verse ? `chapter_${verse.chapterNumber}` : null;
  const isRamayana = verse?.book === 'ramayana' || Boolean(verse?.kanda);
  const readerUrl = isRamayana
    ? `/ramayana/${verse.kandaNumber || verse.chapterNumber}?sarga=${verse.sarga}&verse=${verse.shlokaNumber}`
    : `/chapters/${chapterId}?verse=${verse?.verseNumber}`;

  return (
    <main className="verse-detail">
      <h1 className="sr-only">{isRamayana ? t('ramayana') : t('gita')} · {t('verse')} {verse?.shlokaNumber || verse?.verseNumber}</h1>
      <nav className="verse-detail__breadcrumb" aria-label="Breadcrumb">
        <Link to="/" id="breadcrumb-home">Gyan Sutra</Link>
        {verse && (
          <>
            <span className="verse-detail__breadcrumb-sep">›</span>
            <Link to={readerUrl} id="breadcrumb-chapter">
              {isRamayana ? `${t('kanda')} ${verse.kandaNumber || verse.chapterNumber} · ${t('sarga')} ${verse.sarga}` : `${t('chapter')} ${verse.chapterNumber}`}
            </Link>
            <span className="verse-detail__breadcrumb-sep">›</span>
            <span>{isRamayana ? t('shloka') : t('verse')} {verse.shlokaNumber || verse.verseNumber}</span>
          </>
        )}
      </nav>

      {loading ? (
        <LoadingSpinner size="medium" text={`${t('shloka')}…`} />
      ) : verse ? (
        <>
          <IlluminatedVerseCard verse={verse} variant="full" />
          <RecommendationsRail contentId={verse.id} type="verse" />
        </>
      ) : (
        <p>{t('translationUnavailable')}</p>
      )}
    </main>
  );
}
