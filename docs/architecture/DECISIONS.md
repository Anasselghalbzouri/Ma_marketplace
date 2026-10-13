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
