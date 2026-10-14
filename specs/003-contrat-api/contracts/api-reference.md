# Référence des points d'accès par module (générée)

Générée par `tooling/build_contract.py` depuis la même table que `openapi.yaml`. Ne pas éditer à la main.
Rôles : V = visiteur, C = client, S = vendeur, A = administrateur ; (p) = propriété vérifiée.

## M01 — Comptes et accès

| Opération | Méthode et chemin | Rôles | UC | Matrice | Succès | Erreurs | Tâche |
|---|---|---|---|---|---|---|---|
| `registerCustomer` | `POST /api/v1/auth/register` | V | UC-004 | MX-01 | 201 | 409, 422 | T-014 |
| `login` | `POST /api/v1/auth/login` | V | UC-004, UC-010 | MX-01 | 200 | 401, 422 | T-014 |
| `logout` | `POST /api/v1/auth/logout` | C(p), S(p), A(p) | UC-004 | MX-01 | 204 | 401 | T-014 |
| `getMe` | `GET /api/v1/me` | C(p), S(p), A(p) | UC-004, UC-010 | MX-01 | 200 | 401 | T-006 |
| `registerSeller` | `POST /api/v1/auth/register-seller` | V | UC-010 | MX-01 | 201 | 409, 422 | T-016 |
| `listSellerCommunes` | `GET /api/v1/seller-communes` | V, C, S, A | UC-010 | MX-02 | 200 | 429 | T-017 |
| `getSellerProfile` | `GET /api/v1/seller/profile` | S(p) | UC-010 | MP-11 | 200 | 401, 403 | T-016 |
| `updateSellerProfile` | `PATCH /api/v1/seller/profile` | S(p) | UC-010 | MP-11 | 200 | 401, 403, 422 | T-016 |

## M02 — Boutique et catalogue vendeur

| Opération | Méthode et chemin | Rôles | UC | Matrice | Succès | Erreurs | Tâche |
|---|---|---|---|---|---|---|---|
| `updateShop` | `PATCH /api/v1/seller/shop` | S(p) | UC-010, UC-011 | MP-11 | 200 | 401, 403, 422 | T-016 |
| `listSellerProducts` | `GET /api/v1/seller/products` | S(p) | UC-011 | MP-11 | 200 | 400, 401, 403 | T-021 |
| `createSellerProduct` | `POST /api/v1/seller/products` | S(p) | UC-011 | MP-11 | 201 | 401, 403, 422 | T-021 |
| `getSellerProduct` | `GET /api/v1/seller/products/{productId}` | S(p) | UC-011 | MP-11 | 200 | 401, 403, 404 | T-021 |
| `updateSellerProduct` | `PATCH /api/v1/seller/products/{productId}` | S(p) | UC-011 | MP-11 | 200 | 401, 403, 404, 422 | T-021 |
| `deleteSellerProduct` | `DELETE /api/v1/seller/products/{productId}` | S(p) | UC-011 | MP-11 | 204 | 401, 403, 404 | T-021 |

## M03 — Découverte

| Opération | Méthode et chemin | Rôles | UC | Matrice | Succès | Erreurs | Tâche |
|---|---|---|---|---|---|---|---|
| `listProducts` | `GET /api/v1/products` | V, C, S, A | UC-001 | MP-01, MP-02 | 200 | 400, 429 | T-023 |
| `listCategories` | `GET /api/v1/categories` | V, C, S, A | UC-001 | MP-02 | 200 | 429 | T-023 |
| `getProduct` | `GET /api/v1/products/{productId}` | V, C, S, A | UC-002 | MP-01 | 200 | 404, 429 | T-024 |
| `listProductReviews` | `GET /api/v1/products/{productId}/reviews` | V, C, S, A | UC-002 | MP-01 | 200 | 400, 404, 429 | T-024 |

## M04 — Panier et commande

| Opération | Méthode et chemin | Rôles | UC | Matrice | Succès | Erreurs | Tâche |
|---|---|---|---|---|---|---|---|
| `getCart` | `GET /api/v1/cart` | V(p), C(p) | UC-003 | MP-03 | 200 | 403 | T-026 |
| `addCartItem` | `POST /api/v1/cart/items` | V(p), C(p) | UC-003 | MP-03 | 200 | 403, 409, 422 | T-026 |
| `updateCartItem` | `PATCH /api/v1/cart/items/{itemId}` | V(p), C(p) | UC-003 | MP-03 | 200 | 403, 404, 422 | T-026 |
| `removeCartItem` | `DELETE /api/v1/cart/items/{itemId}` | V(p), C(p) | UC-003 | MP-03 | 200 | 403, 404 | T-026 |
| `listServedCities` | `GET /api/v1/served-cities` | V, C, S, A | UC-005 | MX-02 | 200 | 429 | T-017 |
| `previewOrder` | `POST /api/v1/orders/preview` | C | UC-005 | MP-04 | 200 | 401, 403, 422 | T-028 |
| `createOrder` | `POST /api/v1/orders` | C | UC-005 | MP-04 | 201 | 401, 403, 409, 422 | T-028 |
| `listMyOrders` | `GET /api/v1/orders` | C(p) | UC-006 | MP-05 | 200 | 400, 401, 403 | T-030 |
| `getMyOrder` | `GET /api/v1/orders/{orderId}` | C(p) | UC-006, UC-009 | MP-05 | 200 | 401, 403, 404 | T-030 |
| `cancelMyOrder` | `POST /api/v1/orders/{orderId}/cancel` | C(p) | UC-007 | MP-05 | 200 | 401, 403, 404, 409 | T-030 |
| `getOrderConfirmation` | `GET /api/v1/orders/{orderId}/confirmation` | C(p) | UC-005 | MP-05 | 200 | 401, 403, 404 | T-029 |

## M05 — Commandes vendeur

| Opération | Méthode et chemin | Rôles | UC | Matrice | Succès | Erreurs | Tâche |
|---|---|---|---|---|---|---|---|
| `listSellerSubOrders` | `GET /api/v1/seller/sub-orders` | S(p) | UC-012 | MP-12 | 200 | 400, 401, 403 | T-033 |
| `getSellerSubOrder` | `GET /api/v1/seller/sub-orders/{subOrderId}` | S(p) | UC-012 | MP-12 | 200 | 401, 403, 404 | T-033 |
| `acceptSubOrder` | `POST /api/v1/seller/sub-orders/{subOrderId}/accept` | S(p) | UC-012 | MP-12 | 200 | 401, 403, 404, 409 | T-033 |
| `refuseSubOrder` | `POST /api/v1/seller/sub-orders/{subOrderId}/refuse` | S(p) | UC-012 | MP-12 | 200 | 401, 403, 404, 409, 422 | T-033 |
| `markSubOrderReady` | `POST /api/v1/seller/sub-orders/{subOrderId}/ready` | S(p) | UC-012 | MP-12 | 200 | 401, 403, 404, 409 | T-033 |

## M06 — Livraison et encaissement

| Opération | Méthode et chemin | Rôles | UC | Matrice | Succès | Erreurs | Tâche |
|---|---|---|---|---|---|---|---|
| `adminListOrders` | `GET /api/v1/admin/orders` | A | UC-015, UC-023 | MP-05, MX-04 | 200 | 400, 401, 403 | T-037 |
| `adminGetOrder` | `GET /api/v1/admin/orders/{orderId}` | A | UC-015, UC-016, UC-023 | MP-05, MX-04 | 200 | 401, 403, 404 | T-041 |
| `adminHandoverOrder` | `POST /api/v1/admin/orders/{orderId}/handover` | A | UC-015 | MP-13 | 200 | 401, 403, 404, 409 | T-037 |
| `adminMarkSubOrderCollected` | `POST /api/v1/admin/sub-orders/{subOrderId}/collected` | A | UC-016 | MP-13 | 200 | 401, 403, 404, 409 | T-037 |
| `adminMarkOutForDelivery` | `POST /api/v1/admin/orders/{orderId}/out-for-delivery` | A | UC-016 | MP-13 | 200 | 401, 403, 404, 409 | T-037 |
| `adminMarkDeliveredPaid` | `POST /api/v1/admin/orders/{orderId}/delivered-paid` | A | UC-016 | MP-13 | 200 | 401, 403, 404, 409, 422 | T-038 |
| `adminMarkDeliveryFailed` | `POST /api/v1/admin/orders/{orderId}/delivery-failed` | A | UC-016 | MP-13 | 200 | 401, 403, 404, 409, 422 | T-038 |
| `adminCancelOrder` ⛔ | `POST /api/v1/admin/orders/{orderId}/cancel` | A | UC-023 | MP-05 | 200 | 401, 403, 404, 422, 501 | T-060 |
| `adminAcceptSubOrder` ⚠️H | `POST /api/v1/admin/sub-orders/{subOrderId}/accept` | A | UC-023 | MP-12 | 200 | 401, 403, 404, 409 | T-060 |
| `adminRefuseSubOrder` ⚠️H | `POST /api/v1/admin/sub-orders/{subOrderId}/refuse` | A | UC-023 | MP-12 | 200 | 401, 403, 404, 409, 422 | T-060 |
| `adminMarkSubOrderReady` ⚠️H | `POST /api/v1/admin/sub-orders/{subOrderId}/ready` | A | UC-023 | MP-12 | 200 | 401, 403, 404, 409 | T-060 |
| `adminListDeliveryPartners` | `GET /api/v1/admin/delivery-partners` | A | UC-017 | MP-13 | 200 | 401, 403 | T-039 |
| `adminCreateDeliveryPartner` ⚠️H | `POST /api/v1/admin/delivery-partners` | A | UC-017 | MP-13 | 201 | 401, 403, 409, 422 | T-039 |
| `adminCreateFundRemittance` | `POST /api/v1/admin/fund-remittances` | A | UC-017 | MP-13 | 201 | 401, 403, 422 | T-039 |
| `adminListFundRemittances` | `GET /api/v1/admin/fund-remittances` | A | UC-017 | MP-13, MX-04 | 200 | 400, 401, 403 | T-039 |
| `adminListCashDiscrepancies` | `GET /api/v1/admin/cash-discrepancies` | A | UC-017 | MP-13, MX-04 | 200 | 400, 401, 403 | T-038 |

## M07 — Reversements vendeurs

| Opération | Méthode et chemin | Rôles | UC | Matrice | Succès | Erreurs | Tâche |
|---|---|---|---|---|---|---|---|
| `sellerGetAmountsSummary` | `GET /api/v1/seller/amounts/summary` | S(p) | UC-014 | MP-14 | 200 | 401, 403 | T-055 |
| `sellerListAmounts` | `GET /api/v1/seller/amounts` | S(p) | UC-014 | MP-14 | 200 | 400, 401, 403 | T-055 |
| `sellerListDeductions` | `GET /api/v1/seller/deductions` | S(p) | UC-014 | MP-14 | 200 | 400, 401, 403 | T-048 |
| `sellerListPayouts` | `GET /api/v1/seller/payouts` | S(p) | UC-014 | MP-14 | 200 | 400, 401, 403 | T-055 |
| `adminListSellerAmounts` | `GET /api/v1/admin/seller-amounts` | A | UC-023 | MP-14, MX-04 | 200 | 400, 401, 403 | T-059 |
| `adminPreviewPayouts` | `GET /api/v1/admin/payouts/preview` | A | UC-020 | MP-15 | 200 | 400, 401, 403 | T-054 |
| `adminCreatePayout` | `POST /api/v1/admin/payouts` | A | UC-020 | MP-15 | 201 | 401, 403, 409, 422 | T-054 |
| `adminListPayouts` | `GET /api/v1/admin/payouts` | A | UC-020, UC-023 | MP-15, MX-04 | 200 | 400, 401, 403 | T-054 |

## M08 — Avis et notes

| Opération | Méthode et chemin | Rôles | UC | Matrice | Succès | Erreurs | Tâche |
|---|---|---|---|---|---|---|---|
| `upsertReview` | `PUT /api/v1/order-lines/{orderLineId}/review` | C(p) | UC-009 | MP-10 | 200, 201 | 401, 403, 404, 422 | T-056 |

## M09 — Administration et modération

| Opération | Méthode et chemin | Rôles | UC | Matrice | Succès | Erreurs | Tâche |
|---|---|---|---|---|---|---|---|
| `adminListCategories` | `GET /api/v1/admin/categories` | A | UC-021 | MP-17 | 200 | 401, 403 | T-017 |
| `adminCreateCategory` | `POST /api/v1/admin/categories` | A | UC-021 | MP-17 | 201 | 401, 403, 409, 422 | T-017 |
| `adminUpdateCategory` | `PATCH /api/v1/admin/categories/{id}` | A | UC-021 | MP-17 | 200 | 401, 403, 404, 409, 422 | T-017 |
| `adminDeleteCategory` | `DELETE /api/v1/admin/categories/{id}` | A | UC-021 | MP-17 | 204 | 401, 403, 404, 409 | T-017 |
| `adminListServedCities` | `GET /api/v1/admin/served-cities` | A | UC-021 | MP-17 | 200 | 401, 403 | T-017 |
| `adminCreateServedCity` | `POST /api/v1/admin/served-cities` | A | UC-021 | MP-17 | 201 | 401, 403, 409, 422 | T-017 |
| `adminUpdateServedCity` | `PATCH /api/v1/admin/served-cities/{id}` | A | UC-021 | MP-17 | 200 | 401, 403, 404, 409, 422 | T-017 |
| `adminDeleteServedCity` | `DELETE /api/v1/admin/served-cities/{id}` | A | UC-021 | MP-17 | 204 | 401, 403, 404, 409 | T-017 |
| `adminListSellerCommunes` | `GET /api/v1/admin/seller-communes` | A | UC-021 | MP-17 | 200 | 401, 403 | T-017 |
| `adminCreateSellerCommune` | `POST /api/v1/admin/seller-communes` | A | UC-021 | MP-17 | 201 | 401, 403, 409, 422 | T-017 |
| `adminUpdateSellerCommune` | `PATCH /api/v1/admin/seller-communes/{id}` | A | UC-021 | MP-17 | 200 | 401, 403, 404, 409, 422 | T-017 |
| `adminDeleteSellerCommune` | `DELETE /api/v1/admin/seller-communes/{id}` | A | UC-021 | MP-17 | 204 | 401, 403, 404, 409 | T-017 |
| `adminHideProduct` | `POST /api/v1/admin/products/{productId}/hide` | A | UC-022 | MP-16, MP-11 | 200 | 401, 403, 404, 422 | T-058 |
| `adminUnhideProduct` ⚠️H | `POST /api/v1/admin/products/{productId}/unhide` | A | UC-022 | MP-16, MP-11 | 200 | 401, 403, 404 | T-058 |
| `adminSuspendSeller` | `POST /api/v1/admin/sellers/{sellerId}/suspend` | A | UC-022 | MP-16 | 200 | 401, 403, 404, 409, 422 | T-058 |
| `adminReactivateSeller` ⚠️H | `POST /api/v1/admin/sellers/{sellerId}/reactivate` | A | UC-022 | MP-16 | 200 | 401, 403, 404, 409 | T-058 |
| `adminListReviews` | `GET /api/v1/admin/reviews` | A | UC-022 | MP-16 | 200 | 400, 401, 403 | T-058 |
| `adminHideReview` | `POST /api/v1/admin/reviews/{reviewId}/hide` | A | UC-022 | MP-16 | 200 | 401, 403, 404, 422 | T-058 |
| `adminUnhideReview` ⚠️H | `POST /api/v1/admin/reviews/{reviewId}/unhide` | A | UC-022 | MP-16 | 200 | 401, 403, 404 | T-058 |
| `adminListSellers` | `GET /api/v1/admin/sellers` | A | UC-023 | MX-04 | 200 | 400, 401, 403 | T-059 |
| `adminGetSeller` | `GET /api/v1/admin/sellers/{sellerId}` | A | UC-023 | MX-04 | 200 | 401, 403, 404 | T-059 |
| `adminListProducts` | `GET /api/v1/admin/products` | A | UC-023, UC-022 | MX-04, MP-16 | 200 | 400, 401, 403 | T-059 |

## M10 — Notifications

| Opération | Méthode et chemin | Rôles | UC | Matrice | Succès | Erreurs | Tâche |
|---|---|---|---|---|---|---|---|
| `listNotifications` | `GET /api/v1/notifications` | C(p), S(p), A(p) | UC-006 | MX-03 | 200 | 400, 401 | T-009 |
| `markNotificationRead` | `POST /api/v1/notifications/{notificationId}/read` | C(p), S(p), A(p) | UC-006 | MX-03 | 204 | 401, 404 | T-009 |

## M11 — Retours

| Opération | Méthode et chemin | Rôles | UC | Matrice | Succès | Erreurs | Tâche |
|---|---|---|---|---|---|---|---|
| `getReturnEligibility` | `GET /api/v1/orders/{orderId}/return-eligibility` | C(p) | UC-008 | MP-06 | 200 | 401, 403, 404 | T-042 |
| `createReturn` | `POST /api/v1/returns` | C(p) | UC-008 | MP-06 | 201 | 401, 403, 422 | T-043 |
| `listMyReturns` | `GET /api/v1/returns` | C(p) | UC-008 | MP-06 | 200 | 400, 401, 403 | T-043 |
| `getMyReturn` | `GET /api/v1/returns/{returnId}` | C(p) | UC-008 | MP-06 | 200 | 401, 403, 404 | T-043 |
| `sellerListReturns` | `GET /api/v1/seller/returns` | S(p) | UC-013 | MP-07 | 200 | 400, 401, 403 | T-045 |
| `sellerGetReturn` | `GET /api/v1/seller/returns/{returnId}` | S(p) | UC-013 | MP-07 | 200 | 401, 403, 404 | T-045 |
| `sellerInspectReturn` | `POST /api/v1/seller/returns/{returnId}/inspection` | S(p) | UC-013 | MP-07 | 200 | 401, 403, 404, 409, 422 | T-045 |
| `adminListReturns` | `GET /api/v1/admin/returns` | A | UC-019, UC-023 | MP-09, MX-04 | 200 | 400, 401, 403 | T-052 |
| `adminGetReturn` | `GET /api/v1/admin/returns/{returnId}` | A | UC-018, UC-019, UC-023 | MP-08, MP-09, MX-04 | 200 | 401, 403, 404 | T-052 |
| `adminRequestReturnPickup` | `POST /api/v1/admin/returns/{returnId}/pickup-requested` | A | UC-016 | MP-13 | 200 | 401, 403, 404, 409 | T-044 |
| `adminMarkReturnPickedUp` | `POST /api/v1/admin/returns/{returnId}/picked-up` | A | UC-016 | MP-13 | 200 | 401, 403, 404, 409 | T-044 |
| `adminInspectReturn` ⛔ | `POST /api/v1/admin/returns/{returnId}/inspection` | A | UC-023 | MP-07 | 200 | 401, 403, 404, 422, 501 | T-046 |
| `adminDecideDispute` | `POST /api/v1/admin/returns/{returnId}/dispute-decision` | A | UC-018 | MP-08, MP-07 | 200 | 401, 403, 404, 409, 422 | T-047 |
| `adminRecordRefund` | `POST /api/v1/admin/returns/{returnId}/refund` | A | UC-019 | MP-09 | 200 | 401, 403, 404, 409, 422 | T-049 |

## SOCLE — Socle transverse (paramètres, photos, audit)

| Opération | Méthode et chemin | Rôles | UC | Matrice | Succès | Erreurs | Tâche |
|---|---|---|---|---|---|---|---|
| `uploadPhoto` | `POST /api/v1/photos` | C(p), S(p) | UC-011, UC-008 | MP-11, MP-06 | 201 | 401, 403, 422 | T-020 |
| `adminListAuditEntries` | `GET /api/v1/admin/audit-entries` | A | UC-023 | MX-04 | 200 | 400, 401, 403 | T-008 |
| `adminListSettings` | `GET /api/v1/admin/settings` | A | UC-023 | MX-05 | 200 | 401, 403 | T-007 |
| `adminUpdateSetting` | `PATCH /api/v1/admin/settings/{key}` | A | UC-023 | MX-05 | 200 | 401, 403, 404, 422 | T-007 |

⛔ = contrat réservé, implémentation bloquée (x-blocked-by) ; ⚠️H = HYPOTHÈSE (x-hypothesis).
