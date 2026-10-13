# Feature Specification: Architecture du socle technique (T-001)

**Feature Branch**: `001-architecture-socle`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "Architecture du socle technique de la marketplace de produits locaux marocains (dossier d'architecture T-001) — tâche T-001 du plan `plan-marketplace-produits-locaux-maroc.md`, portée : le socle transverse sur lequel s'appuient les 70 tâches du plan, pas les fonctionnalités métier elles-mêmes."

## Contexte et portée

Cette spécification décrit **le socle transverse** requis par la tâche T-001 du plan d'implémentation
(`/opt/data/uml/marketplace-produits-locaux-maroc/plan/plan-marketplace-produits-locaux-maroc.md`, §3) :
l'infrastructure, le découpage en modules et les services communs sur lesquels s'appuient les 70 tâches
du plan. Elle ne décrit **pas** les fonctionnalités métier (F001–F022, déjà spécifiées au cahier des
charges) ni le code, le schéma de données ou les contrats d'API (livrables séparés des tâches T-002 et
T-003).

**Sources** (citées, non recopiées) :
- Cahier des charges v1.1 validé : `/opt/data/cahiers/marketplace-produits-locaux-maroc/cahier-des-charges-v1.1.md`
  — §5 (acteurs et matrice des permissions), §6 (périmètre), §9 (modules M01–M11), §13 (ENF-001..012),
  §16 (MVP), §17 (hors périmètre), §18 (contraintes C-01..C-08), §19 (sécurité et données), §22 (questions ouvertes).
- Décisions : `decisions.md` (D1–D45).
- UML approuvés : CLASS-01/02, SEQ-001..003, STATE-001..004, ACTIVITY-001..003.
- Plan : §2 (constats M-01..M-09, H-08, H-11), §3 (tâches T-001 à T-070), §4 (vagues et coordination sur
  fichiers partagés).
- Constitution du projet : `.specify/memory/constitution.md` (dix principes, notamment II. Simplicité
  extensible, III. Une seule porte par état métier, IV. Argent et traçabilité, V. Cloisonnement par rôle,
  VII. Mobile-first, VIII. Aucun secret dans le dépôt).

**Principe directeur (Constitution, Principe I ; C-07)** : aucune valeur métier n'est inventée ici. Les
points marqués MANQUANT ou HYPOTHÈSE dans le cahier restent soit des paramètres configurables (voir
Services transverses), soit des `[NEEDS CLARIFICATION]` explicites. Aucune contrainte technique n'ayant
été imposée par le porteur (C-07), toute décision technique nécessaire à ce socle est un **ADR au statut
« Proposé »** dans `docs/architecture/DECISIONS.md`, révisable par le porteur du projet.

## User Scenarios & Testing *(mandatory)*

Les « utilisateurs » de ce socle sont les trois profils finaux (client, vendeur, administrateur), dont
l'expérience dépend directement de ses garanties transverses (mobile-first, performance, cloisonnement,
fiabilité des traitements temporels), ainsi que les équipes d'ingénierie qui implémentent les tâches
T-002 à T-070 en s'appuyant sur lui.

### User Story 1 - Parcours mobile-first pour les trois profils (Priority: P1)

En tant que client, vendeur ou administrateur utilisant un smartphone d'entrée de gamme, je dois pouvoir
réaliser mon parcours principal sur un écran de 360 px de large, sans assistance desktop.

**Why this priority** : ENF-002 (cahier §13) est une exigence confirmée ; la zone de lancement (Tanger
et communes voisines) accède majoritairement à la plateforme depuis un smartphone (Constitution,
Principe VII). Sans ce socle, aucun écran des trois profils ne peut être livré de façon cohérente.

**Independent Test** : charger chaque écran principal des trois profils dans un viewport de 360 px et
vérifier l'absence de défilement horizontal et l'accessibilité de chaque action, indépendamment des
fonctionnalités métier elles-mêmes.

**Acceptance Scenarios**:

1. **Given** un client sur un écran de 360 px, **When** il consulte le catalogue puis une fiche produit,
   **Then** tous les éléments (photo, prix, note, bouton « ajouter au panier ») sont visibles et
   utilisables sans défilement horizontal.
2. **Given** un vendeur sur un écran de 360 px, **When** il remplit le formulaire de publication d'un
   produit, **Then** chaque champ est accessible sans bascule vers un affichage desktop.
3. **Given** un administrateur sur un écran de 360 px, **When** il saisit un statut de livraison,
   **Then** l'action est réalisable entièrement depuis cet écran.

---

### User Story 2 - Catalogue et fiche produit rapides sur mobile (Priority: P1)

En tant que visiteur ou client, je dois pouvoir consulter le catalogue et une fiche produit rapidement
sur une connexion mobile, pour ne pas abandonner ma visite avant de découvrir un vendeur.

**Why this priority** : ENF-004 (cahier §13) fixe un budget de 3 secondes pour 95 % des consultations sur
4G ; la découverte est le point d'entrée de tout le parcours (objectifs O1, O3 du cahier §4).

**Independent Test** : mesurer, sur un échantillon représentatif de consultations et une connexion 4G
simulée, le temps d'affichage du catalogue et d'une fiche produit, sans dépendre des autres parcours
métier.

**Acceptance Scenarios**:

1. **Given** une connexion 4G simulée, **When** un visiteur ouvre le catalogue, **Then** la page est
   affichée en moins de 3 secondes pour 95 % des mesures de l'échantillon.
2. **Given** un produit avec plusieurs photos, **When** sa fiche est ouverte sur mobile, **Then** les
   photos servies sont des versions adaptées au mobile qui ne dégradent pas ce budget.

---

### User Story 3 - Cloisonnement strict par rôle (Priority: P1)

En tant que vendeur, je dois être certain qu'aucun autre vendeur, ni la société de livraison, ne peut
voir ou modifier mes données ; en tant qu'administrateur, je dois être le seul à pouvoir saisir les
statuts de livraison.

**Why this priority** : ENF-007 (cahier §13) est une exigence confirmée pour la société de livraison
(D38) ; l'inscription vendeur étant libre et sans validation préalable (D9), le cloisonnement est la
seule garantie contre les accès croisés (Constitution, Principe V).

**Independent Test** : pour chaque ligne de la matrice des permissions (cahier §5), exécuter un test
d'accès autorisé et un test d'accès interdit, sans dépendre de l'implémentation d'une fonctionnalité
métier précise.

**Acceptance Scenarios**:

1. **Given** deux vendeurs A et B, **When** A tente de consulter une sous-commande ou un montant de B,
   **Then** l'accès est refusé.
2. **Given** un administrateur consultant un compte, **When** il affiche les informations du compte,
   **Then** le mot de passe n'apparaît jamais, sous aucune forme.
3. **Given** la société de livraison (acteur externe), **When** elle tente d'accéder à la plateforme,
   **Then** aucun point d'accès ne lui est exposé ; elle ne peut transmettre ses informations que par un
   moyen hors plateforme, saisi ensuite par l'administrateur (D38).

---

### User Story 4 - Traitements temporels fiables (Priority: P2)

En tant qu'administrateur et vendeur, je dois pouvoir compter sur l'exécution automatique et correcte des
échéances métier (délai de réponse vendeur, fin du délai de retour, alerte légale, reversement
hebdomadaire), même si personne ne déclenche l'action manuellement.

**Why this priority** : ces échéances portent des garanties financières et légales (RG-011b, RG-024,
ENF-012, RG-018) ; une exécution manquée ou dupliquée produirait un statut ou un montant faux.

**Independent Test** : pour chacun des quatre traitements planifiés, exécuter un test à horloge simulée
avant et après l'échéance, et vérifier qu'une double exécution ne produit pas de doublon — sans dépendre
du reste du parcours métier.

**Acceptance Scenarios**:

1. **Given** une sous-commande sans réponse du vendeur après le délai paramétré (Q19), **When** le
   planificateur s'exécute, **Then** elle est traitée comme refusée et la commande entière est annulée
   (RG-011b, D22).
2. **Given** une ligne de commande livrée sans retour en cours à la fin du délai de 7 jours, **When** le
   planificateur s'exécute, **Then** son montant passe de « Retenu » à « Disponible » (RG-024).
3. **Given** un retour non remboursé depuis plus de 12 jours, **When** le planificateur s'exécute,
   **Then** l'administrateur est alerté, sans changement de statut du retour (ENF-012, CA-F022-7).
4. **Given** un reversement hebdomadaire déjà calculé pour une semaine donnée, **When** le planificateur
   s'exécute une seconde fois par erreur sur la même période, **Then** aucun second reversement n'est
   créé (RG-018).

---

### User Story 5 - Photos produits lisibles sur mobile (Priority: P2)

En tant que vendeur, je dois pouvoir ajouter des photos de mes produits sans compétence technique, et en
tant que client, je dois voir des photos lisibles sur mon téléphone.

**Why this priority** : ENF-011 (cahier §13) ; la confiance du client envers un vendeur inconnu dépend de
la qualité perçue des photos (objectif O4 du cahier §4).

**Independent Test** : téléverser des fichiers valides et invalides et vérifier le contrôle, le
redimensionnement et l'affichage, indépendamment de la gestion du produit lui-même.

**Acceptance Scenarios**:

1. **Given** un vendeur qui téléverse une photo d'un format et d'une taille autorisés, **When** elle est
   enregistrée, **Then** une version adaptée à un écran mobile est servie sur la fiche produit.
2. **Given** un fichier qui n'est pas une image, ou qui dépasse la taille autorisée, **When** le vendeur
   le téléverse, **Then** il est refusé avec un message explicite.

---

### User Story 6 - Continuité de service (Priority: P3)

En tant qu'administrateur, je dois pouvoir constater et documenter toute interruption de service non
annoncée, et restaurer les données en cas d'incident.

**Why this priority** : ENF-005 ; la plateforme détient de l'argent pour le compte des vendeurs
(Constitution, Principe IV), ce qui rend la fiabilité de la restauration plus critique qu'un site vitrine.

**Independent Test** : simuler une indisponibilité et une restauration de sauvegarde en environnement de
recette, sans affecter la production.

**Acceptance Scenarios**:

1. **Given** une sauvegarde récente, **When** elle est restaurée en environnement de recette, **Then**
   les données et les statuts financiers restent cohérents entre eux.
2. **Given** une interruption non planifiée, **When** elle survient, **Then** elle est détectée et
   consignée, afin de la distinguer d'une maintenance annoncée.

---

### User Story 7 - Évolution sans refonte (Priority: P3)

En tant que porteur du projet, je dois pouvoir faire évoluer la plateforme (nouvelles villes, nouvelles
communes, paiement en ligne, commission, accès société de livraison, livraison internationale) sans que
l'équipe d'ingénierie ne doive réécrire les parcours V1.

**Why this priority** : ENF-010 est une exigence confirmée (D5, D24) ; c'est la raison d'être du
découpage modulaire (Constitution, Principe II).

**Independent Test** : ajouter une ville, une commune ou un mode de livraison fictif par configuration ou
extension additive, et vérifier qu'aucun module existant n'a dû être réécrit pour cela.

**Acceptance Scenarios**:

1. **Given** une nouvelle commune ajoutée par l'administrateur à son référentiel, **When** un vendeur de
   cette commune s'inscrit, **Then** l'inscription réussit sans nouveau déploiement de code (RG-023).
2. **Given** un mode de paiement en ligne ajouté comme extension du module Panier et commande, **When**
   un client passe une commande en paiement à la livraison, **Then** ce parcours existant continue de
   fonctionner sans modification.

---

### Edge Cases

- Que se passe-t-il si deux exécutions du planificateur se recouvrent (redémarrage, double déclenchement) ?
  → l'idempotence (FR-031) doit empêcher tout doublon de statut ou de montant.
- Que se passe-t-il si une photo dépasse la taille ou n'est pas une image ? → elle est refusée avec un
  message explicite (FR-040), sans bloquer la publication du reste du produit.
- Que se passe-t-il si les volumes réels dépassent largement l'hypothèse de dimensionnement de lancement
  (ENF-006 MANQUANT) ? → le dimensionnement doit rester révisable sans refonte architecturale (FR-070).
- Que se passe-t-il si un module tente d'écrire directement dans les données d'un module dont il n'est pas
  propriétaire ? → interdit par construction (FR-011/FR-012) ; à détecter en revue de code, conformément
  à la gouvernance de la constitution.
- Que se passe-t-il si la société de livraison tente un accès direct à la plateforme ? → aucun point
  d'accès ne lui est exposé en V1 (FR-053, D38).
- Que se passe-t-il pendant une fenêtre de maintenance annoncée ? → elle est exclue du calcul de
  disponibilité (ENF-005) mais doit être annoncée aux utilisateurs avant son déclenchement.
- Que se passe-t-il si un secret (mot de passe d'infrastructure, clé) est détecté dans un commit ? → la
  fusion est bloquée avant mise en production (FR-056, Constitution Principe VIII).
- Que se passe-t-il si une tâche du plan ne peut être rattachée à aucun module M01–M11 ? → elle est
  rattachée explicitement à la liste des composants transverses du socle (FR-013), jamais laissée sans
  propriétaire.

## Requirements *(mandatory)*

### Socle d'exécution et exploitation

- **FR-001**: Le socle DOIT être livré sous la forme d'un unique conteneur applicatif (monolithe
  modulaire) regroupant les modules M01–M11, conformément au Principe II de la constitution et à C-07
  (aucune contrainte technique imposée par le porteur).
- **FR-002**: Le socle DOIT fournir un environnement local reproductible, permettant à toute personne de
  l'équipe d'obtenir, à partir du dépôt, une instance fonctionnelle identique sans configuration manuelle
  additionnelle. [Plan T-004]
- **FR-003**: Le socle DOIT distinguer au moins trois environnements — local, recette, production — avec
  une configuration et des secrets propres à chacun. [Constitution Principe VIII ; Plan T-069]
- **FR-004**: Le socle DOIT produire des journaux d'exploitation (erreurs, accès, exécutions planifiées)
  consultables par l'équipe d'exploitation, sans exposer de donnée personnelle ou financière sensible en
  clair. [§19 ; ENF-008]
- **FR-005**: Le socle DOIT permettre une sauvegarde régulière des données, avec au moins une restauration
  vérifiée avant tout lancement en production. [Plan T-069 ; ENF-005, HYPOTHÈSE H-11]
- **FR-006**: Le socle DOIT permettre de détecter et de consigner une indisponibilité, afin de la
  distinguer d'une maintenance annoncée (ENF-005). [ENF-005, HYPOTHÈSE H-11]
- **FR-007**: Toute décision technique nécessaire à la mise en œuvre du socle (hébergement, bibliothèque
  de planification, format de stockage des photos, etc.) DOIT être consignée dans un ADR au statut
  « Proposé » dans `docs/architecture/DECISIONS.md` ; seul le porteur du projet peut le faire passer à un
  autre statut. [C-07 ; Constitution — Gouvernance]

### Découpage en modules (M01–M11)

- **FR-010**: Le socle DOIT découper les responsabilités métier selon les onze modules du cahier §9 : M01
  Comptes et accès, M02 Boutique et catalogue vendeur, M03 Découverte, M04 Panier et commande, M05
  Commandes vendeur, M06 Livraison et encaissement, M07 Reversements vendeurs, M08 Avis et notes, M09
  Administration et modération, M10 Notifications, M11 Retours. [§9 ; Constitution Principe II]
- **FR-011**: Chaque module DOIT posséder exclusivement ses propres données ; aucun module ne DOIT écrire
  directement dans les données d'un module dont il n'est pas propriétaire. [§9 ; Constitution Principe III]
- **FR-012**: Les statuts de Commande/SousCommande, de MontantVendeur et de Retour DOIVENT chacun être
  modifiés par un unique service propriétaire, partagé entre les modules qui les utilisent (Commande/
  SousCommande entre M04 et M05 ; MontantVendeur porté par M07 ; Retour porté par M11). Tout autre module
  appelle ce service sans écrire directement le statut. [Constitution Principe III ; Plan T-027, T-036,
  T-043]
- **FR-013**: Chaque tâche du plan §3 DOIT être rattachable à exactement un module M01–M11 ou à la liste
  des composants transverses du socle décrite dans ce document (voir table ci-dessous). [Plan §3/§4]
- **FR-014**: Les dépendances autorisées entre modules DOIVENT suivre le graphe de dépendances des tâches
  du plan §4 : M05 dépend de M04 ; M06 dépend de M04 et M05 ; M07 dépend de M06 et M11 ; M11 dépend de
  M02, M04 et M06 ; M08 dépend de M06 ; M09 dépend de M01, M02 et M08 ; M10 est appelé par tous les
  modules mais n'écrit jamais dans leurs données (il ne fait que consommer leurs événements). [Plan §4]

**Table de rattachement module ↔ tâches du plan** (données possédées et tâches associées, cahier §9 et
plan §3) :

| Module | Données possédées | Tâches du plan rattachées |
|---|---|---|
| M01 — Comptes et accès | Compte, rôle, session | T-006, T-014, T-015, T-016 (partagée avec M02), T-018, T-019 |
| M02 — Boutique et catalogue vendeur | Boutique, Produit, stock, photos | T-016 (partagée avec M01), T-020, T-021, T-022 |
| M03 — Découverte | Index de recherche/catalogue (lecture des données M02) | T-023, T-024, T-025 |
| M04 — Panier et commande | Panier, Commande | T-026, T-028, T-029, T-030, T-031, T-032 (+ service partagé T-027) |
| M05 — Commandes vendeur | SousCommande (statut porté par le service partagé T-027) | T-033, T-034, T-035 (+ service partagé T-027) |
| M06 — Livraison et encaissement | Transmission, Collecte, RemiseDeFonds, Écart | T-037, T-038, T-039, T-040 (bloquée), T-041 |
| M07 — Reversements vendeurs | MontantVendeur, Déduction, Reversement | T-036, T-048, T-053, T-054, T-055 |
| M08 — Avis et notes | Avis, note | T-056, T-057 |
| M09 — Administration et modération | Catégorie, VilleDesservie, CommuneVendeur, suspension, masquage | T-017, T-058, T-059, T-060 (bloquée), T-061 |
| M10 — Notifications | Notification interne, abonnement aux événements | T-009, T-010 (bloquée), T-062 |
| M11 — Retours | Retour, Vérification, Litige | T-042, T-043, T-044, T-045, T-046 (bloquée), T-047, T-049, T-050, T-051, T-052 |
| Socle transverse (objet de ce document) | Paramètres, journal d'audit, notifications internes, planificateur, stockage des photos, environnements | T-001, T-002, T-003, T-004, T-005, T-007, T-008, T-011, T-012, T-013, T-069, T-070 (+ recette transverse T-063 à T-068) |

> Note méthodologique : le plan regroupe certaines tâches par vague d'exécution plutôt que par propriété
> stricte du module (ex. T-017 « Référentiels administrateur » est exécuté tôt, dans la vague de M01, mais
> ses données — catégories, villes, communes — appartiennent à M09 selon le cahier §9). En cas de
> divergence entre le regroupement du plan §3 et le découpage du cahier §9, **le cahier §9 prime**
> (Constitution, Principe I).

### Services transverses

- **FR-020**: Le socle DOIT fournir un service de comptes et d'accès unique (M01), gérant
  l'authentification par téléphone et les trois rôles Client/Vendeur/Administrateur, consommé par tous
  les autres modules sans duplication de la logique d'authentification. [ENF-007 ; F001]
- **FR-021**: Le socle DOIT fournir un service de paramètres métier configurables, modifiables par
  l'administrateur sans nouveau déploiement, pour toute valeur marquée MANQUANT ou HYPOTHÈSE dans le
  cahier et non encore tranchée (notamment Q19, Q27, Q40, Q42, Q44, Q45, le délai légal de remboursement,
  le seuil d'alerte, le jour de reversement). Aucune valeur métier n'est fixée en dur ni inventée par le
  socle. [HYPOTHÈSE H-08 ; §22 ; Constitution Principe I]
- **FR-022**: Le socle DOIT fournir un journal d'audit transverse historisant, pour toute saisie de statut
  de livraison et tout mouvement financier (encaissement, remise de fonds, écart, retenue, mise à
  disposition, remboursement, frais imputé, décision de litige, régularisation, reversement), qui a agi,
  quand, quel montant et quel motif. Une entrée DOIT être immuable : seule une nouvelle entrée peut
  corriger ou régulariser une entrée précédente. [ENF-008 ; Constitution Principe IV ; Plan T-008]
- **FR-023**: Le socle DOIT fournir un service de notifications internes à l'application (M10), distinct
  de tout canal externe (SMS, e-mail, WhatsApp…). L'envoi externe reste une décision séparée, non
  bloquante pour ce service interne. [F014 ; Constitution — Contraintes ; Plan T-009/T-010]
- **FR-024**: Le socle DOIT fournir un planificateur de tâches temporelles, capable de déclencher des
  traitements différés de façon périodique et vérifiable par les équipes de test. [Plan T-011]

### Stratégie des tâches planifiées

- **FR-030**: Le planificateur DOIT exécuter au moins les quatre traitements suivants, chacun rattaché à
  son module propriétaire : (a) expiration du délai de réponse vendeur à une sous-commande [RG-011b ; M05 ;
  Plan T-034], (b) passage des montants vendeur de « Retenu » à « Disponible » à la fin du délai de retour
  [RG-024 ; M07 ; Plan T-053], (c) alerte de délai légal de remboursement approchant [ENF-012 ; M11 ; Plan
  T-050], (d) calcul et préparation du reversement hebdomadaire [RG-018 ; M07 ; Plan T-054].
- **FR-031**: Chaque traitement planifié DOIT être idempotent : une exécution répétée sur le même état ne
  DOIT produire ni doublon de statut, ni double comptage financier.
- **FR-032**: Chaque traitement planifié DOIT pouvoir être testé avec une horloge simulable (avancer le
  temps sans attendre le délai réel), condition exigée par les tâches T-005, T-034, T-050, T-053 et T-054
  du plan.
- **FR-033**: Chaque exécution d'un traitement planifié qui modifie un statut ou un montant DOIT être
  historisée dans le journal d'audit transverse (FR-022).

### Stratégie de stockage et de service des photos produits

- **FR-040**: Le socle DOIT contrôler, à la réception d'une photo produit, son type (image) et sa taille,
  et refuser tout fichier non conforme avec un message explicite indiquant la raison. [ENF-011 ; Plan T-020]
- **FR-041**: Le socle DOIT produire au moins une version de chaque photo produit redimensionnée pour un
  affichage lisible sur un écran de 360 px de large. [ENF-002 ; ENF-011]
- **FR-042**: Le socle DOIT nommer et organiser les fichiers de façon à éviter toute collision entre
  vendeurs, et à empêcher qu'une photo d'un autre produit soit déductible par simple manipulation du nom
  de fichier. [ENF-007]
- **FR-043**: Les photos produits DOIVENT être incluses dans la stratégie de sauvegarde du socle (FR-005).
- **FR-044**: Le service des photos DOIT contribuer à l'objectif ENF-004 (95 % des consultations de
  catalogue et de fiche produit affichées en moins de 3 secondes sur 4G), notamment par un poids de
  fichier adapté au mobile et une stratégie de mise en cache. Le budget exact de poids par image et le
  mécanisme de cache sont des décisions d'ADR (FR-007), mesurées lors de la tâche de recette T-067 ; la
  valeur cible elle-même reste HYPOTHÈSE (H-11) à confirmer par le porteur du projet avant le lancement.

### Sécurité et données

- **FR-050**: Le socle DOIT authentifier chaque utilisateur par son numéro de téléphone et distinguer
  trois rôles : Client, Vendeur, Administrateur. [ENF-007 ; F001 ; RG-014]
- **FR-051**: Un vendeur ne DOIT accéder qu'à ses propres données (boutique, produits, sous-commandes,
  montants, retours) ; aucune action du socle ne DOIT lui permettre de lire ou de modifier les données
  d'un autre vendeur. [ENF-007 ; Constitution Principe V]
- **FR-052**: Seul l'administrateur DOIT pouvoir saisir les statuts de collecte, de livraison,
  d'encaissement et de reprise des retours. [D38 ; RG-029 ; ENF-007]
- **FR-053**: La société de livraison ne DOIT disposer d'aucun accès à la plateforme ; toute information
  qu'elle transmet DOIT passer par une saisie de l'administrateur. [D38 ; §5 ; §19]
- **FR-054**: Un mot de passe ne DOIT jamais être affiché ni renvoyé par le socle à aucun rôle, y compris
  l'administrateur. [ENF-007 ; Constitution Principe V]
- **FR-055**: Les coordonnées bancaires des vendeurs et les moyens de remboursement des clients DOIVENT
  être accessibles uniquement à l'administrateur et à la personne concernée. [§19 ; Constitution Principe VIII]
- **FR-056**: Aucun secret (identifiant d'infrastructure, clé, jeton) ne DOIT être commité dans le dépôt ;
  la configuration sensible DOIT provenir de variables d'environnement documentées (gabarit d'exemple
  sans valeur réelle). [Constitution Principe VIII]
- **FR-057**: Les journaux d'exploitation et le journal d'audit ne DOIVENT contenir aucune donnée
  personnelle sensible en clair (coordonnées bancaires, mot de passe) ; seules les références nécessaires
  au suivi métier sont conservées. [§19 ; ENF-008]
- **FR-058**: Pour chaque ligne de la matrice des permissions du cahier §5, le socle DOIT permettre
  d'écrire un test d'accès autorisé et un test d'accès interdit. [§5 ; Constitution Principe V ; Plan T-066]
- **FR-059**: La durée de conservation des données personnelles des clients et des vendeurs est
  [NEEDS CLARIFICATION: durée de conservation non fixée par le cahier §19 ("durées MANQUANTES") ; à
  définir avec un conseil juridique avant le lancement, au titre de la loi 09-08 et de la porte de
  lancement C-08/ENF-009]. En l'absence de valeur validée, le socle DOIT prévoir un mécanisme de purge ou
  d'anonymisation paramétrable plutôt qu'une règle de suppression codée en dur.

### Évolutivité sans refonte (ENF-010)

- **FR-060**: Le socle DOIT permettre d'ajouter une nouvelle ville desservie pour les clients par
  configuration d'un référentiel, sans modification du code des parcours existants. [RG-001 ; ENF-010]
- **FR-061**: Le socle DOIT permettre d'ajouter une nouvelle commune autorisée pour les vendeurs par
  configuration d'un référentiel, sans modification du code des parcours existants. [RG-023 ; ENF-010]
- **FR-062**: Le découpage en modules DOIT permettre d'ajouter un mode de paiement en ligne comme une
  extension du module M04 (Panier et commande), sans réécrire les autres modules. [ENF-010 ; §21]
- **FR-063**: Le découpage en modules DOIT permettre d'ajouter un modèle de commission ou d'abonnement
  vendeur comme une extension du module M07 (Reversements vendeurs), sans réécrire le calcul existant pour
  les vendeurs gratuits en V1. [ENF-010 ; RG-005 ; §21]
- **FR-064**: Le découpage en modules DOIT permettre d'ajouter un accès direct de la société de livraison
  (saisie de ses propres statuts) comme une extension du module M06 (Livraison et encaissement), qui
  complète sans remplacer la saisie par l'administrateur. [ENF-010 ; D38 ; §21]
- **FR-065**: Le découpage en modules DOIT permettre d'ajouter la livraison internationale comme une
  extension des référentiels de zones (FR-060), sans modifier la structure de Commande/SousCommande.
  [ENF-010 ; §21]

### Volumétrie et dimensionnement

- **FR-070**: Le socle DOIT prévoir un dimensionnement (capacité, choix d'hébergement) explicitement
  révisable, car les volumes attendus à 12 mois (nombre de vendeurs, de produits, de commandes) sont
  [NEEDS CLARIFICATION: volumes à 12 mois non fournis par le porteur du projet — ENF-006, Q21]. En
  l'absence de valeur validée, le socle DOIT être dimensionné pour un usage de lancement modeste (zone
  Tanger et communes voisines uniquement) et DOIT permettre une montée en charge par ajustement de
  configuration ou de ressources, sans refonte architecturale.

### Mobile-first et performance

- **FR-080**: Tous les parcours des trois profils (client, vendeur, administrateur) DOIVENT être
  utilisables sur un écran de 360 px de large minimum, sans défilement horizontal ni fonctionnalité
  rendue inaccessible. [ENF-002 ; Constitution Principe VII]
- **FR-081**: Le socle DOIT fournir le cadre commun (gabarits, composants partagés) permettant une
  conception mobile-first pour les trois profils, une adaptation desktop ultérieure ne devant pas casser
  ce parcours à 360 px. [ENF-002]

### Key Entities *(include if feature involves data)*

- **Module (M01–M11)** : unité de responsabilité métier définie au cahier §9 ; possède ses propres
  données, expose un service interne aux autres modules, et ne les appelle que selon le graphe de
  dépendances autorisé (FR-014).
- **Paramètre métier configurable** : valeur révisable par l'administrateur sans déploiement (délais,
  montants, listes de communes/villes/catégories exclues) ; jamais une valeur métier codée en dur.
- **Entrée de journal d'audit** : enregistrement immuable d'une action financière ou d'une saisie de
  statut (qui, quand, quoi, montant, motif) ; une correction se fait par une nouvelle entrée, jamais par
  modification de l'existante.
- **Tâche planifiée (job)** : traitement différé déclenché par le temps, idempotent, dont l'horloge peut
  être simulée en test ; chaque exécution affectant un statut ou un montant produit une entrée d'audit.
- **Photo produit** : fichier image associé à un produit, dont au moins une version redimensionnée pour
  mobile est servie ; soumise au contrôle de type/taille et incluse dans la sauvegarde.
- **Environnement d'exécution** : local, recette ou production ; chacun porte sa propre configuration et
  ses propres secrets, jamais partagés ni commités.
- **ADR (décision d'architecture)** : document consignant une décision technique nécessaire au socle, au
  statut initial « Proposé » ; seul le porteur du projet change ce statut.
- **Notification interne** : message destiné à un acteur (client, vendeur, administrateur) à l'intérieur
  de l'application, distinct par construction de tout canal d'envoi externe (SMS, e-mail, WhatsApp…).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Les trois profils (client, vendeur, administrateur) réalisent leur parcours principal sur un
  écran de 360 px de large, sans défilement horizontal ni élément inaccessible. (ENF-002)
- **SC-002**: 95 % des consultations mesurées du catalogue et de la fiche produit s'affichent en moins de
  3 secondes sur une connexion 4G simulée. (ENF-004 ; valeur cible HYPOTHÈSE H-11 à confirmer avant
  lancement)
- **SC-003**: La disponibilité de la plateforme, mesurée sur une fenêtre glissante mensuelle hors
  maintenance annoncée, atteint 99 %. (ENF-005 ; valeur cible HYPOTHÈSE H-11 à confirmer avant lancement)
- **SC-004**: Chacun des quatre traitements planifiés (expiration réponse vendeur, fin du délai de retour,
  alerte de délai légal, reversement hebdomadaire) produit, dans un test à horloge simulée, un résultat
  unique et correct avant et après son échéance.
- **SC-005**: Une exécution en double d'un même traitement planifié ne produit aucun doublon de statut ni
  de montant, vérifié par un test dédié par traitement.
- **SC-006**: 100 % des photos produits dans un format et une taille autorisés sont servies en une version
  lisible sur un écran de 360 px ; 100 % des fichiers refusés affichent un message explicite de refus.
- **SC-007**: Pour chacune des lignes de la matrice des permissions du cahier §5, un test d'accès autorisé
  et un test d'accès interdit existent et passent ; aucun accès interdit ne réussit en recette.
- **SC-008**: Aucun secret (mot de passe, clé, jeton) n'est trouvé dans le dépôt ou son historique lors
  d'un audit de recette avant le lancement.
- **SC-009**: Chacune des 70 tâches du plan est rattachée sans ambiguïté à exactement un module M01–M11 ou
  à la liste des composants transverses du socle.
- **SC-010**: Au moins une extension d'évolutivité (nouvelle ville, nouvelle commune, ou mode de livraison
  fictif) est ajoutée par configuration ou extension additive sans modification du code des modules
  existants autres que celui qui porte l'extension. (ENF-010)

## Assumptions

- Le choix de stack technique (environnement d'exécution, bibliothèques) est déjà cadré par la
  constitution du projet (section « Contraintes et stack technique », consécutive à C-07) comme une
  décision d'architecte à documenter par un ADR au statut « Proposé » ; cette spécification décrit les
  responsabilités et garanties que ce choix doit satisfaire, sans le reformuler en code ou en
  configuration.
- Le découpage en modules M01–M11 suit strictement la définition du cahier §9 ; en cas de divergence avec
  le regroupement par vague du plan §3 (ex. T-017), le cahier §9 prime (Constitution, Principe I).
- Les valeurs non tranchées du cahier (Q19, Q27, Q40, Q42, Q44, Q45, délai légal, seuil d'alerte, jour de
  reversement — HYPOTHÈSE H-08) sont traitées comme des paramètres configurables par l'administrateur,
  jamais comme des constantes codées en dur.
- Le canal externe de notification (SMS, e-mail, WhatsApp — Q23) reste une décision séparée et non
  bloquante pour le socle : le service de notifications internes (FR-023) fonctionne indépendamment de
  cette décision, et l'adaptateur externe correspondant (plan T-010) reste une extension future.
- Les valeurs cibles ENF-003/004/005 et le dimensionnement ENF-006 restent des hypothèses ou des manques
  (HYPOTHÈSE H-11) : le socle est conçu pour permettre leur mesure et leur révision, pas pour les fixer
  définitivement dans ce document.
- La validation juridique (loi 31-08, loi 09-08, C-08) reste une porte de lancement distincte de ce
  socle : ce document prépare les mécanismes (paramètres, audit, cloisonnement, purge des données) que
  cette validation pourra exiger, sans l'anticiper.
