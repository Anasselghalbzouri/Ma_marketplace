"""UC-DIAG-01..03 — use case diagrams (source: CDC v1.1 §5, §10, decisions D37-D44)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from umlkit import *

OUT = os.path.join(os.path.dirname(__file__), "..", "01-cas-utilisation")
LEG = ["Ellipse pleine = cas CONFIRMÉ [E] ; pointillés = HYPOTHÈSE du CDC [I]",
       "Note rouge = point non résolu (WARN) ; note jaune = règle / précision",
       "Propriétés « req » / « statut » de chaque élément : Édition > Données"]


def uc(d, cid, label, x, y, req, statut="E", w=240, h=64):
    st = USECASE + (INFERRED if statut == "I" else "")
    return d.v(cid, f"<b>{cid}</b><br>{label}" + (" <i>[I]</i>" if statut == "I" else ""),
               x, y, w, h, st, parent="sys", req=req, statut=statut)


# ------------------------------------------------------------ UC-DIAG-01 Achat
d = Diagram("UC-DIAG-01", "UC-DIAG-01 Achat")
d.title("UC-DIAG-01 — Cas d'utilisation : achat (Visiteur, Client)",
        "Source : CDC v1.1 (Brouillon) §5, §8 P2-P3, F001, F004-F008, F012, F022 · D37, D39-D41")
d.v("sys", "Plateforme (marketplace de produits locaux — V1 Tanger)", 250, 80, 600, 700, BOUNDARY)
d.v("ACT-001", "ACT-001<br>Visiteur <i>[I]</i>", 90, 200, 40, 70, ACTOR + INFERRED, req="§5", statut="I")
d.v("ACT-002", "ACT-002<br>Client", 90, 560, 40, 70, ACTOR, req="§5, D41", statut="E")
d.e("g1", "ACT-002", "ACT-001", style=GEN + "exitX=0;exitY=0.3;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;", points=[(60, 581), (60, 235)], statut="I", req="§5 (Client = Visiteur inscrit)")
uc(d, "UC-001", "Consulter le catalogue<br>(rechercher, filtrer par catégorie)", 290, 120, "F004, RG-006, US-003, CA-F004-1, CA-F004-2", "I")
uc(d, "UC-002", "Consulter une fiche produit<br>(notes, avis, conditions de retour)", 290, 200, "F005, RG-006, RG-011, RG-019, US-004, CA-F005-1")
uc(d, "UC-003", "Gérer le panier multi-vendeurs", 290, 280, "F006, RG-003, RG-006", "E")
uc(d, "UC-004", "S'inscrire / se connecter<br>(compte client)", 290, 360, "F001, RG-014, RG-028, CA-F001-1, CA-F001-2, CA-F001-3")
uc(d, "UC-005", "Passer commande<br>(paiement à la livraison, Tanger)", 290, 470, "F007, RG-001/002/003/007/008/009/017/026/028, US-005")
uc(d, "UC-006", "Suivre ses commandes", 290, 550, "F008, F014, US-006", "I")
uc(d, "UC-007", "Annuler sa commande", 600, 550, "F008, RG-010, US-012", "I", w=230)
uc(d, "UC-008", "Demander le retour d'un produit", 290, 630, "F022, RG-019/022/025/030, US-013")
uc(d, "UC-009", "Noter et commenter<br>un produit reçu", 290, 705, "F012, RG-011, US-010, CA-F012-1, CA-F012-2", h=60)
for i, u in enumerate(["UC-001", "UC-002", "UC-003", "UC-004"]):
    d.e(f"a1_{i}", "ACT-001", u, style=ASSOC_L, req="§5 matrice des permissions")
for i, u in enumerate(["UC-005", "UC-006", "UC-008", "UC-009"]):
    d.e(f"a2_{i}", "ACT-002", u, style=ASSOC_L, req="§5 matrice des permissions")
d.e("inc1", "UC-005", "UC-004", "«include»", DEP, req="RG-028, D41, CA-F001-3", statut="E")
d.e("ext1", "UC-007", "UC-006", "«extend»", DEP, req="RG-010, CA-F008-1/2", statut="I")
d.note("n_ext", "<b>Condition d'extension</b> (RG-010 [I])<br>aucune sous-commande collectée, "
       "c.-à-d. commande pas encore « En collecte » (CA-F008-2, D44)", 890, 470, 260, 70, attach=["ext1"])
d.note("n_ret", "<b>UC-008</b> : ≤ 7 j après réception, tout motif ; refusé si produit signalé "
       "périssable/personnalisé ou catégorie exclue (RG-019, D40) ; <b>un retour par produit</b> (RG-030, D39) ; "
       "moyen de remboursement traçable (RG-022)", 890, 600, 260, 96, attach=["UC-008"])
d.note("n_avis", "<b>UC-009</b> : commande « livrée et payée » uniquement (RG-011, D37) ; "
       "un avis par produit et par commande [I]", 890, 712, 260, 58, attach=["UC-009"])
d.note("n_h1", "<b>[I]</b> UC-001 : recherche/catégories = HYPOTHÈSE H1 ; UC-003 ouvert au Visiteur = HYPOTHÈSE "
       "(panier conservé après connexion, CA-F001-3)", 890, 110, 260, 80, warn=True, attach=["UC-001"])
d.note("n_notif", "Notifications (F014) : transverses, non modélisées comme cas d'utilisation "
       "(voir SEQ-001..003). Canal MANQUANT (Q23).", 890, 290, 260, 64)
d.legend(890, 800, LEG, w=320)
d.write(os.path.join(OUT, "UC-DIAG-01-achat.drawio"))

# ------------------------------------------------------------ UC-DIAG-02 Vente
d = Diagram("UC-DIAG-02", "UC-DIAG-02 Vente")
d.title("UC-DIAG-02 — Cas d'utilisation : vente (Vendeur)",
        "Source : CDC v1.1 §5, §8 P1/P4, F002, F003, F009, F011, F022 · D33, D40, D43")
d.v("sys", "Plateforme", 250, 80, 330, 520, BOUNDARY)
d.v("ACT-003", "ACT-003<br>Vendeur", 90, 300, 40, 70, ACTOR, req="§5", statut="E")
uc(d, "UC-010", "S'inscrire comme vendeur<br>et créer sa boutique", 290, 130, "F002, RG-004/005/016/018/023, US-001, CA-F002-1, CA-F002-2, CA-F002-3")
uc(d, "UC-011", "Gérer ses produits<br>(prix, stock, périssable / personnalisé)", 290, 220, "F003, RG-006/007/015/016/017/019, US-002, CA-F003-1, CA-F003-2, CA-F003-3")
uc(d, "UC-012", "Traiter une sous-commande<br>(accepter / refuser / déclarer prête)", 290, 310, "F009, RG-003/008/011b, US-007")
uc(d, "UC-013", "Vérifier un produit retourné<br>(conforme / contesté, remise en vente)", 290, 400, "F022, RG-017/027, US-014, D43")
uc(d, "UC-014", "Consulter ses montants<br>(retenus, disponibles, reversés, déduits)", 290, 490, "F011, RG-012/021/024, US-009")
for i, u in enumerate(["UC-010", "UC-011", "UC-012", "UC-013", "UC-014"]):
    d.e(f"a3_{i}", "ACT-003", u, style=ASSOC_L, req="§5 matrice des permissions")
d.note("n10", "<b>UC-010</b> : commune sur la liste autorisée (RG-023, D33) ; inscription libre, boutique active "
       "immédiatement (RG-004) ; virement ⇒ coordonnées bancaires (CA-F002-2). Informations exigées : MANQUANT (Q22)",
       620, 110, 290, 96, attach=["UC-010"])
d.note("n12", "<b>UC-012</b> : un refus annule la commande entière (RG-008, D22). Sans réponse dans le délai, "
       "traitée comme refus (RG-011b [I]) ; délai MANQUANT (Q19)", 620, 290, 290, 80, warn=True, attach=["UC-012"])
d.note("n13", "<b>UC-013</b> : décision de remise en vente par le vendeur (D43, RG-017). "
       "Délai de vérification MANQUANT (Q44) ; au-delà, l'administrateur décide [I]", 620, 390, 290, 80,
       warn=True, attach=["UC-013"])
d.note("n_cl", "Cloisonnement (ENF-007, RG-003) : le vendeur n'accède qu'à ses boutique, produits, "
       "sous-commandes, retours et montants.", 620, 500, 290, 60, req="ENF-007, RG-003, CA-F003-3, CA-F009-1")
d.legend(620, 590, LEG, w=320)
d.write(os.path.join(OUT, "UC-DIAG-02-vente.drawio"))

# ------------------------------------------------------------ UC-DIAG-03 Exploitation
d = Diagram("UC-DIAG-03", "UC-DIAG-03 Exploitation")
d.title("UC-DIAG-03 — Cas d'utilisation : exploitation (Administrateur)",
        "Source : CDC v1.1 §5, §8 P5, F010, F011, F013, F022 · D31, D37, D38, D44 · RG-029")
d.v("sys", "Plateforme", 250, 80, 330, 790, BOUNDARY)
d.v("ACT-004", "ACT-004<br>Administrateur", 90, 440, 40, 70, ACTOR, req="§5, D31, D37, D38", statut="E")
rows = [
 ("UC-015", "Transmettre les commandes prêtes<br>à la société de livraison", "F010, RG-029, D44, CA-F010-4", "E"),
 ("UC-016", "Enregistrer collecte, livraison,<br>encaissement, échec, reprise", "F010, F022, RG-008/013/029, US-008, CA-F010-1/3", "E"),
 ("UC-017", "Rapprocher les remises de fonds<br>de la société de livraison", "F010, RG-020, ENF-008, CA-F010-2", "I"),
 ("UC-018", "Arbitrer un litige de retour", "F022, RG-027, US-015, CA-F022-6", "E"),
 ("UC-019", "Enregistrer un remboursement client", "F022, RG-021/022/025, ENF-012, US-015, CA-F022-5/7", "E"),
 ("UC-020", "Enregistrer le reversement<br>hebdomadaire d'un vendeur", "F011, RG-018/021/024/025, CA-F011-2/5", "E"),
 ("UC-021", "Gérer catégories (exclusions de retour),<br>zone clients, communes vendeurs", "F013, RG-001/019/023, D40, ENF-010", "E"),
 ("UC-022", "Modérer : masquer un produit,<br>suspendre un vendeur, masquer un avis", "F013, RG-015, US-011, D37, CA-F013-1/2/3", "E"),
 ("UC-023", "Superviser vendeurs, produits,<br>commandes, retours, montants", "F013, §5 matrice", "I"),
]
for i, (cid, lab, req, st) in enumerate(rows):
    uc(d, cid, lab, 300, 120 + i * 82, req, st, w=250)
    d.e(f"a4_{i}", "ACT-004", cid, style=ASSOC_L, req="§5 matrice des permissions")
d.v("ACT-005", "ACT-005<br>Société de livraison<br>«externe»", 1010, 100, 40, 70,
    ACTOR + "fillColor=#f5f5f5;strokeColor=#666666;", req="§5, D19, D38", statut="E")
d.note("n_sdl", "<b>Aucune association</b> : la société de livraison <b>n'a pas accès</b> à la Plateforme en V1 "
       "(D38, RG-029, ENF-007). Elle transmet ses informations à l'administrateur hors système, qui les saisit "
       "(UC-016). Moyen de transmission : à convenir (C-05).", 930, 260, 260, 120, attach=["ACT-005"], req="D38, RG-029, ENF-007")
d.note("n_23", "<b>UC-023 [I]</b> : périmètre de supervision = HYPOTHÈSE (F013). Inclut, selon la matrice §5, "
       "l'annulation d'une commande, le traitement d'une sous-commande et la vérification d'un retour en cas "
       "de litige ou d'absence de vérification ; sort des en-cours d'un vendeur suspendu décidé par l'admin.",
       620, 720, 280, 130, warn=True, attach=["UC-023"])
d.note("n_15", "<b>UC-015 → « En collecte »</b> dès la transmission (D44, RG-029) ; ensuite le client ne peut plus annuler (CA-F010-4).", 620, 110, 280, 64, attach=["UC-015"])
d.note("n_19", "<b>UC-019</b> : moyen traçable, délai légal (15 j selon R1, à confirmer) ; alerte si demande > 12 j (CA-F022-7, ENF-012 [I]).", 620, 450, 280, 70, warn=True, attach=["UC-019"])
d.legend(620, 590, LEG, w=320)
d.write(os.path.join(OUT, "UC-DIAG-03-exploitation.drawio"))
print("ok uc")
