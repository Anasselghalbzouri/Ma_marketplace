/**
 * T-012 — i18next instance.
 *
 * Cadre uniquement : on charge un namespace `common` avec les chaînes minimales
 * du socle (header, navigation, états vides/chargement/erreur). Les modules
 * métier ajoutent leurs namespaces au démarrage (lazy `loadPath`).
 *
 * Conformité :
 *  - `supportedLngs` = langues du socle (cf. i18nSlice).
 *  - `fallbackLng` = `fr` (Constitution IX, ENF-001).
 *  - `nonExplicitSupportedLngs` : i18next détecte `fr-FR` → `fr`.
 *  - `react.returnNull` = false (jamais de composant vide silencieux).
 */

import i18n from 'i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import { initReactI18next } from 'react-i18next';
import frCommon from './locales/fr/common.json';
import arCommon from './locales/ar/common.json';
import { DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES } from '@/store/slices/i18nSlice';

void i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      fr: { common: frCommon },
      ar: { common: arCommon },
    },
    ns: ['common'],
    defaultNS: 'common',
    fallbackLng: DEFAULT_LANGUAGE,
    supportedLngs: SUPPORTED_LANGUAGES as unknown as string[],
    nonExplicitSupportedLngs: true,
    detection: {
      // Le détecteur n'écrit pas dans localStorage : c'est le slice Redux qui
      // persiste (cf. i18nSlice.setLanguage) pour rester source de vérité unique.
      order: ['navigator', 'htmlTag'],
      caches: [],
      lookupLocalStorage: 'mplm.lang',
    },
    interpolation: {
      escapeValue: false, // React échappe déjà.
    },
    returnNull: false,
    returnEmptyString: false,
  });

export default i18n;