# Data Model — Schéma de données physique (T-002)

**Feature** : `002-schema-donnees` · **Date** : 2026-10-14 · **Auteur** : Keystone (Technical Architect)
**Statut** : **Proposé — à valider par @user**. Ce document et le DDL de référence
`contracts/schema-reference.mysql.sql` forment la sortie de T-002. Ce ne sont **pas** des migrations : T-005
écrit les migrations Laravel à partir d'eux.

**Sources** (ordre de priorité) : cahier v1.1 (CONFIRMÉ, D45) · CLASS-01 et CLASS-02 (CONFIRMÉ, approuvés le
2026-10-12) · STATE-001..004 · plan de Compass (T-002, constats H-01..H-10, U-03) · socle T-001
(`specs/001-architecture-socle/data-model.md`, ADR-001..009) · ADR-010..015 (créés par T-002, `docs/architecture/DECISIONS.md`).

**Moteur** : MySQL ≥ 8.0.16 (les `CHECK` y sont appliqués), InnoDB, `utf8mb4_0900_ai_ci`. Validé sur MySQL 8.4.6
(voir §9).

---

## 1. Conventions (ADR-010 à ADR-014)

| Sujet | Règle |
|---|---|
| Noms | Anglais `snake_case`, tables au pluriel, clé `id BIGINT UNSIGNED AUTO_INCREMENT`, FK `<singulier>_id` (ADR-010) |
| Montants | `DECIMAL(10,2)` en MAD, jamais `FLOAT` (ADR-011) |
| Énumérations | `VARCHAR(32)` + `CHECK` nommé `ck_<table>_<colonne>`, valeurs anglaises (ADR-012) |
| Règles | Base = invariants statiques d'une ligne ; services = règles dynamiques et transitions (ADR-013) ; aucun déclencheur SQL |
| Données sensibles | `sellers.bank_details`, `product_returns.refund_details` chiffrés par l'application, clé = variable d'environnement `APP_KEY` (ADR-014) |
| Audit | `audit_entries` en ajout seul : l'utilisateur MySQL applicatif n'a que `SELECT, INSERT` (ADR-015) |
| Suppression | `ON DELETE RESTRICT` par défaut ; `CASCADE` seulement pour `cart_items` et `photo_variants` ; suppression logique (`deleted_at`) pour `products` |
| Temps | `TIMESTAMP` en UTC ; affichage `Africa/Casablanca` ; colonnes `created_at`/`updated_at` Laravel |

## 2. Correspondance classes UML → tables

| ID UML | Classe | Diagramme | Statut UML | Table | Module propriétaire |
|---|---|---|---|---|---|
| ENT-001 | Client | CLASS-01 | E | `customers` | M01 |
| ENT-002 | Vendeur | CLASS-01 | E | `sellers` | M01 |
| ENT-003 | Boutique | CLASS-01 | E | `shops` | M01/M02 |
| ENT-004 | Produit | CLASS-01 | E | `products` (+ `product_photos`) | M02 |
| ENT-005 | Catégorie | CLASS-01 | E | `categories` | M09 |
| ENT-006a | CommuneVendeur | CLASS-01 | E | `seller_communes` | M09 |
| ENT-006b | VilleDesservie | CLASS-01 | E | `served_cities` | M09 |
| ENT-007 | Panier | CLASS-01 | E | `carts` | M04 |
| ENT-007b | LignePanier | CLASS-01 | E | `cart_items` | M04 |
| ENT-008 | Commande | CLASS-01 | E | `orders` | M04 (statut : service T-027) |
| ENT-009 | SousCommande | CLASS-01 | I | `sub_orders` | M04/M05 (statut : service T-027) |
| ENT-010 | LigneCommande | CLASS-01 | I | `order_lines` | M04 |
| ENT-020 | Avis | CLASS-01 | E | `reviews` | M08 |
| ENT-011 | Retour | CLASS-02 | E | `product_returns` | M11 (statut : service T-043) |
| ENT-012 | Vérification | CLASS-02 | E | `return_inspections` | M11 |
| ENT-013 | Litige | CLASS-02 | E | `return_disputes` | M11 |
| ENT-014 | Remboursement | CLASS-02 | E | `refunds` | M11 |
| ENT-015 | FraisDeRetour | CLASS-02 | E | `return_fees` | M11 |
| ENT-016 | MontantVendeur | CLASS-02 | I | `seller_amounts` | M07 (statut : service T-036) |
| ENT-017 | Déduction | CLASS-02 | E | `deductions` | M07 |
| ENT-018 | Reversement | CLASS-02 | E | `payouts` | M07 |
| ENT-019 | RemiseDeFonds | CLASS-02 | I | `fund_remittances` (+ `fund_remittance_orders`) | M06 |
| ENT-019b | Écart | CLASS-02 | I | `cash_discrepancies` | M06 |
| ENT-021 | SociétéDeLivraison «externe» | CLASS-02 | E | `delivery_partners` | M06 |
| — | (socle) Compte | — | — | `users` | M01 / socle |
| — | (socle) FichierPhoto / variantes | — | — | `photo_files`, `photo_variants` | socle Photos |
| — | (socle) Journal d'audit | — | — | `audit_entries` | socle Audit |

Les classes « réf. » de CLASS-02 (REF-002, REF-008, REF-010) renvoient aux tables de CLASS-01.
Tables du socle T-001 **non** reprises ici (sans FK vers les tables métier, livrées par T-007/T-008/T-009/T-011) :
`settings` (Paramètre), `personal_access_tokens`/sessions, `internal_notifications`, `scheduled_tasks`,
`scheduled_task_runs` — leur modèle conceptuel reste `specs/001-architecture-socle/data-model.md`.

**Total** : 24 classes métier → 24 tables + 3 tables de liaison/composition (`product_photos`,
`fund_remittance_orders`, `photo_variants`) + 3 tables de socle (`users`, `photo_files`, `audit_entries`) = 30 tables.

## 3. Attributs UML → colonnes

Légende : **PK** clé primaire · **FK** clé étrangère · **UQ** unique · **CK** contrainte `CHECK` · *ajout* = colonne
absente de l'UML (voir §7).

### CLASS-01

| Table | Attribut / association UML | Colonne | Type et contrainte |
|---|---|---|---|
| `users` | *(socle)* identifiant, mot de passe, rôle | `phone`, `password`, `role` | `phone` UQ ; `password` = hash ; `role` CK ∈ {customer, seller, admin} |
| `customers` | nom | `name` | `VARCHAR(150)` NOT NULL |
| | téléphone {obligatoire} | → `users.phone` | voir écart E-02 |
| | e-mail [U] | `email` | NULL, UQ — **[NEEDS CLARIFICATION]** obligatoire ou non |
| | (compte) | `user_id` | FK `users`, UQ |
| `sellers` | identitéRaisonSociale | `legal_name` | NOT NULL |
| | téléphone | → `users.phone` | écart E-02 |
| | modeReversement : ModeReversement | `payout_method` | CK ∈ {bank_transfer, cash} |
| | coordonnéesBancaires [0..1] {si virement} | `bank_details` | `TEXT` chiffré ; CK `payout_method <> 'bank_transfer' OR bank_details IS NOT NULL` (CA-F002-2) |
| | statut : actif \| suspendu | `status`, `suspended_at` | CK ∈ {active, suspended} ; `suspended_at` requis si suspendu |
| | situé dans → CommuneVendeur 1 | `seller_commune_id` | FK `seller_communes` |
| | autres informations [U Q22] | — | **[NEEDS CLARIFICATION]** Q22 |
| `shops` | nom, présentation, adresseCollecte | `name`, `description`, `pickup_address` | |
| | Vendeur 1 — 1 Boutique | `seller_id` | FK `sellers`, **UQ** (une boutique par vendeur, H-06) |
| `products` | nom, description | `name`, `description` | FULLTEXT (`name`, `description`) pour F004 |
| | prix : MAD {> 0} | `price` | `DECIMAL(10,2)` **CK `price > 0`** |
| | stock : entier ≥ 0 | `stock` | `INT` **CK `stock >= 0`** |
| | origine [I] | `origin` | NULL |
| | périssable, personnalisé, publié, masqué | `is_perishable`, `is_customized`, `is_published`, `is_hidden` (+ `hidden_at`) | `BOOLEAN` |
| | /noteMoyenne | — | dérivée : `AVG(reviews.rating)` des avis non masqués (non stockée) |
| | Boutique publie 0..* | `shop_id` | FK `shops` |
| | Catégorie 1 | `category_id` | FK `categories` |
| | photos [1..*] [I] | `product_photos` | liaison ordonnée vers `photo_files` ; minimum 1 vérifié par le service |
| `categories` | nom, exclueDuRetour | `name` (UQ), `is_return_excluded` | |
| `seller_communes` | nom | `name` | UQ |
| `served_cities` | nom (V1 : Tanger) | `name` | UQ ; donnée « Tanger » insérée par T-005 |
| `carts` | Client 1 — 0..1 Panier | `customer_id` | FK, NULL, UQ |
| | (panier visiteur, H-01) | `guest_token_hash` | *ajout*, UQ ; CK au moins un des deux |
| | /sous-total par vendeur, /total | — | dérivés |
| `cart_items` | quantité {≤ stock} | `quantity` | CK `quantity > 0` ; ≤ stock vérifié par le service (CA-F006-2) |
| | composition Panier ◆ | `cart_id` | FK `ON DELETE CASCADE` ; UQ (`cart_id`, `product_id`) |
| | → Produit 1 | `product_id` | FK |
| `orders` | statut : StatutCommande | `status` | CK (7 valeurs, §4) |
| | adresseLivraison {à Tanger} | `delivery_address` + `served_city_id` | FK `served_cities` (association « livrée dans ») |
| | téléphone | `phone` | NOT NULL (RG-014) |
| | noteLivraison [0..1] | `delivery_note` | NULL |
| | fraisLivraison [U Q27] | `delivery_fee` | `DECIMAL(10,2)` CK ≥ 0, figé à la validation ; valeur = paramètre |
| | /total (RG-009) | — | dérivé : Σ lignes + `delivery_fee` |
| | modePaiement = à la livraison | `payment_method` | CK ∈ {cash_on_delivery} |
| | montantEncaissé [0..1], dateRéception [0..1] | `collected_amount`, `received_at` | CK : requis si `delivered_paid` (CA-F010-1) |
| | motifÉchec [0..1] | `failure_reason` | CK : requis si `delivery_failed` (CA-F010-3) |
| | Client passe 0..* | `customer_id` | FK |
| | (numéro lisible) | `reference` | *ajout*, UQ |
| `sub_orders` | statut : StatutSousCommande | `status` | CK (6 valeurs) |
| | motifRefus [0..1] | `refusal_reason` | CK : requis si `refused` |
| | Commande ◆ 1..* « une par vendeur » | `order_id`, `seller_id` | FK ; **UQ (`order_id`, `seller_id`)** (RG-003) |
| | (échéance de réponse) | `response_deadline_at` | *ajout*, index (`status`, `response_deadline_at`) |
| `order_lines` | quantité | `quantity` | CK > 0 |
| | prixUnitaire {figé} | `unit_price` | CK > 0 |
| | SousCommande ◆ 1..* | `sub_order_id` | FK ; UQ (`sub_order_id`, `product_id`) |
| | → Produit 1 | `product_id` | FK |
| | (libellé figé, exclusion figée) | `product_name`, `is_return_excluded` | *ajouts* (E-09, H-T02-1) |
| `reviews` | note : 1..5 | `rating` | `TINYINT` **CK `rating BETWEEN 1 AND 5`** |
| | commentaire | `comment` | NULL (HYPOTHÈSE : commentaire facultatif) |
| | masqué | `is_hidden`, `hidden_at` | |
| | Client rédige | `customer_id` | FK |
| | porte sur LigneCommande 1 | `order_line_id` | **UQ** (un avis par produit et par commande, RG-011) |
| | (produit, pour la moyenne) | `product_id` | FK composite (`order_line_id`, `product_id`) → `order_lines` |

### CLASS-02

| Table | Attribut / association UML | Colonne | Type et contrainte |
|---|---|---|---|
| `delivery_partners` | (aucun attribut — C-05) | `name` | UQ (écart E-04) |
| `fund_remittances` | montant, date | `amount`, `remitted_on` | CK `amount > 0` |
| | SociétéDeLivraison remet | `delivery_partner_id` | FK |
| | rapprochée de Commande 1..* | `fund_remittance_orders` | PK (`fund_remittance_id`, `order_id`) |
| `cash_discrepancies` | montant, date | `amount`, `recorded_on` | `amount` = encaissé − dû, signé, CK ≠ 0 |
| | Commande 1 — 0..1 | `order_id` | FK, UQ |
| `seller_amounts` | montant | `amount` | CK > 0 |
| | statut : StatutMontant | `status` | CK (4 valeurs) |
| | /dateDisponibilité | `hold_until` | matérialisée à la création (`received_at` + délai), index (`status`, `hold_until`) |
| | LigneCommande 1 — 0..1 | `order_line_id` | FK, UQ |
| | inclus dans Reversement 0..1 | `payout_id` | FK NULL ; CK `(status = 'paid_out') = (payout_id IS NOT NULL)` |
| | (vendeur) | `seller_id` | *ajout* dénormalisé, index (`seller_id`, `status`) |
| `payouts` | date, montant, mode | `paid_on`, `amount`, `method` | CK `amount > 0` ; `method` CK ModeReversement |
| | preuveRemise [0..1] {si espèces} | `cash_proof` | CK requis si `cash` |
| | Vendeur reçoit 0..* | `seller_id` | FK ; UQ (`seller_id`, `period_start`) — idempotence du reversement hebdomadaire |
| `product_returns` | quantité | `quantity` | CK > 0 ; Σ ≤ quantité de la ligne (service) |
| | motif : MotifRetour | `reason` | CK (4 valeurs) |
| | photo [0..1] | `photo_file_id` | FK `photo_files`, NULL |
| | moyenRemboursement | `refund_method` | CK ∈ {bank_transfer, other_traceable} — pas d'espèces (RG-022) |
| | coordonnéesRemboursement | `refund_details` | `TEXT` chiffré |
| | dateDemande | `requested_at` | index (`status`, `requested_at`) pour l'alerte 12 j (CA-F022-7) |
| | statut : StatutRetour | `status` | CK (8 valeurs) |
| | /procheDélaiLégal | — | dérivé (`requested_at` + seuil paramétré) |
| | LigneCommande 1 — 0..* | `order_line_id` | FK, index |
| `return_inspections` | résultat, motifContestation, remiseEnVente, date | `result`, `dispute_reason`, `restock`, `inspected_at` | CK `result`; motif requis si `disputed` ; Retour ◆ 0..1 → UQ `product_return_id` |
| `return_disputes` | décision, montantRemboursé, imputationFrais, date | `decision`, `refunded_amount`, `fee_charged_to`, `decided_at` (+ `opened_at`, `decided_by_user_id`, `decision_reason`) | décision complète ou absente (CK) ; UQ `product_return_id` |
| `refunds` | montant, moyen, référence, date | `amount`, `method`, `reference`, `refunded_on` (+ `recorded_by_user_id`) | CK `amount >= 0`, `method` sans espèces ; UQ `product_return_id` |
| `return_fees` | montant [U Q45], imputéÀ | `amount`, `charged_to` | CK ≥ 0 ; UQ `product_return_id` |
| `deductions` | montant, origine, date | `amount`, `origin`, `deducted_on` | CK > 0 ; `origin` ∈ {refund, return_fee} ; UQ (`product_return_id`, `origin`) |
| | Retour donne lieu à 0..* | `product_return_id` | FK |
| | régularisée sur Reversement 0..1 | `payout_id` | NULL = en attente (CA-F011-5) |
| | (vendeur) | `seller_id` | *ajout* dénormalisé, index (`seller_id`, `payout_id`) |

## 4. Énumérations UML → types contrôlés

Chaque énumération = `CHECK (col IN (…))` + enum PHP « backed » du même nom (ADR-012).

| ID | Énumération | Colonne(s) | Valeur UML → valeur stockée |
|---|---|---|---|
| EN-SC | StatutCommande | `orders.status` | EnAttenteAcceptation → `awaiting_acceptance` · Confirmée → `confirmed` · EnCollecte → `in_collection` · EnLivraison → `out_for_delivery` · LivréeEtPayée → `delivered_paid` · ÉchecDeLivraison → `delivery_failed` · Annulée → `cancelled` |
| EN-SSC | StatutSousCommande | `sub_orders.status` | Nouvelle → `new` · Acceptée → `accepted` · PrêtePourCollecte → `ready_for_pickup` · Collectée → `collected` · Refusée → `refused` · Annulée → `cancelled` |
| EN-MR / EN-MR2 | ModeReversement | `sellers.payout_method`, `payouts.method` | Virement → `bank_transfer` · Espèces → `cash` |
| EN-SR | StatutRetour | `product_returns.status` | Demandé → `requested` · EnReprise → `pickup_in_progress` · Repris → `picked_up` · VérifiéParLeVendeur → `verified_by_seller` · Contesté → `disputed` · Litige → `in_dispute` · ClientRemboursé → `customer_refunded` · RetourRefusé → `return_refused` |
| EN-MOT | MotifRetour | `product_returns.reason` | ChangementDAvis → `change_of_mind` · Défectueux → `defective` · Incorrect → `incorrect` · NonConforme → `not_as_described` |
| EN-SM | StatutMontant | `seller_amounts.status` | Retenu → `held` · Disponible → `available` · Reversé → `paid_out` · Déduit → `deducted` |
| EN-MRB | MoyenRemboursement | `product_returns.refund_method`, `refunds.method` | VirementBancaire → `bank_transfer` · AutreMoyenTraçable [U Q42] → `other_traceable` |
| EN-IF | ImputationFrais | `return_fees.charged_to`, `return_disputes.fee_charged_to` | Client → `customer` · Vendeur → `seller` |
| EN-RV | RésultatVérification | `return_inspections.result` | Conforme → `compliant` · Contesté → `disputed` |

Énumérations implicites de l'UML (attributs à valeurs listées, sans classe «enumeration») :
`sellers.status` {active, suspended} · `deductions.origin` {refund, return_fee} · `orders.payment_method`
{cash_on_delivery} · `return_disputes.decision` {in_favor_of_customer, in_favor_of_seller} (STATE-003 t7/t8).
Énumérations de socle : `users.role`, `photo_files.check_status`, `photo_variants.variant`, `audit_entries.action_type`.

La liste détaillée « autres moyens traçables » (Q42) n'est **pas** une énumération figée : `other_traceable` +
`refund_details` ; la liste autorisée sera un paramètre (H-08).

## 5. Règles : garanties par la base ou par le service (ADR-013)

| Règle | Base (refus SQL) | Service (propriétaire) |
|---|---|---|
| Prix > 0 (F003) | `ck_products_price_positive`, `ck_order_lines_unit_price_positive` | — |
| Stock ≥ 0 (CLASS-01, RG-017) | `ck_products_stock_non_negative` : un décrément sous 0 échoue | Réservation dans une transaction avec `SELECT … FOR UPDATE` (T-028) |
| Note 1..5 (F012) | `ck_reviews_rating_range` | — |
| **RG-006** visible ⇔ publié ∧ ¬masqué ∧ stock > 0 ∧ vendeur actif | Index `ix_products_visible`, `ix_products_category_visible`, `ix_sellers_status` | Filtre unique « produits visibles » (M03) ; pas de colonne dérivée (évite la désynchronisation) |
| **RG-011** avis seulement si commande « livrée et payée » ; un avis par produit et par commande | UQ `reviews.order_line_id` ; FK composite (`order_line_id`, `product_id`) | Vérifie `orders.status = delivered_paid` et que le client est celui de la commande ; 2ᵉ avis = mise à jour (F012) |
| **RG-019** retour ≤ 7 j après réception, produit non exclu | `orders.received_at` obligatoire si livrée ; `order_lines.is_return_excluded` figé | Éligibilité : `requested_at ≤ received_at + délai` et ¬exclu (exclu = périssable ∨ personnalisé ∨ catégorie exclue, figé à la validation) |
| **RG-024** retenue jusqu'à réception + 7 j ; reste retenu si retour en cours | `seller_amounts.hold_until` + index (`status`, `hold_until`) | Traitement planifié idempotent (T-053) : `held → available` si `hold_until ≤ maintenant` et aucun retour ouvert sur la ligne |
| RG-003 une sous-commande par vendeur | UQ (`order_id`, `seller_id`) | Création en une transaction |
| RG-008 / STATE-001..004 transitions | Valeurs autorisées + états complets (CK) | Services uniques T-027, T-036, T-043 |
| RG-018 / CA-F011-5 reversement = Σ disponibles − Σ déductions en attente | UQ (`seller_id`, `period_start`) ; index `ix_seller_amounts_seller_status`, `ix_deductions_pending` | Calcul hebdomadaire (T-054) |
| RG-022 pas d'espèces non traçables | CK sur `refund_method` et `refunds.method` | — |
| CA-F002-2 virement ⇒ coordonnées bancaires | `ck_sellers_bank_details` | Message d'erreur sur le champ |
| CA-F006-2 quantité ≤ stock | `quantity > 0` | Plafonnement au stock (valeur dynamique) |
| CA-F010-1 / CA-F010-3 | `ck_orders_delivered`, `ck_orders_failed` | — |
| ENF-008 traçabilité | `audit_entries` : CK montant + motif pour les actions financières ; droits `SELECT, INSERT` | Écriture d'audit dans la même transaction que l'opération |

## 6. Index et performance (ENF-004, traitements planifiés)

| Besoin | Index |
|---|---|
| Catalogue visible, filtre catégorie, tri récent (F004, ENF-004) | `ix_products_visible` (`is_published`, `is_hidden`, `stock`, `created_at`), `ix_products_category_visible` |
| Recherche par mot-clé (CA-F004-1) | `FULLTEXT ft_products_search` (`name`, `description`) — analyseur par défaut ; à revoir si l'arabe est retenu (Q11) |
| Note moyenne et avis d'un produit (F005) | `ix_reviews_product_visible` (`product_id`, `is_hidden`, `rating`) |
| Commandes du client, back-office par statut | `ix_orders_customer`, `ix_orders_status` |
| Sous-commandes du vendeur (CA-F009-1) | `ix_sub_orders_seller` (`seller_id`, `status`, `created_at`) |
| Expiration du délai de réponse vendeur (T-034) | `ix_sub_orders_deadline` (`status`, `response_deadline_at`) |
| Retenu → Disponible (T-053) | `ix_seller_amounts_release` (`status`, `hold_until`) |
| Alerte délai légal 12 j (T-050, CA-F022-7) | `ix_product_returns_status` (`status`, `requested_at`) |
| Reversement hebdomadaire (T-054) | `ix_seller_amounts_seller_status`, `ix_deductions_pending` (`seller_id`, `payout_id`) |
| Consultation du journal d'audit | `ix_audit_target`, `ix_audit_actor`, `ix_audit_action` |

Toutes les clés étrangères sont indexées (InnoDB l'exige). Pas de partitionnement en V1 (volumes Q21 MANQUANT).

## 7. Écarts avec l'UML (CLASS-01 / CLASS-02)

Classement : **AJOUT** (le schéma ajoute), **PRÉCISION** (le schéma tranche un point non spécifié), **DIVERGENCE**
(le schéma s'écarte d'une multiplicité ou d'un attribut). Destinataire : Blueprint (manque UML) ou @user (manque
métier) — Compass transmet, Keystone ne les contacte pas.

| # | Type | Élément UML | Schéma | Justification | Destinataire |
|---|---|---|---|---|---|
| E-01 | AJOUT | Aucun compte ni Administrateur dans CLASS-01 | `users` (rôle customer/seller/admin) | Authentification transverse (FR-020, FR-050, socle T-001) ; l'Administrateur n'a pas d'attribut métier | Blueprint (information) |
| E-02 | DIVERGENCE | `Client.téléphone`, `Vendeur.téléphone` | Stockés une seule fois dans `users.phone` (UQ) | Le téléphone est l'identifiant de connexion (RG-014, ENF-007) ; évite deux sources | Blueprint (information) |
| E-03 | PRÉCISION | ModeReversement défini deux fois (EN-MR, EN-MR2) | Un seul type | Même liste de valeurs | Blueprint (doublon graphique) |
| E-04 | AJOUT | SociétéDeLivraison «externe», sans attribut (C-05) | `delivery_partners(name)` | Rattacher les remises de fonds ; la société n'a ni compte ni accès (D38) | @user (un seul partenaire ? C-05) |
| E-05 | PRÉCISION | Attributs dérivés `/noteMoyenne`, `/total`, sous-totaux du panier, `/procheDélaiLégal` | Non stockés, calculés | Pas de désynchronisation ; index dédiés (§6) | — |
| E-06 | PRÉCISION | `/dateDisponibilité = dateRéception + 7 j` | Matérialisée dans `seller_amounts.hold_until` | Échéance figée à la création même si le paramètre change ensuite ; index du traitement planifié | Blueprint (information) |
| E-07 | AJOUT | `Produit.photos [1..*]`, `Retour.photo [0..1]` (attributs) | `product_photos` → `photo_files` (socle) ; `product_returns.photo_file_id` | Fichiers gérés par le socle Photos (ADR-004) ; minimum 1 photo vérifié par le service | — |
| E-08 | PRÉCISION | `Litige.décision` sans type | `decision` ∈ {in_favor_of_customer, in_favor_of_seller} + `decision_reason`, `opened_at`, `decided_by_user_id` | Issues de STATE-003 t7/t8 ; le litige existe dès la contestation, décision ensuite | Blueprint (typer `décision`) |
| E-09 | AJOUT | — | `orders.reference`, `order_lines.product_name`, `sub_orders.response_deadline_at`, `payouts.period_start`, colonnes `recorded_by_user_id`, `products.deleted_at`, horodatages | Confirmation écrite (RG-026), échéance figée (Q19 paramètre), idempotence (FR-031), audit (ENF-008), produit supprimé encore référencé (F003) | — |
| E-10 | AJOUT | Exclusion du retour calculée sur le Produit (RG-019) | `order_lines.is_return_excluded` figé à la validation | **HYPOTHÈSE H-T02-1** : un vendeur ne doit pas pouvoir rendre un produit vendu non retournable après coup | **@user** |
| E-11 | DIVERGENCE | Client 1 — 0..1 Panier (panier toujours rattaché à un client) | `carts.customer_id` NULL + `guest_token_hash` | Panier visiteur (H-01, CA-F001-3, note WARN de CLASS-01) | @user (H-01) / Blueprint (multiplicité 0..1 côté Client) |
| E-12 | PRÉCISION | LigneCommande 1 — 0..* Retour (WARN n_warn2) | Plusieurs retours par ligne autorisés ; Σ quantités ≤ quantité (service) | Retours partiels successifs | **@user** (confirmer) |
| E-13 | AJOUT | Déduction, MontantVendeur sans lien direct au Vendeur | `seller_id` dénormalisé dans `deductions` et `seller_amounts` | Calcul hebdomadaire par vendeur (CA-F011-5) sans 4 jointures ; écrit une fois par le service Montants | — |
| E-14 | PRÉCISION | Avis → Client et Avis → LigneCommande | + `reviews.product_id` (FK composite garantissant la cohérence) | Moyenne par produit indexée (F005, CA-F013-3) | — |
| E-15 | PRÉCISION | Écart : montant, date | `amount` = encaissé − dû (signé, ≠ 0) ; une seule ligne par commande | Convention de signe absente de l'UML | Blueprint (information) |
| E-16 | AJOUT | Aucune classe d'historique (U-03) | `audit_entries` (ajout seul) | ENF-008, ADR-008, ADR-015 | Blueprint (U-03 déjà connu) |
| E-17 | PRÉCISION | `Litige.imputationFrais` et `FraisDeRetour.imputéÀ` portent la même information | `return_fees.charged_to` = valeur finale ; `return_disputes.fee_charged_to` = décision de l'administrateur qui l'a fixée | Redondance UML ; le service applique la décision au frais | Blueprint (information) |
| E-18 | PRÉCISION | `Vendeur.statut`, `Déduction.origine`, `Commande.modePaiement` (listes en ligne) | `CHECK` dédiés (§4) | Énumérations implicites | — |
| E-19 | NON MODÉLISÉ | `Vendeur.autres informations [U Q22]` | Aucune colonne | Q22 MANQUANT | **@user** |
| E-20 | NON MODÉLISÉ | Suite d'un échec de livraison (Q24, M-07), annulation par l'administrateur (U-02) | Aucune colonne dédiée | Comportement non spécifié | @user (Q24) / Blueprint (U-02) |
| E-21 | PRÉCISION | RemiseDeFonds, Écart, MontantVendeur, SousCommande, LigneCommande marquées [I] | Persistées comme les autres classes | RG-020, CA-F010-2, RG-003, RG-024 en dépendent ; les retirer bloquerait T-036/T-039/T-041 | @user (H-04, H-05) |
| E-22 | PRÉCISION | Vendeur 1 — 1 Boutique marqué [I] | `UNIQUE(shops.seller_id)` | Rend la cardinalité stricte ; à retirer si un vendeur peut avoir plusieurs boutiques | @user (H-06) |
| E-23 | NON MODÉLISÉ | Décision de l'administrateur faute de vérification vendeur dans le délai (U-01, Q44) | Aucune colonne dédiée (la décision passe par `return_disputes`) | Transition non dessinée dans STATE-003 | Blueprint après décision @user (Q44) |

Correspondance avec la section « Écarts avec l'UML approuvé » de `spec.md` (numérotation propre à la spec) :
spec E-01 = E-16 · spec E-02 = E-01 + E-02 · spec E-03 = E-11 · spec E-04 = E-21 · spec E-05 = E-22 ·
spec E-06 = E-12 · spec E-07 = E-20 + E-23. **La liste de référence est ce tableau (E-01 à E-23).**

## 8. Points ouverts

- **[NEEDS CLARIFICATION: e-mail client obligatoire ou non (F001, M-06)]** — schéma : `customers.email` NULL et unique ; passer à NOT NULL = migration simple.
- **[NEEDS CLARIFICATION: informations vendeur exigées (Q22)]** — schéma : colonnes F002 seulement ; ajout = migration additive.
- **[NEEDS CLARIFICATION: durée de conservation des données personnelles (§19)]** — schéma : aucune purge, suppression logique des produits seulement ; une politique de purge/anonymisation sera ajoutée après décision.
- HYPOTHÈSES reprises sans changement : H-01 (panier visiteur), H-04 (MontantVendeur par ligne), H-05 (RemiseDeFonds, Écart), H-06 (une boutique par vendeur), H-08 (valeurs Q19, Q27, Q40, Q42, Q44, Q45 = paramètres, aucune colonne figée).
- HYPOTHÈSE propre à T-002 : **H-T02-1** (exclusion du retour figée sur la ligne, E-10) ; téléphone au format E.164 dans `VARCHAR(20)`.

## 9. Validation (commandes réelles, 2026-10-14)

Instance MySQL **8.4.6** jetable (binaire officiel, hors dépôt), base vide `t002_schema` :

| Vérification | Script (`validation/`) | Résultat |
|---|---|---|
| Le DDL s'exécute sur base vide | `run_sql.py reset.sql ../contracts/schema-reference.mysql.sql` | 31 instructions, 0 erreur ; 30 tables |
| Chaque classe / énumération UML a une table / un type ; contraintes prix, stock, note présentes | `coverage.py` (lit les `.drawio` et `information_schema`) | 24/24 classes, 10/10 énumérations (nombre de valeurs identique), 3/3 contraintes ; 0 manque |
| Les violations sont refusées | `probe_constraints.py` | 23/23 violations refusées (prix 0 et négatif, stock négatif, note 0 et 6, doublon d'avis, FK composite, statuts hors liste, états incomplets…) |
| Journal d'audit en ajout seul (ADR-015) | `probe_audit_grants.py` | INSERT accepté ; UPDATE et DELETE refusés (erreur 1142) |

Les scripts sont des outils de validation du schéma de référence, pas des tests applicatifs ; les tests de
migration restent la vérification de T-005.

## 10. Consignes pour T-005 (migrations)

1. Ordre de création = ordre du DDL (les FK ne pointent que vers des tables déjà créées).
2. Le constructeur de schéma Laravel n'expose pas, à notre connaissance, de méthode pour les `CHECK` : les ajouter par `DB::statement('ALTER TABLE … ADD CONSTRAINT …')` en conservant les noms `ck_*` (à confirmer par T-005).
3. Image MySQL ≥ 8.0.16 (validé sur 8.4.6) — choix d'image par T-004.
4. Deux utilisateurs MySQL (ADR-015) : variables d'environnement `DB_USERNAME` (application, `SELECT, INSERT` seulement sur `audit_entries`) et `DB_MIGRATION_USERNAME` ; aucune valeur dans le dépôt.
5. Données de référence (T-005) : `served_cities` = Tanger ; compte administrateur initial dont les identifiants viennent de variables d'environnement.
6. Vérification attendue de T-005 : migrations appliquées puis annulées sans erreur, puis `validation/coverage.py` et `validation/probe_constraints.py` rejoués sur la base migrée.
