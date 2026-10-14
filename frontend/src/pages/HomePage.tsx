/**
 * T-012 — page d'accueil du socle.
 *
 * But : démontrer l'enveloppe applicative (Header, LanguageSwitcher, navigation,
 * responsive 360 px, états standards) sans dépendre d'aucun endpoint métier.
 *
 * Les modules M02/M03/M04/M11 remplaceront ce placeholder par leurs propres
 * écrans. Le contenu actuel reste utile en V1 pour la page racine publique :
 * un hero, un appel à l'action « Voir le catalogue » et un pied informatif
 * sur les langues supportées.
 */

import type { ReactElement } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { SUPPORTED_LANGUAGES } from '@/store/slices/i18nSlice';

export function HomePage(): ReactElement {
  const { t } = useTranslation('common');
  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-bold text-ink-900">{t('app.name')}</h1>
        <p className="text-ink-700">{t('app.tagline')}</p>
      </header>

      <div className="rounded border border-ink-300 bg-surface p-4">
        <Link
          to="/products"
          className="inline-flex w-full items-center justify-center rounded bg-brand-500 px-4 py-3 font-semibold text-white hover:bg-brand-700"
        >
          {t('header.catalog')} →
        </Link>
      </div>

      <div className="rounded border border-dashed border-ink-300 p-4 text-sm text-ink-500">
        <p>
          <strong>{`T-012 socle :`}</strong>
          {` routage, client API, session, mise en page 360 px, i18n (${
            SUPPORTED_LANGUAGES.join(', ')
          }).`}
        </p>
        <p className="mt-1">{`Les écrans métier (M02–M11) seront ajoutés par les tâches filles de Compass.`}</p>
      </div>
    </section>
  );
}