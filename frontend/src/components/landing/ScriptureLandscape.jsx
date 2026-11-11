// Original scene geometry. Static placement and animated transforms use separate
// groups so CSS never replaces an SVG element's authored position.
export function TraditionEmblem({ kind, className = '' }) {
  return (
    <svg className={className} viewBox="0 0 100 100" fill="none" aria-hidden="true" focusable="false">
      <g stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
        {kind === 'vedas' && <><path d="M50 76C18 70 21 43 49 16c-4 22 34 39 20 54-5 5-11 7-19 6Z" fill="currentColor" fillOpacity=".12" /><path d="M49 73c-14-5-13-17 2-33-3 14 12 20 8 28-2 3-5 5-10 5ZM25 83h50M35 90h30M16 35l6 5m56-5 6-5" /></>}
        {kind === 'upanishads' && <><circle cx="50" cy="43" r="34" opacity=".3" /><path d="M50 73C30 51 34 31 50 16c16 15 20 35 0 57Zm0 0C20 74 13 53 16 36c21 3 34 16 34 37Zm0 0c30 1 37-20 34-37-21 3-34 16-34 37Z" fill="currentColor" fillOpacity=".08" /><path d="M12 84q19-9 38 0t38 0M26 93h48" /></>}
        {kind === 'itihasas' && <><path d="M38 16C9 45 11 70 38 85V16Zm0 0 29 35-29 34M23 51h60m-9-8 9 8-9 8" /><circle cx="65" cy="51" r="28" opacity=".25" /><path d="M65 26v10m0 30v10M40 51h10m30 0h10" opacity=".4" /></>}
        {kind === 'puranas' && <><circle cx="50" cy="50" r="25" /><ellipse cx="50" cy="50" rx="44" ry="13" transform="rotate(-30 50 50)" /><circle cx="78" cy="28" r="5" fill="currentColor" /><path d="M50 12v8m0 60v8M12 50h8m60 0h8M28 20l4 5m36 50 4 5" /><path d="M50 64c-14-11-13-21 0-30 13 9 14 19 0 30Z" fill="currentColor" fillOpacity=".15" /></>}
      </g>
    </svg>
  );
}

function Temple({ x, y, scale = 1, ornate = false }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${scale})`}>
      <path d="M-72 0h144v-14H-72Z" fill="url(#gs-temple-glow)" stroke="url(#gs-gold-stroke)" strokeWidth="1.2" />
      <path
        d="M-57-14v-29h114v29M-45-43l8-23h74l8 23M-37-66l7-21h60l7 21M-30-87l6-19h48l6 19M-24-106l6-16h36l6 16M-18-122l7-14h22l7 14M-11-136l11-28 11 28"
        fill="url(#gs-temple-glow)"
        stroke="url(#gs-gold-stroke)"
        strokeWidth="1.35"
        strokeLinejoin="round"
      />
      <circle cx="0" cy="-169" r="5" fill="#ffe89e" stroke="url(#gs-gold-stroke)" strokeWidth="1.2" />
      <path d="M0-174v-16" stroke="url(#gs-gold-stroke)" strokeWidth="2.4" strokeLinecap="round" />
      <g transform="translate(0 -189)">
        <path className="gs-scene__flag" d="M1 0c15-8 23 6 39-2-6 14-21 15-39 10Z" fill="url(#gs-flag-gold)" stroke="#fff3c4" strokeWidth=".8" />
      </g>
      <path d="M-12 0v-25a12 12 0 0 1 24 0V0" fill="rgba(255, 214, 118, 0.22)" stroke="url(#gs-gold-stroke)" strokeWidth="1.2" />
      <circle cx="0" cy="-11" r="3.2" fill="#fff4cc" />
      {ornate && (
        <g stroke="url(#gs-gold-stroke)" strokeWidth="1.2" opacity=".88">
          <path d="M-51-39h102M-40-62h80M-33-84h66M-26-103h52M-20-119h40M-14-134h28M-60-10h120M-53-15v-15m18 15v-15m70 15v-15m18 15v-15" />
          {[-28, 0, 28].map((cx) => (
            <path key={cx} d={`M${cx - 5}-44v-10a5 5 0 0 1 10 0v10m-3-22v-9a3 3 0 0 0-6 0v9`} />
          ))}
          <path d="M-13-94v-8m13 8v-8m13 8v-8M-7-111v-6m14 6v-6M-8-139l8-15 8 15" />
        </g>
      )}
    </g>
  );
}

function Tree({ x, y, scale = 1, mirrored = false }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${mirrored ? -scale : scale} ${scale})`}>
      <g className="gs-scene__tree">
        <path d="M0 0c-4-44-2-90 13-144M3-71l-22-27m26 0 27-28" stroke="url(#gs-gold-stroke)" strokeWidth="3.2" strokeOpacity=".55" fill="none" />
        <path
          d="M12-139c-54-31-88-14-113 2 43-5 70-2 100 15-59-13-90 1-108 20 48-12 79-7 107 6-43 2-66 24-76 46 40-24 64-30 83-36 30 9 58 23 79 43-5-34-25-57-60-64 44-4 70 2 102 13-18-30-47-49-99-38 29-20 60-29 96-28-38-20-71-20-111 7Z"
          fill="rgba(255, 204, 102, 0.1)"
          stroke="url(#gs-gold-stroke)"
          strokeWidth="1.1"
          strokeOpacity=".5"
        />
      </g>
    </g>
  );
}

const WORLD_BACKDROPS = {
  vedas: 'images/landing/tradition-vedas.jpg',
  upanishads: 'images/landing/tradition-upanishads.jpg',
  itihasas: 'images/landing/hero-landscape.jpg',
  puranas: 'images/landing/tradition-puranas.jpg',
};

export default function ScriptureLandscape({ world }) {
  const baseUrl = import.meta.env.BASE_URL || '/';
  const backdropSrc = `${baseUrl}${WORLD_BACKDROPS[world] || WORLD_BACKDROPS.itihasas}`;

  return (
    <div className="gs-scripture-scene gs-motion-zone" aria-hidden="true">
      <div className="gs-scene-backdrop">
        <img
          src={backdropSrc}
          alt=""
          width="1600"
          height="900"
          fetchPriority="high"
          decoding="async"
          className="gs-scene-backdrop__img"
        />
        <div className="gs-scene-backdrop__grade" />
      </div>
      <div className="gs-scene-godrays" />
      <div className="gs-scene-flare" />
      <div className="gs-scene-mandala" aria-hidden="true">
        <svg viewBox="0 0 600 600" fill="none" focusable="false">
          <defs>
            <linearGradient id="gs-mandala-gold" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#fff9db" />
              <stop offset="35%" stopColor="#ffd875" />
              <stop offset="70%" stopColor="#e59628" />
              <stop offset="100%" stopColor="#fff1be" />
            </linearGradient>
            <radialGradient id="gs-mandala-glow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#ffe596" stopOpacity=".24" />
              <stop offset="65%" stopColor="#f5a623" stopOpacity=".08" />
              <stop offset="100%" stopColor="#f5a623" stopOpacity="0" />
            </radialGradient>
          </defs>
          <circle cx="300" cy="300" r="280" fill="url(#gs-mandala-glow)" />
          <g stroke="url(#gs-mandala-gold)">
            <circle cx="300" cy="300" r="284" strokeOpacity=".55" strokeDasharray="2 8" strokeWidth="1.6" />
            <circle cx="300" cy="300" r="268" strokeOpacity=".65" strokeWidth="1.4" />
            <circle cx="300" cy="300" r="238" strokeOpacity=".75" strokeWidth="1.6" />
            <circle cx="300" cy="300" r="204" strokeOpacity=".6" strokeDasharray="4 6" strokeWidth="1.5" />
            <circle cx="300" cy="300" r="168" strokeOpacity=".65" strokeWidth="1.3" />
            <circle cx="300" cy="300" r="126" strokeOpacity=".5" strokeDasharray="1 6" strokeWidth="1.6" />
            <polygon points="300,66 502,417 98,417" strokeOpacity=".38" strokeWidth="1.2" />
            <polygon points="300,534 502,183 98,183" strokeOpacity=".38" strokeWidth="1.2" />
            {Array.from({ length: 24 }, (_, i) => (
              <g key={i} transform={`rotate(${i * 15} 300 300)`}>
                <path d="M300 16v22M300 62q24 46 0 94-24-48 0-94Z" strokeOpacity=".72" strokeWidth="1.35" fill="#ffd97d" fillOpacity=".05" />
                <circle cx="300" cy="48" r="2.2" fill="#fff4c2" stroke="none" opacity=".85" />
              </g>
            ))}
            {Array.from({ length: 12 }, (_, i) => (
              <path
                key={`inner-${i}`}
                d="M300 132q16 32 0 64-16-32 0-64Z"
                transform={`rotate(${i * 30 + 15} 300 300)`}
                strokeOpacity=".58"
                strokeWidth="1.2"
              />
            ))}
          </g>
        </svg>
      </div>
      <div className="gs-scene-aura gs-scene-aura--gold" />
      <div className="gs-scene-aura gs-scene-aura--violet" />
      <svg className="gs-scene__canvas" viewBox="0 0 1600 880" preserveAspectRatio="xMidYMid slice" fill="none" focusable="false">
        <defs>
          <linearGradient id="gs-gold-stroke" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#fff8d6" />
            <stop offset="40%" stopColor="#ffd66b" />
            <stop offset="75%" stopColor="#e08b24" />
            <stop offset="100%" stopColor="#ffeba8" />
          </linearGradient>
          <linearGradient id="gs-temple-glow" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ffd878" stopOpacity=".28" />
            <stop offset="100%" stopColor="#8a4214" stopOpacity=".12" />
          </linearGradient>
          <linearGradient id="gs-flag-gold" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#fff1b8" />
            <stop offset="50%" stopColor="#ffae2b" />
            <stop offset="100%" stopColor="#e86f1c" />
          </linearGradient>
          <radialGradient id="gs-scene-sun" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#fff7d6" stopOpacity=".75" />
            <stop offset="45%" stopColor="#ffc857" stopOpacity=".32" />
            <stop offset="100%" stopColor="#ff9e22" stopOpacity="0" />
          </radialGradient>
          <linearGradient id="gs-scene-page" x1="0" y1="0" x2="1" y2="1">
            <stop stopColor="#fff6d6" />
            <stop offset=".55" stopColor="#f5c469" />
            <stop offset="1" stopColor="#cf8328" />
          </linearGradient>
        </defs>
        <g className="gs-scene__depth gs-scene__depth--sky">
          <path d="M180 165 Q800 28 1420 165" stroke="url(#gs-gold-stroke)" strokeOpacity=".45" strokeWidth="1.2" strokeDasharray="3 9" />
          <path d="M260 190 Q800 68 1340 190" stroke="url(#gs-gold-stroke)" strokeOpacity=".32" strokeWidth="1" />
          <g transform="translate(1155 245)">
            <g className="gs-mural__sun">
              <circle r="210" fill="url(#gs-scene-sun)" />
              <circle r="165" stroke="url(#gs-gold-stroke)" strokeOpacity=".68" strokeWidth="1.4" strokeDasharray="2 10" />
              <circle r="124" stroke="url(#gs-gold-stroke)" strokeOpacity=".5" strokeWidth="1.1" />
              {Array.from({ length: 36 }, (_, i) => (
                <path key={i} d="M0-198v-22m0 52v-14" stroke="url(#gs-gold-stroke)" strokeOpacity=".65" strokeWidth="1.3" transform={`rotate(${i * 10})`} />
              ))}
            </g>
          </g>
          <g transform="translate(265 195)">
            <g className="gs-scene__celestial">
              <circle r="92" stroke="url(#gs-gold-stroke)" strokeOpacity=".62" strokeWidth="1.4" />
              <circle r="72" stroke="url(#gs-gold-stroke)" strokeOpacity=".45" strokeDasharray="3 7" strokeWidth="1.2" />
              {Array.from({ length: 12 }, (_, i) => (
                <path key={i} d="M0-88q-28 44 0 88 28-44 0-88Z" stroke="url(#gs-gold-stroke)" strokeOpacity=".52" strokeWidth="1.2" transform={`rotate(${i * 30})`} />
              ))}
            </g>
          </g>
        </g>
        <g className="gs-scene__clouds" stroke="url(#gs-gold-stroke)" strokeOpacity=".36" strokeWidth="1.1">
          <path d="M80 148c140-14 250 18 390 4M1040 118c155-16 260 10 430-4" />
        </g>
        <g className="gs-scene__depth gs-scene__depth--far">
          <path
            d="M0 610 90 525l58 31 151-175 172 180 80-43 129 108 162-80 115 49 194-198 109 138 100-42 240 165"
            stroke="url(#gs-gold-stroke)"
            strokeOpacity=".42"
            strokeWidth="1.4"
            strokeDasharray="6 6"
          />
        </g>
        <g className="gs-scene__depth gs-scene__depth--middle">
          <path
            d="M0 672 169 590l138 66 180-82 138 124 197-70 147 58 192-112 157 98 118-58 164 52"
            stroke="url(#gs-gold-stroke)"
            strokeOpacity=".55"
            strokeWidth="1.5"
          />
          <Temple x={113} y={648} scale={1.35} />
          <Temple x={307} y={678} scale={.72} />
          <Temple x={1285} y={648} scale={1.45} />
          <Temple x={1490} y={680} scale={.78} />
        </g>
        <g className="gs-scene__birds" stroke="url(#gs-gold-stroke)" strokeWidth="2.2" strokeLinecap="round">
          <path d="M225 205q14-15 28 0 14-15 28 0M1090 297q10-12 20 0 10-12 20 0M1383 250q12-13 24 0 12-13 24 0" />
        </g>
        <g className="gs-scene__river" stroke="url(#gs-gold-stroke)" strokeOpacity=".72" strokeWidth="1.8" strokeLinecap="round">
          <path d="M985 628h115m-148 26h178m-210 30h235m-285 36h310m-355 42h395m-430 46h460" />
          <circle cx="1045" cy="684" r="3.5" fill="#fff3c4" />
          <circle cx="1115" cy="720" r="4" fill="#fff3c4" />
          <circle cx="1015" cy="762" r="4.5" fill="#fff3c4" />
          <circle cx="1148" cy="804" r="4" fill="#fff3c4" />
        </g>
        <g className="gs-scene__depth gs-scene__depth--foreground">
          <Tree x={16} y={869} scale={1.75} />
          <Tree x={1577} y={873} scale={1.65} mirrored />
          <g>
            <Temple x={215} y={862} scale={1.12} ornate />
            <Temple x={342} y={870} scale={.62} ornate />
            <Temple x={1345} y={862} scale={1.18} ornate />
            <Temple x={1205} y={872} scale={.62} ornate />
          </g>
          <path d="M0 868h420M1180 868h420" stroke="url(#gs-gold-stroke)" strokeWidth="2" strokeOpacity=".78" />
          <g fill="url(#gs-gold-stroke)" opacity=".82">
            {Array.from({ length: 10 }, (_, i) => (
              <rect key={i} x={i * 39 + 12} y="871" width="20" height="3.5" rx="1.5" />
            ))}
            {Array.from({ length: 10 }, (_, i) => (
              <rect key={i} x={i * 39 + 1207} y="871" width="20" height="3.5" rx="1.5" />
            ))}
          </g>
        </g>
        <g transform="translate(800 72)">
          <g className="gs-scene__manuscript">
            <path d="M-148 24c-42-8-54-38-18-58 64-34 268-34 332 0 36 20 24 50-18 58" stroke="url(#gs-gold-stroke)" strokeWidth="1.5" strokeDasharray="4 7" strokeOpacity=".78" />
            <circle cx="0" cy="-18" r="4" fill="#fff4c2" />
            <circle cx="-86" cy="-10" r="2.5" fill="#ffd875" />
            <circle cx="86" cy="-10" r="2.5" fill="#ffd875" />
          </g>
        </g>
        <g transform="translate(430 335)">
          <g className="gs-scene__relic gs-scene__relic--left">
            <circle r="68" fill="#ffd269" fillOpacity=".1" stroke="url(#gs-gold-stroke)" strokeWidth="1.6" strokeOpacity=".82" />
            <circle r="56" stroke="url(#gs-gold-stroke)" strokeWidth="1" strokeDasharray="3 6" strokeOpacity=".65" />
            <g transform="translate(-42 -42) scale(.84)" stroke="url(#gs-gold-stroke)">
              <path d="M50 76C18 70 21 43 49 16c-4 22 34 39 20 54-5 5-11 7-19 6Z" strokeWidth="2" fill="#ffd875" fillOpacity=".22" />
              <path d="M25 83h50M33 90h34" strokeWidth="2" strokeLinecap="round" />
            </g>
          </g>
        </g>
        <g transform="translate(1175 365)">
          <g className="gs-scene__relic gs-scene__relic--right">
            <circle r="66" fill="#ffd269" fillOpacity=".1" stroke="url(#gs-gold-stroke)" strokeWidth="1.6" strokeOpacity=".82" />
            <circle r="54" stroke="url(#gs-gold-stroke)" strokeWidth="1" strokeDasharray="3 6" strokeOpacity=".65" />
            <g stroke="url(#gs-gold-stroke)" strokeWidth="1.8">
              <circle r="29" fill="#ffd875" fillOpacity=".14" />
              <ellipse rx="47" ry="12" transform="rotate(-30)" />
              <circle cx="35" cy="-24" r="5.5" fill="#fff3c4" />
              <path d="M0-48v9m0 78v9M-48 0h9m78 0h9" strokeLinecap="round" />
            </g>
          </g>
        </g>
      </svg>
      <div className="gs-scene__mobile-sun" />
      <svg className="gs-scene__mobile-architecture" viewBox="0 0 600 300" fill="none" aria-hidden="true" focusable="false">
        <g>
          <path d="M0 296h190M410 296h190" stroke="url(#gs-gold-stroke)" strokeWidth="2" strokeOpacity=".75" />
          <Tree x={0} y={300} scale={1.1} />
          <Tree x={600} y={300} scale={1.1} mirrored />
        </g>
        <g>
          <Temple x={86} y={298} scale={.78} ornate />
          <Temple x={514} y={298} scale={.78} ornate />
        </g>
      </svg>
      <div className="gs-scene__selected-emblem"><TraditionEmblem kind={world} /></div>
      <div className="gs-scene__fireflies">{Array.from({ length: 28 }, (_, i) => <i key={i} style={{ '--particle-x': `${5 + (i * 37) % 90}%`, '--particle-y': `${12 + (i * 19) % 74}%`, '--particle-delay': `${-i * .55}s`, '--particle-duration': `${4 + i % 5}s` }} />)}</div>
      <div className="gs-scene__embers">{Array.from({ length: 22 }, (_, i) => <span key={i} style={{ '--ember-x': `${6 + (i * 41) % 88}%`, '--ember-delay': `${-i * .9}s`, '--ember-duration': `${5.5 + (i % 4) * 1.4}s` }} />)}</div>
      <div className="gs-scene__shade" />
    </div>
  );
}
