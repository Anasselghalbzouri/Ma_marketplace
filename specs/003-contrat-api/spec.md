# Feature Specification: Contrat d'API et matrice d'autorisations (T-003)

**Feature Branch**: `003-contrat-api`

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "Tâche T-003 du plan — contrat d'API et matrice d'autorisations (rôle ×
action) de la marketplace de produits locaux marocains. Spécifier le QUOI et le POURQUOI du contrat
d'API, pas son code : chaque cas d'utilisation UC-001 à UC-023 doit disposer d'au moins un point
d'accès rattaché à un module M01–M11 ou au socle ; chaque ligne de la matrice des permissions du
cahier §5 (17 lignes) doit être appliquée par l'API pour les quatre rôles (visiteur, client, vendeur,
administrateur), la société de livraison n'ayant aucun accès (D38), et les capacités nécessaires mais
absentes de §5 doivent être listées à part et justifiées ; un vendeur ne doit accéder qu'à ses
ressources, sans révéler l'existence de celles d'un autre titulaire ; chaque point d'accès doit avoir
un exemple de requête et des exemples de réponse en succès et en erreur avec leur code HTTP, les
erreurs provenant d'un catalogue fermé de codes stables ; les montants doivent être exacts, les
énumérations identiques au schéma T-002, les transitions d'état conformes à STATE-001..004, et une
transition interdite doit être refusée explicitement ; les actions non encore modélisées par l'UML
(U-01, U-02) doivent être réservées au contrat mais signalées bloquées ; au plus trois points ouverts
restent en [NEEDS CLARIFICATION] (panier visiteur H-01, périmètre de la supervision administrateur
F013/UC-023, levée d'une modération) ; validation par @user au point de contrôle CP-1."

## Contexte et portée

Cette spécification décrit **le contrat d'API et la matrice d'autorisations** requis par la tâche
T-003 du plan d'implémentation
(`/opt/data/uml/marketplace-produits-locaux-maroc/plan/plan-marketplace-produits-locaux-maroc.md`,
§3) : quelles actions l'API expose, à quel rôle, sur quelle ressource, et pourquoi — et non son code
(routes, contrôleurs, sérialiseurs), qui relève d'une tâche d'implémentation ultérieure.

**Sources** (citées, non recopiées) :
- Cahier des charges v1.1 validé :
  `/opt/data/cahiers/marketplace-produits-locaux-maroc/cahier-des-charges-v1.1.md` — §5 (acteurs et
  matrice des permissions, 17 lignes), §9 (modules M01–M11), §10 (F001–F022), §11 (RG-001 à RG-030,
  RG-011b), §13 (ENF-007 sécurité, ENF-008 traçabilité financière), §15 (CA-F0xx).
- Cas d'utilisation et séquences approuvés :
  `/opt/data/uml/marketplace-produits-locaux-maroc/01-cas-utilisation/UC-DIAG-01/02/03` (UC-001 à
  UC-023), `03-sequences/SEQ-001/002/003`, `05-etats/STATE-001..004`, et
  `rapport-tracabilite-validation.md`.
- Plan de Compass, tâche T-003 (§2 constats U-01, U-02 ; §3) :
  `/opt/data/uml/marketplace-produits-locaux-maroc/plan/plan-marketplace-produits-locaux-maroc.md`.
- Socle T-001 : `specs/001-architecture-socle/contracts/` (`format-erreur.md`, `statuts-http.md`,
  `pagination.md`, `authentification.md`, `versionnage.md`) ; `docs/architecture/DECISIONS.md` ;
  `.specify/memory/constitution.md` (Principes III « une seule porte par état métier », IV « argent et
  traçabilité », V « cloisonnement par rôle testé », IX « langue du code et de la documentation »).
- Schéma T-002 : `specs/002-schema-donnees/data-model.md` et
  `specs/002-schema-donnees/contracts/schema-reference.mysql.sql`.

**Principe directeur (Constitution, Principe I ; C-07)** : aucune valeur métier n'est inventée ici.
Des décisions techniques pour cette même tâche ont déjà été proposées et consignées dans
`docs/architecture/DECISIONS.md` (ADR-016 à ADR-020, statut « Proposé », 2026-10-14) et traduites dans
des artefacts machine déjà présents dans ce dossier (`contracts/openapi.yaml`,
`contracts/api-reference.md`, `contracts/authorization-matrix.yaml`/`.md`, `contracts/error-codes.md`).
Ce document ne les redécide pas : il explicite le QUOI et le POURQUOI dont ils sont l'expression
technique, les cite comme sources, et porte les trois points encore ouverts jusqu'à leur validation par
@user au point de contrôle CP-1 (voir `authorization-matrix.yaml`, statut « Proposé — CP-1 à valider
par @user »).

## User Scenarios & Testing *(mandatory)*

Les « utilisateurs » de ce contrat sont les quatre rôles de la Plateforme (visiteur, client, vendeur,
administrateur) dont les actions sont exposées ou refusées par l'API, ainsi que les équipes Frontend et
Backend qui s'appuient sur ce contrat pour construire les parcours contre une interface stable, sans
jamais inventer d'autorisation au cas par cas.

### User Story 1 - Un visiteur ou un client parcourt, commande, suit et retourne un produit en autonomie (Priority: P1)

En tant que visiteur ou client à Tanger, je veux découvrir le catalogue, commander chez plusieurs
vendeurs en un seul panier payé à la livraison, suivre ma commande et, si besoin, la retourner dans les
7 jours, afin que le contrat couvre mon parcours d'achat complet sans jamais m'ouvrir une action
réservée à un autre rôle.

**Why this priority**: c'est le parcours principal du cahier (§8, P2), objectif O3 ; sans lui, aucun
autre rôle n'a de commande à traiter.

**Independent Test**: dérouler, contre le contrat, les opérations couvrant UC-001 à UC-009 (catalogue,
fiche produit, panier, inscription/connexion, commande, suivi, annulation, avis, retour) et vérifier
qu'aucune n'exige un rôle vendeur ou administrateur.

**Acceptance Scenarios**:

1. **Given** un visiteur non connecté, **When** il consulte le catalogue, une fiche produit ou les
   avis, **Then** le contrat l'autorise sans compte (MP-01, MP-02, UC-001, UC-002).
2. **Given** un visiteur avec un panier rempli, **When** il tente de valider sa commande, **Then** le
   contrat exige une connexion ou une création de compte avant de poursuivre, et son panier est
   retrouvé après connexion (RG-028, CA-F001-3, UC-004, UC-005).
3. **Given** un client connecté avec des produits de deux vendeurs dans son panier et une adresse à
   Tanger, **When** il confirme sa commande, **Then** le contrat la crée avec paiement à la livraison
   et une sous-commande par vendeur (RG-003, RG-008, MP-04, UC-005) ; **When** l'adresse est hors de
   Tanger, **Then** le contrat la refuse explicitement (CA-F007-2).
4. **Given** une commande du client dont aucune sous-commande n'est collectée, **When** il l'annule,
   **Then** le contrat l'autorise (MP-05, UC-007) ; **When** la commande est déjà « En collecte »,
   **Then** le contrat refuse explicitement l'annulation (CA-F008-2, STATE-001).
5. **Given** un produit reçu depuis 5 jours et non exclu, **When** le client demande son retour,
   **Then** le contrat l'autorise (MP-06, UC-008) ; **When** le même produit a été reçu depuis plus de
   7 jours, ou est signalé périssable/personnalisé, ou appartient à une catégorie exclue, **Then** le
   contrat le refuse explicitement avec le motif (CA-F022-2/3/8).
6. **Given** une commande livrée et payée, **When** le client note un produit reçu, **Then** le contrat
   l'autorise une seule fois par produit et par commande (MP-10, RG-011, UC-009) ; **When** le produit
   n'a pas été reçu, **Then** le contrat refuse explicitement l'action.

---

### User Story 2 - Un vendeur gère sa boutique, ses commandes et ses retours sans jamais atteindre les ressources d'un autre vendeur (Priority: P1)

En tant que vendeur, je veux inscrire ma boutique, publier mes produits, traiter mes sous-commandes,
vérifier mes retours et consulter mes montants, afin que le contrat couvre mon activité de bout en
bout tout en garantissant qu'aucune de mes actions n'atteint jamais les ressources d'un autre vendeur.

**Why this priority**: parcours du cahier (§8, P1/P4), objectif O2 ; l'inscription vendeur étant libre
et sans validation préalable (RG-004), le cloisonnement est la seule garantie de confidentialité entre
vendeurs concurrents (Constitution, Principe V).

**Independent Test**: dérouler, contre le contrat, les opérations couvrant UC-010 à UC-014 avec deux
vendeurs A et B distincts, et vérifier qu'aucune opération de A ne retourne ni ne modifie une ressource
de B.

**Acceptance Scenarios**:

1. **Given** un visiteur situé dans une commune autorisée, **When** il s'inscrit comme vendeur avec
   toutes les informations obligatoires, **Then** le contrat active sa boutique immédiatement, sans
   validation (RG-004, UC-010) ; **When** sa commune n'est pas sur la liste autorisée, **Then** le
   contrat refuse l'inscription avec un message explicite (CA-F002-3).
2. **Given** les vendeurs A et B ayant chacun des produits, **When** A consulte ou modifie la liste de
   ses produits, **Then** le contrat ne lui montre et ne lui permet de modifier que les siens (MP-11,
   CA-F003-3, UC-011) ; **When** A tente d'agir sur un produit de B par son identifiant, **Then** le
   contrat le refuse sans révéler l'existence du produit de B.
3. **Given** une sous-commande nouvelle du vendeur A, **When** il l'accepte, la refuse ou la déclare
   prête, **Then** le contrat applique la transition correspondante de STATE-002 (MP-12, UC-012) ;
   **When** A tente une transition impossible depuis l'état courant (ex. déclarer prête une
   sous-commande déjà refusée), **Then** le contrat la refuse explicitement.
4. **Given** un produit retourné au vendeur A dans le délai de vérification, **When** il le déclare
   conforme ou le conteste avec motif, **Then** le contrat enregistre sa décision et sa proposition de
   remise en vente (MP-07, UC-013, RG-027) ; cette capacité de vérification est partagée avec
   l'administrateur en cas de litige ou d'absence de vérification du vendeur (MP-07, note cahier §5).
5. **Given** le vendeur A, **When** il consulte ses montants retenus, disponibles, reversés et déduits,
   **Then** le contrat ne lui montre que les siens (MP-14, UC-014).

---

### User Story 3 - L'administrateur opère la logistique, les litiges, les reversements et la modération sur l'ensemble de la Plateforme (Priority: P2)

En tant qu'administrateur, je veux transmettre les commandes prêtes à la société de livraison, saisir
les statuts qu'elle me transmet, arbitrer les litiges de retour, enregistrer les remboursements et les
reversements hebdomadaires, et modérer produits, vendeurs et avis, afin que le contrat couvre toutes
les actions qui, par construction, ne peuvent être exécutées par aucun autre rôle (D38, RG-029).

**Why this priority**: parcours du cahier (§8, P5), objectifs O2/O3/O5 ; sans lui, aucune commande ne
peut être livrée ni aucun vendeur payé.

**Independent Test**: dérouler, contre le contrat, les opérations couvrant UC-015 à UC-023 et vérifier
qu'aucune n'est accessible à un rôle client ou vendeur, et qu'aucune n'est accessible à la société de
livraison (D38).

**Acceptance Scenarios**:

1. **Given** une commande dont toutes les sous-commandes sont prêtes, **When** l'administrateur la
   transmet à la société de livraison, **Then** le contrat la fait passer « En collecte » et bloque son
   annulation par le client (MP-13, RG-029, D44, UC-015, CA-F010-4).
2. **Given** les statuts transmis par la société de livraison, **When** l'administrateur saisit la
   collecte, la livraison, l'encaissement, l'échec ou la reprise d'un retour, **Then** le contrat
   applique la transition correspondante de STATE-001/002/003 (MP-13, UC-016) ; **When** le montant
   encaissé diffère du montant dû, **Then** le contrat signale l'écart (CA-F010-2).
3. **Given** un retour contesté par le vendeur, **When** l'administrateur arbitre le litige et
   enregistre le remboursement, **Then** le contrat impute les frais selon sa décision et déduit les
   montants du vendeur concerné (MP-07, MP-08, MP-09, UC-018, UC-019, RG-021).
4. **Given** les montants disponibles de chaque vendeur, **When** l'administrateur enregistre le
   reversement hebdomadaire, **Then** le contrat déduit les déductions en attente et historise le mode
   (virement ou espèces) (MP-15, UC-020).
5. **Given** un produit non local ou un avis abusif, **When** l'administrateur le masque, **Then** le
   contrat le retire de la visibilité publique et en informe le vendeur (MP-11, MP-16, UC-022, RG-015).
6. **Given** n'importe quelle opération de ce contrat, **When** elle est tentée sans compte ou par la
   société de livraison, **Then** elle est refusée : aucune route n'est exposée à la société de
   livraison (D38, ENF-007).

---

### User Story 4 - Chaque ligne de la matrice des permissions est vérifiable dans un sens autorisé et un sens interdit (Priority: P2)

En tant qu'équipe Backend construisant les tests de cloisonnement (T-066 du plan), je dois pouvoir
dériver, pour chacune des 17 lignes de la matrice du cahier §5 et des 5 capacités dérivées qui n'y
figurent pas, un cas d'accès autorisé et un cas d'accès interdit directement depuis le contrat, sans
logique d'autorisation ad hoc écrite point d'accès par point d'accès.

**Why this priority**: Constitution Principe V (cloisonnement par rôle testé) ; sans cette
correspondance directe, une régression d'autorisation sur une des 22 lignes pourrait passer inaperçue.

**Independent Test**: pour chacune des 22 lignes (MP-01 à MP-17, MX-01 à MX-05), vérifier qu'au moins
une opération du contrat la couvre et que chaque rôle marqué refusé dans le cahier ou dans la matrice
reçoit un refus explicite sur cette même opération.

**Acceptance Scenarios**:

1. **Given** la ligne MP-04 (passer commande), **When** un visiteur ou un vendeur tente l'opération
   correspondante, **Then** le contrat la refuse (rôle non autorisé) ; **When** un client connecté la
   tente, **Then** le contrat l'autorise.
2. **Given** la ligne MP-13 (saisir collecte, livraison, encaissement), **When** un client, un vendeur,
   ou toute requête non authentifiée la tente, **Then** le contrat la refuse systématiquement (admin
   seul, RG-029, D38).
3. **Given** une capacité dérivée absente de §5 (ex. MX-03 notifications internes), **When** un visiteur
   y accède, **Then** le contrat la refuse (visiteur non autorisé) ; **When** le titulaire du compte y
   accède, **Then** le contrat l'autorise sur ses propres notifications seulement.

---

### Edge Cases

- Une requête de la société de livraison : aucune route ne lui est exposée, par construction (D38) ;
  elle n'a ni compte ni jeton.
- Une tentative de transition d'état interdite depuis l'état courant (ex. annuler une commande déjà
  « En collecte », déclarer prête une sous-commande déjà refusée) : refusée explicitement, de façon
  distincte d'une ressource introuvable ou d'un rôle refusé.
- Une tentative d'accéder à une action réservée mais non disponible (U-01, U-02 — voir « Capacités hors
  matrice §5 et actions réservées ») : distinguée d'une action interdite par rôle — le point d'accès
  existe au contrat mais signale son indisponibilité tant que la décision ou la mise à jour UML
  correspondante n'a pas eu lieu.
- Un montant transmis sous une forme qui admettrait un écart d'arrondi (nombre flottant binaire) : non
  conforme au contrat, quelle que soit l'opération.
- Une valeur d'énumération absente du schéma T-002, ou orthographiée différemment : non conforme au
  contrat.
- Un vendeur A qui devine l'identifiant d'une ressource du vendeur B (boutique, produit, sous-commande,
  montant, retour) : reçoit le même refus qu'une ressource inexistante, sans aucune distinction
  observable.
- Un code d'erreur absent du catalogue fermé, ou associé à plus d'un code HTTP selon l'opération qui
  l'émet : non conforme au contrat.

## Requirements *(mandatory)*

### Couverture des cas d'utilisation (UC-001 à UC-023)

- **FR-001**: Le contrat DOIT exposer, pour chacun des 23 cas d'utilisation approuvés (UC-001 à
  UC-023), au moins un point d'accès, rattaché à l'un des modules M01–M11 du cahier §9 ou au socle
  transverse (authentification, photos, journal d'audit, paramètres).
- **FR-002**: Chaque point d'accès DOIT porter la référence du ou des cas d'utilisation et de la ou des
  lignes de la matrice des permissions qu'il sert, afin qu'une revue puisse vérifier la couverture sans
  relecture manuelle de l'ensemble du contrat.

### Application de la matrice des permissions du cahier §5 (17 lignes) pour les quatre rôles

- **FR-003**: Pour chacune des 17 lignes de la matrice des permissions du cahier §5, le contrat DOIT
  exposer, pour chaque rôle marqué autorisé sur cette ligne, au moins une opération qui l'exécute ; pour
  chaque rôle marqué refusé sur cette même ligne, cette même capacité DOIT être explicitement refusée.
- **FR-004**: La société de livraison, acteur externe sans compte ni jeton, NE DOIT disposer d'aucun
  point d'accès au contrat, pour aucune des 17 lignes ni pour aucune capacité dérivée (D38, ENF-007,
  Constitution Principe V).
- **FR-005**: Les capacités nécessaires au fonctionnement de la Plateforme mais absentes de la matrice
  du cahier §5 DOIVENT être recensées séparément de ses 17 lignes, chacune avec sa justification et sa
  source — voir « Capacités hors matrice §5 et actions réservées ». Ces capacités couvrent au moins :
  l'inscription, la connexion, la déconnexion et la consultation de son propre compte ; la consultation
  des référentiels publics nécessaires aux formulaires d'inscription et de commande ; la consultation de
  ses notifications internes ; la supervision administrative transverse ; la gestion des paramètres
  métier.

### Cloisonnement par titulaire et non-divulgation

- **FR-006**: Toute opération portant sur une ressource dont un vendeur ou un client est titulaire
  (boutique, produits, sous-commandes, montants, retours, commandes, panier, avis, notifications) DOIT
  vérifier la propriété à chaque requête, indépendamment du contrôle de rôle (Constitution Principe V,
  ENF-007).
- **FR-007**: Une tentative d'un titulaire sur une ressource appartenant à un autre titulaire du même
  rôle DOIT être refusée sans révéler l'existence de cette ressource. Une tentative d'un rôle non
  autorisé pour la capacité elle-même DOIT recevoir un refus distinct de celui-ci, qui n'a pas besoin de
  masquer l'existence de la ressource.

### Documentation contractuelle de chaque point d'accès

- **FR-008**: Chaque point d'accès DOIT être accompagné d'au moins un exemple de requête, un exemple de
  réponse de succès et un exemple de réponse d'erreur, chacun associé à son code HTTP.
- **FR-009**: Tout code d'erreur utilisé par un exemple DOIT appartenir à un catalogue fermé et stable
  de codes d'erreur ; un même code DOIT toujours correspondre au même code HTTP, quelle que soit
  l'opération qui l'émet.
- **FR-010**: Chaque exemple (requête, succès, erreur) DOIT être valide contre la structure de données
  qu'il illustre, afin qu'un exemple ne puisse pas devenir incohérent avec le reste du contrat au fil de
  son évolution sans que cela soit détecté.

### Exactitude des montants, des énumérations et des transitions d'état

- **FR-011**: Toute valeur monétaire échangée par le contrat, en entrée comme en sortie, DOIT être
  représentée sous une forme décimale exacte, jamais sous une forme qui admette un écart d'arrondi
  (Constitution Principe IV).
- **FR-012**: Toute énumération exposée par le contrat (statuts, motifs, modes, rôles) DOIT reprendre
  exactement les valeurs fermées définies par le schéma de données physique (T-002), sans renommage ni
  valeur supplémentaire absente de ce schéma.
- **FR-013**: Les transitions de statut de commande, de sous-commande, de retour et de montant vendeur
  exposées par le contrat DOIVENT correspondre aux transitions des machines à états approuvées
  (STATE-001 à STATE-004) ; aucune transition non modélisée n'est exposée sans être explicitement
  réservée (voir FR-015).
- **FR-014**: Une tentative de transition interdite depuis l'état courant d'une ressource (ex. annuler
  une commande déjà « En collecte ») DOIT être refusée explicitement, avec une indication distincte
  d'une erreur de rôle, de propriété ou de validation de données.

### Actions réservées mais non disponibles (écarts UML U-01, U-02)

- **FR-015**: Les actions que les machines à états approuvées ne modélisent pas encore — la décision de
  l'administrateur à défaut de vérification du vendeur dans le délai (U-01, STATE-003) et l'annulation
  d'une commande par l'administrateur (U-02, STATE-001) — DOIVENT être réservées dans le contrat (point
  d'accès défini) mais signalées comme non disponibles jusqu'à la décision du porteur ou la mise à jour
  UML correspondante ; une tentative d'y accéder DOIT recevoir une réponse qui la distingue d'un refus
  par rôle ou par propriété.

### Points ouverts (clarifications, maximum trois)

- **FR-016**: Le contrat DOIT prévoir la gestion d'un panier par un visiteur non connecté, rattaché à
  son compte à la connexion ou à l'inscription [NEEDS CLARIFICATION: panier visiteur — le cahier §5
  marque cette capacité HYPOTHÈSE (H-01) ; en l'absence de confirmation du porteur, le contrat retient
  l'hypothèse la plus proche du cahier (panier visiteur autorisé, fusionné au compte à la connexion)
  plutôt que de refuser cette capacité par défaut].
- **FR-017**: Le périmètre exact de la supervision administrative transverse (consultation de vendeurs,
  produits, commandes, retours, montants et journal d'audit, au-delà des actions déjà couvertes par les
  autres lignes de la matrice) [NEEDS CLARIFICATION: périmètre de supervision — F013 et UC-023
  confirment le besoin sans en fixer l'étendue exacte ; en l'absence de réponse, le contrat retient le
  périmètre le plus large compatible avec les ressources déjà modélisées par les diagrammes de classes
  approuvés, sans ajouter de nouvelle capacité non modélisée].
- **FR-018**: La levée d'une mesure de modération (réafficher un produit masqué, réafficher un avis
  masqué, réactiver un vendeur suspendu) [NEEDS CLARIFICATION: levée de modération — le cahier décrit la
  mesure (RG-015) mais jamais sa levée ; en l'absence de réponse, le contrat réserve l'opération inverse,
  symétrique à celle qui impose la mesure, au même rôle administrateur, comme hypothèse la plus proche
  du principe de modération déjà confirmé].

## Capacités hors matrice §5 et actions réservées

**Capacités hors matrice §5** (5 capacités dérivées, nécessaires au fonctionnement de l'API mais
absentes des 17 lignes de la matrice du cahier §5) :

| ID | Capacité | Rôles concernés | Justification | Source |
|---|---|---|---|---|
| MX-01 | S'inscrire, se connecter, se déconnecter, consulter son compte | Visiteur (inscription) ; titulaire (déconnexion, compte) | Aucune capacité de compte n'apparaît dans la matrice §5, qui ne décrit que les capacités métier une fois authentifié | F001, F002, UC-004, UC-010 |
| MX-02 | Consulter les référentiels publics (villes desservies, communes vendeurs) | Tous | Nécessaire aux formulaires d'inscription vendeur (RG-023) et de commande (RG-001) avant que le visiteur ait choisi un rôle | F002, F007 |
| MX-03 | Consulter ses notifications internes | Client, vendeur, administrateur (titulaire) | F014 confirme un besoin de notifications essentielles, sans le faire figurer dans la matrice des capacités §5 | F014 |
| MX-04 | Superviser vendeurs, produits, commandes, retours, montants et journal d'audit | Administrateur | F013 et UC-023 confirment un besoin de supervision transverse ; son périmètre exact reste ouvert (FR-017) | F013, UC-023, ENF-008 |
| MX-05 | Gérer les paramètres métier | Administrateur | Les valeurs non tranchées par le cahier (délais, montants de frais) sont traitées comme des paramètres consultés et modifiés par l'administrateur, pas comme des constantes | HYPOTHÈSE H-08 du plan |

**Actions réservées mais non disponibles** (écarts entre le cahier/UML et les machines à états
approuvées, signalés par Blueprint dans le plan de Compass) :

| ID | Action réservée | Diagramme concerné | Raison du blocage | Destinataire |
|---|---|---|---|---|
| U-01 | Décision de l'administrateur si le vendeur ne vérifie pas un produit retourné dans le délai | STATE-003 (retour) | Le délai de vérification du vendeur (Q44) n'est pas tranché, et STATE-003 ne dessine aucune transition « après délai » faute de cible définie | @user (décision Q44), puis Blueprint (mise à jour de STATE-003) |
| U-02 | Annulation d'une commande par l'administrateur | STATE-001 (commande) | F013 prévoit que l'administrateur décide du sort des sous-commandes d'un vendeur suspendu, mais STATE-001 ne dessine aucune transition d'annulation administrative | Blueprint (modélisation de la transition dans STATE-001) |

## Key Entities *(include if feature involves data)*

Ressources exposées par le contrat, correspondant aux entités du schéma T-002 (`data-model.md`), sans
en redéfinir la structure physique :

- **Compte** (visiteur implicite, client, vendeur, administrateur) : identité d'authentification et
  rôle unique porté par chaque requête (socle T-001).
- **Boutique / Produit** : ressources dont un vendeur est titulaire (MP-11) ; visibles publiquement si
  publiées, non masquées et le vendeur actif (RG-006).
- **Panier** : ressource du client connecté (MP-03), et du visiteur si FR-016 est confirmé.
- **Commande / SousCommande** : commande du client (titulaire), répartie en une sous-commande par
  vendeur (titulaire de la sienne) ; statuts pilotés par STATE-001/STATE-002.
- **Retour** : demande du client (titulaire) sur une ligne de commande reçue, vérifiée par le vendeur
  titulaire du produit, arbitrée par l'administrateur en cas de litige (MP-06, MP-07, MP-08).
- **MontantVendeur** : montants du vendeur (titulaire), également consultables par l'administrateur
  (MP-14) ; reversement enregistré par l'administrateur seul (MP-15).
- **Avis** : avis du client (titulaire) sur un produit reçu (MP-10), modérable par l'administrateur
  (MP-16).
- **Notification** : notifications internes du titulaire du compte (MX-03).
- **Référentiel public** (villes desservies, communes vendeurs, catégories) : lecture publique, écriture
  réservée à l'administrateur (MX-02, MP-17).
- **Paramètre métier** et **Journal d'audit** : lecture et, pour les paramètres, écriture réservées à
  l'administrateur (MX-04, MX-05, ENF-008).

**Hors périmètre de cette spécification** : la structure physique de ces ressources (tables, colonnes,
contraintes), déjà fixée par T-002 (`specs/002-schema-donnees/data-model.md`) ; le détail technique de
chaque point d'accès (schémas JSON, chemins, méthodes), déjà proposé dans `contracts/openapi.yaml`,
`contracts/api-reference.md` et `contracts/authorization-matrix.yaml` (statut Proposé, en attente de
validation par @user au point de contrôle CP-1).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 23/23 cas d'utilisation (UC-001 à UC-023) ont au moins un point d'accès rattaché à un
  module ou au socle.
- **SC-002**: 17/17 lignes de la matrice des permissions du cahier §5 sont couvertes par au moins une
  opération pour chacun de leurs rôles autorisés, avec un refus explicite pour chacun de leurs rôles
  refusés.
- **SC-003**: 0 opération du contrat n'ouvre un rôle marqué refusé par ses lignes de matrice ; 0 point
  d'accès n'est exposé à la société de livraison.
- **SC-004**: 100 % des opérations ont un exemple de requête et des exemples de réponse de succès et
  d'erreur valides contre leur structure de données.
- **SC-005**: 100 % des codes d'erreur utilisés appartiennent au catalogue fermé et portent chacun un
  unique code HTTP associé, quelle que soit l'opération qui les émet.
- **SC-006**: 100 % des énumérations exposées par le contrat ont des valeurs identiques à celles du
  schéma T-002.
- **SC-007**: 100 % des tentatives de transition interdite depuis l'état courant d'une commande, d'une
  sous-commande, d'un retour ou d'un montant vendeur sont refusées explicitement, de façon distincte
  d'un refus de rôle ou de propriété.
- **SC-008**: Ce contrat et sa matrice d'autorisations sont validés par @user au point de contrôle CP-1
  avant le démarrage de l'implémentation (T-003 du plan).

## Assumptions

- Les décisions techniques déjà proposées pour cette tâche (ADR-016 à ADR-020 de
  `docs/architecture/DECISIONS.md`, statut « Proposé ») sont tenues pour acquises par ce document :
  codes et clés en anglais, messages en français (ADR-016) ; 403 pour un rôle refusé et 404 pour une
  ressource d'un autre titulaire (ADR-017) ; montants en chaîne décimale (ADR-018) ; panier visiteur
  identifié par un jeton opaque (ADR-019, dépend de FR-016) ; transitions d'état exposées en
  sous-ressource verbale (ADR-020).
- Les artefacts déjà produits pour cette tâche (`contracts/openapi.yaml`, `contracts/api-reference.md`,
  `contracts/authorization-matrix.yaml`/`.md`, `contracts/error-codes.md`, statut « Proposé ») sont
  l'expression technique de ce document ; il n'en répète pas le détail (points d'accès, schémas JSON) et
  se limite au QUOI et au POURQUOI.
- Le catalogue d'erreurs comprend 24 codes stables, chacun rattaché à un unique code HTTP
  (`contracts/error-codes.md`).
- Pour les trois points ouverts (FR-016 à FR-018), l'hypothèse retenue dans l'intervalle est celle déjà
  portée par `contracts/authorization-matrix.yaml` (statut `allow_hyp` pour le panier visiteur et pour
  la supervision administrative) ou par la symétrie de la mesure de modération déjà confirmée (levée) ;
  aucune de ces hypothèses n'est développée avant confirmation du porteur au point de contrôle CP-1,
  conformément à la consigne du cahier (« les éléments SUGGESTION ne doivent pas être développés sans
  son accord »).
- L'outil `validation/check_contract.py` de ce dossier (outil de documentation, pas un test applicatif)
  vérifie déjà mécaniquement SC-001 (C2), SC-002/SC-003 (C3/C4), SC-004 (C5/C6), SC-005 (C7) et SC-006
  (C8) ; ce document ne redéfinit pas cet outil.
