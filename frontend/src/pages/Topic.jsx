import { Link, Navigate, useParams } from 'react-router-dom';
import SEOHead from '../components/SEO/SEOHead';
import { SEO_TOPIC_BY_SLUG } from '../data/seoTopics';
import './Topic.css';

export default function Topic() {
  const { slug } = useParams();
  const topic = SEO_TOPIC_BY_SLUG[slug];
  if (!topic) return <Navigate to="/" replace />;

  const schemaData = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: topic.title,
    description: topic.description,
    mainEntityOfPage: `https://gyansutraapp.com/topics/${topic.slug}`,
    isAccessibleForFree: true,
    about: ['Bhagavad Gita', 'Hindu philosophy'],
  };

  return (
    <main className="topic-page">
      <SEOHead title={topic.title} description={topic.description} canonical={`/topics/${topic.slug}`} schemaData={schemaData} />
      <article className="topic-page__article">
        <nav className="topic-page__crumbs" aria-label="Breadcrumb">
          <Link to="/">Gyan Sutra</Link><span aria-hidden="true">/</span><Link to="/bhagavad-gita">Bhagavad Gita</Link><span aria-hidden="true">/</span><span>{topic.h1}</span>
        </nav>
        <header className="topic-page__header">
          <p className="topic-page__eyebrow">Bhagavad Gita study guide</p>
          <h1>{topic.h1}</h1>
          <p>{topic.intro}</p>
        </header>

        {topic.sections.map((section) => (
          <section key={section.heading} className="topic-page__section">
            <h2>{section.heading}</h2>
            <p>{section.body}</p>
          </section>
        ))}

        <section className="topic-page__sources" aria-labelledby="topic-sources">
          <h2 id="topic-sources">Read the source passages</h2>
          <p>These passages provide the textual basis for this guide.</p>
          <ul>{topic.sources.map((source) => <li key={source.path}><Link to={source.path}>{source.label}</Link></li>)}</ul>
        </section>

        <section className="topic-page__related" aria-labelledby="related-guides">
          <h2 id="related-guides">Related guides</h2>
          <ul>{topic.related.map((relatedSlug) => {
            const related = SEO_TOPIC_BY_SLUG[relatedSlug];
            return <li key={relatedSlug}><Link to={`/topics/${relatedSlug}`}>{related.h1}</Link></li>;
          })}</ul>
        </section>
      </article>
    </main>
  );
}
