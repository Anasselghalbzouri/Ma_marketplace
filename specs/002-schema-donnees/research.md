# Research — Schéma de données physique (T-002)

**Feature** : `002-schema-donnees` | **Date** : 2026-10-14

**Portée de ce document** : il consolide, sous forme Décision / Raison / Alternatives envisagées /
Conséquences / Statut, les arbitrages techniques de T-002 déjà actés en ADR-010 à ADR-015
(`docs/architecture/DECISIONS.md`, statut « Proposé »). Il ne reproduit ni la correspondance UML → tables
ni le détail des contraintes, qui restent dans `data-model.md` (sources de référence, §1 à §9) ; il
explique seulement **pourquoi** chaque arbitrage a été retenu plutôt qu'une autre option, pour qu'un
futur agent ou le porteur du projet puisse rejuger ces choix sans relire tout le DDL.

---

## R7 — Conventions de nommage et de clés (ADR-010)

- **Décision** : noms anglais `snake_case`, tables au pluriel, clé `id BIGINT UNSIGNED AUTO_INCREMENT`,
  clé étrangère `<singulier>_id` ; les numéros lisibles par l'utilisateur passent par une colonne dédiée
  (`orders.reference`), jamais par `id`.
- **Raison** : Constitution Principe IX (code en anglais) ; Laravel 11 (ADR-001) attend nativement ce
  format (conventions Eloquent, pluriel de table, clé `id`) — s'en écarter aurait exigé de configurer
  manuellement chaque modèle sans bénéfice métier.
- **Alternatives envisagées** : noms français (rejeté — contraire à la Constitution IX, et les accents
  sont interdits dans les identifiants SQL) ; clés UUID/ULID partout (rejeté — index plus lourds, aucun
  besoin d'identifiant global exposé en V1, le besoin de non-devinabilité est couvert par `orders.reference`
  seule).
- **Conséquences** : la correspondance français (UML) ↔ anglais (schéma) doit rester à jour dans
  `data-model.md` §2 ; `RETURN` étant un mot réservé SQL, l'entité Retour devient `product_returns`.
- **Statut** : ADR-010, **Proposé** — révisable par le porteur du projet.

## R8 — Montants en `DECIMAL(10,2)` MAD (ADR-011)

- **Décision** : tout montant monétaire est stocké en `DECIMAL(10,2)`, jamais en `FLOAT`/`DOUBLE` ; la
  devise n'est pas stockée en V1 (MAD unique, RG-007).
- **Raison** : Constitution Principe IV (argent exact) ; RG-007/012/018/021/022 impliquent des
  additions/soustractions de montants vendeurs qui doivent rester exactes au centime (ex. CA-F011-5 :
  500 − 80 = 420, vérifié sans écart d'arrondi en §9 de `data-model.md`).
- **Alternatives envisagées** : entier en centimes (rejeté — exact mais impose une conversion partout
  dans le code et dans les requêtes de lecture humaine, sans bénéfice puisque `DECIMAL(10,2)` est déjà
  exact en MySQL) ; `FLOAT`/`DOUBLE` (rejeté — arrondis binaires interdits pour l'argent, Constitution
  Principe IV).
- **Conséquences** : côté PHP (T-005 et suivantes), les montants doivent être manipulés en chaîne ou via
  une bibliothèque décimale, jamais convertis en `float` à un moment de calcul ; une colonne devise sera
  ajoutée seulement si la livraison internationale (§21 du cahier) est un jour retenue.
- **Statut** : ADR-011, **Proposé**.

## R9 — Énumérations en `VARCHAR` + `CHECK` plutôt qu'`ENUM` MySQL (ADR-012)

- **Décision** : chaque énumération UML devient une colonne `VARCHAR(32)` contrainte par un `CHECK`
  nommé (`ck_<table>_<colonne>`), valeurs en anglais `snake_case`, miroir d'une enum PHP « backed » côté
  application.
- **Raison** : plusieurs énumérations restent HYPOTHÈSE au cahier (étapes de cycle de vie §7, H-03) et
  peuvent évoluer ; MySQL ≥ 8.0.16 applique les `CHECK` nativement (ADR-002), ce qui donne une liste
  fermée vérifiable par simple essai d'écriture (User Story 2 de `spec.md`), sans dépendre du code
  applicatif.
- **Alternatives envisagées** : type `ENUM` natif MySQL (rejeté — ajouter une valeur réécrit la colonne
  via `ALTER TABLE`, et l'ordre des valeurs est implicite et piégeux pour un tri) ; table de référence
  par énumération, avec clé étrangère (rejeté — neuf jointures supplémentaires pour des listes fermées et
  stables, sans besoin de métadonnée associée à chaque valeur).
- **Conséquences** : ajouter une valeur à une énumération = une migration qui remplace la contrainte
  `CHECK` (rapide, sans réécriture des lignes existantes) ; la base refuse toute valeur hors liste,
  vérifié par `validation/probe_constraints.py` (23/23 violations refusées, `data-model.md` §9).
- **Statut** : ADR-012, **Proposé**.

## R10 — Partage des règles entre base et services (ADR-013)

- **Décision** : la base garantit uniquement les invariants statiques d'une ligne (contraintes `CHECK`,
  `UNIQUE`, clés étrangères) ; les règles qui dépendent du temps ou d'autres lignes (RG-006 visibilité,
  RG-019 délai de retour, RG-024 retenue, CA-F006-2 quantité ≤ stock) et toutes les transitions d'état
  restent dans les services uniques désignés par le plan (T-027 Commande/SousCommande, T-036
  MontantVendeur, T-043 Retour). Aucun déclencheur SQL en V1.
- **Raison** : Constitution Principe III (une seule porte par état métier) — un déclencheur SQL
  contournerait cette porte en cachant une règle métier hors du service propriétaire, et serait difficile
  à tester à horloge simulée (cohérence avec ADR-003 du socle T-001, qui impose l'horloge simulée pour
  les traitements planifiés T-034/T-050/T-053/T-054).
- **Alternatives envisagées** : tout en déclencheurs SQL (rejeté — logique cachée hors des services
  uniques, intestable à horloge simulée, viole Constitution Principe III) ; tout dans les services, sans
  aucune garantie en base (rejeté — une écriture directe, un bug ou une migration de données pourrait
  alors corrompre un prix négatif ou un statut incohérent sans qu'aucune couche ne le refuse,
  contraire à Constitution Principe IV).
- **Conséquences** : la table « garanti par la base / garanti par le service » de `data-model.md` §5 fait
  foi pour les tests que T-005 et les tâches Backend concernées devront écrire (Constitution Principe
  VI) ; les index de performance (R11 ci-dessous) compensent l'absence de garantie en base pour ces
  règles dynamiques.
- **Statut** : ADR-013, **Proposé**.

## R11 — Index pour le catalogue (ENF-004) et les traitements planifiés

- **Décision** : des index dédiés couvrent (a) le catalogue public visible et sa recherche
  (`ix_products_visible`, `ix_products_category_visible`, `FULLTEXT ft_products_search`) et (b) les quatre
  traitements planifiés du plan — échéance de réponse vendeur (`ix_sub_orders_deadline`, T-034), fin de
  retenue des montants (`ix_seller_amounts_release`, T-053), alerte de délai légal à 12 jours
  (`ix_product_returns_status`, T-050) et reversement hebdomadaire par vendeur
  (`ix_seller_amounts_seller_status`, `ix_deductions_pending`, T-054) — détail complet dans
  `data-model.md` §6.
- **Raison** : ces règles sont dynamiques (ADR-013, R10 ci-dessus) et donc non garanties par une
  contrainte en base ; sans structure de recherche dédiée, leur coût croît avec le volume de commandes et
  de produits et romprait le budget ENF-004 (catalogue affiché en moins de 3 s pour 95 % des
  consultations) ou ferait dériver les traitements planifiés vers un parcours complet de l'historique.
- **Alternatives envisagées** : colonnes dérivées matérialisées (ex. `is_visible` stockée) mises à jour
  par déclencheur (rejeté — réintroduirait un déclencheur SQL, contraire à R10/ADR-013, et risquerait une
  désynchronisation si l'écriture directe oublie de la recalculer) ; aucun index dédié, filtrage côté
  application sur un `SELECT *` (rejeté — dégrade immédiatement ENF-004 au-delà de quelques centaines de
  produits, et un parcours complet des commandes historiques à chaque exécution planifiée).
- **Conséquences** : `seller_amounts.hold_until` est matérialisée à la création (figée à `received_at` +
  délai) plutôt que recalculée à chaque lecture, pour que l'index (`status`, `hold_until`) reste exact
  même si le paramètre de délai change ensuite (écart E-06 de `data-model.md` §7) ; toutes les clés
  étrangères sont indexées de toute façon (InnoDB l'exige).
- **Statut** : conséquence directe d'ADR-013 et d'ENF-004 ; pas un ADR séparé — documentée ici et dans
  `data-model.md` §6.

## R12 — Chiffrement applicatif des données sensibles (ADR-014) et audit en ajout seul (ADR-015)

- **Décision** : `sellers.bank_details` et `product_returns.refund_details` sont chiffrées par
  l'application (cast chiffré, clé = variable d'environnement `APP_KEY`, jamais dans le dépôt) ;
  `audit_entries` est en ajout seul, garanti par les droits MySQL eux-mêmes — l'utilisateur applicatif
  (`DB_USERNAME`) n'a que `SELECT, INSERT` sur cette table, un utilisateur distinct (`DB_MIGRATION_USERNAME`)
  exécute les migrations.
- **Raison** : FR-055 (socle T-001) et §19 du cahier exigent que les coordonnées bancaires et de
  remboursement restent illisibles par quiconque d'autre que l'administrateur et le titulaire (Constitution
  Principe VIII) ; ENF-008 et ADR-008 (socle T-001) exigent que le journal financier soit immuable
  **indépendamment du code applicatif** — un bug ou un accès direct à la base ne doit pas pouvoir
  corrompre l'historique (Constitution Principe IV).
- **Alternatives envisagées**, pour le chiffrement : chiffrement du disque seul (rejeté — ne protège ni
  les sauvegardes logiques ni les requêtes directes à la base, donc ne couvre pas le cloisonnement entre
  vendeurs/clients) ; aucun chiffrement (rejeté — contraire à la minimisation et à FR-055). Pour l'audit :
  déclencheurs `BEFORE UPDATE/DELETE` levant une erreur (rejeté — réintroduit un déclencheur SQL, R10) ;
  contrôle applicatif seul, sans droits MySQL restreints (rejeté — une écriture directe en base
  contournerait la garantie, alors que l'essai réel `validation/probe_audit_grants.py` montre que les
  droits MySQL seuls suffisent et sont testables indépendamment du code).
- **Conséquences** : `bank_details`/`refund_details` ne sont ni indexables ni recherchables ; une
  rotation de `APP_KEY` impose un rechiffrement planifié (à prévoir par T-069) et sa perte entraîne la
  perte de ces données ; une correction du journal d'audit passe par une nouvelle ligne
  `action_type = correction` référençant l'entrée corrigée, jamais par une modification.
- **Statut** : ADR-014 et ADR-015, **Proposé** — deux comptes MySQL et la clé applicative restent à
  provisionner par T-004/T-005, sans valeur réelle dans ce dépôt.

---

## Points non tranchés (repris de `spec.md` et `data-model.md`, non résolus par ce document)

Conformément à la Constitution Principe I et à la limite de trois points imposée par `spec.md`, ce
document ne tranche aucune valeur métier. Les points suivants restent ouverts et ne sont pas des
arbitrages techniques de ce `research.md` :

| Point | Référence | Statut |
|---|---|---|
| E-mail client obligatoire ou non | F001, M-06, `spec.md` FR-028 | `[NEEDS CLARIFICATION]` — schéma : `customers.email` NULL et unique |
| Informations et statut légal exigés des vendeurs | Q22, `spec.md` FR-029 | `[NEEDS CLARIFICATION]` — schéma : colonnes F002 confirmées seulement |
| Durée de conservation des données personnelles et financières | §19, `spec.md` FR-030 | `[NEEDS CLARIFICATION]` — schéma : aucune purge ni anonymisation automatique, conforme à la Constitution Principe X (validation juridique C-08 avant tout mécanisme) |
| Exclusion du retour figée sur la ligne de commande au moment de la vente | `data-model.md` E-10 | **HYPOTHÈSE H-T02-1** — un vendeur ne peut pas rendre un produit déjà vendu non retournable après coup en reclassant sa catégorie |

Les six valeurs non tranchées listées par `spec.md` FR-027 (Q19, Q27, Q40, Q42, Q44, Q45) ne sont pas des
points ouverts de ce schéma : elles sont déjà traitées comme des paramètres du mécanisme `Parametre` du
socle T-001 (HYPOTHÈSE H-08), sans colonne figée.
