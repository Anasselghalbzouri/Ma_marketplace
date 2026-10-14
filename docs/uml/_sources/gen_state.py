"""STATE-001..004 — state machine diagrams (CDC v1.1 §7 cycles de vie, RG-008/010/011b/013/021/024/027/029)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from umlkit import *

OUT = os.path.join(os.path.dirname(__file__), "..", "05-etats")
LEG = ["Rectangle arrondi vert = état (vocabulaire §7) ; ● état initial ; ◉ état final",
       "Transition : événement [garde] / action ; after(x) = événement temporel paramétré (durée non fixée)",
       "[I] = transition / état HYPOTHÈSE du CDC ou inférence Blueprint ; note rouge = WARN"]


def side(ex, en):
    return (f"exitX={ex[0]};exitY={ex[1]};exitDx=0;exitDy=0;entryX={en[0]};entryY={en[1]};entryDx=0;entryDy=0;")


def st(d, cid, label, x, y, w=190, h=56, req=None, statut="E"):
    style = STATE + (INFERRED if statut == "I" else "")
    return d.v(cid, f"<b>{label}</b>" + (" <i>[I]</i>" if statut == "I" else ""), x, y, w, h, style,
               req=req, statut=statut)


def tr(d, cid, a, b, label, ex, en, points=None, req=None, statut="E"):
    d.e(cid, a, b, label, TRANS + side(ex, en), points=points, req=req, statut=statut)


B, T, L, R = (0.5, 1), (0.5, 0), (0, 0.5), (1, 0.5)

# =================================================================== STATE-001 Commande
d = Diagram("STATE-001", "STATE-001 Commande")
d.title("STATE-001 — Machine à états : Commande (client)",
        "Source : CDC v1.1 §7 cycle « Commande », RG-008, RG-010, RG-011b, RG-013, RG-029, CA-F008-1/2, CA-F009-3, "
        "CA-F010-1/3/4 · D22, D44")
d.v("i", "", 115, 110, 30, 30, INITIAL)
st(d, "S_att", "En attente d'acceptation<br>des vendeurs", 40, 190, w=200, req="§7, F007")
st(d, "S_conf", "Confirmée", 40, 360, w=200, req="§7", statut="I")
st(d, "S_coll", "En collecte", 40, 530, w=200, req="§7, D44, RG-029")
st(d, "S_livr", "En livraison", 40, 700, w=200, req="§7, F010")
st(d, "S_ok", "Livrée et payée", 40, 870, w=200, req="§7, CA-F010-1")
st(d, "S_ann", "Annulée", 560, 360, w=200, req="§7, RG-008, RG-010")
st(d, "S_ech", "Échec de livraison", 560, 870, w=200, req="§7, RG-013, CA-F010-3")
d.v("f1", "", 125, 990, 30, 30, FINAL)
d.v("f2", "", 645, 470, 30, 30, FINAL)
d.v("f3", "", 645, 990, 30, 30, FINAL)
tr(d, "t0", "i", "S_att", "validation de la commande<br>/ créer sous-commandes ; réserver stock ; notifier",
   B, T, req="CA-F007-1, RG-003, RG-017")
tr(d, "t1", "S_att", "S_conf", "toutes les sous-commandes acceptées<br>/ notifier le client", B, T, req="F009, P2.7",
   statut="I")
tr(d, "t2", "S_att", "S_ann", "refus d'un vendeur, ou after(délaiRéponseVendeur) [I],<br>ou annulation client<br>"
   "/ annuler les sous-commandes ; restituer stock ; notifier", R, (0, 0.2), points=[(400, 218), (400, 371)],
   req="RG-008, RG-011b, RG-010, CA-F009-3, CA-F014-2")
tr(d, "t3", "S_conf", "S_coll", "transmission à la société de livraison<br>(saisie admin) [toutes prêtes]", B, T,
   req="D44, RG-029, CA-F010-4")
tr(d, "t4", "S_conf", "S_ann", "annulation client [aucune sous-commande collectée]<br>/ restituer stock ; notifier vendeurs",
   R, (0, 0.8), req="RG-010, CA-F008-1", statut="I")
tr(d, "t5", "S_coll", "S_livr", "saisie « en livraison » (admin)<br>[toutes sous-commandes collectées]", B, T,
   req="RG-008, RG-029")
tr(d, "t6", "S_livr", "S_ok", "saisie livrée et payée (montant, date)<br>/ montants vendeurs « Retenu » ; "
   "écart signalé si ≠ dû", B, T, req="CA-F010-1, CA-F010-2")
tr(d, "t7", "S_livr", "S_ech", "saisie échec (motif) / aucun montant dû ;<br>stock restitué [I]", R, (0, 0.3),
   points=[(470, 728), (470, 887)], req="RG-013, CA-F010-3")
tr(d, "t8", "S_ok", "f1", "", B, T)
tr(d, "t9", "S_ann", "f2", "", B, T)
tr(d, "t10", "S_ech", "f3", "", B, T)
d.note("n1", "<b>Annulation client</b> refusée dès « En collecte » (CA-F008-2, CA-F010-4) : aucune transition "
       "client depuis En collecte / En livraison.", 820, 520, 280, 70)
d.note("n2", "<b>« Livrée et payée »</b> = commande close (CA-F010-1). Les retours sont des objets Retour "
       "distincts (STATE-003), sans nouvel état de la commande (décision Stage A §7.2).", 820, 840, 280, 80)
d.note("n3", "<b>WARN</b> Q24 : après « Échec de livraison », nouvelle tentative ou retour des produits aux "
       "vendeurs non définis ⇒ état final provisoire. Étapes hors « En collecte » = HYPOTHÈSE §7. "
       "Délai de réponse vendeur Q19.", 820, 670, 280, 100, warn=True)
d.legend(820, 960, LEG, w=520)
d.write(os.path.join(OUT, "STATE-001-commande.drawio"))

# =================================================================== STATE-002 SousCommande
d = Diagram("STATE-002", "STATE-002 SousCommande")
d.title("STATE-002 — Machine à états : SousCommande (vendeur) [cycle HYPOTHÈSE §7]",
        "Source : CDC v1.1 §7 cycle « Sous-commande », F009, RG-003, RG-008, RG-011b, RG-029, CA-F009-2/3")
d.v("i", "", 115, 110, 30, 30, INITIAL)
st(d, "S_new", "Nouvelle", 40, 190, w=200, req="§7", statut="I")
st(d, "S_acc", "Acceptée", 40, 360, w=200, req="§7, F009", statut="I")
st(d, "S_pret", "Prête pour collecte", 40, 530, w=200, req="§7, CA-F009-2", statut="I")
st(d, "S_coll", "Collectée", 40, 700, w=200, req="§7, RG-029", statut="I")
st(d, "S_ref", "Refusée", 560, 190, w=200, req="§7, F009, RG-011b", statut="I")
st(d, "S_ann", "Annulée", 560, 450, w=200, req="§7, RG-008", statut="I")
d.v("f1", "", 125, 820, 30, 30, FINAL)
d.v("f2", "", 645, 300, 30, 30, FINAL)
d.v("f3", "", 645, 560, 30, 30, FINAL)
tr(d, "t0", "i", "S_new", "création de la commande / notifier le vendeur", B, T, req="RG-003, CA-F014-1")
tr(d, "t1", "S_new", "S_acc", "accepter (vendeur)", B, T, req="F009")
tr(d, "t2", "S_new", "S_ref", "refuser(motif), ou after(délaiRéponseVendeur) [I]<br>/ annuler la commande entière (RG-008)",
   R, L, req="F009, RG-011b, RG-008, D22")
tr(d, "t3", "S_acc", "S_pret", "déclarer prête (vendeur)", B, T, req="CA-F009-2")
tr(d, "t4", "S_pret", "S_coll", "saisie de la collecte (admin)", B, T, req="RG-029, F010")
tr(d, "t5", "S_new", "S_ann", "commande annulée (autre vendeur, client)", (1, 0.85), (0, 0.2), points=[(420, 238), (420, 461)],
   req="RG-008, CA-F009-3")
tr(d, "t6", "S_acc", "S_ann", "commande annulée", R, (0, 0.5), req="RG-008, RG-010")
tr(d, "t7", "S_pret", "S_ann", "commande annulée [avant transmission]", R, (0, 0.8), req="RG-010, CA-F010-4")
tr(d, "t8", "S_coll", "f1", "", B, T)
tr(d, "t9", "S_ref", "f2", "", B, T)
tr(d, "t10", "S_ann", "f3", "", B, T)
d.note("n1", "<b>Cohérence avec STATE-001</b> : un passage en « Refusée » déclenche l'annulation de la Commande, "
       "qui fait passer les autres SousCommandes en « Annulée » (RG-008, D22).", 820, 190, 280, 80)
d.note("n2", "<b>WARN</b> : l'ensemble du cycle est HYPOTHÈSE (§7) ; délai de réponse (Q19) ; sort des "
       "sous-commandes d'un vendeur suspendu décidé par l'administrateur (F013, N9).", 820, 300, 280, 90, warn=True)
d.legend(820, 700, LEG, w=520)
d.write(os.path.join(OUT, "STATE-002-sous-commande.drawio"))

# =================================================================== STATE-003 Retour
d = Diagram("STATE-003", "STATE-003 Retour")
d.title("STATE-003 — Machine à états : Retour (un produit d'une commande)",
        "Source : CDC v1.1 §7 cycle « Retour » (granularité D39, étapes HYPOTHÈSE), F022, RG-022, RG-027, RG-029, "
        "RG-030, ENF-012, CA-F022-5/6/7")
d.v("i", "", 115, 110, 30, 30, INITIAL)
st(d, "S_dem", "Demandé", 40, 190, w=200, req="§7, CA-F022-1", statut="I")
st(d, "S_enr", "En reprise", 40, 340, w=200, req="§7", statut="I")
st(d, "S_rep", "Repris", 40, 490, w=200, req="§7, RG-029", statut="I")
st(d, "S_ver", "Vérifié par le vendeur", 40, 640, w=200, req="§7, RG-027", statut="I")
st(d, "S_rem", "Client remboursé", 40, 820, w=200, req="§7, RG-022, CA-F022-5")
st(d, "S_con", "Contesté", 560, 640, w=200, req="§7, RG-027", statut="I")
st(d, "S_lit", "Litige", 560, 820, w=200, req="§7, CA-F022-6")
st(d, "S_refu", "Retour refusé", 560, 990, w=200, req="§7, F022 exceptions", statut="I")
d.v("f1", "", 125, 1010, 30, 30, FINAL)
d.v("f2", "", 900, 1003, 30, 30, FINAL)
tr(d, "t0", "i", "S_dem", "demande éligible [≤ 7 j ∧ non exclu] / notifier vendeur + admin", B, T,
   req="RG-019, CA-F022-1")
tr(d, "t1", "S_dem", "S_enr", "reprise demandée à la société de livraison [I]", B, T, req="P3.5, D38", statut="I")
tr(d, "t2", "S_enr", "S_rep", "saisie de la reprise (admin) / notifier le vendeur", B, T, req="RG-029")
tr(d, "t3", "S_rep", "S_ver", "vérification : conforme<br>/ remise en stock si remiseEnVente (RG-017)", B, T,
   req="RG-027, RG-017, D43")
tr(d, "t4", "S_rep", "S_con", "vérification : contestée (motif)<br>/ remise en stock si remiseEnVente",
   R, (0.5, 0), points=[(660, 518)], req="RG-027, D43")
tr(d, "t5", "S_ver", "S_rem", "remboursement enregistré (admin)<br>/ montant = prix − frais si changement d'avis ;"
   "<br>déduction vendeur (RG-021) ; notifier", B, T, req="RG-021, RG-022, RG-025, CA-F022-5")
tr(d, "t6", "S_con", "S_lit", "contestation enregistrée<br>/ notifier l'administrateur", B, T, req="CA-F022-6")
tr(d, "t7", "S_lit", "S_rem", "décision admin en faveur du client<br>/ remboursement selon la décision",
   L, R, req="RG-027, CA-F022-6")
tr(d, "t8", "S_lit", "S_refu", "décision en faveur du vendeur [I]<br>/ produit renvoyé au client", B, T,
   req="F022 exceptions", statut="I")
tr(d, "t9", "S_rem", "f1", "", B, T)
tr(d, "t10", "S_refu", "f2", "", R, L)
d.note("n1", "<b>Événement temporel [I]</b> (ENF-012, CA-F022-7) : after(12 j depuis la demande) sans "
       "remboursement / signaler à l'administrateur — s'applique à tout état non final ; ne change pas l'état.",
       820, 190, 300, 90, warn=True)
d.note("n2", "<b>WARN</b> Q44 : after(délaiVérification) sans vérification ⇒ décision de l'administrateur [I] "
       "(transition non dessinée faute de cible définie). Délai légal 15 j (R1) à valider (C-08).",
       820, 300, 300, 90, warn=True)
d.note("n3", "Un Retour par ligne de commande (RG-030, D39) ; demande non éligible ⇒ aucun objet Retour créé "
       "(CA-F022-2/3/8).", 820, 410, 300, 60)
d.legend(820, 1080, LEG, w=520)
d.write(os.path.join(OUT, "STATE-003-retour.drawio"))

# =================================================================== STATE-004 MontantVendeur
d = Diagram("STATE-004", "STATE-004 MontantVendeur")
d.title("STATE-004 — Machine à états : MontantVendeur (somme due pour une ligne de commande)",
        "Source : CDC v1.1 §7 cycle « Montant vendeur » (CONFIRMÉ D29, D34), F011, RG-012, RG-018, RG-021, RG-024, "
        "RG-025, CA-F011-1..5")
d.v("i", "", 165, 110, 30, 30, INITIAL)
st(d, "S_ret", "Retenu", 80, 200, w=200, req="§7, RG-024, CA-F010-1")
st(d, "S_dis", "Disponible", 80, 420, w=200, req="§7, RG-024, CA-F011-1")
st(d, "S_rev", "Reversé", 80, 640, w=200, req="§7, RG-018, CA-F011-2")
st(d, "S_ded", "Déduit", 560, 420, w=200, req="§7, RG-021, CA-F011-3")
d.v("f1", "", 165, 790, 30, 30, FINAL)
d.v("f2", "", 645, 560, 30, 30, FINAL)
tr(d, "t0", "i", "S_ret", "commande livrée et payée<br>/ montant = valeur de la ligne (sans commission)", B, T,
   req="CA-F010-1, RG-005, RG-012")
tr(d, "t1", "S_ret", "S_dis", "after(dateRéception + 7 j)<br>[aucun retour en cours sur la ligne]", B, T,
   req="RG-024, CA-F011-1")
tr(d, "t1b", "S_ret", "S_dis", "retour clôturé<br>sans remboursement [I]", (0, 0.5), (0, 0.5), points=[(10, 228), (10, 448)], req="RG-024 (cas HYPOTHÈSE)",
   statut="I")
tr(d, "t2", "S_ret", "S_ded", "retour remboursé<br>/ montant annulé ; frais vendeur imputés si défaut", R, T,
   points=[(660, 228)], req="RG-021, RG-025, CA-F011-3")
tr(d, "t3", "S_dis", "S_rev", "reversement hebdomadaire enregistré<br>/ déductions en attente imputées", B, T,
   req="RG-018, CA-F011-5")
tr(d, "t4", "S_dis", "S_ded", "retour remboursé (avant reversement) [I]", R, L, req="RG-021", statut="I")
tr(d, "t5", "S_rev", "f1", "", B, T)
tr(d, "t6", "S_ded", "f2", "", B, T)
d.note("n1", "<b>Reversé puis remboursé</b> (RG-021, CA-F011-4) : le montant reste « Reversé » ; une "
       "<b>Déduction</b> (CLASS-02) est créée et régularisée sur le reversement suivant.", 340, 620, 300, 80,
       attach=["S_rev"])
d.note("n2", "<b>WARN</b> : t1b (retour clôturé sans remboursement, ex. litige gagné par le vendeur) et t4 sont des "
       "inférences ; solde négatif (Q38) ; jour du reversement MANQUANT.", 820, 420, 300, 90, warn=True)
d.legend(820, 640, LEG, w=520)
d.write(os.path.join(OUT, "STATE-004-montant-vendeur.drawio"))
print("ok state")
