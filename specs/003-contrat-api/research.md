# Research — Contrat d'API et matrice d'autorisations (T-003)

**Feature** : `003-contrat-api` | **Date** : 2026-10-14

**Portée de ce document** : il consolide, sous forme Décision / Raison / Alternatives envisagées /
Conséquences / Statut, les arbitrages techniques de T-003 déjà actés en ADR-016 à ADR-020
(`docs/architecture/DECISIONS.md`, statut « Proposé »). Il ne reproduit ni le détail des 101 opérations
ni celui de la matrice, qui restent dans `contracts/openapi.yaml` et `contracts/authorization-matrix.yaml`
(sources de référence) ; il explique seulement **pourquoi** chaque arbitrage a été retenu plutôt qu'une
autre option, documente les trois hypothèses propres à T-003 (H-T03-01 à H-T03-03, distinctes des trois
`[NEEDS CLARIFICATION]` de `spec.md` qu'elles traduisent en défaut concret) et l'écart E-T03-01, pour
qu'un futur agent ou le porteur du projet puisse rejuger ces choix sans relire tout le contrat.

---

## R11 — Langue et forme du contrat (ADR-016)

- **Décision** : clés JSON, paramètres de requête et `error.code` en anglais `snake_case` ;
  `error.message` en français ; pagination `page`/`per_page` ; enveloppes `{data, meta}` et
  `{error:{code,message,details}}` de T-001 conservées.
- **Raison** : Constitution IX (contrats d'API en anglais, messages utilisateurs en français) ; le
  schéma T-002 est déjà en anglais `snake_case` (ADR-010) — un contrat en français aurait créé une
  discontinuité de langue entre la base et l'API consommée par le même code.
- **Alternatives envisagées** : tout en français, comme les exemples provisoires de T-001
  (`acces_refuse`, `par_page`) — rejeté, contraire à la Constitution IX et au schéma T-002 ; mélange
  anglais/français selon le module — rejeté, incohérent pour le frontend qui doit tester `code` par
  égalité stricte.
- **Conséquences** : les exemples français de T-001 (`format-erreur.md`, `pagination.md`) sont remplacés
  de fait par ce contrat (`acces_refuse` → `forbidden`, `ressource_introuvable` → `not_found`,
  `validation_echouee` → `validation_failed`, `fichier_refuse` → `file_rejected`, `par_page` →
  `per_page`) sans réécrire les fichiers T-001 eux-mêmes (statut Proposé, en attente de @user).
- **Statut** : ADR-016, **Proposé**.

## R12 — 403 pour le rôle, 404 pour la propriété (ADR-017)

- **Décision** : un rôle non autorisé pour une capacité reçoit `403 forbidden` ; un titulaire qui tente
  d'accéder à la ressource d'un autre titulaire du même rôle reçoit `404 not_found`, indistinct d'une
  ressource inexistante. Chaque opération porte `x-roles`, `x-ownership` et `x-matrix-rows` ; les routes
  sont séparées par espace (public, `/seller`, `/admin`).
- **Raison** : Constitution V (cloisonnement par rôle testé) et ENF-007 ; l'inscription vendeur est libre
  et sans validation préalable (D9, RG-004), donc un vendeur concurrent peut deviner l'identifiant d'une
  ressource d'un autre vendeur — un `403` sur une ressource existante d'un concurrent confirmerait son
  existence, ce que FR-007 interdit explicitement.
- **Alternatives envisagées** : `403` dans les deux cas — rejeté, révèle l'existence des commandes,
  retours et montants d'un concurrent ; `404` dans les deux cas — rejeté, masquerait au frontend une
  erreur de rôle qu'il doit pouvoir distinguer (ex. proposer une connexion différente plutôt qu'un
  message « introuvable »).
- **Conséquences** : les tests de cloisonnement (T-066) dérivent un cas autorisé et un cas interdit par
  ligne directement de `authorization-matrix.yaml`, sans écrire une logique d'autorisation ad hoc par
  point d'accès (User Story 4 de `spec.md`) ; vérifié mécaniquement par `check_contract.py` C3/C4
  (17/17 lignes MP, 5/5 MX, 0 ouverture de rôle refusé) ; aucune route n'est exposée à la société de
  livraison (D38).
- **Statut** : ADR-017, **Proposé**.

## R13 — Montants en chaîne décimale dans le JSON (ADR-018)

- **Décision** : toute valeur monétaire, en entrée comme en sortie, est une chaîne décimale exacte
  (ex. `"220.00"`, motif `^-?\d{1,8}\.\d{2}$`), devise MAD implicite.
- **Raison** : Constitution IV (montants exacts) ; JavaScript (frontend React) n'a pas de type décimal
  exact — un nombre JSON pour `DECIMAL(10,2)` (ADR-011) admettrait un arrondi binaire silencieux au
  passage navigateur.
- **Alternatives envisagées** : nombre JSON — rejeté, arrondi binaire possible côté client ; entier en
  centimes — rejeté, diverge de l'affichage et du schéma T-002 sans bénéfice d'exactitude supplémentaire
  (`DECIMAL(10,2)` est déjà exact côté base).
- **Conséquences** : le frontend affiche les montants renvoyés par l'API (ex. `previewOrder`) sans jamais
  recalculer un total qui fasse foi ; toute opération financière reste strictement celle du service
  propriétaire désigné (T-027, T-036, T-043, Constitution III).
- **Statut** : ADR-018, **Proposé**.

## R14 — Transitions d'état en route verbale dédiée (ADR-020)

- **Décision** : chaque transition d'état approuvée (STATE-001..004) a sa propre route `POST` sur
  sous-ressource verbale (`/orders/{id}/cancel`, `/sub-orders/{id}/accept`, `/sub-orders/{id}/ready`,
  etc.) plutôt qu'un `PATCH {status: …}` générique. Une transition impossible depuis l'état courant
  renvoie `409 invalid_transition` avec `details.current_status` ; une transition non modélisée par
  l'UML (U-01, U-02) est réservée au contrat et renvoie `501 feature_blocked` avec `x-blocked-by`.
- **Raison** : Constitution III (une seule porte par état métier) — un `PATCH` générique laisserait le
  client choisir n'importe quel statut cible, dispersant la validation hors du service propriétaire ;
  une route par transition nommée rend chaque appel directement traçable à une flèche d'un diagramme
  d'états, et donc à une entrée du journal d'audit (`from_status`/`to_status`, ENF-008).
- **Alternatives envisagées** : `PATCH` générique sur le statut — rejeté, viole Constitution III en
  laissant deviner les transitions possibles côté client ; endpoint RPC unique `/transitions` — rejeté,
  masquerait dans un seul contrôleur fourre-tout la correspondance avec STATE-001..004 que la revue doit
  pouvoir vérifier opération par opération.
- **Conséquences** : U-01 (`adminInspectReturn` après défaut de vérification vendeur, lié à Q44) et U-02
  (`adminCancelOrder`) existent au contrat (schémas, exemples) mais sont inutilisables jusqu'à la
  décision du porteur (U-01) ou la mise à jour de STATE-001 par Blueprint (U-02) — voir
  `spec.md` § « Capacités hors matrice §5 et actions réservées ».
- **Statut** : ADR-020, **Proposé**.

---

## Hypothèses propres à T-003

Ces trois hypothèses traduisent en valeur par défaut concrète les trois `[NEEDS CLARIFICATION]` de
`spec.md` (FR-016 à FR-018) ; elles sont déjà portées par `contracts/authorization-matrix.yaml`
(statut `allow_hyp`) et ne sont pas développées avant validation de @user au point de contrôle CP-1
(Constitution I, SC-008).

### H-T03-01 — Panier visiteur identifié par un jeton opaque (ADR-019)

- **Hypothèse retenue** : un visiteur non connecté gère un panier via un jeton opaque émis par l'API au
  premier ajout et renvoyé en en-tête `X-Cart-Token` à chaque requête suivante ; à la connexion ou à
  l'inscription, ce panier est fusionné dans celui du client (CA-F001-3).
- **Pourquoi cette hypothèse plutôt qu'une autre** : §5 du cahier marque la capacité panier visiteur
  HYPOTHÈSE (H-01) sans trancher son mécanisme ; un cookie de session est exclu par ADR-006 (jeton
  porteur, pas de session serveur) ; un panier local au seul navigateur laisserait le stock non vérifié
  côté serveur avant la connexion (CA-F003-2) — l'en-tête opaque est l'option la plus proche du cahier
  qui reste vérifiable côté serveur sans session.
- **Donnée associée** : `carts.guest_token_hash` (T-002) stocke un hachage SHA-256, jamais le jeton en
  clair — aucune valeur de secret n'est committée (Constitution VIII).
- **Si @user refuse H-01 au CP-1** : les opérations panier (`getCart`, `addCartItem`, `updateCartItem`,
  `removeCartItem`) passent au rôle client seul ; aucun autre point du contrat n'est affecté (MP-03
  perd sa colonne Visiteur, ADR-019 devient sans objet).

### H-T03-02 — Vendeur suspendu : lecture conservée, écriture refusée

- **Hypothèse retenue** : un vendeur suspendu (RG-015) garde l'accès en lecture à ses propres ressources
  (boutique, produits, sous-commandes, montants) mais toute action d'écriture lui est refusée par
  `403 account_suspended`, distinct du refus de rôle générique `forbidden`.
- **Pourquoi cette hypothèse** : le cahier (RG-015) décrit la suspension comme une mesure de modération
  qui retire la visibilité publique du vendeur, sans préciser si le vendeur suspendu perd tout accès à
  son propre tableau de bord ; lui retirer la lecture interdirait de consulter ses montants dus
  (MP-14), ce que RG-015 ne demande pas — la lecture seule est l'option la plus proche du texte, qui ne
  bloque que ce que la mesure vise réellement (la vente).
- **Conséquences** : `account_suspended` (catalogue `error-codes.md`) est un code distinct de `forbidden`
  pour que le frontend affiche un message de suspension plutôt qu'un refus de rôle générique ; cette
  hypothèse n'est pas un des trois `[NEEDS CLARIFICATION]` de `spec.md` (elle précise une mesure déjà
  confirmée par RG-015, elle n'ouvre pas de capacité absente du cahier) mais reste une HYPOTHÈSE de
  modélisation à signaler au porteur du projet si elle le surprend.

### H-T03-03 — Levée d'une mesure de modération symétrique à son imposition

- **Hypothèse retenue** : chaque mesure de modération a son opération inverse, réservée au même rôle
  administrateur : `adminUnhideProduct` (symétrique de `adminHideProduct`), `adminReactivateSeller`
  (symétrique de `adminSuspendSeller`), `adminUnhideReview` (symétrique de `adminHideReview`).
- **Pourquoi cette hypothèse** : le cahier (RG-015) décrit la mesure d'imposition mais jamais sa levée ;
  l'option la plus proche du principe de modération déjà confirmé est l'opération inverse au même rôle,
  plutôt qu'un nouveau rôle de validation ou qu'une levée automatique après délai (qu'aucune exigence du
  cahier ne mentionne).
- **Conséquences** : si @user tranche différemment au CP-1 (ex. délai automatique, rôle distinct), seules
  ces trois opérations et leurs lignes de matrice (MP-11, MP-16) sont à revoir ; le reste du contrat n'en
  dépend pas.

---

## Écart E-T03-01 — Deux énumérations internes de T-002 non exposées par le contrat

- **Constat** : le contrôle C8 de `validation/check_contract.py` (`.specify/logs/T-003-validation.log`)
  signale que deux énumérations `CHECK` du schéma T-002 n'apparaissent dans aucun schéma de
  `openapi.yaml` : `photo_files.check_status` (`accepted`, `rejected`) et `photo_variants.variant`
  (`original`, `mobile`).
- **Justification** : `photo_files.check_status` est un état de traitement interne du contrôle de fichier
  (FR-040 du socle T-001) — un fichier refusé ne devient jamais visible : l'upload renvoie directement
  `422 file_rejected` au moment du refus, sans qu'aucune opération de lecture n'ait jamais à distinguer
  `accepted` de `rejected` après coup. `photo_variants.variant` distingue les fichiers générés
  (`original`/`mobile`) pour le stockage interne ; l'API n'expose que des URL de variante déjà
  résolues (ex. `photo_url`, `photo_url_mobile`), jamais le nom de variante lui-même.
- **Portée** : cet écart ne retire aucune capacité du cahier ni aucune ligne de la matrice §5 — il
  documente pourquoi deux colonnes internes de T-002 restent des détails d'implémentation du socle
  (T-001, module `StockagePhotos`) plutôt que des valeurs contractuelles, conformément à SC-006 (« 100 %
  des énumérations **exposées** par le contrat » — ces deux-là ne le sont jamais, par construction).
- **Destinataire** : aucune action requise ; à surveiller seulement si une future tâche souhaitait un
  jour exposer l'état de contrôle d'un fichier (ex. tableau de bord de modération des photos), ce qui
  exigerait une nouvelle revue de ce même écart.
