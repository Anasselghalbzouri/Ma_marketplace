/**
 * T-012 — sélecteur de langue (cadre i18n).
 *
 * Source : ENF-001 (langues — Q11). Permet à l'utilisateur de basculer entre
 * les langues du socle (`fr`, `ar`). Le RTL est appliqué automatiquement
 * (cf. i18nSlice.setLanguage → document.dir).
 *
 * La liste des langues n'est PAS exhaustive : T-013 ajoutera éventuellement
 * d'autres locales lorsque Q11 sera tranchée par @user.
 */

import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  selectLanguage,
  setLanguage,
  SUPPORTED_LANGUAGES,
  type SupportedLanguage,
} from '@/store/slices/i18nSlice';

export function LanguageSwitcher(): ReactElement {
  const { t } = useTranslation('common');
  const dispatch = useAppDispatch();
  const current = useAppSelector(selectLanguage);

  return (
    <label className="flex items-center gap-2 text-sm">
      <span className="sr-only">{t('header.languageSwitcher')}</span>
      <span aria-hidden="true" className="text-ink-500">
        🌐
      </span>
      <select
        aria-label={t('header.languageSwitcher')}
        value={current}
        onChange={(e) => {
          dispatch(setLanguage(e.target.value as SupportedLanguage));
        }}
        className="rounded border border-ink-300 bg-white px-2 py-1 text-sm"
      >
        {SUPPORTED_LANGUAGES.map((lng) => (
          <option key={lng} value={lng}>
            {t(`languages.${lng}`)}
          </option>
        ))}
      </select>
    </label>
  );
}