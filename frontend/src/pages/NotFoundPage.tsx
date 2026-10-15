import type { ReactElement } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export function NotFoundPage(): ReactElement {
  const { t } = useTranslation('common');
  return (
    <section className="space-y-4 text-center">
      <h1 className="text-3xl font-bold text-ink-900">404</h1>
      <p className="text-ink-700">{t('states.empty')}</p>
      <Link
        to="/"
        className="inline-flex items-center rounded bg-brand-500 px-3 py-2 text-white hover:bg-brand-700"
      >
        {t('header.home')}
      </Link>
    </section>
  );
}