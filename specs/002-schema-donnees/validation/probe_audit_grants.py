"""ADR-015 : vérifie qu'un utilisateur applicatif limité à SELECT, INSERT ne peut ni modifier ni supprimer
une entrée du journal d'audit. Utilisateur jetable sans mot de passe, local à l'instance de test."""
import os

import pymysql

SOCK = os.environ["T002_MYSQL_SOCKET"]  # socket d'une instance MySQL de test
root = pymysql.connect(unix_socket=SOCK, user="root", database="t002_schema", autocommit=True)
r = root.cursor()
r.execute("DROP USER IF EXISTS 't002_app'@'localhost'")
r.execute("CREATE USER 't002_app'@'localhost'")
r.execute("GRANT SELECT, INSERT ON t002_schema.audit_entries TO 't002_app'@'localhost'")

app = pymysql.connect(unix_socket=SOCK, user="t002_app", database="t002_schema", autocommit=True)
a = app.cursor()
a.execute("INSERT INTO audit_entries (occurred_at, actor_system, action_type, target_type, target_id) "
          "VALUES (NOW(3), 'release_seller_amounts', 'scheduled_task_run', 'scheduled_task', 1)")
print("INSERT par l'utilisateur applicatif : accepté")
for label, st in [("UPDATE", "UPDATE audit_entries SET reason = 'x'"), ("DELETE", "DELETE FROM audit_entries")]:
    try:
        a.execute(st)
        print(f"ÉCHEC : {label} accepté à tort")
    except pymysql.err.MySQLError as e:
        print(f"OK {label} refusé [{e.args[0]}]")
r.execute("DROP USER 't002_app'@'localhost'")
