#!/usr/bin/env python3
"""Vérification du contrat d'API T-003 (outil de documentation, pas un test applicatif).

Usage (depuis la racine du dépôt) :
  uv run --no-project --with pyyaml --with openapi-spec-validator --with jsonschema \
      python specs/003-contrat-api/validation/check_contract.py

Contrôles :
  C1  openapi.yaml est un document OpenAPI 3.1 valide (openapi-spec-validator).
  C2  chaque UC-001..UC-023 a au moins un point d'accès (x-uc).
  C3  chaque ligne de la matrice §5 (MP-01..MP-17) et chaque capacité dérivée (MX-*) est couverte
      par au moins une opération, et chaque rôle non « deny » d'une ligne est servi par une opération.
  C4  aucune opération n'ouvre un rôle refusé par ses lignes de matrice (x-roles ⊆ rôles autorisés).
  C5  chaque opération a un exemple de requête (x-request-example), un exemple de succès et au moins
      un exemple d'erreur, chacun rattaché à un code HTTP.
  C6  chaque exemple (requête, succès, erreur) est valide contre son schéma (JSON Schema 2020-12).
  C7  chaque code d'erreur utilisé est au catalogue x-error-codes avec le bon statut HTTP.
  C8  les énumérations des CHECK du schéma T-002 exposées par l'API ont des valeurs identiques.
Sortie : un rapport texte ; code de retour 0 si tout passe, 1 sinon.
"""
from __future__ import annotations

import pathlib
import re
import sys

import yaml
from jsonschema import Draft202012Validator
from openapi_spec_validator import validate

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
OPENAPI = ROOT / "contracts" / "openapi.yaml"
MATRIX = ROOT / "contracts" / "authorization-matrix.yaml"
SQL = REPO / "specs" / "002-schema-donnees" / "contracts" / "schema-reference.mysql.sql"
METHODS = {"get", "post", "put", "patch", "delete"}
ROLES = ["visitor", "customer", "seller", "admin"]

# Énumérations T-002 volontairement non exposées par l'API (détail interne de stockage).
NOT_EXPOSED = {
    frozenset({"original", "mobile"}): "photo_files.variant : variantes internes, l'API expose des URL",
    frozenset({"accepted", "rejected"}): ("photo_files.check_status : un fichier refusé n'est jamais renvoyé, "
                                          "il produit 422 file_rejected (FR-040)"),
}

failures: list[str] = []


def check(name, ok, detail=""):
    print(f"[{'OK' if ok else 'ÉCHEC'}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(name)


doc = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
components = doc["components"]

# C1 -------------------------------------------------------------------------
try:
    validate(doc)
    check("C1 OpenAPI 3.1 valide (openapi-spec-validator)", True, f"openapi={doc['openapi']}")
except Exception as exc:  # noqa: BLE001
    check("C1 OpenAPI 3.1 valide (openapi-spec-validator)", False, str(exc)[:400])

ops = []
for path, item in doc["paths"].items():
    for method, op in item.items():
        if method in METHODS:
            ops.append((method, path, op))
print(f"     {len(ops)} opérations, {len(doc['paths'])} chemins, {len(components['schemas'])} schémas")

# C2 -------------------------------------------------------------------------
uc_ops = {f"UC-{n:03d}": [] for n in range(1, 24)}
for _, _, op in ops:
    for uc in op.get("x-uc", []):
        uc_ops.setdefault(uc, []).append(op["operationId"])
missing_uc = [uc for uc in sorted(uc_ops) if re.fullmatch(r"UC-0(0[1-9]|1\d|2[0-3])", uc) and not uc_ops[uc]]
check("C2 UC-001..UC-023 ont chacun ≥ 1 point d'accès", not missing_uc,
      f"manquants : {missing_uc}" if missing_uc else "23/23")
for uc in sorted(k for k in uc_ops if re.fullmatch(r"UC-0(0[1-9]|1\d|2[0-3])", k)):
    print(f"     {uc}: {len(uc_ops[uc])} op. ({', '.join(uc_ops[uc][:4])}{'…' if len(uc_ops[uc]) > 4 else ''})")

# C3 / C4 --------------------------------------------------------------------
rows = {r["id"]: r for r in matrix["rows"]}
mp_rows = [r for r in rows if r.startswith("MP-")]
op_by_id = {op["operationId"]: op for _, _, op in ops}
uncovered, role_gaps, overreach = [], [], []
for rid, row in rows.items():
    row_ops = [op for op in op_by_id.values() if rid in op.get("x-matrix-rows", [])]
    if not row_ops:
        uncovered.append(rid)
    for role in ROLES:
        if row["roles"][role] != "deny" and not any(role in op["x-roles"] for op in row_ops):
            role_gaps.append(f"{rid}/{role}")
for oid, op in op_by_id.items():
    for role in op["x-roles"]:
        allowed = any(rows[r]["roles"][role] != "deny" for r in op["x-matrix-rows"])
        if not allowed:
            overreach.append(f"{oid}:{role}")
    unknown = [r for r in op["x-matrix-rows"] if r not in rows]
    if unknown:
        overreach.append(f"{oid}: lignes inconnues {unknown}")
check("C3a lignes de la matrice §5 couvertes", not [r for r in uncovered if r.startswith("MP-")],
      f"{len(mp_rows) - len([r for r in uncovered if r.startswith('MP-')])}/{len(mp_rows)} lignes MP")
check("C3b capacités dérivées MX couvertes", not [r for r in uncovered if r.startswith("MX-")],
      f"{len([r for r in rows if r.startswith('MX-')])} lignes MX")
check("C3c chaque rôle autorisé d'une ligne est servi", not role_gaps, ", ".join(role_gaps))
check("C4 aucune opération n'ouvre un rôle refusé", not overreach, ", ".join(overreach))

# C5 / C6 / C7 ---------------------------------------------------------------
def validator_for(schema):
    full = dict(schema)
    full["components"] = components
    return Draft202012Validator(full)


no_req, no_ok, no_err, bad_ex, bad_codes = [], [], [], [], []
n_examples = 0
catalog = doc["x-error-codes"]
for method, path, op in ops:
    oid = op["operationId"]
    rex = op.get("x-request-example")
    if not rex or rex.get("method") != method.upper() or not rex.get("url", "").startswith("/api/v1/"):
        no_req.append(oid)
    rb = op.get("requestBody", {}).get("content", {}).get("application/json")
    if rb:
        for name, ex in rb.get("examples", {}).items():
            n_examples += 1
            errs = list(validator_for(rb["schema"]).iter_errors(ex["value"]))
            if errs:
                bad_ex.append(f"{oid} requête/{name}: {errs[0].message[:120]}")
    succ = [c for c in op["responses"] if c.startswith("2")]
    errc = [c for c in op["responses"] if c[0] in "45"]
    if not succ:
        no_ok.append(oid)
    if not errc:
        no_err.append(oid)
    for code, resp in op["responses"].items():
        content = resp.get("content", {}).get("application/json")
        if code == "204":
            continue
        if not content or not content.get("examples"):
            (no_ok if code.startswith("2") else no_err).append(f"{oid}:{code} sans exemple")
            continue
        v = validator_for(content["schema"])
        for name, ex in content["examples"].items():
            n_examples += 1
            errs = list(v.iter_errors(ex["value"]))
            if errs:
                bad_ex.append(f"{oid} {code}/{name}: {errs[0].message[:120]}")
            if code[0] in "45":
                ecode = ex["value"]["error"]["code"]
                if ecode not in catalog or str(catalog[ecode]["http_status"]) != code:
                    bad_codes.append(f"{oid} {code}:{ecode}")
check("C5a exemple de requête pour chaque opération", not no_req, ", ".join(no_req))
check("C5b exemple de succès (2xx) pour chaque opération", not no_ok, ", ".join(no_ok))
check("C5c exemple d'erreur (4xx/5xx) pour chaque opération", not no_err, ", ".join(no_err))
check("C6 exemples conformes aux schémas", not bad_ex, f"{n_examples} exemples vérifiés" + (
    "; " + " | ".join(bad_ex[:10]) if bad_ex else ""))
check("C7 codes d'erreur au catalogue avec le bon statut HTTP", not bad_codes, ", ".join(bad_codes[:20]))

# C8 -------------------------------------------------------------------------
sql = SQL.read_text(encoding="utf-8")
sql_sets = {}
for m in re.finditer(r"CHECK \((\w+) IN \(([^)]*)\)\)", sql):
    vals = frozenset(re.findall(r"'([^']*)'", m.group(2)))
    sql_sets.setdefault(vals, set()).add(m.group(1))
api_sets = {}


def walk(node, where):
    if isinstance(node, dict):
        if "enum" in node and node.get("type") == "string":
            api_sets.setdefault(frozenset(node["enum"]), set()).add(where)
        for k, v in node.items():
            walk(v, f"{where}.{k}")
    elif isinstance(node, list):
        for k, v in enumerate(node):
            walk(v, f"{where}[{k}]")


walk(components["schemas"], "schemas")
mismatch = []
for vals, cols in sorted(sql_sets.items(), key=lambda x: sorted(x[1])):
    if vals in NOT_EXPOSED:
        print(f"     non exposé : {sorted(cols)} {sorted(vals)} — {NOT_EXPOSED[vals]}")
        continue
    if vals in api_sets:
        print(f"     identique : {sorted(cols)} = {sorted(vals)}")
        continue
    # Ensemble exposé partiellement (superset/sous-ensemble) = divergence à signaler.
    near = [a for a in api_sets if a & vals]
    mismatch.append(f"{sorted(cols)} SQL={sorted(vals)} API≈{[sorted(a) for a in near][:2]}")
check("C8 énumérations T-002 (CHECK IN) identiques dans l'API", not mismatch, " | ".join(mismatch))

print()
print(f"RÉSULTAT : {'SUCCÈS' if not failures else 'ÉCHEC'} — {len(failures)} contrôle(s) en échec")
sys.exit(1 if failures else 0)
