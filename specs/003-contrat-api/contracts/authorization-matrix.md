# Matrice rôle × action (générée)

Générée par `tooling/build_contract.py` ; source machine : `authorization-matrix.yaml` (ADR-017).
MP-xx = ligne de la matrice du cahier §5 (texte repris tel quel) ; MX-xx = capacité dérivée, absente de §5 mais exigée par une fonction ou une ENF.

Règle d'application (ADR-017) : rôle non autorisé → 403 `forbidden` ; ressource d'un autre titulaire → 404 `not_found` ; société de livraison : aucun accès (D38).

| Ligne | Capacité | Visiteur | Client | Vendeur | Admin | Opérations | Note |
|---|---|---|---|---|---|---|---|
| MP-01 | Consulter le catalogue, les fiches produits, les avis | ✔ | ✔ | ✔ | ✔ | 3 : `listProducts`, `getProduct`, `listProductReviews` | §5 |
| MP-02 | Rechercher / filtrer par catégorie | ✔ | ✔ | ✔ | ✔ | 2 : `listProducts`, `listCategories` | §5 |
| MP-03 | Gérer un panier | ✔ (HYP.) | ✔ (siens) | — | — | 4 : `getCart`, `addCartItem`, `updateCartItem`, `removeCartItem` | Visiteur : HYPOTHÈSE H-01 |
| MP-04 | Passer commande (compte obligatoire) | — | ✔ | — | — | 2 : `previewOrder`, `createOrder` | RG-028, D41 |
| MP-05 | Suivre / annuler ses commandes | — | ✔ (siens) | — | ✔ | 7 : `listMyOrders`, `getMyOrder`, `cancelMyOrder`, `getOrderConfirmation`, `adminListOrders`, `adminGetOrder`, `adminCancelOrder` | Annulation administrateur bloquée (U-02) |
| MP-06 | Demander le retour d'un produit reçu (7 jours, tout motif) | — | ✔ (siens) | — | — | 5 : `uploadPhoto`, `getReturnEligibility`, `createReturn`, `listMyReturns`, `getMyReturn` | §5 |
| MP-07 | Vérifier un produit retourné (conforme / contesté) et décider de sa remise en vente | — | — | ✔ (siens) | ✔ | 5 : `sellerListReturns`, `sellerGetReturn`, `sellerInspectReturn`, `adminInspectReturn`, `adminDecideDispute` | Admin : en cas de litige ou d'absence de vérification (U-01, Q44) |
| MP-08 | Arbitrer un litige de retour | — | — | — | ✔ | 2 : `adminGetReturn`, `adminDecideDispute` | §5 |
| MP-09 | Enregistrer un remboursement client | — | — | — | ✔ | 3 : `adminListReturns`, `adminGetReturn`, `adminRecordRefund` | §5 |
| MP-10 | Laisser un avis / une note | — | ✔ (siens) | — | — | 1 : `upsertReview` | Produit reçu uniquement (RG-011) |
| MP-11 | Créer / modifier sa boutique et ses produits (dont caractère périssable/personnalisé) | — | — | ✔ (siens) | ✔ | 11 : `getSellerProfile`, `updateSellerProfile`, `updateShop`, `uploadPhoto`, `listSellerProducts`, `createSellerProduct`, `getSellerProduct`, `updateSellerProduct`, `deleteSellerProduct`, `adminHideProduct`, `adminUnhideProduct` | Admin : modération |
| MP-12 | Accepter / refuser / préparer une sous-commande | — | — | ✔ (siens) | ✔ | 8 : `listSellerSubOrders`, `getSellerSubOrder`, `acceptSubOrder`, `refuseSubOrder`, `markSubOrderReady`, `adminAcceptSubOrder`, `adminRefuseSubOrder`, `adminMarkSubOrderReady` | §5 |
| MP-13 | Saisir collecte, livraison, encaissement, reprise de retour | — | — | — | ✔ | 12 : `adminHandoverOrder`, `adminMarkSubOrderCollected`, `adminMarkOutForDelivery`, `adminMarkDeliveredPaid`, `adminMarkDeliveryFailed`, `adminListDeliveryPartners`, `adminCreateDeliveryPartner`, `adminCreateFundRemittance`, `adminListFundRemittances`, `adminListCashDiscrepancies`, `adminRequestReturnPickup`, `adminMarkReturnPickedUp` | Admin seul (RG-029, D38) |
| MP-14 | Consulter ses montants retenus, disponibles, reversés et déduits | — | — | ✔ (siens) | ✔ | 5 : `sellerGetAmountsSummary`, `sellerListAmounts`, `sellerListDeductions`, `sellerListPayouts`, `adminListSellerAmounts` | §5 |
| MP-15 | Enregistrer un reversement hebdomadaire (virement ou espèces) | — | — | — | ✔ | 3 : `adminPreviewPayouts`, `adminCreatePayout`, `adminListPayouts` | §5 |
| MP-16 | Masquer un produit / suspendre un vendeur / masquer un avis | — | — | — | ✔ | 8 : `adminHideProduct`, `adminUnhideProduct`, `adminSuspendSeller`, `adminReactivateSeller`, `adminListReviews`, `adminHideReview`, `adminUnhideReview`, `adminListProducts` | §5 |
| MP-17 | Gérer les catégories (dont exclusions de retour), la zone clients et la liste des communes vendeurs | — | — | — | ✔ | 12 : `adminListCategories`, `adminCreateCategory`, `adminUpdateCategory`, `adminDeleteCategory`, `adminListServedCities`, `adminCreateServedCity`, `adminUpdateServedCity`, `adminDeleteServedCity`, `adminListSellerCommunes`, `adminCreateSellerCommune`, `adminUpdateSellerCommune`, `adminDeleteSellerCommune` | §5 |
| MX-01 | S'inscrire, se connecter, se déconnecter, consulter son compte | ✔ | ✔ (siens) | ✔ (siens) | ✔ (siens) | 5 : `registerCustomer`, `login`, `logout`, `getMe`, `registerSeller` | Inscription : visiteur ; déconnexion et compte : titulaire |
| MX-02 | Consulter les référentiels publics (villes desservies, communes vendeurs) | ✔ | ✔ | ✔ | ✔ | 2 : `listSellerCommunes`, `listServedCities` | Nécessaire aux formulaires d'inscription et de commande |
| MX-03 | Consulter ses notifications internes | — | ✔ (siens) | ✔ (siens) | ✔ (siens) | 2 : `listNotifications`, `markNotificationRead` | F014, T-009 |
| MX-04 | Superviser vendeurs, produits, commandes, retours, montants et journal d'audit | — | — | — | ✔ (HYP.) | 12 : `adminListOrders`, `adminGetOrder`, `adminListFundRemittances`, `adminListCashDiscrepancies`, `adminListReturns`, `adminGetReturn`, `adminListSellerAmounts`, `adminListPayouts`, `adminListSellers`, `adminGetSeller`, `adminListProducts`, `adminListAuditEntries` | Périmètre de supervision : HYPOTHÈSE (F013) |
| MX-05 | Gérer les paramètres métier | — | — | — | ✔ | 2 : `adminListSettings`, `adminUpdateSetting` | H-08, T-007 |
