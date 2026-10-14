# Journal des décisions d'architecture (ADR) — marketplace-produits-locaux-maroc

**Tâche** : T-001 · **Auteur** : Keystone (Technical Architect) · **Date** : 2026-10-13
**Statut global** : toutes les décisions ci-dessous sont au statut **« Proposé »**. Seul @user (porteur du projet, Anass) peut les accepter, les modifier ou les remplacer. Le cahier des charges v1.1 reste la source de référence : une décision technique ne peut pas contredire une décision métier validée.

Contexte commun : **C-07 — le porteur du projet n'a imposé aucune contrainte technique.** Le cahier décrit QUOI et POURQUOI ; les choix ci-dessous sont donc des décisions d'architecte, révisables. Les arbitrages détaillés (options, raisons) sont dans `specs/001-architecture-socle/research.md` (R1–R6) ; le présent fichier en est le journal de décisions de référence.

---

## ADR-001 — Monolithe modulaire Laravel 11 / PHP 8.3

- **Statut** : Proposé · **Date** : 2026-10-13 · **Arbitrage** : `research.md` R1
- **Contexte** : le cahier §9 définit 11 modules fonctionnels (M01–M11) ; aucune contrainte de charge connue (ENF-006 MANQUANT, Q21) ; évolutions attendues (§21) sans refonte (ENF-010) ; constitution « simplicité extensible » (C-04).
- **Options** : (1) monolithe modulaire — un déploiement, frontières de modules explicites ; (2) microservices par module — transactions distribuées, exploitation lourde, non justifié sans volumes connus ; (3) application non structurée — rapide à démarrer, coûteuse à faire évoluer.
- **Décision** : option 1. Les modules M01–M11 sont des namespaces/contextes internes du même déployable, pas des services réseau séparés.
- **Conséquences** : transactions locales garanties (stock et argent) ; discipline de frontière assurée par la revue de code et les tests de cloisonnement (T-066), pas par isolation réseau ; extraction ultérieure d'un module possible si un besoin réel apparaît.

## ADR-002 — MySQL 8 (utf8mb4) comme moteur de base de données

- **Statut** : Proposé · **Date** : 2026-10-13 · **Arbitrage** : `research.md` R2
- **Contexte** : données relationnelles fortement contraintes (prix > 0, stock ≥ 0, note 1..5), transactions obligatoires pour l'argent, hébergement à coût maîtrisé.
- **Options** : MySQL 8 (répandu, bon marché, compétence établie) ; PostgreSQL (types/contraintes plus riches, sans besoin exprimé) ; moteur documentaire (inadapté aux contraintes d'intégrité et à la traçabilité financière).
- **Décision** : MySQL 8, moteur InnoDB, `utf8mb4` ; **transactions explicites** pour toute opération affectant un montant ou un stock.
- **Conséquences** : le schéma physique (T-002) porte les contraintes et les index nécessaires à ENF-004 ; la migration vers PostgreSQL reste possible mais coûteuse et serait une décision nouvelle tracée ici.

## ADR-003 — File d'attente et planificateur Laravel natifs pour les traitements différés

- **Statut** : Proposé · **Date** : 2026-10-13 · **Arbitrage** : `research.md` R3
- **Contexte** : quatre traitements temporels métier (expiration du délai de réponse vendeur, fin du délai de retour, alerte de délai légal, reversement hebdomadaire) ; les tâches T-034, T-050, T-053, T-054 exigent des tests à **horloge simulée** ; ENF-008 exige la traçabilité.
- **Options** : (1) planificateur + file natifs, point d'entrée unique ; (2) crons système dispersés (pas de registre, pas de test à horloge simulée, idempotence à réinventer) ; (3) orchestrateur externe (complexité disproportionnée pour quatre traitements sur un hôte unique).
- **Décision** : option 1. Chaque traitement est **idempotent**, **journalisé** (ENF-008) et protégé par un verrou d'exécution (une seule instance par échéance) ; le worker est un service Docker Compose distinct du serveur web.
- **Conséquences** : les tests n'utilisent jamais l'heure réelle ; les valeurs de délais viennent du module Paramètres (T-007), jamais du code.

## ADR-004 — Stockage des photos produits sur volume monté, avec abstraction compatible stockage objet

- **Statut** : Proposé · **Date** : 2026-10-13 · **Arbitrage** : `research.md` R4
- **Contexte** : ENF-011 (photos lisibles sur mobile), ENF-004 (performance), ENF-010 (évolutivité), volumes MANQUANT (Q21).
- **Options** : (1) volume de fichiers monté + variantes générées hors requête utilisateur ; (2) stockage objet compatible S3 dès la V1 (coût et dépendance externes, non justifiés avant connaissance des volumes) ; (3) stockage en base (dégrade base, sauvegardes et performance).
- **Décision** : option 1, derrière une abstraction de système de fichiers à pilote interchangeable : la bascule vers l'option 2 ne modifiera aucun module métier.
- **Conséquences** : convention de nommage sans collision ni déductibilité dès l'origine ; le volume entre dans la sauvegarde quotidienne et la restauration testée (T-069) ; la génération des variantes passe par la file d'attente (ADR-003) ; **HYPOTHÈSE** de bascule à confirmer selon la volumétrie réelle.

## ADR-005 — Hébergement par Docker Compose sur hôte(s) Linux (VPS), un seul hôte au lancement

- **Statut** : Proposé · **Date** : 2026-10-13 · **Arbitrage** : `research.md` R5
- **Contexte** : ENF-005 (99 % de disponibilité, HYPOTHÈSE), ENF-006 (volumes MANQUANT), budget MANQUANT (C-06, Q25).
- **Options** : (1) un VPS Linux en Docker Compose (application, base, serveur web, worker) ; (2) PaaS managé (coût récurrent, dépendance fournisseur) ; (3) plusieurs nœuds avec orchestrateur dès la V1 (sur-dimensionné).
- **Décision** : option 1 pour le lancement ; montée en charge par réplication des services application et worker.
- **Conséquences** : l'hôte unique est un point de défaillance, compensé par le redémarrage automatique, la sonde de disponibilité et les sauvegardes quotidiennes avec restauration testée ; sauvegardes, supervision et disponibilité sont opérées par l'équipe, non déléguées à un PaaS. Dimensionnement exact **[NEEDS CLARIFICATION: Q21, ENF-006 — volumes à 12 mois non fournis par le porteur]**.

## ADR-006 — Authentification par jeton porteur pour l'API `/api/v1`

- **Statut** : Proposé · **Date** : 2026-10-13 · **Arbitrage** : `research.md` R6
- **Contexte** : ENF-007 (cloisonnement par compte et par rôle), montée en charge par répliques (ADR-005), API REST consommée par le frontend React (ADR-007).
- **Options** : (1) jeton porteur émis à la connexion (téléphone + mot de passe), vérifié à chaque requête ; (2) session serveur avec cookie (magasin de session partagé requis entre répliques) ; (3) session longue par appareil (surface de risque excessive).
- **Décision** : option 1, jetons expirants, autorisation (rôle **et** propriété) vérifiée à chaque requête ; mots de passe hachés, jamais renvoyés.
- **Conséquences** : aucun état de session partagé entre répliques ; la révocation (déconnexion, changement de mot de passe) doit être prévue ; conventions détaillées dans `specs/001-architecture-socle/contracts/authentification.md`.

## ADR-007 — API REST JSON versionnée (`/api/v1`) plutôt que GraphQL

- **Statut** : Proposé · **Date** : 2026-10-13
- **Contexte** : un seul client connu (l'interface React) ; besoins de pagination, d'erreurs explicites et de tests fonctionnels par critère d'acceptation ; contrat d'API attendu par T-003.
- **Options** : REST JSON (lisible, cachable, outillage de test simple) ; GraphQL (filtrage de champs à protéger, complexité) ; rendu serveur sans API (couple fort, complique le mobile-first).
- **Décision** : REST JSON, préfixe `/api/v1`, conventions de socle dans `specs/001-architecture-socle/contracts/`. Les points d'accès métier sont du ressort de T-003.
- **Conséquences** : versionnage explicite ; une évolution incompatible passe par `/api/v2` sans casser la V1 (ENF-010) ; le cloisonnement est appliqué serveur, jamais seulement côté client.

## ADR-008 — Journal d'audit transverse non modifiable

- **Statut** : Proposé · **Date** : 2026-10-13
- **Contexte** : ENF-008 (traçabilité de l'argent et des saisies de statut, consultable par l'administrateur) ; U-03 — aucune classe d'historique dans CLASS-01/02 (HYPOTHÈSE).
- **Options** : journal en base en ajout seul alimenté par un service unique transverse ; journal dans les fichiers de log (non consultable par l'administrateur) ; aucune historisation (contraire à ENF-008).
- **Décision** : journal en base, ajout seul, écrit par un service unique appelé par les modules concernés (statuts de commande, livraison, montants, retours, remboursements). Ni modification ni suppression depuis l'interface d'administration.
- **Conséquences** : l'hypothèse U-03 (historisation transverse) est confirmée par la conception ; le modèle de ce journal appartient à T-002 et T-008 ; l'écart avec CLASS-01/02 est signalé à Blueprint par Compass.

## ADR-009 — Emplacement du projet et outillage d'architecture : `/opt/data/projects/marketplace-produits-locaux-maroc/` avec Spec Kit

- **Statut** : Proposé · **Date** : 2026-10-13
- **Contexte** : aucun dépôt n'existait (constat M-04) ; T-004 doit créer le dépôt et la CI ; la chaîne d'agents (note `UML → Plan`) situe les documents d'architecture dans `/opt/data/projects/<projet>/`.
- **Options** : cet emplacement (choisi) ; un autre répertoire sur l'hôte ; un dépôt distant à créer par T-004.
- **Décision** : racine du projet `/opt/data/projects/marketplace-produits-locaux-maroc/`, initialisée comme dépôt Git et outillée par Spec Kit (`.specify/`, `.claude/skills/`) ; documents d'architecture dans `docs/architecture/`, spécification du socle dans `specs/001-architecture-socle/`.
- **Conséquences** : T-004 et T-069 s'appuient sur cette racine ; si @user préfère un autre emplacement ou un dépôt distant, le contenu est déplaçable sans modification — seule cette décision change.

---

## Décisions de T-002 — Schéma de données physique (2026-10-14)

Référence : `specs/002-schema-donnees/data-model.md` (schéma, écarts UML) et `specs/002-schema-donnees/contracts/schema-reference.mysql.sql` (DDL de référence validé sur MySQL 8.4).

## ADR-010 — Conventions de nommage et de clés du schéma

- **Statut** : Proposé · **Date** : 2026-10-14 · **Tâche** : T-002
- **Contexte** : Constitution IX (code en anglais, documentation en français) ; Laravel 11 (ADR-001) attend des tables au pluriel et des clés `<singulier>_id` ; les diagrammes UML sont en français.
- **Options** : (1) noms anglais `snake_case`, tables au pluriel, clé `id BIGINT UNSIGNED` auto-incrémentée ; (2) noms français (contraire à la Constitution IX, accents interdits dans les identifiants) ; (3) clés UUID/ULID partout (index plus lourds, pas de besoin d'identifiant global en V1).
- **Décision** : option 1. Correspondance UML ↔ table tenue dans `data-model.md` §2. Les numéros visibles des utilisateurs passent par une colonne dédiée (`orders.reference`), jamais par l'`id`.
- **Conséquences** : la correspondance français ↔ anglais doit rester à jour ; `RETURN` étant un mot réservé SQL, la table de l'entité Retour est `product_returns`.

## ADR-011 — Montants en `DECIMAL(10,2)` (MAD)

- **Statut** : Proposé · **Date** : 2026-10-14 · **Tâche** : T-002
- **Contexte** : RG-007 (prix en MAD), RG-012/018/021/022 (calculs de montants vendeurs, déductions, remboursements), Constitution IV (argent exact et traçable).
- **Options** : (1) `DECIMAL(10,2)` ; (2) entier en centimes (exact, mais conversions partout et lecture humaine moins directe) ; (3) `FLOAT/DOUBLE` (arrondis binaires, interdit pour l'argent).
- **Décision** : option 1 ; plafond 99 999 999,99 MAD par valeur ; la devise n'est pas stockée en V1 (MAD unique, RG-007) — une colonne devise sera ajoutée avec la livraison internationale (§21).
- **Conséquences** : côté PHP, les montants sont manipulés en chaîne ou via une bibliothèque décimale, jamais en `float` ; les tests de calcul (CA-F011-5 : 500 − 80 = 420) comparent des valeurs exactes.

## ADR-012 — Énumérations UML en `VARCHAR` + contrainte `CHECK`

- **Statut** : Proposé · **Date** : 2026-10-14 · **Tâche** : T-002
- **Contexte** : 9 énumérations UML (CLASS-01/02) ; plusieurs sont HYPOTHÈSE (étapes §7, H-03) et peuvent évoluer ; MySQL 8.0.16+ applique les `CHECK`.
- **Options** : (1) `VARCHAR(32)` + `CHECK (col IN (…))` nommé, miroir d'une enum PHP « backed » ; (2) type `ENUM` MySQL (ajout de valeur = `ALTER` réécrivant la colonne, ordre implicite piégeux) ; (3) table de référence par énumération (jointures inutiles pour des listes fermées).
- **Décision** : option 1 ; valeurs en anglais `snake_case` ; correspondance des valeurs dans `data-model.md` §4.
- **Conséquences** : ajouter une valeur = migration qui remplace la contrainte (rapide, sans réécriture des données) ; la base refuse toute valeur hors liste (vérifié par essai).

## ADR-013 — Partage des règles entre base et services

- **Statut** : Proposé · **Date** : 2026-10-14 · **Tâche** : T-002
- **Contexte** : Constitution III (une seule porte par état métier) ; certaines règles sont statiques (prix > 0), d'autres dépendent du temps ou d'autres lignes (RG-006, RG-019, RG-024, quantité ≤ stock).
- **Options** : (1) la base garantit les invariants statiques d'une ligne (CHECK, UNIQUE, FK), les services garantissent les règles dynamiques et les transitions d'état ; (2) tout en déclencheurs SQL (logique cachée, difficile à tester à horloge simulée) ; (3) tout dans les services (une écriture directe peut corrompre l'argent).
- **Décision** : option 1. Aucun déclencheur SQL en V1. Les transitions d'état restent dans les services uniques (T-027, T-036, T-043) ; la base refuse les états incomplets (ex. « livrée et payée » sans montant ni date).
- **Conséquences** : la liste « garanti par la base / garanti par le service » de `data-model.md` §5 sert de base aux tests de T-005 et des tâches Backend.

## ADR-014 — Chiffrement applicatif des données bancaires et de remboursement

- **Statut** : Proposé · **Date** : 2026-10-14 · **Tâche** : T-002
- **Contexte** : FR-055 et §19 (coordonnées bancaires vendeurs, coordonnées de remboursement clients visibles du seul administrateur et du titulaire) ; loi 09-08 ; sauvegardes quotidiennes (T-069).
- **Options** : (1) chiffrement applicatif de la colonne (cast chiffré Laravel, clé `APP_KEY` en variable d'environnement) ; (2) chiffrement du disque seul (ne protège ni les sauvegardes logiques ni les requêtes) ; (3) aucun chiffrement (contraire à la minimisation).
- **Décision** : option 1 pour `sellers.bank_details` et `product_returns.refund_details` (type `TEXT`). La clé n'est jamais dans le dépôt.
- **Conséquences** : ces colonnes ne sont ni indexables ni recherchables ; une rotation de `APP_KEY` impose un rechiffrement planifié (à prévoir par T-069) ; perte de la clé = perte de ces données.

## ADR-015 — Journal d'audit en ajout seul garanti par les droits MySQL

- **Statut** : Proposé · **Date** : 2026-10-14 · **Tâche** : T-002 (précise ADR-008)
- **Contexte** : ADR-008 (journal non modifiable), ENF-008 ; T-002 rend le journal physique (`audit_entries`).
- **Options** : (1) l'utilisateur MySQL de l'application n'a que `SELECT, INSERT` sur `audit_entries` ; les migrations utilisent un autre utilisateur ; (2) déclencheurs `BEFORE UPDATE/DELETE` qui lèvent une erreur ; (3) contrôle applicatif seul.
- **Décision** : option 1. Une correction est une nouvelle ligne `action_type = correction` qui référence l'entrée corrigée (contrainte `CHECK`).
- **Conséquences** : deux comptes MySQL (application et migration), noms en variables d'environnement (`DB_USERNAME`, `DB_MIGRATION_USERNAME`) — à mettre en place par T-004/T-005 ; le test de T-008 vérifie qu'un `UPDATE` est refusé.

---

## ADR-016 — Langue et forme du contrat d'API : clés et codes d'erreur en anglais, messages en français

- **Statut** : Proposé · **Date** : 2026-10-14 · **Tâche** : T-003
- **Contexte** : Constitution IX (contrats d'API en anglais, messages utilisateurs en français) ; les conventions de socle T-001 (`specs/001-architecture-socle/contracts/format-erreur.md`, `pagination.md`) donnaient des exemples en français (`acces_refuse`, `par_page`) ; le schéma T-002 est en anglais snake_case (ADR-010).
- **Options** : (1) clés JSON, paramètres et `error.code` en anglais snake_case, `error.message` en français ; (2) tout en français (contraire à la Constitution IX et au schéma) ; (3) mélange selon le module (incohérent pour le frontend).
- **Décision** : option 1. Catalogue fermé de 24 codes dans `specs/003-contrat-api/contracts/error-codes.md` (généré, chaque code lié à un seul statut HTTP). Pagination `page` / `per_page`. Les exemples francisés de T-001 sont remplacés : `acces_refuse` → `forbidden`, `ressource_introuvable` → `not_found`, `validation_echouee` → `validation_failed`, `fichier_refuse` → `file_rejected`, `par_page` → `per_page`. L'enveloppe `{error:{code,message,details}}` et `{data, meta}` de T-001 est conservée.
- **Conséquences** : les fichiers T-001 ne sont pas réécrits (statut Proposé, en attente de @user) ; ils renvoient de fait à T-003 pour les noms définitifs. Le frontend s'appuie sur `code`, jamais sur `message`.

## ADR-017 — Application de la matrice des permissions : 403 pour le rôle, 404 pour la propriété

- **Statut** : Proposé · **Date** : 2026-10-14 · **Tâche** : T-003 (précise ADR-006)
- **Contexte** : cahier §5 (matrice), ENF-007, Constitution V ; T-001 (`authentification.md`, `statuts-http.md`) laissait à T-003 le choix 403/404 pour une ressource d'un autre titulaire ; l'inscription vendeur est libre (D9), donc un vendeur peut sonder les identifiants des autres.
- **Options** : (1) rôle non autorisé → 403 `forbidden`, ressource d'un autre titulaire du même rôle → 404 `not_found` (n'indique pas l'existence) ; (2) 403 dans les deux cas (révèle l'existence des commandes, retours et montants d'un concurrent) ; (3) 404 dans les deux cas (masque une erreur de rôle utile au frontend).
- **Décision** : option 1. Chaque opération porte `x-roles`, `x-ownership` et `x-matrix-rows` ; `authorization-matrix.yaml` est la source machine de la matrice rôle × action (17 lignes §5 « MP-01..17 » + 5 capacités dérivées « MX-01..05 »). Les routes sont séparées par espace (`/seller/...`, `/admin/...`, public) pour que le contrôle de rôle se fasse par groupe de routes, la propriété par politique de modèle (FR-058).
- **Conséquences** : les tests de T-066 dérivent un cas autorisé et un cas interdit par ligne directement du YAML ; la société de livraison n'a aucun point d'accès (D38).

## ADR-018 — Montants en chaîne décimale dans le JSON

- **Statut** : Proposé · **Date** : 2026-10-14 · **Tâche** : T-003 (prolonge ADR-011)
- **Contexte** : ADR-011 (`DECIMAL(10,2)` MAD) ; JavaScript n'a pas de type décimal exact ; Constitution IV (montants exacts au dirham près).
- **Options** : (1) chaîne `"220.00"` (motif `^-?\d{1,8}\.\d{2}$`) ; (2) nombre JSON (arrondi binaire possible côté client) ; (3) entier en centimes (diverge du schéma et de l'affichage).
- **Décision** : option 1 pour toute valeur monétaire, en entrée comme en sortie ; devise implicite MAD.
- **Conséquences** : le frontend ne calcule jamais un montant qui fait foi ; il affiche ceux renvoyés par l'API (ex. `previewOrder`).

## ADR-019 — Panier visiteur identifié par un jeton opaque `X-Cart-Token`

- **Statut** : Proposé · **Date** : 2026-10-14 · **Tâche** : T-003 · **Dépend de** : HYPOTHÈSE H-01 (panier visiteur, §5)
- **Contexte** : §5 autorise le panier au visiteur (HYPOTHÈSE) ; CA-F001-3 rattache le panier au compte à la connexion ; ADR-006 exclut la session serveur ; T-002 stocke `carts.guest_token_hash` (SHA-256, jamais le jeton en clair).
- **Options** : (1) jeton opaque émis par l'API au premier ajout (en-tête de réponse), renvoyé par le client en en-tête `X-Cart-Token` ; (2) cookie de session (contraire à ADR-006) ; (3) panier local au navigateur seulement (stock non vérifié côté serveur, CA-F003-2).
- **Décision** : option 1 ; à la connexion ou à l'inscription, le panier visiteur est fusionné dans celui du client.
- **Conséquences** : si @user refuse H-01, les opérations panier passent au rôle client seul, sans autre changement de contrat.

## ADR-020 — Transitions d'état exposées en POST sur sous-ressource verbale

- **Statut** : Proposé · **Date** : 2026-10-14 · **Tâche** : T-003 (applique Constitution III et ADR-013)
- **Contexte** : STATE-001..004 ; une seule porte par état métier (services T-027, T-036, T-043) ; les saisies de l'administrateur sont historisées (ENF-008).
- **Options** : (1) `POST /…/{id}/accept`, `/cancel`, `/delivered-paid`, etc., une route par transition ; (2) `PATCH {status: …}` générique (laisse le client choisir n'importe quel état, validations dispersées) ; (3) RPC unique `/transitions`.
- **Décision** : option 1. Une transition impossible depuis l'état courant renvoie 409 `invalid_transition` avec `details.current_status`. Une transition non modélisée par l'UML est réservée au contrat avec `x-blocked-by` et renvoie 501 `feature_blocked` (U-01 `adminInspectReturn`, U-02 `adminCancelOrder`).
- **Conséquences** : chaque route correspond à une transition nommée d'un diagramme d'états ; le journal d'audit enregistre `from_status` / `to_status` par appel.
