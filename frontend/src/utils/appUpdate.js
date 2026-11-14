import { clearStaleAppShell } from './chunkRecovery.js';

export const UPDATE_RELOAD_KEY = 'gyansutra_update_reload_at';
export const RELOAD_COOLDOWN_MS = 15_000;
export const VERSION_CHECK_THROTTLE_MS = 30_000;

export function isUserTyping(doc = typeof document !== 'undefined' ? document : null) {
  const active = doc?.activeElement;
  if (!active) return false;
  const tag = String(active.tagName || '').toUpperCase();
  return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || Boolean(active.isContentEditable);
}

export function canAutoReload(storage = typeof window !== 'undefined' ? window.sessionStorage : null, now = Date.now()) {
  if (!storage) return false;
  try {
    const previous = Number(storage.getItem(UPDATE_RELOAD_KEY));
    if (Number.isFinite(previous) && now - previous < RELOAD_COOLDOWN_MS) {
      return false;
    }
    storage.setItem(UPDATE_RELOAD_KEY, String(now));
    return true;
  } catch {
    return false;
  }
}

export function shouldReloadForVersion(currentVersion, remoteVersion) {
  return Boolean(currentVersion && remoteVersion && currentVersion !== remoteVersion);
}

/**
 * Keep open tabs and returning visitors on the latest deployed bundle:
 * - React immediately when a newly activated service worker takes control
 * - Verify /version.json on idle boot, tab focus/resume, and long-lived sessions
 */
export function initAppUpdate({
  currentVersion,
  baseUrl = '/',
  win = typeof window !== 'undefined' ? window : null,
  doc = typeof document !== 'undefined' ? document : null,
  nav = typeof navigator !== 'undefined' ? navigator : null,
  fetchFn = typeof fetch !== 'undefined' ? fetch.bind(globalThis) : null,
} = {}) {
  if (!win || !doc) return () => {};

  let reloading = false;
  let pendingReloadOnBlur = false;
  let lastVersionCheck = 0;

  const scheduleOrReloadNow = async ({ clearCaches = false } = {}) => {
    if (reloading) return false;
    if (isUserTyping(doc)) {
      pendingReloadOnBlur = true;
      return false;
    }
    if (!canAutoReload(win.sessionStorage)) return false;
    reloading = true;
    if (clearCaches) {
      try {
        await clearStaleAppShell({ includeHtml: true, unregister: false });
      } catch {
        // Proceed with reload even if cache cleanup throws.
      }
    }
    win.location.reload();
    return true;
  };

  const handleBlur = () => {
    if (!pendingReloadOnBlur || isUserTyping(doc)) return;
    pendingReloadOnBlur = false;
    void scheduleOrReloadNow({ clearCaches: true });
  };
  doc.addEventListener('focusout', handleBlur);

  const sw = nav?.serviceWorker;
  const hadController = Boolean(sw?.controller);
  const handleControllerChange = () => {
    if (!hadController) return;
    void scheduleOrReloadNow({ clearCaches: false });
  };
  sw?.addEventListener?.('controllerchange', handleControllerChange);

  const checkForUpdates = async (force = false) => {
    const now = Date.now();
    if (!force && now - lastVersionCheck < VERSION_CHECK_THROTTLE_MS) return false;
    lastVersionCheck = now;

    if (sw?.getRegistration) {
      try {
        const scope = new URL(baseUrl, win.location.origin).href;
        const reg = await sw.getRegistration(scope);
        await reg?.update();
      } catch {
        // Ignore offline SW update check failures.
      }
    }

    if (!currentVersion || !fetchFn) return false;
    try {
      const normalizedBase = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`;
      const response = await fetchFn(`${normalizedBase}version.json?t=${now}`, { cache: 'no-store' });
      if (!response?.ok) return false;
      const payload = await response.json();
      if (shouldReloadForVersion(currentVersion, payload?.version)) {
        return await scheduleOrReloadNow({ clearCaches: true });
      }
    } catch {
      // Offline or transient CDN blip; keep current view uninterrupted.
    }
    return false;
  };

  const handleVisibilityChange = () => {
    if (doc.visibilityState === 'visible') {
      void checkForUpdates(false);
    }
  };
  doc.addEventListener('visibilitychange', handleVisibilityChange);

  let idleId = null;
  let initialTimerId = null;
  if ('requestIdleCallback' in win) {
    idleId = win.requestIdleCallback(() => void checkForUpdates(true), { timeout: 2500 });
  } else {
    initialTimerId = win.setTimeout(() => void checkForUpdates(true), 1500);
  }
  const intervalId = win.setInterval(() => {
    if (doc.visibilityState === 'visible') {
      void checkForUpdates(false);
    }
  }, 5 * 60_000);

  return () => {
    doc.removeEventListener('focusout', handleBlur);
    doc.removeEventListener('visibilitychange', handleVisibilityChange);
    sw?.removeEventListener?.('controllerchange', handleControllerChange);
    if (idleId !== null && 'cancelIdleCallback' in win) win.cancelIdleCallback(idleId);
    if (initialTimerId !== null) win.clearTimeout(initialTimerId);
    win.clearInterval(intervalId);
  };
}
