# Étape A — Analyse et proposition UML
**Projet** : Marketplace de produits locaux marocains (« la Plateforme »)
**Source unique** : `/opt/data/cahiers/marketplace-produits-locaux-maroc/cahier-des-charges-v1.0.md` (Validé, S9/D36) + `decisions.md` (D1–D36)
**Auteur** : Blueprint (UML Architect) — **Statut : PROPOSITION, en attente d'approbation** (aucun diagramme généré)

Convention de statut de modélisation (en plus des statuts du CDC) :
- **[E] Explicite** : élément CONFIRMÉ dans le CDC.
- **[I] Inféré** : HYPOTHÈSE du CDC, ou déduction de Blueprint ; sera marqué visuellement (stéréotype `«hypothèse»` / note) dans les diagrammes.
- **[S] Suggestion** : SUGGESTION du CDC ; non modélisée sans accord (voir question B1).
- **[U] Non résolu** : MANQUANT ; représenté comme paramètre ou note, jamais comme valeur.

Les ID du CDC (F…, RG-…, ENF-…, US-…, CA-…, D…, Q…) sont conservés tels quels. Les ID ajoutés par Blueprint sont `ACT-`, `UC-`, `ENT-`, `SEQ-`, `ACTIVITY-`, `STATE-`.

---

## 1. Synthèse du projet
Une marketplace B2C multi-vendeurs lancée à Tanger [E D18]. Les vendeurs sont situés à Tanger et dans les communes voisines, avec une inscription libre et gratuite [E D9, D16, D33]. Le panier est multi-vendeurs et donne lieu à une commande unique, répartie en sous-commandes par vendeur [E D12 ; répartition I]. Le paiement se fait uniquement à la livraison, les frais de livraison étant à la charge du client [E D6, D20]. Il n'y a pas de livraison partielle : le refus d'un vendeur annule toute la commande [E D22]. Une société de livraison partenaire collecte, livre en une fois, encaisse et reprend les retours [E D19]. Le client dispose d'un droit de retour de 7 jours après réception, pour tout motif, sauf exclusions légales [E D30, D35]. Le vendeur vérifie le produit retourné et l'administrateur arbitre les litiges ; le remboursement est traçable et intervient dans le délai légal [E D31, D32]. Les fonds vendeurs sont retenus jusqu'à la fin du délai de retour, puis reversés chaque semaine avec régularisation [E D29, D34]. Les clients laissent des avis, et l'administration modère le catalogue.

Périmètre analysé : 15 fonctionnalités MUST (F001–F014, F022), 15 US, 43 CA, 12 ENF. Les fonctionnalités SHOULD/COULD F015–F021 sont toutes des SUGGESTIONS : elles sont **exclues** de la modélisation.

## 2. Acteurs
| ID | Acteur | Type | Statut | Source |
|---|---|---|---|---|
| ACT-001 | Visiteur | Humain, principal | [I] navigation sans compte | §5 |
| ACT-002 | Client | Humain, principal ; spécialise Visiteur [I] | [E] (compte obligatoire [I], Q16) | §5, S1, D6, D18 |
| ACT-003 | Vendeur | Humain, principal | [E] | §5, D3, D9, D31, D33 |
| ACT-004 | Administrateur de la Plateforme | Humain, principal | [E] litiges/remboursements (D31) ; autres responsabilités [I] | §5 |
| ACT-005 | Société de livraison (partenaire) | Système/organisation externe | [E] D19 ; interaction directe avec la Plateforme [U] Q30 | §5 |
| — | Temps (horloge) | Déclencheur d'événements temporels, pas un acteur UML | [I] : expiration du délai de réponse vendeur (RG-011b), fin du délai de retour (RG-024), cycle hebdomadaire (RG-018), alerte du délai légal (CA-F022-7) | — |

Le **canal de notification** (Q23) n'est pas modélisé comme acteur. Les notifications (F014) apparaissent comme messages dans les séquences et comme actions dans les activités et les états.

## 3. Exigences prises en compte
- **Fonctionnelles** : F001–F014, F022 (§10). Les modules M01–M11 servent de paquetages.
- **Règles métier** : RG-001 à RG-027 **+ RG-011b**, soit **28 règles** (le CDC en annonce 27 au §22 ; incohérence de décompte sans effet sur le fond, voir N10).
- **Non fonctionnelles pertinentes pour l'UML** : ENF-007 (cloisonnement, d'où les associations d'accès et les notes), ENF-008 (traçabilité financière, d'où les classes d'historique financier), ENF-009 (conformité, d'où une note dans les diagrammes de commande et de retour), ENF-010 (évolutivité : zones et communes paramétrables), ENF-012 (alerte du délai de remboursement, d'où un événement temporel). ENF-001 à 006 et ENF-011 sont des exigences de qualité **non modélisables en UML** : elles sont tracées dans la matrice avec le statut « hors UML ».

## 4. Cas d'utilisation proposés
| ID | Cas d'utilisation | Acteurs | Exigences | Statut |
|---|---|---|---|---|
| UC-001 | Consulter le catalogue (rechercher, filtrer par catégorie) | Visiteur (hérité par Client) | F004, RG-006 | [I] H1 |
| UC-002 | Consulter une fiche produit (notes, avis, conditions de retour) | Visiteur | F005, RG-019 | [E] (conditions de retour [I]) |
| UC-003 | Gérer le panier multi-vendeurs | Visiteur [I] / Client | F006, RG-003 | [E] |
| UC-004 | S'inscrire / se connecter (client) | Visiteur | F001, RG-014 | [E] / [I] Q16 |
| UC-005 | Passer commande (paiement à la livraison, Tanger) — «include» UC-004 [I Q16] | Client | F007, RG-001/002/007/009/017/026 | [E] |
| UC-006 | Suivre ses commandes | Client | F008 | [I] |
| UC-007 | Annuler sa commande — «extend» UC-006, condition : aucune sous-commande collectée | Client | F008, RG-010 | [I] |
| UC-008 | Demander le retour d'un produit | Client | F022, RG-019/022/025 | [E] |
| UC-009 | Noter et commenter un produit reçu | Client | F012, RG-011 | [E] (restriction [S], B1) |
| UC-010 | S'inscrire comme vendeur et créer sa boutique | Vendeur | F002, RG-004/005/016/018/023 | [E] |
| UC-011 | Gérer ses produits (prix, stock, périssable/personnalisé) | Vendeur | F003, RG-006/007/016/019 | [E] |
| UC-012 | Traiter une sous-commande (accepter / refuser / déclarer prête) | Vendeur | F009, RG-003/008/011b | [E]/[I] |
| UC-013 | Vérifier un produit retourné (conforme / contesté) | Vendeur | F022, RG-027 | [E] |
| UC-014 | Consulter ses montants (retenus, disponibles, reversés, déduits) | Vendeur | F011, RG-012/021/024 | [E] |
| UC-015 | Transmettre les commandes prêtes à la société de livraison | Administrateur ; Société de livraison (secondaire) | F010, P5 | [E] |
| UC-016 | Enregistrer collecte, livraison, encaissement, échec, reprise de retour | Administrateur et/ou Société de livraison (Q30) | F010, F022, RG-008/013 | [E] / [U] Q30 |
| UC-017 | Rapprocher les remises de fonds de la société de livraison | Administrateur | F010, RG-020, ENF-008 | [I] |
| UC-018 | Arbitrer un litige de retour | Administrateur | F022, RG-027 | [E] |
| UC-019 | Enregistrer un remboursement client | Administrateur | F022, RG-021/022, ENF-012 | [E] |
| UC-020 | Enregistrer le reversement hebdomadaire d'un vendeur | Administrateur | F011, RG-018/021/024/025 | [E] |
| UC-021 | Gérer catégories et exclusions, zone clients, communes vendeurs | Administrateur | F013, RG-001/019/023 | [E]/[I] |
| UC-022 | Modérer : masquer un produit, suspendre un vendeur, masquer un avis | Administrateur | F013, RG-015, US-011 | **[S] S-1** (B1) |
| UC-023 | Superviser vendeurs, produits, commandes, retours, montants (y compris l'annulation administrative) | Administrateur | F013, matrice §5 | [I] |

La notification (F014) est transverse et n'est pas un cas d'utilisation : elle apparaît dans SEQ et ACTIVITY.
Les cas « Accepter » et « Refuser » sont regroupés dans UC-012 pour éviter un cas d'utilisation par bouton.

## 5. Entités du domaine (diagramme de classes)
Seuls les attributs **cités** dans le CDC seront portés. Les types et multiplicités non précisés seront notés `[I]`.

| ID | Classe | Attributs clés (source) | Statut |
|---|---|---|---|
| ENT-001 | Client | nom, téléphone (RG-014), e-mail [U] | [E] |
| ENT-002 | Vendeur | identité/raison sociale, téléphone, commune, modeReversement, coordonnéesBancaires (si virement), statut actif/suspendu [S-1] | [E] (Q22 [U]) |
| ENT-003 | Boutique | nom, présentation, adresseCollecte ; 1 boutique par vendeur [I] | [E] |
| ENT-004 | Produit | nom, description, photos (≥1 [I]), prix MAD [I], stock, origine [I], périssable, personnalisé, publié/masqué | [E] |
| ENT-005 | Catégorie | nom, exclueDuRetour [I] | [E]/[I] |
| ENT-006 | Commune (zone vendeurs) / Ville desservie (zone clients) | nom, autorisée | [E] RG-001, RG-023 |
| ENT-007 | Panier / LignePanier | quantité | [E] |
| ENT-008 | Commande | statut, adresse de livraison (Tanger), téléphone, note de livraison, fraisLivraison (forfait unique [I]), total, montantEncaissé, dateRéception | [E] |
| ENT-009 | SousCommande | statut, motifRefus | [I] (répartition) |
| ENT-010 | LigneCommande | quantité, prixUnitaire figé (RG-007) | [I] |
| ENT-011 | Retour | quantité, motif, photo [I], moyenRemboursement, statut, dateDemande | [E] (granularité : B3) |
| ENT-012 | Vérification / Contestation | résultat (conforme/contesté), motif | [E] RG-027 |
| ENT-013 | Litige (décision) | décision, montantRemboursé, imputationFrais ; décision finale [I] | [E] |
| ENT-014 | Remboursement | montant, moyen, référence, date | [E] RG-022, CA-F022-5 |
| ENT-015 | FraisDeRetour | montant [U Q45], imputéÀ (client/vendeur) | [E] RG-025 |
| ENT-016 | MontantVendeur | montant, statut (retenu/disponible/reversé/déduit) ; porté par la LigneCommande [I] (RG-024 retient le produit en retour) | [E] principe |
| ENT-017 | Déduction / Régularisation | montant, origine (remboursement, frais de retour) | [E] RG-021 |
| ENT-018 | Reversement | date, montant, mode (virement/espèces), preuve de remise [I] | [E] RG-018, CA-F011-2 |
| ENT-019 | RemiseDeFonds (société de livraison) + Écart | montant, date ; écart signalé | [I] RG-020, CA-F010-2 |
| ENT-020 | Avis | note 1–5 [I], commentaire, masqué [S] | [E] |
| ENT-021 | SociétéDeLivraison | — (non choisie, C-05) | [E] |
| Énumérations | StatutCommande, StatutSousCommande, StatutRetour, StatutMontant, MotifRetour {changement d'avis, défectueux, incorrect, non conforme}, ModeReversement {virement, espèces}, MoyenRemboursement {virement, autre moyen traçable [U Q42]} | | |

Associations principales : Vendeur 1–1 Boutique ; Boutique 1–* Produit ; Produit *–1 Catégorie ; Client 1–* Commande ; Commande 1–1..* SousCommande (composition) ; SousCommande *–1 Vendeur ; SousCommande 1–1..* LigneCommande (composition) ; LigneCommande *–1 Produit ; LigneCommande 1–0..* Retour [I] ; Retour 1–0..1 Vérification, 0..1 Litige, 0..1 Remboursement, 0..1 FraisDeRetour ; LigneCommande 1–1 MontantVendeur [I] ; Vendeur 1–* Reversement ; Reversement 1–* MontantVendeur / Déduction ; RemiseDeFonds *–* Commande [I] ; Client 1–* Avis ; Avis *–1 Produit, *–1 Commande (RG-011).
**Pas d'opérations** dans le modèle du domaine : le CDC décrit des comportements métier, pas des responsabilités de classes. Ces comportements sont portés par les séquences et les états.

## 6. Diagrammes proposés (15 fichiers `.drawio`)
| ID | Type | Contenu | Exigences couvertes |
|---|---|---|---|
| UC-DIAG-01 | Cas d'utilisation | Achat : Visiteur/Client (UC-001 à 009) | F001, F004–F008, F012, F022 |
| UC-DIAG-02 | Cas d'utilisation | Vente : Vendeur (UC-010 à 014) | F002, F003, F009, F011, F022 |
| UC-DIAG-03 | Cas d'utilisation | Exploitation : Administrateur et Société de livraison (UC-015 à 023) | F010, F011, F013, F022 |
| CLASS-01 | Classes | Domaine : comptes, catalogue, panier, commandes, zones, avis | F001–F010, F012, F013 |
| CLASS-02 | Classes | Domaine : retours, remboursements, litiges, montants vendeurs, reversements, remises de fonds | F010, F011, F022, ENF-008 |
| SEQ-001 | Séquence | Passage d'une commande multi-vendeurs + acceptation ; `alt` refus/expiration, d'où l'annulation totale | F006, F007, F009, F014, RG-003/008/011b/017/026, CA-F007-1, CA-F009-3, CA-F014-2 |
| SEQ-002 | Séquence | Collecte, livraison groupée, encaissement, rapprochement ; `alt` échec / écart | F010, RG-008/013/020, CA-F010-1..3 |
| SEQ-003 | Séquence | Retour : demande, reprise, vérification ; `alt` litige ; remboursement ; déduction vendeur | F022, F011, RG-021/022/025/027, CA-F022-1/5/6 |
| ACTIVITY-001 | Activité (couloirs : Client, Plateforme, Vendeur, Société de livraison, Admin) | Cycle de commande de bout en bout | P2, P4, P5, F007–F010 |
| ACTIVITY-002 | Activité (couloirs) | Processus de retour avec éligibilité (7 j, exclusions), frais, vérification, litige, délai légal | P3, F022, RG-019/022/025/027, ENF-012 |
| ACTIVITY-003 | Activité | Retenue, mise à disposition et calcul du reversement hebdomadaire avec régularisation | F011, RG-012/018/021/024/025, CA-F011-1..5 |
| STATE-001 | États | Commande | §7 cycles, RG-008/010/013 |
| STATE-002 | États | SousCommande | §7, RG-011b |
| STATE-003 | États | Retour | §7, RG-027, ENF-012 |
| STATE-004 | États | MontantVendeur | §7, RG-021/024 |

**Non proposés** : composants et déploiement (C-07 : aucune architecture spécifiée) ; machines à états Produit/Vendeur (simples combinaisons de booléens couvertes par RG-006 et les classes). Le recouvrement entre ACTIVITY-002 et SEQ-003 est volontaire : le premier montre les décisions métier, le second les échanges entre acteurs. SEQ-003 peut être retiré si vous préférez réduire le livrable.

Organisation des fichiers : `/opt/data/uml/marketplace-produits-locaux-maroc/{01-cas-utilisation,02-classes,03-sequences,04-activites,05-etats}/<ID>.drawio`, plus `rapport-tracabilite-validation.md`.

## 7. Décisions de modélisation importantes
1. Les cycles de vie §7 (HYPOTHÈSE) sont repris tels quels pour STATE-001 à 004. Les transitions et événements absents du CDC sont marqués [I].
2. La commande est « close » au statut *Livrée et payée* (CA-F010-1). Le retour est un objet distinct rattaché à la ligne de commande, et non un nouvel état de la commande.
3. Les délais non chiffrés (Q19 réponse vendeur, Q44 vérification, délai légal de 15 j [R1]) sont modélisés comme des **événements temporels paramétrés** (`after(délaiRéponseVendeur)`), sans valeur.
4. La valeur du montant vendeur est suivie **par ligne de commande**, car RG-024 n'en retient qu'une partie en cas de retour en cours [I].
5. Le Client spécialise le Visiteur (généralisation d'acteurs) [I].
6. Les SUGGESTIONS (F015–F021, liste d'attente vendeurs hors zone, confirmation téléphonique, masquage de l'adresse client pour le vendeur) **ne sont pas modélisées**.

## 8. Questions
### Bloquantes : elles changent la structure des diagrammes. Je propose un choix par défaut pour chacune.
- **B1 — SUGGESTIONS couvertes par des critères MUST.** S-1 (RG-015 : masquer produit / suspendre vendeur / masquer avis) et RG-011 (avis réservés aux produits reçus) sont étiquetés SUGGESTION, alors que F013/F012 sont MUST, que US-011 les demande et que CA-F013-1/2, CA-F004-2 et CA-F012-2 les testent dans un document validé. *Défaut proposé* : les modéliser, marqués « SUGGESTION couverte par CA validé — à confirmer ».
- **B2 — Q30 : la société de livraison agit-elle directement sur la Plateforme ?** Cela détermine si ACT-005 est un acteur principal de UC-016 et une ligne de vie active dans SEQ-002/003. *Défaut* : représenter les deux variantes, la société de livraison en direct et l'administrateur en saisie, avec une note Q30.
- **B3 — Granularité du retour.** Une demande peut couvrir « un ou plusieurs produits » (F022). Faut-il un objet Retour par produit (ligne de commande), chacun vérifié et remboursé séparément, ou une demande unique regroupant plusieurs lignes ? *Défaut* : un Retour par ligne de commande, avec quantité et motif propres.
- **B4 — Source de l'exclusion du droit de retour.** Elle relève à la fois d'un attribut du produit (F003 : périssable/personnalisé, renseigné par le vendeur) et des catégories (F013 : « catégories, dont exclusions de retour », gérées par l'administrateur). *Défaut* : les deux, le produit étant exclu si l'un ou l'autre l'indique.
- **B5 — Q16 : compte client obligatoire pour commander ?** Cela décide du lien «include» entre UC-005 et UC-004. *Défaut* : obligatoire (hypothèse du CDC).

### Non bloquantes : je les note comme avertissements (WARN) dans les diagrammes.
- N1 Q19 / Q44 : valeurs des délais (événements paramétrés).
- N2 Q24 : suite d'un échec de livraison (nouvelle tentative, retour des produits aux vendeurs, stock). STATE-001 s'arrête en *Échec de livraison*, avec une note.
- N3 Q38 : solde vendeur négatif (report signalé [I]).
- N4 Q40 / Q42 / Q45 / Q27 : montants et moyens. Ce sont des attributs sans valeur.
- N5 : déduction des frais de retour du remboursement (changement d'avis) [I] ou facturation séparée.
- N6 RG-017 : qui décide qu'un produit retourné est « remis en vente » (restitution du stock) ? Non spécifié.
- N7 : l'événement qui fait passer la commande à *En collecte* (transmission à la société de livraison ou première collecte ?) n'est pas défini.
- N8 Q39 : identité du « fournisseur » au sens de la loi 31-08. Sans effet structurel, une note est portée sur la confirmation écrite (RG-026).
- N9 F013 : sort des sous-commandes et retours d'un vendeur suspendu, laissé à la décision de l'administrateur (UC-023).
- N10 : le §22 annonce « 27 règles métier » alors que le CDC en définit 28 (RG-001 à RG-027 + RG-011b). Simple coquille à corriger en v1.1.

## 9. Traçabilité préliminaire (fonctionnalités → diagrammes)
| Fonctionnalité | UC | Classes | Séquence | Activité | États |
|---|---|---|---|---|---|
| F001 | UC-004 | CLASS-01 | (SEQ-001 pré-condition) | — | — |
| F002 | UC-010 | CLASS-01 | — | — | — |
| F003 | UC-011 | CLASS-01 | — | — | — |
| F004 | UC-001 | CLASS-01 | — | — | — |
| F005 | UC-002 | CLASS-01 | — | — | — |
| F006 | UC-003 | CLASS-01 | SEQ-001 | ACTIVITY-001 | — |
| F007 | UC-005 | CLASS-01 | SEQ-001 | ACTIVITY-001 | STATE-001 |
| F008 | UC-006, 007 | CLASS-01 | — | ACTIVITY-001 | STATE-001 |
| F009 | UC-012 | CLASS-01 | SEQ-001 | ACTIVITY-001 | STATE-002 |
| F010 | UC-015, 016, 017 | CLASS-01/02 | SEQ-002 | ACTIVITY-001 | STATE-001/002 |
| F011 | UC-014, 020 | CLASS-02 | SEQ-003 (déduction) | ACTIVITY-003 | STATE-004 |
| F012 | UC-009 | CLASS-01 | — | — | — |
| F013 | UC-021, 022, 023 | CLASS-01 | — | — | — |
| F014 | (transverse) | — | SEQ-001/002/003 | ACTIVITY-001/002 | actions d'entrée |
| F022 | UC-008, 013, 016, 018, 019 | CLASS-02 | SEQ-003 | ACTIVITY-002 | STATE-003 |

Après génération, la matrice complète (RG, ENF, US, CA) figurera dans le rapport de l'étape B.

---

## 10. Décisions du porteur (réponses dans le chat Blueprint)
Réponse : `b1-a b2-a b3-a b4-c b5-a n5-a n6-a n7-a`

| # | Décision | Effet sur le modèle |
|---|---|---|
| B1 | Modération (RG-015, S-1) et avis réservés aux produits reçus (RG-011) **confirmés** | UC-022 modélisé comme confirmé ; contrainte RG-011 sur Avis |
| B2 | **L'administrateur seul** saisit les statuts de collecte, livraison, encaissement (et reprise), à partir des informations de la société de livraison | ACT-005 = acteur secondaire, hors Plateforme ; UC-016 → Administrateur ; ligne de vie Société de livraison sans échange direct avec la Plateforme dans SEQ-002/003 |
| B3 | **Un retour par produit** (ligne de commande), vérifié et remboursé séparément | Retour 0..* par LigneCommande |
| B4 | Exclusion du droit de retour : **vendeur (produit) et administrateur (catégorie)** | Produit exclu si l'un ou l'autre ; garde dans ACTIVITY-002 |
| B5 | **Compte obligatoire** pour commander | UC-005 «include» UC-004 (authentification) |
| N5 | Frais de retour (changement d'avis) **déduits du remboursement** | Montant remboursé = prix − frais de retour |
| N6 | Le **vendeur** remet en vente le produit retourné, après vérification | Restitution du stock déclenchée par le vendeur (RG-017) |
| N7 | « En collecte » = **commande confiée à la société de livraison** | Transition STATE-001 sur l'événement de transmission |

Statut : décisions à intégrer par Product Analyst dans la v1.1. Génération des diagrammes (étape B) : **non encore autorisée**.

---
**Mise à jour (étape B)** : génération autorisée par le porteur (« go » / « continue the work »), sur la base de la v1.1 Brouillon, avec réserve. 15 diagrammes générés et validés : voir `rapport-tracabilite-validation.md`.
