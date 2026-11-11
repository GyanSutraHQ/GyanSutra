# Gyan Sutra landing page

## Design and content

The homepage interprets the user's supplied Ramayana screen recording as an
original Gyan Sutra landscape: saffron sunset, plum silhouettes, layered mountains,
temples, a river, drifting clouds, swaying trees, waving flags, a floating manuscript,
and fireflies. The heading is “Many scriptures. One living thread.” Four scene
controls shift the colors and emblem for Vedas, Upanishads, Itihasas, and Puranas.
This reflects the wider scripture identity without copying the film's characters,
artwork, title, or marketing copy. Native scrolling moves scenery at different
depths, with subtle pointer parallax on desktop; it never hijacks scrolling.

Below the landscape, an illustrated four-tradition overview explicitly labels
Vedas and Upanishads “In preparation.” The live reading collection remains the
Bhagavad Gita, Valmiki Ramayana, and Vishnu Purana, alongside guides and Sarathi.
There are no invented reviews, reader counts, endorsements, or authorship claims.
Sarathi remains explicitly an AI study guide, with a reminder to check citations.

Content and implementation locations:

- `frontend/src/pages/Home.jsx`: sections, links, daily verse, assistant prompts.
- `frontend/src/pages/Home.css`: scoped palette, responsive layout, motion.
- `frontend/src/pages/CinematicScene.css`: cinematic scene, themed controls,
  tradition illustrations, mobile framing, and transform-based motion.
- `frontend/src/components/landing/ScriptureLandscape.jsx`: original layered
  landscape, reusable temple/tree geometry, and four tradition emblems.
- `frontend/src/components/landing/ScriptureArt.jsx`: book and Sarathi illustrations.
- `frontend/src/data/scriptureTraditions.js`: six-language hero copy, tradition
  names, thematic descriptions, and explicit availability.
- `frontend/src/data/landing.js`: six-language core copy, FAQ, metadata, schema,
  and a source-attributed Gita 2.47 fallback when the daily API is unavailable.
- `frontend/src/hooks/useLandingMotion.js`: persistent pause preference,
  reduced-motion support, offscreen animation and hidden-tab suspension, plus
  passive scroll/pointer handling batched in one requested animation frame.
- `frontend/public/social/gyansutra-library.png`: 1200 × 630 share image rendered
  from the same design. This is a static share preview, not a hero download.

Web newcomers see the page immediately in English and can change language in
the header or mobile settings. Android retains its first-run language chooser.
Core introductory and collection copy is localized; editorial guide sections
remain explicitly marked English. Translation availability is not overstated.
Existing localized daily meanings are labelled AI-assisted. A homepage visit
does not request AI translation or automatically submit a Sarathi question.

## Performance and accessibility

SVG scenes use CSS transforms, not video, WebGL, large photographs, or animation
timers. Hero geometry is reserved before load. Animations pause offscreen, in
hidden tabs, or through the user's motion control; OS reduced-motion settings
disable them. Motion does not carry information required to read the page.
FAQs use native keyboard-operable `details`/`summary`, links have visible focus
states, and a skip link reaches the page content.

Readers and the assistant load on navigation/open, not on homepage startup.
The homepage does not warm every route. Native controls avoid loading the motion
library solely for the header or error screen. Vendor matching is restricted to
React/router packages, rather than every dependency with “react” in its name.
Reader fonts load non-blockingly; the main heading uses a system serif stack.
The PWA precaches its shell, not the large narration inventory or all readers;
other hashed JS chunks are cached as they are opened. Modern browsers receive
native modules while older supported browsers retain the legacy fallback.

Build-time prerendering uses the real React homepage through `landing-entry.jsx`.
It ships styled, useful HTML without waiting for JavaScript or the daily API.
No production SSR server is needed. On startup, React 19 replaces the template's
SEO metadata; each route has one metadata owner, avoiding duplicate titles and
schema after JavaScript loads. The static generator removes prior generated
metadata on repeated runs, so homepage schema does not leak into other routes.
The remaining 141 static pages and sitemap verification are preserved.

## Verification

Run `npm test`, `npm run lint`, and `npm run build` from `frontend`.
Five homepage rendering tests cover useful API-independent HTML, six languages,
base-path links, truthful schema, and the separation of future collections from
published texts. The existing 45 reader/audio tests remain: 50 tests in total.

Local Chrome production-preview checks covered 320, 390, 820, and 1440 px widths,
dark mode, reduced motion, JavaScript disabled, motion controls, FAQ interaction,
Sarathi prompt handoff, and Hindi switching. No horizontal overflow or browser
exceptions were observed. A service-worker check also confirmed offline homepage
navigation, offline reload of a previously visited guide, and singular metadata
after navigating between the guide and homepage. A local mobile lab run at 1.6 Mbps download, 150 ms
latency, and 4× CPU slowdown measured approximately 1.0 s LCP and 0 CLS, with only
the app, React vendor, and runtime JS loaded at startup. This is not a deployed
Core Web Vitals measurement or a universal performance guarantee.

Local Lighthouse checks scored 100 for accessibility and SEO. The live backend
rejected the local production-preview origin on the daily-verse request, producing
a console/CORS warning and a 96 best-practices score on the final audit. The
attributed fallback still displays correctly. Browser interaction tests used an
intercepted empty daily response; these do not certify the deployed backend.

## SEO launch checklist

The build includes title/description, canonical URLs, Open Graph/Twitter previews,
truthful WebSite/Organization/WebPage/ItemList JSON-LD, semantic sections, real
internal links, robots.txt, and the existing sitemap. Structured data describes
the page; it does not promise rich results or higher rankings.

After deployment:

1. Verify the production homepage, `/social/gyansutra-library.png`, `/robots.txt`,
   and `/sitemap.xml` return successfully. Inspect the homepage's raw HTML.
2. Confirm HTTPS and alternate-host redirects point to `gyansutraapp.com`, matching
   the canonical URLs. Deployment configuration is not changed by this work.
3. Verify ownership in Google Search Console, submit the sitemap, and inspect
   the homepage and a topic guide. This requires the site's owner account.
4. Monitor real-user Core Web Vitals and Search Console search impressions and
   clicks. Recheck after release; local lab checks cannot establish real traffic.
5. Publish genuinely useful, source-attributed guides and keep their source links
   accurate. Do not add fabricated testimonials or mass-generated keyword pages.

Google's [JavaScript SEO guidance](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
explains why accessible rendered content and crawlable links matter.
[Animation performance guidance](https://web.dev/articles/animations-and-performance/)
and [reduced-motion guidance](https://web.dev/articles/prefers-reduced-motion)
inform the motion approach. Rankings and traffic growth cannot be guaranteed.
