# Quickstart — Rejouer la validation du schéma T-002 et l'usage par T-005

**Portée** : ce guide explique comment rejouer la validation déjà exécutée du DDL de référence
(`contracts/schema-reference.mysql.sql`, résultats dans `data-model.md` §9), et comment la tâche T-005
(migrations Laravel) doit s'appuyer sur ces mêmes artefacts et scripts. Il ne contient aucune migration
exécutable ni code applicatif : seules les commandes de vérification de schéma, déjà utilisées par
l'architecte le 2026-10-14.

## Prérequis

- Une instance MySQL **≥ 8.0.16** (validée sur 8.4.6) **jetable**, joignable par socket Unix en `root`
  local sans mot de passe — jamais une base réelle : `validation/reset.sql` supprime la base `t002_schema`
  si elle existe.
- Dépendance Python : `pymysql` (`pip install pymysql`).
- Variable d'environnement `T002_MYSQL_SOCKET` pointant vers le socket de cette instance de test.

## Rejouer la validation du schéma de référence

```bash
cd specs/002-schema-donnees/validation
export T002_MYSQL_SOCKET=/chemin/vers/mysql.sock   # instance de test jetable uniquement

python run_sql.py reset.sql ../contracts/schema-reference.mysql.sql
python coverage.py
python probe_constraints.py
python probe_audit_grants.py
```

Résultats attendus (déjà obtenus le 2026-10-14, MySQL 8.4.6 — voir `data-model.md` §9) :

| Étape | Résultat attendu |
|---|---|
| `run_sql.py reset.sql schema-reference.mysql.sql` | 31 instructions, 0 erreur, 30 tables créées sur une base vide |
| `coverage.py` | 24/24 classes UML couvertes, 10/10 énumérations (même nombre de valeurs que l'UML), contraintes prix > 0 / stock ≥ 0 / note 1..5 présentes |
| `probe_constraints.py` | 23/23 violations attendues refusées (prix ≤ 0, stock négatif, note hors 1..5, doublon d'avis, doublon de sous-commande, virement sans coordonnées bancaires, remboursement en espèces, « livrée et payée » sans montant/date, échec/refus sans motif, statuts hors liste, états incomplets…) |
| `probe_audit_grants.py` | `INSERT` sur `audit_entries` accepté ; `UPDATE` et `DELETE` refusés (erreur MySQL 1142, ADR-015) |

Le détail de chaque vérification et son script associé est dans `validation/README.md`. Ces scripts
sont des outils de vérification du **schéma de référence**, pas des tests applicatifs Laravel.

## Usage par T-005 (migrations Laravel)

T-005 traduit `contracts/schema-reference.mysql.sql` en migrations Laravel 11 exécutables, sans en
changer le contenu métier :

1. **Ordre de création** : reprendre l'ordre des tables du DDL de référence (les clés étrangères ne
   pointent que vers des tables déjà créées) — voir `data-model.md` §10, point 1.
2. **Contraintes `CHECK`** : le constructeur de schéma Laravel n'expose pas, à notre connaissance, de
   méthode pour les `CHECK` — les ajouter par `DB::statement('ALTER TABLE … ADD CONSTRAINT …')` en
   conservant les noms `ck_<table>_<colonne>` du DDL de référence (à confirmer par T-005).
3. **Deux comptes MySQL** (ADR-015) : provisionner les variables d'environnement `DB_USERNAME`
   (application, droits `SELECT, INSERT` seulement sur `audit_entries`) et `DB_MIGRATION_USERNAME`
   (migrations) — aucune valeur réelle dans ce dépôt, seulement les noms de variables.
4. **Clé de chiffrement** (ADR-014) : `sellers.bank_details` et `product_returns.refund_details` sont
   chiffrées par l'application via la variable d'environnement `APP_KEY`, jamais en clair en base ni dans
   le dépôt.
5. **Données de référence** : `served_cities` = Tanger (V1) ; un compte administrateur initial dont les
   identifiants viennent de variables d'environnement, jamais codés en dur.
6. **Vérification attendue de T-005** : après application puis annulation des migrations sans erreur,
   rejouer `validation/coverage.py` et `validation/probe_constraints.py` (adaptés au besoin au schéma
   d'information de la base migrée) pour confirmer que la traduction en migrations n'a perdu aucune
   contrainte du DDL de référence.

## Ce que ce guide ne couvre pas

- Les migrations Laravel exécutables elles-mêmes (T-005).
- Les tests applicatifs PHPUnit/Pest par règle métier (RG-0xx, CA-F0xx) — dus par les tâches Backend
  concernées (Constitution Principe VI), pas par ce schéma.
- Toute valeur réelle de secret (mot de passe, clé) — seuls des noms de variables d'environnement sont
  cités (Constitution Principe VIII).
