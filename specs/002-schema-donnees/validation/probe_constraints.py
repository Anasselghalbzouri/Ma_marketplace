"""Sonde des contraintes du schéma T-002 sur MySQL jetable (base t002_schema déjà créée).
Insère un jeu minimal valide, puis tente des violations ; chaque violation doit être refusée."""
import os

import pymysql

SOCK = os.environ["T002_MYSQL_SOCKET"]  # socket d'une instance MySQL de test
c = pymysql.connect(unix_socket=SOCK, user="root", database="t002_schema", autocommit=True)
cur = c.cursor()

VALID = [
    "INSERT INTO users (id, phone, password, role) VALUES (1,'+212600000001','h','customer'),(2,'+212600000002','h','seller'),(3,'+212600000003','h','admin')",
    "INSERT INTO served_cities (id, name) VALUES (1,'Tanger')",
    "INSERT INTO seller_communes (id, name) VALUES (1,'Tanger')",
    "INSERT INTO categories (id, name) VALUES (1,'Artisanat')",
    "INSERT INTO customers (id, user_id, name) VALUES (1,1,'Client')",
    "INSERT INTO sellers (id, user_id, legal_name, seller_commune_id, payout_method) VALUES (1,2,'Coop',1,'cash')",
    "INSERT INTO shops (id, seller_id, name, pickup_address) VALUES (1,1,'Boutique','Adresse')",
    "INSERT INTO products (id, shop_id, category_id, name, description, price, stock, is_published) VALUES (1,1,1,'Argan','Huile',120.00,3,TRUE)",
    "INSERT INTO orders (id, reference, customer_id, served_city_id, delivery_address, phone, delivery_fee, created_at) VALUES (1,'C-0001',1,1,'Adr','+212600000001',20.00,NOW())",
    "INSERT INTO sub_orders (id, order_id, seller_id, response_deadline_at) VALUES (1,1,1,NOW())",
    "INSERT INTO order_lines (id, sub_order_id, product_id, product_name, quantity, unit_price, is_return_excluded) VALUES (1,1,1,'Argan',1,120.00,FALSE)",
    "INSERT INTO reviews (customer_id, order_line_id, product_id, rating) VALUES (1,1,1,5)",
    "INSERT INTO seller_amounts (order_line_id, seller_id, amount, hold_until) VALUES (1,1,120.00,NOW())",
    "INSERT INTO product_returns (id, order_line_id, quantity, reason, refund_method, refund_details, requested_at) VALUES (1,1,1,'change_of_mind','bank_transfer','enc',NOW())",
    "INSERT INTO audit_entries (occurred_at, actor_user_id, action_type, target_type, target_id, amount, reason) VALUES (NOW(3),3,'cash_collected','order',1,140.00,'saisie')",
]

INVALID = {
    "prix = 0 refusé (prix > 0)": "INSERT INTO products (shop_id, category_id, name, description, price, stock) VALUES (1,1,'X','d',0,1)",
    "prix < 0 refusé (prix > 0)": "INSERT INTO products (shop_id, category_id, name, description, price, stock) VALUES (1,1,'X','d',-5,1)",
    "stock < 0 refusé (stock >= 0)": "INSERT INTO products (shop_id, category_id, name, description, price, stock) VALUES (1,1,'X','d',10,-1)",
    "décrément de stock sous 0 refusé": "UPDATE products SET stock = stock - 4 WHERE id = 1",
    "prix figé unit_price = 0 refusé": "INSERT INTO order_lines (sub_order_id, product_id, product_name, quantity, unit_price, is_return_excluded) VALUES (1,1,'A',1,0,FALSE)",
    "note 0 refusée (1..5)": "UPDATE reviews SET rating = 0 WHERE order_line_id = 1",
    "note 6 refusée (1..5)": "UPDATE reviews SET rating = 6 WHERE order_line_id = 1",
    "2e avis même produit/commande refusé (RG-011)": "INSERT INTO reviews (customer_id, order_line_id, product_id, rating) VALUES (1,1,1,4)",
    "avis sur produit ≠ ligne refusé (FK composite)": "INSERT INTO products (id, shop_id, category_id, name, description, price, stock) VALUES (2,1,1,'B','d',5,1)",
    "quantité panier 0 refusée": "INSERT INTO carts (id, customer_id) VALUES (1,1)",
    "statut commande hors énumération refusé": "UPDATE orders SET status = 'shipped' WHERE id = 1",
    "livrée et payée sans montant/date refusée (CA-F010-1)": "UPDATE orders SET status = 'delivered_paid' WHERE id = 1",
    "échec sans motif refusé (CA-F010-3)": "UPDATE orders SET status = 'delivery_failed' WHERE id = 1",
    "refus sous-commande sans motif refusé": "UPDATE sub_orders SET status = 'refused' WHERE id = 1",
    "2e sous-commande même vendeur refusée (RG-003)": "INSERT INTO sub_orders (order_id, seller_id, response_deadline_at) VALUES (1,1,NOW())",
    "virement sans coordonnées bancaires refusé (CA-F002-2)": "UPDATE sellers SET payout_method = 'bank_transfer' WHERE id = 1",
    "2e boutique pour un vendeur refusée (H-06)": "INSERT INTO shops (seller_id, name, pickup_address) VALUES (1,'B2','A')",
    "motif de retour hors énumération refusé": "UPDATE product_returns SET reason = 'other' WHERE id = 1",
    "remboursement en espèces refusé (RG-022)": "UPDATE product_returns SET refund_method = 'cash' WHERE id = 1",
    "montant vendeur Reversé sans reversement refusé": "UPDATE seller_amounts SET status = 'paid_out' WHERE order_line_id = 1",
    "reversement espèces sans preuve refusé": "INSERT INTO payouts (seller_id, period_start, paid_on, amount, method, recorded_by_user_id) VALUES (1,'2026-10-12','2026-10-14',10,'cash',3)",
    "audit financier sans montant refusé (ENF-008)": "INSERT INTO audit_entries (occurred_at, actor_user_id, action_type, target_type, target_id, reason) VALUES (NOW(3),3,'refund_recorded','product_return',1,'x')",
    "rôle inconnu refusé": "INSERT INTO users (phone, password, role) VALUES ('+212600000009','h','courier')",
}

for st in VALID:
    cur.execute(st)
print(f"Jeu valide : {len(VALID)} insertions acceptées")

# Préparation de deux cas qui exigent un état initial.
special = {
    "avis sur produit ≠ ligne refusé (FK composite)": "INSERT INTO reviews (customer_id, order_line_id, product_id, rating) VALUES (1,2,1,4)",
    "quantité panier 0 refusée": "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (1,1,0)",
}
ok = ko = 0
for label, st in INVALID.items():
    if label in special:
        cur.execute(st)          # préparation (doit réussir)
        if "FK composite" in label:
            cur.execute("INSERT INTO order_lines (id, sub_order_id, product_id, product_name, quantity, unit_price, is_return_excluded) VALUES (2,1,2,'B',1,5,FALSE)")
        st = special[label]
    try:
        cur.execute(st)
        print(f"ÉCHEC (accepté à tort) : {label}")
        ko += 1
    except pymysql.err.MySQLError as e:
        print(f"OK refusé [{e.args[0]}] : {label}")
        ok += 1
print(f"Violations refusées : {ok}/{len(INVALID)} ; acceptées à tort : {ko}")
