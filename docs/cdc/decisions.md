# Journal des décisions — Plateforme e-commerce de produits locaux marocains

Sources :
- S1 — Message utilisateur initial (chat), description de l'idée
- S2 — Réponses utilisateur au tour 1 de questions (chat) : « q1-a q2-d q3-c q4-market q5-a »

| ID | Date | Décision | Statut | Source |
|---|---|---|---|---|
| D1 | session 1 | Plateforme e-commerce dédiée aux produits locaux marocains | CONFIRMÉ | S1 |
| D2 | session 1 | Les clients parcourent les produits, ajoutent au panier et passent commande | CONFIRMÉ | S1 |
| D3 | session 1 | Plusieurs vendeurs locaux ajoutent et gèrent leurs propres produits (marketplace) | CONFIRMÉ | S1 |
| D4 | session 1 | Finalité : aider les petites entreprises locales à vendre en ligne | CONFIRMÉ | S1 |
| D5 | session 1 | Démarrage simple, extensible ultérieurement | CONFIRMÉ | S1 |
| D6 | session 1 | Paiement au démarrage : paiement à la livraison uniquement | CONFIRMÉ | S2 (Q1-a) |
| D7 | session 1 | Livraison : modèle mixte, selon le vendeur (expédition par le vendeur / livraison organisée par la plateforme / retrait chez le vendeur) | CONFIRMÉ | S2 (Q2-d) |
| D8 | session 1 | Problème principal : manque de visibilité des petits vendeurs | CONFIRMÉ | S2 (Q5-a) |

| D9 | session 1 | Admission des vendeurs : inscription libre, vente immédiate (sans validation préalable) | CONFIRMÉ | S3 (Q3-a) |
| D10 | session 1 | Marché : Maroc + Marocains résidant à l'étranger | CONFIRMÉ | S3 (Q4-b) |
| D11 | session 1 | Livraison au lancement : expédition par le vendeur + retrait chez le vendeur ; livraison organisée par la plateforme plus tard | CONFIRMÉ | S3 (Q6-a) |
| D12 | session 1 | Panier multi-vendeurs : la plateforme livre l'ensemble et encaisse une seule fois | CONFIRMÉ (en conflit avec D11) | S3 (Q7-c) |
| D13 | session 1 | Levier de visibilité retenu pour la V1 : avis et notes clients | CONFIRMÉ | S3 (Q8-e) |

Sources (suite) :
- S3 — Réponses utilisateur au tour 2 (chat) : « q3-a q4-b q6-a q7-c q8-e »
- S4 — Réponses utilisateur au tour 3 (chat) : « The platform delivers from day one, c2-Morocco only for the first version, q9-Free at launch, decide later »

| ID | Date | Décision | Statut | Source |
|---|---|---|---|---|
| D14 | session 1 | C1 résolue : la plateforme organise la livraison dès le lancement et encaisse le paiement à la livraison. **Remplace D11** (D12 maintenu) | CONFIRMÉ | S4 (C1-b) |
| D15 | session 1 | C2 résolue : V1 = Maroc uniquement (clients et livraison) ; diaspora en phase ultérieure. **Précise D10** | CONFIRMÉ | S4 (C2-c) |
| D16 | session 1 | Modèle de revenu : gratuit pour les vendeurs au lancement, à décider plus tard | CONFIRMÉ | S4 (Q9-b) |

Statut révisé : D11 → REMPLACÉE par D14 ; D10 → phase ultérieure (V1 limitée au Maroc par D15).

| ID | Date | Décision | Statut | Source |
|---|---|---|---|---|
| D17 | session 1 | Vision produit acceptée ; rédaction du Cahier des Charges autorisée avec points non tranchés en HYPOTHÈSE → v0.1 Brouillon | CONFIRMÉ | S5 (« go ahead now ») |

Points ouverts suivants : voir §22 du cahier-des-charges-v0.2.md.

Sources (suite) :
- S6 — Réponses utilisateur sur la v0.1 (chat) : « Q18-TANGER the first city, delivery company, Q14-the customer, Q13-bank transfer, cash, Q20-Non, Q15-yes return Product »

| ID | Date | Décision | Statut | Source |
|---|---|---|---|---|
| D18 | session 1 | Zone de lancement : Tanger (première ville) ; précise D15 | CONFIRMÉ | S6 (Q18) |
| D19 | session 1 | Livraison, collecte et encaissement confiés à une société de livraison partenaire | CONFIRMÉ | S6 (Q18) |
| D20 | session 1 | Frais de livraison à la charge du client | CONFIRMÉ | S6 (Q14) |
| D21 | session 1 | Reversement aux vendeurs par virement bancaire ou en espèces (fréquence non précisée) | CONFIRMÉ | S6 (Q13) |
| D22 | session 1 | Pas de livraison partielle : si un vendeur refuse, la commande entière est annulée | CONFIRMÉ | S6 (Q20 « Non ») |
| D23 | session 1 | Les clients peuvent retourner un produit après livraison (conditions à définir) | CONFIRMÉ | S6 (Q15) |

→ Cahier des Charges v0.2 (Brouillon). Nouvelles questions : Q26–Q32.

Sources (suite) :
- S7 — Propositions du porteur sur la v0.2 (chat) : Q26, Q28, Q29, Q31/Q32, Q13
- R1 — Référence réglementaire (non une source de besoin) : MCINET, Guide du consommateur, loi 31-08, contrat conclu à distance : rétractation 7 jours, remboursement ≤ 15 jours

| ID | Date | Décision | Statut | Source |
|---|---|---|---|---|
| D24 | session 1 | Vendeurs V1 : Tanger et environs ; extension à tout le Maroc ensuite | CONFIRMÉ | S7 (Q26) |
| D25 | session 1 | Délai de retour : 7 jours après la livraison, sous réserve des règles légales | CONFIRMÉ | S7 (Q28) |
| D26 | session 1 | Motifs de retour : défectueux, incorrect, non conforme à la description ; exclusions (alimentaire, cosmétique…) à définir conformément à la réglementation | CONFIRMÉ (changement d'avis : voir C3) | S7 (Q29) |
| D27 | session 1 | Frais de retour à la charge du vendeur en cas d'erreur ou de défaut ; cas du changement d'avis à préciser | CONFIRMÉ | S7 (Q31) |
| D28 | session 1 | Remboursement client traçable, de préférence par virement ; délais et procédure à définir | CONFIRMÉ | S7 (Q32) |
| D29 | session 1 | Retenue des fonds vendeurs jusqu'à la fin du délai de retour ; régularisation des remboursements, y compris après reversement | CONFIRMÉ | S7 (Q13) |

- C3 CONTRADICTOIRE (ouverte) — D26 (défauts uniquement) vs D27 (évoque le changement d'avis) vs R1 (rétractation légale 7 jours sans justification)

→ Cahier des Charges v0.3 (Brouillon). Nouvelles questions : C3, Q33, Q35–Q39, Q13b.

Sources (suite) :
- S8 — Réponses du porteur sur la v0.3 (chat) : C3, Q36, Q37, Q33, Q13b, Q35

| ID | Date | Décision | Statut | Source |
|---|---|---|---|---|
| D30 | session 1 | C3 résolue : retour dans les 7 jours suivant la réception pour tout motif, y compris changement d'avis, sauf exceptions légales ; frais de retour au client (changement d'avis) ou au vendeur (défaut/erreur) lorsque la loi le prévoit ; validation juridique avant lancement | CONFIRMÉ | S8 (C3-a) |
| D31 | session 1 | Le vendeur vérifie le produit retourné ; l'administrateur supervise les litiges et les remboursements ; remboursement dans le délai légal | CONFIRMÉ | S8 (Q36) |
| D32 | session 1 | Remboursement par virement bancaire ou autre moyen traçable et légalement autorisé pour les clients sans compte bancaire | CONFIRMÉ | S8 (Q37) |
| D33 | session 1 | Vendeurs limités à Tanger et aux communes voisines ; liste exacte définie avant lancement (précise D24) | CONFIRMÉ | S8 (Q33) |
| D34 | session 1 | Reversements vendeurs hebdomadaires, uniquement des fonds disponibles après retenue et après déduction des remboursements | CONFIRMÉ | S8 (Q13b) |
| D35 | session 1 | Exclusions de retour uniquement si la loi le permet : périssables, personnalisés ; cosmétiques ouverts à confirmer juridiquement | CONFIRMÉ | S8 (Q35) |

→ Cahier des Charges v0.4 (Brouillon). Aucune contradiction ouverte. Nouvelles questions : Q40–Q45.

Sources (suite) :
- S9 — Validation du porteur sur la v0.4 (chat) : « passe au statut validé »

| ID | Date | Décision | Statut | Source |
|---|---|---|---|---|
| D36 | session 1 | Cahier des Charges validé par le porteur du projet ; passage au statut Validé (v1.0, sans changement de fond par rapport à la v0.4). Les points du §22 restent à régler avant le lancement ; validation juridique obligatoire avant lancement. | CONFIRMÉ | S9 |

→ Cahier des Charges v1.0 (**Validé**). Prêt à être transmis aux agents d'ingénierie.

Sources (suite) :
- S10 — Réponses du porteur aux questions de l'étape A de Blueprint, données dans le chat Blueprint : « b1-a b2-a b3-a b4-c b5-a n5-a n6-a n7-a » ; transmises par Blueprint, vérifiées au §10 de /opt/data/uml/marketplace-produits-locaux-maroc/00-etape-A-analyse-et-proposition.md

| ID | Date | Décision | Statut | Source |
|---|---|---|---|---|
| D37 | session 1 | Modération (masquer produit, suspendre vendeur, masquer avis — RG-015) et avis réservés aux produits reçus (RG-011) confirmés (résout C4/B1) | CONFIRMÉ | S10 (b1-a) |
| D38 | session 1 | Seul l'administrateur saisit les statuts de collecte, livraison, encaissement et reprise, à partir des informations de la société de livraison ; celle-ci n'a pas d'accès à la Plateforme (résout Q30) | CONFIRMÉ | S10 (b2-a) |
| D39 | session 1 | Un retour par produit (ligne de commande), vérifié et remboursé séparément | CONFIRMÉ | S10 (b3-a) |
| D40 | session 1 | Exclusion du droit de retour : par le produit (signalé par le vendeur) et par la catégorie (administrateur) ; exclu si l'un ou l'autre | CONFIRMÉ | S10 (b4-c) |
| D41 | session 1 | Compte client obligatoire pour commander (résout Q16) | CONFIRMÉ | S10 (b5-a) |
| D42 | session 1 | Changement d'avis : frais de retour déduits du remboursement | CONFIRMÉ | S10 (n5-a) |
| D43 | session 1 | Remise en vente d'un produit retourné décidée par le vendeur après vérification | CONFIRMÉ | S10 (n6-a) |
| D44 | session 1 | Une commande passe « En collecte » à sa transmission à la société de livraison | CONFIRMÉ | S10 (n7-a) |

→ Cahier des Charges v1.1 (Brouillon, en attente de revalidation). Corrige aussi le décompte des règles métier (N10).

Sources (suite) :
- S11 — Validation du porteur du projet (Anass) sur la v1.1, écrite dans le chat Product Analyst le 2026-10-12 : « v1.1 validée »

| ID | Date | Décision | Statut | Source |
|---|---|---|---|---|
| D45 | 2026-10-12 | Cahier des Charges v1.1 validé par le porteur du projet (Anass) ; passage au statut Validé, sans changement de fond. La v1.1 remplace la v1.0 comme référence validée. Les points du §22 restent à régler avant le lancement ; validation juridique obligatoire avant lancement (C-08). | CONFIRMÉ | S11 |

→ Cahier des Charges v1.1 (**Validé**). Prêt à être transmis aux agents d'ingénierie.

## Points ouverts (avant synthèse de vision — historique)
- Q12 — La livraison plateforme couvre-t-elle toutes les commandes, ou les modes vendeur/retrait restent-ils possibles ? — HYPOTHÈSE : toutes les commandes passent par la plateforme
- Q13 — Reversement aux vendeurs de l'argent encaissé (conséquence de D14) — MANQUANT (délai/fréquence)
- Q14 — Frais de livraison : qui paie ? — MANQUANT
- Q10 — Profil des vendeurs — MANQUANT (non bloquant)
- Q11 — Langues — MANQUANT
- H1 — Recherche / catégories incluses dans « parcourir » (D2) — HYPOTHÈSE
- S-1 — Admin peut masquer un produit / suspendre un vendeur non local — SUGGESTION
