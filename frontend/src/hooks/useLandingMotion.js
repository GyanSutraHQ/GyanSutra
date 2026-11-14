import { useEffect, useRef, useState } from 'react';

export default function useLandingMotion() {
  const rootRef = useRef(null);
  const [paused, setPaused] = useState(() => {
    try { return typeof window !== 'undefined' && localStorage.getItem('gyansutra-motion') === 'paused'; }
    catch { return false; }
  });
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return undefined;
    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const preference = () => setReduced(media.matches);
    const visibility = () => { root.dataset.pageVisible = String(!document.hidden); };
    preference();
    visibility();
    media.addEventListener('change', preference);
    document.addEventListener('visibilitychange', visibility);

    let zoneObserver;
    if ('IntersectionObserver' in window) {
      // Scenery pauses cleanly once scrolled far off screen, leaving native
      // scrolling completely free of main-thread scroll or pointer listeners.
      zoneObserver = new IntersectionObserver((entries) => {
        entries.forEach(({ target, isIntersecting }) => { target.dataset.inView = String(isIntersecting); });
      }, { threshold: 0, rootMargin: '100% 0px' });
      root.querySelectorAll('.gs-motion-zone').forEach((element) => zoneObserver.observe(element));
    }

    return () => {
      zoneObserver?.disconnect();
      media.removeEventListener('change', preference);
      document.removeEventListener('visibilitychange', visibility);
    };
  }, []);

  const toggleMotion = () => setPaused((current) => {
    try { localStorage.setItem('gyansutra-motion', current ? 'running' : 'paused'); } catch { /* session preference */ }
    return !current;
  });
  return { rootRef, paused: paused || reduced, reduced, toggleMotion };
}
