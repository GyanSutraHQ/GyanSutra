import { renderToString } from 'react-dom/server';
import { MemoryRouter } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { LanguageProvider } from './i18n/LanguageContext';
import App from './App';

// Build-time only. Ship the same real homepage that React renders, not a
// separate SEO-only page; no runtime SSR service or new dependency is needed.
export function renderLanding(base = '/') {
  const markup = renderToString(
    <HelmetProvider context={{}}>
      <LanguageProvider>
        <MemoryRouter basename={base} initialEntries={[base]}>
          <App />
        </MemoryRouter>
      </LanguageProvider>
    </HelmetProvider>,
  );
  // React 19 hoists resource hints and metadata ahead of the app. The static
  // generator owns <head>, so retain only the body and avoid duplicate JSON-LD.
  return markup.slice(markup.indexOf('<div class="gs-app'))
    .replace(/<script type="application\/ld\+json">[\s\S]*?<\/script>/g, '');
}
