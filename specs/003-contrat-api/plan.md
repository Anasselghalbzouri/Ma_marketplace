# Implementation Plan: Contrat d'API et matrice d'autorisations (T-003)

**Branch**: `003-contrat-api` | **Date**: 2026-10-14 | **Spec**: `specs/003-contrat-api/spec.md`

**Input**: Feature specification (`spec.md`) et les artefacts déjà produits par l'architecte pour cette
tâche : `contracts/openapi.yaml` (OpenAPI 3.1, 101 opérations, 85 chemins, 93 schémas),
`contracts/authorization-matrix.yaml`/`.md` (matrice rôle × action, 17 lignes MP du cahier §5 + 5
capacités dérivées MX), `contracts/api-reference.md` (index par module M01–M11 + socle),
`contracts/error-codes.md` (catalogue de 24 codes), `tooling/build_contract.py` (générateur unique de
ces quatre fichiers), `validation/check_contract.py` (contrôles C1–C8, résultat dans
`.specify/logs/T-003-validation.log`) et `docs/architecture/DECISIONS.md` (ADR-016 à ADR-020, statut
« Proposé »).

**Note** : ce plan ne refait ni ne réécrit `contracts/openapi.yaml`, `contracts/authorization-matrix.yaml`/`.md`,
`contracts/api-reference.md`, `contracts/error-codes.md`, `tooling/build_contract.py` ni
`validation/check_contract.py` — ils existent déjà, sont cités comme sorties de Phase 1, et restent la
seule version de référence. Ce document ajoute seulement `plan.md` (ce fichier), `research.md` (Phase 0)
et `quickstart.md` (Phase 1, guide de régénération/vérification et d'usage par les tâches Backend,
Frontend et T-066). Le modèle de données exposé par ce contrat est celui déjà fixé par T-002
(`specs/002-schema-donnees/data-model.md`) ; aucun `data-model.md` n'est produit dans ce dossier. Les
migrations, contrôleurs, routes et tests exécutables qui implémentent ce contrat relèvent des tâches
Backend/Frontend et de T-066 (Constitution Principe I — aucune implémentation anticipée ici).

## Summary

Le contrat d'API de la V1 (T-003) expose en OpenAPI 3.1, sous `/api/v1` (ADR-007, jeton porteur ADR-006),
101 opérations couvrant les 23 cas d'utilisation approuvés (UC-001 à UC-023, 23/23) et les 17 lignes de
la matrice des permissions du cahier §5 plus 5 capacités dérivées non couvertes par celle-ci (MX-01 à
MX-05), pour les quatre rôles de la Plateforme — la société de livraison n'ayant par construction aucune
route (D38). Chaque opération porte ses rôles autorisés, sa vérification de propriété et ses lignes de
matrice (`x-roles`, `x-ownership`, `x-matrix-rows`), un refus de rôle rendant `403 forbidden` et une
ressource d'un autre titulaire `404 not_found`, sans la distinguer d'une ressource inexistante
(ADR-017). Les montants circulent en chaîne décimale MAD (ADR-018), les énumérations reprennent
exactement celles du schéma T-002, et les transitions d'état sont exposées en `POST` sur sous-ressource
verbale conforme à STATE-001..004, une transition interdite depuis l'état courant étant refusée par
`409 invalid_transition` (ADR-020). Deux actions que l'UML ne modélise pas encore (U-01 décision admin
après défaut de vérification vendeur, U-02 annulation de commande par l'administrateur) sont réservées
au contrat mais renvoient `501 feature_blocked` avec `x-blocked-by`. La vérification mécanique déjà
exécutée (`validation/check_contract.py`, `.specify/logs/T-003-validation.log`) confirme les huit
contrôles C1–C8 sans échec : OpenAPI 3.1 valide, 23/23 UC, 17/17 lignes MP et 5/5 MX couvertes pour
chaque rôle autorisé, aucune ouverture de rôle refusé, 468 exemples conformes à leur schéma, catalogue de
24 codes d'erreur à statut HTTP unique, énumérations identiques à T-002 (deux énumérations internes non
exposées, justifiées). Trois points restent `[NEEDS CLARIFICATION]`, portés jusqu'au point de contrôle
CP-1 (panier visiteur H-01, périmètre de la supervision administrateur F013/UC-023, levée d'une mesure de
modération), chacun déjà traduit en hypothèse par défaut dans `authorization-matrix.yaml` (statut
`allow_hyp`) sans être développé avant l'accord du porteur du projet.

## Technical Context

**Language/Version** : OpenAPI 3.1 (YAML) comme artefact de référence du contrat ; Python 3 pour les
outils de génération et de vérification (`tooling/build_contract.py`, `validation/check_contract.py`,
outils de documentation, pas du code applicatif). L'implémentation en routes/contrôleurs Laravel 11
(PHP 8.3) et en appels React 18 consommant ce contrat relève des tâches Backend/Frontend qui en
dépendent (voir `contracts/api-reference.md`, colonne « Tâche »).

**Primary Dependencies** : `PyYAML`, `openapi-spec-validator`, `jsonschema` (JSON Schema 2020-12),
invoqués via `uv run --no-project --with ...` sans dépendance applicative ajoutée par cette tâche.
Aucune bibliothèque HTTP/client n'est choisie ici : le contrat est indépendant de son implémentation.

**Storage** : aucune donnée persistée par cette tâche ; le contrat expose, sans en redéfinir la
structure, les ressources déjà fixées par T-002 (`specs/002-schema-donnees/data-model.md`,
`contracts/schema-reference.mysql.sql`) — notamment `carts.guest_token_hash` (ADR-019).

**Testing** : vérification du contrat (pas des tests applicatifs) via `validation/check_contract.py`
(C1–C8, déjà exécuté avec succès, `.specify/logs/T-003-validation.log`). Les tests de cloisonnement par
rôle (Constitution Principe V, VI) restent dus par T-066, qui dérive un cas autorisé et un cas interdit
par ligne directement depuis `contracts/authorization-matrix.yaml`, sans logique d'autorisation ad hoc
(User Story 4 de `spec.md`) ; les tests fonctionnels par tâche Backend restent dus par chacune d'elles.

**Target Platform** : API HTTP servie par le même socle d'exécution que `specs/001-architecture-socle/plan.md`
(Docker Compose, backend Laravel derrière `/api/v1`) ; aucune nouvelle plateforme introduite.

**Project Type** : artefact de contrat d'interface (OpenAPI 3.1 + matrice d'autorisation machine) — pas
une application exécutable ; aucune arborescence `src/`/`tests/` applicative n'est produite par T-003.

**Performance Goals** : aucun nouveau budget de performance ; le contrat porte le code d'erreur
transversal `rate_limited` (429) sur les opérations sensibles (catalogue, authentification) en
préparation du budget ENF-004 déjà fixé par T-002, sans le redéfinir ici.

**Constraints** : conventions ADR-016 (clés et codes en anglais snake_case, messages en français,
pagination `page`/`per_page`) à ADR-020 (transitions verbales) tenues pour acquises (statut « Proposé »,
non rediscutées ici) ; trois points `[NEEDS CLARIFICATION]` au maximum portés jusqu'à CP-1 (FR-016 à
FR-018) ; aucune valeur de secret dans le dépôt, seulement des noms de variables d'environnement (aucune
nouvelle variable n'est introduite par cette tâche au-delà de celles déjà citées par T-001/T-002).

**Scale/Scope** : 101 opérations, 85 chemins, 93 schémas ; 23/23 cas d'utilisation couverts ; 17/17
lignes de la matrice §5 (MP-01..17) + 5/5 capacités dérivées (MX-01..05) ; 24 codes d'erreur stables ;
468 exemples vérifiés contre leur schéma ; 2 actions réservées bloquées (U-01, U-02) ; 3 points
`[NEEDS CLARIFICATION]` au maximum (imposé par `spec.md`).

## Constitution Check

*GATE : évalué avant Phase 0 (research) et réévalué après Phase 1 (design — déjà livrée, voir Note
ci-dessus).*

| Principe | Évaluation | Statut |
|---|---|---|
| I. Le métier d'abord | Aucune valeur métier inventée : les trois points non tranchés du cahier/UML (panier visiteur H-01, périmètre de supervision F013, levée de modération) restent `[NEEDS CLARIFICATION]` explicites (FR-016 à FR-018, maximum trois) avec une hypothèse par défaut déjà tracée dans `authorization-matrix.yaml` (`allow_hyp`), jamais développée sans l'accord de @user ; les écarts UML U-01/U-02 sont réservés et signalés bloqués, pas masqués. | PASS |
| II. Simplicité extensible | REST JSON unique sous `/api/v1` (pas de GraphQL ni de RPC générique, ADR-007) ; transitions d'état en route verbale dédiée plutôt qu'un `PATCH` générique ou un endpoint `/transitions` (ADR-020, option 1 retenue) ; découpage des opérations par module M01–M11 + socle, identique à celui du cahier §9 et de T-001. | PASS |
| III. Une seule porte par état métier | Chaque route de transition (`accept`, `cancel`, `delivered-paid`, etc.) correspond à une transition nommée de STATE-001..004 et reste appliquée par le service propriétaire désigné (T-027, T-036, T-043, Constitution III) ; le contrat ne permet aucune écriture directe de statut par un champ générique ; une transition impossible est refusée par `409 invalid_transition`, distincte d'un refus de rôle ou de propriété (ADR-020, FR-014). | PASS |
| IV. Argent et traçabilité | Tout montant circule en chaîne décimale MAD, jamais en nombre flottant (ADR-018, FR-011) ; chaque mouvement financier (écart de caisse, remboursement, frais de retour, déduction, reversement) a son opération dédiée et historisée (M06, M07) ; aucun calcul de montant n'est laissé au client. | PASS |
| V. Cloisonnement par rôle testé | `x-roles`, `x-ownership` et `x-matrix-rows` sur chacune des 101 opérations ; refus de rôle = 403, ressource d'un autre titulaire = 404 sans révéler son existence (ADR-017, FR-006, FR-007) ; vérifié mécaniquement par `check_contract.py` C3/C4 (17/17 lignes MP, 5/5 MX, chaque rôle autorisé servi, 0 ouverture de rôle refusé) ; aucune route exposée à la société de livraison (D38, SC-003). | PASS |
| VI. Tests obligatoires | `check_contract.py` est un outil de vérification du contrat (cohérence interne, exemples conformes), pas un test applicatif ; les tests de cloisonnement par ligne de matrice et les tests fonctionnels par critère d'acceptation restent dus respectivement par T-066 et par chaque tâche Backend, qui s'appuient directement sur `authorization-matrix.yaml` sans logique ad hoc (User Story 4). | PASS (vérification de contrat faite ; tests applicatifs dus par T-066 et les tâches Backend) |
| VII. Mobile-first et performance | Pagination `page`/`per_page` et code `rate_limited` (429) sur les opérations de catalogue/authentification, compatibles avec le budget ENF-004 déjà fixé par T-002 ; aucune interface n'est produite par cette tâche. | PASS |
| VIII. Aucun secret dans le dépôt | Aucune valeur de secret dans les artefacts du contrat ; le jeton de panier visiteur (`X-Cart-Token`, ADR-019) est émis à l'exécution par l'API, haché en base (`carts.guest_token_hash`, T-002), jamais une valeur committée. | PASS |
| IX. Langue du code et de la documentation | Clés JSON, codes d'erreur et noms d'opérations en anglais snake_case (ADR-016, Constitution IX) ; messages d'erreur en français ; `spec.md`, ce plan, `research.md` et `quickstart.md` en français. | PASS |
| X. Validation juridique avant lancement | Le contrat expose le délai de retour de 7 jours et ses exclusions tels que déjà validés par le cahier (loi 31-08) sans les redéfinir ; aucune mise en production n'est anticipée par cette tâche, la porte C-08/ENF-009 reste entière. | PASS |

Aucune violation ne nécessite d'entrée dans la table « Complexity Tracking » ci-dessous.

## Project Structure

### Documentation (this feature)

```text
specs/003-contrat-api/
├── spec.md                              # Spécification (déjà livrée)
├── plan.md                              # Ce document
├── research.md                          # Phase 0 : arbitrages T-003, liés à ADR-016..020
├── quickstart.md                        # Phase 1 : régénération/vérification du contrat, usage Backend/Frontend/T-066
├── contracts/
│   ├── openapi.yaml                     # Phase 1 (déjà livré) : référence du contrat, 101 opérations
│   ├── authorization-matrix.yaml        # Phase 1 (déjà livré) : matrice rôle × action, source machine (T-066)
│   ├── authorization-matrix.md          # Phase 1 (déjà livré) : matrice lisible, miroir du YAML
│   ├── api-reference.md                 # Phase 1 (déjà livré) : index des points d'accès par module
│   └── error-codes.md                   # Phase 1 (déjà livré) : catalogue de 24 codes d'erreur
├── tooling/
│   └── build_contract.py                # Phase 1 (déjà livré) : générateur unique des quatre fichiers contracts/
├── validation/
│   └── check_contract.py                # Phase 1 (déjà livré) : contrôles C1–C8
├── checklists/
│   └── requirements.md                  # Déjà livré
└── tasks.md                             # Phase 2 (/speckit-tasks, non lancé par cette commande)
```

**Modèle de données** : celui de `specs/002-schema-donnees/data-model.md` (T-002) ; ce dossier n'en
produit pas de second exemplaire, conformément à l'instruction explicite de l'architecte pour cette
tâche.

### Source Code (repository root)

**Structure Decision** : T-003 ne produit aucun code applicatif — son livrable est un contrat d'interface
(`contracts/openapi.yaml` et `contracts/authorization-matrix.yaml`) et sa documentation. La structure
applicative (`backend/app/Http/Controllers/Api/V1/`, `backend/routes/api.php`,
`backend/app/Http/Middleware/`) a été fixée par `specs/001-architecture-socle/plan.md` et n'est pas
redéfinie ici ; les tâches Backend listées en dernière colonne de `contracts/api-reference.md`
implémentent chacune leurs routes contre ce contrat, et les tâches Frontend consomment les mêmes schémas
et exemples pour construire leurs appels, sans jamais inventer une autorisation ou un format non présent
dans `openapi.yaml`.

```text
backend/routes/api.php                          # Cible des tâches Backend : déclaration des routes /api/v1 décrites par openapi.yaml
backend/app/Http/Controllers/Api/V1/            # Cible des tâches Backend : un contrôleur par opération/module, x-plan-task dans openapi.yaml
backend/app/Http/Middleware/                    # Cible des tâches Backend : contrôle de rôle (x-roles) et de propriété (x-ownership)
frontend/src/services/                          # Cible des tâches Frontend : clients HTTP consommant openapi.yaml (schémas, exemples, error-codes.md)
```

## Complexity Tracking

*Aucune violation du Constitution Check ne nécessite de justification : cette table reste vide.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
