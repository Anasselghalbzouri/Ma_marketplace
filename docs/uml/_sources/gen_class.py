"""CLASS-01 / CLASS-02 — domain class diagrams (CDC v1.1 §5, §7, §10, §11, glossaire; Stage A §5)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from umlkit import *

OUT = os.path.join(os.path.dirname(__file__), "..", "02-classes")
LEG = ["Classe bleue = entité CONFIRMÉE ; bordure pointillée + [I] = HYPOTHÈSE / inférence",
       "Classe grise «réf.» = définie dans l'autre diagramme de classes ; «externe» = hors Plateforme",
       "Seuls les attributs cités par le CDC sont portés ; aucune opération (décision Stage A §5)",
       "[0..1] = optionnel ; / = dérivé ; [U Qxx] = valeur MANQUANTE ; note rouge = WARN",
       "Lien pointillé + [I] = association inférée ; losange plein = composition"]


def off(side_xy):
    """Label offset just outside the class box, from the exit/entry side."""
    x, y = side_xy
    if x == 1:
        return (18, -12)
    if x == 0:
        return (-18, -12)
    if y == 1:
        return (14, 14)
    return (14, -14)


def rel(d, cid, a, b, ma, mb, kind="assoc", label="", ex=None, en=None, points=None, req=None, statut="E"):
    style = {"assoc": LINK, "compo": COMPO, "gen": INHERIT}[kind]
    style += f"exitX={ex[0]};exitY={ex[1]};exitDx=0;exitDy=0;entryX={en[0]};entryY={en[1]};entryDx=0;entryDy=0;"
    if statut == "I":
        style += "dashed=1;"
    mid = (label + (" [I]" if statut == "I" else "")) if label else ("[I]" if statut == "I" else None)
    d.e(cid, a, b, "", style, points=points, req=req, statut=statut, src_lbl=ma, tgt_lbl=mb, mid_lbl=mid,
        src_off=off(ex), tgt_off=off(en))


def ey(top, h, y):            # relative Y on a box for an absolute y
    return round((y - top) / h, 3)


def hcls(n):                  # class height for n attribute lines (matches umlkit.cls)
    return 40 + max(1, n) * 16 + 10


W = 260
C = [40, 420, 800, 1180, 1560]

# =================================================================== CLASS-01
d = Diagram("CLASS-01", "CLASS-01 Comptes, catalogue, commandes")
d.title("CLASS-01 — Domaine : comptes, catalogue, panier, commandes, zones, avis",
        "Source : CDC v1.1 §5, §7, F001-F010, F012, F013, RG-001/003/006/007/009/011/014/015/019/023/028 · D37, D40, D41")
d.cls("ENT-005", "Catégorie", ["nom", "exclueDuRetour : booléen (D40, RG-019)"], C[1], 90, W, req="F003, F013, RG-019, D40")
prod = ["nom", "description", "photos [1..*] [I]", "prix : MAD {> 0} [I]", "stock : entier ≥ 0", "origine [I]",
        "périssable : booléen", "personnalisé : booléen", "publié : booléen", "masqué : booléen (RG-015)",
        "/noteMoyenne"]
d.cls("ENT-004", "Produit", prod, C[1], 260, W, req="F003, F005, RG-006, RG-007, RG-015, RG-019")
d.cls("ENT-003", "Boutique", ["nom", "présentation", "adresseCollecte"], C[2], 260, W, req="F002")
vend = ["identitéRaisonSociale", "téléphone", "modeReversement : ModeReversement",
        "coordonnéesBancaires [0..1] {si virement}", "statut : actif | suspendu (RG-015)", "autres informations [U Q22]"]
d.cls("ENT-002", "Vendeur", vend, C[3], 260, W, req="F002, RG-015, RG-018, CA-F002-2")
d.cls("ENT-006a", "CommuneVendeur", ["nom", "{liste fixée par l'admin, RG-023 ; Q41}"], C[4], 260, W,
      req="RG-023, D33, F013")
d.cls("ENT-007b", "LignePanier", ["quantité {≤ stock, CA-F006-2}"], C[0], 300, W, req="F006")
d.cls("ENT-007", "Panier", ["/sous-total par vendeur", "/total des produits"], C[0], 480, W, req="F006, CA-F006-1")
d.cls("ENT-010", "LigneCommande", ["quantité", "prixUnitaire : MAD {figé, RG-007}"], C[1], 620, W,
      req="F007, RG-007", statut="I")
d.cls("ENT-009", "SousCommande", ["statut : StatutSousCommande", "motifRefus [0..1]"], C[2], 620, W,
      req="F009, RG-003", statut="I")
cmd = ["statut : StatutCommande", "adresseLivraison {à Tanger}", "téléphone", "noteLivraison [0..1]",
       "fraisLivraison : MAD [U Q27]", "/total (RG-009)", "modePaiement = à la livraison (RG-002)",
       "montantEncaissé [0..1]", "dateRéception [0..1]", "motifÉchec [0..1]"]
d.cls("ENT-008", "Commande", cmd, C[2], 800, W,
      req="F007, F008, F010, RG-001, RG-002, RG-009, RG-013, CA-F010-1/3")
d.cls("ENT-006b", "VilleDesservie", ["nom (V1 : Tanger)"], C[3], 880, W, req="RG-001, F013")
d.cls("ENT-001", "Client", ["nom", "téléphone {obligatoire, RG-014 [I]}", "e-mail [U]"], C[0], 900, W,
      req="F001, RG-014, RG-028")
d.cls("ENT-020", "Avis", ["note : 1..5 [I]", "commentaire", "masqué : booléen (RG-015)"], C[1], 900, W,
      req="F012, RG-011, RG-015, CA-F013-3")
d.cls("EN-SC", "StatutCommande", ["EnAttenteAcceptation", "Confirmée", "EnCollecte", "EnLivraison", "LivréeEtPayée",
                                  "ÉchecDeLivraison", "Annulée"], C[4], 480, 230, style=ENUM, stereo="enumeration",
      req="§7 (étapes HYPOTHÈSE, « En collecte » D44)")
d.cls("EN-SSC", "StatutSousCommande", ["Nouvelle", "Acceptée", "PrêtePourCollecte", "Collectée", "Refusée",
                                       "Annulée"], C[4], 680, 230, style=ENUM, stereo="enumeration", req="§7 [I]")
d.cls("EN-MR", "ModeReversement", ["Virement", "Espèces"], C[4], 880, 230, style=ENUM, stereo="enumeration",
      req="D21, RG-018")

hP, hB, hV, hCo = hcls(len(prod)), hcls(3), hcls(len(vend)), hcls(2)
rel(d, "r_cat", "ENT-004", "ENT-005", "0..*", "1", ex=(0.5, 0), en=(0.5, 1), req="F003")
rel(d, "r_bout", "ENT-003", "ENT-004", "1", "0..*", label="publie", ex=(0, ey(260, hB, 310)), en=(1, ey(260, hP, 310)),
    req="F002, F003")
rel(d, "r_vb", "ENT-002", "ENT-003", "1", "1", ex=(0, ey(260, hV, 310)), en=(1, ey(260, hB, 310)),
    req="F002 (1 boutique par vendeur)", statut="I")
rel(d, "r_vc", "ENT-002", "ENT-006a", "0..*", "1", label="situé dans", ex=(1, ey(260, hV, 310)),
    en=(0, ey(260, hCo, 310)), req="RG-023, D33")
rel(d, "r_pl", "ENT-007", "ENT-007b", "1", "0..*", kind="compo", ex=(0.5, 0), en=(0.5, 1), req="F006")
rel(d, "r_lpp", "ENT-007b", "ENT-004", "0..*", "1", ex=(1, 0.5), en=(0, ey(260, hP, 333)), req="F006")
rel(d, "r_cp", "ENT-001", "ENT-007", "1", "0..1", ex=(0.5, 0), en=(0.5, 1), req="F006 ; panier du Visiteur [I]",
    statut="I")
rel(d, "r_lcp", "ENT-010", "ENT-004", "0..*", "1", ex=(0.5, 0), en=(0.5, 1), req="F007")
rel(d, "r_sclc", "ENT-009", "ENT-010", "1", "1..*", kind="compo", ex=(0, 0.5), en=(1, 0.5), req="RG-003")
rel(d, "r_csc", "ENT-008", "ENT-009", "1", "1..*", kind="compo", label="une par vendeur", ex=(0.5, 0), en=(0.5, 1),
    req="RG-003", statut="I")
rel(d, "r_scv", "ENT-009", "ENT-002", "0..*", "1", ex=(1, 0.5), en=(0.5, 1), points=[(C[3] + 130, 661)],
    req="RG-003, CA-F009-1")
rel(d, "r_cc", "ENT-001", "ENT-008", "1", "0..*", label="passe", ex=(0.5, 1), en=(0.5, 1),
    points=[(170, 1070), (930, 1070)], req="F007, RG-028")
rel(d, "r_cv", "ENT-008", "ENT-006b", "0..*", "1", label="livrée dans", ex=(1, ey(800, hcls(len(cmd)), 913)),
    en=(0, 0.5), req="RG-001")
rel(d, "r_ac", "ENT-020", "ENT-001", "0..*", "1", label="rédige", ex=(0, 0.5), en=(1, 0.5), req="F012")
rel(d, "r_al", "ENT-020", "ENT-010", "0..*", "1", label="porte sur", ex=(0.5, 0), en=(0.5, 1), req="RG-011, D37")

d.note("n_rg006", "<b>{RG-006 [I]}</b> Produit visible et commandable ⇔ publié ∧ ¬masqué ∧ stock > 0 ∧ vendeur actif.<br>"
       "<b>{RG-019, D40}</b> exclu du retour ⇔ périssable ∨ personnalisé ∨ catégorie.exclueDuRetour.",
       C[2], 90, 400, 80, attach=["ENT-004"])
d.note("n_rg011", "<b>{RG-011, D37}</b> un Avis n'existe que si la Commande de la LigneCommande est « LivréeEtPayée » ; "
       "un avis par produit et par commande [I] (2ᵉ avis = modification). Avis masqué ⇒ /noteMoyenne recalculée "
       "(CA-F013-3).", C[0], 1110, 340, 90, attach=["ENT-020"])
d.note("n_rg008", "<b>{RG-008, D22}</b> pas de livraison partielle : Commande livrée seulement si toutes ses "
       "SousCommandes sont acceptées et collectées ; un refus ⇒ Commande et toutes SousCommandes Annulées.<br>"
       "<b>{RG-017 [I]}</b> stock réservé à la validation, restitué si annulation / refus / échec.",
       C[2], 1110, 420, 104, attach=["ENT-008"])
d.note("n_warn", "<b>WARN</b> : un Visiteur sans compte peut tenir un panier (HYPOTHÈSE §5) ; rattachement "
       "Panier ↔ Client après connexion (CA-F001-3). Données vendeur exigées : MANQUANT (Q22). "
       "Une boutique par vendeur : inféré (F002).", C[3] + 100, 1110, 360, 90, warn=True)
d.legend(C[3] + 100, 1220, LEG, w=520)
d.write(os.path.join(OUT, "CLASS-01-comptes-catalogue-commandes.drawio"))

# =================================================================== CLASS-02
d = Diagram("CLASS-02", "CLASS-02 Retours et argent")
d.title("CLASS-02 — Domaine : retours, litiges, remboursements, montants vendeurs, reversements, remises de fonds",
        "Source : CDC v1.1 §7, F010, F011, F022, RG-012/017/018/020/021/022/024/025/027/030, ENF-008, ENF-012 · "
        "D29-D32, D34, D39, D42, D43")
d.cls("ENT-021", "SociétéDeLivraison", ["(aucun attribut spécifié — C-05)"], C[0], 90, W, style=EXT_CLASS,
      stereo="externe", req="D19, D38, C-05")
d.cls("ENT-019", "RemiseDeFonds", ["montant : MAD", "date"], C[1], 90, W, req="RG-020, ENF-008", statut="I")
d.cls("REF-008", "Commande", ["(voir CLASS-01)"], C[2], 90, W, style=EXT_CLASS, stereo="réf.")
d.cls("ENT-019b", "Écart", ["montant : MAD", "date"], C[3], 90, W, req="CA-F010-2, RG-020, ENF-008", statut="I")
d.cls("REF-002", "Vendeur", ["(voir CLASS-01)"], C[4], 90, W, style=EXT_CLASS, stereo="réf.")
d.cls("REF-010", "LigneCommande", ["(voir CLASS-01)"], C[2], 320, W, style=EXT_CLASS, stereo="réf.")
mv = ["montant : MAD", "statut : StatutMontant", "/dateDisponibilité = dateRéception + 7 j"]
d.cls("ENT-016", "MontantVendeur", mv, C[3], 320, W,
      req="F011, RG-012, RG-024, CA-F010-1, CA-F011-1", statut="I")
rev = ["date", "montant : MAD", "mode : ModeReversement", "preuveRemise [0..1] {si espèces} [I]"]
d.cls("ENT-018", "Reversement", rev, C[4], 320, W, req="F011, RG-018, CA-F011-2, CA-F011-5")
ret = ["quantité", "motif : MotifRetour", "photo [0..1] [I]", "moyenRemboursement : MoyenRemboursement",
       "coordonnéesRemboursement", "dateDemande", "statut : StatutRetour", "/procheDélaiLégal (ENF-012 [I])"]
d.cls("ENT-011", "Retour", ret, C[2], 540, W, req="F022, RG-019, RG-022, RG-030, CA-F022-1/4/7/9")
d.cls("ENT-017", "Déduction", ["montant : MAD", "origine : remboursement | fraisDeRetour", "date"], C[3], 600, W,
      req="RG-021, RG-025, CA-F011-3/4/5")
d.cls("ENT-015", "FraisDeRetour", ["montant : MAD [U Q45]", "imputéÀ : ImputationFrais"], C[0], 820, W,
      req="RG-025, D42")
d.cls("ENT-012", "Vérification", ["résultat : RésultatVérification", "motifContestation [0..1]",
                                  "remiseEnVente : booléen (D43)", "date"], C[1], 820, W,
      req="RG-027, RG-017, D31, D43, US-014")
d.cls("ENT-013", "Litige", ["décision", "montantRemboursé : MAD", "imputationFrais : ImputationFrais", "date"],
      C[2], 820, W, req="RG-027, CA-F022-6, US-015")
d.cls("ENT-014", "Remboursement", ["montant : MAD", "moyen : MoyenRemboursement", "référence", "date"], C[3], 820, W,
      req="RG-022, CA-F022-5, ENF-008, ENF-012")
EY = 1100
enums = [("EN-SR", "StatutRetour", ["Demandé", "EnReprise", "Repris", "VérifiéParLeVendeur", "Contesté", "Litige",
                                     "ClientRemboursé", "RetourRefusé"], 210, "§7 (étapes HYPOTHÈSE)"),
         ("EN-MOT", "MotifRetour", ["ChangementDAvis", "Défectueux", "Incorrect", "NonConforme"], 200, "F022, D30"),
         ("EN-SM", "StatutMontant", ["Retenu", "Disponible", "Reversé", "Déduit"], 180, "§7, D29, D34"),
         ("EN-MRB", "MoyenRemboursement", ["VirementBancaire", "AutreMoyenTraçable [U Q42]"], 240, "RG-022, D32"),
         ("EN-IF", "ImputationFrais", ["Client", "Vendeur"], 180, "RG-025"),
         ("EN-RV", "RésultatVérification", ["Conforme", "Contesté"], 200, "RG-027"),
         ("EN-MR2", "ModeReversement", ["Virement", "Espèces"], 190, "D21, RG-018")]
x = C[0]
for cid, name, vals, w, req in enums:
    d.cls(cid, name, vals, x, EY, w, style=ENUM, stereo="enumeration", req=req)
    x += w + 40

hR, hMV, hRev, hRet = hcls(2), hcls(len(mv)), hcls(len(rev)), hcls(len(ret))
rel(d, "r_sr", "ENT-021", "ENT-019", "1", "0..*", label="remet", ex=(1, 0.5), en=(0, ey(90, hR, 123)),
    req="RG-020", statut="I")
rel(d, "r_rc", "ENT-019", "REF-008", "0..*", "1..*", label="rapprochée de", ex=(1, ey(90, hR, 123)), en=(0, 0.5),
    req="RG-020", statut="I")
rel(d, "r_ce", "REF-008", "ENT-019b", "1", "0..1", ex=(1, 0.5), en=(0, ey(90, hR, 123)), req="CA-F010-2", statut="I")
rel(d, "r_vr", "REF-002", "ENT-018", "1", "0..*", label="reçoit", ex=(0.5, 1), en=(0.5, 0), req="F011, RG-018")
rel(d, "r_lm", "REF-010", "ENT-016", "1", "0..1", ex=(1, 0.5), en=(0, ey(320, hMV, 353)),
    req="RG-024 (retenue par produit)", statut="I")
rel(d, "r_mr", "ENT-016", "ENT-018", "0..*", "0..1", label="inclus dans", ex=(1, ey(320, hMV, 353)),
    en=(0, ey(320, hRev, 353)), req="RG-018, CA-F011-2")
rel(d, "r_lr", "REF-010", "ENT-011", "1", "0..*", label="un retour par produit", ex=(0.5, 1), en=(0.5, 0),
    req="RG-030, D39")
rel(d, "r_rd", "ENT-011", "ENT-017", "1", "0..*", label="donne lieu à", ex=(1, ey(540, hRet, 649)), en=(0, 0.5),
    req="RG-021, RG-025")
rel(d, "r_dr", "ENT-017", "ENT-018", "0..*", "0..1", label="régularisée sur", ex=(1, 0.5), en=(0.5, 1),
    points=[(C[4] + 130, 649)], req="RG-021, CA-F011-4/5")
rel(d, "r_rf", "ENT-011", "ENT-015", "1", "0..1", ex=(0, ey(540, hRet, 690)), en=(0.5, 0), points=[(170, 690)],
    req="RG-025, D42")
rel(d, "r_rv", "ENT-011", "ENT-012", "1", "0..1", kind="compo", ex=(0.25, 1), en=(0.5, 0),
    points=[(865, 780), (550, 780)], req="RG-027, D31")
rel(d, "r_rl", "ENT-011", "ENT-013", "1", "0..1", kind="compo", ex=(0.5, 1), en=(0.5, 0), req="RG-027, CA-F022-6")
rel(d, "r_rb", "ENT-011", "ENT-014", "1", "0..1", kind="compo", ex=(0.75, 1), en=(0.5, 0),
    points=[(995, 780), (1310, 780)], req="RG-022, CA-F022-5")

d.note("n_ret", "<b>{RG-019}</b> Retour possible seulement si dateDemande ≤ Commande.dateRéception + 7 j et produit "
       "non exclu.<br><b>{RG-027 [I]}</b> décision du Litige finale.<br><b>{RG-017, D43}</b> stock restitué "
       "seulement si Vérification.remiseEnVente.", C[0], 540, 340, 110, attach=["ENT-011"])
d.note("n_mv", "<b>{RG-024}</b> Retenu jusqu'à dateRéception + 7 j ; reste Retenu si un Retour est en cours sur la "
       "ligne [I].<br><b>{RG-018, CA-F011-5}</b> Reversement.montant = Σ Disponibles − Σ Déductions non encore "
       "imputées.", C[3], 195, 330, 100, attach=["ENT-016"])
d.note("n_rem", "<b>{RG-022, D42}</b> Remboursement.montant = prix du produit retourné − frais de retour si "
       "motif = ChangementDAvis ; jamais en espèces non traçables. Délai légal 15 j (R1, à confirmer) ; "
       "frais de livraison initiaux remboursés ? [U Q40]", C[4], 800, 300, 120, warn=True, attach=["ENT-014"])
d.note("n_warn2", "<b>WARN</b> : multiplicité LigneCommande–Retour 0..* [I] (retours partiels successifs ?) ; "
       "solde vendeur négatif : report signalé [I] (Q38) ; Écart et RemiseDeFonds = HYPOTHÈSE (RG-020).",
       C[4], 940, 300, 100, warn=True)
d.legend(C[0], 1320, LEG, w=520)
d.write(os.path.join(OUT, "CLASS-02-retours-argent.drawio"))
print("ok class")
