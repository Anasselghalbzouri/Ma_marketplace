# Plan d'implémentation — marketplace-produits-locaux-maroc
Version : 1 — Date : 2026-10-12 — Statut : Proposition (non validé)
Auteur : Compass (Implementation Planner). Demande : « Plan request » de Blueprint, sur instruction d'Anass.

Ce plan est une proposition. @user décide des changements de statut. Aucune tâche n'a été exécutée. Aucune vérification n'a été faite.

## 1. Sources

| Fichier | Statut (validé par @user ?) |
|---|---|
| /opt/data/cahiers/marketplace-produits-locaux-maroc/cahier-des-charges-v1.1.md | Validé — Anass, 2026-10-12 (S11, D45) |
| /opt/data/cahiers/marketplace-produits-locaux-maroc/decisions.md (D1–D45) | Validé (journal du porteur) |
| /opt/data/uml/marketplace-produits-locaux-maroc/ — 15 diagrammes (UC-DIAG-01..03, CLASS-01..02, SEQ-001..003, ACTIVITY-001..003, STATE-001..004) | Approuvés — Anass, 2026-10-12 (transmis par Blueprint) |
| /opt/data/uml/marketplace-produits-locaux-maroc/rapport-tracabilite-validation.md | Lu. Réserve « v1.1 Brouillon » caduque depuis D45 |
| /opt/data/uml/marketplace-produits-locaux-maroc/00-etape-A-analyse-et-proposition.md (§10 décisions B1–B5, N5–N7) | Lu. Décisions reprises dans D37–D44 |
| Backlog (Atlas), conception écrans (Iris), architecture et contrats d'API (Forge) | Absents — voir M-01, M-02, M-03 |
| Dépôt de code | Aucun. Aucune commande de test trouvée |

Lecture des diagrammes : libellés et propriétés `req` extraits des fichiers .drawio (CLASS-01/02, STATE-001..004) ; autres diagrammes via la matrice du rapport §3.

## 2. Constats

| ID | Type | Constat | Source | Impact | Responsable | Tâches touchées |
|---|---|---|---|---|---|---|
| K-01 | CONFIRMÉ | CDC v1.1 validé ; il remplace la v1.0. La réserve « Brouillon » du rapport UML est caduque. | CDC §23, D45 | Aucun | — | toutes |
| K-02 | CONFIRMÉ | 15 diagrammes approuvés. 0 erreur structurelle. W-OVERLAP SEQ-001/002/003 acceptés. | Rapport §1, message Blueprint | Aucun | — | — |
| K-03 | CONFIRMÉ | Périmètre MVP = F001–F014 + F022 (MUST). F015–F021 exclus (SUGGESTION). | CDC §16, rapport §2 | Pas de tâche SHOULD/COULD | — | — |
| K-04 | CONFIRMÉ | Aucune contradiction ouverte dans le CDC. Aucune contradiction trouvée entre CDC et UML. | CDC §22 | — | — | — |
| M-01 | MANQUANT | Aucune architecture : stack, hébergement, découpage. C-07 : aucune contrainte imposée. | CDC C-07 | Toutes les tâches techniques attendent T-001 | Architecte (Forge) | T-001 → toutes |
| M-02 | MANQUANT | Aucun schéma physique ni contrat d'API. | — | Le frontend ne démarre qu'après CP-1 | Architecte (Forge) | T-002, T-003 |
| M-03 | MANQUANT | Aucune conception d'écrans (Iris) ni backlog (Atlas). Les stories US-001..015 du CDC servent de backlog. | — | Écrans construits depuis les parcours P1–P5 (HYPOTHÈSE) ; risque de reprise | Iris / Atlas | tâches Frontend |
| M-04 | MANQUANT | Aucun dépôt, donc aucune commande de test. | — | Vérifications : « commande à définir » | Release / Architecte | toutes |
| M-05 | MANQUANT | Canal des notifications (Q23). | CDC F014, Q23 | Envoi externe impossible | @user | T-010 (bloquée), T-015 |
| M-06 | MANQUANT | E-mail client obligatoire ou non. Moyen de récupération d'accès non défini. | CDC F001 | Récupération d'accès impossible | @user / Product Analyst | T-015 (bloquée) |
| M-07 | MANQUANT | Suite d'un échec de livraison : nouvelle tentative, retour des produits, frais (Q24). STATE-001 : état final provisoire. | RG-013, Q24 | Traitement post-échec non spécifié | @user | T-040 (bloquée) |
| M-08 | MANQUANT | Délai de vérification vendeur (Q44) et suite en cas de dépassement. | RG-027, Q44 | Décision admin à défaut non spécifiée | @user | T-046 (bloquée) |
| M-09 | MANQUANT | Langues de l'interface (Q11). | ENF-001 | Traductions impossibles | @user | T-013 (bloquée) |
| U-01 | MANQUANT (UML) | STATE-003 : pas de transition after(délaiVérification). La note n2 dit « transition non dessinée faute de cible ». | STATE-003 n2 | Comportement à défaut non modélisé | Blueprint (après décision Q44) | T-046 (bloquée) |
| U-02 | MANQUANT (UML) | STATE-001 : pas de transition d'annulation par l'administrateur. F013 prévoit qu'il décide du sort des sous-commandes d'un vendeur suspendu (N9, UC-023). | STATE-001 t2, F013 | Annulation admin non modélisée | Blueprint | T-060 (bloquée) |
| U-03 | HYPOTHÈSE | Historisation des saisies de statut (qui, quand) exigée par ENF-008. Aucune classe d'historique dans CLASS-01/02. Journal d'audit transverse prévu. | ENF-008, CLASS-02 | Si faux : modèle d'audit à revoir | Architecte / Blueprint | T-008 |
| H-01 | HYPOTHÈSE | Panier accessible sans compte, rattaché au client après connexion. | §5, CLASS-01 n_warn, CA-F001-3 | Si faux : panier réservé aux clients | @user | T-026 |
| H-02 | HYPOTHÈSE | Absence de réponse vendeur dans le délai = refus. | RG-011b | Si faux : retirer T-034 | @user | T-034 |
| H-03 | HYPOTHÈSE | Étapes des cycles de vie §7, sauf « En collecte » (D44) et Montant vendeur (D29, D34). | STATE-001..003 [I] | Si faux : machines à états à revoir | @user | T-027, T-043 |
| H-04 | HYPOTHÈSE | MontantVendeur porté par LigneCommande. | CLASS-02 [I] | Si faux : schéma et calculs à revoir | Blueprint / @user | T-036 |
| H-05 | HYPOTHÈSE | RemiseDeFonds et Écart. | CLASS-02 [I], RG-020 | Si faux : retirer T-039 | @user | T-039 |
| H-06 | HYPOTHÈSE | Une boutique par vendeur. Client spécialise Visiteur. | CLASS-01, UC-DIAG-01 [I] | Si faux : schéma à revoir | @user | T-006, T-016 |
| H-07 | HYPOTHÈSE | Solde vendeur négatif : reporté et signalé à l'admin (Q38). | F011, ACTIVITY-003 | Si faux : règle de calcul à revoir | @user | T-054 |
| H-08 | HYPOTHÈSE | Valeurs non fixées traitées comme paramètres : Q19, Q27, Q40, Q42, Q44, Q45, délai légal 15 j, alerte 12 j, jour du reversement. | CDC §22 (« le développement peut prévoir les paramètres ») | Valeurs à saisir avant lancement | @user | T-007 |
| H-09 | HYPOTHÈSE | Champs vendeur obligatoires (Q22) : ceux listés en F002. | F002 | Si faux : formulaire à compléter | @user | T-016 |
| H-10 | HYPOTHÈSE | Contenu de la confirmation écrite (RG-026). Identité du « fournisseur » (Q39) à valider juridiquement. | RG-026, Q39, C-08 | Gabarit à ajuster | @user (juriste) | T-029 |
| H-11 | HYPOTHÈSE | Valeurs ENF-003/004/005 ; volumes ENF-006 MANQUANT (Q21). | CDC §13 | Dimensionnement incertain | @user | T-001, T-067, T-068, T-069 |
| H-12 | HYPOTHÈSE | Q43 (cosmétiques ouverts) et Q41 (communes) : données saisies par l'admin, sans développement propre. | RG-019, RG-023 | Aucun code ; saisie avant lancement | @user | T-017, T-070 |
| H-13 | CONFIRMÉ | Validation juridique obligatoire avant lancement (C-08). | D30, D45 | Porte de lancement | @user | T-070 |

## 3. Tâches

Convention. Chaque tâche Backend inclut ses tests automatisés (unitaires + fonctionnels). Commande de test : à définir (M-04). « CP-n » = point d'intégration.

### Fondations

### T-001 — Dossier d'architecture
- Story : transverse · ENF-002, ENF-004, ENF-005, ENF-006, ENF-007, ENF-010 · C-07
- Rôle : Architecte
- Dépend de : —
- Parallélisable avec : T-070
- Fichiers/modules : à définir
- Entrées : CDC v1.1, CLASS-01/02, rapport UML
- Sorties : stack, découpage en modules M01–M11, hébergement, stratégie de tâches planifiées et de stockage des photos
- Vérification : document validé par @user ; chaque ENF citée a une réponse
- Priorité : Must · Estimation : M (estimation)
- Statut initial proposé : pending

### T-002 — Schéma de données physique
- Story : transverse · CLASS-01, CLASS-02 (ENT-001..021, énumérations)
- Rôle : Architecte
- Dépend de : T-001
- Parallélisable avec : T-004
- Fichiers/modules : à définir
- Entrées : CLASS-01, CLASS-02, notes RG-006/011/019/024
- Sorties : schéma (tables, clés, contraintes, index) ; écarts avec l'UML listés
- Vérification : chaque classe et énumération de CLASS-01/02 a une table ou un type ; contraintes prix > 0, stock ≥ 0, note 1..5 présentes
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### T-003 — Contrat d'API et matrice d'autorisations
- Story : transverse · ENF-007 · matrice des permissions CDC §5 · SEQ-001/002/003
- Rôle : Architecte
- Dépend de : T-002
- Parallélisable avec : T-005
- Fichiers/modules : à définir (ex. fichier OpenAPI)
- Entrées : UC-DIAG-01..03, SEQ-001..003, matrice §5
- Sorties : contrat d'API par module ; matrice rôle × action
- Vérification : chaque UC-001..023 a au moins un point d'accès ; chaque ligne de la matrice §5 est couverte ; validé par @user (CP-1)
- Priorité : Must · Estimation : L
- Statut initial proposé : pending

### T-004 — Dépôt, environnement local, CI
- Story : transverse
- Rôle : Release
- Dépend de : T-001
- Parallélisable avec : T-002
- Fichiers/modules : à définir
- Entrées : T-001
- Sorties : dépôt, environnement local reproductible, pipeline CI (lint, tests, build)
- Vérification : un commit déclenche la CI ; la CI exécute les tests (commande à définir et à consigner ici)
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### T-005 — Migrations et données de référence
- Story : transverse · CLASS-01/02 · RG-001 (Tanger)
- Rôle : Backend
- Dépend de : T-002, T-004
- Parallélisable avec : T-003
- Fichiers/modules : migrations, seeds
- Entrées : T-002
- Sorties : migrations ; seed VilleDesservie = Tanger ; rôle Administrateur initial
- Vérification : migrations appliquées puis annulées sans erreur sur base vide ; commande à définir
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### T-006 — Authentification, rôles et cloisonnement
- Story : US-001, US-005 · ENF-007 · RG-028 · UC-DIAG-01..03
- Rôle : Backend
- Dépend de : T-003, T-005
- Parallélisable avec : T-007, T-008, T-009
- Fichiers/modules : module Comptes (M01), middleware d'autorisation
- Entrées : matrice T-003
- Sorties : rôles Client, Vendeur, Administrateur ; contrôle d'accès par propriété (vendeur → ses données)
- Vérification : tests autorisé + interdit pour chaque rôle ; un vendeur A ne lit aucune donnée du vendeur B ; mots de passe jamais renvoyés
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### T-007 — Paramètres métier configurables
- Story : transverse · Q19, Q27, Q40, Q42, Q44, Q45, RG-019 (7 j), RG-022 (15 j), CA-F022-7 (12 j), RG-018 (jour)
- Rôle : Backend
- Dépend de : T-005
- Parallélisable avec : T-006, T-008, T-009
- Fichiers/modules : module Paramètres
- Entrées : CDC §22
- Sorties : paramètres lisibles par le code, modifiables par l'admin, sans valeur métier inventée (valeurs de test seulement)
- Vérification : changer un paramètre modifie le comportement sans redéploiement ; test par paramètre
- Priorité : Must · Estimation : S
- Statut initial proposé : pending · HYPOTHÈSE H-08

### T-008 — Journal d'audit transverse
- Story : US-008 · ENF-008 · RG-029
- Rôle : Backend
- Dépend de : T-005
- Parallélisable avec : T-006, T-007, T-009
- Fichiers/modules : module Audit
- Entrées : ENF-008
- Sorties : historisation (qui, quand, montant, motif) des saisies de statut et des mouvements financiers ; consultation admin
- Vérification : chaque saisie de statut crée une entrée ; entrée non modifiable
- Priorité : Must · Estimation : M
- Statut initial proposé : pending · HYPOTHÈSE U-03

### T-009 — Service de notifications interne
- Story : US-006, US-007 · F014
- Rôle : Backend
- Dépend de : T-005
- Parallélisable avec : T-006, T-007, T-008
- Fichiers/modules : module Notifications (M10)
- Entrées : F014
- Sorties : notifications stockées et consultables dans l'application ; interface d'envoi pour un canal externe
- Vérification : un événement crée une notification pour le bon destinataire, et pour lui seul
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### T-010 — Adaptateur de canal externe (SMS / e-mail / WhatsApp)
- Story : US-006, US-007 · F014 · Q23
- Rôle : Backend
- Dépend de : T-009
- Parallélisable avec : —
- Fichiers/modules : à définir
- Entrées : choix du canal
- Sorties : envoi externe des notifications
- Vérification : envoi reçu sur le canal choisi en environnement de test
- Priorité : Must · Estimation : M
- Statut initial proposé : blocked · Raison : M-05

### T-011 — Planificateur de tâches temporelles
- Story : transverse · RG-011b, RG-024, RG-018, ENF-012
- Rôle : Backend
- Dépend de : T-004, T-007
- Parallélisable avec : T-014, T-017
- Fichiers/modules : à définir
- Entrées : T-001
- Sorties : exécution périodique de jobs (expiration, fin du délai de retour, reversement, alerte)
- Vérification : un job de test s'exécute à l'heure prévue ; test avec horloge simulée
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### T-012 — Socle frontend mobile-first
- Story : transverse · ENF-001 (cadre), ENF-002, ENF-011
- Rôle : Frontend
- Dépend de : T-003, T-004
- Parallélisable avec : T-006..T-009
- Fichiers/modules : à définir
- Entrées : contrat T-003 (CP-1)
- Sorties : routage, client d'API, gestion de session, mise en page 360 px, cadre i18n
- Vérification : build OK ; affichage correct à 360 px de large
- Priorité : Must · Estimation : M
- Statut initial proposé : pending · HYPOTHÈSE M-03

### T-013 — Traductions de l'interface
- Story : transverse · ENF-001 · Q11
- Rôle : Frontend
- Dépend de : T-012
- Parallélisable avec : —
- Fichiers/modules : fichiers de langue
- Entrées : langues retenues
- Sorties : interface dans chaque langue retenue
- Vérification : aucune clé non traduite dans chaque langue
- Priorité : Must · Estimation : M
- Statut initial proposé : blocked · Raison : M-09

### M01 — Comptes

### T-014 — Inscription et connexion client
- Story : US-005 · CA-F001-1, CA-F001-2 · F001, RG-014, RG-028 · UC-004
- Rôle : Backend
- Dépend de : T-006
- Parallélisable avec : T-017, T-027, T-036
- Fichiers/modules : M01
- Entrées : T-003
- Sorties : inscription par téléphone, connexion, déconnexion
- Vérification : CA-F001-1 et CA-F001-2 testés ; erreur d'identifiants sans préciser le champ
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### T-015 — Récupération d'accès client
- Story : F001
- Rôle : Backend
- Dépend de : T-014, T-010
- Parallélisable avec : —
- Fichiers/modules : M01
- Entrées : moyen de récupération
- Sorties : réinitialisation du mot de passe
- Vérification : un client récupère l'accès ; lien ou code à usage unique et expirant
- Priorité : Must · Estimation : S
- Statut initial proposé : blocked · Raison : M-06, M-05

### T-016 — Inscription vendeur et boutique
- Story : US-001 · CA-F002-1, CA-F002-2, CA-F002-3 · F002, RG-004, RG-005, RG-023 · UC-010
- Rôle : Backend
- Dépend de : T-006, T-017
- Parallélisable avec : T-018
- Fichiers/modules : M01, M02
- Entrées : CLASS-01 (Vendeur, Boutique, CommuneVendeur)
- Sorties : vendeur + boutique active immédiatement ; mode de reversement ; coordonnées bancaires si virement
- Vérification : CA-F002-1/2/3 testés ; une seule boutique par vendeur
- Priorité : Must · Estimation : M
- Statut initial proposé : pending · HYPOTHÈSE H-06, H-09

### T-017 — Référentiels administrateur
- Story : US-011 · F013, RG-001, RG-019, RG-023, D40 · UC-021
- Rôle : Backend
- Dépend de : T-006
- Parallélisable avec : T-014, T-027, T-036
- Fichiers/modules : M09
- Entrées : CLASS-01 (Catégorie.exclueDuRetour, VilleDesservie, CommuneVendeur)
- Sorties : CRUD catégories (avec exclusion du retour), villes desservies, communes vendeurs
- Vérification : action réservée à l'admin (test autorisé + interdit) ; ajout d'une commune autorise l'inscription d'un vendeur de cette commune
- Priorité : Must · Estimation : S
- Statut initial proposé : pending · HYPOTHÈSE H-12

### T-018 — Écrans inscription et connexion client
- Story : US-005 · CA-F001-1, CA-F001-2, CA-F001-3
- Rôle : Frontend
- Dépend de : T-012, T-014
- Parallélisable avec : T-016
- Fichiers/modules : à définir
- Entrées : T-003, parcours P2.3
- Sorties : écrans inscription, connexion, déconnexion
- Vérification : parcours réalisable à 360 px ; messages d'erreur conformes aux exceptions F001
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### T-019 — Parcours inscription vendeur
- Story : US-001 · CA-F002-1, CA-F002-2, CA-F002-3
- Rôle : Frontend
- Dépend de : T-012, T-016
- Parallélisable avec : T-021
- Fichiers/modules : à définir
- Entrées : parcours P1
- Sorties : formulaire vendeur + boutique, champs manquants signalés
- Vérification : les trois CA reproduits manuellement ; message de commune hors zone affiché
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### M02 — Catalogue vendeur

### T-020 — Stockage des photos produits
- Story : US-002 · ENF-011
- Rôle : Backend
- Dépend de : T-004, T-005
- Parallélisable avec : T-006..T-009
- Fichiers/modules : à définir
- Entrées : T-001
- Sorties : téléversement, redimensionnement pour mobile, contrôle de type et de taille
- Vérification : un fichier non image est refusé ; une image est servie en taille mobile
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### T-021 — Gestion des produits par le vendeur
- Story : US-002 · CA-F003-1, CA-F003-2, CA-F003-3 · F003, RG-006, RG-007, RG-019 · UC-011
- Rôle : Backend
- Dépend de : T-016, T-017, T-020
- Parallélisable avec : T-019
- Fichiers/modules : M02
- Entrées : CLASS-01 (Produit)
- Sorties : CRUD produit, prix > 0, stock, catégorie, ≥ 1 photo, périssable, personnalisé, masquage par le vendeur
- Vérification : CA-F003-1/2/3 testés ; prix ≤ 0 refusé ; changement de prix sans effet sur une commande existante
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### T-022 — Espace vendeur : gestion des produits
- Story : US-002 · CA-F003-1, CA-F003-2, CA-F003-3
- Rôle : Frontend
- Dépend de : T-012, T-021
- Parallélisable avec : T-023
- Fichiers/modules : à définir
- Entrées : parcours P1.3
- Sorties : liste, création, modification, masquage des produits
- Vérification : un vendeur publie un produit complet ; il ne voit que ses produits
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### M03 — Découverte

### T-023 — Catalogue, recherche, catégories
- Story : US-003 · CA-F004-1, CA-F004-2 · F004, RG-006 · UC-001
- Rôle : Backend
- Dépend de : T-021
- Parallélisable avec : T-022
- Fichiers/modules : M03
- Entrées : note RG-006 de CLASS-01
- Sorties : liste filtrée (publié ∧ ¬masqué ∧ stock > 0 ∧ vendeur actif), recherche par mot-clé, filtre catégorie
- Vérification : CA-F004-1/2 testés ; aucun résultat = message + suggestion de catégories
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### T-024 — Fiche produit
- Story : US-004 · CA-F005-1 · F005, RG-011, RG-019 · UC-002
- Rôle : Backend
- Dépend de : T-023
- Parallélisable avec : T-026
- Fichiers/modules : M03
- Entrées : CLASS-01 (Produit, Avis, Catégorie)
- Sorties : fiche avec note moyenne, nombre d'avis, avis non masqués, vendeur, commune, conditions de retour et exclusion
- Vérification : CA-F005-1 testé ; produit masqué ou vendeur suspendu = page indisponible
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### T-025 — Écrans catalogue et fiche produit
- Story : US-003, US-004 · CA-F004-1, CA-F004-2, CA-F005-1
- Rôle : Frontend
- Dépend de : T-012, T-023, T-024
- Parallélisable avec : T-028
- Fichiers/modules : à définir
- Entrées : parcours P2.1
- Sorties : catalogue, recherche, filtre, fiche produit
- Vérification : CA reproduits manuellement à 360 px
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### M04 — Panier et commande

### T-026 — Panier multi-vendeurs
- Story : US-005 · CA-F006-1, CA-F006-2, CA-F001-3 · F006, RG-003, RG-006 · UC-003
- Rôle : Backend
- Dépend de : T-023, T-006
- Parallélisable avec : T-024
- Fichiers/modules : M04
- Entrées : CLASS-01 (Panier, LignePanier)
- Sorties : ajout, quantité, retrait ; sous-total par vendeur ; panier visiteur rattaché au client à la connexion
- Vérification : CA-F006-1/2 et CA-F001-3 testés ; produit indisponible signalé et exclu du total
- Priorité : Must · Estimation : M
- Statut initial proposé : pending · HYPOTHÈSE H-01

### T-027 — Machines à états Commande et SousCommande
- Story : US-006, US-007, US-008, US-012 · STATE-001, STATE-002 · RG-008, RG-010, RG-029 · D22, D44
- Rôle : Backend
- Dépend de : T-005, T-008
- Parallélisable avec : T-014, T-017, T-036
- Fichiers/modules : service de transitions Commande / SousCommande (fichier partagé : seul ce service modifie les statuts)
- Entrées : STATE-001, STATE-002
- Sorties : transitions et gardes de STATE-001/002 ; transition interdite = erreur ; chaque transition historisée (T-008)
- Vérification : un test par transition autorisée ; un test par transition interdite (ex. annulation client depuis En collecte)
- Priorité : Must · Estimation : M
- Statut initial proposé : pending · HYPOTHÈSE H-03

### T-028 — Passage de commande (paiement à la livraison)
- Story : US-005 · CA-F007-1, CA-F007-2, CA-F007-3, CA-F007-4 · F007, RG-001, RG-002, RG-003, RG-007, RG-009, RG-017, RG-028 · SEQ-001, ACTIVITY-001
- Rôle : Backend
- Dépend de : T-026, T-027, T-007, T-009
- Parallélisable avec : T-025
- Fichiers/modules : M04
- Entrées : SEQ-001
- Sorties : commande unique, une sous-commande par vendeur, prix figé, frais de livraison (paramètre Q27), stock réservé en transaction, statut « En attente d'acceptation »
- Vérification : CA-F007-1..4 testés ; deux commandes concurrentes sur le dernier article : une seule réussit
- Priorité : Must · Estimation : L
- Statut initial proposé : pending

### T-029 — Confirmation écrite de commande
- Story : US-005 · CA-F007-1 · RG-026 · ENF-009
- Rôle : Backend
- Dépend de : T-028, T-009
- Parallélisable avec : T-030, T-033
- Fichiers/modules : M04, M10
- Entrées : RG-026
- Sorties : confirmation avec produits, prix, frais de livraison, vendeurs, conditions de retour
- Vérification : tous les champs minimaux de RG-026 présents ; gabarit soumis au juriste (T-070)
- Priorité : Must · Estimation : S
- Statut initial proposé : pending · HYPOTHÈSE H-10

### T-030 — Suivi et annulation par le client
- Story : US-006, US-012 · CA-F008-1, CA-F008-2 · F008, RG-010 · UC-006, UC-007
- Rôle : Backend
- Dépend de : T-028
- Parallélisable avec : T-029, T-033
- Fichiers/modules : M04 (appelle T-027)
- Entrées : STATE-001
- Sorties : liste et détail des commandes du client ; annulation avant collecte, stock restitué, vendeurs notifiés
- Vérification : CA-F008-1/2 testés ; un client ne voit que ses commandes
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### T-031 — Écrans panier, récapitulatif, confirmation
- Story : US-005 · CA-F006-1, CA-F006-2, CA-F007-1..4, CA-F001-3
- Rôle : Frontend
- Dépend de : T-012, T-018, T-026, T-028
- Parallélisable avec : T-030, T-033
- Fichiers/modules : à définir
- Entrées : parcours P2.2–P2.6
- Sorties : panier groupé par vendeur, adresse Tanger, téléphone, récapitulatif avec frais, seul mode « paiement à la livraison »
- Vérification : CA reproduits manuellement ; redirection connexion puis retour au panier
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### T-032 — Écran « Mes commandes »
- Story : US-006, US-012 · CA-F008-1, CA-F008-2
- Rôle : Frontend
- Dépend de : T-012, T-030
- Parallélisable avec : T-035
- Fichiers/modules : à définir
- Entrées : parcours P2.7
- Sorties : statut, raison d'annulation, bouton annuler selon garde
- Vérification : bouton absent dès « En collecte »
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### M05 — Sous-commandes vendeur

### T-033 — Traitement des sous-commandes
- Story : US-007 · CA-F009-1, CA-F009-2, CA-F009-3, CA-F014-2 · F009, RG-003, RG-008 · UC-012, SEQ-001
- Rôle : Backend
- Dépend de : T-028
- Parallélisable avec : T-029, T-030, T-031
- Fichiers/modules : M05 (appelle T-027)
- Entrées : STATE-002
- Sorties : liste cloisonnée ; accepter ; refuser avec motif ⇒ commande annulée, stock restitué, client et autres vendeurs notifiés ; déclarer prête
- Vérification : CA-F009-1/2/3 testés ; le vendeur ne voit ni adresse ni téléphone du client (ENF-007)
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### T-034 — Expiration du délai de réponse vendeur
- Story : US-007 · RG-011b · Q19 · STATE-002 t2
- Rôle : Backend
- Dépend de : T-033, T-011
- Parallélisable avec : T-035, T-037
- Fichiers/modules : M05, job planifié
- Entrées : paramètre délai (T-007)
- Sorties : sous-commande non traitée dans le délai = refusée ⇒ annulation totale
- Vérification : test avec horloge simulée, avant et après le délai
- Priorité : Must · Estimation : S
- Statut initial proposé : pending · HYPOTHÈSE H-02

### T-035 — Espace vendeur : sous-commandes
- Story : US-007 · CA-F009-1, CA-F009-2, CA-F009-3
- Rôle : Frontend
- Dépend de : T-012, T-033
- Parallélisable avec : T-032, T-034
- Fichiers/modules : à définir
- Entrées : parcours P4.1–P4.3
- Sorties : liste, accepter, refuser (avertissement « un refus annule la commande »), déclarer prête
- Vérification : avertissement affiché avant refus ; CA reproduits manuellement
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### M06 — Livraison et encaissement

### T-036 — MontantVendeur et machine à états STATE-004
- Story : US-009 · STATE-004 · RG-012, RG-024, RG-005
- Rôle : Backend
- Dépend de : T-005, T-008
- Parallélisable avec : T-014, T-017, T-027
- Fichiers/modules : M07 (service Montants, seul à modifier les statuts de montant)
- Entrées : CLASS-02 (MontantVendeur), STATE-004
- Sorties : création « Retenu » par ligne, transitions Retenu → Disponible → Reversé, Déduit
- Vérification : un test par transition de STATE-004 ; aucune commission appliquée
- Priorité : Must · Estimation : M
- Statut initial proposé : pending · HYPOTHÈSE H-04

### T-037 — Transmission, collecte, en livraison (saisie admin)
- Story : US-008 · CA-F010-4 · F010, RG-008, RG-029, D44 · UC-015, UC-016, SEQ-002
- Rôle : Backend
- Dépend de : T-027, T-008, T-033
- Parallélisable avec : T-034, T-035
- Fichiers/modules : M06 (appelle T-027)
- Entrées : SEQ-002, STATE-001 t3/t5, STATE-002 t4
- Sorties : liste des commandes prêtes ; transmission ⇒ « En collecte » ; collecte par sous-commande ; « En livraison » si tout collecté
- Vérification : CA-F010-4 testé ; action réservée à l'admin ; chaque saisie historisée
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### T-038 — Livrée et payée, échec de livraison
- Story : US-008 · CA-F010-1, CA-F010-2, CA-F010-3 · F010, RG-013 · SEQ-002, STATE-001 t6/t7
- Rôle : Backend
- Dépend de : T-037, T-036
- Parallélisable avec : —
- Fichiers/modules : M06
- Entrées : STATE-001, STATE-004 t0
- Sorties : saisie montant encaissé + date de réception ⇒ montants vendeurs « Retenu » ; écart signalé si ≠ dû ; échec avec motif ⇒ aucun montant dû, stock restitué
- Vérification : CA-F010-1/2/3 testés
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### T-039 — Remises de fonds et rapprochement
- Story : US-008 · RG-020 · ENF-008 · UC-017
- Rôle : Backend
- Dépend de : T-038
- Parallélisable avec : T-042, T-056
- Fichiers/modules : M06
- Entrées : CLASS-02 (RemiseDeFonds, Écart)
- Sorties : saisie d'une remise ; rattachement aux commandes ; écart calculé et signalé
- Vérification : remise = Σ montants encaissés ⇒ aucun écart ; sinon écart enregistré
- Priorité : Must · Estimation : M
- Statut initial proposé : pending · HYPOTHÈSE H-05

### T-040 — Suite d'un échec de livraison
- Story : US-008 · RG-013 · Q24
- Rôle : Backend
- Dépend de : T-038
- Parallélisable avec : —
- Fichiers/modules : M06
- Entrées : décision Q24
- Sorties : nouvelle tentative et/ou retour des produits aux vendeurs
- Vérification : à définir après décision
- Priorité : Must · Estimation : M
- Statut initial proposé : blocked · Raison : M-07

### T-041 — Back-office admin : livraison et encaissement
- Story : US-008 · CA-F010-1..4
- Rôle : Frontend
- Dépend de : T-012, T-037, T-038, T-039
- Parallélisable avec : T-043
- Fichiers/modules : à définir
- Entrées : parcours P5
- Sorties : commandes prêtes, transmission, saisies de statut, encaissement, remises, écarts
- Vérification : CA reproduits manuellement
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### M11 — Retours

### T-042 — Éligibilité au retour
- Story : US-013 · CA-F022-2, CA-F022-3, CA-F022-8 · RG-019, D40 · ACTIVITY-002
- Rôle : Backend
- Dépend de : T-038, T-017, T-021
- Parallélisable avec : T-039, T-056
- Fichiers/modules : M11
- Entrées : note RG-019 de CLASS-01/02
- Sorties : règle : ≤ 7 j après réception ∧ ¬périssable ∧ ¬personnalisé ∧ ¬catégorie exclue ; raison renvoyée sinon
- Vérification : CA-F022-2/3/8 testés ; jour 7 accepté, jour 8 refusé
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### T-043 — Demande de retour et machine à états Retour
- Story : US-013 · CA-F022-1, CA-F022-4, CA-F022-9 · RG-022, RG-025, RG-030 · STATE-003, SEQ-003
- Rôle : Backend
- Dépend de : T-042, T-007, T-009
- Parallélisable avec : T-041, T-057, T-058
- Fichiers/modules : M11 (service Retour, seul à modifier les statuts de retour)
- Entrées : STATE-003, CLASS-02 (Retour)
- Sorties : un retour par ligne ; motif, quantité, moyen de remboursement traçable (jamais espèces) ; frais affichés avant confirmation si changement d'avis ; vendeur et admin notifiés
- Vérification : CA-F022-1/4/9 testés ; un test par transition de STATE-003
- Priorité : Must · Estimation : M
- Statut initial proposé : pending · HYPOTHÈSE H-03, H-08 (Q42, Q45)

### T-044 — Saisie de la reprise (admin)
- Story : US-015 · RG-029 · STATE-003 t1/t2
- Rôle : Backend
- Dépend de : T-043, T-008
- Parallélisable avec : T-050, T-053
- Fichiers/modules : M11
- Entrées : SEQ-003
- Sorties : Demandé → En reprise → Repris ; vendeur notifié
- Vérification : réservé à l'admin ; saisie historisée
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### T-045 — Vérification vendeur et remise en vente
- Story : US-014 · CA-F022-6 · RG-027, RG-017, D43 · UC-013
- Rôle : Backend
- Dépend de : T-044
- Parallélisable avec : T-054
- Fichiers/modules : M11 (appelle le stock produit)
- Entrées : CLASS-02 (Vérification)
- Sorties : conforme ou contesté avec motif ; remise en vente ⇒ stock restitué ; contestation ⇒ Litige, admin notifié
- Vérification : CA-F022-6 testé ; stock inchangé si remiseEnVente = faux ; vendeur limité à ses retours
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### T-046 — Décision admin à défaut de vérification vendeur
- Story : US-015 · RG-027 · Q44 · STATE-003 n2
- Rôle : Backend
- Dépend de : T-045
- Parallélisable avec : —
- Fichiers/modules : M11
- Entrées : décision Q44 ; transition STATE-003
- Sorties : après le délai, l'admin vérifie à la place du vendeur
- Vérification : à définir après décision
- Priorité : Must · Estimation : S
- Statut initial proposé : blocked · Raison : M-08, U-01

### T-047 — Arbitrage d'un litige
- Story : US-015 · CA-F022-6 · RG-027 · UC-018
- Rôle : Backend
- Dépend de : T-045
- Parallélisable avec : T-051, T-054
- Fichiers/modules : M11
- Entrées : CLASS-02 (Litige)
- Sorties : décision, montant remboursé, imputation des frais ; en faveur du vendeur ⇒ Retour refusé
- Vérification : les deux issues testées ; décision réservée à l'admin
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### T-048 — Déductions et régularisations
- Story : US-009 · CA-F011-3, CA-F011-4 · RG-021, RG-025 · STATE-004 t2/t4, note n1
- Rôle : Backend
- Dépend de : T-036
- Parallélisable avec : T-014, T-017
- Fichiers/modules : M07
- Entrées : CLASS-02 (Déduction)
- Sorties : montant retenu ⇒ annulé (Déduit) ; montant déjà reversé ⇒ Déduction régularisée au reversement suivant ; frais imputés au vendeur
- Vérification : CA-F011-3/4 testés avec un remboursement fictif
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### T-049 — Enregistrement du remboursement
- Story : US-013, US-015 · CA-F022-5, CA-F011-3 · RG-021, RG-022, RG-025, D42 · UC-019
- Rôle : Backend
- Dépend de : T-045, T-047, T-048
- Parallélisable avec : T-061
- Fichiers/modules : M11, M07
- Entrées : STATE-003 t5/t7
- Sorties : montant = prix − frais si changement d'avis (frais de livraison initiaux selon paramètre Q40) ; moyen, référence, date ; déduction vendeur ; client notifié
- Vérification : CA-F022-5 et CA-F011-3 testés ; moyen « espèces » refusé
- Priorité : Must · Estimation : M
- Statut initial proposé : pending · HYPOTHÈSE H-08 (Q40)

### T-050 — Alerte de délai légal
- Story : US-015 · CA-F022-7 · ENF-012 · STATE-003 n1
- Rôle : Backend
- Dépend de : T-043, T-011
- Parallélisable avec : T-044, T-053
- Fichiers/modules : M11, job planifié
- Entrées : paramètre 12 j (T-007)
- Sorties : retour non remboursé depuis plus de 12 j signalé à l'admin, sans changement d'état
- Vérification : CA-F022-7 testé avec horloge simulée
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### T-051 — Écrans retour client et vérification vendeur
- Story : US-013, US-014 · CA-F022-1..4, CA-F022-8, CA-F022-9
- Rôle : Frontend
- Dépend de : T-012, T-043, T-045
- Parallélisable avec : T-047, T-055
- Fichiers/modules : à définir
- Entrées : parcours P3, P4.6
- Sorties : demande de retour par produit ; raison d'exclusion ; frais affichés ; écran de vérification vendeur
- Vérification : CA reproduits manuellement
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### T-052 — Back-office admin : retours, litiges, remboursements
- Story : US-015 · CA-F022-5, CA-F022-6, CA-F022-7
- Rôle : Frontend
- Dépend de : T-012, T-044, T-047, T-049, T-050
- Parallélisable avec : T-062
- Fichiers/modules : à définir
- Entrées : parcours P5.5
- Sorties : liste des retours, alerte délai, reprise, arbitrage, remboursement
- Vérification : CA reproduits manuellement
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### M07 — Montants et reversements

### T-053 — Fin du délai de retour : Retenu → Disponible
- Story : US-009 · CA-F011-1 · RG-024 · STATE-004 t1, ACTIVITY-003
- Rôle : Backend
- Dépend de : T-036, T-011, T-043
- Parallélisable avec : T-044, T-050
- Fichiers/modules : M07, job planifié
- Entrées : STATE-004
- Sorties : montant disponible à J + 7 si aucun retour en cours sur la ligne
- Vérification : CA-F011-1 testé ; ligne avec retour en cours reste « Retenu »
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### T-054 — Reversement hebdomadaire
- Story : US-009 · CA-F011-2, CA-F011-5 · RG-018 · ACTIVITY-003 · UC-020
- Rôle : Backend
- Dépend de : T-053, T-048
- Parallélisable avec : T-045, T-047
- Fichiers/modules : M07
- Entrées : CLASS-02 (Reversement), note n_mv
- Sorties : calcul Σ disponibles − Σ déductions ; enregistrement (date, montant, mode, preuve si espèces) ; solde négatif reporté et signalé
- Vérification : CA-F011-2/5 testés ; montants retenus exclus ; solde négatif testé
- Priorité : Must · Estimation : M
- Statut initial proposé : pending · HYPOTHÈSE H-07

### T-055 — Écrans montants vendeur et reversements admin
- Story : US-009 · CA-F011-1..5
- Rôle : Frontend
- Dépend de : T-012, T-054
- Parallélisable avec : T-051
- Fichiers/modules : à définir
- Entrées : parcours P4.5, P5.7
- Sorties : vendeur : retenu, disponible, reversé, déduit, historique ; admin : calcul et enregistrement du reversement
- Vérification : CA reproduits manuellement
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### M08 — Avis

### T-056 — Avis et notes
- Story : US-010, US-004 · CA-F012-1, CA-F012-2 · RG-011, D37 · UC-009
- Rôle : Backend
- Dépend de : T-038
- Parallélisable avec : T-039, T-042
- Fichiers/modules : M08
- Entrées : CLASS-01 (Avis), note n_rg011
- Sorties : note 1..5 + commentaire sur produit reçu ; un avis par produit et commande (2ᵉ = modification) ; moyenne recalculée
- Vérification : CA-F012-1/2 testés ; avis refusé si commande non « Livrée et payée »
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### T-057 — Écrans avis
- Story : US-010, US-004 · CA-F012-1, CA-F012-2
- Rôle : Frontend
- Dépend de : T-012, T-056, T-025
- Parallélisable avec : T-043
- Fichiers/modules : à définir
- Entrées : parcours P2.9
- Sorties : invitation à noter, formulaire, affichage sur la fiche
- Vérification : action « noter » absente pour un produit non reçu
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### M09 — Administration et modération

### T-058 — Modération
- Story : US-011 · CA-F013-1, CA-F013-2, CA-F013-3 · RG-015, D37 · UC-022
- Rôle : Backend
- Dépend de : T-021, T-056, T-009
- Parallélisable avec : T-043
- Fichiers/modules : M09
- Entrées : CLASS-01 (Produit.masqué, Vendeur.statut, Avis.masqué)
- Sorties : masquer produit, suspendre vendeur, masquer avis ; vendeur notifié ; moyenne recalculée
- Vérification : CA-F013-1/2/3 testés ; action réservée à l'admin
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### T-059 — Supervision administrateur
- Story : US-011 · F013 · UC-023
- Rôle : Backend
- Dépend de : T-038, T-043, T-054
- Parallélisable avec : T-047, T-051
- Fichiers/modules : M09
- Entrées : matrice §5
- Sorties : consultation vendeurs, produits, commandes, retours, montants
- Vérification : réservé à l'admin ; coordonnées bancaires visibles seulement par l'admin et le titulaire
- Priorité : Must · Estimation : S
- Statut initial proposé : pending

### T-060 — Annulation admin et vendeur suspendu en cours d'activité
- Story : US-011 · F013 (exception), N9 · UC-023
- Rôle : Backend
- Dépend de : T-058, T-027
- Parallélisable avec : —
- Fichiers/modules : M09, service T-027
- Entrées : transition d'annulation admin dans STATE-001
- Sorties : l'admin honore ou annule les sous-commandes d'un vendeur suspendu ; droits de retour préservés
- Vérification : à définir après mise à jour de STATE-001
- Priorité : Must · Estimation : S
- Statut initial proposé : blocked · Raison : U-02

### T-061 — Back-office admin : référentiels, modération, supervision
- Story : US-011 · CA-F013-1..3
- Rôle : Frontend
- Dépend de : T-012, T-017, T-058, T-059
- Parallélisable avec : T-049
- Fichiers/modules : à définir
- Entrées : matrice §5
- Sorties : écrans catégories, villes, communes, modération, consultation
- Vérification : CA reproduits manuellement
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### M10 — Notifications

### T-062 — Câblage des événements de notification F014
- Story : US-006, US-007 · CA-F014-1, CA-F014-2 · F014
- Rôle : Backend
- Dépend de : T-009, T-033, T-037, T-038, T-043, T-045, T-047, T-049, T-053, T-054
- Parallélisable avec : T-052
- Fichiers/modules : M10 (abonnements aux événements ; ne modifie pas les services émetteurs)
- Entrées : liste F014
- Sorties : chaque événement F014 (client et vendeur) produit une notification
- Vérification : un test par événement de la liste F014 ; CA-F014-1/2 testés
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### Tests d'intégration et qualité

### T-063 — Recette parcours P1 + P2 (vendeur → commande → livraison → avis)
- Story : US-001..008, US-010, US-012 · CA-F001..F010, CA-F012, CA-F014
- Rôle : QA/Intégration
- Dépend de : T-019, T-022, T-025, T-031, T-032, T-035, T-041, T-057, T-062
- Parallélisable avec : T-064, T-065, T-066
- Fichiers/modules : tests de bout en bout
- Entrées : ACTIVITY-001, SEQ-001, SEQ-002
- Sorties : scénarios automatisés : commande 2 vendeurs livrée ; refus d'un vendeur ; annulation client ; échec de livraison
- Vérification : scénarios exécutés en CI ; commande à définir
- Priorité : Must · Estimation : L
- Statut initial proposé : pending

### T-064 — Recette parcours P3 (retour)
- Story : US-013, US-014, US-015 · CA-F022-1..9
- Rôle : QA/Intégration
- Dépend de : T-051, T-052, T-062
- Parallélisable avec : T-063, T-065
- Fichiers/modules : tests de bout en bout
- Entrées : ACTIVITY-002, SEQ-003, STATE-003
- Sorties : scénarios : changement d'avis ; défaut ; litige gagné par le client ; litige gagné par le vendeur ; retour de 2 produits de 2 vendeurs
- Vérification : scénarios exécutés en CI ; commande à définir
- Priorité : Must · Estimation : L
- Statut initial proposé : pending

### T-065 — Recette argent (P4.5, P5)
- Story : US-008, US-009 · CA-F010-1, CA-F010-2, CA-F011-1..5
- Rôle : QA/Intégration
- Dépend de : T-055, T-049, T-039
- Parallélisable avec : T-063, T-064
- Fichiers/modules : tests de bout en bout
- Entrées : ACTIVITY-003, STATE-004
- Sorties : scénarios avec horloge simulée : retenue, mise à disposition, reversement, régularisation après reversement
- Vérification : montants des CA-F011-1..5 retrouvés à l'unité près ; commande à définir
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### T-066 — Tests de cloisonnement et de modération
- Story : US-001, US-002, US-011 · CA-F002-1..3, CA-F003-3, CA-F009-1, CA-F013-1..3 · ENF-007
- Rôle : QA/Intégration
- Dépend de : T-061, T-022, T-035, T-051
- Parallélisable avec : T-063, T-064
- Fichiers/modules : tests de sécurité
- Entrées : matrice T-003
- Sorties : pour chaque ligne de la matrice : accès autorisé et accès interdit testés
- Vérification : 0 accès interdit réussi ; commande à définir
- Priorité : Must · Estimation : M
- Statut initial proposé : pending

### T-067 — Mesures mobile et performance
- Story : transverse · ENF-002, ENF-004, ENF-011
- Rôle : QA/Intégration
- Dépend de : T-025
- Parallélisable avec : T-029, T-030
- Fichiers/modules : à définir
- Entrées : valeurs ENF (HYPOTHÈSE)
- Sorties : rapport de mesure catalogue et fiche (4G simulée, 360 px)
- Vérification : p95 < 3 s mesuré (valeur à valider par @user) ; outil à définir
- Priorité : Should · Estimation : S
- Statut initial proposé : pending · HYPOTHÈSE H-11

### T-068 — Test utilisateur vendeur (premier produit)
- Story : US-001, US-002 · ENF-003
- Rôle : QA/Intégration
- Dépend de : T-019, T-022
- Parallélisable avec : T-023
- Fichiers/modules : —
- Entrées : protocole de test
- Sorties : temps mesuré pour 3 vendeurs au moins, sans assistance
- Vérification : < 10 min (valeur à valider par @user)
- Priorité : Should · Estimation : S
- Statut initial proposé : pending · HYPOTHÈSE H-11

### T-069 — Hébergement, déploiement, supervision
- Story : transverse · ENF-005, ENF-006
- Rôle : Release
- Dépend de : T-001, T-004
- Parallélisable avec : T-003, T-005
- Fichiers/modules : à définir
- Entrées : T-001
- Sorties : environnement de recette et de production, sauvegardes, supervision de disponibilité
- Vérification : déploiement reproductible depuis la CI ; sauvegarde restaurée une fois
- Priorité : Must · Estimation : M
- Statut initial proposé : pending · HYPOTHÈSE H-11

### T-070 — Porte de lancement : juridique et paramètres
- Story : transverse · C-08, ENF-009 · Q39, Q40, Q41, Q42, Q43, Q44, Q45, Q27, Q19
- Rôle : Porteur du projet (@user), hors développement
- Dépend de : —
- Parallélisable avec : toutes
- Fichiers/modules : —
- Entrées : CDC §22
- Sorties : avis juridique ; valeurs des paramètres T-007 ; liste des communes ; catégories exclues
- Vérification : chaque question du §22 « avant lancement » a une réponse écrite
- Priorité : Must · Estimation : à définir
- Statut initial proposé : pending

## 4. Ordre d'exécution

Vagues (une vague démarre quand ses dépendances sont terminées) :
- V1 {T-001 ∥ T-070}
- V2 {T-002 ∥ T-004}
- V3 {T-003 ∥ T-005 ∥ T-069}
- V4 {T-006 ∥ T-007 ∥ T-008 ∥ T-009 ∥ T-012 ∥ T-020} — CP-1 : contrat T-003 validé avant T-012
- V5 {T-011 ∥ T-014 ∥ T-017 ∥ T-027 ∥ T-036}
- V6 {T-016 ∥ T-018 ∥ T-048}
- V7 {T-019 ∥ T-021}
- V8 {T-022 ∥ T-023}
- V9 {T-024 ∥ T-026 ∥ T-068}
- V10 {T-025 ∥ T-028}
- V11 {T-029 ∥ T-030 ∥ T-031 ∥ T-033 ∥ T-067} — CP-2 : commande de bout en bout
- V12 {T-032 ∥ T-034 ∥ T-035 ∥ T-037}
- V13 {T-038} — CP-3 : livraison et montants retenus
- V14 {T-039 ∥ T-042 ∥ T-056}
- V15 {T-041 ∥ T-043 ∥ T-057 ∥ T-058}
- V16 {T-044 ∥ T-050 ∥ T-053}
- V17 {T-045 ∥ T-054}
- V18 {T-047 ∥ T-051 ∥ T-055 ∥ T-059}
- V19 {T-049 ∥ T-061} — CP-4 : retour remboursé et déduit
- V20 {T-052 ∥ T-062 ∥ T-065 ∥ T-066}
- V21 {T-063 ∥ T-064} — CP-5 : recette MVP ; lancement seulement après T-070
- Bloquées, hors vagues : T-010, T-013, T-015, T-040, T-046, T-060

Chemin critique :
T-001 → T-002 → T-003 → T-006 → T-017 → T-016 → T-021 → T-023 → T-026 → T-028 → T-033 → T-037 → T-038 → T-042 → T-043 → T-044 → T-045 → T-047 → T-049 → T-062 → T-064

Coordination sur fichiers partagés :
- Statuts Commande / SousCommande : seul le service T-027 les modifie. T-030, T-033, T-037, T-038 appellent ce service sans le modifier. Toute nouvelle transition (ex. T-060) passe par une revue de T-027.
- Statuts de montant : seul le service T-036 les modifie (T-038, T-048, T-053, T-054 l'appellent).
- Statuts de retour : seul le service T-043 les modifie (T-044, T-045, T-047, T-049).
- Contrôle du graphe : 70 tâches ; toutes les dépendances citées existent ; aucun cycle (ordre par vagues ci-dessus).

## 5. Traçabilité

| Story | Critères | Tâches | Tâche de test |
|---|---|---|---|
| US-001 | CA-F002-1..3 | T-016, T-017, T-019 | T-066, T-068, T-063 |
| US-002 | CA-F003-1..3 | T-020, T-021, T-022 | T-066, T-068, T-063 |
| US-003 | CA-F004-1..2 | T-023, T-025 | T-063 |
| US-004 | CA-F005-1 | T-024, T-025, T-056, T-057 | T-063 |
| US-005 | CA-F001-1..3, CA-F006-1..2, CA-F007-1..4 | T-014, T-018, T-026, T-028, T-029, T-031 | T-063 |
| US-006 | CA-F008-1, CA-F014-1..2 | T-030, T-032, T-009, T-062 | T-063 |
| US-007 | CA-F009-1..3 | T-033, T-034, T-035 | T-063, T-066 |
| US-008 | CA-F010-1..4 | T-037, T-038, T-039, T-041 (T-040 bloquée) | T-063, T-065 |
| US-009 | CA-F011-1..5 | T-036, T-048, T-053, T-054, T-055 | T-065 |
| US-010 | CA-F012-1..2 | T-056, T-057 | T-063 |
| US-011 | CA-F013-1..3 | T-017, T-058, T-059, T-061 (T-060 bloquée) | T-066 |
| US-012 | CA-F008-1..2 | T-030, T-032 | T-063 |
| US-013 | CA-F022-1..4, CA-F022-8..9 | T-042, T-043, T-049, T-051 | T-064 |
| US-014 | CA-F022-6 | T-045, T-051 | T-064 |
| US-015 | CA-F022-5..7 | T-044, T-047, T-049, T-050, T-052 (T-046 bloquée) | T-064 |
| ENF-001..006, 011 (hors UML) | — | T-001, T-012, T-013, T-020, T-069 | T-067, T-068 |

## 6. Remise

Tâches dispatchables maintenant (dépendances vides, non bloquées) : T-001 (Architecte), T-070 (@user, hors développement).

Tâches bloquées (6) : T-010 (M-05), T-013 (M-09), T-015 (M-06, M-05), T-040 (M-07), T-046 (M-08, U-01), T-060 (U-02).

Questions ouvertes (détail en §2) :
1. Stack technique pour T-001. Défaut : Laravel + React + MySQL + Docker (HYPOTHÈSE, à confirmer par l'Architecte).
2. Canal des notifications (Q23). Défaut : notifications dans l'application + SMS (le téléphone est obligatoire, RG-014).
3. Écrans : attendre une conception (Iris) ou partir des parcours P1–P5 du CDC. Défaut : partir des parcours P1–P5.
Autres décisions attendues : Q24, Q44, Q11, e-mail client (F001) ; paramètres et avis juridique via T-070.

Écarts UML signalés à Blueprint : U-01, U-02, U-03 (signalement seulement ; aucune modification demandée sans l'accord de @user).
