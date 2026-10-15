/**
 * T-012 — page "Catalogue" (placeholder M03).
 *
 * But : démontrer l'intégration RTK Query contre l'API (via le mock serveur
 * de T-012 ou, plus tard, contre l'API réelle). Cet écran ne consomme qu'un
 * seul endpoint public (`GET /api/v1/products`), conformément au contrat
 * T-003 (MP-01) : un visiteur non connecté parcourt le catalogue sans compte.
 *
 * Aucun rendu produit n'est encore implémenté — T-028 livrera la fiche produit.
 * Le socle se contente de prouver le câblage : un appel RTK Query, un état
 * chargement, un état vide, un état erreur (catalogué via `ApiError`).
 */

import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '@/api/api';
import { EmptyState, ErrorState, LoadingState } from '@/components/States';
import type { ApiError } from '@/api/errorEnvelope';

interface ProductSummary {
  id: number;
  name: string;
  price: string; // DECIMAL chaîne (ADR-018).
}

interface Paginated<T> {
  data: T[];
  meta: { page: number; per_page: number; total: number; total_pages: number };
}

export function CatalogPage(): ReactElement {
  const { t } = useTranslation('common');
  const [page] = useState(1);

  // T-012 livre l'endpoint `listProducts` avec un squelette de contrat. Le
  // câblage RTK Query est effectif ; le rendu produit détaillé (carte, photos,
  // pagination, filtres) est livré par T-028. T-012 se contente ici de
  // démontrer l'appel : la requête part (`skip` à `false` par défaut) et la
  // liste vide s'affiche si le backend n'a pas de produits.
  const result = api.useListProductsQuery({ page, per_page: 12 });

  return (
    <section className="space-y-4">
      <h1 className="text-xl font-bold text-ink-900">{t('header.catalog')}</h1>

      {result.isLoading ? <LoadingState height="lg" /> : null}

      {result.isError ? (
        <ErrorState
          detail={
            (result.error as { data?: ApiError })?.data?.message
            ?? t('states.errorUnavailable')
          }
        />
      ) : null}

      {result.isSuccess && result.data.data.length === 0 ? (
        <EmptyState detail={t('states.empty')} />
      ) : null}

      {result.isSuccess && result.data.data.length > 0 ? (
        <ul className="grid grid-cols-2 gap-3" data-testid="catalog-list">
          {result.data.data.map((p: ProductSummary) => (
            <li
              key={p.id}
              className="rounded border border-ink-300 bg-white p-3 text-sm shadow-sm"
            >
              <p className="font-medium text-ink-900">{p.name}</p>
              <p className="text-ink-500">{`${p.price} MAD`}</p>
            </li>
          ))}
        </ul>
      ) : null}

      <p className="text-xs text-ink-500">
        {(result.data as Paginated<ProductSummary> | undefined)?.meta
          ? `${(result.data as Paginated<ProductSummary>).meta.total} produits au total`
          : '\u00a0'}
      </p>
    </section>
  );
}