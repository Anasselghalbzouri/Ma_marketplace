# Validation du schéma de référence T-002

Outils de vérification du DDL `../contracts/schema-reference.mysql.sql`. Ce ne sont **pas** des tests applicatifs
ni des migrations. Ils exigent une instance MySQL ≥ 8.0.16 **de test**, joignable par socket Unix en `root` local
sans mot de passe (instance jetable) — ne jamais les lancer sur une base réelle : `reset.sql` supprime la base
`t002_schema`.

```bash
export T002_MYSQL_SOCKET=/chemin/vers/mysql.sock          # instance de test uniquement
python run_sql.py reset.sql ../contracts/schema-reference.mysql.sql   # crée t002_schema puis le schéma
python coverage.py             # classes/énumérations UML -> tables/CHECK ; contraintes prix, stock, note
python probe_constraints.py    # 23 violations attendues refusées
python probe_audit_grants.py   # journal d'audit : INSERT oui, UPDATE/DELETE non (ADR-015)
```

Dépendance Python : `pymysql`. Résultats du 2026-10-14 (MySQL 8.4.6) : voir `../data-model.md` §9.
