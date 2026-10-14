# Quickstart — Régénérer et vérifier le contrat T-003, usage par Backend/Frontend/T-066

**Portée** : ce guide explique comment régénérer et rejouer la vérification déjà exécutée du contrat
d'API (`contracts/openapi.yaml`, `contracts/authorization-matrix.yaml`/`.md`, `contracts/api-reference.md`,
`contracts/error-codes.md`, résultats dans `.specify/logs/T-003-validation.log`), et comment les tâches
Backend, Frontend et T-066 doivent s'appuyer sur ces mêmes artefacts. Il ne contient aucune route, aucun
contrôleur ni aucun test applicatif exécutable : seules les commandes de génération et de vérification du
contrat, déjà utilisées par l'architecte le 2026-10-14.

## Prérequis

- `uv` installé (exécute les scripts sans environnement Python préinstallé, via `--with`).
- Aucune base de données ni service externe requis : ces scripts ne lisent/écrivent que les fichiers de
  `specs/003-contrat-api/`.

## Régénérer les artefacts du contrat

`tooling/build_contract.py` est le générateur **unique** des quatre fichiers `contracts/*` : toute
modification du contrat passe par la table de définition de ce script (ou directement par
`openapi.yaml`, puis une vérification), jamais par une édition manuelle de `api-reference.md`,
`authorization-matrix.md` ou `authorization-matrix.yaml`, qui sont dérivés.

```bash
cd specs/003-contrat-api
uv run --no-project --with pyyaml python tooling/build_contract.py
```

Régénère, à partir de la même table source :

- `contracts/openapi.yaml`
- `contracts/authorization-matrix.yaml` (source machine, lue par T-066)
- `contracts/authorization-matrix.md` (miroir lisible)
- `contracts/api-reference.md` (index par module)

## Rejouer la vérification du contrat

```bash
# depuis la racine du dépôt
uv run --no-project --with pyyaml --with openapi-spec-validator --with jsonschema \
    python specs/003-contrat-api/validation/check_contract.py
```

Résultats attendus (déjà obtenus le 2026-10-14 — voir `.specify/logs/T-003-validation.log`) :

| Contrôle | Résultat attendu |
|---|---|
| C1 | `openapi.yaml` valide comme document OpenAPI 3.1 (101 opérations, 85 chemins, 93 schémas) |
| C2 | UC-001..UC-023 ont chacun ≥ 1 point d'accès (`x-uc`) — 23/23 |
| C3 | 17/17 lignes MP (cahier §5) et 5/5 capacités dérivées MX couvertes ; chaque rôle autorisé d'une ligne est servi par au moins une opération |
| C4 | 0 opération n'ouvre un rôle refusé par ses lignes de matrice |
| C5 | chaque opération a un exemple de requête, un exemple de succès (2xx) et un exemple d'erreur (4xx/5xx) |
| C6 | 468 exemples conformes à leur schéma JSON (2020-12) |
| C7 | chaque code d'erreur utilisé appartient au catalogue `error-codes.md` avec le bon statut HTTP |
| C8 | les énumérations `CHECK` de T-002 exposées par l'API ont des valeurs identiques (2 énumérations internes non exposées, justifiées — voir `research.md`, écart E-T03-01) |

Le détail de chaque contrôle est dans la docstring de `validation/check_contract.py`. Ce script est un
outil de vérification du **contrat de référence**, pas un test applicatif Laravel/PHPUnit.

## Usage par les tâches Backend

Chaque tâche Backend de `contracts/api-reference.md` (colonne « Tâche ») implémente ses routes contre ce
contrat, sans en changer le comportement :

1. **Routes et contrôleurs** : une route par opération, déclarée sous `/api/v1` (`backend/routes/api.php`),
   un contrôleur par opération ou petit groupe cohérent (`backend/app/Http/Controllers/Api/V1/`) — chemin,
   méthode, codes de succès/erreur et schémas de `openapi.yaml` ne sont pas renégociés à l'implémentation.
2. **Autorisation** : le middleware de rôle lit `x-roles` (groupes de routes public/`/seller`/`/admin`) ;
   la politique de modèle vérifie `x-ownership` à chaque requête, indépendamment du contrôle de rôle
   (ADR-017, `specs/001-architecture-socle/contracts/authentification.md`).
3. **Transitions d'état** : chaque route verbale (`/cancel`, `/accept`, `/delivered-paid`, …) appelle
   exclusivement le service propriétaire désigné (T-027 Commande/SousCommande, T-036 MontantVendeur,
   T-043 Retour, Constitution III) — jamais une écriture directe du champ de statut.
4. **Montants** : toute valeur monétaire en entrée est parsée depuis la chaîne décimale reçue (ADR-018),
   jamais convertie en `float` à un moment du calcul ; toute valeur en sortie est formatée en chaîne
   avant sérialisation.
5. **Panier visiteur (si H-01 confirmé au CP-1)** : le jeton `X-Cart-Token` est émis à la création du
   panier, haché (SHA-256) avant d'être comparé à `carts.guest_token_hash` (T-002) — jamais stocké en
   clair ni journalisé.
6. **Vérification attendue** : après implémentation d'un module, rejouer les exemples de requête/réponse
   de `openapi.yaml` pour ce module contre l'API réellement démarrée (`contracts/openapi.yaml`, champ
   `x-request-example`) avant de considérer la tâche terminée ; les tests par critère d'acceptation
   (CA-F0xx) et par règle métier (RG-0xx) restent dus par la tâche elle-même (Constitution VI).

## Usage par les tâches Frontend

Les tâches Frontend consomment `openapi.yaml` (schémas, exemples) et `error-codes.md` pour construire
leurs appels et leurs messages, sans jamais inventer un champ, un rôle ou un code d'erreur absent du
contrat :

1. **Client HTTP** (`frontend/src/services/`) : un appel par opération, typé depuis les schémas de
   `openapi.yaml` ; le jeton porteur (ADR-006) et, pour le panier visiteur (si H-01 confirmé), l'en-tête
   `X-Cart-Token` sont ajoutés par un intercepteur commun, jamais répétés appel par appel.
2. **Messages d'erreur** : affichés depuis `error.message` (déjà en français) ; la logique conditionnelle
   (ex. proposer une connexion, un autre délai, un autre montant) se base uniquement sur `error.code`
   (`error-codes.md`), jamais sur le texte de `message`, qui peut être reformulé sans préavis.
3. **Montants** : affichés tels que renvoyés par l'API (chaînes décimales, ADR-018) ; aucun recalcul de
   total côté frontend ne doit faire foi — seul celui renvoyé par `previewOrder`/`createOrder`.
4. **Transitions bloquées (U-01, U-02)** : une réponse `501 feature_blocked` (`x-blocked-by`) doit être
   distinguée dans l'interface d'un refus de rôle ou de propriété — par exemple une action grisée avec un
   message « fonctionnalité pas encore disponible », jamais un message de refus d'accès.

## Usage par T-066 (tests de cloisonnement par rôle)

T-066 dérive, pour chacune des 22 lignes de `contracts/authorization-matrix.yaml` (17 MP + 5 MX), un cas
autorisé et un cas interdit directement depuis ce fichier, sans écrire de logique d'autorisation ad hoc
point d'accès par point d'accès (Constitution V, User Story 4 de `spec.md`) :

1. Lire `authorization-matrix.yaml` : pour chaque ligne, la liste `operations`, les rôles marqués
   `allow`/`allow_own`/`allow_hyp`/`deny`, et le champ `note`.
2. Pour chaque rôle `allow`/`allow_own` : exécuter l'opération avec un compte de ce rôle et vérifier le
   succès (et, si `allow_own`, que seule la ressource du titulaire est accessible — vendeur A ne voit
   jamais une ressource du vendeur B, `403`/`404` selon ADR-017).
3. Pour chaque rôle `deny` : exécuter la même opération avec un compte de ce rôle et vérifier `403
   forbidden` (ou l'absence de route, pour la société de livraison, D38).
4. Pour les lignes `allow_hyp` (MP-03 panier visiteur, MX-04 supervision admin) : traiter le test comme
   conditionnel à la confirmation de @user au CP-1 — ne pas le considérer en échec si l'hypothèse est
   encore ouverte au moment où T-066 s'exécute, mais le signaler.

## Ce que ce guide ne couvre pas

- Les routes, contrôleurs et migrations Laravel exécutables eux-mêmes (tâches Backend listées dans
  `contracts/api-reference.md`).
- Les appels et composants React exécutables eux-mêmes (tâches Frontend).
- Les tests de cloisonnement par rôle exécutables eux-mêmes (T-066) et les tests applicatifs par critère
  d'acceptation (Constitution Principe VI) — dus par les tâches concernées, pas par ce contrat.
- Toute valeur réelle de secret (mot de passe, jeton, clé) — seuls des noms de variables d'environnement
  et des mécanismes de hachage/émission sont cités (Constitution Principe VIII).
- La décision de @user sur les trois points `[NEEDS CLARIFICATION]` (H-01, F013, levée de modération) —
  ce guide suppose les hypothèses par défaut documentées dans `research.md` tant que le CP-1 n'a pas eu
  lieu.
