import test from 'node:test';
import assert from 'node:assert/strict';
import {
  canAutoReload,
  initAppUpdate,
  isUserTyping,
  shouldReloadForVersion,
  UPDATE_RELOAD_KEY,
} from './appUpdate.js';

test('shouldReloadForVersion compares distinct non-empty build versions', () => {
  assert.equal(shouldReloadForVersion('v1', 'v2'), true);
  assert.equal(shouldReloadForVersion('v1', 'v1'), false);
  assert.equal(shouldReloadForVersion('', 'v2'), false);
  assert.equal(shouldReloadForVersion('v1', ''), false);
});

test('canAutoReload throttles repeated reloads within cooldown window', () => {
  const store = new Map();
  const storage = {
    getItem: (k) => store.get(k) ?? null,
    setItem: (k, v) => store.set(k, v),
  };

  assert.equal(canAutoReload(storage, 100_000), true);
  assert.equal(store.get(UPDATE_RELOAD_KEY), '100000');
  assert.equal(canAutoReload(storage, 105_000), false);
  assert.equal(canAutoReload(storage, 120_000), true);
});

test('isUserTyping detects active text fields and contentEditable elements', () => {
  assert.equal(isUserTyping({ activeElement: { tagName: 'TEXTAREA' } }), true);
  assert.equal(isUserTyping({ activeElement: { tagName: 'INPUT' } }), true);
  assert.equal(isUserTyping({ activeElement: { tagName: 'DIV', isContentEditable: true } }), true);
  assert.equal(isUserTyping({ activeElement: { tagName: 'BODY' } }), false);
});

test('initAppUpdate reloads cleanly on service worker controllerchange after initial install', async () => {
  const listeners = new Map();
  const docListeners = new Map();
  let reloads = 0;
  const session = new Map();

  const sw = {
    controller: { scriptURL: '/sw.js' },
    addEventListener: (ev, fn) => listeners.set(ev, fn),
    removeEventListener: (ev) => listeners.delete(ev),
  };
  const win = {
    location: { origin: 'https://gyansutraapp.com', reload: () => { reloads += 1; } },
    sessionStorage: {
      getItem: (k) => session.get(k) ?? null,
      setItem: (k, v) => session.set(k, v),
    },
    setTimeout: () => 1,
    clearTimeout: () => {},
    setInterval: () => 2,
    clearInterval: () => {},
  };
  const doc = {
    visibilityState: 'visible',
    activeElement: { tagName: 'BODY' },
    addEventListener: (ev, fn) => docListeners.set(ev, fn),
    removeEventListener: (ev) => docListeners.delete(ev),
  };

  const cleanup = initAppUpdate({
    currentVersion: 'build-1',
    win,
    doc,
    nav: { serviceWorker: sw },
    fetchFn: async () => ({ ok: true, json: async () => ({ version: 'build-1' }) }),
  });

  await listeners.get('controllerchange')?.();
  assert.equal(reloads, 1);

  cleanup();
  assert.equal(listeners.size, 0);
  assert.equal(docListeners.size, 0);
});

test('initAppUpdate reloads when server version.json differs from running build', async () => {
  const listeners = new Map();
  let reloads = 0;
  let updated = false;
  let scheduledIdle = null;
  const session = new Map();

  const sw = {
    controller: null,
    getRegistration: async () => ({ update: async () => { updated = true; } }),
    addEventListener: () => {},
    removeEventListener: () => {},
  };
  const win = {
    location: { origin: 'https://gyansutraapp.com', reload: () => { reloads += 1; } },
    sessionStorage: {
      getItem: (k) => session.get(k) ?? null,
      setItem: (k, v) => session.set(k, v),
    },
    requestIdleCallback: (cb) => { scheduledIdle = cb; return 1; },
    cancelIdleCallback: () => {},
    setInterval: () => 2,
    clearInterval: () => {},
  };
  const doc = {
    visibilityState: 'visible',
    activeElement: { tagName: 'BODY' },
    addEventListener: (ev, fn) => listeners.set(ev, fn),
    removeEventListener: (ev) => listeners.delete(ev),
  };

  const cleanup = initAppUpdate({
    currentVersion: 'build-old',
    win,
    doc,
    nav: { serviceWorker: sw },
    fetchFn: async () => ({ ok: true, json: async () => ({ version: 'build-new' }) }),
  });

  await scheduledIdle?.();
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.equal(updated, true);
  assert.equal(reloads, 1);
  cleanup();
});
