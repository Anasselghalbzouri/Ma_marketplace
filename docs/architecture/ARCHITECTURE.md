# Dossier d'architecture — marketplace-produits-locaux-maroc

**Tâche** : T-001 « Dossier d'architecture » du plan `/opt/data/uml/marketplace-produits-locaux-maroc/plan/plan-marketplace-produits-locaux-maroc.md`
**Auteur** : Keystone (Technical Architect) · **Date** : 2026-10-13 · **Version** : 1
**Statut** : **Proposé — à valider par @user (Anass)**. Aucun élément de ce dossier n'est validé tant que @user ne l'a pas approuvé.
**Dépôt** : `/opt/data/projects/marketplace-produits-locaux-maroc/` (racine du projet ; dépôt Git initialisé, Spec Kit installé)

## 1. Sources et classement des informations

| Source | Statut | Usage dans ce dossier |
|---|---|---|
| `/opt/data/cahiers/marketplace-produits-locaux-maroc/cahier-des-charges-v1.1.md` | **CONFIRMÉ** — validé par Anass le 2026-10-12 (S11, D45) | Source de référence : périmètre, acteurs, matrice §5, modules §9, ENF §13, contraintes §18, sécurité §19 |
| `/opt/data/cahiers/marketplace-produits-locaux-maroc/decisions.md` (D1–D45) | CONFIRMÉ | Décisions du porteur |
| `/opt/data/uml/marketplace-produits-locaux-maroc/` (15 diagrammes) | CONFIRMÉ — approuvés 2026-10-12 | Modèle : CLASS-01/02, SEQ-001..003, STATE-001..004, ACTIVITY-001..003 |
| `/opt/data/uml/marketplace-produits-locaux-maroc/plan/plan-marketplace-produits-locaux-maroc.md` | **PROPOSITION** (non validé) | Découpage des tâches, vagues, coordination |
| Stack Laravel + React + MySQL + Docker (note `Ressources/Stack technique` du vault) | HYPOTHÈSE de travail, confirmée par l'usage de Laravel dans les autres projets de l'utilisateur | Retenue ici comme décision d'architecte (voir ADR-001 à ADR-006) |
| Volumes attendus à 12 mois (ENF-006, Q21) | **MANQUANT** | Dimensionnement non figé |
| Canal de notification externe (Q23) | **MANQUANT** | Hors socle, tâche T-010 bloquée |
| Durées de conservation des données (§19) | **MANQUANT** | `[NEEDS CLARIFICATION]` dans la spécification |
| Contrainte technique imposée par le porteur | **C-07 : aucune** | Toute décision technique de ce dossier est un ADR au statut « Proposé » |

Aucune information **CONTRADICTOIRE** n'a été trouvée : le cahier v1.1 ne contient plus de contradiction ouverte (§22 « Aucune contradiction ouverte ») et le rapport de traçabilité UML ne relève aucun écart bloquant. Le rapport de traçabilité porte une réserve « v1.1 Brouillon » devenue **OBSOLÈTE** depuis D45 (constat K-01 du plan).

## 2. Portée du dossier

T-001 livre l'architecture du **socle transverse** : stack, découpage en modules, hébergement, tâches planifiées, stockage des photos. **Hors portée** (tâches suivantes du plan) :

| Hors portée T-001 | Tâche |
|---|---|
| Schéma de données physique (tables, clés, index) | T-002 |
| Contrat d'API détaillé et matrice rôle × action | T-003 |
| Dépôt Git, environnement local, pipeline CI (mise en œuvre) | T-004 |
| Migrations et données de référence | T-005 |
| Écrans, parcours détaillés, traductions | tâches Frontend (Iris / T-012+) |
| Procédures d'exploitation détaillées (recette, production, sauvegardes, supervision) | T-069 |
| Valeurs métier non tranchées (§22 du cahier) | @user (T-070) |

## 3. Vue d'ensemble

Une **application unique (monolithe modulaire)** sert trois interfaces (client, vendeur, administrateur) et une **API REST**, sur une base MySQL, avec un **worker de traitements différés** et un **planificateur** pour les échéances métier (délais de réponse, fin de délai de retour, alerte de remboursement, reversement hebdomadaire).

```
                 ┌──────────────────────── navigateur mobile (360 px) ────────────────────────┐
                 │  Espace client        Espace vendeur        Back-office administrateur     │
                 └───────────────────────────────┬────────────────────────────────────────────┘
                                                 │ HTTPS · API REST /api/v1
                                    ┌────────────▼─────────────┐
                                    │  Application (Laravel)   │
                                    │  M01 … M11 (modules)     │
                                    │  Transverses : Sécurité, │
                                    │  Paramètres, Audit,      │
                                    │  Notifications, Socle    │
                                    └───┬───────────┬──────────┘
                                        │           │
                     ┌──────────────────▼──┐   ┌────▼─────────────────────┐
                     │ MySQL (transactions)│   │ Fichiers photos (volume) │
                     └─────────────────────┘   └──────────────────────────┘
                                        │
                        ┌───────────────▼────────────────┐
                        │ File d'attente + Planificateur │  → jobs : expiration vendeur,
                        │ (worker dédié)                 │    fin de délai de retour, alerte
                        └────────────────────────────────┘    15/12 j, reversement hebdo
```

Détail des exigences transverses : `specs/001-architecture-socle/spec.md`.
Détail technique (arbitrages, structure de dépôt, modèle de socle, conventions, mise en route) : `specs/001-architecture-socle/plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`.
Décisions techniques : `docs/architecture/DECISIONS.md`. Risques : `docs/architecture/RISKS.md`. Sécurité : `docs/architecture/SECURITY.md`.

## 4. Stack retenue (ADR-001 à ADR-006 — statut « Proposé »)

| Couche | Choix | Justification (résumé) |
|---|---|---|
| Application | **Laravel 11 (PHP 8.3)**, monolithe modulaire | Un seul déployable = simplicité V1 (C-04) ; écosystème complet (authentification, file d'attente, planificateur, migrations, tests) ; compétence et projets existants de l'utilisateur |
| Interface | **React 18 + Vite**, mobile-first 360 px | SPA légère et rapide ; cadre i18n prêt pour ENF-001 ; écosystème connu |
| API | **REST JSON `/api/v1`** | Contrat explicite et testable (T-003), pas de sur-ingénierie (pas de GraphQL en V1) |
| Base de données | **MySQL 8** (utf8mb4, InnoDB, transactions) | Transactions pour l'argent et le stock ; hébergement courant et peu coûteux |
| Traitements différés | **File d'attente + planificateur** (worker dédié) | Échéances métier fiables, idempotentes, testables à horloge simulée |
| Photos | **Volume de fichiers + variantes redimensionnées** ; option objet compatible S3 | ENF-011 ; migration vers un stockage objet sans changer le code métier (ENF-010) |
| Exécution | **Docker Compose** (app, serveur web, base, worker) en local, recette et production | Reproductibilité demandée par T-004/T-069 ; un seul hôte suffit au lancement |
| Tests | **PHPUnit/Pest** (backend), **Vitest + Playwright** (frontend) | Tests fonctionnels par critère d'acceptation du cahier §15 ; mesures mobile/performance à 360 px (T-067) |
| CI | Lint + tests + build à chaque commit | Vérification de T-004 |

**Contraintes confirmées respectées** : C-01 (aucun paiement en ligne), C-02 (société de livraison sans accès à la Plateforme — D38), C-03 (Tanger / communes voisines via référentiels), C-04 (simplicité extensible).
**Non décidé par le porteur** : C-07 : la stack ci-dessus est une décision d'architecte, révisable (ADR-001, statut « Proposé »).

## 5. Découpage en modules M01–M11

Les modules sont ceux du cahier §9. Ce sont des **contextes du même déploiement** (namespaces + frontières de code), pas des services indépendants. Chaque module possède ses données ; un module ne modifie pas les données d'un autre : il appelle son service. Les libellés suivent le cahier §9 ; lorsque le plan §3 emploie un autre libellé pour le même module, il est signalé dans la ligne.

| Module | Responsabilité | Données possédées | Dépend de | Tâches du plan |
|---|---|---|---|---|
| **M01 Comptes et accès** | Inscription, connexion, profils client et vendeur, rôles, récupération d'accès | Comptes, rôles, clients, vendeurs, boutiques, communes vendeurs | Socle sécurité, Paramètres | T-006, T-014, T-015, T-016, T-018, T-019 |
| **M02 Boutique et catalogue vendeur** | Boutique, produits, stock, photos produits | Produits, catégories (lecture), photos, stock | M01, Paramètres, Photos | T-020, T-021, T-022 |
| **M03 Découverte** | Catalogue public, recherche, catégories, fiche produit, notes affichées | (lecture : produits, avis, catégories) | M02, M08 | T-023, T-024, T-025 |
| **M04 Panier et commande** | Panier multi-vendeurs, passage de commande (paiement à la livraison), confirmation écrite, suivi et annulation par le client | Paniers, lignes de panier, commandes, sous-commandes (création), adresses, confirmation | M01, M02, M03, M05 (statuts), Paramètres, Notifications, Audit | T-026, T-027, T-028, T-029, T-030, T-031, T-032 |
| **M05 Commandes vendeur** | Réception et traitement des sous-commandes (accepter, refuser, prête) | Sous-commandes (champs vendeur) | M04, Paramètres, Notifications, Audit | T-033, T-034, T-035 |
| **M06 Livraison et encaissement** | Transmission à la société de livraison, saisie des statuts par l'administrateur, livraison et encaissement, échecs, remises de fonds | Statuts de commande (via service de statuts), encaissements, remises de fonds, écarts | M04, M07 (montants), Audit, Paramètres | T-036, T-037, T-038, T-039, T-040, T-041 |
| **M07 Reversements vendeurs** (libellé du cahier §9 ; « Montants et reversements » dans le plan §3) | Montants vendeurs (retenu, disponible, reversé, déduit), déductions, régularisations, reversements hebdomadaires | Montants vendeurs, reversements, déductions | M06, M11, Paramètres, Audit | T-048, T-053, T-054, T-055 |
| **M08 Avis** | Avis et notes des produits reçus, moyenne | Avis, notes | M04 (commande livrée), M02 | T-056, T-057 |
| **M09 Administration et modération** | Référentiels (catégories, villes, communes), modération (produits, vendeurs, avis), supervision | Catégories, villes desservies, communes vendeurs, drapeaux de modération | M01, M02, M08, socle Audit | T-017, T-058, T-059, T-060, T-061 |
| **M10 Notifications** | Notifications internes stockées et consultables ; abonnement aux événements ; interface d'envoi externe | Notifications | (écoute les autres modules) | T-009, T-010, T-062 |
| **M11 Retours** | Éligibilité, demande de retour, reprise, vérification vendeur, litige, remboursement | Retours, vérifications, litiges, remboursements | M04, M07, Paramètres, Notifications, Audit | T-042, T-043, T-044, T-045, T-046, T-047, T-049, T-050, T-051, T-052 |

**Composants transverses** (hors M01–M11, socle) : Sécurité et cloisonnement, Paramètres métier configurables, Journal d'audit, Planificateur de tâches, Stockage et service des photos, Observabilité (journaux, sonde de disponibilité, sauvegardes), Cadre i18n.
Détail et affectation exhaustive des 70 tâches : `specs/001-architecture-socle/plan.md`.

### 5.1 Une seule porte par état métier (obligatoire)

Trois machines à états sont critiques pour l'argent et les parcours. **Un seul service écrit chaque statut** ; tous les autres modules appellent ce service :

| État | Service unique (tâche) | Diagrammes |
|---|---|---|
| Commande / Sous-commande | service de transitions Commande/SousCommande (T-027) | STATE-001, STATE-002 |
| Montant vendeur | service Montants (T-036) | STATE-004 |
| Retour | service Retour (T-043) | STATE-003 |

Toute nouvelle transition (ex. annulation par l'administrateur, T-060) passe par une évolution de ce service, pas par une écriture directe ailleurs.

## 6. Stratégie des tâches planifiées

Un **planificateur unique** déclenche les traitements différés ; chaque traitement est **idempotent** (rejouable sans doubler un statut ou un montant), **journalisé** (ENF-008) et **testable avec une horloge simulée** (exigence explicite des tâches T-034, T-050, T-053, T-054 du plan).

| Traitement planifié | Déclencheur | Effet | Tâche du plan |
|---|---|---|---|
| Expiration du délai de réponse vendeur | Échéance = commande créée + `delai_reponse_vendeur` (paramètre, Q19 MANQUANT) | Sous-commande non traitée = refusée ⇒ commande annulée, stock restitué, client et autres vendeurs notifiés | T-034 (dépend de T-011) |
| Fin du délai de retour : Retenu → Disponible | Échéance = réception + `delai_retour` (7 j, D25) et aucun retour en cours sur la ligne | Montant vendeur devient disponible (aucune commission — RG-005) | T-053 |
| Alerte de délai légal de remboursement | Retour non remboursé depuis plus de `seuil_alerte_remboursement` (12 j, HYPOTHÈSE) | Signalement à l'administrateur, **sans** changement d'état | T-050 |
| Calcul / préparation du reversement hebdomadaire | Jour de reversement paramétré (RG-018) | Σ disponibles − Σ déductions ; solde négatif signalé (H-07) | T-054 |
| Rappels et notifications différées | Événements F014 | Notifications internes | T-062 |

**Règles d'exploitation** : verrou d'exécution (une seule instance par échéance), reprise après erreur, alerte en cas d'échec répété, aucun envoi externe en V1 (Q23 MANQUANT) — le canal externe reste un adaptateur branché plus tard (T-010).
**Valeurs** : aucune valeur métier n'est fixée dans le code ; toutes proviennent du module **Paramètres** (T-007), modifiables par l'administrateur **sans redéploiement** (H-08).

## 7. Stratégie de stockage et de service des photos produits (ENF-011)

1. **Téléversement** : réservé au vendeur propriétaire du produit ; contrôle du type MIME réel et de la taille maximale (valeur = paramètre) ; refus explicite sinon.
2. **Traitement** : génération de variantes redimensionnées (vignette catalogue + image fiche) pour un affichage lisible à 360 px (ENF-002, ENF-011) ; le redimensionnement est fait **hors requête utilisateur** (traitement différé) pour ne pas dégrader ENF-004.
3. **Nommage et stockage** : nom opéré par l'application (jamais le nom fourni par l'utilisateur), un fichier par variante ; stockage sur **volume monté** en V1.
4. **Service** : les fichiers sont servis par le serveur web ; les réponses de catalogue utilisent les variantes et non l'original.
5. **Sauvegarde** : le volume de fichiers fait partie de la sauvegarde quotidienne, au même titre que la base (voir §8), avec une restauration documentée (vérification de T-069).
6. **Évolution (ENF-010)** : le passage à un stockage objet compatible S3 ne change que le composant de stockage ; aucun module métier ne connaît le chemin physique des fichiers.
7. **Suppression** : une photo retirée n'est plus servie ; la purge physique suit les durées de conservation des données (§19 : **MANQUANT**, `[NEEDS CLARIFICATION]`).

## 8. Hébergement, déploiement et exploitation (ENF-005)

| Environnement | Contenu | Remarque |
|---|---|---|
| Local | Docker Compose : application, serveur web, MySQL, worker + planificateur | Reproductible ; livré comme base de T-004 |
| Recette | Même composition, données de test, réinitialisable | Sert aux recettes T-063..T-066 |
| Production | Même composition sur un hôte Linux unique (VPS), TLS, sauvegardes, sonde de disponibilité | Suffisant au lancement (volumes H-11 / Q21 MANQUANT) |

- **Déploiement** : reproductible depuis la CI (image immuable + `docker compose up`), migrations appliquées à la mise en service, retour arrière documenté.
- **Disponibilité (ENF-005, 99 % — HYPOTHÈSE à confirmer)** : redémarrage automatique des conteneurs, contrôle de santé applicatif, sonde externe de disponibilité (détecte l'indisponibilité et alerte), fenêtre de maintenance annoncée et exclue du calcul.
- **Sauvegardes** : sauvegarde quotidienne de la base **et** du volume de photos ; rétention paramétrée ; **restauration testée au moins une fois** (critère de vérification de T-069).
- **Journaux** : journaux applicatifs et journaux d'audit métier (ENF-008) séparés ; aucune donnée sensible (mot de passe, coordonnées bancaires) dans les journaux.
- **Scalabilité (ENF-010)** : montée en charge par réplication de l'application et worker séparé ; base répliquée en lecture si nécessaire ; aucune refonte des parcours.
- **Échéances** : ces éléments sont mis en œuvre par T-069 (Release) ; T-001 en fixe la cible et les contraintes.

## 9. Sécurité et données (ENF-007, §19, ENF-008)

- **Authentification** : identifiant = téléphone (RG-014), mot de passe haché ; mots de passe **jamais** renvoyés ni journalisés.
- **Autorisation** : rôle (Visiteur, Client, Vendeur, Administrateur) **et** propriété (un vendeur n'accède qu'à ses données). Chaque ligne de la matrice des permissions du cahier §5 est couverte par un test autorisé **et** un test interdit (T-066).
- **Société de livraison** : aucun accès à la Plateforme (D38) ; l'administrateur lui transmet uniquement les informations nécessaires (adresses, téléphone du client, montant à encaisser).
- **Cloisonnement** : le vendeur ne voit ni l'adresse ni le téléphone du client (ENF-007 ; application de la suggestion acceptée du cahier §19) ; coordonnées bancaires visibles seulement par l'administrateur et le titulaire.
- **Traçabilité (ENF-008)** : toute opération d'argent et toute saisie de statut de livraison crée une entrée d'audit (qui, quand, montant, motif), non modifiable et consultable par l'administrateur.
- **Secrets** : aucun secret dans le dépôt ; uniquement des variables d'environnement, documentées dans un `.env.example` sans valeur réelle.
- **Conformité** : loi 09-08 (données personnelles) et loi 31-08 (consommateur) ; durée de conservation **MANQUANTE** → `[NEEDS CLARIFICATION]` ; validation juridique obligatoire avant lancement (C-08), porte bloquante.
- **Détail** : `docs/architecture/SECURITY.md`.

## 10. Performance et mobile (ENF-002, ENF-004, ENF-011)

- **Mobile-first 360 px** : mise en page conçue d'abord à 360 px pour les trois profils (client, vendeur, administrateur) ; aucune action essentielle inaccessible sur cet écran.
- **Budget de performance (ENF-004, p95 < 3 s sur 4G pour 95 % des consultations — HYPOTHÈSE à confirmer)** : requêtes de catalogue paginées et indexées, images servies en variantes redimensionnées, mise en cache des listes de catalogue et des catégories, poids de page maîtrisé (JS et CSS), mesures reproductibles à 360 px sur 4G simulée (T-067).
- **Écarts avec les valeurs cibles** : ENF-003/004/005 et ENF-006 restent HYPOTHÈSE/MANQUANT (H-11) ; l'architecture permet de **mesurer** puis de **réviser** sans refonte.

## 11. Évolutivité (ENF-010)

| Évolution attendue (§21 du cahier) | Point d'extension prévu |
|---|---|
| Autres villes clients | Référentiel villes desservies (M09), paramètre de zone — aucune règle de distance codée |
| Vendeurs d'autres communes / tout le Maroc | Référentiel communes vendeurs (M01/M09) |
| Paiement en ligne | Le mode de paiement est un champ de commande + un adaptateur ; le socle ne présuppose que « paiement à la livraison » (C-01) sans le figer dans le modèle |
| Commission / abonnement vendeur | Paramètre de calcul (M07) + journal d'audit ; aujourd'hui explicitement « aucune commission » (RG-005) |
| Accès direct de la société de livraison | Rôle supplémentaire et périmètre de saisie réduit (M06), sans changement des machines à états |
| Livraison internationale | Référentiel de zones + paramètres de frais ; devise paramétrée (aujourd'hui MAD, RG-007) |
| Autres modes de livraison | Le mode est porté par la commande ; l'adaptateur « société de livraison » est isolé dans M06 |

## 12. Réponse exigence par exigence (critère de vérification de T-001)

| Exigence | Réponse | Où |
|---|---|---|
| **ENF-002** (mobile 360 px, 3 profils) | Mise en page mobile-first 360 px pour client, vendeur et administrateur ; vérification par test de navigateur à 360 px (T-067) | §10, `specs/…/spec.md` (FR mobile), `docs/architecture/SECURITY.md` n/a |
| **ENF-004** (p95 < 3 s catalogue/fiche sur 4G) | Pagination + indexation, images en variantes redimensionnées, cache des listes, budget de page ; mesure reproductible (T-067) ; valeur cible **HYPOTHÈSE** à confirmer | §10, `specs/…/plan.md` (performance) |
| **ENF-005** (99 % de disponibilité) | Docker Compose redémarrage automatique, contrôle de santé, sonde externe, fenêtre de maintenance annoncée, sauvegardes quotidiennes base + photos, restauration testée | §8, T-069 |
| **ENF-006** (volumes à 12 mois) | **MANQUANT (Q21)** : aucun dimensionnement figé ; socle paramétrable et montée en charge par réplication | §8, §10, `[NEEDS CLARIFICATION]` dans `specs/…/spec.md` |
| **ENF-007** (cloisonnement, mots de passe) | Rôles + autorisation par propriété, couverture de la matrice §5 par tests autorisés/interdits (T-066), aucun accès société de livraison, mots de passe hachés jamais renvoyés | §9, `docs/architecture/SECURITY.md` |
| **ENF-010** (évolutivité sans refonte) | Monolithe modulaire + référentiels + paramètres + adaptateurs isolés ; liste des points d'extension | §5, §11 |
| **C-07** (aucune contrainte technique imposée) | Toute décision technique est un ADR « Proposé » (`ADR-001` à `ADR-009`), révisable par @user | `docs/architecture/DECISIONS.md` |

Exigences citées par d'autres tâches mais traitées hors de T-001 : ENF-001 (langues — Q11 MANQUANT), ENF-003 (test utilisateur vendeur — T-068), ENF-008/ENF-009/ENF-011/ENF-012 (touchées par le socle : audit, photos, alerte — voir §6, §7, §9).

## 13. Décisions attendues de @user

| # | Question | Défaut proposé (si pas de réponse) |
|---|---|---|
| 1 | Valider la stack retenue (Laravel 11 / React 18 / MySQL 8 / Docker) et le découpage M01–M11 | Valider tel quel (ADR-001 à ADR-009 au statut « Proposé ») |
| 2 | Volumes attendus à 12 mois (Q21, ENF-006) : vendeurs, produits, commandes/mois | Dimensionnement minimal d'un hôte unique, révisable |
| 3 | Durée de conservation des données personnelles (§19) et validation juridique (C-08) | `[NEEDS CLARIFICATION]` maintenu ; porte de lancement inchangée |
| 4 | Emplacement du dépôt de code (`/opt/data/projects/marketplace-produits-locaux-maroc/` retenu par défaut) | Conserver cet emplacement ; T-004 y initialise l'environnement et la CI |
| 5 | Canal de notification externe (Q23) | Reste hors socle : notifications internes seulement, adaptateur T-010 bloqué |

## 14. Livrables et suite

| Livrable | Chemin | Consommé par |
|---|---|---|
| Spécification du socle | `specs/001-architecture-socle/spec.md` | T-002, T-003, T-004 |
| Plan technique, arbitrages, modèle de socle, conventions, mise en route | `specs/001-architecture-socle/plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` | T-004 (dépôt, CI), T-069 (hébergement) |
| Constitution du projet | `.specify/memory/constitution.md` | toutes les tâches |
| Dossier d'architecture (ce document) + ADR + risques + sécurité | `docs/architecture/` | toutes les tâches |
| **T-002** Schéma de données physique : correspondance UML → tables, écarts E-01..E-23, DDL de référence MySQL, scripts de validation ; ADR-010 à ADR-015 | `specs/002-schema-donnees/data-model.md`, `contracts/schema-reference.mysql.sql`, `validation/` | T-003, T-005, tâches Backend |

**Réserves** : ce dossier est au statut **Proposé** ; les valeurs ENF-003/004/005 et les volumes (ENF-006) restent HYPOTHÈSE/MANQUANT ; les points ouverts du cahier §22 restent à trancher par @user (T-070) ; aucun élément de ce dossier ne remplace le cahier des charges v1.1, qui reste la source de référence.
