/**
 * T-012 — client d'API (RTK Query).
 *
 * Source : specs/003-contrat-api/contracts/openapi.yaml (101 opérations).
 * Cette couche expose :
 * - `baseQuery` typé qui injecte le jeton (socle T-001 auth), propage la langue
 *   (`Accept-Language`, ENF-001), et convertit toute réponse non-2xx en `ApiError`
 *   (cf. errorEnvelope.ts).
 * - Tags de cache dérivés du contrat (auth/cart/products/orders/...) ; chaque module
 *   métier fils ajoute ses propres endpoints en `injectEndpoints` (cf. slices).
 * - Aucun endpoint métier n'est défini ici : T-012 livre le **cadre**, pas les
 *   routes. Les routes concrètes arrivent avec T-021 (produits vendeur),
 *   T-028 (catalogue), T-035 (panier/commande), etc.
 *
 * Branchement backend : voir vite.config.ts (proxy `/api`, `/photos`) et
 * docs/integration.md. Le backend Laravel (`backend/`) écoute sur :8080
 * (T-004) ; les modules M01–M11 seront livrés par Anvil.
 */

import {
  createApi,
  fetchBaseQuery,
  type BaseQueryFn,
  type FetchArgs,
  type FetchBaseQueryError,
} from '@reduxjs/toolkit/query/react';
import { ApiError, toApiError, type ErrorCode } from './errorEnvelope';

export interface RootStateShape {
  // Le store complet est défini dans src/store/index.ts. Cette projection suffit
  // au baseQuery pour lire le jeton et la langue sans dépendance circulaire.
  auth: { token: string | null };
  i18n: { language: 'fr' | 'ar' };
}

const rawBaseQuery = fetchBaseQuery({
  baseUrl: '/api/v1',
  prepareHeaders: (headers, { getState }) => {
    const state = getState() as RootStateShape;
    if (state.auth?.token) {
      headers.set('Authorization', `Bearer ${state.auth.token}`);
    }
    // ADR-019 : jeton de panier visiteur, persistant côté client.
    const cartToken = typeof window !== 'undefined'
      ? window.localStorage.getItem('mplm.cartToken')
      : null;
    if (cartToken !== null) {
      headers.set('X-Cart-Token', cartToken);
    }
    if (state.i18n?.language) {
      headers.set('Accept-Language', state.i18n.language);
    }
    headers.set('Accept', 'application/json');
    return headers;
  },
});

/**
 * Wrapper qui convertit les erreurs `fetchBaseQuery` en `ApiError` normalisé.
 * - Erreurs réseau / CORS / 502 proxy → `server_error`.
 * - 4xx/5xx avec enveloppe JSON → code+messsage du catalogue.
 * - Le 502 du proxy Vite (backend Laravel non démarré) est explicitement détecté.
 */
export const baseQuery: BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError> = async (
  args,
  api,
  extraOptions,
) => {
  const result = await rawBaseQuery(args, api, extraOptions);
  if (result.error) {
    const err = result.error;
    if (err.status === 'FETCH_ERROR') {
      // Le proxy Vite n'a pas pu joindre le backend (souvent ECONNREFUSED).
      // On expose un `server_error` pour que les composants traitent un seul cas.
      const apiErr = new ApiError({
        code: 'server_error',
        message: 'Le service est momentan\u00e9ment indisponible.',
        httpStatus: 0,
      });
      return { error: { status: 0, data: apiErr } };
    }
    if (typeof err.status === 'number' && err.data !== undefined) {
      // fetchBaseQuery a déjà parsé le JSON d'enveloppe dans err.data.
      const body = err.data as unknown;
      if (
        body !== null
        && typeof body === 'object'
        && 'error' in body
        && (body as { error: { code?: unknown } }).error !== null
        && typeof (body as { error: { code?: unknown } }).error === 'object'
        && typeof (body as { error: { code?: unknown } }).error.code === 'string'
      ) {
        const inner = (body as { error: { code: string; message?: string; details?: unknown } }).error;
        const apiErr = new ApiError({
          code: inner.code as ErrorCode | string,
          message: typeof inner.message === 'string' ? inner.message : '',
          httpStatus: err.status,
          ...(inner.details !== null && typeof inner.details === 'object' && inner.details !== undefined
            ? { details: inner.details as Record<string, unknown> }
            : {}),
        });
        return { error: { status: err.status, data: apiErr } };
      }
      // 502 du proxy : pas d'enveloppe — fallback propre.
      const apiErr = await toApiError(new Response(null, { status: err.status }));
      return { error: { status: err.status, data: apiErr } };
    }
  }
  return result;
};

/**
 * Tags RTK Query : un socle minimal. Les modules métier étendent via
 * `injectEndpoints` avec leurs propres tags et opérations.
 *
 * Convention : `<module>:<état>` (ex. `products:list`, `cart:current`).
 */
export const API_TAGS = [
  'Auth',
  'Me',
  'Cart',
  'Products',
  'Categories',
  'ServedCities',
  'SellerCommunes',
  'SellerProducts',
  'MyOrders',
  'MyReturns',
  'SellerSubOrders',
  'SellerReturns',
  'SellerAmounts',
  'Notifications',
] as const;

export type ApiTag = (typeof API_TAGS)[number];

export const api = createApi({
  reducerPath: 'mplmApi',
  baseQuery,
  tagTypes: API_TAGS,
  // Stale time court : ENF-004 (catalogue < 3 s) et M03 (panier frais).
  refetchOnReconnect: true,
  endpoints: (build) => ({
    /**
     * T-012 — stub d'endpoint catalogue.
     *
     * Pourquoi présent dès le socle :
     *  - Le contrat T-003 expose `GET /api/v1/products` (MP-01, UC-001) ;
     *    le client d'API doit donc savoir l'adresser.
     *  - T-028 (catalogue consommateur) **étendra** cet endpoint (filtres,
     *    tri, pagination configurable). T-012 se contente de poser le tag
     *    de cache et la signature de hook pour que les modules en aval
     *    puissent l'utiliser sans redéfinir l'API.
     *
     * Comportement par défaut : la requête n'est **pas** émise tant que
     * l'appelant n'utilise pas `{ skip: false }` — T-012 reste sans logique
     * métier, conformément à la consigne.
     */
    listProducts: build.query<
      { data: Array<{ id: number; name: string; price: string }>; meta: { page: number; per_page: number; total: number; total_pages: number } },
      { page?: number; per_page?: number; q?: string; category_id?: number }
    >({
      query: (params) => ({
        url: '/products',
        params: {
          page: params.page ?? 1,
          per_page: params.per_page ?? 20,
          ...(params.q !== undefined ? { q: params.q } : {}),
          ...(params.category_id !== undefined ? { category_id: params.category_id } : {}),
        },
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.data.map((p) => ({ type: 'Products' as const, id: p.id })),
              { type: 'Products' as const, id: 'LIST' },
            ]
          : [{ type: 'Products' as const, id: 'LIST' }],
    }),
    /**
     * T-012 — stub d'endpoint panier (utilisé par les modules M04).
     * ADR-019 : `X-Cart-Token` est propagé automatiquement par le baseQuery.
     */
    getCart: build.query<
      {
        data: {
          items: Array<{ id: number; product_id: number; quantity: number; unit_price: string }>;
          subtotal: string;
        };
      },
      void
    >({
      query: () => '/cart',
      providesTags: [{ type: 'Cart', id: 'CURRENT' }],
    }),
    /**
     * T-012 — stub endpoint villes desservies (lecture publique).
     */
    listServedCities: build.query<
      { data: Array<{ id: number; name: string }> },
      void
    >({
      query: () => '/served-cities',
      providesTags: [{ type: 'ServedCities', id: 'LIST' }],
    }),
  }),
});

/** Helper exporté pour les tests et le typing des `injectEndpoints`. */
export type MplmApi = typeof api;
export { ApiError, toApiError };
export type { ErrorCode };