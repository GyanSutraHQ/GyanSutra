// Cinematic photorealistic compositions paired with sacred geometry emblems.
// Decorative art is kept out of the accessibility tree; the adjacent text tells the story.

const BOOK_IMAGES = {
  gita: 'images/landing/gita-card.jpg',
  ramayana: 'images/landing/ramayana-card.jpg',
  purana: 'images/landing/purana-card.jpg',
};

export function Lotus({ className = '', ...props }) {
  return (
    <svg viewBox="0 0 120 90" fill="none" className={className} aria-hidden="true" {...props}>
      <path d="M60 70C38 51 40 28 60 7c20 21 22 44 0 63Z" fill="currentColor" opacity=".12" />
      <g stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
        <path d="M60 72C38 52 40 28 60 7c20 21 22 45 0 65Z" />
        <path d="M60 72C29 70 18 51 19 25c27 5 40 19 41 47Zm0 0c31-2 42-21 41-47-27 5-40 19-41 47Z" />
        <path d="M60 72C32 85 12 68 5 48c25-1 43 5 55 24Zm0 0c28 13 48-4 55-24-25-1-43 5-55 24Z" />
        <path d="M24 83h72" strokeLinecap="round" />
      </g>
    </svg>
  );
}

export function BookArtwork({ kind }) {
  const baseUrl = import.meta.env.BASE_URL || '/';
  const relPath = BOOK_IMAGES[kind] || BOOK_IMAGES.gita;
  const imageSrc = `${baseUrl}${relPath}`;
  const imageSmSrc = `${baseUrl}${relPath.replace('.jpg', '-sm.jpg')}`;

  return (
    <div className={`gs-book-visual gs-book-visual--${kind}`} aria-hidden="true">
      <img
        src={imageSrc}
        srcSet={`${imageSmSrc} 720w, ${imageSrc} 1376w`}
        sizes="(max-width: 767px) 92vw, 390px"
        alt=""
        width="720"
        height="402"
        loading="lazy"
        decoding="async"
        fetchPriority="low"
        className="gs-book-visual__photo"
      />
      <div className="gs-book-visual__vignette" />
      <div className="gs-book-visual__glare" />
      <svg className={`gs-book-art gs-book-art--${kind}`} viewBox="0 0 360 250" fill="none" focusable="false">
        <g className="gs-book-art__cover" opacity="0.88">
          <g stroke="var(--book-line)" strokeWidth="1.35">
            {kind === 'gita' && <>
              <circle cx="180" cy="125" r="42" strokeOpacity=".55" />
              <circle cx="180" cy="125" r="32" strokeOpacity=".75" />
              {Array.from({ length: 12 }, (_, i) => <path key={i} d="M180 88v74" strokeOpacity=".45" transform={`rotate(${i * 15} 180 125)`} />)}
              <circle cx="180" cy="125" r="7" fill="var(--book-line)" fillOpacity=".35" />
            </>}
            {kind === 'ramayana' && <>
              <path d="M174 82c-45 43-45 68 0 87V82Zm0 0 24 47-24 40m-17-40h54m-7-5 7 5-7 5" strokeOpacity=".8" />
            </>}
            {kind === 'purana' && <>
              <path d="M180 155c-26-27-21-48 0-65 21 23 24 44 0 65Zm0 0c-32 4-42-14-41-37 24 4 37 16 41 37Zm0 0c32 4 42-14 41-37-24 4-37 16-41 37Z" strokeOpacity=".8" />
              <circle cx="180" cy="113" r="5" />
            </>}
          </g>
        </g>
        <g className="gs-book-art__orbit" stroke="var(--book-line)" strokeWidth="1">
          <path d="M52 94h14m-7-7v14M294 168h12m-6-6v12" />
          <circle cx="288" cy="58" r="3" />
          <path d="M38 176c-11-27-7-58 13-78M298 102c13 18 17 39 11 60" strokeDasharray="2 6" opacity=".65" />
        </g>
      </svg>
    </div>
  );
}

export function SarathiArtwork() {
  const baseUrl = import.meta.env.BASE_URL || '/';
  const imageSrc = `${baseUrl}images/landing/sarathi-companion.jpg`;
  const imageSmSrc = `${baseUrl}images/landing/sarathi-companion-sm.jpg`;

  return (
    <div className="gs-companion-visual" aria-hidden="true">
      <img
        src={imageSrc}
        srcSet={`${imageSmSrc} 720w, ${imageSrc} 1376w`}
        sizes="(max-width: 767px) 90vw, 560px"
        alt=""
        width="640"
        height="357"
        loading="lazy"
        decoding="async"
        fetchPriority="low"
        className="gs-companion-visual__photo"
      />
      <div className="gs-companion-visual__aura" />
      <svg className="gs-companion-art" viewBox="0 0 400 330" fill="none" focusable="false">
        <circle cx="200" cy="165" r="126" stroke="currentColor" opacity=".28" />
        <circle className="gs-companion-art__orbit" cx="200" cy="165" r="146" stroke="currentColor" strokeDasharray="3 9" opacity=".45" />
        <g className="gs-companion-art__flame" opacity=".35">
          <path d="M200 222c-60-12-52-72 0-132-2 50 68 84 36 118-8 10-21 15-36 14Z" fill="#ffd98a" />
        </g>
        <g stroke="currentColor" strokeWidth="1.3">
          <path d="M318 85v16m-8-8h16M82 252v12m-6-6h12" />
          <circle cx="286" cy="44" r="3" />
        </g>
      </svg>
    </div>
  );
}
