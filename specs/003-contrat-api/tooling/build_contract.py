#!/usr/bin/env python3
"""Générateur du contrat d'API T-003 (outil de documentation, pas du code applicatif).

Produit, à partir d'une seule table de définition :
  - contracts/openapi.yaml              (OpenAPI 3.1, référence du contrat)
  - contracts/authorization-matrix.yaml (matrice rôle x action, lisible par les tests T-066)
  - contracts/api-reference.md          (index des points d'accès par module)

Usage :  uv run --no-project --with pyyaml python tooling/build_contract.py
Après la validation CP-1 par @user, le fichier openapi.yaml devient la référence ; toute
modification passe par ce générateur OU directement dans le YAML, puis par
validation/check_contract.py.
"""
from __future__ import annotations

import copy
import json
import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"
ALL_ROLES = ["visitor", "customer", "seller", "admin"]
BASE = "/api/v1"

# ---------------------------------------------------------------------------
# Schémas (helpers)
# ---------------------------------------------------------------------------

def ref(name):
    return {"$ref": f"#/components/schemas/{name}"}


def s(**kw):
    d = {"type": "string"}
    d.update(kw)
    return d


def i(**kw):
    d = {"type": "integer", "format": "int64"}
    d.update(kw)
    return d


B = {"type": "boolean"}
DT = s(format="date-time")
D = s(format="date")
ID = ref("Id")
MONEY = ref("Money")


def arr(items, **kw):
    d = {"type": "array", "items": items}
    d.update(kw)
    return d


def obj(props, required=None, **kw):
    d = {"type": "object", "properties": props, "additionalProperties": False}
    if required is None:
        required = list(props.keys())
    if required:
        d["required"] = required
    d.update(kw)
    return d


def null(x):
    if "$ref" in x:
        return {"anyOf": [x, {"type": "null"}]}
    y = copy.deepcopy(x)
    t = y.get("type")
    if isinstance(t, str):
        y["type"] = [t, "null"]
    if "enum" in y:
        y["enum"] = list(y["enum"]) + [None]
    return y


def enum(*vals, **kw):
    return s(enum=list(vals), **kw)


SCHEMAS = {
    "Id": i(minimum=1, description="Identifiant numérique (ADR-010)."),
    "Money": s(pattern=r"^-?\d{1,8}\.\d{2}$",
               description="Montant en MAD, chaîne décimale à 2 décimales, jamais un flottant (ADR-011, ADR-018)."),
    "Phone": s(pattern=r"^\+[1-9]\d{6,14}$", description="Téléphone au format E.164 (RG-014, H-T02)."),
    "Role": enum("customer", "seller", "admin"),
    "OrderStatus": enum("awaiting_acceptance", "confirmed", "in_collection", "out_for_delivery",
                        "delivered_paid", "delivery_failed", "cancelled",
                        description="StatutCommande (STATE-001, data-model T-002 §4)."),
    "SubOrderStatus": enum("new", "accepted", "ready_for_pickup", "collected", "refused", "cancelled",
                           description="StatutSousCommande (STATE-002)."),
    "PayoutMethod": enum("bank_transfer", "cash", description="ModeReversement."),
    "ReturnStatus": enum("requested", "pickup_in_progress", "picked_up", "verified_by_seller", "disputed",
                         "in_dispute", "customer_refunded", "return_refused", description="StatutRetour (STATE-003)."),
    "ReturnReason": enum("change_of_mind", "defective", "incorrect", "not_as_described", description="MotifRetour."),
    "SellerAmountStatus": enum("held", "available", "paid_out", "deducted", description="StatutMontant (STATE-004)."),
    "RefundMethod": enum("bank_transfer", "other_traceable",
                         description="MoyenRemboursement ; aucune valeur « espèces » (RG-022). Liste détaillée : Q42."),
    "FeeChargedTo": enum("customer", "seller", description="ImputationFrais."),
    "InspectionResult": enum("compliant", "disputed", description="RésultatVérification."),
    "DisputeDecision": enum("in_favor_of_customer", "in_favor_of_seller"),
    "SellerStatus": enum("active", "suspended"),
    "DeductionOrigin": enum("refund", "return_fee"),
    "ReturnIneligibility": enum("order_not_delivered", "window_expired", "product_excluded", "category_excluded",
                                "fully_returned",
                                description="Raison de non-éligibilité au retour (CA-F022-2/3/8). "
                                            "product_excluded = signalé périssable ou personnalisé par le vendeur."),
    "CancellationCause": enum("customer_request", "seller_refusal", "admin_decision",
                              description="Cause d'annulation affichée au client (CA-F014-2). Le délai de réponse "
                                          "dépassé est un refus (RG-011b, H-02). admin_decision : bloqué (U-02)."),
    "Error": obj({
        "error": obj({
            "code": s(description="Code stable en anglais (catalogue : contracts/error-codes.md)."),
            "message": s(description="Message explicite en français, affichable."),
            "details": {"type": "object", "description": "Optionnel, structuré ; jamais de donnée sensible."},
        }, required=["code", "message"]),
    }),
    "PaginationMeta": obj({"page": i(minimum=1), "per_page": i(minimum=1), "total": i(minimum=0),
                           "total_pages": i(minimum=0)}),
    "UserSummary": obj({"id": ID, "role": ref("Role"), "phone": ref("Phone")}),
    "AuthToken": obj({"token": s(description="Jeton porteur opaque (ADR-006). Jamais journalisé."),
                      "token_type": enum("Bearer"), "expires_at": DT, "user": ref("UserSummary")}),
    "Me": obj({"user": ref("UserSummary"),
               "customer": null(obj({"id": ID, "name": s(), "email": null(s(format="email"))})),
               "seller": null(obj({"id": ID, "legal_name": s(), "status": ref("SellerStatus"), "shop_id": ID}))}),
    "RegisterCustomerRequest": obj({
        "name": s(minLength=1, maxLength=150), "phone": ref("Phone"),
        "password": s(minLength=8, writeOnly=True, description="Écriture seule ; jamais renvoyé (FR-054)."),
        "email": null(s(format="email", description="[NEEDS CLARIFICATION: e-mail obligatoire ou non — F001, M-06]")),
    }, required=["name", "phone", "password"]),
    "LoginRequest": obj({"phone": ref("Phone"), "password": s(writeOnly=True)}),
    "ReferenceItem": obj({"id": ID, "name": s()}),
    "ReferenceItemWrite": obj({"name": s(minLength=1, maxLength=150)}),
    "Category": obj({"id": ID, "name": s(), "is_return_excluded": B}),
    "CategoryWrite": obj({"name": s(minLength=1, maxLength=150), "is_return_excluded": B},
                         required=["name", "is_return_excluded"]),
    "CategoryPatch": obj({"name": s(minLength=1, maxLength=150), "is_return_excluded": B}, required=[]),
    "Shop": obj({"id": ID, "name": s(), "description": null(s()), "pickup_address": s()}),
    "ShopWrite": obj({"name": s(minLength=1), "description": null(s()), "pickup_address": s(minLength=1)},
                     required=["name", "pickup_address"]),
    "ShopPatch": obj({"name": s(minLength=1), "description": null(s()), "pickup_address": s(minLength=1)},
                     required=[]),
    "RegisterSellerRequest": obj({
        "phone": ref("Phone"), "password": s(minLength=8, writeOnly=True),
        "legal_name": s(minLength=1, description="Identité / raison sociale. Autres champs : [NEEDS CLARIFICATION: Q22]"),
        "seller_commune_id": ID, "payout_method": ref("PayoutMethod"),
        "bank_details": null(s(description="Requis si payout_method = bank_transfer (CA-F002-2). Chiffré (ADR-014).")),
        "shop": ref("ShopWrite"),
    }, required=["phone", "password", "legal_name", "seller_commune_id", "payout_method", "shop"]),
    "SellerProfile": obj({
        "id": ID, "legal_name": s(), "phone": ref("Phone"), "seller_commune": ref("ReferenceItem"),
        "payout_method": ref("PayoutMethod"),
        "bank_details": null(s(description="Visible du seul titulaire et de l'administrateur (FR-055).")),
        "status": ref("SellerStatus"), "shop": ref("Shop")}),
    "SellerProfilePatch": obj({"payout_method": ref("PayoutMethod"), "bank_details": null(s())}, required=[]),
    "PhotoFile": obj({"id": ID, "mime_type": s(), "size_bytes": i(minimum=1), "mobile_url": s(format="uri")}),
    "ProductPhoto": obj({"photo_file_id": ID, "position": i(minimum=0), "mobile_url": s(format="uri")}),
    "ReturnPolicy": obj({
        "window_days": i(minimum=0, description="Paramètre, 7 j (D25)."),
        "change_of_mind_fee": null(ref("Money")),
        "is_excluded": B,
        "exclusion_reason": null(enum("product_excluded", "category_excluded")),
    }, description="Conditions de retour affichées (RG-019, CA-F005-1). Frais : paramètre Q45 (null tant que non fixé)."),
    "ProductCard": obj({
        "id": ID, "name": s(), "price": MONEY, "main_photo_url": null(s(format="uri")),
        "shop": obj({"id": ID, "name": s()}), "average_rating": null({"type": "number", "minimum": 1, "maximum": 5}),
        "review_count": i(minimum=0), "is_available": B}),
    "ProductDetail": obj({
        "id": ID, "name": s(), "description": s(), "price": MONEY, "origin": null(s()),
        "category": ref("Category"), "photos": arr(ref("ProductPhoto")),
        "shop": obj({"id": ID, "name": s(), "commune": s()}),
        "average_rating": null({"type": "number", "minimum": 1, "maximum": 5}), "review_count": i(minimum=0),
        "is_available": B, "return_policy": ref("ReturnPolicy")}),
    "Review": obj({"id": ID, "product_id": ID, "rating": i(minimum=1, maximum=5), "comment": null(s()),
                   "created_at": DT, "updated_at": DT}),
    "ReviewWrite": obj({"rating": i(minimum=1, maximum=5), "comment": null(s(maxLength=2000))}, required=["rating"]),
    "AdminReview": obj({"id": ID, "product_id": ID, "order_line_id": ID, "customer_id": ID,
                        "rating": i(minimum=1, maximum=5), "comment": null(s()), "is_hidden": B,
                        "hidden_at": null(DT), "created_at": DT}),
    "SellerProduct": obj({
        "id": ID, "name": s(), "description": s(), "price": MONEY, "stock": i(minimum=0), "category_id": ID,
        "origin": null(s()), "is_perishable": B, "is_customized": B, "is_published": B,
        "is_hidden": B, "photos": arr(ref("ProductPhoto")), "created_at": DT, "updated_at": DT}),
    "ProductWrite": obj({
        "name": s(minLength=1, maxLength=200), "description": s(minLength=1),
        "price": MONEY, "stock": i(minimum=0), "category_id": ID, "origin": null(s()),
        "is_perishable": B, "is_customized": B, "is_published": B,
        "photo_file_ids": arr(ID, minItems=1, description="Au moins une photo (HYPOTHÈSE F003).")},
        required=["name", "description", "price", "stock", "category_id", "is_perishable", "is_customized",
                  "is_published", "photo_file_ids"]),
    "ProductPatch": obj({
        "name": s(minLength=1, maxLength=200), "description": s(minLength=1), "price": MONEY,
        "stock": i(minimum=0), "category_id": ID, "origin": null(s()), "is_perishable": B,
        "is_customized": B, "is_published": B, "photo_file_ids": arr(ID, minItems=1)}, required=[]),
    "AdminProduct": obj({
        "id": ID, "name": s(), "price": MONEY, "stock": i(minimum=0), "category_id": ID,
        "is_published": B, "is_hidden": B, "hidden_at": null(DT),
        "seller": obj({"id": ID, "legal_name": s(), "status": ref("SellerStatus")}), "created_at": DT}),
    "CartItem": obj({"id": ID, "product_id": ID, "product_name": s(), "unit_price": MONEY,
                     "quantity": i(minimum=1), "line_total": MONEY, "is_available": B}),
    "CartWarning": obj({"code": enum("quantity_capped", "product_unavailable"), "product_id": ID, "message": s()}),
    "Cart": obj({
        "groups": arr(obj({"shop": obj({"id": ID, "name": s()}), "items": arr(ref("CartItem")),
                           "subtotal": MONEY})),
        "items_total": MONEY, "warnings": arr(ref("CartWarning"))}),
    "CartItemWrite": obj({"product_id": ID, "quantity": i(minimum=1)}),
    "CartItemPatch": obj({"quantity": i(minimum=1)}),
    "CheckoutRequest": obj({"served_city_id": ID, "delivery_address": s(minLength=1),
                            "phone": ref("Phone"), "delivery_note": null(s(maxLength=500))},
                           required=["served_city_id", "delivery_address", "phone"]),
    "OrderPreview": obj({
        "groups": arr(obj({"shop": obj({"id": ID, "name": s()}), "items": arr(ref("CartItem")),
                           "subtotal": MONEY})),
        "items_total": MONEY, "delivery_fee": MONEY, "total": MONEY,
        "payment_methods": arr(enum("cash_on_delivery"), minItems=1, maxItems=1),
        "return_policy_reminder": s()}),
    "OrderLine": obj({"id": ID, "product_id": ID, "product_name": s(), "quantity": i(minimum=1),
                      "unit_price": MONEY, "line_total": MONEY, "is_return_excluded": B,
                      "review_id": null(ID)}),
    "CustomerSubOrder": obj({"id": ID, "shop": obj({"id": ID, "name": s()}), "status": ref("SubOrderStatus"),
                             "lines": arr(ref("OrderLine"))}),
    "OrderSummary": obj({"id": ID, "reference": s(), "status": ref("OrderStatus"), "total": MONEY,
                         "created_at": DT}),
    "Order": obj({
        "id": ID, "reference": s(), "status": ref("OrderStatus"), "created_at": DT,
        "served_city": ref("ReferenceItem"), "delivery_address": s(), "phone": ref("Phone"),
        "delivery_note": null(s()), "items_total": MONEY, "delivery_fee": MONEY, "total": MONEY,
        "payment_method": enum("cash_on_delivery"), "received_at": null(DT),
        "cancellation_cause": null(ref("CancellationCause")), "can_cancel": B,
        "sub_orders": arr(ref("CustomerSubOrder"))}),
    "OrderConfirmation": obj({
        "order_reference": s(), "issued_at": DT,
        "sellers": arr(obj({"shop_name": s(), "legal_name": s(), "commune": s(),
                            "lines": arr(obj({"product_name": s(), "quantity": i(minimum=1),
                                              "unit_price": MONEY, "line_total": MONEY}))})),
        "items_total": MONEY, "delivery_fee": MONEY, "total": MONEY, "payment_method": enum("cash_on_delivery"),
        "return_policy": s(description="Existence et conditions du droit de retour (RG-026, gabarit T-029, avis juridique C-08/Q39).")},
        description="Confirmation écrite (RG-026 — contenu HYPOTHÈSE, à valider juridiquement)."),
    "SellerSubOrder": obj({
        "id": ID, "order_reference": s(), "status": ref("SubOrderStatus"), "created_at": DT,
        "response_deadline_at": null(DT), "refusal_reason": null(s()),
        "lines": arr(obj({"product_id": ID, "product_name": s(), "quantity": i(minimum=1), "unit_price": MONEY,
                          "line_total": MONEY})),
        "subtotal": MONEY},
        description="Vue vendeur : ni adresse ni téléphone du client (ENF-007, §19)."),
    "ReasonRequest": obj({"reason": s(minLength=1, maxLength=500)}),
    "AdminSubOrder": obj({
        "id": ID, "status": ref("SubOrderStatus"), "refusal_reason": null(s()),
        "seller": obj({"id": ID, "legal_name": s(), "shop_name": s(), "pickup_address": s(), "commune": s(),
                       "status": ref("SellerStatus")}),
        "lines": arr(ref("OrderLine")), "subtotal": MONEY}),
    "AdminOrder": obj({
        "id": ID, "reference": s(), "status": ref("OrderStatus"), "created_at": DT,
        "customer": obj({"id": ID, "name": s(), "phone": ref("Phone")}),
        "served_city": ref("ReferenceItem"), "delivery_address": s(), "phone": ref("Phone"),
        "delivery_note": null(s()), "items_total": MONEY, "delivery_fee": MONEY, "amount_due": MONEY,
        "collected_amount": null(MONEY), "received_at": null(DT), "failure_reason": null(s()),
        "cash_discrepancy": null(MONEY), "all_sub_orders_ready": B, "sub_orders": arr(ref("AdminSubOrder"))}),
    "AdminOrderSummary": obj({"id": ID, "reference": s(), "status": ref("OrderStatus"), "amount_due": MONEY,
                              "all_sub_orders_ready": B, "created_at": DT}),
    "DeliveredPaidRequest": obj({"collected_amount": MONEY, "received_at": DT}),
    "DeliveryPartner": obj({"id": ID, "name": s()}),
    "FundRemittanceWrite": obj({"delivery_partner_id": ID, "amount": MONEY, "remitted_on": D,
                                "order_ids": arr(ID, minItems=1, uniqueItems=True)}),
    "FundRemittance": obj({"id": ID, "delivery_partner": ref("DeliveryPartner"), "amount": MONEY,
                           "remitted_on": D, "order_ids": arr(ID), "expected_amount": MONEY,
                           "difference": MONEY, "has_discrepancy": B, "recorded_by_user_id": ID}),
    "CashDiscrepancy": obj({"id": ID, "order_id": ID, "order_reference": s(), "amount": MONEY,
                            "recorded_on": D}),
    "ReturnEligibility": obj({
        "order_id": ID, "received_at": null(DT), "return_deadline_at": null(DT),
        "lines": arr(obj({"order_line_id": ID, "product_name": s(), "quantity": i(minimum=1),
                          "returnable_quantity": i(minimum=0), "eligible": B,
                          "ineligibility_reason": null(ref("ReturnIneligibility"))})),
        "change_of_mind_fee": null(MONEY),
        "allowed_refund_methods": arr(ref("RefundMethod"), minItems=1)}),
    "ReturnWrite": obj({"order_line_id": ID, "quantity": i(minimum=1), "reason": ref("ReturnReason"),
                        "refund_method": ref("RefundMethod"), "refund_details": s(minLength=1, writeOnly=False),
                        "photo_file_id": null(ID)},
                       required=["order_line_id", "quantity", "reason", "refund_method", "refund_details"]),
    "Inspection": obj({"result": ref("InspectionResult"), "dispute_reason": null(s()), "restock": B,
                       "inspected_at": DT}),
    "InspectionWrite": obj({"result": ref("InspectionResult"), "dispute_reason": null(s(maxLength=500)),
                            "restock": B}, required=["result", "restock"]),
    "Dispute": obj({"opened_at": DT, "decision": null(ref("DisputeDecision")), "decision_reason": null(s()),
                    "refunded_amount": null(MONEY), "fee_charged_to": null(ref("FeeChargedTo")),
                    "decided_at": null(DT)}),
    "DisputeDecisionWrite": obj({"decision": ref("DisputeDecision"), "decision_reason": s(minLength=1),
                                 "refunded_amount": null(MONEY), "fee_charged_to": ref("FeeChargedTo")},
                                required=["decision", "decision_reason", "fee_charged_to"]),
    "Refund": obj({"amount": MONEY, "method": ref("RefundMethod"), "reference": s(), "refunded_on": D}),
    "RefundWrite": obj({"method": ref("RefundMethod"), "reference": s(minLength=1, maxLength=100),
                        "refunded_on": D}),
    "CustomerReturn": obj({
        "id": ID, "order_id": ID, "order_reference": s(), "order_line_id": ID, "product_name": s(),
        "quantity": i(minimum=1), "reason": ref("ReturnReason"), "refund_method": ref("RefundMethod"),
        "refund_details": s(description="Titulaire et administrateur seulement (FR-055)."),
        "status": ref("ReturnStatus"), "requested_at": DT, "return_fee": null(MONEY),
        "refund": null(ref("Refund"))}),
    "SellerReturn": obj({
        "id": ID, "order_reference": s(), "product_id": ID, "product_name": s(), "quantity": i(minimum=1),
        "reason": ref("ReturnReason"), "photo_url": null(s(format="uri")), "status": ref("ReturnStatus"),
        "requested_at": DT, "inspection": null(ref("Inspection")),
        "dispute": null(ref("Dispute"))},
        description="Vue vendeur : ni coordonnées de remboursement ni contact du client (ENF-007, FR-055)."),
    "AdminReturn": obj({
        "id": ID, "order_id": ID, "order_reference": s(), "order_line_id": ID, "product_name": s(),
        "seller_id": ID, "customer_id": ID, "quantity": i(minimum=1), "reason": ref("ReturnReason"),
        "refund_method": ref("RefundMethod"), "refund_details": s(), "status": ref("ReturnStatus"),
        "requested_at": DT, "legal_deadline_at": DT, "near_legal_deadline": B,
        "expected_refund_amount": null(MONEY), "return_fee": null(MONEY),
        "inspection": null(ref("Inspection")), "dispute": null(ref("Dispute")), "refund": null(ref("Refund"))}),
    "SellerAmount": obj({"id": ID, "order_reference": s(), "product_name": s(), "amount": MONEY,
                         "status": ref("SellerAmountStatus"), "hold_until": DT, "payout_id": null(ID)}),
    "SellerAmountsSummary": obj({"held": MONEY, "available": MONEY, "paid_out": MONEY, "deducted": MONEY,
                                 "pending_deductions": MONEY}),
    "Deduction": obj({"id": ID, "product_return_id": ID, "amount": MONEY, "origin": ref("DeductionOrigin"),
                      "deducted_on": D, "payout_id": null(ID)}),
    "Payout": obj({"id": ID, "seller_id": ID, "period_start": D, "paid_on": D, "amount": MONEY,
                   "method": ref("PayoutMethod"), "cash_proof": null(s()), "order_references": arr(s()),
                   "deduction_ids": arr(ID)}),
    "PayoutPreviewLine": obj({"seller_id": ID, "legal_name": s(), "payout_method": ref("PayoutMethod"),
                              "available_total": MONEY, "pending_deductions_total": MONEY,
                              "payable_amount": MONEY, "negative_balance": B}),
    "PayoutWrite": obj({"seller_id": ID, "period_start": D, "paid_on": D, "method": ref("PayoutMethod"),
                        "cash_proof": null(s(maxLength=255, description="Requis si method = cash (HYPOTHÈSE F011)."))},
                       required=["seller_id", "period_start", "paid_on", "method"]),
    "AdminSeller": obj({"id": ID, "legal_name": s(), "phone": ref("Phone"), "seller_commune": ref("ReferenceItem"),
                        "payout_method": ref("PayoutMethod"), "bank_details": null(s()),
                        "status": ref("SellerStatus"), "suspended_at": null(DT), "shop": ref("Shop"),
                        "open_sub_orders_count": i(minimum=0), "open_returns_count": i(minimum=0)}),
    "AuditEntry": obj({"id": ID, "occurred_at": DT, "actor_user_id": null(ID), "actor_system": null(s()),
                       "action_type": ref("AuditActionType"), "target_type": s(), "target_id": ID, "from_status": null(s()),
                       "to_status": null(s()), "amount": null(MONEY), "reason": null(s()),
                       "corrects_entry_id": null(ID)}),
    "AuditActionType": enum("order_status_changed", "sub_order_status_changed", "delivery_status_recorded",
                            "cash_collected", "fund_remittance_recorded", "cash_discrepancy_recorded",
                            "seller_amount_held", "seller_amount_released", "seller_amount_deducted",
                            "return_status_changed", "return_pickup_recorded", "return_fee_charged",
                            "dispute_decided", "refund_recorded", "deduction_recorded", "payout_recorded",
                            "correction", "scheduled_task_run",
                            description="Type d'action auditée, valeurs identiques à audit_entries.action_type (T-002)."),
    "Notification": obj({"id": ID, "type": s(), "title": s(), "body": s(), "data": {"type": "object"},
                         "read_at": null(DT), "created_at": DT}),
    "Setting": obj({"key": s(), "value": {"type": ["string", "number", "integer", "boolean", "null"]},
                    "value_type": enum("string", "integer", "decimal", "boolean"), "description": s(),
                    "updated_at": null(DT)}),
    "SettingWrite": obj({"value": {"type": ["string", "number", "integer", "boolean", "null"]}}),
}

# ---------------------------------------------------------------------------
# Matrice des permissions (CDC §5) + capacités dérivées
# ---------------------------------------------------------------------------
# Valeurs : allow (sans condition de propriété), own (ses ressources seulement),
#           allow_hyp / own_hyp (HYPOTHÈSE du cahier), deny.
MATRIX_ROWS = [
    ("MP-01", "Consulter le catalogue, les fiches produits, les avis", "§5", ["allow", "allow", "allow", "allow"], ""),
    ("MP-02", "Rechercher / filtrer par catégorie", "§5", ["allow", "allow", "allow", "allow"], ""),
    ("MP-03", "Gérer un panier", "§5", ["allow_hyp", "own", "deny", "deny"], "Visiteur : HYPOTHÈSE H-01"),
    ("MP-04", "Passer commande (compte obligatoire)", "§5", ["deny", "allow", "deny", "deny"], "RG-028, D41"),
    ("MP-05", "Suivre / annuler ses commandes", "§5", ["deny", "own", "deny", "allow"],
     "Annulation administrateur bloquée (U-02)"),
    ("MP-06", "Demander le retour d'un produit reçu (7 jours, tout motif)", "§5", ["deny", "own", "deny", "deny"], ""),
    ("MP-07", "Vérifier un produit retourné (conforme / contesté) et décider de sa remise en vente", "§5",
     ["deny", "deny", "own", "allow"], "Admin : en cas de litige ou d'absence de vérification (U-01, Q44)"),
    ("MP-08", "Arbitrer un litige de retour", "§5", ["deny", "deny", "deny", "allow"], ""),
    ("MP-09", "Enregistrer un remboursement client", "§5", ["deny", "deny", "deny", "allow"], ""),
    ("MP-10", "Laisser un avis / une note", "§5", ["deny", "own", "deny", "deny"], "Produit reçu uniquement (RG-011)"),
    ("MP-11", "Créer / modifier sa boutique et ses produits (dont caractère périssable/personnalisé)", "§5",
     ["deny", "deny", "own", "allow"], "Admin : modération"),
    ("MP-12", "Accepter / refuser / préparer une sous-commande", "§5", ["deny", "deny", "own", "allow"], ""),
    ("MP-13", "Saisir collecte, livraison, encaissement, reprise de retour", "§5", ["deny", "deny", "deny", "allow"],
     "Admin seul (RG-029, D38)"),
    ("MP-14", "Consulter ses montants retenus, disponibles, reversés et déduits", "§5",
     ["deny", "deny", "own", "allow"], ""),
    ("MP-15", "Enregistrer un reversement hebdomadaire (virement ou espèces)", "§5", ["deny", "deny", "deny", "allow"], ""),
    ("MP-16", "Masquer un produit / suspendre un vendeur / masquer un avis", "§5", ["deny", "deny", "deny", "allow"], ""),
    ("MP-17", "Gérer les catégories (dont exclusions de retour), la zone clients et la liste des communes vendeurs",
     "§5", ["deny", "deny", "deny", "allow"], ""),
    # Capacités dérivées (absentes de la matrice §5 mais exigées ailleurs) — ADR-017
    ("MX-01", "S'inscrire, se connecter, se déconnecter, consulter son compte", "F001, F002, UC-004, UC-010",
     ["allow", "own", "own", "own"], "Inscription : visiteur ; déconnexion et compte : titulaire"),
    ("MX-02", "Consulter les référentiels publics (villes desservies, communes vendeurs)", "F002, F007",
     ["allow", "allow", "allow", "allow"], "Nécessaire aux formulaires d'inscription et de commande"),
    ("MX-03", "Consulter ses notifications internes", "F014, T-009", ["deny", "own", "own", "own"], ""),
    ("MX-04", "Superviser vendeurs, produits, commandes, retours, montants et journal d'audit", "F013, UC-023, ENF-008",
     ["deny", "deny", "deny", "allow_hyp"], "Périmètre de supervision : HYPOTHÈSE (F013)"),
    ("MX-05", "Gérer les paramètres métier", "H-08, T-007", ["deny", "deny", "deny", "allow"], ""),
]
ROLE_IDX = {r: k for k, r in enumerate(ALL_ROLES)}


def row_allows(row_id, role):
    for rid, _, _, vals, _ in MATRIX_ROWS:
        if rid == row_id:
            return vals[ROLE_IDX[role]] != "deny"
    raise KeyError(row_id)


# ---------------------------------------------------------------------------
# Catalogue des codes d'erreur (ADR-016)
# ---------------------------------------------------------------------------
ERROR_CODES = {
    "malformed_request": (400, "Requête mal formée (JSON invalide, paramètre de type incorrect)."),
    "unauthenticated": (401, "Jeton absent, invalide ou expiré."),
    "invalid_credentials": (401, "Téléphone ou mot de passe incorrect, sans préciser lequel (F001)."),
    "forbidden": (403, "Rôle non autorisé pour cette action (matrice, ADR-017)."),
    "account_suspended": (403, "Compte vendeur suspendu : actions d'écriture refusées (RG-015 ; HYPOTHÈSE)."),
    "not_found": (404, "Ressource inexistante, non visible publiquement, ou appartenant à un autre titulaire (ADR-017)."),
    "invalid_transition": (409, "Transition d'état interdite depuis l'état courant (STATE-001..004)."),
    "phone_already_registered": (409, "Téléphone déjà utilisé ; la connexion est proposée (CA-F001-2)."),
    "insufficient_stock": (409, "Stock insuffisant à la validation ; le panier est mis à jour (F007)."),
    "product_unavailable": (409, "Produit indisponible (stock 0, masqué, vendeur suspendu) — CA-F003-2."),
    "payout_already_recorded": (409, "Reversement déjà enregistré pour ce vendeur et cette semaine (idempotence)."),
    "duplicate_name": (409, "Nom déjà utilisé dans le référentiel."),
    "resource_in_use": (409, "Suppression impossible : la ressource est référencée."),
    "validation_failed": (422, "Données invalides ; details.fields liste les champs en erreur."),
    "commune_not_allowed": (422, "Commune hors de la liste autorisée (CA-F002-3)."),
    "city_not_served": (422, "Adresse hors des villes desservies — seule Tanger en V1 (CA-F007-2)."),
    "cart_empty": (422, "Panier vide ou sans produit disponible."),
    "return_not_eligible": (422, "Retour impossible ; details.reason = ReturnIneligibility (CA-F022-2/3/8)."),
    "review_not_allowed": (422, "Avis impossible : commande non « livrée et payée » (RG-011)."),
    "file_rejected": (422, "Fichier refusé (type ou taille), FR-040."),
    "nothing_to_pay_out": (422, "Aucun montant positif à reverser (solde nul ou négatif reporté, H-07)."),
    "feature_blocked": (501, "Action prévue au contrat mais bloquée par une décision manquante (U-01, U-02)."),
    "rate_limited": (429, "Trop de requêtes."),
    "server_error": (500, "Erreur interne, sans détail d'implémentation."),
}


def err(code, message, details=None):
    e = {"code": code, "message": message}
    if details is not None:
        e["details"] = details
    return {"error": e}


# ---------------------------------------------------------------------------
# Opérations
# ---------------------------------------------------------------------------
OPS = []
MODULES = {
    "M01": "Comptes et accès", "M02": "Boutique et catalogue vendeur", "M03": "Découverte",
    "M04": "Panier et commande", "M05": "Commandes vendeur", "M06": "Livraison et encaissement",
    "M07": "Reversements vendeurs", "M08": "Avis et notes", "M09": "Administration et modération",
    "M10": "Notifications", "M11": "Retours", "SOCLE": "Socle transverse (paramètres, photos, audit)",
}


def op(oid, method, path, module, summary, *, roles, uc, rows, own=None, req=None, req_ex=None,
       query=None, ok=None, errors=None, desc="", blocked=None, hyp=None, multipart=False, headers=None,
       resp_headers=None, task=None):
    OPS.append(dict(oid=oid, method=method, path=path, module=module, summary=summary, roles=roles, uc=uc,
                    rows=rows, own=own or {}, req=req, req_ex=req_ex, query=query or [], ok=ok,
                    errors=errors or [], desc=desc, blocked=blocked, hyp=hyp, multipart=multipart,
                    headers=headers or [], resp_headers=resp_headers or {}, task=task))


def page(items, total=None):
    n = len(items) if total is None else total
    return {"data": items, "meta": {"page": 1, "per_page": 20, "total": n, "total_pages": 1 if n else 0}}


def one(x):
    return {"data": x}


PUB = ALL_ROLES
C, S_, A = ["customer"], ["seller"], ["admin"]
CART_HDR = ("X-Cart-Token", "Jeton opaque du panier visiteur (ADR-019). Absent pour un client connecté.",
            "b3f1c2d4e5f6a7b8c9d0e1f2a3b4c5d6")

# ---- Exemples réutilisables ----
EX_USER_C = {"id": 41, "role": "customer", "phone": "+212600000041"}
EX_USER_S = {"id": 12, "role": "seller", "phone": "+212600000012"}
EX_TOKEN = {"token": "<jeton-opaque>", "token_type": "Bearer", "expires_at": "2026-10-21T10:00:00Z", "user": EX_USER_C}
EX_CAT = {"id": 3, "name": "Cosmétiques naturels", "is_return_excluded": False}
EX_CITY = {"id": 1, "name": "Tanger"}
EX_COMMUNE = {"id": 2, "name": "Gueznaia"}
EX_SHOP = {"id": 7, "name": "Coopérative Argan Nord", "description": "Huiles et savons artisanaux",
           "pickup_address": "12 rue Al Massira, Gueznaia"}
EX_PHOTO = {"photo_file_id": 501, "position": 0, "mobile_url": "https://cdn.example.ma/p/7f3a9c-mobile.jpg"}
EX_POLICY = {"window_days": 7, "change_of_mind_fee": None, "is_excluded": False, "exclusion_reason": None}
EX_CARD = {"id": 101, "name": "Huile d'argan 250 ml", "price": "120.00",
           "main_photo_url": "https://cdn.example.ma/p/7f3a9c-mobile.jpg",
           "shop": {"id": 7, "name": "Coopérative Argan Nord"}, "average_rating": 4.5, "review_count": 12,
           "is_available": True}
EX_DETAIL = {"id": 101, "name": "Huile d'argan 250 ml", "description": "Huile pressée à froid.", "price": "120.00",
             "origin": "Souss", "category": EX_CAT, "photos": [EX_PHOTO],
             "shop": {"id": 7, "name": "Coopérative Argan Nord", "commune": "Gueznaia"},
             "average_rating": 4.5, "review_count": 12, "is_available": True, "return_policy": EX_POLICY}
EX_REVIEW = {"id": 900, "product_id": 101, "rating": 5, "comment": "Très bonne huile.",
             "created_at": "2026-10-20T09:00:00Z", "updated_at": "2026-10-20T09:00:00Z"}
EX_SPROD = {"id": 101, "name": "Huile d'argan 250 ml", "description": "Huile pressée à froid.", "price": "120.00",
            "stock": 15, "category_id": 3, "origin": "Souss", "is_perishable": False, "is_customized": False,
            "is_published": True, "is_hidden": False, "photos": [EX_PHOTO],
            "created_at": "2026-10-10T08:00:00Z", "updated_at": "2026-10-12T08:00:00Z"}
EX_PROD_WRITE = {"name": "Huile d'argan 250 ml", "description": "Huile pressée à froid.", "price": "120.00",
                 "stock": 15, "category_id": 3, "origin": "Souss", "is_perishable": False, "is_customized": False,
                 "is_published": True, "photo_file_ids": [501]}
EX_CART_ITEM_A = {"id": 31, "product_id": 101, "product_name": "Huile d'argan 250 ml", "unit_price": "120.00",
                  "quantity": 1, "line_total": "120.00", "is_available": True}
EX_CART_ITEM_B = {"id": 32, "product_id": 205, "product_name": "Miel de thym 500 g", "unit_price": "80.00",
                  "quantity": 1, "line_total": "80.00", "is_available": True}
EX_GROUPS = [
    {"shop": {"id": 7, "name": "Coopérative Argan Nord"}, "items": [EX_CART_ITEM_A], "subtotal": "120.00"},
    {"shop": {"id": 9, "name": "Rucher du Rif"}, "items": [EX_CART_ITEM_B], "subtotal": "80.00"},
]
EX_CART = {"groups": EX_GROUPS, "items_total": "200.00", "warnings": []}
EX_CHECKOUT = {"served_city_id": 1, "delivery_address": "Quartier Iberia, rue 5, n° 10, près de la mosquée",
               "phone": "+212600000041", "delivery_note": "Appeler avant d'arriver"}
EX_LINE_A = {"id": 7001, "product_id": 101, "product_name": "Huile d'argan 250 ml", "quantity": 1,
             "unit_price": "120.00", "line_total": "120.00", "is_return_excluded": False, "review_id": None}
EX_LINE_B = {"id": 7002, "product_id": 205, "product_name": "Miel de thym 500 g", "quantity": 1,
             "unit_price": "80.00", "line_total": "80.00", "is_return_excluded": False, "review_id": None}
EX_ORDER = {"id": 5001, "reference": "CMD-2026-000123", "status": "awaiting_acceptance",
            "created_at": "2026-10-14T10:00:00Z", "served_city": EX_CITY,
            "delivery_address": EX_CHECKOUT["delivery_address"], "phone": "+212600000041",
            "delivery_note": "Appeler avant d'arriver", "items_total": "200.00", "delivery_fee": "25.00",
            "total": "225.00", "payment_method": "cash_on_delivery", "received_at": None,
            "cancellation_cause": None, "can_cancel": True,
            "sub_orders": [
                {"id": 6001, "shop": {"id": 7, "name": "Coopérative Argan Nord"}, "status": "new", "lines": [EX_LINE_A]},
                {"id": 6002, "shop": {"id": 9, "name": "Rucher du Rif"}, "status": "new", "lines": [EX_LINE_B]}]}
EX_ORDER_SUM = {"id": 5001, "reference": "CMD-2026-000123", "status": "awaiting_acceptance", "total": "225.00",
                "created_at": "2026-10-14T10:00:00Z"}
EX_SSUB = {"id": 6001, "order_reference": "CMD-2026-000123", "status": "new", "created_at": "2026-10-14T10:00:00Z",
           "response_deadline_at": "2026-10-15T10:00:00Z", "refusal_reason": None,
           "lines": [{"product_id": 101, "product_name": "Huile d'argan 250 ml", "quantity": 1,
                      "unit_price": "120.00", "line_total": "120.00"}], "subtotal": "120.00"}
EX_ASUB = {"id": 6001, "status": "ready_for_pickup", "refusal_reason": None,
           "seller": {"id": 12, "legal_name": "Coopérative Argan Nord SARL", "shop_name": "Coopérative Argan Nord",
                      "pickup_address": "12 rue Al Massira, Gueznaia", "commune": "Gueznaia", "status": "active"},
           "lines": [EX_LINE_A], "subtotal": "120.00"}
EX_AORDER = {"id": 5001, "reference": "CMD-2026-000123", "status": "confirmed", "created_at": "2026-10-14T10:00:00Z",
             "customer": {"id": 41, "name": "Salma B.", "phone": "+212600000041"}, "served_city": EX_CITY,
             "delivery_address": EX_CHECKOUT["delivery_address"], "phone": "+212600000041",
             "delivery_note": "Appeler avant d'arriver", "items_total": "200.00", "delivery_fee": "25.00",
             "amount_due": "225.00", "collected_amount": None, "received_at": None, "failure_reason": None,
             "cash_discrepancy": None, "all_sub_orders_ready": True, "sub_orders": [EX_ASUB]}
EX_AORDER_SUM = {"id": 5001, "reference": "CMD-2026-000123", "status": "confirmed", "amount_due": "225.00",
                 "all_sub_orders_ready": True, "created_at": "2026-10-14T10:00:00Z"}


def with_(base, **kw):
    d = copy.deepcopy(base)
    d.update(kw)
    return d


EX_INSPECTION = {"result": "compliant", "dispute_reason": None, "restock": True, "inspected_at": "2026-10-24T11:00:00Z"}
EX_DISPUTE = {"opened_at": "2026-10-24T11:00:00Z", "decision": None, "decision_reason": None,
              "refunded_amount": None, "fee_charged_to": None, "decided_at": None}
EX_REFUND = {"amount": "120.00", "method": "bank_transfer", "reference": "VIR-2026-10-28-0042",
             "refunded_on": "2026-10-28"}
EX_CRET = {"id": 801, "order_id": 5001, "order_reference": "CMD-2026-000123", "order_line_id": 7001,
           "product_name": "Huile d'argan 250 ml", "quantity": 1, "reason": "defective",
           "refund_method": "bank_transfer", "refund_details": "RIB 0117 **** **** 2231",
           "status": "requested", "requested_at": "2026-10-21T09:00:00Z", "return_fee": None, "refund": None}
EX_SRET = {"id": 801, "order_reference": "CMD-2026-000123", "product_id": 101, "product_name": "Huile d'argan 250 ml",
           "quantity": 1, "reason": "defective", "photo_url": None, "status": "picked_up",
           "requested_at": "2026-10-21T09:00:00Z", "inspection": None, "dispute": None}
EX_ARET = {"id": 801, "order_id": 5001, "order_reference": "CMD-2026-000123", "order_line_id": 7001,
           "product_name": "Huile d'argan 250 ml", "seller_id": 12, "customer_id": 41, "quantity": 1,
           "reason": "defective", "refund_method": "bank_transfer", "refund_details": "RIB 011 780 0000123456789 22",
           "status": "verified_by_seller", "requested_at": "2026-10-21T09:00:00Z",
           "legal_deadline_at": "2026-11-05T09:00:00Z", "near_legal_deadline": False,
           "expected_refund_amount": "120.00", "return_fee": "15.00", "inspection": EX_INSPECTION,
           "dispute": None, "refund": None}
EX_SAMOUNT = {"id": 3001, "order_reference": "CMD-2026-000123", "product_name": "Huile d'argan 250 ml",
              "amount": "120.00", "status": "held", "hold_until": "2026-10-27T18:30:00Z", "payout_id": None}
EX_PAYOUT = {"id": 401, "seller_id": 12, "period_start": "2026-11-02", "paid_on": "2026-11-02", "amount": "420.00",
             "method": "bank_transfer", "cash_proof": None, "order_references": ["CMD-2026-000123", "CMD-2026-000131"],
             "deduction_ids": [77]}
EX_DEDUCTION = {"id": 77, "product_return_id": 801, "amount": "80.00", "origin": "refund", "deducted_on": "2026-10-28",
                "payout_id": None}
EX_ASELLER = {"id": 12, "legal_name": "Coopérative Argan Nord SARL", "phone": "+212600000012",
              "seller_commune": EX_COMMUNE, "payout_method": "bank_transfer",
              "bank_details": "RIB 011 780 0000987654321 10", "status": "active", "suspended_at": None,
              "shop": EX_SHOP, "open_sub_orders_count": 2, "open_returns_count": 1}
EX_SPROFILE = {"id": 12, "legal_name": "Coopérative Argan Nord SARL", "phone": "+212600000012",
               "seller_commune": EX_COMMUNE, "payout_method": "bank_transfer",
               "bank_details": "RIB 011 780 0000987654321 10", "status": "active", "shop": EX_SHOP}

E422 = lambda fields: err("validation_failed", "Certaines informations sont invalides.", {"fields": fields})
E409T = lambda cur, action: err("invalid_transition", "Cette action n'est pas possible dans l'état actuel.",
                                {"current_status": cur, "action": action})

# ===================== M01 — Comptes et accès =====================
op("registerCustomer", "post", "/auth/register", "M01", "Créer un compte client et se connecter",
   roles=["visitor"], uc=["UC-004"], rows=["MX-01"], req=ref("RegisterCustomerRequest"),
   req_ex={"name": "Salma B.", "phone": "+212600000041", "password": "<mot-de-passe>", "email": None},
   headers=[CART_HDR], ok=(201, ref("AuthToken"), EX_TOKEN),
   errors=[(409, err("phone_already_registered", "Ce numéro est déjà utilisé. Connectez-vous.",
                     {"suggested_action": "login"}))],
   desc="CA-F001-1/2. Si X-Cart-Token est fourni, le panier visiteur est rattaché au nouveau compte (CA-F001-3, ADR-019). "
        "Récupération d'accès : non contractualisée, [NEEDS CLARIFICATION: M-06/Q23, T-015 bloquée].", task="T-014")
op("login", "post", "/auth/login", "M01", "Se connecter (client, vendeur, administrateur)",
   roles=["visitor"], uc=["UC-004", "UC-010"], rows=["MX-01"], req=ref("LoginRequest"),
   req_ex={"phone": "+212600000041", "password": "<mot-de-passe>"}, headers=[CART_HDR],
   ok=(200, ref("AuthToken"), EX_TOKEN),
   errors=[(401, err("invalid_credentials", "Téléphone ou mot de passe incorrect."))],
   desc="Message identique que le téléphone ou le mot de passe soit faux (F001). Panier visiteur rattaché si X-Cart-Token (CA-F001-3).",
   task="T-014")
op("logout", "post", "/auth/logout", "M01", "Se déconnecter (révoque le jeton courant)",
   roles=["customer", "seller", "admin"], own={"customer": "own", "seller": "own", "admin": "own"},
   uc=["UC-004"], rows=["MX-01"], ok=(204, None, None), task="T-014")
op("getMe", "get", "/me", "M01", "Consulter son compte",
   roles=["customer", "seller", "admin"], own={"customer": "own", "seller": "own", "admin": "own"},
   uc=["UC-004", "UC-010"], rows=["MX-01"],
   ok=(200, ref("Me"), {"user": EX_USER_C, "customer": {"id": 41, "name": "Salma B.", "email": None}, "seller": None}),
   desc="Ne renvoie jamais le mot de passe (FR-054).", task="T-006")
op("registerSeller", "post", "/auth/register-seller", "M01", "S'inscrire comme vendeur et créer sa boutique",
   roles=["visitor"], uc=["UC-010"], rows=["MX-01"], req=ref("RegisterSellerRequest"),
   req_ex={"phone": "+212600000012", "password": "<mot-de-passe>", "legal_name": "Coopérative Argan Nord SARL",
           "seller_commune_id": 2, "payout_method": "bank_transfer", "bank_details": "RIB 011 780 0000987654321 10",
           "shop": {"name": "Coopérative Argan Nord", "description": "Huiles et savons artisanaux",
                    "pickup_address": "12 rue Al Massira, Gueznaia"}},
   ok=(201, ref("AuthToken"), with_(EX_TOKEN, user=EX_USER_S)),
   errors=[(422, err("commune_not_allowed",
                     "La Plateforme n'accepte pour le moment que les vendeurs de Tanger et des communes voisines.")),
           (422, E422({"bank_details": ["Les coordonnées bancaires sont obligatoires pour un reversement par virement."]})),
           (409, err("phone_already_registered", "Ce numéro est déjà utilisé. Connectez-vous.", {"suggested_action": "login"}))],
   desc="Boutique active immédiatement (RG-004, CA-F002-1). Une boutique par vendeur (H-06). Champs exigés : [NEEDS CLARIFICATION: Q22].",
   task="T-016")
op("listSellerCommunes", "get", "/seller-communes", "M01", "Lister les communes vendeurs autorisées",
   roles=PUB, uc=["UC-010"], rows=["MX-02"], ok=(200, "page:ReferenceItem", page([EX_COMMUNE])), task="T-017")
op("getSellerProfile", "get", "/seller/profile", "M01", "Consulter son profil vendeur et sa boutique",
   roles=S_, own={"seller": "own"}, uc=["UC-010"], rows=["MP-11"], ok=(200, ref("SellerProfile"), EX_SPROFILE),
   task="T-016")
op("updateSellerProfile", "patch", "/seller/profile", "M01", "Modifier son mode de reversement",
   roles=S_, own={"seller": "own"}, uc=["UC-010"], rows=["MP-11"], req=ref("SellerProfilePatch"),
   req_ex={"payout_method": "cash", "bank_details": None}, ok=(200, ref("SellerProfile"), with_(EX_SPROFILE, payout_method="cash", bank_details=None)),
   errors=[(422, E422({"bank_details": ["Obligatoire si le mode de reversement est le virement."]}))], task="T-016")
op("updateShop", "patch", "/seller/shop", "M02", "Modifier sa boutique",
   roles=S_, own={"seller": "own"}, uc=["UC-010", "UC-011"], rows=["MP-11"], req=ref("ShopPatch"),
   req_ex={"description": "Huiles, savons et amlou artisanaux"},
   ok=(200, ref("Shop"), with_(EX_SHOP, description="Huiles, savons et amlou artisanaux")), task="T-016")

# ===================== SOCLE — photos =====================
op("uploadPhoto", "post", "/photos", "SOCLE", "Téléverser une photo (produit ou retour)",
   roles=["customer", "seller"], own={"customer": "own", "seller": "own"}, uc=["UC-011", "UC-008"],
   rows=["MP-11", "MP-06"], multipart=True, req_ex={"file": "<binaire image/jpeg>"},
   ok=(201, ref("PhotoFile"), {"id": 501, "mime_type": "image/jpeg", "size_bytes": 284112,
                               "mobile_url": "https://cdn.example.ma/p/7f3a9c-mobile.jpg"}),
   errors=[(422, err("file_rejected", "Le fichier doit être une image (JPEG, PNG ou WebP) de taille autorisée.",
                     {"max_bytes_setting": "photo_max_bytes"}))],
   desc="Contrôle du type réel et de la taille (FR-040) ; nom généré (FR-042) ; variante mobile différée (ADR-004). "
        "La photo n'est utilisable que par son propriétaire (owner_user_id).", task="T-020")

# ===================== M02 — Catalogue vendeur =====================
op("listSellerProducts", "get", "/seller/products", "M02", "Lister ses produits",
   roles=S_, own={"seller": "own"}, uc=["UC-011"], rows=["MP-11"],
   query=[("page", i(minimum=1), "Page", 1), ("per_page", i(minimum=1), "Taille de page (max = paramètre)", 20)],
   ok=(200, "page:SellerProduct", page([EX_SPROD])), desc="CA-F003-3 : seulement ses produits.", task="T-021")
op("createSellerProduct", "post", "/seller/products", "M02", "Créer un produit",
   roles=S_, own={"seller": "own"}, uc=["UC-011"], rows=["MP-11"], req=ref("ProductWrite"), req_ex=EX_PROD_WRITE,
   ok=(201, ref("SellerProduct"), EX_SPROD),
   errors=[(422, E422({"price": ["Le prix doit être supérieur à 0."], "photo_file_ids": ["Au moins une photo est requise."]})),
           (403, err("account_suspended", "Votre compte vendeur est suspendu."))],
   desc="Publié immédiatement si is_published (RG-004, CA-F003-1). Prix > 0 (F003).", task="T-021")
op("getSellerProduct", "get", "/seller/products/{productId}", "M02", "Consulter un de ses produits",
   roles=S_, own={"seller": "own"}, uc=["UC-011"], rows=["MP-11"], ok=(200, ref("SellerProduct"), EX_SPROD), task="T-021")
op("updateSellerProduct", "patch", "/seller/products/{productId}", "M02",
   "Modifier un de ses produits (prix, stock, publication, périssable, personnalisé)",
   roles=S_, own={"seller": "own"}, uc=["UC-011"], rows=["MP-11"], req=ref("ProductPatch"),
   req_ex={"price": "130.00", "stock": 0}, ok=(200, ref("SellerProduct"), with_(EX_SPROD, price="130.00", stock=0)),
   errors=[(422, E422({"stock": ["Le stock ne peut pas être négatif."]}))],
   desc="Un changement de prix n'affecte pas les commandes existantes (prix figé sur order_lines, RG-007). "
        "is_published = false : masquage par le vendeur ; is_hidden est réservé à la modération.", task="T-021")
op("deleteSellerProduct", "delete", "/seller/products/{productId}", "M02", "Supprimer un de ses produits",
   roles=S_, own={"seller": "own"}, uc=["UC-011"], rows=["MP-11"], ok=(204, None, None),
   desc="Suppression logique (deleted_at) : les commandes passées gardent la référence (T-002 E-09).", task="T-021")

# ===================== M03 — Découverte =====================
op("listProducts", "get", "/products", "M03", "Parcourir et rechercher le catalogue",
   roles=PUB, uc=["UC-001"], rows=["MP-01", "MP-02"],
   query=[("q", s(minLength=1, maxLength=100), "Mot-clé (nom, description)", "argan"),
          ("category_id", ID, "Filtre catégorie", 3), ("page", i(minimum=1), "Page", 1),
          ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:ProductCard", page([EX_CARD])),
   desc="Seulement les produits visibles : publié ∧ ¬masqué ∧ stock > 0 ∧ vendeur actif (RG-006, CA-F004-1/2). "
        "Aucun résultat : liste vide (200) ; le frontend propose des catégories.", task="T-023")
op("listCategories", "get", "/categories", "M03", "Lister les catégories",
   roles=PUB, uc=["UC-001"], rows=["MP-02"], ok=(200, "page:Category", page([EX_CAT])), task="T-023")
op("getProduct", "get", "/products/{productId}", "M03", "Consulter une fiche produit",
   roles=PUB, uc=["UC-002"], rows=["MP-01"], ok=(200, ref("ProductDetail"), EX_DETAIL),
   errors=[(404, err("not_found", "Ce produit n'est pas disponible."))],
   desc="Produit masqué ou vendeur suspendu : 404 (F005). Conditions de retour incluses (CA-F005-1).", task="T-024")
op("listProductReviews", "get", "/products/{productId}/reviews", "M03", "Lister les avis d'un produit",
   roles=PUB, uc=["UC-002"], rows=["MP-01"],
   query=[("page", i(minimum=1), "Page", 1), ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:Review", page([EX_REVIEW])), desc="Avis non masqués seulement (CA-F013-3).", task="T-024")

# ===================== M04 — Panier et commande =====================
op("getCart", "get", "/cart", "M04", "Consulter son panier",
   roles=["visitor", "customer"], own={"customer": "own", "visitor": "own"}, uc=["UC-003"], rows=["MP-03"],
   headers=[CART_HDR], ok=(200, ref("Cart"), EX_CART),
   desc="Regroupé par vendeur avec sous-totaux (CA-F006-1). Produit devenu indisponible : signalé et exclu du total (F006).",
   task="T-026")
op("addCartItem", "post", "/cart/items", "M04", "Ajouter un produit au panier",
   roles=["visitor", "customer"], own={"customer": "own", "visitor": "own"}, uc=["UC-003"], rows=["MP-03"],
   headers=[CART_HDR], req=ref("CartItemWrite"), req_ex={"product_id": 205, "quantity": 5},
   ok=(200, ref("Cart"), with_(EX_CART, warnings=[{"code": "quantity_capped", "product_id": 205,
                                                    "message": "Quantité limitée au stock disponible (3)."}])),
   resp_headers={"X-Cart-Token": "Émis au premier ajout d'un visiteur ; à renvoyer ensuite (ADR-019)."},
   errors=[(409, err("product_unavailable", "Ce produit n'est plus disponible."))],
   desc="Quantité > stock : limitée au stock avec avertissement (CA-F006-2). Stock 0 : refus (CA-F003-2).", task="T-026")
op("updateCartItem", "patch", "/cart/items/{itemId}", "M04", "Modifier la quantité d'une ligne du panier",
   roles=["visitor", "customer"], own={"customer": "own", "visitor": "own"}, uc=["UC-003"], rows=["MP-03"],
   headers=[CART_HDR], req=ref("CartItemPatch"), req_ex={"quantity": 2}, ok=(200, ref("Cart"), EX_CART), task="T-026")
op("removeCartItem", "delete", "/cart/items/{itemId}", "M04", "Retirer une ligne du panier",
   roles=["visitor", "customer"], own={"customer": "own", "visitor": "own"}, uc=["UC-003"], rows=["MP-03"],
   headers=[CART_HDR], ok=(200, ref("Cart"), EX_CART), task="T-026")
op("listServedCities", "get", "/served-cities", "M04", "Lister les villes desservies",
   roles=PUB, uc=["UC-005"], rows=["MX-02"], ok=(200, "page:ReferenceItem", page([EX_CITY])), task="T-017")
op("previewOrder", "post", "/orders/preview", "M04", "Afficher le récapitulatif avant confirmation",
   roles=C, uc=["UC-005"], rows=["MP-04"], req=ref("CheckoutRequest"), req_ex=EX_CHECKOUT,
   ok=(200, ref("OrderPreview"), {"groups": EX_GROUPS, "items_total": "200.00", "delivery_fee": "25.00",
                                  "total": "225.00", "payment_methods": ["cash_on_delivery"],
                                  "return_policy_reminder": "Retour possible sous 7 jours après réception, sauf produits exclus."}),
   errors=[(422, err("city_not_served", "Seule la ville de Tanger est desservie pour le moment.")),
           (422, err("cart_empty", "Votre panier est vide."))],
   desc="Frais de livraison séparés, total = produits + frais (CA-F007-4) ; seul mode : paiement à la livraison (CA-F007-3). "
        "Frais = paramètre (Q27). Aucune écriture.", task="T-028")
op("createOrder", "post", "/orders", "M04", "Passer commande (paiement à la livraison)",
   roles=C, uc=["UC-005"], rows=["MP-04"], req=ref("CheckoutRequest"), req_ex=EX_CHECKOUT,
   ok=(201, ref("Order"), EX_ORDER),
   errors=[(422, err("city_not_served", "Seule la ville de Tanger est desservie pour le moment.")),
           (409, err("insufficient_stock", "Le stock a changé ; votre panier a été mis à jour.",
                     {"lines": [{"product_id": 205, "requested": 2, "available": 1}]})),
           (422, err("cart_empty", "Votre panier est vide."))],
   desc="Une commande, une sous-commande par vendeur, prix figés, stock réservé en transaction, statut awaiting_acceptance, "
        "confirmation écrite envoyée (CA-F007-1, RG-017, RG-026). Visiteur : 401 puis connexion (RG-028, CA-F001-3).",
   task="T-028")
op("listMyOrders", "get", "/orders", "M04", "Lister ses commandes",
   roles=C, own={"customer": "own"}, uc=["UC-006"], rows=["MP-05"],
   query=[("status", ref("OrderStatus"), "Filtre statut", "awaiting_acceptance"), ("page", i(minimum=1), "Page", 1),
          ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:OrderSummary", page([EX_ORDER_SUM])), task="T-030")
op("getMyOrder", "get", "/orders/{orderId}", "M04", "Suivre une de ses commandes",
   roles=C, own={"customer": "own"}, uc=["UC-006", "UC-009"], rows=["MP-05"], ok=(200, ref("Order"), EX_ORDER),
   desc="can_cancel = aucune sous-commande collectée et statut avant in_collection (RG-010, CA-F010-4). "
        "cancellation_cause renseignée si annulée (CA-F014-2).", task="T-030")
op("cancelMyOrder", "post", "/orders/{orderId}/cancel", "M04", "Annuler une de ses commandes",
   roles=C, own={"customer": "own"}, uc=["UC-007"], rows=["MP-05"],
   ok=(200, ref("Order"), with_(EX_ORDER, status="cancelled", can_cancel=False, cancellation_cause="customer_request")),
   errors=[(409, E409T("in_collection", "cancel"))],
   desc="STATE-001 t2/t4 : stock restitué, vendeurs notifiés (CA-F008-1) ; refus dès in_collection (CA-F008-2).", task="T-030")
op("getOrderConfirmation", "get", "/orders/{orderId}/confirmation", "M04", "Consulter la confirmation écrite",
   roles=C, own={"customer": "own"}, uc=["UC-005"], rows=["MP-05"],
   ok=(200, ref("OrderConfirmation"), {
       "order_reference": "CMD-2026-000123", "issued_at": "2026-10-14T10:00:01Z",
       "sellers": [{"shop_name": "Coopérative Argan Nord", "legal_name": "Coopérative Argan Nord SARL",
                    "commune": "Gueznaia", "lines": [{"product_name": "Huile d'argan 250 ml", "quantity": 1,
                                                      "unit_price": "120.00", "line_total": "120.00"}]}],
       "items_total": "120.00", "delivery_fee": "25.00", "total": "145.00", "payment_method": "cash_on_delivery",
       "return_policy": "Vous pouvez retourner chaque produit dans les 7 jours suivant sa réception, sauf exceptions légales."}),
   desc="RG-026 (contenu HYPOTHÈSE, Q39 identité du fournisseur, validation juridique C-08).", task="T-029")

# ===================== M05 — Commandes vendeur =====================
op("listSellerSubOrders", "get", "/seller/sub-orders", "M05", "Lister ses sous-commandes",
   roles=S_, own={"seller": "own"}, uc=["UC-012"], rows=["MP-12"],
   query=[("status", ref("SubOrderStatus"), "Filtre statut", "new"), ("page", i(minimum=1), "Page", 1),
          ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:SellerSubOrder", page([EX_SSUB])), desc="CA-F009-1 : ses produits seulement, sans contact client.",
   task="T-033")
op("getSellerSubOrder", "get", "/seller/sub-orders/{subOrderId}", "M05", "Consulter une de ses sous-commandes",
   roles=S_, own={"seller": "own"}, uc=["UC-012"], rows=["MP-12"], ok=(200, ref("SellerSubOrder"), EX_SSUB), task="T-033")
op("acceptSubOrder", "post", "/seller/sub-orders/{subOrderId}/accept", "M05", "Accepter une sous-commande",
   roles=S_, own={"seller": "own"}, uc=["UC-012"], rows=["MP-12"],
   ok=(200, ref("SellerSubOrder"), with_(EX_SSUB, status="accepted")),
   errors=[(409, E409T("cancelled", "accept"))], desc="STATE-002 t1.", task="T-033")
op("refuseSubOrder", "post", "/seller/sub-orders/{subOrderId}/refuse", "M05",
   "Refuser une sous-commande (annule la commande entière)",
   roles=S_, own={"seller": "own"}, uc=["UC-012"], rows=["MP-12"], req=ref("ReasonRequest"),
   req_ex={"reason": "Rupture de stock chez le producteur"},
   ok=(200, ref("SellerSubOrder"), with_(EX_SSUB, status="refused", refusal_reason="Rupture de stock chez le producteur")),
   errors=[(409, E409T("ready_for_pickup", "refuse"))],
   desc="STATE-002 t2 → commande annulée, stocks restitués, client et autres vendeurs notifiés (RG-008, CA-F009-3).",
   task="T-033")
op("markSubOrderReady", "post", "/seller/sub-orders/{subOrderId}/ready", "M05", "Déclarer une sous-commande prête pour collecte",
   roles=S_, own={"seller": "own"}, uc=["UC-012"], rows=["MP-12"],
   ok=(200, ref("SellerSubOrder"), with_(EX_SSUB, status="ready_for_pickup")),
   errors=[(409, E409T("new", "ready"))], desc="STATE-002 t3 (CA-F009-2).", task="T-033")

# ===================== M06 — Livraison et encaissement (admin) =====================
op("adminListOrders", "get", "/admin/orders", "M06", "Lister les commandes (supervision, commandes prêtes)",
   roles=A, uc=["UC-015", "UC-023"], rows=["MP-05", "MX-04"],
   query=[("status", ref("OrderStatus"), "Filtre statut", "confirmed"),
          ("ready_for_handover", B, "Seulement les commandes dont toutes les sous-commandes sont prêtes (P5.1)", True),
          ("page", i(minimum=1), "Page", 1), ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:AdminOrderSummary", page([EX_AORDER_SUM])), task="T-037")
op("adminGetOrder", "get", "/admin/orders/{orderId}", "M06", "Consulter une commande (vue administrateur)",
   roles=A, uc=["UC-015", "UC-016", "UC-023"], rows=["MP-05", "MX-04"], ok=(200, ref("AdminOrder"), EX_AORDER),
   desc="Seul l'administrateur voit adresse et téléphone du client et les adresses de collecte (§19).", task="T-041")
op("adminHandoverOrder", "post", "/admin/orders/{orderId}/handover", "M06",
   "Enregistrer la transmission à la société de livraison",
   roles=A, uc=["UC-015"], rows=["MP-13"], ok=(200, ref("AdminOrder"), with_(EX_AORDER, status="in_collection")),
   errors=[(409, E409T("confirmed", "handover"))],
   desc="STATE-001 t3, garde : toutes les sous-commandes prêtes ; passe in_collection (D44, CA-F010-4). Historisé (ENF-008).",
   task="T-037")
op("adminMarkSubOrderCollected", "post", "/admin/sub-orders/{subOrderId}/collected", "M06",
   "Saisir la collecte d'une sous-commande",
   roles=A, uc=["UC-016"], rows=["MP-13"], ok=(200, ref("AdminSubOrder"), with_(EX_ASUB, status="collected")),
   errors=[(409, E409T("accepted", "collected"))], desc="STATE-002 t4 (RG-029).", task="T-037")
op("adminMarkOutForDelivery", "post", "/admin/orders/{orderId}/out-for-delivery", "M06", "Saisir « en livraison »",
   roles=A, uc=["UC-016"], rows=["MP-13"], ok=(200, ref("AdminOrder"), with_(EX_AORDER, status="out_for_delivery")),
   errors=[(409, E409T("in_collection", "out_for_delivery"))],
   desc="STATE-001 t5, garde : toutes les sous-commandes collectées (RG-008). Client notifié.", task="T-037")
op("adminMarkDeliveredPaid", "post", "/admin/orders/{orderId}/delivered-paid", "M06",
   "Saisir « livrée et payée » (montant encaissé, date de réception)",
   roles=A, uc=["UC-016"], rows=["MP-13"], req=ref("DeliveredPaidRequest"),
   req_ex={"collected_amount": "220.00", "received_at": "2026-10-20T18:30:00Z"},
   ok=(200, ref("AdminOrder"), with_(EX_AORDER, status="delivered_paid", collected_amount="220.00",
                                     received_at="2026-10-20T18:30:00Z", cash_discrepancy="-5.00")),
   errors=[(409, E409T("in_collection", "delivered_paid")),
           (422, E422({"received_at": ["La date de réception est obligatoire."]}))],
   desc="STATE-001 t6 : commande close, montants vendeurs « held » par ligne (CA-F010-1, STATE-004 t0) ; "
        "écart signalé si encaissé ≠ dû (CA-F010-2, cash_discrepancies).", task="T-038")
op("adminMarkDeliveryFailed", "post", "/admin/orders/{orderId}/delivery-failed", "M06",
   "Saisir un échec de livraison (motif)",
   roles=A, uc=["UC-016"], rows=["MP-13"], req=ref("ReasonRequest"), req_ex={"reason": "Client injoignable"},
   ok=(200, ref("AdminOrder"), with_(EX_AORDER, status="delivery_failed", failure_reason="Client injoignable")),
   errors=[(409, E409T("confirmed", "delivery_failed"))],
   desc="STATE-001 t7 : aucun montant dû, stock restitué (CA-F010-3). Suite de l'échec : [NEEDS CLARIFICATION: Q24, T-040].",
   task="T-038")
op("adminCancelOrder", "post", "/admin/orders/{orderId}/cancel", "M06", "Annuler une commande (administrateur)",
   roles=A, uc=["UC-023"], rows=["MP-05"], req=ref("ReasonRequest"), req_ex={"reason": "Vendeur suspendu"},
   ok=(200, ref("AdminOrder"), with_(EX_AORDER, status="cancelled")),
   errors=[(501, err("feature_blocked", "Annulation administrateur non modélisée (U-02).", {"blocked_by": "U-02"}))],
   blocked="U-02 (STATE-001 sans transition d'annulation administrateur) — T-060",
   desc="Matrice §5 : l'administrateur peut annuler. Le contrat est réservé ; l'implémentation attend la mise à jour de "
        "STATE-001 par Blueprint (U-02). Tant que bloqué : 501 feature_blocked.", task="T-060")
op("adminAcceptSubOrder", "post", "/admin/sub-orders/{subOrderId}/accept", "M06",
   "Accepter une sous-commande à la place du vendeur",
   roles=A, uc=["UC-023"], rows=["MP-12"], ok=(200, ref("AdminSubOrder"), with_(EX_ASUB, status="accepted")),
   errors=[(409, E409T("cancelled", "accept"))], hyp="Périmètre de supervision F013 (UC-023 [I], N9)", task="T-060")
op("adminRefuseSubOrder", "post", "/admin/sub-orders/{subOrderId}/refuse", "M06",
   "Refuser une sous-commande à la place du vendeur",
   roles=A, uc=["UC-023"], rows=["MP-12"], req=ref("ReasonRequest"), req_ex={"reason": "Vendeur suspendu"},
   ok=(200, ref("AdminSubOrder"), with_(EX_ASUB, status="refused", refusal_reason="Vendeur suspendu")),
   errors=[(409, E409T("collected", "refuse"))], hyp="Périmètre de supervision F013 (UC-023 [I], N9)", task="T-060")
op("adminMarkSubOrderReady", "post", "/admin/sub-orders/{subOrderId}/ready", "M06",
   "Déclarer prête une sous-commande à la place du vendeur",
   roles=A, uc=["UC-023"], rows=["MP-12"], ok=(200, ref("AdminSubOrder"), EX_ASUB),
   errors=[(409, E409T("new", "ready"))], hyp="Périmètre de supervision F013 (UC-023 [I], N9)", task="T-060")
op("adminListDeliveryPartners", "get", "/admin/delivery-partners", "M06", "Lister les sociétés de livraison",
   roles=A, uc=["UC-017"], rows=["MP-13"], ok=(200, "page:DeliveryPartner", page([{"id": 1, "name": "Partenaire Tanger Express"}])),
   desc="Référentiel sans compte ni accès (D38, T-002 E-04).", task="T-039")
op("adminCreateDeliveryPartner", "post", "/admin/delivery-partners", "M06", "Enregistrer une société de livraison",
   roles=A, uc=["UC-017"], rows=["MP-13"], req=ref("ReferenceItemWrite"), req_ex={"name": "Partenaire Tanger Express"},
   ok=(201, ref("DeliveryPartner"), {"id": 1, "name": "Partenaire Tanger Express"}),
   errors=[(409, err("duplicate_name", "Ce nom existe déjà."))], hyp="Un ou plusieurs partenaires (C-05, E-04)",
   task="T-039")
op("adminCreateFundRemittance", "post", "/admin/fund-remittances", "M06",
   "Enregistrer une remise de fonds et la rapprocher des commandes",
   roles=A, uc=["UC-017"], rows=["MP-13"], req=ref("FundRemittanceWrite"),
   req_ex={"delivery_partner_id": 1, "amount": "440.00", "remitted_on": "2026-10-22", "order_ids": [5001, 5003]},
   ok=(201, ref("FundRemittance"), {"id": 61, "delivery_partner": {"id": 1, "name": "Partenaire Tanger Express"},
                                    "amount": "440.00", "remitted_on": "2026-10-22", "order_ids": [5001, 5003],
                                    "expected_amount": "445.00", "difference": "-5.00", "has_discrepancy": True,
                                    "recorded_by_user_id": 1}),
   errors=[(422, E422({"order_ids": ["La commande 5002 n'est pas « livrée et payée »."]}))],
   desc="Rapprochement : attendu = Σ montants encaissés des commandes (RG-020) ; écart signalé (SEQ-002). HYPOTHÈSE H-05.",
   task="T-039")
op("adminListFundRemittances", "get", "/admin/fund-remittances", "M06", "Lister les remises de fonds",
   roles=A, uc=["UC-017"], rows=["MP-13", "MX-04"],
   query=[("page", i(minimum=1), "Page", 1), ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:FundRemittance", page([{"id": 61, "delivery_partner": {"id": 1, "name": "Partenaire Tanger Express"},
                                          "amount": "440.00", "remitted_on": "2026-10-22", "order_ids": [5001, 5003],
                                          "expected_amount": "445.00", "difference": "-5.00", "has_discrepancy": True,
                                          "recorded_by_user_id": 1}])), task="T-039")
op("adminListCashDiscrepancies", "get", "/admin/cash-discrepancies", "M06", "Lister les écarts d'encaissement",
   roles=A, uc=["UC-017"], rows=["MP-13", "MX-04"],
   query=[("page", i(minimum=1), "Page", 1), ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:CashDiscrepancy", page([{"id": 9, "order_id": 5001, "order_reference": "CMD-2026-000123",
                                           "amount": "-5.00", "recorded_on": "2026-10-20"}])),
   desc="CA-F010-2.", task="T-038")

# ===================== M11 — Retours =====================
op("getReturnEligibility", "get", "/orders/{orderId}/return-eligibility", "M11",
   "Connaître les produits retournables d'une commande",
   roles=C, own={"customer": "own"}, uc=["UC-008"], rows=["MP-06"],
   ok=(200, ref("ReturnEligibility"), {
       "order_id": 5001, "received_at": "2026-10-20T18:30:00Z", "return_deadline_at": "2026-10-27T18:30:00Z",
       "lines": [{"order_line_id": 7001, "product_name": "Huile d'argan 250 ml", "quantity": 1, "returnable_quantity": 1,
                  "eligible": True, "ineligibility_reason": None},
                 {"order_line_id": 7002, "product_name": "Miel de thym 500 g", "quantity": 1, "returnable_quantity": 0,
                  "eligible": False, "ineligibility_reason": "product_excluded"}],
       "change_of_mind_fee": "15.00", "allowed_refund_methods": ["bank_transfer", "other_traceable"]}),
   desc="Raison indiquée pour chaque produit non retournable (CA-F022-2/3/8) ; frais affichés avant confirmation "
        "(CA-F022-1, Q45). Voir écart E-T03-01 (raison d'exclusion non figée en base).", task="T-042")
op("createReturn", "post", "/returns", "M11", "Demander le retour d'un produit reçu",
   roles=C, own={"customer": "own"}, uc=["UC-008"], rows=["MP-06"], req=ref("ReturnWrite"),
   req_ex={"order_line_id": 7001, "quantity": 1, "reason": "defective", "refund_method": "bank_transfer",
           "refund_details": "RIB 011 780 0000123456789 22", "photo_file_id": 502},
   ok=(201, ref("CustomerReturn"), EX_CRET),
   errors=[(422, err("return_not_eligible", "Le délai de retour de 7 jours est dépassé.", {"reason": "window_expired"})),
           (422, E422({"refund_method": ["Le remboursement en espèces n'est pas autorisé."]}))],
   desc="Un retour par ligne (RG-030) ; enregistré sans acceptation préalable (P3.4 [I]) ; vendeur et admin notifiés "
        "(CA-F022-1). Moyen traçable uniquement (RG-022, CA-F022-4). Plusieurs produits = plusieurs appels (CA-F022-9).",
   task="T-043")
op("listMyReturns", "get", "/returns", "M11", "Lister ses retours",
   roles=C, own={"customer": "own"}, uc=["UC-008"], rows=["MP-06"],
   query=[("page", i(minimum=1), "Page", 1), ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:CustomerReturn", page([EX_CRET])), task="T-043")
op("getMyReturn", "get", "/returns/{returnId}", "M11", "Suivre un de ses retours",
   roles=C, own={"customer": "own"}, uc=["UC-008"], rows=["MP-06"], ok=(200, ref("CustomerReturn"), EX_CRET), task="T-043")
op("sellerListReturns", "get", "/seller/returns", "M11", "Lister les retours de ses produits",
   roles=S_, own={"seller": "own"}, uc=["UC-013"], rows=["MP-07"],
   query=[("status", ref("ReturnStatus"), "Filtre statut", "picked_up"), ("page", i(minimum=1), "Page", 1),
          ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:SellerReturn", page([EX_SRET])), task="T-045")
op("sellerGetReturn", "get", "/seller/returns/{returnId}", "M11", "Consulter un retour d'un de ses produits",
   roles=S_, own={"seller": "own"}, uc=["UC-013"], rows=["MP-07"], ok=(200, ref("SellerReturn"), EX_SRET), task="T-045")
op("sellerInspectReturn", "post", "/seller/returns/{returnId}/inspection", "M11",
   "Vérifier un produit retourné et décider de sa remise en vente",
   roles=S_, own={"seller": "own"}, uc=["UC-013"], rows=["MP-07"], req=ref("InspectionWrite"),
   req_ex={"result": "disputed", "dispute_reason": "Flacon ouvert et entamé ; motif « défaut » non constaté.", "restock": False},
   ok=(200, ref("SellerReturn"), with_(EX_SRET, status="in_dispute",
                                       inspection={"result": "disputed", "dispute_reason": "Flacon ouvert et entamé ; motif « défaut » non constaté.",
                                                   "restock": False, "inspected_at": "2026-10-24T11:00:00Z"},
                                       dispute=EX_DISPUTE)),
   errors=[(409, E409T("requested", "inspect")),
           (422, E422({"dispute_reason": ["Le motif est obligatoire en cas de contestation."]}))],
   desc="STATE-003 t3/t4/t6 : conforme → verified_by_seller ; contesté → disputed puis in_dispute, admin notifié "
        "(CA-F022-6). restock = vrai → stock restitué (RG-017, D43). Délai : [NEEDS CLARIFICATION: Q44].", task="T-045")
op("adminListReturns", "get", "/admin/returns", "M11", "Lister les retours (alerte de délai légal)",
   roles=A, uc=["UC-019", "UC-023"], rows=["MP-09", "MX-04"],
   query=[("status", ref("ReturnStatus"), "Filtre statut", "in_dispute"),
          ("near_legal_deadline", B, "Seulement les retours signalés proches du délai légal (CA-F022-7)", True),
          ("page", i(minimum=1), "Page", 1), ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:AdminReturn", page([with_(EX_ARET, near_legal_deadline=True)])),
   desc="near_legal_deadline : demande > seuil (12 j, paramètre) sans remboursement (ENF-012).", task="T-052")
op("adminGetReturn", "get", "/admin/returns/{returnId}", "M11", "Consulter un retour (vue administrateur)",
   roles=A, uc=["UC-018", "UC-019", "UC-023"], rows=["MP-08", "MP-09", "MX-04"], ok=(200, ref("AdminReturn"), EX_ARET),
   task="T-052")
op("adminRequestReturnPickup", "post", "/admin/returns/{returnId}/pickup-requested", "M11",
   "Enregistrer la demande de reprise à la société de livraison",
   roles=A, uc=["UC-016"], rows=["MP-13"], ok=(200, ref("AdminReturn"), with_(EX_ARET, status="pickup_in_progress", inspection=None)),
   errors=[(409, E409T("picked_up", "pickup_requested"))], desc="STATE-003 t1 [I].", task="T-044")
op("adminMarkReturnPickedUp", "post", "/admin/returns/{returnId}/picked-up", "M11", "Saisir la reprise du produit",
   roles=A, uc=["UC-016"], rows=["MP-13"], ok=(200, ref("AdminReturn"), with_(EX_ARET, status="picked_up", inspection=None)),
   errors=[(409, E409T("requested", "picked_up"))], desc="STATE-003 t2 (RG-029) ; vendeur notifié.", task="T-044")
op("adminInspectReturn", "post", "/admin/returns/{returnId}/inspection", "M11",
   "Vérifier un retour à la place du vendeur (absence de vérification)",
   roles=A, uc=["UC-023"], rows=["MP-07"], req=ref("InspectionWrite"),
   req_ex={"result": "compliant", "dispute_reason": None, "restock": True},
   ok=(200, ref("AdminReturn"), EX_ARET),
   errors=[(501, err("feature_blocked", "Décision administrateur à défaut de vérification non modélisée (U-01, Q44).",
                     {"blocked_by": "U-01"}))],
   blocked="U-01 / Q44 (délai de vérification et transition STATE-003) — T-046",
   desc="Matrice §5 : l'administrateur vérifie en cas d'absence de vérification. Contrat réservé ; 501 tant que bloqué.",
   task="T-046")
op("adminDecideDispute", "post", "/admin/returns/{returnId}/dispute-decision", "M11", "Arbitrer un litige de retour",
   roles=A, uc=["UC-018"], rows=["MP-08", "MP-07"], req=ref("DisputeDecisionWrite"),
   req_ex={"decision": "in_favor_of_customer", "decision_reason": "Défaut visible sur la photo du client.",
           "refunded_amount": "120.00", "fee_charged_to": "seller"},
   ok=(200, ref("AdminReturn"), with_(EX_ARET, status="in_dispute",
                                      dispute={"opened_at": "2026-10-24T11:00:00Z", "decision": "in_favor_of_customer",
                                               "decision_reason": "Défaut visible sur la photo du client.",
                                               "refunded_amount": "120.00", "fee_charged_to": "seller",
                                               "decided_at": "2026-10-25T09:00:00Z"})),
   errors=[(409, E409T("verified_by_seller", "dispute_decision")),
           (422, E422({"refunded_amount": ["Obligatoire si la décision est en faveur du client."]}))],
   desc="STATE-003 t7/t8 : en faveur du client → remboursement selon la décision (montant, imputation des frais) ; "
        "en faveur du vendeur → return_refused, produit renvoyé [I]. Décision finale de l'administrateur (RG-027 [I]).",
   task="T-047")
op("adminRecordRefund", "post", "/admin/returns/{returnId}/refund", "M11", "Enregistrer le remboursement du client",
   roles=A, uc=["UC-019"], rows=["MP-09"], req=ref("RefundWrite"),
   req_ex={"method": "bank_transfer", "reference": "VIR-2026-10-28-0042", "refunded_on": "2026-10-28"},
   ok=(200, ref("AdminReturn"), with_(EX_ARET, status="customer_refunded", refund=EX_REFUND)),
   errors=[(409, E409T("picked_up", "refund")),
           (422, E422({"method": ["Moyen de remboursement non traçable refusé."]}))],
   desc="Montant calculé par le serveur : prix × quantité − frais si changement d'avis, ou montant de la décision de litige "
        "(RG-022, CA-F022-5) ; frais de livraison initiaux selon paramètre (Q40). Déduction vendeur (RG-021, STATE-004 t2/t4). "
        "Client notifié.", task="T-049")

# ===================== M07 — Montants et reversements =====================
op("sellerGetAmountsSummary", "get", "/seller/amounts/summary", "M07", "Consulter le total de ses montants par statut",
   roles=S_, own={"seller": "own"}, uc=["UC-014"], rows=["MP-14"],
   ok=(200, ref("SellerAmountsSummary"), {"held": "300.00", "available": "500.00", "paid_out": "1250.00",
                                          "deducted": "100.00", "pending_deductions": "80.00"}),
   task="T-055")
op("sellerListAmounts", "get", "/seller/amounts", "M07", "Lister ses montants (retenus, disponibles, reversés, déduits)",
   roles=S_, own={"seller": "own"}, uc=["UC-014"], rows=["MP-14"],
   query=[("status", ref("SellerAmountStatus"), "Filtre statut", "held"), ("page", i(minimum=1), "Page", 1),
          ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:SellerAmount", page([EX_SAMOUNT])), task="T-055")
op("sellerListDeductions", "get", "/seller/deductions", "M07", "Lister ses déductions et régularisations",
   roles=S_, own={"seller": "own"}, uc=["UC-014"], rows=["MP-14"],
   query=[("page", i(minimum=1), "Page", 1), ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:Deduction", page([EX_DEDUCTION])), desc="CA-F011-4 : régularisation visible dans l'historique.", task="T-048")
op("sellerListPayouts", "get", "/seller/payouts", "M07", "Consulter l'historique de ses reversements",
   roles=S_, own={"seller": "own"}, uc=["UC-014"], rows=["MP-14"],
   query=[("page", i(minimum=1), "Page", 1), ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:Payout", page([EX_PAYOUT])), desc="CA-F011-2 : montant, date, mode, commandes concernées.", task="T-055")
op("adminListSellerAmounts", "get", "/admin/seller-amounts", "M07", "Consulter les montants d'un vendeur",
   roles=A, uc=["UC-023"], rows=["MP-14", "MX-04"],
   query=[("seller_id", ID, "Vendeur", 12), ("status", ref("SellerAmountStatus"), "Filtre statut", "available"),
          ("page", i(minimum=1), "Page", 1), ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:SellerAmount", page([with_(EX_SAMOUNT, status="available")])), task="T-059")
op("adminPreviewPayouts", "get", "/admin/payouts/preview", "M07", "Calculer les reversements de la semaine",
   roles=A, uc=["UC-020"], rows=["MP-15"],
   query=[("period_start", D, "Lundi de la semaine de reversement", "2026-11-02")],
   ok=(200, "page:PayoutPreviewLine", page([{"seller_id": 12, "legal_name": "Coopérative Argan Nord SARL",
                                             "payout_method": "bank_transfer", "available_total": "500.00",
                                             "pending_deductions_total": "80.00", "payable_amount": "420.00",
                                             "negative_balance": False}])),
   desc="Σ disponibles − Σ déductions en attente ; montants retenus exclus (CA-F011-5) ; solde négatif signalé (H-07, Q38). "
        "Aucune écriture.", task="T-054")
op("adminCreatePayout", "post", "/admin/payouts", "M07", "Enregistrer le reversement hebdomadaire d'un vendeur",
   roles=A, uc=["UC-020"], rows=["MP-15"], req=ref("PayoutWrite"),
   req_ex={"seller_id": 12, "period_start": "2026-11-02", "paid_on": "2026-11-02", "method": "bank_transfer", "cash_proof": None},
   ok=(201, ref("Payout"), EX_PAYOUT),
   errors=[(409, err("payout_already_recorded", "Un reversement existe déjà pour ce vendeur et cette semaine.",
                     {"payout_id": 401})),
           (422, err("nothing_to_pay_out", "Aucun montant positif à reverser cette semaine.", {"payable_amount": "-30.00"})),
           (422, E422({"cash_proof": ["La preuve de remise est obligatoire pour un reversement en espèces."]}))],
   desc="Montant calculé par le serveur (jamais saisi) ; montants passent paid_out, déductions imputées (STATE-004 t3). "
        "Unicité (seller_id, period_start) = idempotence.", task="T-054")
op("adminListPayouts", "get", "/admin/payouts", "M07", "Lister les reversements",
   roles=A, uc=["UC-020", "UC-023"], rows=["MP-15", "MX-04"],
   query=[("seller_id", ID, "Vendeur", 12), ("page", i(minimum=1), "Page", 1), ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:Payout", page([EX_PAYOUT])), task="T-054")

# ===================== M08 — Avis =====================
op("upsertReview", "put", "/order-lines/{orderLineId}/review", "M08", "Noter et commenter un produit reçu",
   roles=C, own={"customer": "own"}, uc=["UC-009"], rows=["MP-10"], req=ref("ReviewWrite"),
   req_ex={"rating": 5, "comment": "Très bonne huile."}, ok=(200, ref("Review"), EX_REVIEW),
   errors=[(422, err("review_not_allowed", "Vous pourrez noter ce produit après l'avoir reçu."))],
   desc="Commande delivered_paid uniquement (RG-011, CA-F012-1/2). Un avis par ligne : un second appel modifie l'avis "
        "(F012). 201 à la création, 200 à la modification.", task="T-056")

# ===================== M09 — Administration et modération =====================
for kind, label, sch, ex_item, ex_write, task in [
    ("categories", "catégorie", "Category", EX_CAT, {"name": "Cosmétiques naturels", "is_return_excluded": False}, "T-017"),
    ("served-cities", "ville desservie", "ReferenceItem", EX_CITY, {"name": "Tétouan"}, "T-017"),
    ("seller-communes", "commune vendeur", "ReferenceItem", EX_COMMUNE, {"name": "Gueznaia"}, "T-017"),
]:
    cname = "".join(p.capitalize() for p in kind.split("-"))
    single = cname[:-1] if not cname.endswith("ies") else cname[:-3] + "y"
    if cname.endswith("ies"):
        single = cname[:-3] + "y"
    wsch = "CategoryWrite" if sch == "Category" else "ReferenceItemWrite"
    psch = "CategoryPatch" if sch == "Category" else "ReferenceItemWrite"
    op(f"adminList{cname}", "get", f"/admin/{kind}", "M09", f"Lister les éléments : {label}",
       roles=A, uc=["UC-021"], rows=["MP-17"], ok=(200, f"page:{sch}", page([ex_item])), task=task)
    op(f"adminCreate{single}", "post", f"/admin/{kind}", "M09", f"Créer : {label}",
       roles=A, uc=["UC-021"], rows=["MP-17"], req=ref(wsch), req_ex=ex_write, ok=(201, ref(sch), ex_item),
       errors=[(409, err("duplicate_name", "Ce nom existe déjà."))],
       desc="RG-001/RG-023/RG-019 : extension des zones sans redéploiement (ENF-010).", task=task)
    op(f"adminUpdate{single}", "patch", f"/admin/{kind}/{{id}}", "M09", f"Modifier : {label}",
       roles=A, uc=["UC-021"], rows=["MP-17"], req=ref(psch),
       req_ex={"is_return_excluded": True} if sch == "Category" else {"name": ex_item["name"]},
       ok=(200, ref(sch), with_(ex_item, is_return_excluded=True) if sch == "Category" else ex_item),
       errors=[(409, err("duplicate_name", "Ce nom existe déjà."))],
       desc="Catégorie : l'exclusion s'applique aux commandes futures (exclusion figée sur la ligne, H-T02-1)." if sch == "Category" else "",
       task=task)
    op(f"adminDelete{single}", "delete", f"/admin/{kind}/{{id}}", "M09", f"Supprimer : {label}",
       roles=A, uc=["UC-021"], rows=["MP-17"], ok=(204, None, None),
       errors=[(409, err("resource_in_use", "Suppression impossible : élément utilisé."))], task=task)

op("adminHideProduct", "post", "/admin/products/{productId}/hide", "M09", "Masquer un produit",
   roles=A, uc=["UC-022"], rows=["MP-16", "MP-11"], req=ref("ReasonRequest"), req_ex={"reason": "Produit non local"},
   ok=(200, ref("AdminProduct"), {"id": 101, "name": "Huile d'argan 250 ml", "price": "120.00", "stock": 15,
                                  "category_id": 3, "is_published": True, "is_hidden": True,
                                  "hidden_at": "2026-10-14T12:00:00Z",
                                  "seller": {"id": 12, "legal_name": "Coopérative Argan Nord SARL", "status": "active"},
                                  "created_at": "2026-10-10T08:00:00Z"}),
   desc="Disparaît du catalogue, vendeur informé (RG-015, CA-F013-1). Historisé.", task="T-058")
op("adminUnhideProduct", "post", "/admin/products/{productId}/unhide", "M09", "Rendre visible un produit masqué",
   roles=A, uc=["UC-022"], rows=["MP-16", "MP-11"],
   ok=(200, ref("AdminProduct"), {"id": 101, "name": "Huile d'argan 250 ml", "price": "120.00", "stock": 15,
                                  "category_id": 3, "is_published": True, "is_hidden": False, "hidden_at": None,
                                  "seller": {"id": 12, "legal_name": "Coopérative Argan Nord SARL", "status": "active"},
                                  "created_at": "2026-10-10T08:00:00Z"}),
   hyp="H-T03-03 : levée de la modération non décrite par le cahier", task="T-058")
op("adminSuspendSeller", "post", "/admin/sellers/{sellerId}/suspend", "M09", "Suspendre un vendeur",
   roles=A, uc=["UC-022"], rows=["MP-16"], req=ref("ReasonRequest"), req_ex={"reason": "Produits non conformes répétés"},
   ok=(200, ref("AdminSeller"), with_(EX_ASELLER, status="suspended", suspended_at="2026-10-14T12:00:00Z")),
   errors=[(409, E409T("suspended", "suspend"))],
   desc="Boutique et produits invisibles (CA-F013-2). Sort des en-cours décidé par l'admin (F013, T-060, U-02).", task="T-058")
op("adminReactivateSeller", "post", "/admin/sellers/{sellerId}/reactivate", "M09", "Réactiver un vendeur suspendu",
   roles=A, uc=["UC-022"], rows=["MP-16"], ok=(200, ref("AdminSeller"), EX_ASELLER),
   errors=[(409, E409T("active", "reactivate"))], hyp="H-T03-03 : levée de la modération non décrite par le cahier",
   task="T-058")
op("adminListReviews", "get", "/admin/reviews", "M09", "Lister les avis (modération)",
   roles=A, uc=["UC-022"], rows=["MP-16"],
   query=[("product_id", ID, "Produit", 101), ("is_hidden", B, "Filtre masqué", False), ("page", i(minimum=1), "Page", 1),
          ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:AdminReview", page([{"id": 900, "product_id": 101, "order_line_id": 7001, "customer_id": 41,
                                       "rating": 1, "comment": "Texte abusif", "is_hidden": False, "hidden_at": None,
                                       "created_at": "2026-10-20T09:00:00Z"}])), task="T-058")
op("adminHideReview", "post", "/admin/reviews/{reviewId}/hide", "M09", "Masquer un avis",
   roles=A, uc=["UC-022"], rows=["MP-16"], req=ref("ReasonRequest"), req_ex={"reason": "Propos injurieux"},
   ok=(200, ref("AdminReview"), {"id": 900, "product_id": 101, "order_line_id": 7001, "customer_id": 41, "rating": 1,
                                 "comment": "Texte abusif", "is_hidden": True, "hidden_at": "2026-10-21T08:00:00Z",
                                 "created_at": "2026-10-20T09:00:00Z"}),
   desc="Moyenne recalculée sans l'avis (CA-F013-3).", task="T-058")
op("adminUnhideReview", "post", "/admin/reviews/{reviewId}/unhide", "M09", "Rendre visible un avis masqué",
   roles=A, uc=["UC-022"], rows=["MP-16"],
   ok=(200, ref("AdminReview"), {"id": 900, "product_id": 101, "order_line_id": 7001, "customer_id": 41, "rating": 1,
                                 "comment": "Texte abusif", "is_hidden": False, "hidden_at": None,
                                 "created_at": "2026-10-20T09:00:00Z"}),
   hyp="H-T03-03 : levée de la modération non décrite par le cahier", task="T-058")
op("adminListSellers", "get", "/admin/sellers", "M09", "Lister les vendeurs",
   roles=A, uc=["UC-023"], rows=["MX-04"],
   query=[("status", ref("SellerStatus"), "Filtre statut", "active"), ("page", i(minimum=1), "Page", 1),
          ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:AdminSeller", page([EX_ASELLER])), task="T-059")
op("adminGetSeller", "get", "/admin/sellers/{sellerId}", "M09", "Consulter un vendeur",
   roles=A, uc=["UC-023"], rows=["MX-04"], ok=(200, ref("AdminSeller"), EX_ASELLER),
   desc="Coordonnées bancaires visibles de l'administrateur (FR-055).", task="T-059")
op("adminListProducts", "get", "/admin/products", "M09", "Lister tous les produits (y compris masqués)",
   roles=A, uc=["UC-023", "UC-022"], rows=["MX-04", "MP-16"],
   query=[("seller_id", ID, "Vendeur", 12), ("is_hidden", B, "Filtre masqué", False), ("page", i(minimum=1), "Page", 1),
          ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:AdminProduct", page([{"id": 101, "name": "Huile d'argan 250 ml", "price": "120.00", "stock": 15,
                                        "category_id": 3, "is_published": True, "is_hidden": False, "hidden_at": None,
                                        "seller": {"id": 12, "legal_name": "Coopérative Argan Nord SARL", "status": "active"},
                                        "created_at": "2026-10-10T08:00:00Z"}])), task="T-059")
op("adminListAuditEntries", "get", "/admin/audit-entries", "SOCLE", "Consulter le journal d'audit",
   roles=A, uc=["UC-023"], rows=["MX-04"],
   query=[("target_type", s(), "Type de cible", "order"), ("target_id", ID, "Identifiant de cible", 5001),
          ("action_type", ref("AuditActionType"), "Type d'action", "order_status_changed"),
          ("page", i(minimum=1), "Page", 1), ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:AuditEntry", page([{"id": 1, "occurred_at": "2026-10-20T18:31:02.120Z", "actor_user_id": 1,
                                      "actor_system": None, "action_type": "order_status_changed", "target_type": "order",
                                      "target_id": 5001, "from_status": "out_for_delivery", "to_status": "delivered_paid",
                                      "amount": "220.00", "reason": None, "corrects_entry_id": None}])),
   desc="Lecture seule (ENF-008, ADR-015) : aucun point d'accès d'écriture ou de suppression.", task="T-008")
op("adminListSettings", "get", "/admin/settings", "SOCLE", "Lister les paramètres métier",
   roles=A, uc=["UC-023"], rows=["MX-05"],
   ok=(200, "page:Setting", page([{"key": "seller_response_delay_hours", "value": None, "value_type": "integer",
                                   "description": "Délai de réponse vendeur (Q19) — valeur à fixer par @user",
                                   "updated_at": None}])),
   desc="Clés indicatives (liste fixée par T-007) : délai vendeur (Q19), frais de livraison (Q27), remboursement des frais "
        "de livraison (Q40), frais de retour (Q45), délai de vérification (Q44), délai de retour (7 j), délai légal (15 j), "
        "seuil d'alerte (12 j), jour de reversement, taille photo, taille de page.", task="T-007")
op("adminUpdateSetting", "patch", "/admin/settings/{key}", "SOCLE", "Modifier un paramètre métier",
   roles=A, uc=["UC-023"], rows=["MX-05"], req=ref("SettingWrite"), req_ex={"value": 24},
   ok=(200, ref("Setting"), {"key": "seller_response_delay_hours", "value": 24, "value_type": "integer",
                             "description": "Délai de réponse vendeur (Q19)", "updated_at": "2026-10-14T12:00:00Z"}),
   errors=[(422, E422({"value": ["Un entier positif est attendu."]}))],
   desc="Effet sans redéploiement (H-08) ; historisé (ENF-008).", task="T-007")

# ===================== M10 — Notifications =====================
op("listNotifications", "get", "/notifications", "M10", "Lister ses notifications",
   roles=["customer", "seller", "admin"], own={"customer": "own", "seller": "own", "admin": "own"},
   uc=["UC-006"], rows=["MX-03"],
   query=[("unread", B, "Seulement les non lues", True), ("page", i(minimum=1), "Page", 1),
          ("per_page", i(minimum=1), "Taille de page", 20)],
   ok=(200, "page:Notification", page([{"id": 3, "type": "order_cancelled", "title": "Commande annulée",
                                        "body": "Votre commande CMD-2026-000123 est annulée : un produit n'est pas disponible.",
                                        "data": {"order_id": 5001}, "read_at": None, "created_at": "2026-10-14T15:00:00Z"}])),
   desc="Notifications internes (F014, CA-F014-1/2). Canal externe : [NEEDS CLARIFICATION: Q23].", task="T-009")
op("markNotificationRead", "post", "/notifications/{notificationId}/read", "M10", "Marquer une notification comme lue",
   roles=["customer", "seller", "admin"], own={"customer": "own", "seller": "own", "admin": "own"},
   uc=["UC-006"], rows=["MX-03"], ok=(204, None, None), task="T-009")


# ---------------------------------------------------------------------------
# Construction OpenAPI
# ---------------------------------------------------------------------------

def path_params(path):
    return re.findall(r"{(\w+)}", path)


def build_request_line(o):
    url = BASE + o["path"]
    for p in path_params(o["path"]):
        url = url.replace("{" + p + "}", "settings_key" if p == "key" else str({
            "productId": 101, "itemId": 31, "orderId": 5001, "subOrderId": 6001, "returnId": 801,
            "orderLineId": 7001, "sellerId": 12, "reviewId": 900, "notificationId": 3, "id": 3}.get(p, 1)))
    if o["path"] == "/admin/settings/{key}":
        url = BASE + "/admin/settings/seller_response_delay_hours"
    if o["query"]:
        url += "?" + "&".join(f"{n}={str(ex).lower() if isinstance(ex, bool) else ex}" for n, _, _, ex in o["query"])
    headers = {}
    if not ("visitor" in o["roles"]) or o["roles"] == ["visitor"]:
        pass
    if "visitor" not in o["roles"]:
        headers["Authorization"] = "Bearer <jeton>"
    for hn, _, hex_ in o["headers"]:
        headers[hn] = hex_
    if o["req"] is not None or o["multipart"]:
        headers["Content-Type"] = "multipart/form-data" if o["multipart"] else "application/json"
    return {"method": o["method"].upper(), "url": url, "headers": headers}


def resp_schema(spec):
    if isinstance(spec, str) and spec.startswith("page:"):
        return obj({"data": arr(ref(spec[5:])), "meta": ref("PaginationMeta")})
    return obj({"data": spec})


def auto_errors(o):
    out = []
    roles = set(o["roles"])
    if "visitor" not in roles:
        out.append((401, err("unauthenticated", "Veuillez vous connecter.")))
    if roles != set(ALL_ROLES) and roles != {"visitor"}:
        denied = [r for r in ALL_ROLES if r not in roles and r != "visitor"]
        if denied:
            out.append((403, err("forbidden", "Vous n'avez pas accès à cette action.")))
    if path_params(o["path"]) and o["path"] != "/admin/settings/{key}":
        msg = "Ressource introuvable."
        out.append((404, err("not_found", msg)))
    if o["path"] == "/admin/settings/{key}":
        out.append((404, err("not_found", "Paramètre inconnu.")))
    if o["query"]:
        out.append((400, err("malformed_request", "Paramètre de requête invalide.",
                             {"parameter": o["query"][0][0]})))
    if o["method"] == "get" and set(o["roles"]) == set(ALL_ROLES):
        out.append((429, err("rate_limited", "Trop de requêtes, réessayez dans un instant.",
                             {"retry_after_seconds": 60})))
    if o["req"] is not None and not any(c == 422 and e["error"]["code"] == "validation_failed" for c, e in o["errors"]):
        out.append((422, err("validation_failed", "Certaines informations sont invalides.",
                             {"fields": {"<champ>": ["<message>"]}})))
    return out


def build_openapi():
    paths = {}
    for o in OPS:
        p = BASE + o["path"]
        entry = paths.setdefault(p, {})
        params = []
        for pp in path_params(o["path"]):
            params.append({"name": pp, "in": "path", "required": True,
                           "schema": s(pattern=r"^[a-z_]+$") if pp == "key" else ID})
        for n, sch, d, ex in o["query"]:
            params.append({"name": n, "in": "query", "required": n == "period_start", "description": d,
                           "schema": sch, "example": ex})
        for hn, hd, hex_ in o["headers"]:
            params.append({"name": hn, "in": "header", "required": False, "description": hd,
                           "schema": s(pattern=r"^[A-Za-z0-9]{32,64}$"), "example": hex_})
        operation = {
            "operationId": o["oid"], "tags": [f"{o['module']} — {MODULES[o['module']]}"], "summary": o["summary"],
        }
        desc = o["desc"]
        if o["blocked"]:
            desc = f"**BLOQUÉ** : {o['blocked']}. " + desc
        if o["hyp"]:
            desc = f"**HYPOTHÈSE** : {o['hyp']}. " + desc
        if desc:
            operation["description"] = desc
        if params:
            operation["parameters"] = params
        operation["security"] = ([{}, {"bearerAuth": []}] if "visitor" in o["roles"] and o["roles"] != ["visitor"]
                                 else [{}] if o["roles"] == ["visitor"] else [{"bearerAuth": []}])
        if o["multipart"]:
            operation["requestBody"] = {"required": True, "content": {"multipart/form-data": {
                "schema": obj({"file": s(contentMediaType="application/octet-stream")}),
                "examples": {"photo": {"summary": "Image JPEG", "value": {"file": "<binaire image/jpeg>"}}}}}}
        elif o["req"] is not None:
            operation["requestBody"] = {"required": True, "content": {"application/json": {
                "schema": o["req"], "examples": {"request": {"summary": "Exemple de requête", "value": o["req_ex"]}}}}}
        responses = {}
        code, sch, ex = o["ok"]
        if code == 204:
            responses["204"] = {"description": "Succès sans contenu"}
        else:
            if isinstance(sch, str):
                body = ex
            else:
                body = one(ex)
            r = {"description": "Succès", "content": {"application/json": {
                "schema": resp_schema(sch), "examples": {"success": {"summary": "Succès", "value": body}}}}}
            if o["resp_headers"]:
                r["headers"] = {k: {"description": v, "schema": s()} for k, v in o["resp_headers"].items()}
            responses[str(code)] = r
            if o["oid"] == "upsertReview":
                responses["201"] = {"description": "Avis créé", "content": {"application/json": {
                    "schema": resp_schema(sch), "examples": {"created": {"summary": "Création", "value": body}}}}}
        all_errors = auto_errors(o) + o["errors"]
        for c, e in all_errors:
            k = str(c)
            resp = responses.setdefault(k, {"description": ERROR_CODES[e["error"]["code"]][1],
                                            "content": {"application/json": {"schema": ref("Error"), "examples": {}}}})
            exs = resp["content"]["application/json"]["examples"]
            name = e["error"]["code"]
            n = 2
            while name in exs:
                name = f"{e['error']['code']}_{n}"
                n += 1
            exs[name] = {"summary": e["error"]["message"], "value": e}
        operation["responses"] = dict(sorted(responses.items()))
        operation["x-module"] = o["module"]
        operation["x-roles"] = o["roles"]
        operation["x-ownership"] = o["own"] or "none"
        operation["x-uc"] = o["uc"]
        operation["x-matrix-rows"] = o["rows"]
        operation["x-plan-task"] = o["task"]
        operation["x-request-example"] = build_request_line(o)
        if o["blocked"]:
            operation["x-blocked-by"] = o["blocked"]
        if o["hyp"]:
            operation["x-hypothesis"] = o["hyp"]
        entry[o["method"]] = operation
    doc = {
        "openapi": "3.1.0",
        "info": {
            "title": "Marketplace produits locaux Maroc — API V1",
            "version": "1.0.0-proposed",
            "description": (
                "Contrat d'API de la V1 (T-003). Statut : **Proposé — à valider par @user (CP-1)**.\n\n"
                "Sources : cahier des charges v1.1 (validé, D45), UC-DIAG-01..03, SEQ-001..003, STATE-001..004 "
                "(approuvés 2026-10-12), schéma T-002, conventions de socle T-001.\n\n"
                "Conventions : préfixe /api/v1 (ADR-007) ; JSON en anglais snake_case (Constitution IX, ADR-016) ; "
                "messages en français ; montants en chaîne décimale MAD (ADR-018) ; dates ISO 8601 UTC ; erreurs "
                "{error:{code,message,details}} (catalogue error-codes.md) ; pagination page/per_page ; jeton porteur "
                "(ADR-006) ; refus de rôle = 403, ressource d'un autre titulaire = 404 (ADR-017) ; transitions d'état "
                "en POST sur sous-ressource verbale, transition interdite = 409 (ADR-020).\n\n"
                "Extensions : x-module, x-roles, x-ownership, x-uc, x-matrix-rows (authorization-matrix.yaml), "
                "x-plan-task, x-request-example, x-blocked-by, x-hypothesis."),
        },
        "servers": [{"url": "http://localhost:8080", "description": "local (docker-compose, T-004)"},
                    {"url": "https://staging.example.invalid", "description": "staging — nommé seulement (étape 6)"},
                    {"url": "https://api.example.invalid", "description": "prod — nommé seulement (étape 6)"}],
        "tags": [{"name": f"{k} — {v}"} for k, v in MODULES.items()],
        "paths": paths,
        "components": {
            "securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer",
                                               "description": "Jeton opaque émis à la connexion (ADR-006)."}},
            "schemas": SCHEMAS,
        },
        "x-error-codes": {k: {"http_status": v[0], "description": v[1]} for k, v in ERROR_CODES.items()},
    }
    return doc


def build_matrix():
    rows = []
    for rid, label, src, vals, note in MATRIX_ROWS:
        ops = [o["oid"] for o in OPS if rid in o["rows"]]
        rows.append({"id": rid, "capability": label, "source": src,
                     "roles": dict(zip(ALL_ROLES, vals)), "note": note or None, "operations": ops})
    return {"version": "1.0.0-proposed", "status": "Proposé — CP-1 à valider par @user",
            "legend": {"allow": "autorisé", "own": "autorisé sur ses propres ressources seulement",
                       "allow_hyp": "autorisé (HYPOTHÈSE du cahier)", "deny": "interdit"},
            "rows": rows}


def md_escape(t):
    return str(t).replace("|", "\\|")


def build_reference_md(doc):
    lines = ["# Référence des points d'accès par module (générée)", "",
             "Générée par `tooling/build_contract.py` depuis la même table que `openapi.yaml`. Ne pas éditer à la main.",
             "Rôles : V = visiteur, C = client, S = vendeur, A = administrateur ; (p) = propriété vérifiée.", ""]
    short = {"visitor": "V", "customer": "C", "seller": "S", "admin": "A"}
    for mod, name in MODULES.items():
        mops = [o for o in OPS if o["module"] == mod]
        if not mops:
            continue
        lines += [f"## {mod} — {name}", "", "| Opération | Méthode et chemin | Rôles | UC | Matrice | Succès | Erreurs | Tâche |",
                  "|---|---|---|---|---|---|---|---|"]
        for o in mops:
            pathops = doc["paths"][BASE + o["path"]][o["method"]]
            codes = sorted(pathops["responses"].keys())
            okc = [c for c in codes if c.startswith("2")]
            errc = [c for c in codes if not c.startswith("2")]
            roles = ", ".join(short[r] + ("(p)" if o["own"].get(r) == "own" else "") for r in o["roles"])
            flag = " ⛔" if o["blocked"] else (" ⚠️H" if o["hyp"] else "")
            lines.append(f"| `{o['oid']}`{flag} | `{o['method'].upper()} {BASE}{o['path']}` | {roles} | "
                         f"{', '.join(o['uc'])} | {', '.join(o['rows'])} | {', '.join(okc)} | {', '.join(errc)} | {o['task']} |")
        lines.append("")
    lines += ["⛔ = contrat réservé, implémentation bloquée (x-blocked-by) ; ⚠️H = HYPOTHÈSE (x-hypothesis).", ""]
    return "\n".join(lines)


def build_error_codes_md():
    used = {}
    for o in OPS:
        for _, e in auto_errors(o) + o["errors"]:
            used.setdefault(e["error"]["code"], []).append(o["oid"])
    lines = ["# Catalogue des codes d'erreur (généré)", "",
             "Généré par `tooling/build_contract.py` (ADR-016). Ne pas éditer à la main.", "",
             "Enveloppe : `{\"error\": {\"code\", \"message\", \"details?\"}}` (convention T-001 `format-erreur.md`).",
             "`code` est stable et en anglais (Constitution IX) ; `message` est en français et peut être reformulé.",
             "`details` ne contient jamais de mot de passe, de coordonnée bancaire ni de trace technique.", "",
             "| Code | HTTP | Signification | Opérations |", "|---|---|---|---|"]
    for code, (status, d) in sorted(ERROR_CODES.items(), key=lambda kv: (kv[1][0], kv[0])):
        n = len(set(used.get(code, [])))
        lines.append(f"| `{code}` | {status} | {md_escape(d)} | {n if n else 'transverse (toute opération)'} |")
    lines += ["", "Codes de T-001 remplacés (ADR-016) : `acces_refuse` → `forbidden`, `ressource_introuvable` → "
              "`not_found`, `validation_echouee` → `validation_failed`, `fichier_refuse` → `file_rejected` ; "
              "paramètre `par_page` → `per_page`.", ""]
    return "\n".join(lines)


def build_matrix_md():
    sym = {"allow": "✔", "own": "✔ (siens)", "allow_hyp": "✔ (HYP.)", "deny": "—"}
    lines = ["# Matrice rôle × action (générée)", "",
             "Générée par `tooling/build_contract.py` ; source machine : `authorization-matrix.yaml` (ADR-017).",
             "MP-xx = ligne de la matrice du cahier §5 (texte repris tel quel) ; MX-xx = capacité dérivée, absente "
             "de §5 mais exigée par une fonction ou une ENF.", "",
             "Règle d'application (ADR-017) : rôle non autorisé → 403 `forbidden` ; ressource d'un autre titulaire "
             "→ 404 `not_found` ; société de livraison : aucun accès (D38).", "",
             "| Ligne | Capacité | Visiteur | Client | Vendeur | Admin | Opérations | Note |",
             "|---|---|---|---|---|---|---|---|"]
    for rid, label, src, vals, note in MATRIX_ROWS:
        ops = [o["oid"] for o in OPS if rid in o["rows"]]
        lines.append(f"| {rid} | {md_escape(label)} | " + " | ".join(sym[v] for v in vals) +
                     f" | {len(ops)} : {', '.join(f'`{x}`' for x in ops)} | {md_escape(note or src)} |")
    lines.append("")
    return "\n".join(lines)


def main():
    doc = build_openapi()
    CONTRACTS.mkdir(parents=True, exist_ok=True)

    class NoAlias(yaml.SafeDumper):
        def ignore_aliases(self, data):
            return True

    hdr = ("# GÉNÉRÉ par specs/003-contrat-api/tooling/build_contract.py — T-003 — statut : Proposé (CP-1)\n"
           "# Vérification : uv run --no-project --with pyyaml --with openapi-spec-validator --with jsonschema "
           "python specs/003-contrat-api/validation/check_contract.py\n")
    (CONTRACTS / "openapi.yaml").write_text(hdr + yaml.dump(doc, Dumper=NoAlias, sort_keys=False, allow_unicode=True,
                                                            width=120), encoding="utf-8")
    (CONTRACTS / "authorization-matrix.yaml").write_text(
        "# GÉNÉRÉ par tooling/build_contract.py — matrice rôle × action (T-003)\n"
        + yaml.dump(build_matrix(), Dumper=NoAlias, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
    (CONTRACTS / "api-reference.md").write_text(build_reference_md(doc), encoding="utf-8")
    (CONTRACTS / "error-codes.md").write_text(build_error_codes_md(), encoding="utf-8")
    (CONTRACTS / "authorization-matrix.md").write_text(build_matrix_md(), encoding="utf-8")
    print(f"operations={len(OPS)} paths={len(doc['paths'])} schemas={len(SCHEMAS)} rows={len(MATRIX_ROWS)}")


if __name__ == "__main__":
    main()
