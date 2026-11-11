import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import legacy from '@vitejs/plugin-legacy';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

const webBase = process.env.VITE_BASE_PATH || '/';
const siteUrl = (process.env.VITE_SITE_URL || 'https://gyansutraapp.com/').replace(/\/$/, '') + '/';
process.env.VITE_SITE_URL = siteUrl;

export default defineConfig(({ mode }) => {
  const isAndroidBuild = mode === 'android';

  return {
    base: isAndroidBuild ? '/' : webBase,
    plugins: [
      tailwindcss(),
      react(),
      !isAndroidBuild && VitePWA({
      // Take a new app shell immediately. `prompt` leaves installed PWAs on
      // their old HTML/chunk set until every open client has been closed,
      // which is especially common on iOS and Windows.
      registerType: 'autoUpdate',
      manifest: false, // We provide our own public/manifest.json
      workbox: {
        clientsClaim: true,
        skipWaiting: true,
        // Cache the small shell, not every reader and the large audio inventory
        // during a first homepage visit. Other chunks cache as they are opened.
        globPatterns: ['index.html', 'icons/*.{png,svg,ico}', 'assets/*.{css,woff,woff2}', 'assets/{index,vendor,polyfills,rolldown-runtime}-*.js'],
        runtimeCaching: [
          {
            urlPattern: /\/assets\/.*\.js$/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'app-route-chunks',
              expiration: { maxEntries: 60, maxAgeSeconds: 60 * 60 * 24 * 30 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
          // Google Fonts - cache-first
          {
            urlPattern: /^https:\/\/fonts\.(googleapis|gstatic)\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts',
              expiration: { maxEntries: 20, maxAgeSeconds: 60 * 60 * 24 * 365 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
          // API - network-first, fall back to cache
          {
            urlPattern: /^https?:\/\/.*\/api\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-scripture',
              expiration: { maxEntries: 200, maxAgeSeconds: 60 * 60 * 24 * 30 },
              networkTimeoutSeconds: 30,
              cacheableResponse: { statuses: [0, 200] },
            },
          },
        ],
      },
      }),
      // Modern visitors get the smaller native bundle; the legacy plugin's
      // feature detection serves SystemJS to older supported browsers. Emitting
      // both also preserves Vite 8's extracted production stylesheets.
      !isAndroidBuild && legacy({
        targets: ['iOS >= 12', 'Safari >= 12', 'Edge >= 16', 'Chrome >= 64'],
        renderModernChunks: true,
      }),
    ].filter(Boolean),
    server: {
      port: 5173,
      // Optional same-origin proxy for verifying a local reader against a
      // deployed public API. Production builds and CORS settings are unchanged.
      proxy: process.env.VITE_DEV_API_PROXY ? {
        '/api': { target: process.env.VITE_DEV_API_PROXY, changeOrigin: true },
      } : undefined,
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks: (id) => {
            if (id.includes('node_modules')) {
              if (/node_modules\/(react|react-dom|react-router|react-router-dom|scheduler)\//.test(id)) {
                return 'vendor';
              }
            }
          },
        },
      },
    },
  };
});
