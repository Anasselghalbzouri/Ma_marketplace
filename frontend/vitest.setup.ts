import '@testing-library/jest-dom/vitest';
import { afterEach, beforeEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// jsdom v26+ ne fournit plus `localStorage` par défaut ; on en installe un
// in-memory pour permettre aux slices auth/i18n de persister leurs valeurs
// pendant les tests.
if (typeof window !== 'undefined' && typeof window.localStorage === 'undefined') {
  const store = new Map<string, string>();
  Object.defineProperty(window, 'localStorage', {
    value: {
      getItem: (k: string) => store.get(k) ?? null,
      setItem: (k: string, v: string) => { store.set(k, v); },
      removeItem: (k: string) => { store.delete(k); },
      clear: () => { store.clear(); },
      key: (i: number) => Array.from(store.keys())[i] ?? null,
      get length() { return store.size; },
    },
    configurable: true,
  });
}

// jsdom ne fournit pas matchMedia ; i18next-browser-languagedetector l'utilise
// dans certains chemins. Stub minimal.
if (typeof window !== 'undefined' && typeof window.matchMedia === 'undefined') {
  window.matchMedia = (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => undefined,
    removeListener: () => undefined,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
    dispatchEvent: () => false,
  });
}

// Chaque test repart d'un DOM propre (storage + jsdom URL).
beforeEach(() => {
  window.localStorage.clear();
});
afterEach(() => {
  cleanup();
});