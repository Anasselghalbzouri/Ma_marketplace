# Feature Specification: Schéma de données physique (T-002)

**Feature Branch**: `002-schema-donnees`

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "Tâche T-002 du plan — schéma de données physique (persistance) de la marketplace de produits locaux marocains. Couvrir chaque classe de CLASS-01 et CLASS-02 par une structure persistée, chaque énumération par un type contrôlé par la base, garantir en base les invariants statiques du cahier des charges, laisser les règles dynamiques aux services en fournissant les index qui les rendent rapides, garantir l'exactitude, la traçabilité et le cloisonnement de l'argent, lister un par un les écarts entre le schéma et l'UML avec leur destinataire, et conserver au plus trois points ouverts en [NEEDS CLARIFICATION]."

## Contexte et portée

Cette spécification décrit **le schéma de données physique** requis par la tâche T-002 du plan
d'implémentation (`/opt/data/uml/marketplace-produits-locaux-maroc/plan/plan-marketplace-produits-locaux-maroc.md`,
§3) : la persistance des entités métier de la marketplace (comptes, catalogue, panier, commandes,
retours, argent), telle qu'approuvée par les diagrammes de classes. Elle décrit **le QUOI et le
POURQUOI** — quelles structures existent, quelles garanties la base apporte, quelles garanties
restent du ressort des services — et non le code (migrations, requêtes, ORM), qui relève d'une
tâche d'implémentation ultérieure.

**Sources** (citées, non recopiées) :
- Cahier des charges v1.1 validé : `/opt/data/cahiers/marketplace-produits-locaux-maroc/cahier-des-charges-v1.1.md`
  — §5 (acteurs, matrice des permissions), §7 (vision fonctionnelle, cycles de vie), §10 (F001–F022),
  §11 (RG-001 à RG-030, RG-011b), §15 (CA-F0xx), §19 (sécurité et données).
- Diagrammes de classes approuvés : `CLASS-01-comptes-catalogue-commandes.drawio`,
  `CLASS-02-retours-argent.drawio` (source lisible : `_sources/gen_class.py`).
- Machines à états approuvées : `STATE-001-commande.drawio`, `STATE-002-sous-commande.drawio`,
  `STATE-003-retour.drawio`, `STATE-004-montant-vendeur.drawio` (source lisible : `_sources/gen_state.py`).
- Plan de Compass : §2 (constats M-01..M-09, U-01, U-02, H-01..H-11), §3 (tâche T-002), §4 (chemin
  critique, coordination sur fichiers partagés).
- Socle T-001 : `specs/001-architecture-socle/spec.md` (FR-050 à FR-057) et `data-model.md` (Compte,
  Parametre, EntreeJournalAudit, vue socle hors périmètre métier).
- Architecture : `docs/architecture/ARCHITECTURE.md` (découpage M01–M11), `docs/architecture/DECISIONS.md`
  (ADR-008, ADR-010 à ADR-015 — déjà proposés pour T-002), `docs/architecture/SECURITY.md`.
- Constitution : `.specify/memory/constitution.md` (Principe I le métier d'abord, III une seule porte
  par état métier, IV argent et traçabilité, V cloisonnement par rôle, VIII aucun secret).

**Principe directeur (Constitution, Principe I ; C-07)** : aucune valeur métier n'est inventée ici.
Les décisions techniques déjà proposées pour cette tâche (ADR-010 à ADR-015, statut « Proposé ») sont
des contraintes de conception à respecter, pas des choix que ce document refait ; elles sont citées
comme sources, pas répétées. Les points encore MANQUANT ou HYPOTHÈSE au cahier (§22) restent soit des
paramètres (mécanisme `Parametre` du socle T-001, HYPOTHÈSE H-08), soit des `[NEEDS CLARIFICATION]`
explicites (maximum trois, imposé par ce document).

## User Scenarios & Testing *(mandatory)*

Les « utilisateurs » de ce schéma sont les trois profils finaux, dont les garanties métier (prix,
stock, avis, argent, retours) ne doivent jamais dépendre uniquement d'un contrôle applicatif oublié,
ainsi que les équipes Backend qui construisent les tâches T-005 et suivantes sur cette base.

### User Story 1 - Chaque classe approuvée a une structure persistée (Priority: P1)

En tant qu'équipe Backend construisant une fonctionnalité (ex. retours, montants vendeurs), je dois
trouver une structure persistée pour chaque entité des diagrammes CLASS-01 et CLASS-02 approuvés, afin
de ne jamais avoir à improviser une table manquante en cours d'implémentation.

**Why this priority** : sans couverture complète, toute tâche en aval (T-005 et suivantes) est bloquée
ou doit improviser une structure non revue, ce qui romprait la chaîne de validation (Constitution,
Principe I).

**Independent Test** : pour chacune des 24 classes de CLASS-01/02 (13 de CLASS-01, 11 de CLASS-02),
vérifier qu'une structure persistée existe et porte chacun des attributs listés par le diagramme,
indépendamment de toute autre fonctionnalité métier.

**Acceptance Scenarios**:

1. **Given** la liste des classes de CLASS-01 (Client, Vendeur, Boutique, Produit, Catégorie,
   CommuneVendeur, VilleDesservie, Panier, LignePanier, Commande, SousCommande, LigneCommande, Avis),
   **When** on la confronte au schéma physique, **Then** chacune a une structure persistée correspondante.
2. **Given** la liste des classes de CLASS-02 (Retour, Vérification, Litige, Remboursement,
   FraisDeRetour, MontantVendeur, Déduction, Reversement, RemiseDeFonds, Écart, SociétéDeLivraison),
   **When** on la confronte au schéma physique, **Then** chacune a une structure persistée correspondante
   (SociétéDeLivraison, acteur externe sans accès à la Plateforme — D38 —, n'a aucun attribut métier à
   persister au-delà d'une référence).

---

### User Story 2 - Chaque énumération est un type fermé contrôlé par la base (Priority: P1)

En tant qu'administrateur ou service applicatif, je dois être certain qu'aucune valeur de statut ou de
motif hors de la liste approuvée ne peut jamais être enregistrée, même par une erreur de code ou une
écriture directe, afin que les machines à états (STATE-001 à STATE-004) restent fiables.

**Why this priority** : les statuts pilotent l'argent (Principe III, une seule porte par état métier) ;
une valeur hors liste non détectée casserait silencieusement les machines à états et les calculs de
montants.

**Independent Test** : sur une base vide, tenter d'insérer chacune des 9 énumérations (StatutCommande,
StatutSousCommande, ModeReversement, StatutRetour, MotifRetour, StatutMontant, MoyenRemboursement,
ImputationFrais, RésultatVérification) avec une valeur absente de sa liste fermée et constater le rejet
par la base elle-même, pas par un contrôle applicatif contournable.

**Acceptance Scenarios**:

1. **Given** une base vide, **When** une tentative d'écriture fixe `StatutCommande` à une valeur hors de
   {EnAttenteAcceptation, Confirmée, EnCollecte, EnLivraison, LivréeEtPayée, ÉchecDeLivraison, Annulée},
   **Then** la base refuse l'écriture.
2. **Given** une base vide, **When** la même tentative est répétée pour chacune des 8 autres énumérations
   avec une valeur hors de leur liste fermée respective, **Then** la base refuse systématiquement
   l'écriture.

---

### User Story 3 - Les invariants statiques du cahier sont garantis par la base (Priority: P1)

En tant que client, vendeur ou administrateur, je dois être protégé contre un prix négatif, un stock
négatif, une note hors de 1 à 5, un deuxième avis sur le même produit et la même commande, une
sous-commande dupliquée pour un même vendeur, un virement sans coordonnées bancaires, un remboursement
en espèces non traçable, ou une commande déclarée « livrée et payée » sans montant ni date — même si le
code applicatif oublie de les vérifier.

**Why this priority** : ce sont des règles qui ne dépendent d'aucune autre ligne ni du temps (contraire
de RG-006/RG-019/RG-024) ; ADR-013 les confie explicitement à la base pour qu'une écriture directe ne
puisse jamais les violer (Principe IV, argent non négociable).

**Independent Test** : sur une base vide, tenter chacune des violations listées (prix ≤ 0, stock < 0,
note hors 1..5, deuxième avis même produit/même commande, deuxième sous-commande même vendeur/même
commande, virement sans coordonnées bancaires, remboursement en espèces non traçable, « livrée et
payée » sans montant encaissé ni date de réception, échec ou refus sans motif) et constater le rejet par
la base.

**Acceptance Scenarios**:

1. **Given** une base vide, **When** un produit est inséré avec un prix ≤ 0 MAD, **Then** la base rejette
   l'écriture (F003, CA équivalent à l'exception « prix ≤ 0, donc refusé »).
2. **Given** une base vide, **When** un produit est inséré avec un stock négatif, **Then** la base rejette
   l'écriture (CLASS-01).
3. **Given** une base vide, **When** un avis est inséré avec une note hors de 1 à 5, **Then** la base
   rejette l'écriture (F012).
4. **Given** un avis déjà enregistré pour un produit et une commande, **When** un second avis est inséré
   pour le même produit et la même commande, **Then** la base rejette la seconde insertion (RG-011).
5. **Given** une sous-commande déjà créée pour un vendeur et une commande, **When** une seconde
   sous-commande est insérée pour le même vendeur et la même commande, **Then** la base rejette
   l'insertion (RG-003).
6. **Given** un vendeur qui choisit le virement comme mode de reversement, **When** il est inséré ou mis
   à jour sans coordonnées bancaires, **Then** la base rejette l'écriture (CA-F002-2).
7. **Given** un remboursement en cours d'enregistrement, **When** le moyen choisi est « espèces » sans
   référence traçable, **Then** la base rejette l'écriture (RG-022).
8. **Given** une commande passant au statut « livrée et payée », **When** le montant encaissé ou la date
   de réception sont absents, **Then** la base rejette la transition (CA-F010-1).
9. **Given** une commande passant au statut « échec de livraison », ou une sous-commande passant au
   statut « refusée », **When** le motif est absent, **Then** la base rejette l'écriture (CA-F010-3,
   RG-011b).

---

### User Story 4 - L'argent est exact, traçable et cloisonné (Priority: P1)

En tant qu'administrateur, je dois pouvoir faire confiance à chaque montant affiché au dirham près, et
retrouver l'historique complet de chaque mouvement financier sans qu'aucune ligne n'ait pu être modifiée
après coup ; en tant que vendeur ou client, mes coordonnées bancaires ou de remboursement ne doivent
jamais être visibles par quiconque d'autre que l'administrateur et moi-même.

**Why this priority** : Constitution Principe IV (argent et traçabilité non négociables) et Principe
VIII (aucun secret, données sensibles cloisonnées) ; ENF-008 exige une traçabilité complète et
consultable par l'administrateur ; FR-055 (T-001) exige le cloisonnement des coordonnées bancaires et de
remboursement.

**Independent Test** : vérifier qu'aucune opération d'addition/soustraction de montants ne produit
d'écart d'arrondi sur un jeu de montants exacts (ex. CA-F011-5 : 500 − 80 = 420 au centime) ; vérifier
qu'une tentative de modification ou de suppression d'une ligne du journal d'audit est refusée ; vérifier
qu'un compte autre que l'administrateur ou le titulaire ne peut pas lire des coordonnées bancaires ou de
remboursement.

**Acceptance Scenarios**:

1. **Given** un vendeur ayant 500 MAD disponibles et 80 MAD de déductions en attente, **When** le
   reversement hebdomadaire est calculé, **Then** le montant obtenu est exactement 420 MAD, sans écart
   d'arrondi (CA-F011-5).
2. **Given** une ligne déjà écrite dans le journal d'audit, **When** une tentative de mise à jour ou de
   suppression est effectuée, **Then** elle est refusée ; seule une nouvelle ligne référençant l'entrée
   visée peut la corriger (ADR-008, ADR-015).
3. **Given** les coordonnées bancaires d'un vendeur A, **When** un vendeur B ou un client tente de les
   lire, **Then** l'accès est refusé ; seul le vendeur A et un administrateur y accèdent (FR-055).
4. **Given** les coordonnées de remboursement d'un client, **When** un autre client, un vendeur ou la
   société de livraison tente de les lire, **Then** l'accès est refusé.

---

### User Story 5 - Les règles dynamiques restent dans les services, avec des index qui les rendent rapides (Priority: P2)

En tant que client parcourant le catalogue, ou en tant qu'administrateur suivant les échéances
(réponse vendeur, fin du délai de retour, alerte légale, reversement hebdomadaire), je dois obtenir une
réponse rapide même si ces règles dépendent du temps ou d'autres lignes et ne sont donc pas garanties
par la base elle-même.

**Why this priority** : RG-006 (visibilité), RG-019 (délai de 7 jours), RG-024 (retenue) et la
comparaison quantité ≤ stock dépendent d'autres lignes ou du temps (ADR-013) ; sans index adapté, ENF-004
(catalogue affiché en moins de 3 s pour 95 % des consultations) ne peut pas être tenu à mesure que le
volume de produits et de commandes augmente.

**Independent Test** : sur un jeu de données de taille représentative, mesurer que la recherche des
produits visibles et commandables, le repérage des échéances des traitements planifiés et le calcul
hebdomadaire des montants disponibles par vendeur s'exécutent sans dégradation perceptible, sans
dépendre de l'implémentation des services qui les appellent.

**Acceptance Scenarios**:

1. **Given** un catalogue de plusieurs milliers de produits, **When** le catalogue public est affiché,
   **Then** le filtrage « publié ∧ non masqué ∧ stock > 0 ∧ vendeur actif » (RG-006) s'appuie sur une
   structure de recherche dédiée et ne dégrade pas le budget ENF-004.
2. **Given** plusieurs milliers de commandes en cours, **When** le traitement planifié repère les
   commandes dont le délai de retour de 7 jours (RG-024) se termine, **Then** il les retrouve sans
   parcourir l'ensemble des commandes historiques.
3. **Given** plusieurs centaines de vendeurs, **When** le reversement hebdomadaire calcule les montants
   disponibles moins les déductions en attente par vendeur, **Then** le calcul s'appuie sur une structure
   de recherche dédiée par vendeur et par statut de montant.

---

### User Story 6 - Les écarts entre le schéma et l'UML sont tous identifiés (Priority: P3)

En tant qu'architecte ou porteur du projet relisant ce schéma, je dois pouvoir distinguer ce qui suit
exactement les diagrammes approuvés de ce qui s'en écarte, avec pour chaque écart une justification et
la personne qui doit le trancher, afin de ne jamais découvrir un écart non documenté en cours
d'implémentation.

**Why this priority** : Constitution Principe I (le métier d'abord) ; un écart non signalé romprait la
chaîne de validation entre le cahier des charges, l'UML approuvé et le schéma physique.

**Independent Test** : comparer la liste des écarts documentés (section « Écarts avec l'UML approuvé »)
à une relecture indépendante des diagrammes CLASS-01/02 et STATE-001..004 ; tout écart trouvé en dehors
de cette liste est un défaut de cette spécification.

**Acceptance Scenarios**:

1. **Given** la liste des écarts documentés, **When** chaque écart est relu, **Then** il porte une
   justification et un destinataire (Blueprint pour un manque de modélisation UML, @user pour une
   question métier non tranchée).
2. **Given** le schéma complet, **When** il est confronté classe par classe et énumération par
   énumération aux diagrammes approuvés, **Then** aucune différence non listée n'est trouvée.

---

### Edge Cases

- Que se passe-t-il si un service applicatif tente d'écrire un statut `StatutCommande`,
  `StatutSousCommande`, `StatutRetour` ou `StatutMontant` directement, en dehors du service propriétaire
  désigné (Constitution Principe III) ? → Hors du périmètre de ce schéma (c'est une règle d'organisation
  du code, pas une contrainte de base) ; le schéma n'impose qu'un type fermé par valeur, pas l'identité de
  l'appelant.
- Que se passe-t-il si une commande passe à « Annulée » après que des sous-commandes ont déjà été
  acceptées ? → Le stock réservé doit pouvoir être restitué (RG-017) ; le schéma doit conserver la
  quantité réservée par ligne de commande pour permettre cette restitution, sans la recalculer depuis le
  panier d'origine (qui a pu changer depuis).
- Que se passe-t-il si un retour est en cours sur une ligne de commande au moment où le délai de 7 jours
  expire ? → Le montant correspondant reste « Retenu » jusqu'à la clôture du retour (RG-024, note
  CLASS-02 n_mv) ; le schéma doit permettre de savoir, pour chaque ligne de commande, si un retour non
  clos lui est associé.
- Que se passe-t-il si le même vendeur est réglé deux fois pour le même produit retourné (une fois avant,
  une fois après son reversement hebdomadaire) ? → Le schéma distingue l'annulation d'un montant encore
  « Retenu » (RG-021) de la création d'une « Déduction » régularisée sur le reversement suivant si le
  montant est déjà « Reversé » (CA-F011-4) ; les deux chemins doivent être représentables sans ambiguïté.
- Que se passe-t-il si le solde d'un vendeur devient négatif après régularisation ? → Non tranché (Q38,
  HYPOTHÈSE H-07) ; le schéma ne doit pas empêcher qu'une « Déduction » dépasse le montant « Disponible »
  d'un vendeur, le traitement du solde négatif restant un comportement de service à définir après
  décision du porteur.
- Que se passe-t-il si l'administrateur tente de modifier une ligne déjà écrite dans le journal
  d'audit ? → Refusé par construction (User Story 4) ; seule une nouvelle ligne corrective est possible.
- Que se passe-t-il si une catégorie est marquée « exclue du retour » après qu'un produit de cette
  catégorie a déjà été vendu ? → Le schéma n'a pas besoin de figer l'exclusion au moment de la vente :
  RG-019 est une règle dynamique évaluée au moment de la demande de retour, pas une contrainte statique
  de la base.

## Requirements *(mandatory)*

### Couverture des entités métier (CLASS-01, CLASS-02)

- **FR-001**: Le schéma DOIT fournir une structure persistée pour chacune des entités de comptes, de
  zones et de catalogue de CLASS-01 : Client, Vendeur, Boutique, Produit, Catégorie, CommuneVendeur,
  VilleDesservie — portant au minimum les attributs listés par le diagramme.
- **FR-002**: Le schéma DOIT fournir une structure persistée pour le panier (Panier, LignePanier) et pour
  la commande (Commande, SousCommande, LigneCommande) de CLASS-01, avec une sous-commande par vendeur et
  par commande (RG-003) et une ligne de panier limitée en quantité par le stock au moment de l'ajout
  (CA-F006-2, règle dynamique — voir FR-019).
- **FR-003**: Le schéma DOIT fournir une structure persistée pour l'avis (Avis), rattachée à une ligne de
  commande et soumise à l'invariant « un avis par produit et par commande » (RG-011, voir FR-013).
- **FR-004**: Le schéma DOIT fournir une structure persistée pour chacune des entités de retour et de
  litige de CLASS-02 : Retour, Vérification, Litige, Remboursement, FraisDeRetour — portant au minimum
  les attributs listés par le diagramme, avec un retour distinct par ligne de commande (RG-030).
- **FR-005**: Le schéma DOIT fournir une structure persistée pour chacune des entités de montants
  vendeurs de CLASS-02 : MontantVendeur, Déduction, Reversement.
- **FR-006**: Le schéma DOIT fournir une structure persistée pour le rapprochement avec la société de
  livraison (RemiseDeFonds, Écart) ; SociétéDeLivraison, acteur externe sans accès à la Plateforme (D38),
  n'est représentée que par une référence minimale, sans duplication de données qu'elle ne transmet pas
  à la Plateforme (C-05).
- **FR-007**: Le schéma DOIT fournir une structure persistée pour le journal d'audit financier
  (EntreeJournalAudit), absent des diagrammes CLASS-01/02 mais exigé par ENF-008 et confirmé par
  ADR-008 ; voir la section « Écarts avec l'UML approuvé ».

### Énumérations contrôlées par la base

- **FR-008**: Chacune des neuf énumérations suivantes DOIT être un type fermé contrôlé par la base :
  aucune valeur hors de sa liste n'est acceptée, lors d'un essai sur une base vide.

  | Énumération | Valeurs fermées | Source |
  |---|---|---|
  | StatutCommande | EnAttenteAcceptation, Confirmée, EnCollecte, EnLivraison, LivréeEtPayée, ÉchecDeLivraison, Annulée | §7, D44, RG-029 |
  | StatutSousCommande | Nouvelle, Acceptée, PrêtePourCollecte, Collectée, Refusée, Annulée | §7, RG-003, RG-029 |
  | ModeReversement | Virement, Espèces | D21, RG-018 |
  | StatutRetour | Demandé, EnReprise, Repris, VérifiéParLeVendeur, Contesté, Litige, ClientRemboursé, RetourRefusé | §7, RG-030 |
  | MotifRetour | ChangementDAvis, Défectueux, Incorrect, NonConforme | F022, D30 |
  | StatutMontant | Retenu, Disponible, Reversé, Déduit | §7, D29, D34 |
  | MoyenRemboursement | VirementBancaire, AutreMoyenTraçable | RG-022, D32 |
  | ImputationFrais | Client, Vendeur | RG-025 |
  | RésultatVérification | Conforme, Contesté | RG-027 |

### Invariants statiques garantis par la base

- **FR-009**: Le prix d'un produit DOIT être strictement supérieur à 0 ; la base DOIT refuser toute
  écriture contraire (F003).
- **FR-010**: Le stock d'un produit DOIT être supérieur ou égal à 0 ; la base DOIT refuser toute écriture
  contraire (CLASS-01).
- **FR-011**: La note d'un avis DOIT être comprise entre 1 et 5 inclus ; la base DOIT refuser toute
  écriture contraire (F012).
- **FR-012**: La base DOIT garantir qu'il n'existe jamais plus d'un avis pour un même produit et une même
  commande (RG-011) ; un second avis est une modification de l'avis existant, pas une nouvelle ligne.
- **FR-013**: La base DOIT garantir qu'il n'existe jamais plus d'une sous-commande pour un même vendeur
  et une même commande (RG-003).
- **FR-014**: La base DOIT refuser qu'un vendeur ayant choisi le virement comme mode de reversement soit
  enregistré ou mis à jour sans coordonnées bancaires (CA-F002-2).
- **FR-015**: La base DOIT refuser qu'un remboursement soit enregistré avec un moyen non traçable (espèces
  non traçables) ; seuls le virement bancaire ou un autre moyen traçable et légalement autorisé sont
  acceptés (RG-022).
- **FR-016**: La base DOIT refuser qu'une commande passe au statut « livrée et payée » sans montant
  encaissé ni date de réception renseignés (CA-F010-1).
- **FR-017**: La base DOIT refuser qu'une commande passe au statut « échec de livraison », ou qu'une
  sous-commande passe au statut « refusée », sans motif renseigné (CA-F010-3, RG-011b).

### Règles dynamiques laissées aux services, avec index de performance

- **FR-018**: Le schéma NE DOIT PAS tenter de garantir lui-même les règles qui dépendent du temps ou
  d'autres lignes : visibilité et commandabilité d'un produit (RG-006), délai de retour de 7 jours
  (RG-019), fin de la retenue des montants vendeurs (RG-024), quantité demandée au plus égale au stock
  (CA-F006-2) ; ces règles restent garanties par les services uniques désignés (Constitution Principe III,
  ADR-013).
- **FR-019**: Le schéma DOIT fournir une structure de recherche dédiée permettant de retrouver rapidement
  les produits visibles et commandables (publié, non masqué, stock > 0, vendeur actif — RG-006), pour
  tenir le budget de performance du catalogue (ENF-004).
- **FR-020**: Le schéma DOIT fournir une structure de recherche dédiée permettant de retrouver rapidement
  les échéances des traitements planifiés : expiration de la réponse vendeur, fin du délai de retour de 7
  jours, alerte de délai légal (ENF-012), reversement hebdomadaire (FR-030 du socle T-001).
- **FR-021**: Le schéma DOIT fournir une structure de recherche dédiée, par vendeur et par statut de
  montant, permettant le calcul hebdomadaire des montants disponibles moins les déductions en attente
  (RG-018, CA-F011-5) sans parcours complet de l'historique des montants.

### Argent exact, traçable et cloisonné

- **FR-022**: Tout montant monétaire DOIT être conservé sous une forme décimale exacte ; aucun calcul
  financier ne DOIT produire d'écart d'arrondi par rapport à un calcul exact au centime (Constitution
  Principe IV, ADR-011).
- **FR-023**: Tout mouvement financier (encaissement, remise de fonds, écart, retenue, mise à
  disposition, remboursement, frais de retour imputé, décision de litige, régularisation, reversement) et
  toute saisie de statut de livraison par l'administrateur DOIVENT être historisés dans un journal
  d'audit (qui, quand, montant si applicable, motif) consultable par l'administrateur (ENF-008).
- **FR-024**: Une ligne du journal d'audit, une fois écrite, NE DOIT JAMAIS pouvoir être modifiée ni
  supprimée ; seule une nouvelle ligne référençant l'entrée visée peut la corriger ou la régulariser
  (ADR-008) ; cette garantie DOIT être appliquée indépendamment du code applicatif (ADR-015).
- **FR-025**: Les coordonnées bancaires d'un vendeur et les coordonnées ou le moyen de remboursement d'un
  client DOIVENT être accessibles uniquement à l'administrateur et au titulaire des données ; aucun autre
  compte, y compris un autre vendeur ou un autre client, ne DOIT pouvoir les lire (FR-055 du socle T-001,
  ADR-014).

### Écarts documentés et paramètres non figés

- **FR-026**: Tout écart entre le schéma physique et les diagrammes CLASS-01/02 ou STATE-001..004
  approuvés DOIT être documenté individuellement, avec sa justification et son destinataire (Blueprint
  pour un manque de modélisation UML, @user pour une question métier non tranchée) — voir la section
  « Écarts avec l'UML approuvé ».
- **FR-027**: Les valeurs suivantes, non tranchées par le cahier des charges, NE DOIVENT PAS être des
  colonnes figées dans le schéma, mais des paramètres consultés via le mécanisme générique `Parametre` du
  socle (HYPOTHÈSE H-08) : délai de réponse vendeur (Q19), montant des frais de livraison (Q27),
  remboursement des frais de livraison initiaux (Q40), moyens de remboursement alternatifs autorisés
  (Q42), délai de vérification vendeur (Q44), montant des frais de retour (Q45).
- **FR-028**: Le schéma DOIT persister pour le Client au moins un nom et un téléphone obligatoire
  (RG-014, RG-028). Le caractère obligatoire ou non de l'adresse e-mail n'est pas tranché par le cahier
  [NEEDS CLARIFICATION: adresse e-mail du client obligatoire ou non — F001 ne tranche pas, et le moyen de
  récupération d'accès (constat M-06 du plan) en dépend ; en l'absence de réponse, le schéma rend
  l'e-mail facultatif et le téléphone seul sert à la récupération d'accès].
- **FR-029**: Le schéma DOIT persister pour le Vendeur au moins l'identité ou raison sociale, le
  téléphone, la commune, l'adresse de collecte, le mode de reversement et les coordonnées bancaires si
  virement (F002). La liste complète des informations et du statut légal exigés n'est pas tranchée
  [NEEDS CLARIFICATION: informations et statut légal exigés des vendeurs — Q22 ; en l'absence de réponse,
  le schéma ne fige que les champs confirmés ci-dessus et prévoit une zone libre pour les informations
  complémentaires, sans contrainte d'obligation supplémentaire].
- **FR-030**: Les données personnelles et financières de ce schéma (clients, vendeurs, retours,
  remboursements, journal d'audit) ont une durée de conservation non tranchée par le cahier (§19)
  [NEEDS CLARIFICATION: durée de conservation des données — §19 indique seulement « durées MANQUANTES » ;
  en l'absence de réponse, le schéma ne prévoit pas de suppression ni d'anonymisation automatique, la
  conformité à la loi 09-08 restant soumise à la validation juridique C-08 avant tout mécanisme de purge].

## Écarts avec l'UML approuvé

| ID | Écart | Justification | Destinataire |
|---|---|---|---|
| E-01 | Ajout d'un journal d'audit financier (EntreeJournalAudit), absent de CLASS-01/02. | ENF-008 exige une traçabilité complète ; U-03 du plan constate l'absence de classe d'historique dans les diagrammes approuvés ; ADR-008 confirme la nécessité de ce journal. | Blueprint (à intégrer dans une future révision des diagrammes de classes) |
| E-02 | Rattachement de Client et de Vendeur à un Compte d'authentification transverse, non représenté dans CLASS-01. | Évite de dupliquer l'authentification entre les trois rôles (FR-050 du socle T-001) ; CLASS-01 modélise Client et Vendeur comme autonomes. | Blueprint (modélisation UML à compléter) |
| E-03 | La relation Client–Panier est rendue facultative côté client (panier sans titulaire avant connexion), alors que CLASS-01 porte une cardinalité 1 côté Client (statut [I]). | Nécessaire pour un panier de visiteur rattaché après connexion (CA-F001-3) ; la cardinalité du diagramme est elle-même marquée hypothèse (H-01). | @user (confirmer H-01), puis Blueprint (mise à jour du diagramme) |
| E-04 | RemiseDeFonds et Écart sont persistées malgré leur statut HYPOTHÈSE dans CLASS-02 (aucun attribut de la société de livraison n'est spécifié, C-05). | RG-020 et le critère CA-F010-2 (écart signalé à l'administrateur) sont déjà confirmés et en dépendent directement ; les retirer bloquerait T-039/T-041. | @user (confirmer H-05 après choix du partenaire de livraison, C-05) |
| E-05 | Une contrainte d'unicité impose une seule boutique par vendeur, alors que cette cardinalité 1–1 est marquée HYPOTHÈSE (inférence) dans CLASS-01. | Aucune autre lecture du cahier des charges n'indique plusieurs boutiques par vendeur ; une contrainte stricte évite une ambiguïté silencieuse. | @user (confirmer H-06 ; si un vendeur peut tenir plusieurs boutiques, la contrainte devra être retirée) |
| E-06 | La relation entre une ligne de commande et ses retours reste ouverte (0..* dans CLASS-02) sans règle d'unicité sur la quantité déjà retournée. | La note WARN de CLASS-02 signale que les retours partiels successifs sur une même ligne ne sont pas tranchés par le cahier ; figer une règle maintenant risquerait d'interdire un cas métier valide. | @user (clarifier si une même ligne de commande peut faire l'objet de plusieurs retours partiels successifs) |
| E-07 | Le schéma ne modélise aucune transition ni aucun champ pour une décision de l'administrateur en l'absence de vérification vendeur dans les temps (STATE-003), ni pour une annulation administrative d'une sous-commande (STATE-001). | U-01 et U-02 du plan constatent que ces transitions ne sont pas dessinées dans les machines à états approuvées, faute de décision sur le délai de vérification (Q44) et de modélisation de l'annulation admin (F013). | Blueprint, après décision du porteur sur Q44 (U-01) et modélisation de l'annulation admin (U-02) |

**Liste de référence** : ce tableau résume les écarts de niveau spécification. La liste complète et
numérotée de référence (E-01 à E-23, dont les ajouts techniques et précisions de colonnes) est
`data-model.md` §7, qui donne aussi la correspondance avec les identifiants ci-dessus. Aucun écart n'est
admis s'il n'y figure pas.

## Key Entities *(include if feature involves data)*

**Comptes, zones et catalogue (CLASS-01)**
- **Client** (ENT-001) : personne inscrite commandant depuis Tanger ; nom, téléphone obligatoire, e-mail
  à préciser (FR-028).
- **Vendeur** (ENT-002) : petite entreprise locale ; identité, téléphone, commune, mode de reversement,
  coordonnées bancaires si virement, statut actif/suspendu.
- **Boutique** (ENT-003) : espace public d'un vendeur (nom, présentation, adresse de collecte) ; une par
  vendeur (E-05).
- **Produit** (ENT-004) : article vendu par un vendeur ; nom, description, photos, prix (> 0), stock
  (≥ 0), origine, périssable, personnalisé, publié, masqué, note moyenne dérivée.
- **Catégorie** (ENT-005) : regroupement de produits ; porte le drapeau d'exclusion du droit de retour
  (RG-019, D40).
- **CommuneVendeur** (ENT-006a) : commune autorisée pour l'inscription vendeur (liste fixée par
  l'administrateur, RG-023, Q41).
- **VilleDesservie** (ENT-006b) : ville où la livraison est possible (V1 : Tanger, RG-001).
- **Panier** (ENT-007) / **LignePanier** (ENT-007b) : panier multi-vendeurs d'un client (ou d'un visiteur,
  E-03) et ses lignes, quantité limitée au stock.
- **Commande** (ENT-008) : achat validé, un paiement à la livraison, un statut (StatutCommande), un
  montant encaissé et une date de réception renseignés à « livrée et payée ».
- **SousCommande** (ENT-009) : partie de la commande pour un seul vendeur, une par vendeur et par
  commande (RG-003), un statut (StatutSousCommande), un motif si refusée.
- **LigneCommande** (ENT-010) : produit, quantité et prix unitaire figé au moment de la commande (RG-007).
- **Avis** (ENT-020) : note (1 à 5) et commentaire d'un client sur un produit reçu, un par produit et par
  commande (RG-011).

**Retours et argent (CLASS-02)**
- **Retour** (ENT-011) : demande de retour d'une ligne de commande, un par ligne (RG-030) ; quantité,
  motif (MotifRetour), moyen et coordonnées de remboursement, statut (StatutRetour).
- **Vérification** (ENT-012) : contrôle du produit retourné par le vendeur ; résultat
  (RésultatVérification), décision de remise en vente.
- **Litige** (ENT-013) : arbitrage administratif d'une contestation ; décision, montant remboursé,
  imputation des frais.
- **Remboursement** (ENT-014) : montant remboursé au client, moyen traçable (MoyenRemboursement),
  référence, date.
- **FraisDeRetour** (ENT-015) : coût de la reprise d'un produit retourné, imputé au client ou au vendeur
  (ImputationFrais).
- **MontantVendeur** (ENT-016) : somme due à un vendeur pour une ligne de commande livrée et payée,
  statut (StatutMontant : Retenu, Disponible, Reversé, Déduit).
- **Déduction** (ENT-017) : montant déduit d'un vendeur, par origine (remboursement ou frais de retour),
  régularisé sur un reversement.
- **Reversement** (ENT-018) : versement hebdomadaire à un vendeur, mode (ModeReversement), montant.
- **RemiseDeFonds** (ENT-019) : montant remis par la société de livraison à la Plateforme, rapproché des
  commandes livrées et payées (E-04).
- **Écart** (ENT-019b) : différence constatée entre montant dû et montant remis (CA-F010-2, E-04).
- **SociétéDeLivraison** (ENT-021) : partenaire externe sans accès à la Plateforme (D38) ; référence
  minimale (E-06 non applicable, FR-006).

**Socle transverse réutilisé, non redéfini ici** : Compte, Parametre, EntreeJournalAudit (voir
`specs/001-architecture-socle/data-model.md` ; le journal d'audit financier devient une structure
physique concrète dans ce schéma — voir FR-007, E-01).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 % des 24 classes des diagrammes CLASS-01 et CLASS-02 approuvés ont une structure
  persistée correspondante dans le schéma.
- **SC-002**: 100 % des 9 énumérations approuvées refusent, lors d'un essai sur une base vide, toute
  valeur hors de leur liste fermée.
- **SC-003**: 100 % des tentatives de violation d'un invariant statique (prix ≤ 0, stock négatif, note
  hors de 1 à 5, second avis sur le même produit et la même commande, seconde sous-commande pour le même
  vendeur et la même commande, virement sans coordonnées bancaires, remboursement en espèces non
  traçable, « livrée et payée » sans montant ni date, échec ou refus sans motif) sont refusées par la
  base lors d'un essai sur une base vide.
- **SC-004**: Un calcul financier exact (ex. 500 MAD disponibles − 80 MAD de déductions = 420 MAD)
  produit toujours le même résultat exact, sans écart d'arrondi, sur un échantillon de montants de test.
- **SC-005**: 100 % des tentatives de modification ou de suppression d'une ligne déjà écrite du journal
  d'audit sont refusées, lors d'un essai sur une base de test.
- **SC-006**: 100 % des tentatives d'accès à des coordonnées bancaires ou de remboursement par un compte
  autre que l'administrateur ou le titulaire sont refusées, lors d'un essai par ligne de la matrice des
  permissions concernée.
- **SC-007**: La recherche des produits visibles et commandables du catalogue, le repérage des échéances
  des traitements planifiés et le calcul hebdomadaire des montants disponibles par vendeur s'exécutent
  sans dégradation perceptible sur un jeu de données de taille représentative (plusieurs milliers de
  produits et de commandes).
- **SC-008**: Aucun écart entre le schéma et les diagrammes UML approuvés n'est trouvé en dehors de la
  liste documentée dans la section « Écarts avec l'UML approuvé ».

## Assumptions

- Les décisions techniques déjà proposées pour cette tâche (ADR-010 à ADR-015 de
  `docs/architecture/DECISIONS.md`, statut « Proposé ») sont tenues pour acquises par ce document :
  conventions de nommage (ADR-010), montants en forme décimale exacte (ADR-011), énumérations en type
  fermé contrôlé par contrainte (ADR-012), partage statique/dynamique entre base et services (ADR-013),
  chiffrement applicatif des données bancaires et de remboursement (ADR-014), journal d'audit en ajout
  seul garanti par les droits d'accès à la base (ADR-015).
- Les étapes des cycles de vie Commande, SousCommande et Retour marquées HYPOTHÈSE au cahier §7 (hors
  « En collecte », confirmé par D44) sont reprises telles que modélisées par STATE-001 à STATE-003 ; si le
  porteur du projet les invalide, le schéma des statuts correspondants devra être revu (H-03 du plan).
- Le solde négatif d'un vendeur après régularisation (Q38, HYPOTHÈSE H-07) n'est pas bloqué par le
  schéma : une Déduction peut dépasser le montant Disponible d'un vendeur ; le traitement de ce cas
  (report, alerte) reste une règle de service à définir après décision du porteur.
- La définition de « produit local marocain » (Q17) n'a aucune traduction dans ce schéma au-delà de
  l'origine déclarée du produit (déjà portée par CLASS-01) ; tout contrôle additionnel dépend d'une
  définition qui reste à fixer (hors périmètre de cette tâche).
- Les six valeurs non tranchées listées en FR-027 (Q19, Q27, Q40, Q42, Q44, Q45) sont traitées comme des
  paramètres du socle T-001 et non comme des colonnes figées ; ce document ne propose aucune valeur par
  défaut pour elles.
