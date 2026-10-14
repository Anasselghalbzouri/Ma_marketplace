# Implementation Plan: Schéma de données physique (T-002)

**Branch**: `002-schema-donnees` | **Date**: 2026-10-14 | **Spec**: `specs/002-schema-donnees/spec.md`

**Input**: Feature specification (`spec.md`) et les artefacts déjà produits par l'architecte pour cette
tâche : `data-model.md` (correspondance UML → tables, 23 écarts E-01..E-23, résultats de validation),
`contracts/schema-reference.mysql.sql` (DDL de référence, 30 tables, validé sur MySQL 8.4.6),
`validation/` (scripts et README de vérification), et `docs/architecture/DECISIONS.md` (ADR-010 à
ADR-015, statut « Proposé », créés pour T-002).

**Note** : ce plan ne refait ni ne réécrit `data-model.md`, `contracts/schema-reference.mysql.sql` ni
`validation/` — ils existent déjà, sont cités comme sorties de Phase 1, et restent la seule version de
référence. Ce document ajoute seulement `plan.md` (ce fichier), `research.md` (Phase 0) et
`quickstart.md` (Phase 1, guide de rejeu de la validation). Les migrations Laravel exécutables relèvent
de T-005, pas de cette tâche (Constitution Principe I — aucune implémentation anticipée ici).

## Summary

Le schéma de données physique de la marketplace (T-002) couvre les 24 classes métier de CLASS-01 et
CLASS-02 par 30 tables MySQL 8 (InnoDB, `utf8mb4_0900_ai_ci`), garantit en base les 9 énumérations
approuvées (`VARCHAR` + `CHECK`, ADR-012) et les invariants statiques d'une ligne (prix > 0, stock ≥ 0,
note 1..5, unicité avis/sous-commande, cohérence des transitions terminales), tout en laissant les règles
dynamiques et les transitions d'état aux services uniques désignés T-027/T-036/T-043 (ADR-013,
Constitution Principe III). L'argent reste exact (`DECIMAL(10,2)` MAD, ADR-011), traçable (journal
`audit_entries` en ajout seul garanti par les droits MySQL, ADR-015) et cloisonné (chiffrement
applicatif de `sellers.bank_details` et `product_returns.refund_details`, clé `APP_KEY`, ADR-014). Des
index dédiés couvrent le catalogue visible et la recherche (ENF-004) ainsi que les quatre traitements
planifiés (échéance vendeur T-034, retenue T-053, alerte 12 j T-050, reversement T-054). Le DDL de
référence a été validé sur une instance MySQL 8.4.6 jetable : 31 instructions sans erreur, couverture
24/24 classes et 10/10 énumérations, 23/23 violations refusées, journal d'audit refusant UPDATE/DELETE
(`data-model.md` §9). Vingt-trois écarts avec l'UML approuvé sont documentés un par un, avec
justification et destinataire (`data-model.md` §7). Trois points restent `[NEEDS CLARIFICATION]`
(e-mail client, informations vendeur, durée de conservation) et une hypothèse propre à T-002
(H-T02-1, exclusion du retour figée sur la ligne de commande) est assumée explicitement.

## Technical Context

**Language/Version** : DDL SQL (dialecte MySQL 8) comme artefact de référence ; aucun code applicatif
n'est produit par cette tâche. L'implémentation en migrations Laravel 11 (PHP 8.3) consommant ce DDL
relève de T-005.

**Primary Dependencies** : MySQL ≥ 8.0.16 (support des `CHECK`, ADR-002/ADR-012) ; InnoDB (clés
étrangères, transactions) ; `utf8mb4_0900_ai_ci`. Scripts de validation Python (`pymysql`) dans
`validation/`, outils de vérification du schéma, pas des migrations.

**Storage** : MySQL 8 — 30 tables (24 tables métier + 3 tables de liaison/composition +
`users`/`photo_files`/`audit_entries` du socle T-001), décrites dans `data-model.md` §2-§4 et le DDL
`contracts/schema-reference.mysql.sql`.

**Testing** : vérification du schéma (pas des tests applicatifs) via `validation/coverage.py` (couverture
classes/énumérations UML), `validation/probe_constraints.py` (23 violations attendues refusées),
`validation/probe_audit_grants.py` (droits `SELECT, INSERT` seuls sur `audit_entries`, ADR-015) sur une
instance MySQL ≥ 8.0.16 jetable. Les tests de migration (PHPUnit/Pest, cloisonnement, horloge simulée)
restent la responsabilité de T-005, qui rejoue `coverage.py` et `probe_constraints.py` sur la base
migrée (`data-model.md` §10).

**Target Platform** : Linux, conteneur MySQL 8 sous Docker Compose (image choisie par T-004) ; même socle
d'exécution que `specs/001-architecture-socle/plan.md`.

**Project Type** : artefact de schéma de données (contrat DDL) — pas une application exécutable ; aucune
arborescence `src/`/`tests/` applicative n'est produite par T-002.

**Performance Goals** : ENF-004 (catalogue affiché en moins de 3 s pour 95 % des consultations, index
`ix_products_visible`, `ix_products_category_visible`, `FULLTEXT ft_products_search`) ; traitements
planifiés sans dégradation perceptible à plusieurs milliers de commandes/produits (échéance vendeur
T-034, retenue T-053, alerte légale 12 j T-050, reversement hebdomadaire T-054) — index listés dans
`data-model.md` §6.

**Constraints** : conventions ADR-010 (anglais `snake_case`, pluriel, `id BIGINT UNSIGNED`) à ADR-015
(droits MySQL du journal d'audit) tenues pour acquises (statut « Proposé », non rediscutées ici) ;
aucun déclencheur SQL (ADR-013) ; aucune valeur de secret dans le dépôt, seulement des noms de variables
d'environnement (`APP_KEY`, `DB_USERNAME`, `DB_MIGRATION_USERNAME` — ADR-014, ADR-015).

**Scale/Scope** : 24 classes métier (13 CLASS-01, 11 CLASS-02) → 30 tables ; 9 énumérations UML + 4
énumérations implicites + 4 de socle ; 23 écarts UML documentés (E-01..E-23) ; 3 points
`[NEEDS CLARIFICATION]` au maximum (imposé par `spec.md`) ; 1 hypothèse propre à T-002 (H-T02-1).

## Constitution Check

*GATE : évalué avant Phase 0 (research) et réévalué après Phase 1 (design — déjà livrée, voir Note
ci-dessus).*

| Principe | Évaluation | Statut |
|---|---|---|
| I. Le métier d'abord | Aucune valeur métier inventée : les points non tranchés du cahier restent soit des paramètres du socle T-001 (H-08 : Q19, Q27, Q40, Q42, Q44, Q45), soit des `[NEEDS CLARIFICATION]` explicites (FR-028 à FR-030, maximum trois) ; les hypothèses de modélisation (H-T02-1, H-01, H-04 à H-06) sont déclarées, pas dissimulées. | PASS |
| II. Simplicité extensible | `VARCHAR` + `CHECK` plutôt qu'un moteur de workflow ou des tables de référence par énumération (ADR-012) ; pas de déclencheur SQL (ADR-013) ; chiffrement applicatif simple plutôt qu'un service de secrets dédié (ADR-014) — aucune complexité ajoutée sans besoin validé par le cahier. | PASS |
| III. Une seule porte par état métier | Les statuts `orders.status`, `sub_orders.status`, `seller_amounts.status`, `product_returns.status` ne sont contraints que par des `CHECK` de valeurs et d'états complets (§5) ; aucune transition n'est écrite en base — elle reste du ressort exclusif des services T-027/T-036/T-043 (ADR-013). | PASS |
| IV. Argent et traçabilité | `DECIMAL(10,2)` MAD sans arrondi binaire (ADR-011, validé CA-F011-5 : 500 − 80 = 420 exact) ; `audit_entries` en ajout seul garanti par les droits MySQL, pas seulement par le code (ADR-015, vérifié par `probe_audit_grants.py`). | PASS |
| V. Cloisonnement par rôle testé | `sellers.bank_details` et `product_returns.refund_details` chiffrés par l'application (ADR-014) ; le cloisonnement d'accès par rôle au niveau applicatif (middleware, autorisation) relève du socle T-001 (`contracts/authentification.md`), pas de ce schéma — ce schéma rend la donnée illisible même en cas de lecture directe non autorisée. | PASS |
| VI. Tests obligatoires | Validation réelle déjà exécutée sur MySQL 8.4.6 (`data-model.md` §9) : 24/24 classes, 10/10 énumérations, 23/23 violations refusées, droits d'audit vérifiés ; ce ne sont pas des tests applicatifs (PHPUnit/Pest), qui restent dus par T-005 sur les migrations. | PASS (vérification de schéma faite ; tests applicatifs dus par T-005) |
| VII. Mobile-first et performance | Hors périmètre direct (pas d'interface) ; contribue au budget ENF-004 par les index du catalogue (`ix_products_visible`, `FULLTEXT`). | PASS |
| VIII. Aucun secret dans le dépôt | Le DDL et les ADR ne citent que des noms de variables d'environnement (`APP_KEY`, `DB_USERNAME`, `DB_MIGRATION_USERNAME`), jamais de valeur réelle (ADR-014, ADR-015). | PASS |
| IX. Langue du code et de la documentation | DDL, noms de tables/colonnes/contraintes en anglais `snake_case` (ADR-010) ; `spec.md`, `data-model.md`, ce plan et `research.md` en français. | PASS |
| X. Validation juridique avant lancement | Ce schéma ne fige aucune durée de conservation (FR-030, `[NEEDS CLARIFICATION]`) ni aucun mécanisme de purge tant que la validation juridique (C-08) n'a pas eu lieu ; aucune donnée n'est supprimée automatiquement. | PASS |

Aucune violation ne nécessite d'entrée dans la table « Complexity Tracking ».

## Project Structure

### Documentation (this feature)

```text
specs/002-schema-donnees/
├── spec.md                              # Spécification (déjà livrée)
├── plan.md                              # Ce document
├── research.md                          # Phase 0 : arbitrages T-002, liés à ADR-010..015
├── data-model.md                        # Phase 1 (déjà livré) : correspondance UML -> tables, écarts E-01..E-23, validation §9
├── quickstart.md                        # Phase 1 : rejeu de la validation du schéma, usage par T-005
├── contracts/
│   └── schema-reference.mysql.sql       # Phase 1 (déjà livré) : DDL de référence, 30 tables
├── validation/                          # Phase 1 (déjà livré) : scripts de vérification + README
│   ├── README.md
│   ├── reset.sql
│   ├── run_sql.py
│   ├── coverage.py
│   ├── probe_constraints.py
│   └── probe_audit_grants.py
├── checklists/
└── tasks.md                             # Phase 2 (/speckit-tasks, non lancé par cette commande)
```

### Source Code (repository root)

**Structure Decision** : T-002 ne produit aucun code applicatif ni migration exécutable — son livrable
est un contrat DDL de référence (`contracts/schema-reference.mysql.sql`) et sa documentation
(`data-model.md`). La structure du socle applicatif (`backend/`, `database/migrations/`) a été fixée par
`specs/001-architecture-socle/plan.md` et n'est pas redéfinie ici ; T-005 y ajoutera les migrations
Laravel qui traduisent ce DDL, dans l'ordre de création documenté par `data-model.md` §10 (les FK ne
pointent que vers des tables déjà créées).

```text
specs/002-schema-donnees/contracts/schema-reference.mysql.sql   # Référence de schéma pour T-005 (pas une migration)

backend/database/migrations/        # Cible de T-005 : une migration par table, dans l'ordre du DDL de référence
```

## Complexity Tracking

*Aucune violation du Constitution Check ne nécessite de justification : cette table reste vide.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
