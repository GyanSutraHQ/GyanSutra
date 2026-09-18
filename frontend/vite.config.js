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
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2}'],
        runtimeCaching: [
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
      // Serve one transpiled bundle instead of allowing browsers with partial
      // ESM support (notably iOS Safari 12–13 and legacy Edge) to parse a
      // modern dependency chunk that they cannot execute. IE is not supported
      // by React 19, but current and older supported iOS/Windows browsers are.
      !isAndroidBuild && legacy({
        targets: ['iOS >= 12', 'Safari >= 12', 'Edge >= 16', 'Chrome >= 64'],
        renderModernChunks: false,
      }),
    ].filter(Boolean),
    server: {
      port: 5173,
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks: (id) => {
            if (id.includes('node_modules')) {
              if (id.includes('react') || id.includes('react-dom') || id.includes('react-router-dom')) {
                return 'vendor';
              }
            }
          },
        },
      },
    },
  };
});
