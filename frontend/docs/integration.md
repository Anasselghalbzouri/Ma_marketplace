# Intégration frontend ↔ backend

## État au 2026-10-14

| Composant | Statut | Source |
|---|---|---|
| Contrat d'API T-003 | ✅ livré, statut Proposé (CP-1) | `specs/003-contrat-api/contracts/openapi.yaml` |
| Backend Laravel T-004 | ✅ livré (coquille) | `backend/` dans le dépôt principal |
| Socle frontend T-012 | ✅ livré (ce dépôt) | `frontend/` |

## Branchement prévu

Le frontend (`frontend/`) et le backend Laravel (`backend/`) cohabitent dans
le même dépôt `04-dev` (`/opt/data/projects/marketplace-produits-locaux-maroc`).
Le frontend utilise Vite ; le backend utilise Laravel 11.

Trois modes de travail coexistent :

### 1. Mode mock (par défaut, sans backend démarré)

Le plus simple : on lance uniquement le mock de T-012.

```bash
cd frontend
node tools/mock-server.mjs &   # port 8080
npm run dev                    # port 5173 → proxy /api → 8080
```

Utile pour : itérer sur l'UI, vérifier le câblage RTK Query, démo client.

### 2. Mode backend réel (quand Anvil livre les modules M01–M11)

```bash
# Dans le dépôt principal :
docker compose up -d           # backend Laravel + nginx (étape 6 réactivée)
                              # backend écoute sur :8080
cd frontend && npm run dev      # Vite proxy /api → :8080
```

Utile pour : tests d'intégration bout-en-bout, validation contre le backend
réel avant publication.

### 3. Mode CI (étape 6)

Le pipeline CI démarre `npm run build` pour produire `frontend/dist/` et le sert
derrière nginx (même origin que l'API : `/api/v1/...` sur le même hôte).
Aucun proxy nécessaire en CI : le frontend et le backend partagent l'origine.

## Convention d'API respectée par le socle

- Préfixe unique : `/api/v1/...` (ADR-007, `versionnage.md`).
- Enveloppe de réponse : `{ data, meta? }` ou `{ error: { code, message, details? } }`
  (ADR-016, `format-erreur.md`).
- Pagination : `?page=&per_page=` + `meta: { page, per_page, total, total_pages }`
  (`pagination.md`).
- Authentification : `Authorization: Bearer <token>` (`authentification.md`).
- Codes d'erreur : 24 codes stables du catalogue (`error-codes.md`).
- Localisation : `Accept-Language: fr|ar` (ENF-001).
- Panier visiteur : `X-Cart-Token: <jeton opaque>` (ADR-019).

## Points de vigilance pour les tâches filles

| Tâche | Vérifier |
|---|---|
| T-014/T-016 (M01) | `setSession` doit être appelé sur `matchFulfilled` du endpoint login ; `forceUnauthenticated` sur 401. |
| T-021 (produits vendeur) | Réutiliser l'endpoint `listProducts` du socle via `injectEndpoints`. |
| T-028 (catalogue consommateur) | Étendre `listProducts` (filtres `q`, `category_id`). |
| T-035 (panier) | Utiliser `getCart` et propager `X-Cart-Token` au login si visiteur. |
| T-040+ | Suivre `ApiError.code` pour les分支ements d'UI (toast, modal, redirect). |

## Blocages actuels

1. **CP-1 non validé** : le contrat T-003 attend la validation d'Anass avant
   le démarrage des modules. Le socle frontend ne dépend pas des champs
   métier ; il est figé sur l'enveloppe et les codes.
2. **Modules M01–M11 non livrés** : le backend Laravel réel ne répond qu'à
   `/` ; tous les `/api/v1/*` renvoient 404. Le mock T-012 est donc la cible
   de test tant qu'Anvil ne livre pas T-006+.
3. **CI étape 6 en pause** : `docker compose` n'est pas exécutable dans
   l'environnement actuel (pas de daemon Docker). À réactiver étape 6.
4. **Q11 (langues)** non tranchée : T-013 ajoutera éventuellement d'autres
   locales. Le socle est prêt à les recevoir (ajouter une entrée dans
   `SUPPORTED_LANGUAGES` + un fichier `locales/<lng>/common.json`).