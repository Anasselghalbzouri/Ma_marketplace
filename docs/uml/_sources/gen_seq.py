"""SEQ-001..003 — sequence diagrams (CDC v1.1 §8 P2-P5, F007-F011, F014, F022)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from umlkit import *

OUT = os.path.join(os.path.dirname(__file__), "..", "03-sequences")
LEG = ["Flèche pleine = appel / saisie sur la Plateforme ; flèche ouverte = message asynchrone (notification)",
       "Flèche pointillée grise = réponse ; « hors Plateforme » = échange réel sans accès au système (D38)",
       "Ligne de vie grise = acteur externe ; [I] = étape HYPOTHÈSE du CDC ; alt / opt = fragments combinés UML"]

# ------------------------------------------------------------------ SEQ-001
d = Diagram("SEQ-001", "SEQ-001 Commande multi-vendeurs")
d.title("SEQ-001 — Passage d'une commande multi-vendeurs, acceptation, refus ⇒ annulation totale",
        "Source : CDC v1.1 P2, P4, F006, F007, F009, F014 · RG-001/003/008/011b/017/026/028 · CA-F007-1/2, CA-F009-3, "
        "CA-F014-1/2 · D22, D41")
parts = [("cli", "Client", "actor"), ("pf", "Plateforme", "sys"), ("va", "Vendeur A", "actor"),
         ("vb", "Vendeur B", "actor")]
s = Seq(d, parts, x0=40, y0=100, spacing=300)
steps = [
    ("note", "cli", "Pré-condition : Client connecté (RG-028, D41) ;<br>panier avec produits de A et de B (F006)", 50, 290),
    ("msg", "cli", "pf", "validerCommande(adresse, téléphone, note)", "sync", "F007"),
    ("self", "pf", "contrôler adresse à Tanger (RG-001)<br>et stock disponible (F007)", "RG-001"),
    ("frame", "alt", "adresse hors Tanger ou stock insuffisant"),
    ("msg", "pf", "cli", "refus + message ; panier mis à jour (CA-F007-2)", "ret", "CA-F007-2"),
    ("else", "commande valide"),
    ("self", "pf", "créer Commande « En attente d'acceptation »<br>+ 1 SousCommande par vendeur (RG-003 [I])"
             "<br>réserver le stock (RG-017 [I]) ; figer les prix (RG-007)", "RG-003, RG-017"),
    ("msg", "pf", "cli", "confirmation écrite (RG-026 [I], ENF-009)", "ret", "RG-026, CA-F007-1, ENF-009"),
    ("msg", "pf", "va", "notifier nouvelle sous-commande", "async", "CA-F014-1"),
    ("msg", "pf", "vb", "notifier nouvelle sous-commande", "async", "CA-F014-1"),
    ("end",),
    ("msg", "va", "pf", "accepter(sous-commande A)", "sync", "F009"),
    ("frame", "alt", "toutes les sous-commandes acceptées"),
    ("msg", "vb", "pf", "accepter(sous-commande B)", "sync", "F009"),
    ("self", "pf", "Commande → « Confirmée » [I]", "§7"),
    ("msg", "pf", "cli", "notifier : tous les vendeurs ont accepté", "async", "F014, P2.7"),
    ("msg", "va", "pf", "déclarerPrête(sous-commande A)", "sync", "CA-F009-2"),
    ("msg", "vb", "pf", "déclarerPrête(sous-commande B)", "sync", "CA-F009-2"),
    ("note", "pf", "Commande visible « prête » pour l'administrateur → SEQ-002", 46, 380),
    ("else", "Vendeur B refuse (motif) ou ne répond pas dans le délai (RG-011b [I], délai Q19)"),
    ("msg", "vb", "pf", "refuser(sous-commande B, motif)", "sync", "F009"),
    ("self", "pf", "annuler la Commande et toutes ses SousCommandes ;<br>restituer le stock de A et B (RG-008, D22)",
     "RG-008, CA-F009-3"),
    ("msg", "pf", "cli", "notifier annulation : produit non disponible", "async", "CA-F014-2"),
    ("msg", "pf", "va", "notifier annulation de la commande", "async", "CA-F009-3"),
    ("end",),
]
y_end = s.build(steps)
d.legend(40, y_end + 50, LEG, w=620)
d.write(os.path.join(OUT, "SEQ-001-commande-multi-vendeurs.drawio"))

# ------------------------------------------------------------------ SEQ-002
d = Diagram("SEQ-002", "SEQ-002 Collecte livraison encaissement")
d.title("SEQ-002 — Collecte, livraison groupée, encaissement et rapprochement (statuts saisis par l'administrateur)",
        "Source : CDC v1.1 P5, F010, F011 · RG-008/013/020/029 · CA-F010-1/2/3/4 · D19, D38, D44")
parts = [("adm", "Administrateur", "actor"), ("pf", "Plateforme", "sys"), ("sdl", "Société de livraison<br>«externe»", "ext"),
         ("ven", "Vendeur(s)", "actor"), ("cli", "Client", "actor")]
s = Seq(d, parts, x0=40, y0=100, spacing=270)
steps = [
    ("msg", "adm", "pf", "consulterCommandesPrêtes()", "sync", "F010, P5.1"),
    ("msg", "pf", "adm", "commandes dont toutes les sous-commandes sont prêtes", "ret", "CA-F009-2"),
    ("msg", "adm", "sdl", "transmettre la commande (hors Plateforme, C-05)", "async", "D44"),
    ("msg", "adm", "pf", "enregistrerTransmission(commande)", "sync", "RG-029"),
    ("self", "pf", "Commande → « En collecte » (D44)<br>annulation client désormais refusée", "CA-F010-4"),
    ("msg", "sdl", "ven", "collecte des produits (hors Plateforme)", "async", "D19"),
    ("msg", "sdl", "adm", "informe : collecte effectuée (hors Plateforme)", "async", "D38"),
    ("msg", "adm", "pf", "saisirCollecte(sous-commande) ×n", "sync", "RG-029"),
    ("msg", "adm", "pf", "saisirEnLivraison(commande)", "sync", "RG-029"),
    ("msg", "pf", "cli", "notifier : commande en livraison", "async", "F014"),
    ("msg", "sdl", "cli", "livraison groupée unique ; encaissement espèces<br>(produits + frais de livraison) — hors Plateforme",
     "async", "RG-002, RG-008, RG-009"),
    ("msg", "sdl", "adm", "informe : résultat de la livraison", "async", "D38"),
    ("frame", "alt", "livrée et payée"),
    ("msg", "adm", "pf", "saisirLivréeEtPayée(montantEncaissé, dateRéception)", "sync", "CA-F010-1"),
    ("self", "pf", "clôturer la Commande ;<br>créer MontantVendeur « Retenu » par ligne (RG-024)", "CA-F010-1"),
    ("frame", "opt", "montantEncaissé ≠ montant dû", ["adm", "pf"]),
    ("msg", "pf", "adm", "écart signalé (CA-F010-2)", "ret", "CA-F010-2"),
    ("end",),
    ("msg", "pf", "cli", "notifier : commande livrée", "async", "F014"),
    ("else", "client absent, injoignable ou refus"),
    ("msg", "adm", "pf", "saisirÉchec(motif)", "sync", "CA-F010-3"),
    ("self", "pf", "Commande → « Échec de livraison » ; aucun montant dû ;<br>stock restitué (RG-013, RG-017 [I])",
     "RG-013"),
    ("note", "pf", "WARN Q24 : nouvelle tentative, retour des produits aux<br>vendeurs, frais perdus — non définis", 50, 330),
    ("end",),
    ("msg", "sdl", "adm", "remise des fonds encaissés (hors Plateforme) [I]", "async", "RG-020"),
    ("msg", "adm", "pf", "enregistrerRemiseDeFonds(montant, date) [I]", "sync", "RG-020, ENF-008"),
    ("self", "pf", "rapprocher la remise des commandes livrées et payées", "RG-020"),
    ("frame", "opt", "écart entre montants remis et montants dus [I]", ["adm", "pf"]),
    ("msg", "pf", "adm", "écart signalé", "ret", "RG-020"),
    ("end",),
]
y_end = s.build(steps)
d.legend(40, y_end + 50, LEG, w=620)
d.write(os.path.join(OUT, "SEQ-002-collecte-livraison-encaissement.drawio"))

# ------------------------------------------------------------------ SEQ-003
d = Diagram("SEQ-003", "SEQ-003 Retour litige remboursement")
d.title("SEQ-003 — Retour d'un produit : demande, reprise, vérification, litige, remboursement, effet vendeur",
        "Source : CDC v1.1 P3, P4.6, P5.5, F022, F011 · RG-017/019/021/022/025/027/029/030 · CA-F022-1..9, "
        "CA-F011-3/4 · D30-D32, D38-D40, D42, D43")
parts = [("cli", "Client", "actor"), ("pf", "Plateforme", "sys"), ("adm", "Administrateur", "actor"),
         ("sdl", "Société de livraison<br>«externe»", "ext"), ("ven", "Vendeur", "actor")]
s = Seq(d, parts, x0=40, y0=100, spacing=270)
steps = [
    ("note", "cli", "Un retour = une ligne de commande (RG-030, D39) ;<br>plusieurs produits ⇒ plusieurs retours (CA-F022-9)", 50, 300),
    ("msg", "cli", "pf", "demanderRetour(ligne, quantité, motif, moyen)", "sync", "F022"),
    ("self", "pf", "contrôler : ≤ 7 j après réception ; produit non exclu<br>(périssable/personnalisé ou catégorie exclue)",
     "RG-019, D40"),
    ("frame", "alt", "hors délai ou produit exclu"),
    ("msg", "pf", "cli", "retour non proposé + raison (CA-F022-2/3/8)", "ret", "CA-F022-2, CA-F022-3, CA-F022-8"),
    ("else", "éligible"),
    ("frame", "opt", "motif = changement d'avis", ["cli", "pf"]),
    ("msg", "pf", "cli", "frais de retour déduits du remboursement", "ret", "CA-F022-1, D42"),
    ("end",),
    ("msg", "cli", "pf", "confirmer (moyen traçable, CA-F022-4)", "sync", "RG-022"),
    ("self", "pf", "créer Retour « Demandé » (sans acceptation préalable [I])", "P3.4"),
    ("msg", "pf", "ven", "notifier : retour demandé (motif)", "async", "CA-F022-1"),
    ("msg", "pf", "adm", "notifier : retour demandé", "async", "CA-F022-1"),
    ("end",),
    ("msg", "adm", "sdl", "demander la reprise (hors Plateforme)", "async", "D38"),
    ("msg", "sdl", "cli", "reprise du produit (hors Plateforme)", "async", "P3.5"),
    ("msg", "sdl", "ven", "remise du produit (hors Plateforme)", "async", "P3.5"),
    ("msg", "sdl", "adm", "informe : reprise effectuée", "async", "D38"),
    ("msg", "adm", "pf", "saisirReprise(retour)", "sync", "RG-029"),
    ("msg", "pf", "ven", "notifier : retour à vérifier", "async", "F014"),
    ("msg", "ven", "pf", "enregistrerVérification(résultat, motif, remiseEnVente)", "sync", "RG-027, D43"),
    ("frame", "opt", "remiseEnVente = vrai", ["pf", "adm"]),
    ("self", "pf", "restituer le stock (RG-017, D43)", "RG-017"),
    ("end",),
    ("frame", "alt", "conforme"),
    ("self", "pf", "Retour → « Vérifié par le vendeur »", "§7"),
    ("else", "contesté avec motif"),
    ("self", "pf", "Retour → « Litige »", "CA-F022-6"),
    ("msg", "pf", "adm", "notifier : litige à arbitrer", "async", "CA-F022-6"),
    ("msg", "pf", "cli", "notifier : retour contesté", "async", "F014"),
    ("msg", "adm", "pf", "trancher(décision, montantRemboursé, imputationFrais)", "sync", "RG-027 (décision finale [I])"),
    ("end",),
    ("frame", "alt", "remboursement dû (conforme, ou litige en faveur du client)"),
    ("msg", "adm", "pf", "enregistrerRemboursement(montant, moyen, référence, date)", "sync", "CA-F022-5, RG-022"),
    ("self", "pf", "montant = prix − frais si changement d'avis (RG-022) ;<br>Déduction vendeur : annule le montant retenu ou"
             "<br>régularise au prochain reversement ; frais vendeur si défaut", "RG-021, RG-025, CA-F011-3/4"),
    ("msg", "pf", "cli", "notifier : remboursé", "async", "F014"),
    ("msg", "pf", "ven", "notifier : effet sur les montants", "async", "F014, P4.6"),
    ("else", "litige tranché en faveur du vendeur [I]"),
    ("self", "pf", "Retour → « Retour refusé » ; produit renvoyé au client [I]", "F022 exceptions"),
    ("msg", "pf", "cli", "notifier : retour refusé", "async", "F014"),
    ("end",),
    ("note", "pf", "ENF-012 / CA-F022-7 : demande > 12 j sans remboursement ⇒ signalée<br>à l'administrateur ; délai légal "
                   "15 j (R1, à confirmer). Délai de vérification : Q44.", 66, 400),
]
y_end = s.build(steps)
d.legend(40, y_end + 50, LEG, w=620)
d.write(os.path.join(OUT, "SEQ-003-retour-litige-remboursement.drawio"))
print("ok seq")
