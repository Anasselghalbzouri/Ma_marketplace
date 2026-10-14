-- =====================================================================================================
-- Schéma physique de référence — marketplace-produits-locaux-maroc (T-002)
-- MySQL 8.0.16+ (CHECK appliqués) · InnoDB · utf8mb4 / utf8mb4_0900_ai_ci
--
-- STATUT : Proposé — à valider par @user. Document de CONCEPTION (référence), PAS une migration.
-- Les migrations Laravel sont écrites par T-005 à partir de ce fichier ; en cas d'écart, ce fichier et
-- specs/002-schema-donnees/data-model.md font foi jusqu'à décision contraire de @user.
--
-- Sources : CLASS-01 (ENT-001..010, ENT-020, EN-SC, EN-SSC, EN-MR), CLASS-02 (ENT-011..021, EN-SR, EN-MOT,
-- EN-SM, EN-MRB, EN-IF, EN-RV, EN-MR2), CDC v1.1 (RG-006/011/019/024, F001-F022, CA-*), ADR-002, ADR-008,
-- ADR-010..ADR-015 (docs/architecture/DECISIONS.md).
--
-- Conventions (ADR-010) :
--   * noms de tables / colonnes en anglais snake_case (Constitution IX) ; tables au pluriel (Laravel) ;
--   * clé primaire id BIGINT UNSIGNED AUTO_INCREMENT ; FK <table_singulier>_id ;
--   * montants MAD en DECIMAL(10,2) (ADR-011) ; jamais de FLOAT ;
--   * énumérations UML = VARCHAR(32) + CHECK nommé ck_<table>_<colonne>, valeurs anglaises snake_case,
--     miroir d'une enum PHP « backed » (ADR-012) ;
--   * horodatages en UTC (TIMESTAMP), affichage Africa/Casablanca ;
--   * ON DELETE RESTRICT par défaut ; CASCADE seulement pour une composition sans valeur métier propre
--     (cart_items, photo_variants) ;
--   * données sensibles (coordonnées bancaires, coordonnées de remboursement) chiffrées par l'application
--     (ADR-014) : colonne TEXT contenant le texte chiffré ; la clé vient de la variable d'environnement
--     APP_KEY (jamais dans le dépôt).
-- Aucune donnée n'est insérée ici : les données de référence (ville Tanger, administrateur initial) sont
-- l'objet de T-005.
-- =====================================================================================================

SET NAMES utf8mb4;

-- -----------------------------------------------------------------------------------------------------
-- SOCLE (comptes, fichiers, audit) — vue physique des entités conceptuelles de
-- specs/001-architecture-socle/data-model.md nécessaires comme cibles de clés étrangères.
-- -----------------------------------------------------------------------------------------------------

-- Compte (socle). Absent de CLASS-01/02 (écart E-01/E-02) : porte l'identifiant de connexion et le rôle.
CREATE TABLE users (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    phone           VARCHAR(20)     NOT NULL COMMENT 'Identifiant de connexion, format E.164 (RG-014, FR-050)',
    password        VARCHAR(255)    NOT NULL COMMENT 'Hash uniquement ; jamais renvoyé (FR-054)',
    role            VARCHAR(32)     NOT NULL,
    last_login_at   TIMESTAMP       NULL,
    created_at      TIMESTAMP       NULL,
    updated_at      TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_phone (phone),
    KEY ix_users_role (role),
    CONSTRAINT ck_users_role CHECK (role IN ('customer', 'seller', 'admin'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Fichier image (socle FichierPhoto) : photos produits (Produit.photos) et photo de retour (Retour.photo).
CREATE TABLE photo_files (
    id                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    owner_user_id     BIGINT UNSIGNED NOT NULL COMMENT 'Compte qui a téléversé (cloisonnement FR-051)',
    stored_name       VARCHAR(64)     NOT NULL COMMENT 'Nom généré, non prédictible (FR-042)',
    mime_type         VARCHAR(64)     NOT NULL,
    size_bytes        INT UNSIGNED    NOT NULL,
    check_status      VARCHAR(32)     NOT NULL,
    rejection_reason  VARCHAR(255)    NULL,
    created_at        TIMESTAMP       NULL,
    updated_at        TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_photo_files_stored_name (stored_name),
    KEY ix_photo_files_owner (owner_user_id),
    CONSTRAINT fk_photo_files_owner FOREIGN KEY (owner_user_id) REFERENCES users (id),
    CONSTRAINT ck_photo_files_check_status CHECK (check_status IN ('accepted', 'rejected')),
    CONSTRAINT ck_photo_files_rejection CHECK (check_status <> 'rejected' OR rejection_reason IS NOT NULL),
    CONSTRAINT ck_photo_files_size CHECK (size_bytes > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE photo_variants (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    photo_file_id   BIGINT UNSIGNED NOT NULL,
    variant         VARCHAR(32)     NOT NULL,
    storage_path    VARCHAR(255)    NOT NULL COMMENT 'Chemin relatif au disque (volume ou objet S3, ADR-004)',
    width_px        SMALLINT UNSIGNED NOT NULL,
    height_px       SMALLINT UNSIGNED NOT NULL,
    created_at      TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_photo_variants_file_variant (photo_file_id, variant),
    CONSTRAINT fk_photo_variants_file FOREIGN KEY (photo_file_id) REFERENCES photo_files (id) ON DELETE CASCADE,
    CONSTRAINT ck_photo_variants_variant CHECK (variant IN ('original', 'mobile')),
    CONSTRAINT ck_photo_variants_size CHECK (width_px > 0 AND height_px > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Journal d'audit transverse, ajout seul (ADR-008, ENF-008, U-03 / écart E-16).
-- Aucune UPDATE/DELETE : l'utilisateur MySQL d'exécution n'a que SELECT, INSERT sur cette table (ADR-015).
CREATE TABLE audit_entries (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    occurred_at         TIMESTAMP(3)    NOT NULL,
    actor_user_id       BIGINT UNSIGNED NULL COMMENT 'NULL seulement pour un traitement planifié',
    actor_system        VARCHAR(64)     NULL COMMENT 'Code du traitement planifié si acteur système',
    action_type         VARCHAR(48)     NOT NULL,
    target_type         VARCHAR(48)     NOT NULL COMMENT 'Référence logique (ex. sub_order, seller_amount)',
    target_id           BIGINT UNSIGNED NOT NULL,
    from_status         VARCHAR(32)     NULL,
    to_status           VARCHAR(32)     NULL,
    amount              DECIMAL(10,2)   NULL,
    reason              VARCHAR(500)    NULL,
    corrects_entry_id   BIGINT UNSIGNED NULL,
    PRIMARY KEY (id),
    KEY ix_audit_target (target_type, target_id, occurred_at),
    KEY ix_audit_actor (actor_user_id, occurred_at),
    KEY ix_audit_action (action_type, occurred_at),
    CONSTRAINT fk_audit_actor FOREIGN KEY (actor_user_id) REFERENCES users (id),
    CONSTRAINT fk_audit_corrects FOREIGN KEY (corrects_entry_id) REFERENCES audit_entries (id),
    CONSTRAINT ck_audit_actor CHECK (actor_user_id IS NOT NULL OR actor_system IS NOT NULL),
    CONSTRAINT ck_audit_action CHECK (action_type IN (
        'order_status_changed', 'sub_order_status_changed', 'delivery_status_recorded', 'cash_collected',
        'fund_remittance_recorded', 'cash_discrepancy_recorded', 'seller_amount_held', 'seller_amount_released',
        'seller_amount_deducted', 'return_status_changed', 'return_pickup_recorded', 'return_fee_charged',
        'dispute_decided', 'refund_recorded', 'deduction_recorded', 'payout_recorded', 'correction',
        'scheduled_task_run')),
    -- Toute action financière porte un montant et un motif (Constitution IV, FR-022).
    CONSTRAINT ck_audit_money CHECK (
        action_type NOT IN ('cash_collected', 'fund_remittance_recorded', 'cash_discrepancy_recorded',
                            'seller_amount_deducted', 'return_fee_charged', 'refund_recorded',
                            'deduction_recorded', 'payout_recorded', 'correction')
        OR (amount IS NOT NULL AND reason IS NOT NULL)),
    CONSTRAINT ck_audit_correction CHECK (action_type <> 'correction' OR corrects_entry_id IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------------------------------
-- CLASS-01 — référentiels (M09)
-- -----------------------------------------------------------------------------------------------------

-- ENT-006b VilleDesservie (RG-001 ; V1 : Tanger, seed par T-005)
CREATE TABLE served_cities (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name        VARCHAR(100)    NOT NULL,
    created_at  TIMESTAMP       NULL,
    updated_at  TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_served_cities_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ENT-006a CommuneVendeur (RG-023 ; liste fixée par l'administrateur, Q41 MANQUANT)
CREATE TABLE seller_communes (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name        VARCHAR(100)    NOT NULL,
    created_at  TIMESTAMP       NULL,
    updated_at  TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_seller_communes_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ENT-005 Catégorie (F003, F013, RG-019, D40)
CREATE TABLE categories (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name                VARCHAR(100)    NOT NULL,
    is_return_excluded  BOOLEAN         NOT NULL DEFAULT FALSE COMMENT 'exclueDuRetour (RG-019, D40)',
    created_at          TIMESTAMP       NULL,
    updated_at          TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_categories_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------------------------------
-- CLASS-01 — comptes (M01)
-- -----------------------------------------------------------------------------------------------------

-- ENT-001 Client (F001, RG-014, RG-028). téléphone -> users.phone (écart E-02).
CREATE TABLE customers (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id     BIGINT UNSIGNED NOT NULL,
    name        VARCHAR(150)    NOT NULL,
    email       VARCHAR(255)    NULL COMMENT 'Obligatoire ou non : MANQUANT (F001, M-06)',
    created_at  TIMESTAMP       NULL,
    updated_at  TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_customers_user (user_id),
    UNIQUE KEY uq_customers_email (email),
    CONSTRAINT fk_customers_user FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ENT-002 Vendeur (F002, RG-015, RG-018, CA-F002-2). « autres informations » : Q22 MANQUANT, non modélisé.
CREATE TABLE sellers (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id             BIGINT UNSIGNED NOT NULL,
    legal_name          VARCHAR(200)    NOT NULL COMMENT 'identitéRaisonSociale',
    seller_commune_id   BIGINT UNSIGNED NOT NULL COMMENT 'situé dans (RG-023)',
    payout_method       VARCHAR(32)     NOT NULL COMMENT 'ModeReversement',
    bank_details        TEXT            NULL COMMENT 'coordonnéesBancaires, chiffré (ADR-014, FR-055)',
    status              VARCHAR(32)     NOT NULL DEFAULT 'active',
    suspended_at        TIMESTAMP       NULL,
    created_at          TIMESTAMP       NULL,
    updated_at          TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_sellers_user (user_id),
    KEY ix_sellers_commune (seller_commune_id),
    KEY ix_sellers_status (status),
    CONSTRAINT fk_sellers_user FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT fk_sellers_commune FOREIGN KEY (seller_commune_id) REFERENCES seller_communes (id),
    CONSTRAINT ck_sellers_payout_method CHECK (payout_method IN ('bank_transfer', 'cash')),
    -- CA-F002-2 : virement => coordonnées bancaires obligatoires.
    CONSTRAINT ck_sellers_bank_details CHECK (payout_method <> 'bank_transfer' OR bank_details IS NOT NULL),
    CONSTRAINT ck_sellers_status CHECK (status IN ('active', 'suspended')),
    CONSTRAINT ck_sellers_suspended_at CHECK (status <> 'suspended' OR suspended_at IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ENT-003 Boutique (F002). Une boutique par vendeur (H-06) => UNIQUE(seller_id).
CREATE TABLE shops (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    seller_id       BIGINT UNSIGNED NOT NULL,
    name            VARCHAR(150)    NOT NULL,
    description     TEXT            NULL COMMENT 'présentation',
    pickup_address  VARCHAR(500)    NOT NULL COMMENT 'adresseCollecte',
    created_at      TIMESTAMP       NULL,
    updated_at      TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_shops_seller (seller_id),
    CONSTRAINT fk_shops_seller FOREIGN KEY (seller_id) REFERENCES sellers (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------------------------------
-- CLASS-01 — catalogue (M02)
-- -----------------------------------------------------------------------------------------------------

-- ENT-004 Produit (F003, F005, RG-006, RG-007, RG-015, RG-019). /noteMoyenne dérivée (reviews), non stockée.
CREATE TABLE products (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    shop_id         BIGINT UNSIGNED NOT NULL COMMENT 'Boutique publie Produit',
    category_id     BIGINT UNSIGNED NOT NULL,
    name            VARCHAR(200)    NOT NULL,
    description     TEXT            NOT NULL,
    price           DECIMAL(10,2)   NOT NULL COMMENT 'MAD, prix courant (RG-007)',
    stock           INT             NOT NULL DEFAULT 0,
    origin          VARCHAR(150)    NULL COMMENT 'origine ville/région (HYPOTHÈSE F003)',
    is_perishable   BOOLEAN         NOT NULL DEFAULT FALSE,
    is_customized   BOOLEAN         NOT NULL DEFAULT FALSE,
    is_published    BOOLEAN         NOT NULL DEFAULT FALSE,
    is_hidden       BOOLEAN         NOT NULL DEFAULT FALSE COMMENT 'masqué par l''administrateur (RG-015)',
    hidden_at       TIMESTAMP       NULL,
    created_at      TIMESTAMP       NULL,
    updated_at      TIMESTAMP       NULL,
    deleted_at      TIMESTAMP       NULL COMMENT 'Suppression logique : un produit commandé reste référencé',
    PRIMARY KEY (id),
    KEY ix_products_shop (shop_id),
    KEY ix_products_category_visible (category_id, is_published, is_hidden, stock),
    KEY ix_products_visible (is_published, is_hidden, stock, created_at),
    FULLTEXT KEY ft_products_search (name, description),
    CONSTRAINT fk_products_shop FOREIGN KEY (shop_id) REFERENCES shops (id),
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories (id),
    CONSTRAINT ck_products_price_positive CHECK (price > 0),
    CONSTRAINT ck_products_stock_non_negative CHECK (stock >= 0),
    CONSTRAINT ck_products_hidden_at CHECK (is_hidden = FALSE OR hidden_at IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Produit.photos [1..*] (écart E-07) : liaison ordonnée produit <-> fichier.
CREATE TABLE product_photos (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    product_id      BIGINT UNSIGNED NOT NULL,
    photo_file_id   BIGINT UNSIGNED NOT NULL,
    position        SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    created_at      TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_product_photos_file (photo_file_id),
    KEY ix_product_photos_product (product_id, position),
    CONSTRAINT fk_product_photos_product FOREIGN KEY (product_id) REFERENCES products (id),
    CONSTRAINT fk_product_photos_file FOREIGN KEY (photo_file_id) REFERENCES photo_files (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------------------------------
-- CLASS-01 — panier (M04)
-- -----------------------------------------------------------------------------------------------------

-- ENT-007 Panier (F006). Client 1 — 0..1 Panier ; panier visiteur par jeton (H-01, CA-F001-3).
CREATE TABLE carts (
    id                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    customer_id       BIGINT UNSIGNED NULL,
    guest_token_hash  CHAR(64)        NULL COMMENT 'SHA-256 du jeton de panier visiteur ; jamais le jeton en clair',
    created_at        TIMESTAMP       NULL,
    updated_at        TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_carts_customer (customer_id),
    UNIQUE KEY uq_carts_guest_token (guest_token_hash),
    CONSTRAINT fk_carts_customer FOREIGN KEY (customer_id) REFERENCES customers (id),
    CONSTRAINT ck_carts_owner CHECK (customer_id IS NOT NULL OR guest_token_hash IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ENT-007b LignePanier (F006, CA-F006-2 : quantité <= stock vérifiée par le service, valeur dynamique).
CREATE TABLE cart_items (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    cart_id     BIGINT UNSIGNED NOT NULL,
    product_id  BIGINT UNSIGNED NOT NULL,
    quantity    INT             NOT NULL,
    created_at  TIMESTAMP       NULL,
    updated_at  TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_cart_items_cart_product (cart_id, product_id),
    KEY ix_cart_items_product (product_id),
    CONSTRAINT fk_cart_items_cart FOREIGN KEY (cart_id) REFERENCES carts (id) ON DELETE CASCADE,
    CONSTRAINT fk_cart_items_product FOREIGN KEY (product_id) REFERENCES products (id),
    CONSTRAINT ck_cart_items_quantity_positive CHECK (quantity > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------------------------------
-- CLASS-01 — commandes (M04 / M05 / M06)
-- -----------------------------------------------------------------------------------------------------

-- ENT-008 Commande (F007, F008, F010, RG-001, RG-002, RG-009, RG-013, CA-F010-1/3).
-- /total = Σ(order_lines.quantity × unit_price) + delivery_fee : dérivé, non stocké.
CREATE TABLE orders (
    id                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    reference         VARCHAR(20)     NOT NULL COMMENT 'Numéro lisible (confirmation RG-026, transmission livreur) — ajout technique',
    customer_id       BIGINT UNSIGNED NOT NULL COMMENT 'Client passe Commande',
    served_city_id    BIGINT UNSIGNED NOT NULL COMMENT 'livrée dans (RG-001)',
    status            VARCHAR(32)     NOT NULL DEFAULT 'awaiting_acceptance',
    delivery_address  VARCHAR(500)    NOT NULL COMMENT 'adresseLivraison (quartier, adresse, repères : HYPOTHÈSE F007)',
    phone             VARCHAR(20)     NOT NULL COMMENT 'téléphone de livraison (RG-014)',
    delivery_note     VARCHAR(500)    NULL,
    delivery_fee      DECIMAL(10,2)   NOT NULL COMMENT 'fraisLivraison figés à la validation ; valeur = paramètre (Q27 MANQUANT)',
    payment_method    VARCHAR(32)     NOT NULL DEFAULT 'cash_on_delivery',
    collected_amount  DECIMAL(10,2)   NULL COMMENT 'montantEncaissé',
    received_at       TIMESTAMP       NULL COMMENT 'dateRéception : départ du délai de retour (RG-019, RG-024)',
    failure_reason    VARCHAR(500)    NULL COMMENT 'motifÉchec (RG-013)',
    created_at        TIMESTAMP       NULL COMMENT '= date de validation de la commande',
    updated_at        TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_orders_reference (reference),
    KEY ix_orders_customer (customer_id, created_at),
    KEY ix_orders_status (status, created_at),
    KEY ix_orders_city (served_city_id),
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES customers (id),
    CONSTRAINT fk_orders_city FOREIGN KEY (served_city_id) REFERENCES served_cities (id),
    CONSTRAINT ck_orders_status CHECK (status IN ('awaiting_acceptance', 'confirmed', 'in_collection',
        'out_for_delivery', 'delivered_paid', 'delivery_failed', 'cancelled')),
    CONSTRAINT ck_orders_payment_method CHECK (payment_method IN ('cash_on_delivery')),
    CONSTRAINT ck_orders_delivery_fee CHECK (delivery_fee >= 0),
    CONSTRAINT ck_orders_collected_amount CHECK (collected_amount IS NULL OR collected_amount >= 0),
    -- CA-F010-1 : « livrée et payée » => montant encaissé et date de réception enregistrés.
    CONSTRAINT ck_orders_delivered CHECK (status <> 'delivered_paid'
        OR (collected_amount IS NOT NULL AND received_at IS NOT NULL)),
    -- CA-F010-3 : échec de livraison => motif.
    CONSTRAINT ck_orders_failed CHECK (status <> 'delivery_failed' OR failure_reason IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ENT-009 SousCommande (F009, RG-003) : une par vendeur et par commande.
CREATE TABLE sub_orders (
    id                    BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    order_id              BIGINT UNSIGNED NOT NULL,
    seller_id             BIGINT UNSIGNED NOT NULL,
    status                VARCHAR(32)     NOT NULL DEFAULT 'new',
    refusal_reason        VARCHAR(500)    NULL COMMENT 'motifRefus',
    response_deadline_at  TIMESTAMP       NOT NULL COMMENT 'created_at + délai de réponse (paramètre, Q19) figé à la création — ajout technique',
    created_at            TIMESTAMP       NULL,
    updated_at            TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_sub_orders_order_seller (order_id, seller_id),
    KEY ix_sub_orders_seller (seller_id, status, created_at),
    KEY ix_sub_orders_deadline (status, response_deadline_at),
    CONSTRAINT fk_sub_orders_order FOREIGN KEY (order_id) REFERENCES orders (id),
    CONSTRAINT fk_sub_orders_seller FOREIGN KEY (seller_id) REFERENCES sellers (id),
    CONSTRAINT ck_sub_orders_status CHECK (status IN ('new', 'accepted', 'ready_for_pickup', 'collected',
        'refused', 'cancelled')),
    CONSTRAINT ck_sub_orders_refused CHECK (status <> 'refused' OR refusal_reason IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ENT-010 LigneCommande (F007, RG-007) : prix figé à la validation.
CREATE TABLE order_lines (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    sub_order_id        BIGINT UNSIGNED NOT NULL,
    product_id          BIGINT UNSIGNED NOT NULL,
    product_name        VARCHAR(200)    NOT NULL COMMENT 'Libellé figé (confirmation RG-026) — ajout technique',
    quantity            INT             NOT NULL,
    unit_price          DECIMAL(10,2)   NOT NULL COMMENT 'prixUnitaire figé (RG-007)',
    is_return_excluded  BOOLEAN         NOT NULL COMMENT 'Exclusion du retour figée à la validation (RG-019) — HYPOTHÈSE H-T02-1',
    created_at          TIMESTAMP       NULL,
    updated_at          TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_order_lines_sub_order_product (sub_order_id, product_id),
    UNIQUE KEY uq_order_lines_id_product (id, product_id),
    KEY ix_order_lines_product (product_id),
    CONSTRAINT fk_order_lines_sub_order FOREIGN KEY (sub_order_id) REFERENCES sub_orders (id),
    CONSTRAINT fk_order_lines_product FOREIGN KEY (product_id) REFERENCES products (id),
    CONSTRAINT ck_order_lines_quantity_positive CHECK (quantity > 0),
    CONSTRAINT ck_order_lines_unit_price_positive CHECK (unit_price > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------------------------------
-- CLASS-01 — avis (M08)
-- -----------------------------------------------------------------------------------------------------

-- ENT-020 Avis (F012, RG-011, RG-015, CA-F013-3). Un avis par ligne de commande (= par produit et par
-- commande, RG-011). product_id dupliqué pour le calcul de /noteMoyenne, cohérence garantie par la FK
-- composite (order_line_id, product_id).
CREATE TABLE reviews (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    customer_id     BIGINT UNSIGNED NOT NULL COMMENT 'Client rédige Avis',
    order_line_id   BIGINT UNSIGNED NOT NULL COMMENT 'Avis porte sur LigneCommande',
    product_id      BIGINT UNSIGNED NOT NULL,
    rating          TINYINT UNSIGNED NOT NULL COMMENT 'note 1..5 (HYPOTHÈSE F012)',
    comment         TEXT            NULL,
    is_hidden       BOOLEAN         NOT NULL DEFAULT FALSE COMMENT 'masqué (RG-015)',
    hidden_at       TIMESTAMP       NULL,
    created_at      TIMESTAMP       NULL,
    updated_at      TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_reviews_order_line (order_line_id),
    KEY ix_reviews_product_visible (product_id, is_hidden, rating),
    KEY ix_reviews_customer (customer_id),
    CONSTRAINT fk_reviews_customer FOREIGN KEY (customer_id) REFERENCES customers (id),
    CONSTRAINT fk_reviews_order_line FOREIGN KEY (order_line_id, product_id) REFERENCES order_lines (id, product_id),
    CONSTRAINT fk_reviews_product FOREIGN KEY (product_id) REFERENCES products (id),
    CONSTRAINT ck_reviews_rating_range CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT ck_reviews_hidden_at CHECK (is_hidden = FALSE OR hidden_at IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------------------------------
-- CLASS-02 — livraison, encaissement (M06)
-- -----------------------------------------------------------------------------------------------------

-- ENT-021 SociétéDeLivraison «externe» (D19, D38, C-05). Sans compte ni accès ; référentiel minimal pour
-- rattacher les remises de fonds (écart E-04).
CREATE TABLE delivery_partners (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name        VARCHAR(150)    NOT NULL,
    created_at  TIMESTAMP       NULL,
    updated_at  TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_delivery_partners_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ENT-019 RemiseDeFonds [I] (RG-020, ENF-008).
CREATE TABLE fund_remittances (
    id                    BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    delivery_partner_id   BIGINT UNSIGNED NOT NULL COMMENT 'SociétéDeLivraison remet',
    amount                DECIMAL(10,2)   NOT NULL,
    remitted_on           DATE            NOT NULL COMMENT 'date',
    recorded_by_user_id   BIGINT UNSIGNED NOT NULL COMMENT 'Administrateur (saisie, RG-029)',
    created_at            TIMESTAMP       NULL,
    updated_at            TIMESTAMP       NULL,
    PRIMARY KEY (id),
    KEY ix_fund_remittances_partner (delivery_partner_id, remitted_on),
    CONSTRAINT fk_fund_remittances_partner FOREIGN KEY (delivery_partner_id) REFERENCES delivery_partners (id),
    CONSTRAINT fk_fund_remittances_recorder FOREIGN KEY (recorded_by_user_id) REFERENCES users (id),
    CONSTRAINT ck_fund_remittances_amount CHECK (amount > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- RemiseDeFonds 0..* — 1..* Commande « rapprochée de » (RG-020).
CREATE TABLE fund_remittance_orders (
    fund_remittance_id  BIGINT UNSIGNED NOT NULL,
    order_id            BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (fund_remittance_id, order_id),
    KEY ix_fund_remittance_orders_order (order_id),
    CONSTRAINT fk_fro_remittance FOREIGN KEY (fund_remittance_id) REFERENCES fund_remittances (id),
    CONSTRAINT fk_fro_order FOREIGN KEY (order_id) REFERENCES orders (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ENT-019b Écart [I] (CA-F010-2, RG-020) : Commande 1 — 0..1 Écart. amount = encaissé − dû (signé, ≠ 0).
CREATE TABLE cash_discrepancies (
    id                    BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    order_id              BIGINT UNSIGNED NOT NULL,
    amount                DECIMAL(10,2)   NOT NULL,
    recorded_on           DATE            NOT NULL COMMENT 'date',
    recorded_by_user_id   BIGINT UNSIGNED NULL,
    created_at            TIMESTAMP       NULL,
    updated_at            TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_cash_discrepancies_order (order_id),
    CONSTRAINT fk_cash_discrepancies_order FOREIGN KEY (order_id) REFERENCES orders (id),
    CONSTRAINT fk_cash_discrepancies_recorder FOREIGN KEY (recorded_by_user_id) REFERENCES users (id),
    CONSTRAINT ck_cash_discrepancies_amount CHECK (amount <> 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------------------------------
-- CLASS-02 — reversements (M07)
-- -----------------------------------------------------------------------------------------------------

-- ENT-018 Reversement (F011, RG-018, CA-F011-2, CA-F011-5).
CREATE TABLE payouts (
    id                    BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    seller_id             BIGINT UNSIGNED NOT NULL COMMENT 'Vendeur reçoit Reversement',
    period_start          DATE            NOT NULL COMMENT 'Lundi de la semaine de reversement — idempotence (FR-031), ajout technique',
    paid_on               DATE            NOT NULL COMMENT 'date',
    amount                DECIMAL(10,2)   NOT NULL,
    method                VARCHAR(32)     NOT NULL COMMENT 'mode : ModeReversement',
    cash_proof            VARCHAR(255)    NULL COMMENT 'preuveRemise si espèces (HYPOTHÈSE F011)',
    recorded_by_user_id   BIGINT UNSIGNED NOT NULL,
    created_at            TIMESTAMP       NULL,
    updated_at            TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_payouts_seller_period (seller_id, period_start),
    KEY ix_payouts_seller_paid (seller_id, paid_on),
    CONSTRAINT fk_payouts_seller FOREIGN KEY (seller_id) REFERENCES sellers (id),
    CONSTRAINT fk_payouts_recorder FOREIGN KEY (recorded_by_user_id) REFERENCES users (id),
    CONSTRAINT ck_payouts_amount CHECK (amount > 0),
    CONSTRAINT ck_payouts_method CHECK (method IN ('bank_transfer', 'cash')),
    CONSTRAINT ck_payouts_cash_proof CHECK (method <> 'cash' OR cash_proof IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ENT-016 MontantVendeur [I] (F011, RG-012, RG-024, H-04) : LigneCommande 1 — 0..1 MontantVendeur.
-- seller_id dupliqué (calcul hebdomadaire par vendeur), écrit une fois par le service Montants (T-036).
CREATE TABLE seller_amounts (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    order_line_id   BIGINT UNSIGNED NOT NULL,
    seller_id       BIGINT UNSIGNED NOT NULL,
    amount          DECIMAL(10,2)   NOT NULL COMMENT 'quantité × prixUnitaire, sans commission (RG-005)',
    status          VARCHAR(32)     NOT NULL DEFAULT 'held',
    hold_until      TIMESTAMP       NOT NULL COMMENT '/dateDisponibilité = dateRéception + délai de retour (7 j), figée — RG-024',
    payout_id       BIGINT UNSIGNED NULL COMMENT 'inclus dans Reversement 0..1',
    created_at      TIMESTAMP       NULL,
    updated_at      TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_seller_amounts_order_line (order_line_id),
    KEY ix_seller_amounts_seller_status (seller_id, status),
    KEY ix_seller_amounts_release (status, hold_until),
    KEY ix_seller_amounts_payout (payout_id),
    CONSTRAINT fk_seller_amounts_order_line FOREIGN KEY (order_line_id) REFERENCES order_lines (id),
    CONSTRAINT fk_seller_amounts_seller FOREIGN KEY (seller_id) REFERENCES sellers (id),
    CONSTRAINT fk_seller_amounts_payout FOREIGN KEY (payout_id) REFERENCES payouts (id),
    CONSTRAINT ck_seller_amounts_amount CHECK (amount > 0),
    CONSTRAINT ck_seller_amounts_status CHECK (status IN ('held', 'available', 'paid_out', 'deducted')),
    CONSTRAINT ck_seller_amounts_paid_out CHECK ((status = 'paid_out') = (payout_id IS NOT NULL))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------------------------------
-- CLASS-02 — retours (M11)
-- -----------------------------------------------------------------------------------------------------

-- ENT-011 Retour (F022, RG-019, RG-022, RG-030). Table nommée product_returns (RETURN est un mot réservé).
-- LigneCommande 1 — 0..* Retour (WARN n_warn2) : Σ quantités <= quantité de la ligne, vérifié par le service.
CREATE TABLE product_returns (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    order_line_id       BIGINT UNSIGNED NOT NULL COMMENT 'un retour par produit (RG-030)',
    quantity            INT             NOT NULL,
    reason              VARCHAR(32)     NOT NULL COMMENT 'motif : MotifRetour',
    photo_file_id       BIGINT UNSIGNED NULL COMMENT 'photo [0..1] (HYPOTHÈSE)',
    refund_method       VARCHAR(32)     NOT NULL COMMENT 'moyenRemboursement',
    refund_details      TEXT            NOT NULL COMMENT 'coordonnéesRemboursement, chiffré (ADR-014, FR-055)',
    requested_at        TIMESTAMP       NOT NULL COMMENT 'dateDemande (RG-019 : <= received_at + 7 j, vérifié par le service)',
    status              VARCHAR(32)     NOT NULL DEFAULT 'requested',
    created_at          TIMESTAMP       NULL,
    updated_at          TIMESTAMP       NULL,
    PRIMARY KEY (id),
    KEY ix_product_returns_order_line (order_line_id),
    KEY ix_product_returns_status (status, requested_at),
    CONSTRAINT fk_product_returns_order_line FOREIGN KEY (order_line_id) REFERENCES order_lines (id),
    CONSTRAINT fk_product_returns_photo FOREIGN KEY (photo_file_id) REFERENCES photo_files (id),
    CONSTRAINT ck_product_returns_quantity CHECK (quantity > 0),
    CONSTRAINT ck_product_returns_reason CHECK (reason IN ('change_of_mind', 'defective', 'incorrect',
        'not_as_described')),
    CONSTRAINT ck_product_returns_refund_method CHECK (refund_method IN ('bank_transfer', 'other_traceable')),
    CONSTRAINT ck_product_returns_status CHECK (status IN ('requested', 'pickup_in_progress', 'picked_up',
        'verified_by_seller', 'disputed', 'in_dispute', 'customer_refunded', 'return_refused'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ENT-012 Vérification (RG-027, RG-017, D31, D43) : Retour 1 ◆— 0..1 Vérification.
CREATE TABLE return_inspections (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    product_return_id   BIGINT UNSIGNED NOT NULL,
    result              VARCHAR(32)     NOT NULL COMMENT 'RésultatVérification',
    dispute_reason      VARCHAR(500)    NULL COMMENT 'motifContestation',
    restock             BOOLEAN         NOT NULL COMMENT 'remiseEnVente (D43)',
    inspected_at        TIMESTAMP       NOT NULL COMMENT 'date',
    created_at          TIMESTAMP       NULL,
    updated_at          TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_return_inspections_return (product_return_id),
    CONSTRAINT fk_return_inspections_return FOREIGN KEY (product_return_id) REFERENCES product_returns (id),
    CONSTRAINT ck_return_inspections_result CHECK (result IN ('compliant', 'disputed')),
    CONSTRAINT ck_return_inspections_dispute CHECK (result <> 'disputed' OR dispute_reason IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ENT-013 Litige (RG-027, CA-F022-6) : Retour 1 ◆— 0..1 Litige. Ouvert à la contestation, décidé ensuite.
CREATE TABLE return_disputes (
    id                    BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    product_return_id     BIGINT UNSIGNED NOT NULL,
    opened_at             TIMESTAMP       NOT NULL,
    decision              VARCHAR(32)     NULL COMMENT 'décision (STATE-003 t7/t8) — écart E-08',
    decision_reason       VARCHAR(1000)   NULL,
    refunded_amount       DECIMAL(10,2)   NULL COMMENT 'montantRemboursé fixé par la décision',
    fee_charged_to        VARCHAR(32)     NULL COMMENT 'imputationFrais : ImputationFrais',
    decided_at            TIMESTAMP       NULL COMMENT 'date',
    decided_by_user_id    BIGINT UNSIGNED NULL,
    created_at            TIMESTAMP       NULL,
    updated_at            TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_return_disputes_return (product_return_id),
    KEY ix_return_disputes_open (decided_at),
    CONSTRAINT fk_return_disputes_return FOREIGN KEY (product_return_id) REFERENCES product_returns (id),
    CONSTRAINT fk_return_disputes_decider FOREIGN KEY (decided_by_user_id) REFERENCES users (id),
    CONSTRAINT ck_return_disputes_decision CHECK (decision IS NULL OR decision IN ('in_favor_of_customer',
        'in_favor_of_seller')),
    CONSTRAINT ck_return_disputes_fee CHECK (fee_charged_to IS NULL OR fee_charged_to IN ('customer', 'seller')),
    CONSTRAINT ck_return_disputes_amount CHECK (refunded_amount IS NULL OR refunded_amount >= 0),
    -- Une décision est complète ou absente.
    CONSTRAINT ck_return_disputes_decided CHECK (
        (decision IS NULL AND decided_at IS NULL AND decided_by_user_id IS NULL)
        OR (decision IS NOT NULL AND decided_at IS NOT NULL AND decided_by_user_id IS NOT NULL
            AND refunded_amount IS NOT NULL))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ENT-014 Remboursement (RG-022, CA-F022-5, ENF-008, ENF-012) : Retour 1 ◆— 0..1 Remboursement.
CREATE TABLE refunds (
    id                    BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    product_return_id     BIGINT UNSIGNED NOT NULL,
    amount                DECIMAL(10,2)   NOT NULL COMMENT 'prix − frais si changement d''avis (RG-022)',
    method                VARCHAR(32)     NOT NULL COMMENT 'moyen : MoyenRemboursement',
    reference             VARCHAR(100)    NOT NULL COMMENT 'référence de l''opération traçable',
    refunded_on           DATE            NOT NULL COMMENT 'date',
    recorded_by_user_id   BIGINT UNSIGNED NOT NULL,
    created_at            TIMESTAMP       NULL,
    updated_at            TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_refunds_return (product_return_id),
    CONSTRAINT fk_refunds_return FOREIGN KEY (product_return_id) REFERENCES product_returns (id),
    CONSTRAINT fk_refunds_recorder FOREIGN KEY (recorded_by_user_id) REFERENCES users (id),
    CONSTRAINT ck_refunds_amount CHECK (amount >= 0),
    CONSTRAINT ck_refunds_method CHECK (method IN ('bank_transfer', 'other_traceable'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ENT-015 FraisDeRetour (RG-025, D42) : Retour 1 — 0..1 FraisDeRetour. Montant = paramètre (Q45 MANQUANT).
CREATE TABLE return_fees (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    product_return_id   BIGINT UNSIGNED NOT NULL,
    amount              DECIMAL(10,2)   NOT NULL,
    charged_to          VARCHAR(32)     NOT NULL COMMENT 'imputéÀ : ImputationFrais',
    created_at          TIMESTAMP       NULL,
    updated_at          TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_return_fees_return (product_return_id),
    CONSTRAINT fk_return_fees_return FOREIGN KEY (product_return_id) REFERENCES product_returns (id),
    CONSTRAINT ck_return_fees_amount CHECK (amount >= 0),
    CONSTRAINT ck_return_fees_charged_to CHECK (charged_to IN ('customer', 'seller'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ENT-017 Déduction (RG-021, RG-025, CA-F011-3/4/5) : Retour 1 — 0..* Déduction ; régularisée sur 0..1
-- Reversement. payout_id NULL = déduction en attente (Σ déductions non encore imputées, CA-F011-5).
CREATE TABLE deductions (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    product_return_id   BIGINT UNSIGNED NOT NULL COMMENT 'Retour donne lieu à',
    seller_id           BIGINT UNSIGNED NOT NULL COMMENT 'dupliqué pour le calcul hebdomadaire',
    amount              DECIMAL(10,2)   NOT NULL,
    origin              VARCHAR(32)     NOT NULL COMMENT 'origine : remboursement | fraisDeRetour',
    deducted_on         DATE            NOT NULL COMMENT 'date',
    payout_id           BIGINT UNSIGNED NULL COMMENT 'régularisée sur Reversement 0..1',
    created_at          TIMESTAMP       NULL,
    updated_at          TIMESTAMP       NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_deductions_return_origin (product_return_id, origin),
    KEY ix_deductions_pending (seller_id, payout_id),
    KEY ix_deductions_payout (payout_id),
    CONSTRAINT fk_deductions_return FOREIGN KEY (product_return_id) REFERENCES product_returns (id),
    CONSTRAINT fk_deductions_seller FOREIGN KEY (seller_id) REFERENCES sellers (id),
    CONSTRAINT fk_deductions_payout FOREIGN KEY (payout_id) REFERENCES payouts (id),
    CONSTRAINT ck_deductions_amount CHECK (amount > 0),
    CONSTRAINT ck_deductions_origin CHECK (origin IN ('refund', 'return_fee'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
