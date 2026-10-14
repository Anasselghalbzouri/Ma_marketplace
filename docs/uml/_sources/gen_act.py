"""ACTIVITY-001..003 — activity diagrams with swimlanes (CDC v1.1 §8 P2-P5, F007-F011, F022)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from umlkit import *

OUT = os.path.join(os.path.dirname(__file__), "..", "04-activites")
LEG = ["Rectangle arrondi = action ; losange = décision / fusion ; ● début ; ◉ fin d'activité ; ⊗ fin de flot",
       "Sablier = événement temporel (durée paramétrée, non fixée) ; [garde] sur les flots",
       "Bordure pointillée + [I] = étape HYPOTHÈSE du CDC ; couloir gris = acteur externe sans accès (D38)"]
FLOWFINAL = "shape=sumEllipse;perimeter=ellipsePerimeter;whiteSpace=wrap;html=1;backgroundOutline=1;fillColor=#ffffff;"


class Act:
    def __init__(self, d, lanes, x0=20, y0=90, rh=86, rows=12):
        """lanes: list of (id, label, width, ext)"""
        self.d, self.rh, self.y0 = d, rh, y0
        self.cx, x = {}, x0
        self.lane_x = {}
        h = 40 + rows * rh
        for lid, label, w, ext in lanes:
            st = LANE + ("fillColor=#e0e0e0;fontColor=#555555;" if ext else "")
            d.v(lid, label, x, y0, w, h, st)
            self.cx[lid], self.lane_x[lid] = x + w / 2, x
            x += w
        self.bottom = y0 + h

    def n(self, cid, kind, lane, row, label="", dx=0, req=None, statut="E", w=210, h=None):
        y = self.y0 + 40 + row * self.rh + self.rh / 2
        cx = self.cx[lane] + dx
        if kind == "init":
            return self.d.v(cid, "", cx - 15, y - 15, 30, 30, INITIAL, parent=lane, req=req)
        if kind == "final":
            return self.d.v(cid, "", cx - 15, y - 15, 30, 30, FINAL, parent=lane, req=req)
        if kind == "ff":
            return self.d.v(cid, "", cx - 13, y - 13, 26, 26, FLOWFINAL, parent=lane, req=req)
        if kind == "dec":
            return self.d.v(cid, label, cx - 22, y - 22, 44, 44, DECISION, parent=lane, req=req)
        if kind == "time":
            return self.d.v(cid, label, cx - 12, y - 18, 24, 36, TIMEEV, parent=lane, req=req, statut=statut)
        h = h or 60
        st = ACTION + (INFERRED if statut == "I" else "")
        lab = label + (" <i>[I]</i>" if statut == "I" else "")
        return self.d.v(cid, lab, cx - w / 2, y - h / 2, w, h, st, parent=lane, req=req, statut=statut)

    def f(self, cid, a, b, guard="", ex=None, en=None, points=None, req=None):
        st = FLOW
        if ex:
            st += f"exitX={ex[0]};exitY={ex[1]};exitDx=0;exitDy=0;"
        if en:
            st += f"entryX={en[0]};entryY={en[1]};entryDx=0;entryDy=0;"
        self.d.e(cid, a, b, f"[{guard}]" if guard else "", st, points=points, req=req)

    def chain(self, prefix, ids):
        for i in range(len(ids) - 1):
            self.f(f"{prefix}{i}", ids[i], ids[i + 1])


B, T, L, R = (0.5, 1), (0.5, 0), (0, 0.5), (1, 0.5)
Y = lambda r: 90 + 40 + r * 86 + 43

# =================================================================== ACTIVITY-001
d = Diagram("ACTIVITY-001", "ACTIVITY-001 Cycle de commande")
d.title("ACTIVITY-001 — Cycle de commande de bout en bout (panier → livraison et paiement)",
        "Source : CDC v1.1 P2, P4, P5, F006-F010, F014 · RG-001/003/008/011b/013/017/024/026/028/029 · D22, D38, D41, D44")
a = Act(d, [("lC", "Client", 280, False), ("lP", "Plateforme", 300, False), ("lV", "Vendeur(s)", 280, False),
            ("lA", "Administrateur", 300, False), ("lS", "Société de livraison «externe»", 280, True)], rows=16)
a.n("i0", "init", "lC", 0)
a.n("c1", "act", "lC", 1, "Constituer le panier<br>(un ou plusieurs vendeurs)", req="F006")
a.n("c2", "act", "lC", 2, "Se connecter ou créer un compte<br>(obligatoire, RG-028)", req="RG-028, D41, CA-F001-3")
a.n("c3", "act", "lC", 3, "Saisir adresse à Tanger et téléphone ;<br>confirmer (paiement à la livraison)",
    req="F007, RG-002, RG-014, CA-F007-3/4")
a.n("p1", "dec", "lP", 4, "", req="RG-001, F007")
a.n("pff", "ff", "lP", 4, dx=120, req="CA-F007-2 (hors Tanger ou stock insuffisant)")
a.n("p2", "act", "lP", 5, "Créer la commande et une sous-commande<br>par vendeur ; réserver le stock ;<br>"
    "confirmation écrite ; notifier", req="RG-003, RG-017, RG-026, CA-F007-1, CA-F014-1", h=66)
a.n("v1", "act", "lV", 6, "Accepter ou refuser sa sous-commande<br>(chaque vendeur, délai Q19)", req="F009, RG-011b")
a.n("p3", "dec", "lP", 7, "", req="RG-008, D22")
a.n("p4", "act", "lP", 8, "Annuler la commande entière ;<br>restituer le stock ; notifier tous", req="RG-008, CA-F009-3, CA-F014-2")
a.n("pf1", "final", "lP", 9)
a.n("v2", "act", "lV", 8, "Préparer et déclarer<br>« prête pour collecte »", req="CA-F009-2")
a.n("a1", "act", "lA", 9, "Transmettre la commande à la société<br>de livraison → « En collecte »", req="D44, RG-029, CA-F010-4")
a.n("s1", "act", "lS", 10, "Collecter chez chaque vendeur ;<br>livrer en une fois ; encaisser", req="D19, RG-008, RG-002")
a.n("a2", "act", "lA", 11, "Saisir collecte, « en livraison »<br>et résultat transmis (RG-029)", req="RG-029, US-008")
a.n("a3", "dec", "lA", 12, "", req="CA-F010-1, CA-F010-3")
a.n("p5", "act", "lP", 12, "« Échec de livraison » ; aucun montant<br>dû ; stock restitué [RG-013]",
    req="RG-013, RG-017, CA-F010-3", statut="I")
a.n("pf2", "final", "lP", 13, dx=-100)
a.n("a4", "act", "lA", 13, "Saisir montant encaissé<br>et date de réception", req="CA-F010-1")
a.n("p6", "act", "lP", 14, "Clôturer la commande ; montants vendeurs<br>« Retenu » ; écart signalé si ≠ dû",
    req="CA-F010-1, CA-F010-2, RG-024")
a.n("pf3", "final", "lP", 15)
a.chain("fc", ["i0", "c1", "c2", "c3"])
a.f("f_c3p1", "c3", "p1", ex=B, en=L, points=[(160, 90 + 40 + 4 * 86 + 43)])
a.f("f_p1n", "p1", "pff", "non", ex=R, en=L)
d.v("t_pff", "hors Tanger ou stock<br>insuffisant : message<br>(CA-F007-2)", 595, Y(4) + 16, 140, 44, TEXT + "fontSize=10;", parent="lP")
a.f("f_p1o", "p1", "p2", "oui", ex=B, en=T)
a.f("f_p2v1", "p2", "v1", ex=B, en=T, points=[(450, 90 + 40 + 6 * 86 + 5), (740, 90 + 40 + 6 * 86 + 5)])
a.f("f_v1p3", "v1", "p3", ex=B, en=R, points=[(740, 90 + 40 + 7 * 86 + 43)])
a.f("f_p3n", "p3", "p4", "non : refus ou sans réponse", ex=B, en=T)
a.f("f_p4", "p4", "pf1", ex=B, en=T)
a.f("f_p3o", "p3", "v2", "oui : toutes acceptées", ex=R, en=T, points=[(740, 90 + 40 + 7 * 86 + 43)])
a.f("f_v2a1", "v2", "a1", ex=B, en=T, points=[(740, 90 + 40 + 9 * 86 + 5), (1030, 90 + 40 + 9 * 86 + 5)])
a.f("f_a1s1", "a1", "s1", ex=B, en=T, points=[(1030, 90 + 40 + 10 * 86 + 5), (1320, 90 + 40 + 10 * 86 + 5)])
a.f("f_s1a2", "s1", "a2", ex=B, en=T, points=[(1320, 90 + 40 + 11 * 86 + 5), (1030, 90 + 40 + 11 * 86 + 5)])
a.f("f_a2a3", "a2", "a3", ex=B, en=T)
a.f("f_a3n", "a3", "p5", "non : absent, injoignable, refus", ex=L, en=R)
a.f("f_p5", "p5", "pf2", ex=B, en=T, points=[(350, 90 + 40 + 13 * 86 + 5)])
a.f("f_a3o", "a3", "a4", "livrée et payée", ex=B, en=T)
a.f("f_a4p6", "a4", "p6", ex=B, en=R, points=[(1030, 90 + 40 + 14 * 86 + 43)])
a.f("f_p6", "p6", "pf3", ex=B, en=T)
d.note("n1", "<b>Annulation client</b> (F008, RG-010 [I]) possible tant qu'aucune sous-commande n'est collectée, "
       "c.-à-d. avant « En collecte » (CA-F008-2, CA-F010-4). Non dessinée comme flot : événement interrompant "
       "les étapes 5-9.", 1480, 130, 260, 110)
d.note("n2", "<b>WARN</b> Q19 délai de réponse vendeur ; Q24 suite d'un échec de livraison ; Q27 montant des "
       "frais de livraison. Répartition en sous-commandes et étapes intermédiaires = HYPOTHÈSE §7.",
       1480, 260, 260, 100, warn=True)
d.note("n3", "Suite : retours → ACTIVITY-002 ; retenue et reversement → ACTIVITY-003 ; "
       "rapprochement des remises de fonds → SEQ-002.", 1480, 380, 260, 70)
d.legend(20, a.bottom + 20, LEG, w=620)
d.write(os.path.join(OUT, "ACTIVITY-001-cycle-commande.drawio"))

# =================================================================== ACTIVITY-002
d = Diagram("ACTIVITY-002", "ACTIVITY-002 Processus de retour")
d.title("ACTIVITY-002 — Processus de retour d'un produit (éligibilité, reprise, vérification, litige, remboursement)",
        "Source : CDC v1.1 P3, P4.6, P5.5, F022 · RG-017/019/021/022/025/027/029/030 · ENF-012 · CA-F022-1..9 · "
        "D30-D32, D38-D40, D42, D43")
Y = lambda r: 90 + 40 + r * 86 + 43
a = Act(d, [("lC", "Client", 280, False), ("lP", "Plateforme", 300, False), ("lA", "Administrateur", 300, False),
            ("lS", "Société de livraison «externe»", 260, True), ("lV", "Vendeur", 300, False)], rows=18)
xC, xP, xA, xS, xV = 160, 450, 750, 1030, 1310
a.n("i0", "init", "lC", 0)
a.n("c1", "act", "lC", 1, "Sélectionner un produit reçu<br>(un retour par ligne, RG-030)", req="F022, RG-030, CA-F022-9")
a.n("p1", "dec", "lP", 2, "", req="RG-019, D40")
a.n("pff", "ff", "lP", 2, dx=120, req="CA-F022-2/3/8 (> 7 j ou produit exclu)")
a.n("p2", "act", "lP", 3, "Afficher les frais de retour déduits<br>si motif = changement d'avis", req="D42, CA-F022-1")
a.n("c2", "act", "lC", 4, "Indiquer quantité, motif et moyen<br>de remboursement traçable ; confirmer",
    req="RG-022, CA-F022-4")
a.n("p3", "act", "lP", 5, "Enregistrer le retour « Demandé » ;<br>notifier vendeur et administrateur",
    req="CA-F022-1, P3.4 [I]")
a.n("a1", "act", "lA", 6, "Demander la reprise<br>(hors Plateforme)", req="D38")
a.n("s1", "act", "lS", 7, "Reprendre le produit chez<br>le client ; le remettre au vendeur", req="P3.5, D19", w=200)
a.n("a2", "act", "lA", 8, "Saisir la reprise (RG-029)", req="RG-029")
a.n("v1", "act", "lV", 9, "Vérifier le produit : conforme<br>ou contesté (motif) ; décider<br>la remise en vente",
    req="RG-027, D31, D43, US-014", h=66)
a.n("v2", "dec", "lV", 10, "", req="RG-017, D43")
a.n("p4", "act", "lP", 10, "Restituer le stock (RG-017)", req="RG-017, D43")
a.n("v3", "dec", "lV", 11, "", req="")
a.n("v4", "dec", "lV", 12, "", req="RG-027")
a.n("a3", "act", "lA", 12, "Arbitrer le litige<br>(décision finale [I])", req="RG-027, CA-F022-6, US-015")
a.n("a4", "dec", "lA", 13, "", req="")
a.n("c3", "act", "lC", 13, "Retour refusé ; produit<br>renvoyé au client", req="F022 exceptions", statut="I")
a.n("cf", "final", "lC", 14)
a.n("a5", "act", "lA", 14, "Enregistrer le remboursement<br>(moyen, référence, date)", req="RG-022, CA-F022-5")
a.n("p5", "act", "lP", 15, "Montant = prix − frais si changement d'avis ;<br>frais au vendeur si défaut/erreur ;<br>"
    "déduction vendeur (RG-021) ; notifier", req="RG-021, RG-022, RG-025, CA-F011-3/4", w=250, h=66)
a.n("pf", "final", "lP", 16)
a.n("t1", "time", "lA", 16, "demande > 12 j<br>sans remboursement", dx=-40, statut="I", req="ENF-012, CA-F022-7")
a.n("a6", "act", "lA", 17, "Retour signalé proche<br>du délai légal", dx=-40, req="ENF-012, CA-F022-7", statut="I", w=160, h=56)
a.f("f0", "i0", "c1", ex=B, en=T)
a.f("f1", "c1", "p1", ex=B, en=L, points=[(xC, Y(2))])
a.f("f2", "p1", "pff", "non", ex=R, en=L)
d.v("t_pff", "> 7 j ou produit exclu :<br>retour non proposé, raison<br>(CA-F022-2/3/8)", 595, Y(2) + 16, 150, 44, TEXT + "fontSize=10;", parent="lP")
a.f("f3", "p1", "p2", "oui", ex=B, en=T)
a.f("f4", "p2", "c2", ex=B, en=T, points=[(xP, Y(4) - 38), (xC, Y(4) - 38)])
a.f("f5", "c2", "p3", ex=B, en=T, points=[(xC, Y(5) - 38), (xP, Y(5) - 38)])
a.f("f6", "p3", "a1", ex=B, en=T, points=[(xP, Y(6) - 38), (xA, Y(6) - 38)])
a.f("f7", "a1", "s1", ex=B, en=T, points=[(xA, Y(7) - 38), (xS, Y(7) - 38)])
a.f("f8", "s1", "a2", ex=B, en=T, points=[(xS, Y(8) - 38), (xA, Y(8) - 38)])
a.f("f9", "a2", "v1", ex=B, en=T, points=[(xA, Y(9) - 42), (xV, Y(9) - 42)])
a.f("f10", "v1", "v2", ex=B, en=T)
a.f("f11", "v2", "p4", "remise en vente", ex=L, en=R)
a.f("f12", "p4", "v3", ex=B, en=L, points=[(xP, Y(11))])
a.f("f13", "v2", "v3", "non", ex=B, en=T)
a.f("f14", "v3", "v4", ex=B, en=T)
a.f("f15", "v4", "a3", "contesté", ex=L, en=R)
a.f("f16", "a3", "a4", ex=B, en=T)
a.f("f17", "a4", "c3", "en faveur du vendeur [I]", ex=L, en=R)
a.f("f18", "c3", "cf", ex=B, en=T)
a.f("f19", "a4", "a5", "en faveur du client", ex=B, en=T)
a.f("f20", "v4", "a5", "conforme", ex=B, en=R, points=[(xV, Y(14))])
a.f("f21", "a5", "p5", ex=B, en=T, points=[(xA, Y(15) - 40), (xP, Y(15) - 40)])
a.f("f22", "p5", "pf", ex=B, en=T)
a.f("f23", "t1", "a6", ex=B, en=T)
d.note("n1", "<b>WARN</b> Q44 délai de vérification vendeur : au-delà, l'administrateur décide [I] (F022). "
       "Q45 montant des frais de retour ; Q40 remboursement des frais de livraison initiaux ; Q42 moyens "
       "alternatifs ; Q43 cosmétiques ouverts. Délai légal 15 j (R1) à valider juridiquement (C-08, ENF-009).",
       1480, 130, 270, 130, warn=True, req="ENF-009, C-08, ENF-012")
d.note("n2", "Frais de retour (RG-025) : client si changement d'avis (déduits), vendeur si défaut / incorrect / "
       "non conforme ; en litige, la décision fixe l'imputation (CA-F022-6).", 1480, 280, 270, 90)
d.legend(20, a.bottom + 20, LEG, w=620)
d.write(os.path.join(OUT, "ACTIVITY-002-processus-retour.drawio"))

# =================================================================== ACTIVITY-003
d = Diagram("ACTIVITY-003", "ACTIVITY-003 Retenue et reversement")
d.title("ACTIVITY-003 — Retenue, mise à disposition et reversement hebdomadaire des montants vendeurs",
        "Source : CDC v1.1 P4.5, P5.6-7, F011 · RG-005/012/018/021/024/025 · CA-F011-1..5 · D16, D21, D29, D34")
a = Act(d, [("lP", "Plateforme", 620, False), ("lA", "Administrateur", 320, False), ("lV", "Vendeur", 300, False)],
        rows=14)
MAIN, SIDE = -150, 160
xM, xS2 = 20 + 310 + MAIN, 20 + 310 + SIDE
a.n("i0", "init", "lP", 0, dx=MAIN)
a.n("p1", "act", "lP", 1, "Commande livrée et payée : calculer le<br>montant dû par ligne (sans commission<br>"
    "ni frais de livraison) → « Retenu »", dx=MAIN, req="RG-005, RG-012, RG-024, CA-F010-1", w=260, h=66)
a.n("t1", "time", "lP", 2, "fin du délai de retour<br>(réception + 7 j)", dx=MAIN, req="RG-024, CA-F011-1")
a.n("p2", "dec", "lP", 3, "", dx=MAIN, req="RG-024")
a.n("p3", "act", "lP", 3, "Maintenir « Retenu » jusqu'à<br>la clôture du retour", dx=SIDE, req="RG-024 (cas HYPOTHÈSE)",
    statut="I")
a.n("p4", "dec", "lP", 4, "", dx=SIDE, req="RG-021")
a.n("p5", "act", "lP", 5, "Montant « Déduit » : annulé<br>(et frais vendeur imputés)", dx=SIDE,
    req="RG-021, RG-025, CA-F011-3")
a.n("pff", "ff", "lP", 6, dx=SIDE)
a.n("p6", "dec", "lP", 5, "", dx=MAIN)
a.n("p7", "act", "lP", 6, "Montant → « Disponible »", dx=MAIN, req="CA-F011-1")
a.n("t2", "time", "lP", 7, "chaque semaine<br>(jour à fixer)", dx=MAIN, req="RG-018, D34")
a.n("p8", "act", "lP", 8, "Calculer par vendeur : Σ disponibles<br>− Σ déductions non encore imputées<br>"
    "(remboursements, frais de retour)", dx=MAIN, req="RG-018, RG-021, CA-F011-4, CA-F011-5", w=260, h=66)
a.n("p9", "dec", "lP", 9, "", dx=MAIN, req="F011 exceptions")
a.n("p10", "act", "lP", 9, "Pas de reversement ; solde<br>négatif reporté et signalé (Q38)", dx=140, w=180,
    req="F011 exceptions, Q38", statut="I")
a.n("pff2", "ff", "lP", 9, dx=285)
a.n("a1", "act", "lA", 10, "Effectuer le virement ou la remise<br>en espèces (mode du vendeur)", req="RG-018, D21")
a.n("a2", "act", "lA", 11, "Enregistrer le reversement (date,<br>montant, mode ; preuve si espèces [I])",
    req="CA-F011-2, ENF-008")
a.n("p11", "act", "lP", 12, "Montants → « Reversé » ; déductions<br>imputées (régularisation) ; notifier", dx=MAIN,
    req="RG-021, CA-F011-4, F014", w=260)
a.n("v1", "act", "lV", 13, "Consulter l'historique (montant, date,<br>mode, commandes, régularisations)",
    req="CA-F011-2, US-009", w=240)
a.n("vf", "final", "lV", 13, dx=135)
a.f("f0", "i0", "p1", ex=B, en=T)
a.f("f1", "p1", "t1", ex=B, en=T)
a.f("f2", "t1", "p2", ex=B, en=T)
a.f("f3", "p2", "p3", "retour en cours sur la ligne", ex=R, en=L)
a.f("f4", "p3", "p4", "retour clôturé", ex=B, en=T)
a.f("f5", "p4", "p5", "remboursé", ex=B, en=T)
a.f("f6", "p5", "pff", ex=B, en=T)
a.f("f7", "p4", "p6", "refusé", ex=L, en=R, points=[(xM + 90, Y(4)), (xM + 90, Y(5))])
a.f("f8", "p2", "p6", "aucun retour en cours", ex=B, en=T)
a.f("f9", "p6", "p7", ex=B, en=T)
a.f("f10", "p7", "t2", ex=B, en=T)
a.f("f11", "t2", "p8", ex=B, en=T)
a.f("f12", "p8", "p9", ex=B, en=T)
a.f("f13", "p9", "p10", "≤ 0", ex=R, en=L)
a.f("f14", "p10", "pff2", ex=R, en=L)
a.f("f15", "p9", "a1", "> 0", ex=B, en=L, points=[(xM, Y(10))])
a.f("f16", "a1", "a2", ex=B, en=T)
a.f("f17", "a2", "p11", ex=B, en=R, points=[(800, Y(12))])
a.f("f18", "p11", "v1", ex=B, en=L, points=[(xM, Y(13))])
a.f("f19", "v1", "vf", ex=R, en=L)
d.note("n1", "<b>Après reversement</b> : un remboursement ultérieur crée une Déduction régularisée sur le "
       "reversement suivant (RG-021, CA-F011-4). Montants des commandes annulées ou en échec : aucun montant dû.",
       1280, 130, 300, 100)
d.note("n2", "<b>WARN</b> Q38 solde négatif (report = HYPOTHÈSE) ; jour du reversement MANQUANT ; "
       "retenue prolongée d'un retour en cours = HYPOTHÈSE (RG-024).", 1280, 250, 300, 90, warn=True)
d.legend(20, a.bottom + 20, LEG, w=620)
d.write(os.path.join(OUT, "ACTIVITY-003-retenue-reversement.drawio"))
print("ok act")
