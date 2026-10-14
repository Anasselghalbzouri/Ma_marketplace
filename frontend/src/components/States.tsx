/**
 * T-012 — états standards de l'interface.
 *
 * Conventions socle (réutilisées par tous les modules M01–M11) :
 * - `LoadingState` : skeleton léger, accessible (role="status", aria-live="polite").
 * - `ErrorState`   : message d'erreur lisible + bouton "Réessayer" si appelant.
 * - `EmptyState`   : message vide + action optionnelle.
 *
 * Aucune logique métier : ces composants ne connaissent pas le code d'erreur
 * API. La traduction du code vers un libellé localisé est faite par l'appelant,
 * qui peut s'appuyer sur `t('states.errorGeneric')` comme fallback.
 */

import { useTranslation } from 'react-i18next';
import type { ReactNode } from 'react';

export interface LoadingStateProps {
  /** Texte localisé (par défaut t('states.loading')). */
  label?: string;
  /** Hauteur approximative (pour les skeletons). */
  height?: 'sm' | 'md' | 'lg';
}

const HEIGHTS: Record<NonNullable<LoadingStateProps['height']>, string> = {
  sm: 'h-16',
  md: 'h-32',
  lg: 'h-56',
};

export function LoadingState({ label, height = 'md' }: LoadingStateProps): ReactNode {
  const { t } = useTranslation('common');
  return (
    <div
      role="status"
      aria-live="polite"
      className={`mplm-skel w-full ${HEIGHTS[height]}`}
    >
      <span className="sr-only">{label ?? t('states.loading')}</span>
    </div>
  );
}

export interface ErrorStateProps {
  title?: string;
  detail?: string;
  onRetry?: () => void;
}

export function ErrorState({ title, detail, onRetry }: ErrorStateProps): ReactNode {
  const { t } = useTranslation('common');
  return (
    <div
      role="alert"
      className="rounded border border-red-200 bg-red-50 p-4 text-sm text-red-900"
    >
      <p className="font-semibold">{title ?? t('states.errorGeneric')}</p>
      {detail !== undefined ? <p className="mt-1 text-red-800">{detail}</p> : null}
      {onRetry !== undefined ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-3 inline-flex items-center rounded bg-red-700 px-3 py-2 text-white hover:bg-red-800"
        >
          {t('states.retry')}
        </button>
      ) : null}
    </div>
  );
}

export interface EmptyStateProps {
  title?: string;
  detail?: string;
  action?: ReactNode;
}

export function EmptyState({ title, detail, action }: EmptyStateProps): ReactNode {
  const { t } = useTranslation('common');
  return (
    <div className="rounded border border-dashed border-ink-300 bg-surface p-6 text-center text-ink-700">
      <p className="font-medium">{title ?? t('states.empty')}</p>
      {detail !== undefined ? <p className="mt-1 text-sm text-ink-500">{detail}</p> : null}
      {action !== undefined ? <div className="mt-3">{action}</div> : null}
    </div>
  );
}