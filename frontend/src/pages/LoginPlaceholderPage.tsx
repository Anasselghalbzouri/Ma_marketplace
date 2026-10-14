/**
 * T-012 — placeholder authentification.
 *
 * L'écran complet de connexion est livré par T-014/T-016 (M01). Le socle
 * expose uniquement la coquille (titre + état "à venir") pour que la route
 * `/login` réponde dès maintenant et puisse être référencée par le Header
 * et les futures opérations RTK Query.
 */

import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

export function LoginPlaceholderPage(): ReactElement {
  const { t } = useTranslation('common');
  return (
    <section className="space-y-4">
      <h1 className="text-xl font-bold text-ink-900">{t('header.login')}</h1>
      <p className="rounded border border-dashed border-ink-300 bg-surface p-4 text-sm text-ink-700">
        {`L'écran de connexion (M01) sera livré par la tâche T-014/T-016 d'Anvil.`}
      </p>
    </section>
  );
}