# Implementation Plan: Architecture du socle technique (T-001)

**Branch**: `001-architecture-socle` | **Date**: 2026-10-13 | **Spec**: `specs/001-architecture-socle/spec.md`

**Input**: Feature specification from `specs/001-architecture-socle/spec.md`, directives techniques de
l'architecte transmises pour cette tâche (C-07 : aucune contrainte imposée par le porteur).

**Note** : ce plan décrit uniquement le **socle transverse** (T-001). Le schéma physique des entités
métier relève de T-002, le contrat d'API métier détaillé de T-003, l'environnement local exécutable de
T-004. Aucun point d'accès métier, aucune migration exécutable, aucune tâche d'implémentation n'est
produite ici.

## Summary

Le socle technique de la marketplace est un monolithe modulaire Laravel 11 (PHP 8.3), découpé selon les
onze modules M01–M11 du cahier §9 (namespaces internes, pas de services séparés), servi à un frontend
React 18 + Vite mobile-first (360 px) via une API REST JSON versionnée `/api/v1`. La persistance repose
sur MySQL 8 (utf8mb4) avec transactions explicites pour toute opération d'argent ou de stock. Les
traitements différés (expiration de délai, libération de montants, alerte légale, reversement
hebdomadaire) sont pris en charge par la file d'attente et le planificateur natifs de Laravel, idempotents
et testables à horloge simulée. Les photos produits sont stockées sur un volume monté, avec variantes
mobiles, derrière une abstraction de système de fichiers permettant une bascule future vers un stockage
objet compatible S3 sans changement de code métier. L'exécution est assurée par Docker Compose
(application, base de données, serveur web, worker de file) sur un seul hôte Linux au lancement, avec
montée en charge par réplique. La sécurité repose sur l'authentification téléphone + mot de passe, une
autorisation à deux niveaux (rôle, propriété), un journal d'audit immuable pour toute opération
financière, et l'absence de tout secret dans le dépôt. Chaque arbitrage technique est tracé en ADR
« Proposé » dans `docs/architecture/DECISIONS.md` (détail et alternatives dans `research.md`), révisable
par le porteur du projet.

## Technical Context

**Language/Version**: PHP 8.3 (backend Laravel 11) ; JavaScript (ES2022+) pour le frontend React 18 —
le choix TypeScript éventuel n'est pas tranché par les directives reçues et reste à documenter en ADR
séparé si retenu plus tard, sans bloquer ce socle.

**Primary Dependencies**: Laravel 11 (framework backend, ORM Eloquent, file d'attente et planificateur
natifs, système de fichiers/Flysystem pour l'abstraction de stockage) ; React 18 + Vite (build frontend
statique) ; client HTTP du frontend consommant `/api/v1` (voir `contracts/`).

**Storage**: MySQL 8 (utf8mb4) pour les données relationnelles ; volume monté pour les photos produits,
avec abstraction de système de fichiers compatible stockage objet S3 en évolution (voir `research.md`
R4, ADR-004).

**Testing**: PHPUnit/Pest pour le backend (tests unitaires et fonctionnels, y compris horloge simulée
pour les traitements planifiés) ; Vitest pour les tests unitaires frontend ; Playwright pour les
parcours de bout en bout mobile-first (360 px).

**Target Platform**: Linux, conteneurs Docker Compose (application, base de données, serveur web, worker
de file) ; un seul hôte Linux suffisant au lancement (HYPOTHÈSE H-11 ; dimensionnement exact
**[NEEDS CLARIFICATION: Q21, ENF-006 — volumes à 12 mois non fournis par le porteur]**), montée en
charge par réplique des services application et worker.

**Project Type**: application web (frontend React servi en statique + backend API Laravel) — structure
« Option 2 : application web » du gabarit, adaptée au découpage modulaire interne du backend.

**Performance Goals**: ENF-004 — 95 % des consultations du catalogue et de la fiche produit affichées en
moins de 3 secondes sur une connexion 4G simulée ; valeur cible confirmée comme exigence mais mesure et
seuil exact restent HYPOTHÈSE H-11 à valider avant lancement (voir `spec.md` SC-002).

**Constraints**: mobile-first à 360 px de large sans défilement horizontal (ENF-002) ; disponibilité
mensuelle visée 99 % hors maintenance annoncée (ENF-005, HYPOTHÈSE H-11) ; chaque traitement planifié
idempotent et rejouable (FR-031, FR-032) ; aucun secret dans le dépôt (FR-056) ; aucune donnée
personnelle sensible en clair dans les journaux (FR-057) ; un mot de passe n'est jamais renvoyé par le
socle (FR-054).

**Scale/Scope**: onze modules métier (M01–M11, cahier §9) plus le socle transverse objet de ce document ;
70 tâches du plan rattachées sans ambiguïté à un module ou au socle (FR-013, SC-009) ; volumétrie
business à 12 mois **[NEEDS CLARIFICATION: Q21, ENF-006]** — dimensionnement de lancement modeste retenu
par défaut (zone Tanger et communes voisines, FR-070).

## Constitution Check

*GATE : évalué avant Phase 0 (research) et réévalué après Phase 1 (design).*

| Principe | Évaluation | Statut |
|---|---|---|
| I. Le métier d'abord | Aucune valeur métier n'est fixée par ce socle ; les questions ouvertes (Q19, Q21, Q24, Q27, Q38, Q40–Q45) restent portées par le service de paramètres configurables (FR-021) ou marquées `[NEEDS CLARIFICATION]`. | PASS |
| II. Simplicité extensible | Monolithe modulaire retenu (ADR-001) plutôt que microservices ; pas de complexité ajoutée sans besoin validé (voir `research.md` R1, R3, R5). | PASS |
| III. Une seule porte par état métier | FR-012/FR-014 imposent un service propriétaire unique par statut (Commande/SousCommande, MontantVendeur, Retour) ; ce plan fait de cette règle une frontière de module explicite (voir Project Structure). | PASS |
| IV. Argent et traçabilité | Transactions explicites MySQL pour toute opération d'argent/stock (ADR-002) ; journal d'audit immuable (FR-022, `data-model.md`). | PASS |
| V. Cloisonnement par rôle testé | Convention d'autorisation à deux niveaux (rôle + propriété) spécifiée dans `contracts/authentification.md` ; la structure de test (FR-058) est prévue dans `quickstart.md`. | PASS |
| VI. Tests obligatoires | PHPUnit/Pest + Vitest + Playwright intégrés au pipeline CI (`quickstart.md`) ; ce socle ne fixe pas les tests métier eux-mêmes (hors périmètre T-001). | PASS |
| VII. Mobile-first et performance | React 18 + Vite mobile-first 360 px, variantes photo mobiles (FR-041), budget de performance ENF-004 rappelé en contrainte. | PASS |
| VIII. Aucun secret dans le dépôt | `.env.example` uniquement, secrets par variable d'environnement par environnement (FR-003, FR-056) ; aucune valeur réelle produite par ce plan. | PASS |
| IX. Langue du code et de la documentation | Code et contrats en anglais (noms de champs ci-dessus en français car ce sont des documents de cadrage, pas du code — à traduire en anglais lors de l'implémentation T-002/T-003) ; documentation d'architecture en français. | PASS (à vérifier à l'implémentation) |
| X. Validation juridique avant lancement | Ce socle ne contourne pas la porte C-08/ENF-009 ; la durée de conservation des données reste `[NEEDS CLARIFICATION]` (FR-059), un mécanisme de purge paramétrable est prévu plutôt qu'une règle codée en dur. | PASS |

Aucune violation ne nécessite d'entrée dans la table « Complexity Tracking » ci-dessous.

## Project Structure

### Documentation (this feature)

```text
specs/001-architecture-socle/
├── plan.md              # Ce document
├── research.md           # Phase 0 : arbitrages (monolithe, MySQL, file+scheduler, stockage, hébergement)
├── data-model.md          # Phase 1 : entités de socle uniquement
├── quickstart.md          # Phase 1 : mise en route locale, tests, build
├── contracts/             # Phase 1 : conventions de socle (erreur, pagination, auth, versionnage, HTTP)
│   ├── format-erreur.md
│   ├── pagination.md
│   ├── authentification.md
│   ├── versionnage.md
│   └── statuts-http.md
└── tasks.md               # Phase 2 (/speckit-tasks, hors périmètre de /speckit-plan)
```

### Source Code (repository root)

**Structure Decision** : application web à deux répertoires de premier niveau (`backend/`, `frontend/`),
orchestrés par Docker Compose, avec le découpage modulaire interne du backend reflétant strictement les
modules M01–M11 et le socle transverse (Constitution Principe II ; FR-010, FR-013). Cette arborescence
cadre T-002 (schéma), T-003 (contrat API métier) et T-004 (environnement local) sans les anticiper.

```text
backend/                        # Monolithe modulaire Laravel 11 (PHP 8.3) — un seul déployable (FR-001)
├── app/
│   ├── Modules/
│   │   ├── M01Comptes/         # Comptes, rôles, sessions — service de comptes et d'accès (FR-020)
│   │   ├── M02Boutique/        # Boutique, Produit, stock, photos (propriétaire de FichierPhoto)
│   │   ├── M03Decouverte/      # Lecture seule des données M02 (FR-014 : dépend de M02)
│   │   ├── M04Panier/          # Panier, Commande (service de transition partagé avec M05, FR-012)
│   │   ├── M05CommandesVendeur/# SousCommande (statut porté par le service partagé de M04/M05)
│   │   ├── M06Livraison/       # Transmission, Collecte, RemiseDeFonds, Écart (dépend de M04, M05)
│   │   ├── M07Reversements/    # MontantVendeur, Déduction, Reversement (dépend de M06, M11)
│   │   ├── M08Avis/            # Avis, note (dépend de M06)
│   │   ├── M09Administration/  # Référentiels, suspension, masquage (dépend de M01, M02, M08)
│   │   ├── M10Notifications/   # Consomme les événements des autres modules, n'écrit jamais leurs données
│   │   ├── M11Retours/         # Retour, Vérification, Litige (dépend de M02, M04, M06)
│   │   └── Socle/              # Composants transverses de ce document (voir détail ci-dessous)
│   │       ├── Parametres/       # FR-021 — paramètres métier configurables
│   │       ├── JournalAudit/     # FR-022 — journal d'audit immuable
│   │       ├── NotificationsInternes/ # FR-023 — service interne, consommé par M10
│   │       ├── Planificateur/    # FR-024, FR-030..033 — registre des traitements planifiés
│   │       └── StockagePhotos/   # FR-040..044 — contrôle, variantes, abstraction de stockage
│   ├── Http/
│   │   ├── Controllers/Api/V1/ # Points d'accès REST sous /api/v1 (contenu métier : T-003)
│   │   ├── Middleware/         # Authentification par jeton, autorisation rôle/propriété (contracts/)
│   │   └── Requests/           # Validation d'entrée par module
│   ├── Console/                # Commandes artisan + planificateur (app/Console/Kernel)
│   ├── Jobs/                   # Jobs de file d'attente (traitements différés)
│   └── Providers/               # Enregistrement des services propriétaires par module (FR-012)
├── config/                     # Configuration par variable d'environnement (FR-003, FR-056)
├── database/
│   └── migrations/             # Migrations de socle uniquement à ce stade (T-002 : migrations métier)
├── routes/
│   └── api.php                 # Déclaration des routes sous /api/v1 (contenu métier : T-003)
├── storage/
│   └── app/photos/             # Volume monté (ADR-004) ; variantes originale/mobile
├── tests/
│   ├── Unit/                   # PHPUnit/Pest — par module, miroir de app/Modules
│   └── Feature/                # Tests fonctionnels, y compris cloisonnement (FR-058) et horloge simulée
└── docker/
    └── Dockerfile

frontend/                       # React 18 + Vite, mobile-first 360 px, build statique (FR-080, FR-081)
├── src/
│   ├── components/             # Composants partagés (gabarits communs aux trois profils)
│   ├── pages/                  # Écrans par profil (client, vendeur, administrateur)
│   ├── services/                # Client API versionné (/api/v1), gestion du jeton d'authentification
│   └── styles/                  # Base mobile-first (360 px minimum)
├── tests/
│   ├── unit/                    # Vitest
│   └── e2e/                     # Playwright (parcours 360 px, catalogue, fiche produit)
└── docker/
    └── Dockerfile               # Build de production du bundle statique

docker/
├── docker-compose.yml           # Services : app, db, web, worker (point 6 des directives)
├── docker-compose.override.yml  # Ajustements locaux (HYPOTHÈSE — détail hors périmètre de ce document)
└── web/                         # Configuration du serveur web (statique frontend + reverse-proxy /api/v1)

docs/
└── architecture/
    └── DECISIONS.md             # ADR « Proposé » (FR-007)

.env.example                     # Gabarit de variables d'environnement, aucune valeur réelle (FR-056)
```

### Frontières de modules et contrat de socle entre modules

- **Propriété exclusive des données** (FR-011) : chaque sous-répertoire `app/Modules/<Mxx>` possède
  exclusivement ses propres modèles Eloquent et migrations ; aucun autre module n'y accède par requête
  directe. Un module qui a besoin d'une donnée d'un autre module appelle le **service propriétaire**
  exposé par celui-ci (classe de service injectée via le conteneur de services Laravel), jamais une
  requête SQL ou un modèle Eloquent importé directement depuis un autre module.
- **Une seule porte par état métier** (FR-012, Constitution Principe III) : les statuts de
  Commande/SousCommande (service partagé entre M04 et M05), de MontantVendeur (porté par M07) et de
  Retour (porté par M11) ne sont modifiés que par leur service dédié ; les autres modules appellent ce
  service, ils n'écrivent jamais directement le champ de statut.
- **Graphe de dépendances autorisé** (FR-014, repris du plan §4) : M05 → M04 ; M06 → M04, M05 ; M07 →
  M06, M11 ; M11 → M02, M04, M06 ; M08 → M06 ; M09 → M01, M02, M08 ; M10 est appelé par tous les modules
  mais ne consomme que leurs événements, sans jamais écrire dans leurs données. Toute dépendance hors de
  ce graphe est un signal de revue de code à corriger avant fusion (Constitution — Gouvernance).
- **Composants transverses du socle** (`app/Modules/Socle/...`) : ne portent aucune règle métier
  (Constitution Principe I) ; ils exposent des services génériques consommés par tous les modules
  (paramètres, audit, notifications internes, planificateur, stockage photos), conformément à FR-013
  (toute tâche du plan non rattachable à un module M01–M11 est rattachée ici, jamais laissée sans
  propriétaire).
- **Contrat d'API** : chaque module expose ses points d'accès métier sous `Http/Controllers/Api/V1/`,
  en respectant les conventions transverses de `contracts/` (format d'erreur, pagination, authentification,
  versionnage, statuts HTTP). Le contenu métier de ces points d'accès (chemins, champs) relève de T-003,
  pas de ce document.

### Phases de livraison alignées sur les vagues du plan (§4)

Les vagues ci-dessous reprennent le regroupement de tâches du plan §3/§4 (table de rattachement module ↔
tâches de `spec.md`) et le graphe de dépendances FR-014 ; elles ne redéfinissent pas l'ordonnancement du
plan, qui reste la source de vérité en cas de divergence (Constitution Principe I).

| Vague | Contenu | Dépendances |
|---|---|---|
| **V1 — Socle + fondations** | T-001 à T-013 (ce document et les composants transverses), M01 Comptes et accès (T-014 à T-019) | Aucune dépendance de module (fondation) |
| **V2 — Catalogue vendeur** | M02 Boutique et catalogue vendeur (T-016, T-020 à T-022) | M01 |
| **V3 — Découverte et commande** | M03 Découverte (T-023 à T-025), M04 Panier et commande (T-026 à T-032), M05 Commandes vendeur (T-033 à T-035) | M01, M02 ; M05 → M04 |
| **V4 — Livraison, retours, avis** | M06 Livraison et encaissement (T-037 à T-041), M11 Retours (T-042 à T-052), M08 Avis et notes (T-056, T-057) | M06 → M04, M05 ; M11 → M02, M04, M06 ; M08 → M06 |
| **V5 — Reversements, administration, recette** | M07 Reversements vendeurs (T-036, T-048, T-053 à T-055), M09 Administration et modération (T-017, T-058 à T-061), M10 Notifications (T-009, T-010 bloquée, T-062), recette transverse (T-063 à T-068), clôture socle (T-069, T-070) | M07 → M06, M11 ; M09 → M01, M02, M08 ; M10 appelé par tous |

> Note : T-010 (adaptateur de notification externe) et T-040/T-046/T-060 (tâches bloquées selon le plan)
> restent au statut que seul le porteur du projet peut faire évoluer (Constitution — Gouvernance,
> « Statuts de tâches »). Ce plan ne modifie aucun statut de tâche.

## Complexity Tracking

*Aucune violation du Constitution Check ne nécessite de justification : cette table reste vide.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
