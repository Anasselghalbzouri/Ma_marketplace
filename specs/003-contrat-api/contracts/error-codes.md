# Catalogue des codes d'erreur (généré)

Généré par `tooling/build_contract.py` (ADR-016). Ne pas éditer à la main.

Enveloppe : `{"error": {"code", "message", "details?"}}` (convention T-001 `format-erreur.md`).
`code` est stable et en anglais (Constitution IX) ; `message` est en français et peut être reformulé.
`details` ne contient jamais de mot de passe, de coordonnée bancaire ni de trace technique.

| Code | HTTP | Signification | Opérations |
|---|---|---|---|
| `malformed_request` | 400 | Requête mal formée (JSON invalide, paramètre de type incorrect). | 22 |
| `invalid_credentials` | 401 | Téléphone ou mot de passe incorrect, sans préciser lequel (F001). | 1 |
| `unauthenticated` | 401 | Jeton absent, invalide ou expiré. | 88 |
| `account_suspended` | 403 | Compte vendeur suspendu : actions d'écriture refusées (RG-015 ; HYPOTHÈSE). | 1 |
| `forbidden` | 403 | Rôle non autorisé pour cette action (matrice, ADR-017). | 88 |
| `not_found` | 404 | Ressource inexistante, non visible publiquement, ou appartenant à un autre titulaire (ADR-017). | 50 |
| `duplicate_name` | 409 | Nom déjà utilisé dans le référentiel. | 7 |
| `insufficient_stock` | 409 | Stock insuffisant à la validation ; le panier est mis à jour (F007). | 1 |
| `invalid_transition` | 409 | Transition d'état interdite depuis l'état courant (STATE-001..004). | 19 |
| `payout_already_recorded` | 409 | Reversement déjà enregistré pour ce vendeur et cette semaine (idempotence). | 1 |
| `phone_already_registered` | 409 | Téléphone déjà utilisé ; la connexion est proposée (CA-F001-2). | 2 |
| `product_unavailable` | 409 | Produit indisponible (stock 0, masqué, vendeur suspendu) — CA-F003-2. | 1 |
| `resource_in_use` | 409 | Suppression impossible : la ressource est référencée. | 3 |
| `cart_empty` | 422 | Panier vide ou sans produit disponible. | 2 |
| `city_not_served` | 422 | Adresse hors des villes desservies — seule Tanger en V1 (CA-F007-2). | 2 |
| `commune_not_allowed` | 422 | Commune hors de la liste autorisée (CA-F002-3). | 1 |
| `file_rejected` | 422 | Fichier refusé (type ou taille), FR-040. | 1 |
| `nothing_to_pay_out` | 422 | Aucun montant positif à reverser (solde nul ou négatif reporté, H-07). | 1 |
| `return_not_eligible` | 422 | Retour impossible ; details.reason = ReturnIneligibility (CA-F022-2/3/8). | 1 |
| `review_not_allowed` | 422 | Avis impossible : commande non « livrée et payée » (RG-011). | 1 |
| `validation_failed` | 422 | Données invalides ; details.fields liste les champs en erreur. | 35 |
| `rate_limited` | 429 | Trop de requêtes. | 6 |
| `server_error` | 500 | Erreur interne, sans détail d'implémentation. | transverse (toute opération) |
| `feature_blocked` | 501 | Action prévue au contrat mais bloquée par une décision manquante (U-01, U-02). | 2 |

Codes de T-001 remplacés (ADR-016) : `acces_refuse` → `forbidden`, `ressource_introuvable` → `not_found`, `validation_echouee` → `validation_failed`, `fichier_refuse` → `file_rejected` ; paramètre `par_page` → `per_page`.
