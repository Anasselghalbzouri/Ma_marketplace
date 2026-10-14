"""Traceability + validation audit: parses every .drawio, runs validate.py, extracts req IDs,
and checks coverage against the IDs defined in the CDC v1.1. Writes _sources/audit.json."""
import glob, json, os, re, subprocess, xml.etree.ElementTree as ET

ROOT = os.path.join(os.path.dirname(__file__), "..")
CDC = "/opt/data/cahiers/marketplace-produits-locaux-maroc/cahier-des-charges-v1.1.md"
VAL = "/opt/data/profiles/blueprint/skills/drawio-skill/scripts/validate.py"
cdc = open(CDC, encoding="utf-8").read()


def expand(text):
    """Expand 'RG-001/003/008', 'CA-F022-1..9', 'CA-F010-1/3', 'RG-012/018' into explicit IDs."""
    ids = set()
    for m in re.finditer(r"\b(RG|ENF|US)-(\d{3}b?)((?:/\d{3}b?)*)", text):
        ids.add(f"{m.group(1)}-{m.group(2)}")
        for n in filter(None, m.group(3).split("/")):
            ids.add(f"{m.group(1)}-{n}")
    for m in re.finditer(r"\bCA-(F\d{3})-(\d+)((?:/\d+)*)(?:\.\.(\d+))?", text):
        f, a = m.group(1), int(m.group(2))
        ids.add(f"CA-{f}-{a}")
        for n in filter(None, m.group(3).split("/")):
            ids.add(f"CA-{f}-{n}")
        if m.group(4):
            for n in range(a, int(m.group(4)) + 1):
                ids.add(f"CA-{f}-{n}")
    for m in re.finditer(r"\bF(\d{3})(?:-F(\d{3}))?\b", text):
        a = int(m.group(1)); b = int(m.group(2) or a)
        for n in range(a, b + 1):
            ids.add(f"F{n:03d}")
    for m in re.finditer(r"\bD(\d{1,2})(?:-D(\d{1,2}))?\b", text):
        a = int(m.group(1)); b = int(m.group(2) or a)
        for n in range(a, b + 1):
            ids.add(f"D{n}")
    return ids


defined = {
    "F": sorted(set(re.findall(r"^F\d{3}(?= —)", cdc, re.M))),
    "RG": sorted(set(re.findall(r"^\| (RG-\d{3}b?) \|", cdc, re.M))),
    "CA": sorted(set(re.findall(r"^\| (CA-F\d{3}-\d+) \|", cdc, re.M))),
    "US": sorted(set(re.findall(r"^(US-\d{3}) —", cdc, re.M))),
    "ENF": sorted(set(re.findall(r"^\| (ENF-\d{3}) \|", cdc, re.M))),
}
MUST = [f"F{n:03d}" for n in list(range(1, 15)) + [22]]
defined["F"] = [f for f in defined["F"] if f in MUST]

files = sorted(glob.glob(os.path.join(ROOT, "0[1-5]-*", "*.drawio")))
per_file, all_ids = {}, {}
for f in files:
    name = os.path.basename(f)[:-7]
    out = subprocess.run(["python3", VAL, f, "--json"], capture_output=True, text=True)
    try:
        v = json.loads(out.stdout)
    except Exception:
        v = {"raw": out.stdout[-500:]}
    tree = ET.parse(f)
    text = []
    n_el = 0
    statut = {"E": 0, "I": 0, "WARN": 0}
    for o in tree.iter("object"):
        n_el += 1
        s = o.get("statut")
        if s in statut:
            statut[s] += 1
        text.append(o.get("req", "") + " " + o.get("label", ""))
    ids = expand(" ".join(text))
    per_file[name] = {"validate_exit": out.returncode, "validate": v, "elements": n_el, "statut": statut,
                      "ids": sorted(ids)}
    for i in ids:
        all_ids.setdefault(i, []).append(name)

coverage = {}
for k, lst in defined.items():
    coverage[k] = {"defined": len(lst), "covered": [i for i in lst if i in all_ids],
                   "missing": [i for i in lst if i not in all_ids]}
json.dump({"files": per_file, "coverage": coverage, "map": all_ids, "defined": defined},
          open(os.path.join(os.path.dirname(__file__), "audit.json"), "w"), ensure_ascii=False, indent=1)
for name, d in per_file.items():
    vv = d["validate"]
    errs = vv.get("errors", "?")
    warns = vv.get("warnings", "?")
    print(f"{name:45s} exit={d['validate_exit']} err={errs} warn={warns} elements={d['elements']} statut={d['statut']}")
for k, c in coverage.items():
    print(f"{k}: {len(c['covered'])}/{c['defined']} missing={c['missing']}")
