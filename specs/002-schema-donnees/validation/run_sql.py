"""Exécute un fichier SQL sur une instance MySQL de test (validation du DDL de référence de T-002).
Usage : T002_MYSQL_SOCKET=/chemin/mysql.sock python run_sql.py fichier.sql [fichier2.sql ...]
        (dépendance : pymysql ; ex. uv venv venv && uv pip install --python venv/bin/python pymysql)
"""
import os
import sys

import pymysql

SOCK = os.environ["T002_MYSQL_SOCKET"]  # socket d'une instance MySQL de test


def split_sql(text):
    out, buf = [], []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("--") or not s:
            continue
        buf.append(line)
        if s.endswith(";"):
            out.append("\n".join(buf).rstrip().rstrip(";"))
            buf = []
    if buf:
        out.append("\n".join(buf))
    return out


def main():
    conn = pymysql.connect(unix_socket=SOCK, user="root", autocommit=True, charset="utf8mb4")
    cur = conn.cursor()
    args = sys.argv[1:]
    if args and args[0] == "--query":
        for q in args[1:]:
            cur.execute(q)
            for row in cur.fetchall():
                print("\t".join("" if v is None else str(v) for v in row))
        return
    for path in args:
        stmts = split_sql(open(path, encoding="utf-8").read())
        ok = 0
        for st in stmts:
            try:
                cur.execute(st)
                if cur.description:
                    for row in cur.fetchall():
                        print("\t".join("" if v is None else str(v) for v in row))
                ok += 1
            except Exception as e:  # report and stop
                print(f"ERREUR dans {path} (instruction {ok + 1}) : {e}\n--- {st[:300]}")
                sys.exit(1)
        print(f"{path} : {ok} instructions exécutées sans erreur")


if __name__ == "__main__":
    main()
