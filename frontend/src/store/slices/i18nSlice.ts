/**
 * T-012 — slice i18n (cadre).
 *
 * Source : ENF-001 (langues — Q11 encore ouverte : fr confirmé, ar pressenti).
 *          specs/003-contrat-api/contracts/openapi.yaml en-tête
 *          (« messages en français », « codes en anglais »).
 *
 * T-012 livre uniquement le **cadre** : le sélecteur de langue, la persistance
 * localStorage, l'attribut `dir` du `<html>` et le `Accept-Language` propagé par
 * le baseQuery. Les **traductions effectives** sont l'objet de T-013 (dépend
 * de T-012 + Q11). T-013 ajoutera les fichiers de langue et garantira la
 * couverture 100 % par langue.
 *
 * Langues du socle :
 *  - `fr` : français (par défaut, confirmé par le contrat, messages d'erreur,
 *           interface).
 *  - `ar` : arabe (pressenti, ENF-001 Q11). T-013 fournira les chaînes.
 *
 * Tant que la langue `ar` n'est pas livrée, on retombe gracieusement sur `fr`
 * (fallback explicite d'i18next).
 */

import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

export const SUPPORTED_LANGUAGES = ['fr', 'ar'] as const;
export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number];

export const DEFAULT_LANGUAGE: SupportedLanguage = 'fr';
export const RTL_LANGUAGES: ReadonlySet<SupportedLanguage> = new Set(['ar']);

export interface I18nState {
  language: SupportedLanguage;
  hydrated: boolean;
}

const STORAGE_KEY = 'mplm.lang';

function detectInitial(): SupportedLanguage {
  if (typeof window === 'undefined') return DEFAULT_LANGUAGE;
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored !== null && SUPPORTED_LANGUAGES.includes(stored as SupportedLanguage)) {
      return stored as SupportedLanguage;
    }
  } catch {
    /* localStorage indisponible : on retombe sur défaut. */
  }
  const nav = window.navigator.language.toLowerCase();
  if (nav.startsWith('ar')) return 'ar';
  return DEFAULT_LANGUAGE;
}

const initialState: I18nState = {
  language: detectInitial(),
  hydrated: false,
};

const i18nSlice = createSlice({
  name: 'i18n',
  initialState,
  reducers: {
    hydrateFromStorage(state) {
      state.hydrated = true;
    },
    setLanguage(state, action: PayloadAction<SupportedLanguage>) {
      state.language = action.payload;
      state.hydrated = true;
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(STORAGE_KEY, action.payload);
        document.documentElement.lang = action.payload;
        document.documentElement.dir = RTL_LANGUAGES.has(action.payload) ? 'rtl' : 'ltr';
      }
    },
  },
});

export const { hydrateFromStorage: hydrateI18nFromStorage, setLanguage } = i18nSlice.actions;
export default i18nSlice.reducer;

export const selectLanguage = (s: { i18n: I18nState }): SupportedLanguage => s.i18n.language;
export const selectIsRtl = (s: { i18n: I18nState }): boolean => RTL_LANGUAGES.has(s.i18n.language);