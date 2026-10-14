# Socle frontend (T-012)

Socle frontend **mobile-first** de la marketplace de produits locaux (V1, Tanger).
Ce dépôt livre le cadre applicatif (routage, client d'API, gestion de session,
mise en page 360 px, i18n) ; les écrans métier (catalogue, panier, commande,
…) sont ajoutés par les tâches filles du plan Compass (T-021, T-028, T-035…).

## Stack

| Domaine | Choix | Raison |
|---|---|---|
| Build | Vite 6 | Démarrage < 1 s, HMR stable, support natif ESM/TS. |
| UI | React 19 + TypeScript strict | Constitution IX, typage des contrats. |
| State | Redux Toolkit 2 + RTK Query | Cache invalidation par tag, baseQuery typé. |
| Routing | react-router-dom 7 (data router) | Routes imbriquées, future-proof. |
| Style | Tailwind v4 (PostCSS) | Utility-first, mobile-first par défaut. |
| i18n | i18next + react-i18next | `Accept-Language` propagé au backend (ENF-001). |
| Tests | Vitest + React Testing Library | jsdom, `user-event` réaliste. |

## Démarrage local

```bash
cd frontend
npm install
# (option A) avec le mock serveur conforme au contrat T-003 :
node tools/mock-server.mjs &
# (option B) avec le backend Laravel réel — voir docs/integration.md
npm run dev    # http://127.0.0.1:5173
```

Le proxy Vite redirige `/api/*` et `/photos/*` vers `http://127.0.0.1:8080`,
qui est le port du mock par défaut **et** le port Laravel défini par T-004.

## Critère exit de T-012

- ✅ Build production : `npm run build` produit `dist/` sans erreur.
- ✅ Tests unitaires : `npm test` (Vitest) couvre les composants du socle.
- ✅ Affichage correct à 360 px de large (ENF-002) : vérifié par inspection
  des classes Tailwind (`px-4`, `text-base`, `min-h-[44px]` sur les boutons).
- ✅ Cadre i18n opérationnel pour `fr` et `ar` (RTL automatique).
- ✅ Câblage RTK Query vérifié contre le mock conforme au contrat T-003.

## Architecture

```
src/
├── main.tsx              # Entrée — hydratation Redux + i18n, montage du router
├── router/index.tsx      # Routes socle (Home, Catalog placeholder, Login placeholder, 404)
├── components/
│   ├── AppShell.tsx      # Coquille : header + main + footer
│   ├── Header.tsx        # Navigation mobile-first (hamburger < 768 px)
│   ├── LanguageSwitcher.tsx
│   └── States.tsx        # LoadingState / ErrorState / EmptyState
├── pages/
│   ├── HomePage.tsx
│   ├── CatalogPage.tsx   # Câble RTK Query → /api/v1/products
│   ├── LoginPlaceholderPage.tsx  # Placeholder M01 (livré par T-014/T-016)
│   └── NotFoundPage.tsx
├── store/
│   ├── index.ts          # configureStore + setupListeners
│   ├── hooks.ts          # useAppDispatch, useAppSelector typés
│   └── slices/
│       ├── authSlice.ts  # Jeton + rôle, persistance localStorage
│       └── i18nSlice.ts  # Langue + RTL
├── api/
│   ├── api.ts            # createApi + baseQuery (injection Bearer, X-Cart-Token, Accept-Language)
│   └── errorEnvelope.ts  # ApiError normalisé sur les 24 codes du catalogue
├── i18n/
│   ├── index.ts          # initReactI18next, ressources fr/ar
│   └── locales/{fr,ar}/common.json
├── styles/index.css      # Tailwind v4 + thème mobile-first
└── tools/
    └── mock-server.mjs   # Mock conforme T-003 (voir ci-dessous)
```

## Mock serveur — pourquoi

Le backend Laravel livré par T-004 (Anvil) écoute sur :8080, mais ne couvre
que la coquille : les modules M01–M11 seront livrés par les tâches Backend
suivantes (T-006, T-014…T-046). En attendant, **toute requête vers `/api/v1/*`
depuis Vite renvoie `502 server_error`**.

Pour prouver que le câblage frontend est correct *sans dépendre du backend
réel*, le fichier `tools/mock-server.mjs` implémente cinq endpoints publics
du contrat T-003 (served-cities, categories, products, login, me) en respectant
strictement l'enveloppe d'erreur, le catalogue de codes, la pagination et les
ADR (snakecase anglais, montants en chaîne décimale). Le mock **n'implémente
aucune logique métier** : il existe pour les tests et la vérification locale.

| Endpoint mock | Contrat |
|---|---|
| `GET /api/v1/served-cities` | UC-007 + MX-02 (V1 = Tanger) |
| `GET /api/v1/categories` | UC-001 + MX-02 (référentiel public) |
| `GET /api/v1/products?demo=1` | UC-001 + MP-01 (catalogue paginé, 3 stubs) |
| `POST /api/v1/auth/login` | M01 (login demo : `+212600000001` / `demo`) |
| `GET /api/v1/me` | MP-04 (protégé par Bearer) |

## Tests

```bash
npm test         # Vitest — tests unitaires
npm run build    # TS + Vite build (vérifie aussi les types)
```

Couvre :
- `errorEnvelope` : 7 tests (codes, fallbacks, accesseurs dérivés).
- `authSlice` : 4 tests (setSession, logout, forceUnauthenticated, hydrate).
- `i18nSlice` : 3 tests (setLanguage, RTL auto, hydratation).
- `States` : 4 tests (accessibilité role/aria-live, libellés localisés).
- `LanguageSwitcher` : 2 tests (options, bascule RTL).
- `Header` : 4 tests (hamburger, login/logout conditionnel).

## Lien avec le reste du projet

- Contrat API : `../specs/003-contrat-api/contracts/openapi.yaml` (T-003).
- Schéma de données : `../specs/002-schema-donnees/` (T-002).
- Conventions de socle : `../specs/001-architecture-socle/contracts/` (T-001).
- ADR (architecture) : `../docs/architecture/DECISIONS.md`.

Pour brancher le frontend sur le backend réel, voir `docs/integration.md`.