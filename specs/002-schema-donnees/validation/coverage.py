"""Couverture UML -> schéma (critère de vérification de T-002).
Lit les classes et énumérations des fichiers drawio CLASS-01/02, les tables et contraintes de la base
t002_schema, puis vérifie que chaque classe/énumération a une table/un type (correspondance de data-model.md §2/§4)
et que les contraintes prix > 0, stock >= 0, note 1..5 existent."""
import html
import os
import re
import sys

import pymysql

UML = os.environ.get("T002_UML_DIR", "/opt/data/uml/marketplace-produits-locaux-maroc/02-classes/")
FILES = ["CLASS-01-comptes-catalogue-commandes.drawio", "CLASS-02-retours-argent.drawio"]
SOCK = os.environ["T002_MYSQL_SOCKET"]  # socket d'une instance MySQL de test (aucun mot de passe : root local)

# Correspondance de data-model.md §2 (classes) et §4 (énumérations -> table.colonne avec CHECK).
CLASSES = {
    "ENT-001": "customers", "ENT-002": "sellers", "ENT-003": "shops", "ENT-004": "products",
    "ENT-005": "categories", "ENT-006a": "seller_communes", "ENT-006b": "served_cities", "ENT-007": "carts",
    "ENT-007b": "cart_items", "ENT-008": "orders", "ENT-009": "sub_orders", "ENT-010": "order_lines",
    "ENT-020": "reviews", "ENT-011": "product_returns", "ENT-012": "return_inspections",
    "ENT-013": "return_disputes", "ENT-014": "refunds", "ENT-015": "return_fees", "ENT-016": "seller_amounts",
    "ENT-017": "deductions", "ENT-018": "payouts", "ENT-019": "fund_remittances", "ENT-019b": "cash_discrepancies",
    "ENT-021": "delivery_partners",
}
ENUMS = {
    "EN-SC": [("orders", "status")], "EN-SSC": [("sub_orders", "status")],
    "EN-MR": [("sellers", "payout_method"), ("payouts", "method")], "EN-MR2": [("sellers", "payout_method"), ("payouts", "method")],
    "EN-SR": [("product_returns", "status")], "EN-MOT": [("product_returns", "reason")],
    "EN-SM": [("seller_amounts", "status")],
    "EN-MRB": [("product_returns", "refund_method"), ("refunds", "method")],
    "EN-IF": [("return_fees", "charged_to"), ("return_disputes", "fee_charged_to")],
    "EN-RV": [("return_inspections", "result")],
}
REQUIRED_CHECKS = {
    "prix > 0": ("products", "ck_products_price_positive", "price"),
    "stock >= 0": ("products", "ck_products_stock_non_negative", "stock"),
    "note 1..5": ("reviews", "ck_reviews_rating_range", "rating"),
}

uml_classes, uml_enums, uml_enum_vals = {}, {}, {}
for f in FILES:
    s = open(UML + f, encoding="utf-8").read()
    for m in re.finditer(r'<object id="((?:ENT|EN)-[0-9A-Za-z]+)" label="([^"]*)"', s):
        name = re.sub("<[^>]+>", " ", html.unescape(m.group(2))).replace("«enumeration»", "").strip()
        (uml_enums if m.group(1).startswith("EN-") else uml_classes)[m.group(1)] = name
    for m in re.finditer(r'<object id="(EN-[0-9A-Za-z]+)_attrs" label="([^"]*)"', s):
        uml_enum_vals[m.group(1)] = [v for v in html.unescape(m.group(2)).split("<br>") if v.strip()]

c = pymysql.connect(unix_socket=SOCK, user="root", database="t002_schema")
cur = c.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='t002_schema'")
tables = {r[0] for r in cur.fetchall()}
cur.execute("SELECT tc.table_name, cc.constraint_name, cc.check_clause FROM information_schema.check_constraints cc "
            "JOIN information_schema.table_constraints tc ON tc.constraint_name = cc.constraint_name "
            "AND tc.constraint_schema = cc.constraint_schema WHERE cc.constraint_schema='t002_schema'")
checks = {(t, n): clause for t, n, clause in cur.fetchall()}

missing = 0
print(f"Classes UML lues : {len(uml_classes)} ; énumérations UML lues : {len(uml_enums)} ; tables en base : {len(tables)}")
for cid, name in sorted(uml_classes.items()):
    t = CLASSES.get(cid)
    ok = t in tables
    missing += not ok
    print(f"{'OK ' if ok else 'MANQUE'} {cid:9} {name:28} -> {t}")
for eid, name in sorted(uml_enums.items()):
    targets = ENUMS.get(eid, [])
    found = [f"{t}.{col}" for t, col in targets
             if any(tt == t and col in clause and " in " in clause.lower() for (tt, _), clause in checks.items())]
    ok = bool(targets) and len(found) == len(targets)
    # Nombre de valeurs : UML vs CHECK de la première colonne cible.
    n_uml = len(uml_enum_vals.get(eid, []))
    t0, col0 = targets[0] if targets else (None, None)
    clause0 = next((cl for (tt, _), cl in checks.items() if tt == t0 and f"`{col0}` in" in cl), "")
    n_db = len(re.findall(r"_utf8mb4'([^']*)'", clause0)) or len(re.findall(r"'([^']*)'", clause0))
    ok = ok and n_uml == n_db
    missing += not ok
    print(f"{'OK ' if ok else 'MANQUE'} {eid:9} {name:28} -> CHECK sur {', '.join(found) or '-'} "
          f"(valeurs UML {n_uml} / base {n_db})")
for label, (t, n, col) in REQUIRED_CHECKS.items():
    clause = checks.get((t, n))
    ok = clause is not None and col in clause
    missing += not ok
    print(f"{'OK ' if ok else 'MANQUE'} contrainte {label:10} -> {t}.{n} : {clause}")
print(f"Résultat : {missing} manque(s)")
sys.exit(1 if missing else 0)
