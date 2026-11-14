import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import './index.css';
import App from './App.jsx';
import SplashScreen from './components/SplashScreen.jsx';
import ErrorBoundary from './components/ErrorBoundary.jsx';
import { LanguageProvider } from './i18n/LanguageContext.jsx';
import { initAppUpdate } from './utils/appUpdate.js';

const basename = import.meta.env.BASE_URL;

if (import.meta.env.PROD && import.meta.env.MODE !== 'android') {
  initAppUpdate({
    currentVersion: import.meta.env.VITE_APP_VERSION,
    baseUrl: basename,
  });
}

// React 19 manages metadata natively; Helmet 3 no longer replaces unowned
// template tags. Retire the initial static SEO tags only when React starts,
// leaving the prerendered document intact for no-JS readers and crawlers.
document.head.querySelectorAll('title, meta[name="description"], meta[name="robots"], meta[property^="og:"], meta[name^="twitter:"], link[rel="canonical"], script[type="application/ld+json"]')
  .forEach((element) => element.remove());

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <HelmetProvider>
        <LanguageProvider>
          <BrowserRouter basename={basename}>
            <SplashScreen>
              <App />
            </SplashScreen>
          </BrowserRouter>
        </LanguageProvider>
      </HelmetProvider>
    </ErrorBoundary>
  </StrictMode>,
);
