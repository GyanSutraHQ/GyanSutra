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
    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const preference = () => setReduced(media.matches);
    const visibility = () => { root.dataset.pageVisible = String(!document.hidden); };
    preference();
    visibility();
    media.addEventListener('change', preference);
    document.addEventListener('visibilitychange', visibility);
    const hero = root.querySelector('.gs-landing-hero');
    const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
    let frame = 0;
    let pointerX = 0;
    let pointerY = 0;
    const drawScene = () => {
      frame = 0;
      if (!hero || !finePointer.matches || window.innerWidth < 768 || root.dataset.motion === 'paused' || document.hidden || media.matches) return;
      const rect = hero.getBoundingClientRect();
      if (rect.bottom < 0 || rect.top > window.innerHeight) return;
      hero.style.setProperty('--scene-scroll', `${Math.min(rect.height, Math.max(0, -rect.top))}px`);
      hero.style.setProperty('--scene-pointer-x', `${pointerX}px`);
      hero.style.setProperty('--scene-pointer-y', `${pointerY}px`);
    };
    const scheduleScene = () => {
      if (!finePointer.matches || window.innerWidth < 768) return;
      if (!frame) frame = window.requestAnimationFrame(drawScene);
    };
    const pointer = (event) => {
      if (event.pointerType !== 'mouse' || !hero) return;
      const rect = hero.getBoundingClientRect();
      pointerX = ((event.clientX - rect.left) / rect.width - .5) * 18;
      pointerY = ((event.clientY - rect.top) / rect.height - .5) * 12;
      scheduleScene();
    };
    const resetPointer = () => { pointerX = 0; pointerY = 0; scheduleScene(); };
    if (finePointer.matches) {
      window.addEventListener('scroll', scheduleScene, { passive: true });
      hero?.addEventListener('pointermove', pointer, { passive: true });
      hero?.addEventListener('pointerleave', resetPointer);
      scheduleScene();
    }

    const tiltCards = finePointer.matches ? Array.from(root.querySelectorAll('.gs-tilt-card')) : [];
    const handleCardMove = (event) => {
      if (event.pointerType !== 'mouse' || root.dataset.motion === 'paused' || media.matches) return;
      const card = event.currentTarget;
      const rect = card.getBoundingClientRect();
      const nx = (event.clientX - rect.left) / rect.width - 0.5;
      const ny = (event.clientY - rect.top) / rect.height - 0.5;
      card.style.setProperty('--card-rx', `${(-ny * 7).toFixed(2)}deg`);
      card.style.setProperty('--card-ry', `${(nx * 9).toFixed(2)}deg`);
      card.style.setProperty('--glare-x', `${((nx + 0.5) * 100).toFixed(1)}%`);
      card.style.setProperty('--glare-y', `${((ny + 0.5) * 100).toFixed(1)}%`);
    };
    const handleCardLeave = (event) => {
      const card = event.currentTarget;
      card.style.setProperty('--card-rx', '0deg');
      card.style.setProperty('--card-ry', '0deg');
    };
    tiltCards.forEach((card) => {
      card.addEventListener('pointermove', handleCardMove, { passive: true });
      card.addEventListener('pointerleave', handleCardLeave);
    });

    let observer;
    let zoneObserver;
    if ('IntersectionObserver' in window) {
      observer = new IntersectionObserver((entries) => {
        entries.forEach(({ target, isIntersecting }) => {
          if (!isIntersecting) return;
          target.dataset.revealed = 'true';
          observer.unobserve(target);
        });
      }, { threshold: 0.04, rootMargin: '60px 0px' });
      // Scenery resumes a full screen before it re-enters the viewport, so scrolling
      // back up never shows a cold, half-started animation.
      zoneObserver = new IntersectionObserver((entries) => {
        entries.forEach(({ target, isIntersecting }) => { target.dataset.inView = String(isIntersecting); });
      }, { threshold: 0, rootMargin: '100% 0px' });
      root.querySelectorAll('[data-reveal]').forEach((element) => observer.observe(element));
      root.querySelectorAll('.gs-motion-zone').forEach((element) => zoneObserver.observe(element));
      root.dataset.enhanced = 'true';
    }
    return () => {
      observer?.disconnect();
      zoneObserver?.disconnect();
      if (frame) window.cancelAnimationFrame(frame);
      window.removeEventListener('scroll', scheduleScene);
      hero?.removeEventListener('pointermove', pointer);
      hero?.removeEventListener('pointerleave', resetPointer);
      tiltCards.forEach((card) => {
        card.removeEventListener('pointermove', handleCardMove);
        card.removeEventListener('pointerleave', handleCardLeave);
      });
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
