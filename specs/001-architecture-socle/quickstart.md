# Quickstart — Environnement local du socle (T-001 → T-004)

**Portée** : ce guide prépare la tâche **T-004** (environnement local reproductible). Il décrit la mise
en route, les commandes de test et de build attendues de la structure définie par `plan.md`. Il ne
contient ni code d'implémentation, ni migration exécutable, ni tâche métier : seulement les commandes de
socle que T-004 devra rendre fonctionnelles.

## Prérequis

- Docker et Docker Compose installés sur la machine locale.
- Un fichier `.env` local créé à partir de `.env.example` (FR-003, FR-056 — jamais de valeur réelle de
  secret commitée ; `.env.example` ne contient que des gabarits de variables, pas de valeur de
  production).
- Aucun outil PHP/Node n'est requis en dehors des conteneurs : l'environnement local reproductible
  (FR-002) s'appuie sur les services Docker Compose définis par `plan.md` (application, base de données,
  serveur web, worker de file).

## Démarrage de l'environnement local

```bash
cp .env.example .env
docker compose up -d
```

Résultat attendu : les quatre services (application, base de données, serveur web, worker de file)
démarrent ; le serveur web sert le build statique du frontend et expose l'API sous `/api/v1` (voir
`contracts/versionnage.md`).

## Préparation de la base (socle uniquement)

```bash
docker compose exec app php artisan migrate
```

Au stade de cette tâche (T-001), seules les migrations de **socle** existent (paramètres, journal
d'audit, notifications internes, tâches planifiées, fichiers/photos, comptes — voir `data-model.md`) ;
le schéma métier complet est livré par T-002, hors périmètre de ce document.

## Tests backend (PHPUnit/Pest)

```bash
docker compose exec app php artisan test
```

- Tests unitaires et fonctionnels, selon la convention « chaque tâche Backend inclut ses tests
  automatisés » (Constitution Principe VI).
- Les tests de traitements planifiés utilisent une horloge simulée (FR-032) plutôt que d'attendre un
  délai réel — condition requise par T-005, T-034, T-050, T-053, T-054.
- Les tests de cloisonnement (FR-058) couvrent, pour chaque ligne de la matrice de permissions du
  cahier §5, un cas d'accès autorisé et un cas d'accès interdit (SC-007).

## Tests frontend (Vitest + Playwright)

```bash
# Tests unitaires de composants
npm --prefix frontend run test

# Tests de bout en bout (parcours mobile-first, 360 px)
npx --prefix frontend playwright test
```

- Les scénarios Playwright couvrent au minimum les parcours à 360 px des User Stories 1 et 2 de
  `spec.md` (mobile-first, catalogue et fiche produit).

## Qualité et build

```bash
# Lint backend
docker compose exec app ./vendor/bin/pint --test
docker compose exec app ./vendor/bin/phpstan analyse

# Lint frontend
npm --prefix frontend run lint

# Build frontend statique (servi par le serveur web)
npm --prefix frontend run build
```

## Pipeline CI (référence)

Le pipeline CI exécute, dans cet ordre, les étapes ci-dessus (lint → tests → build) pour le backend et
le frontend, avant toute fusion vers la branche principale. Le détail du pipeline (nom de l'outil CI,
déclencheurs) relève de la configuration du dépôt, pas de ce document.

## Validation de ce socle (à rapprocher des critères de succès de `spec.md`)

| Vérification | Référence |
|---|---|
| `docker compose up -d` démarre les quatre services sans configuration manuelle additionnelle | FR-002 |
| `.env` local ne contient aucune valeur réelle de secret partagée hors de la machine locale | FR-003, FR-056 |
| Un traitement planifié rejoué deux fois sur la même période ne produit aucun doublon | FR-031, SC-005 |
| Un fichier photo non conforme est refusé avec un message explicite | FR-040, SC-006 |
| Un test d'accès interdit existe et échoue correctement pour au moins une ligne de la matrice de permissions | FR-058, SC-007 |

## Restauration d'une sauvegarde (recette, non destructif)

La procédure de restauration vérifiée avant tout lancement en production (FR-005, ENF-005) est exécutée
en environnement de **recette**, jamais directement en production lors de sa validation initiale. Le
détail opérationnel exact (fréquence, outil de sauvegarde, rétention) est une décision d'exploitation à
documenter en ADR (FR-007) et à vérifier lors de la tâche de recette dédiée (T-069), pas à ce stade de
quickstart.
