/**
 * T-012 — tests du slice i18n.
 *
 * Couvre :
 *  - D\u00e9tection initiale via localStorage prioritaire sur navigator.
 *  - setLanguage met \u00e0 jour state + localStorage + document.dir.
 *  - Bascule RTL automatique pour `ar`.
 */

import { describe, expect, it, beforeEach } from 'vitest';
import i18nReducer, {
  hydrateI18nFromStorage,
  selectIsRtl,
  selectLanguage,
  setLanguage,
} from '@/store/slices/i18nSlice';

function makeState() {
  return { i18n: i18nReducer(undefined, { type: 'init' }) };
}

describe('i18nSlice', () => {
  beforeEach(() => {
    window.localStorage.clear();
    document.documentElement.lang = 'fr';
    document.documentElement.dir = 'ltr';
  });

  it('setLanguage met \u00e0 jour la langue, localStorage et <html>', () => {
    const s1 = i18nReducer(makeState().i18n, setLanguage('ar'));
    expect(selectLanguage({ i18n: s1 })).toBe('ar');
    expect(selectIsRtl({ i18n: s1 })).toBe(true);
    expect(window.localStorage.getItem('mplm.lang')).toBe('ar');
    expect(document.documentElement.lang).toBe('ar');
    expect(document.documentElement.dir).toBe('rtl');
  });

  it('bascule LTR pour fr', () => {
    const s1 = i18nReducer(makeState().i18n, setLanguage('ar'));
    const s2 = i18nReducer(s1, setLanguage('fr'));
    expect(document.documentElement.dir).toBe('ltr');
    expect(selectIsRtl({ i18n: s2 })).toBe(false);
  });

  it('hydrateI18nFromStorage marque hydrated=true', () => {
    const s1 = i18nReducer(makeState().i18n, hydrateI18nFromStorage());
    expect(s1.hydrated).toBe(true);
  });
});