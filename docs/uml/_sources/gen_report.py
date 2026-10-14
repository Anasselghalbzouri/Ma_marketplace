"""Builds rapport-tracabilite-validation.md from audit.json (tool output) + fixed review findings."""
import json, os

H = os.path.dirname(__file__)
a = json.load(open(os.path.join(H, "audit.json"), encoding="utf-8"))
F, M = a["files"], a["map"]
short = lambda n: n.split("-")[0] + "-" + n.split("-")[1] if not n.startswith("UC-DIAG") else "-".join(n.split("-")[:3])
DIR = {"UC": "01-cas-utilisation", "CL": "02-classes", "SE": "03-sequences", "AC": "04-activites", "ST": "05-etats"}

L = []
w = L.append
w("# Étape B — Rapport de traçabilité et de validation UML")
w("**Projet** : Marketplace de produits locaux marocains · **Auteur** : Blueprint (UML Architect)  ")
w("**Source** : `cahier-des-charges-v1.1.md` (**Brouillon**, en attente de revalidation par le porteur) + `decisions.md` "
  "(D1–D44) + Stage A `00-etape-A-analyse-et-proposition.md` §10 (décisions b1-a … n7-a).  ")
w("**Réserve** : la v1.0 reste la référence validée tant que le porteur n'a pas revalidé la v1.1. Les écarts v1.0 → v1.1 "
  "proviennent tous de décisions du porteur (D37–D44) ; si la revalidation modifie ces points, les diagrammes concernés "
  "devront être régénérés.\n")
w("Toutes les valeurs PASS/WARN/FAIL ci-dessous proviennent d'une exécution réelle : `validate.py` (drawio-skill v3.4.0), "
  "export PNG draw.io 32.4.1 sans écran (xvfb), inspection visuelle de chaque aperçu, et `_sources/audit.py` "
  "(extraction des ID depuis les propriétés `req` et les libellés des fichiers .drawio).\n")

w("## 1. Livrables\n")
w("| ID | Fichier .drawio (éditable) | Éléments | `validate.py` | Rendu PNG | Inspection visuelle |")
w("|---|---|---|---|---|---|")
for name, d in F.items():
    v = d["validate"]
    e, wn = v.get("errors"), v.get("warnings")
    status = "PASS (0 err, 0 warn)" if e == 0 and wn == 0 else (f"WARN (0 err, {wn} warn)" if e == 0 else f"FAIL ({e} err)")
    folder = DIR[name[:2]]
    w(f"| {short(name)} | `{folder}/{name}.drawio` | {d['elements']} | {status} | PASS | PASS |")
w("\nAperçus de contrôle (brouillons non éditables) : `_previews/*.png`. Générateurs reproductibles : `_sources/*.py` "
  "(régénération explicite avec `BP_REGEN=1`, sinon refus d'écraser un fichier existant).\n")
w("**Avertissements résiduels SEQ-001/002/003 (WARN, accepté)** : `W-OVERLAP` entre une note et la ligne de vie qu'elle "
  "commente (notes posées volontairement sur la ligne de vie, convention UML). Aucun chevauchement de messages, cadres "
  "ou libellés n'a été constaté à l'inspection visuelle.\n")

w("## 2. Couverture des exigences (extraction automatique)\n")
w("| Famille | Définies dans le CDC v1.1 | Couvertes | Manquantes | Statut |")
w("|---|---|---|---|---|")
lab = {"F": "Fonctionnalités MUST", "RG": "Règles métier", "CA": "Critères d'acceptation", "US": "User stories",
       "ENF": "Exigences non fonctionnelles"}
for k, c in a["coverage"].items():
    n = len(c["covered"])
    st = "PASS" if not c["missing"] else ("WARN (hors UML, voir §4)" if k == "ENF" else "FAIL")
    w(f"| {lab[k]} | {c['defined']} | {n} | {', '.join(c['missing']) or '—'} | {st} |")
w("\nLes SHOULD/COULD F015–F021 (toutes SUGGESTION) sont **exclues** par décision Stage A et ne figurent dans aucun diagramme.\n")

w("## 3. Matrice de traçabilité\n")
w("### 3.1 Fonctionnalités → diagrammes\n")
w("| Exigence | Diagrammes |\n|---|---|")
for i in a["defined"]["F"]:
    w(f"| {i} | {', '.join(sorted({short(n) for n in M[i]}))} |")
w("\n### 3.2 Règles métier → diagrammes\n")
w("| Règle | Diagrammes |\n|---|---|")
for i in a["defined"]["RG"]:
    w(f"| {i} | {', '.join(sorted({short(n) for n in M[i]}))} |")
w("\n### 3.3 User stories et critères d'acceptation → diagrammes\n")
w("| ID | Diagrammes |\n|---|---|")
for i in a["defined"]["US"] + a["defined"]["CA"]:
    w(f"| {i} | {', '.join(sorted({short(n) for n in M[i]}))} |")
w("\n### 3.4 Éléments Blueprint → sources\n")
w("| Élément | Diagramme | Source principale |\n|---|---|---|")
rows = [
 ("ACT-001 Visiteur [I]", "UC-DIAG-01", "§5 (navigation sans compte = HYPOTHÈSE)"),
 ("ACT-002 Client", "UC-DIAG-01, SEQ-001/003, ACTIVITY-001/002", "§5, D41"),
 ("ACT-003 Vendeur", "UC-DIAG-02, SEQ, ACTIVITY", "§5, D31, D33, D43"),
 ("ACT-004 Administrateur", "UC-DIAG-03, SEQ-002/003, ACTIVITY", "§5, D31, D37, D38"),
 ("ACT-005 Société de livraison «externe», sans association", "UC-DIAG-03, SEQ-002/003, ACTIVITY-001/002", "D19, D38, RG-029"),
 ("UC-001 … UC-023", "UC-DIAG-01/02/03", "voir propriété `req` de chaque cas"),
 ("ENT-001 … ENT-021 + 10 énumérations", "CLASS-01/02", "Stage A §5 ; attributs du CDC uniquement"),
 ("SEQ-001 / 002 / 003", "03-sequences", "P2/P4 ; P5 ; P3"),
 ("ACTIVITY-001 / 002 / 003", "04-activites", "P2/P4/P5 ; P3 ; F011"),
 ("STATE-001 … 004", "05-etats", "§7 cycles de vie"),
]
for r in rows:
    w(f"| {r[0]} | {r[1]} | {r[2]} |")

w("\n## 4. Exigences non fonctionnelles\n")
w("| ENF | Traitement | Statut |\n|---|---|---|")
enf = [("ENF-001 Langues", "Hors UML (qualité d'interface)", "WARN — hors UML, MANQUANT Q11"),
       ("ENF-002 Mobile", "Hors UML", "WARN — hors UML"),
       ("ENF-003 Simplicité vendeur", "Hors UML", "WARN — hors UML"),
       ("ENF-004 Performance", "Hors UML", "WARN — hors UML"),
       ("ENF-005 Disponibilité", "Hors UML", "WARN — hors UML"),
       ("ENF-006 Volumes", "Hors UML", "WARN — hors UML, MANQUANT Q21"),
       ("ENF-007 Sécurité / cloisonnement", "Notes UC-DIAG-02 et UC-DIAG-03 ; société de livraison sans association", "PASS"),
       ("ENF-008 Traçabilité financière", "Classes RemiseDeFonds, Écart, Déduction, Remboursement, Reversement (CLASS-02)", "PASS"),
       ("ENF-009 Conformité légale", "Confirmation écrite (SEQ-001) ; délais légaux (ACTIVITY-002, STATE-003)", "PASS (validation juridique C-08 hors modèle)"),
       ("ENF-010 Évolutivité", "VilleDesservie, CommuneVendeur paramétrables (CLASS-01) ; UC-021", "PASS"),
       ("ENF-011 Photos", "Hors UML", "WARN — hors UML"),
       ("ENF-012 Délai de remboursement", "Événement temporel ACTIVITY-002, note STATE-003, attribut /procheDélaiLégal", "PASS")]
for r in enf:
    w(f"| {r[0]} | {r[1]} | {r[2]} |")

w("\n## 5. Contrôles de qualité (§8 du rôle Blueprint)\n")
w("| Contrôle | Résultat | Preuve |\n|---|---|---|")
qa = [
 ("Toutes les fonctionnalités MUST considérées", "PASS", "15/15 (audit.json)"),
 ("Acteurs justifiés par la source ou marqués inférés", "PASS", "ACT-001 marqué [I] ; ACT-005 «externe» sans accès (D38)"),
 ("Cas d'utilisation = objectifs réels (pas de boutons)", "PASS", "23 cas ; accepter/refuser regroupés (UC-012)"),
 ("«include»/«extend» justifiés", "PASS", "UC-005 «include» UC-004 (RG-028) ; UC-007 «extend» UC-006 avec condition RG-010"),
 ("Relations de classes justifiées", "PASS / WARN", "compositions Commande→SousCommande→LigneCommande, Retour→Vérif./Litige/Remb. ; 6 associations inférées en pointillé"),
 ("Aucun attribut / opération inventé", "PASS", "attributs issus du CDC ; [I]/[U] signalés ; aucune opération"),
 ("Séquences dans l'ordre chronologique du scénario", "PASS", "P2/P4 (SEQ-001), P5 (SEQ-002), P3 (SEQ-003)"),
 ("Activités conformes aux parcours", "PASS", "couloirs Client/Plateforme/Vendeur/Admin/Société de livraison"),
 ("Transitions d'états appuyées par des règles", "PASS / WARN", "§7 ; transitions [I] signalées (ex. STATE-004 t1b, t4)"),
 ("Décisions du porteur appliquées (B1–B5, N5–N7)", "PASS", "RG-011/015 confirmées ; admin seul (RG-029) ; 1 retour/produit (RG-030) ; exclusion produit ∨ catégorie (RG-019) ; compte obligatoire ; frais déduits ; remise en vente vendeur ; « En collecte » à la transmission"),
 ("Contradictions et manques documentés", "PASS", "notes WARN dans 13 diagrammes (SEQ-001 et SEQ-003 : réserves en notes jaunes) ; §6 ci-dessous"),
 ("Fichiers éditables", "PASS", "XML draw.io non compressé ; ouverts et rendus par draw.io 32.4.1"),
 ("Aucun diagramme écrasé silencieusement", "PASS", "dossiers créés vides ; seuls les fichiers de cette génération ont été régénérés (BP_REGEN=1)"),
 ("Validation structurelle", "PASS / WARN", "0 erreur sur 15 fichiers ; 10 avertissements note/ligne de vie (SEQ)"),
 ("Inspection visuelle", "PASS", "15 aperçus PNG inspectés ; défauts corrigés en 1 à 2 itérations"),
]
for r in qa:
    w(f"| {r[0]} | {r[1]} | {r[2]} |")

w("\n## 6. Hypothèses, limites et questions ouvertes portées par les diagrammes\n")
for t in [
 "**Version de référence** : modèles fondés sur la v1.1 Brouillon (voir réserve en tête).",
 "**Délais non chiffrés**, modélisés comme événements paramétrés : réponse vendeur (Q19), vérification du retour (Q44), jour du reversement, délai légal de 15 j (R1, à valider C-08).",
 "**Q24** : suite d'un échec de livraison non définie → état final provisoire dans STATE-001.",
 "**Q38** : solde vendeur négatif → report signalé, HYPOTHÈSE (ACTIVITY-003).",
 "**Q40 / Q42 / Q43 / Q45 / Q27** : montants et moyens portés comme attributs sans valeur.",
 "**Q44 au-delà du délai** : décision de l'administrateur [I], transition non dessinée dans STATE-003 faute de cible définie.",
 "**Cycles de vie §7** : HYPOTHÈSE, sauf « En collecte » (D44) et le cycle Montant vendeur (D29, D34).",
 "**Inférences Blueprint** (pointillés [I]) : une boutique par vendeur ; MontantVendeur porté par LigneCommande ; RemiseDeFonds/Écart ; Client spécialise Visiteur ; Panier 0..1 par client.",
 "**N8 / Q39** (identité du « fournisseur », loi 31-08) et **N9** (en-cours d'un vendeur suspendu) : notes, sans effet structurel.",
 "**Non produits, conformément à la proposition** : diagrammes de composants et de déploiement (C-07).",
]:
    w(f"- {t}")

w("\n## 7. Environnement et méthode\n")
w("- Génération : `_sources/umlkit.py` (styles UML de `drawio-skill/references/diagram-types.md`) + un script par famille. "
  "Chaque élément porte les propriétés `req` (ID sources) et `statut` (E / I / WARN), consultables dans draw.io via *Édition > Modifier les données*.")
w("- Validation : `python3 drawio-skill/scripts/validate.py <fichier> --score` (aussi en `--json` dans `_sources/audit.json`).")
w("- Rendu : `xvfb-run -a drawio -x -f png … --disable-gpu --no-sandbox --disable-dev-shm-usage`. Sans "
  "`--disable-dev-shm-usage`, le moteur de rendu plante sur les grandes pages (/dev/shm = 64 Mo).")
w("- La matrice §3 est extraite automatiquement des propriétés `req` et des libellés ; elle indique où un ID est référencé, et non une preuve sémantique en soi. Les vérifications sémantiques figurent au §5.")

open(os.path.join(H, "..", "rapport-tracabilite-validation.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("ok report", len(L))
