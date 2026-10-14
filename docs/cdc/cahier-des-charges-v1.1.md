# 📄 CAHIER DES CHARGES — Marketplace de produits locaux marocains

**Version** 1.1 — **Statut : Validé** (validée par le porteur du projet, Anass, le 2026-10-12 : « v1.1 validée » — S11, D45)
**Nom du produit :** MANQUANT (désigné ci-après « la Plateforme »)

> **Statut de cette révision** : la v1.0 a été validée par le porteur (S9). La v1.1 corrige une incohérence relevée par l'agent Blueprint (B1 : règles marquées SUGGESTION alors que des critères validés les exigeaient), corrige le décompte des règles métier (28 et non 27), et intègre huit décisions du porteur (S10, D37–D44). Le porteur l'a validée (S11, D45) : **la v1.1 remplace la v1.0 comme référence validée** pour les agents d'ingénierie.

> **Portée de la validation** : la validation porte sur le périmètre, les acteurs, les parcours, les fonctionnalités, les règles métier, les exigences et le MVP décrits ici. Les points encore marqués HYPOTHÈSE, MANQUANT ou SUGGESTION restent **à régler avant le lancement** (voir §22). Ils ne remettent pas en cause la structure du produit. La validation juridique (C-08) reste obligatoire avant le lancement.

**Sources**

| ID | Source | Contenu |
|---|---|---|
| S1 | Message initial du porteur de projet (chat) | Idée : e-commerce de produits locaux marocains ; clients (parcourir, panier, commande) ; vendeurs locaux (ajout/gestion produits) ; aider les petites entreprises ; simple au début, évolutif |
| S2 | Réponses tour 1 (chat) : « q1-a q2-d q3-c q4-market q5-a » | Paiement à la livraison ; livraison mixte ; problème = visibilité |
| S3 | Réponses tour 2 (chat) : « q3-a q4-b q6-a q7-c q8-e » | Inscription vendeur libre ; Maroc + diaspora ; panier multi-vendeurs livré et encaissé par la plateforme ; avis/notes |
| S4 | Réponses tour 3 (chat) | Livraison par la plateforme dès le lancement ; V1 Maroc uniquement ; gratuit pour les vendeurs au lancement |
| S5 | « go ahead now » (chat) | Autorisation de rédiger avec les points non tranchés en HYPOTHÈSE |
| S6 | Réponses sur la v0.1 (chat) | Lancement à Tanger ; société de livraison ; frais de livraison payés par le client ; reversement par virement ou espèces ; pas de livraison partielle ; retours acceptés |
| S7 | Réponses sur la v0.2 (chat) | Vendeurs à Tanger et environs ; retours 7 jours ; motifs ; frais de retour ; remboursement traçable ; retenue des fonds vendeurs et régularisation |
| S8 | Réponses sur la v0.3 (chat) : C3, Q36, Q37, Q33, Q13b, Q35 | Retour possible pour changement d'avis dans les 7 jours suivant la réception, sauf exceptions légales ; frais de retour au client (changement d'avis) ou au vendeur (défaut/erreur) lorsque la loi le prévoit ; vérification par le vendeur, supervision des litiges et remboursements par l'administrateur ; remboursement dans le délai légal ; virement ou autre moyen traçable et légal ; vendeurs à Tanger et communes voisines ; reversements hebdomadaires ; exclusions uniquement si la loi le permet ; validation juridique avant lancement |
| S9 | Validation du porteur sur la v0.4 (chat) : « passe au statut validé » | Approbation de la v1.0 |
| S10 | Réponses du porteur aux questions de l'étape A de Blueprint, données dans le chat Blueprint : « b1-a b2-a b3-a b4-c b5-a n5-a n6-a n7-a » ; transmises par Blueprint et vérifiées au §10 de `/opt/data/uml/marketplace-produits-locaux-maroc/00-etape-A-analyse-et-proposition.md` | Modération et avis réservés aux produits reçus confirmés ; statuts de livraison saisis par l'administrateur seul ; un retour par produit ; exclusion du retour par le produit (vendeur) et par la catégorie (administrateur) ; compte client obligatoire ; frais de retour déduits du remboursement ; remise en vente décidée par le vendeur ; « En collecte » à la transmission à la société de livraison |
| S11 | Validation du porteur (Anass) sur la v1.1 (chat, 2026-10-12) : « v1.1 validée » | Approbation de la v1.1 |
| R1 | Ministère de l'Industrie et du Commerce, *Guide du consommateur* (mcinet.gov.ma), rubrique « Le contrat conclu à distance » | **Référence réglementaire, pas une source de besoin.** Droit de rétractation de 7 jours à compter de la réception du bien ; remboursement du montant total payé au plus tard 15 jours après l'exercice du droit ; délai porté à 30 jours si les informations obligatoires ne sont pas confirmées par écrit. À faire vérifier par un conseil juridique. |

Journal des décisions : `decisions.md` (D1–D45).

**Méthodologie (skills PM utilisés)** : `cahier-des-charges` (procédure), `problem-statement` (§3), `user-story` (§14–15, format Cohn + Gherkin), `prioritization-advisor` (§16 ; MoSCoW retenu car le produit n'est pas lancé, sans données d'usage, et des arbitrages nets sont nécessaires).

**Légende des statuts**
- **CONFIRMÉ (S#/D#)** : explicitement décidé par le porteur de projet.
- **HYPOTHÈSE** : déduction de l'analyste, à confirmer avant le lancement.
- **MANQUANT** : information nécessaire, non fournie.
- **CONTRADICTOIRE** : sources en conflit.
- **SUGGESTION** : proposition de l'analyste, non retenue tant qu'elle n'est pas acceptée.

**Adaptation de la structure** : les 23 sections sont conservées. Le §10 détaille uniquement les fonctionnalités MUST (les SHOULD/COULD figurent dans le tableau du §12). Le §15 regroupe les critères d'acceptation des fonctionnalités MUST.

**Consignes pour les équipes d'ingénierie** : ce document décrit QUOI et POURQUOI. Les choix techniques (architecture, technologies, données, hébergement) relèvent des équipes d'ingénierie ; aucune contrainte technique n'a été imposée par le porteur de projet (C-07). Les éléments HYPOTHÈSE peuvent être conçus de façon paramétrable ou faire l'objet d'une confirmation auprès du porteur avant développement ; les éléments SUGGESTION ne doivent pas être développés sans son accord.

---

## 1. Présentation du projet

La Plateforme est une **place de marché en ligne (marketplace) dédiée aux produits locaux marocains** [CONFIRMÉ — S1, D1, D3]. De petits vendeurs locaux **situés à Tanger et dans les communes voisines** y créent leur boutique et y publient leurs produits [CONFIRMÉ — D24, D33]. Des clients **à Tanger**, disposant d'un compte, les découvrent, les commandent dans un panier unique, même s'il contient plusieurs vendeurs, et **paient à la livraison** [CONFIRMÉ — D6, D12, D18, D41].

La Plateforme **organise la livraison et l'encaissement via une société de livraison partenaire**. Celle-ci collecte les produits chez les vendeurs, livre la commande en une seule fois et encaisse le paiement ; **l'administrateur enregistre sur la Plateforme les informations transmises par la société de livraison** [CONFIRMÉ — D12, D14, D19, D38]. Les clients peuvent **retourner un produit dans les 7 jours suivant sa réception, y compris par simple changement d'avis**, sauf exceptions légales [CONFIRMÉ — D30]. Le vendeur vérifie le produit retourné, l'administrateur supervise les litiges et les remboursements, et le client est remboursé **de façon traçable, dans le délai légal** [CONFIRMÉ — D31, D32].

La Plateforme **retient les sommes dues aux vendeurs jusqu'à la fin du délai de retour**, puis les leur reverse **chaque semaine**, **par virement bancaire ou en espèces**, après déduction des remboursements éventuels [CONFIRMÉ — D21, D29, D34]. L'administrateur **modère** le catalogue et les avis, et seuls les clients ayant reçu un produit peuvent le noter [CONFIRMÉ — D37].

La première version doit rester **simple** et permettre d'**ajouter des fonctionnalités par la suite** [CONFIRMÉ — D5]. **Une validation juridique est requise avant le lancement** [CONFIRMÉ — D30].

| Élément | Valeur | Statut |
|---|---|---|
| Type de projet | Création d'un nouveau produit (marketplace B2C multi-vendeurs) | CONFIRMÉ — S1 |
| Domaine | Commerce en ligne, produits locaux marocains | CONFIRMÉ — S1 ; nature exacte des produits MANQUANT (Q10) |
| Porteur / opérateur | Le porteur du projet (exploitant de la Plateforme) | HYPOTHÈSE |
| Zone clients V1 | Tanger | CONFIRMÉ — D18 |
| Zone vendeurs V1 | Tanger et communes voisines ; extension à tout le Maroc ensuite | CONFIRMÉ — D24, D33 ; liste des communes à fixer avant lancement (Q41) |
| Livraison | Confiée à une **société de livraison** partenaire, sans accès direct à la Plateforme ; statuts saisis par l'administrateur | CONFIRMÉ — D19, D38 |
| Frais de livraison | Payés par le **client** | CONFIRMÉ — D20 ; montant MANQUANT (Q27) |
| Compte client | Obligatoire pour commander | CONFIRMÉ — D41 |
| Retours | 7 jours après réception, tout motif, sauf exceptions légales ; un retour par produit | CONFIRMÉ — D30, D35, D39 |
| Reversements vendeurs | Hebdomadaires, après la période de retenue | CONFIRMÉ — D34 |
| Modèle économique V1 | Gratuit pour les vendeurs ; modèle de revenus à définir plus tard | CONFIRMÉ — D16 |

## 2. Contexte

- De nombreuses petites entreprises locales marocaines produisent des biens locaux mais **ne sont pas connues** au-delà de leur entourage immédiat [CONFIRMÉ — D8]. Leur profil exact (artisans, coopératives, commerces) est MANQUANT (Q10).
- Le porteur de projet veut leur offrir un canal de vente en ligne [CONFIRMÉ — D4].
- Le lancement se fait sur **Tanger**, avec des vendeurs **de Tanger et des communes voisines** et une société de livraison partenaire, pour simplifier la collecte et la livraison avant une extension nationale [CONFIRMÉ — D18, D19, D24, D33].
- Le paiement à la livraison est le seul mode de paiement au lancement [CONFIRMÉ — D6].
- L'ouverture à la diaspora marocaine est envisagée, mais **reportée** après la V1 [CONFIRMÉ — D10, D15].
- La vente en ligne au Maroc est encadrée par la **loi 31-08** sur la protection du consommateur (vente à distance, droit de rétractation, information du consommateur) [Référence R1]. Le porteur de projet a décidé d'aligner la politique de retour sur ce cadre et de la faire **valider juridiquement avant le lancement** [CONFIRMÉ — D30].
- Aucune étude de marché, donnée de volume, liste de concurrents ni société de livraison choisie n'a été fournie [MANQUANT, non bloquant].

## 3. Problématique

**Récit du problème (côté vendeur)**
- **Je suis** un petit vendeur local marocain qui fabrique ou vend des produits locaux.
- **J'essaie de** vendre mes produits à des clients au-delà de mon entourage.
- **Mais** les clients potentiels ne me connaissent pas et ne trouvent pas mes produits [CONFIRMÉ — D8].
- **Parce que** je n'ai pas de vitrine en ligne visible, et qu'il m'est difficile de gérer seul la livraison et l'encaissement à distance [HYPOTHÈSE : la seconde partie est déduite du choix D14 de confier livraison et encaissement à la Plateforme].
- **Ce qui me fait ressentir** : non documenté [MANQUANT ; aucune donnée d'entretien, rien n'est inventé].

**Énoncé du problème**
> Les petits vendeurs locaux marocains ont besoin d'un moyen d'être découverts et de vendre à des clients au-delà de leur entourage, parce qu'ils manquent aujourd'hui de visibilité, ce qui limite leurs ventes à la vente de proximité.

**Côté client** [HYPOTHÈSE] : les clients qui cherchent des produits locaux authentiques n'ont pas d'endroit unique pour découvrir plusieurs petits producteurs et commander chez plusieurs d'entre eux en une seule fois.

**Coût de l'inaction** [HYPOTHÈSE] : les vendeurs restent dépendants de la vente de proximité, et les clients ne trouvent pas ces produits.

## 4. Objectifs

| ID | Type | Objectif | Statut | KPI (§20) |
|---|---|---|---|---|
| O1 | Business | Donner de la visibilité aux petits vendeurs locaux et leur permettre de vendre en ligne | CONFIRMÉ — D4, D8 | K1, K2 |
| O2 | Utilisateur (vendeur) | Permettre à un vendeur de mettre ses produits en vente sans compétence technique et sans gérer lui-même la livraison ni l'encaissement, et d'être payé de façon fiable et régulière | CONFIRMÉ (livraison/encaissement — D14 ; reversement — D21, D29, D34) ; « sans compétence technique » HYPOTHÈSE | K3, K4, K9 |
| O3 | Utilisateur (client) | Permettre à un client à Tanger de découvrir des produits locaux, de commander chez plusieurs vendeurs en un seul panier, de payer à la livraison et de retourner un produit dans les 7 jours | CONFIRMÉ — D2, D6, D12, D18, D30 | K5, K6, K8 |
| O4 | Produit | Établir la confiance entre clients et vendeurs grâce aux avis, aux notes et à la modération | CONFIRMÉ — D13, D37 | K7 |
| O5 | Produit | Lancer une V1 simple, extensible et conforme à la réglementation, sans remise en cause des parcours existants | CONFIRMÉ — D5, D30 | — (critères qualitatifs, ENF-009, ENF-010) |

Les valeurs cibles des KPI sont **MANQUANTES** (Q21).

## 5. Utilisateurs et acteurs

| Acteur | Description | Objectifs | Responsabilités | Statut |
|---|---|---|---|---|
| **Visiteur** | Personne non connectée | Découvrir les produits et les vendeurs | — | HYPOTHÈSE (navigation sans compte) ; doit créer un compte ou se connecter pour commander (D41) |
| **Client** | Personne inscrite, livrée à Tanger | Trouver des produits locaux, commander, être livré, payer à la livraison, retourner un produit, donner son avis | Fournir une adresse à Tanger et un téléphone joignable ; payer produits et frais de livraison à la réception ; fournir un moyen de remboursement traçable en cas de retour ; supporter les frais de retour en cas de changement d'avis | CONFIRMÉ — S1, D6, D18, D20, D30, D32, D41 |
| **Vendeur** | Petite entreprise locale marocaine **située à Tanger ou dans une commune voisine** (profil exact Q10) | Être visible, vendre, être payé | Publier des produits locaux exacts et conformes à leur description ; signaler les produits périssables ou personnalisés ; tenir son stock à jour ; préparer les commandes à temps ; **vérifier les produits retournés et décider de leur remise en vente** ; supporter les frais de retour en cas de défaut ou d'erreur, lorsque la loi le prévoit | CONFIRMÉ — S1, D3, D9, D30, D31, D33, D40, D43 |
| **Administrateur de la Plateforme** | Équipe du porteur de projet | Faire fonctionner la marketplace, garantir la qualité du catalogue et la conformité | Gérer vendeurs, catégories (dont exclusions de retour), zones ; **modérer** produits, vendeurs et avis ; **saisir les statuts de collecte, livraison, encaissement et reprise** transmis par la société de livraison ; superviser les litiges et les remboursements ; gérer retenues et reversements hebdomadaires ; relation avec la société de livraison | CONFIRMÉ — D31, D37, D38, D40 ; existence d'une équipe dédiée HYPOTHÈSE |
| **Société de livraison (partenaire)** | Entreprise externe chargée de la collecte chez les vendeurs, de la livraison au client, de l'encaissement et de la reprise des retours. **N'utilise pas la Plateforme** : elle transmet ses informations à l'administrateur. | Exécuter collectes, livraisons et reprises | Transmettre à l'administrateur les statuts de collecte, de livraison, d'encaissement et de reprise ; remettre à la Plateforme les montants encaissés | CONFIRMÉ — D19, D38 ; moyen de transmission (hors Plateforme) à convenir avec le partenaire (C-05) |

### Matrice des permissions (V1)

| Capacité | Visiteur | Client | Vendeur | Admin |
|---|---|---|---|---|
| Consulter le catalogue, les fiches produits, les avis | ✔ | ✔ | ✔ | ✔ |
| Rechercher / filtrer par catégorie | ✔ | ✔ | ✔ | ✔ |
| Gérer un panier | ✔ (HYPOTHÈSE) | ✔ | — | — |
| Passer commande (compte obligatoire) | — | ✔ | — | — |
| Suivre / annuler ses commandes | — | ✔ | — | ✔ |
| Demander le retour d'un produit reçu (7 jours, tout motif) | — | ✔ | — | — |
| Vérifier un produit retourné (conforme / contesté) et décider de sa remise en vente | — | — | ✔ (ses produits) | ✔ (en cas de litige ou d'absence de vérification) |
| Arbitrer un litige de retour | — | — | — | ✔ |
| Enregistrer un remboursement client | — | — | — | ✔ |
| Laisser un avis / une note | — | ✔ (produit reçu uniquement) | — | — |
| Créer / modifier sa boutique et ses produits (dont caractère périssable/personnalisé) | — | — | ✔ (les siens) | ✔ (modération) |
| Accepter / refuser / préparer une sous-commande | — | — | ✔ (les siennes) | ✔ |
| Saisir collecte, livraison, encaissement, reprise de retour | — | — | — | ✔ (seul) |
| Consulter ses montants retenus, disponibles, reversés et déduits | — | — | ✔ (les siens) | ✔ |
| Enregistrer un reversement hebdomadaire (virement ou espèces) | — | — | — | ✔ |
| Masquer un produit / suspendre un vendeur / masquer un avis | — | — | — | ✔ |
| Gérer les catégories (dont exclusions de retour), la zone clients et la liste des communes vendeurs | — | — | — | ✔ |

La société de livraison n'a pas d'accès à la Plateforme en V1 (D38).

## 6. Périmètre (synthèse)

| Dans le périmètre V1 | Hors périmètre V1 | Évolutions futures |
|---|---|---|
| Comptes client (obligatoires pour commander) et vendeur (vendeurs de Tanger et communes voisines) ; boutiques et catalogue vendeur ; découverte (catalogue, recherche, catégories, fiche produit) ; panier multi-vendeurs ; commande avec paiement à la livraison à Tanger, frais de livraison à la charge du client ; acceptation des sous-commandes (commande annulée si un vendeur refuse) ; collecte, livraison groupée et encaissement par la société de livraison, statuts saisis par l'administrateur ; retours sous 7 jours pour tout motif (sauf exceptions légales), un retour par produit, vérification par le vendeur, litiges et remboursements supervisés par l'administrateur ; retenue des fonds vendeurs puis reversement hebdomadaire par virement ou espèces ; avis et notes réservés aux produits reçus ; administration et modération ; notifications de base | Paiement en ligne ; commande sans compte ; accès direct de la société de livraison à la Plateforme ; livraison hors de Tanger ; vendeurs hors de Tanger et communes voisines ; livraison hors du Maroc ; abonnement / commission vendeurs ; livraison par le vendeur et retrait chez le vendeur ; livraison partielle ; remboursement en espèces non traçable ; messagerie client-vendeur ; outils marketing | Voir §21 |

Détail : §16 (MVP) et §17 (Hors périmètre).

## 7. Description de la solution (vision fonctionnelle)

1. Un vendeur **de Tanger ou d'une commune voisine** s'inscrit librement, crée sa boutique et publie ses produits, visibles immédiatement [CONFIRMÉ — D9, D24, D33].
2. Les visiteurs et clients découvrent les produits par le catalogue, la recherche et les catégories [HYPOTHÈSE H1 : inclus dans « parcourir », D2], et consultent les notes, les avis et les conditions de retour [CONFIRMÉ — D13 ; affichage des conditions de retour : HYPOTHÈSE, conséquence de R1].
3. Le client, **connecté à son compte**, ajoute au panier des produits d'un ou plusieurs vendeurs, puis passe **une commande unique** livrée à **Tanger**, avec paiement à la livraison et **frais de livraison à sa charge** [CONFIRMÉ — D6, D12, D18, D20, D41].
4. La commande est répartie en **sous-commandes par vendeur**, et chaque vendeur accepte et prépare la sienne [HYPOTHÈSE]. **Si un vendeur refuse, la commande entière est annulée** [CONFIRMÉ — D22].
5. Quand toutes les sous-commandes sont prêtes, l'administrateur **transmet la commande à la société de livraison** (la commande passe « En collecte ») [CONFIRMÉ — D44]. La société de livraison collecte les produits chez chaque vendeur, livre l'ensemble **en une seule fois** et **encaisse une seule fois**, puis remet les fonds à la Plateforme ; **l'administrateur saisit les statuts** qu'elle lui transmet [CONFIRMÉ — D12, D19, D38 ; remise des fonds HYPOTHÈSE].
6. Pendant **7 jours après la réception**, le client peut **retourner un produit pour tout motif, y compris un changement d'avis**, sauf pour les produits légalement exclus (signalés par le vendeur ou appartenant à une catégorie exclue par l'administrateur) [CONFIRMÉ — D30, D35, D40]. **Chaque produit retourné fait l'objet d'un retour distinct** [CONFIRMÉ — D39]. La société de livraison reprend le produit ; **le vendeur le vérifie** et décide de sa remise en vente ; en cas de désaccord, **l'administrateur arbitre** ; le client est **remboursé dans le délai légal** par un moyen **traçable** [CONFIRMÉ — D31, D32, D43].
7. Les frais de retour sont **à la charge du client en cas de changement d'avis** (déduits de son remboursement), et **du vendeur en cas de défaut ou d'erreur**, lorsque la loi le prévoit [CONFIRMÉ — D30, D42].
8. Les sommes dues à chaque vendeur sont **retenues jusqu'à la fin du délai de retour**, puis deviennent disponibles et lui sont reversées **chaque semaine**, par virement ou en espèces, sans commission et après déduction des remboursements éventuels. Un remboursement intervenu après un reversement est **régularisé** sur le reversement suivant [CONFIRMÉ — D16, D21, D29, D34].
9. Après livraison, le client note et commente **uniquement les produits qu'il a reçus** ; l'administrateur peut masquer un avis abusif [CONFIRMÉ — D13, D37].

### Cycles de vie (vocabulaire métier, non technique)

- **Commande (client)** : En attente d'acceptation des vendeurs → Confirmée → **En collecte** (dès sa transmission à la société de livraison — CONFIRMÉ D44) → En livraison → **Livrée et payée** | Échec de livraison | Annulée (par le client ou suite au refus d'un vendeur). [Autres étapes : HYPOTHÈSE]
- **Sous-commande (vendeur)** : Nouvelle → Acceptée → Prête pour collecte → Collectée | Refusée | Annulée. [HYPOTHÈSE]
- **Retour (un produit d'une commande)** : Demandé → En reprise → Repris → Vérifié par le vendeur → Client remboursé | Contesté → Litige (arbitrage administrateur) → Client remboursé ou Retour refusé. [Granularité CONFIRMÉE — D39 ; étapes HYPOTHÈSE]
- **Montant vendeur** : Retenu (jusqu'à la fin du délai de retour) → Disponible → Reversé (hebdomadaire) | Déduit (retour remboursé, frais de retour imputés). [CONFIRMÉ — D29, D34]

## 8. Parcours utilisateurs

### P1 — Vendeur : de l'inscription au premier produit en ligne
1. Crée un compte vendeur et indique sa commune (Tanger ou commune voisine) ; informations exigées MANQUANT (Q22).
2. Renseigne sa boutique (nom, présentation, adresse de collecte) et son mode de reversement : virement bancaire ou espèces [CONFIRMÉ — D21 ; choix par le vendeur HYPOTHÈSE]. Il est informé du calendrier de paiement : retenue pendant le délai de retour, puis reversement hebdomadaire [SUGGESTION].
3. Ajoute un produit (nom, description, photos, prix, catégorie, stock, caractère périssable ou personnalisé).
4. Le produit est publié immédiatement [CONFIRMÉ — D9].
- *Exception* : informations obligatoires manquantes, donc publication impossible et champs indiqués.
- *Exception* : commune hors de la liste autorisée, donc inscription impossible, avec un message invitant à revenir lors de l'extension [CONFIRMÉ — D33 ; message et liste d'attente : SUGGESTION].

### P2 — Client : de la découverte à la livraison (parcours principal)
1. Découvre des produits (catalogue, recherche, catégorie) et consulte la fiche produit avec notes, avis et conditions de retour.
2. Ajoute des produits d'un ou plusieurs vendeurs au panier.
3. **Se connecte ou crée un compte**, obligatoire pour commander [CONFIRMÉ — D41].
4. Saisit ou choisit une adresse de livraison **à Tanger** et un téléphone.
5. Voit le récapitulatif : produits par vendeur, **frais de livraison**, total à payer à la livraison, rappel des conditions de retour.
6. Confirme la commande et reçoit une confirmation écrite (RG-026).
7. Est informé quand tous les vendeurs ont accepté, puis suit l'état de sa commande.
8. Reçoit la livraison groupée et paie en espèces au livreur (produits + frais de livraison).
9. Est invité à noter et commenter les produits reçus.
- *Exceptions* : produit devenu indisponible avant validation, donc retiré du panier avec message ; adresse hors de Tanger, donc refusée ; **un vendeur refuse ou ne répond pas, donc la commande entière est annulée et le client est informé** (D22) ; client absent ou refus à la livraison, donc échec de livraison (RG-013).

### P3 — Client : retour d'un produit
1. Dans les **7 jours** suivant la réception, depuis la commande, sélectionne le ou les produits à retourner ; **chaque produit donne lieu à un retour distinct**, avec sa quantité et son motif : **changement d'avis**, produit défectueux, incorrect ou non conforme à la description [CONFIRMÉ — D30, D39].
2. Est informé, avant de confirmer, des frais de retour **déduits de son remboursement** en cas de changement d'avis [CONFIRMÉ — D42].
3. Indique son moyen de remboursement : virement bancaire, ou autre moyen traçable et légalement autorisé s'il n'a pas de compte bancaire [CONFIRMÉ — D32 ; liste des moyens : Q42].
4. La demande est enregistrée automatiquement si le produit est dans le délai et n'est pas exclu [HYPOTHÈSE : le droit de retour ne nécessite pas d'acceptation préalable].
5. La société de livraison reprend le produit chez le client et le remet au vendeur ; l'administrateur saisit la reprise [CONFIRMÉ — D38].
6. **Le vendeur vérifie le produit** et le déclare conforme (remboursement) ou le conteste avec motif (ex. produit endommagé par le client, motif « défaut » non constaté) ; il indique s'il remet le produit en vente [CONFIRMÉ — D31, D43].
7. En cas de contestation, **l'administrateur arbitre le litige** [CONFIRMÉ — D31].
8. **L'administrateur enregistre le remboursement** dans le délai légal [CONFIRMÉ — D31] ; le client en est informé.
- *Exceptions* : délai de 7 jours dépassé, donc demande impossible ; produit signalé périssable/personnalisé par le vendeur ou appartenant à une catégorie exclue, donc demande impossible ; litige tranché en faveur du vendeur, donc retour refusé et produit renvoyé au client (HYPOTHÈSE).

### P4 — Vendeur : traitement d'une commande, des retours et paiement
1. Est notifié d'une nouvelle sous-commande.
2. L'accepte ou la refuse (avec motif) dans le délai fixé (Q19). Il est informé qu'un refus annule la commande entière du client.
3. Prépare les produits et les déclare « prêts pour collecte ».
4. Remet les produits au livreur de la société de livraison.
5. Après livraison et encaissement, voit le montant **retenu** jusqu'à la fin du délai de retour, puis **disponible**, puis **reversé** lors du reversement hebdomadaire.
6. En cas de retour, est informé du motif, reçoit le produit, le **vérifie** dans le délai fixé (Q44), le déclare conforme ou le conteste, et décide de sa **remise en vente** ; voit l'effet du retour et des frais imputés sur ses montants.

### P5 — Plateforme : collecte, livraison, encaissement, retours, reversement
1. L'administrateur voit les commandes dont toutes les sous-commandes sont prêtes.
2. Transmet la commande à la société de livraison (collecte chez chaque vendeur, livraison au client) ; la commande passe « En collecte » [CONFIRMÉ — D44].
3. **L'administrateur saisit** les statuts transmis par la société de livraison (collectée, en livraison, livrée et payée, échec, reprise de retour) [CONFIRMÉ — D38].
4. La société de livraison remet les montants encaissés à la Plateforme ; l'administrateur rapproche montants dus et montants reçus.
5. L'administrateur suit les retours en cours, arbitre les litiges et enregistre les remboursements dans le délai légal.
6. À la fin du délai de retour, les montants vendeurs non concernés par un retour en cours deviennent disponibles.
7. **Chaque semaine**, l'administrateur enregistre les reversements des montants disponibles, après déduction des remboursements et frais de retour imputés.

## 9. Modules fonctionnels

| Module | Rôle | Objectifs |
|---|---|---|
| M01 — Comptes et accès | Inscription, connexion, profils client et vendeur | O2, O3 |
| M02 — Boutique et catalogue vendeur | Création de boutique, gestion des produits et du stock | O1, O2 |
| M03 — Découverte | Catalogue public, recherche, catégories, fiche produit | O1, O3 |
| M04 — Panier et commande | Panier multi-vendeurs, passage de commande avec paiement à la livraison | O3 |
| M05 — Commandes vendeur | Réception, acceptation, préparation des sous-commandes | O2 |
| M06 — Livraison et encaissement | Transmission à la société de livraison, saisie des statuts par l'administrateur, échecs, rapprochement | O2, O3 |
| M07 — Reversements vendeurs | Montants retenus, disponibles, reversés chaque semaine ; régularisations | O2 |
| M08 — Avis et notes | Notation et commentaires clients sur les produits reçus | O1, O4 |
| M09 — Administration et modération | Vendeurs, produits, catégories, zones, commandes, avis | O1, O4, O5 |
| M10 — Notifications | Informations clés envoyées aux acteurs | O2, O3 |
| M11 — Retours | Demande (un retour par produit), reprise, vérification vendeur, litiges, remboursement | O3, O5 |

## 10. Fonctionnalités détaillées (MUST)

```text
F001 — Inscription et connexion client
Module : M01 | Statut : CONFIRMÉ — S1, D41 (compte obligatoire pour commander) | Priorité : MUST
Acteur(s) : Visiteur, Client
Description : créer un compte client, se connecter, se déconnecter, récupérer l'accès en cas d'oubli. Le compte est obligatoire pour passer commande.
Objectif : O3
Entrées : nom, téléphone (obligatoire pour la livraison — HYPOTHÈSE), e-mail (obligatoire ou non : MANQUANT), mot de passe.
Sorties : compte actif ; client connecté.
Règles métier : RG-014, RG-028
Exceptions : identifiant déjà utilisé, donc message et proposition de connexion ; identifiants erronés, donc message sans préciser lequel est faux.
Critères d'acceptation : CA-F001-1, CA-F001-2, CA-F001-3
```

```text
F002 — Inscription vendeur et création de boutique
Module : M01/M02 | Statut : CONFIRMÉ — D3, D9, D21, D24, D33 | Priorité : MUST
Acteur(s) : Vendeur
Description : un vendeur de Tanger ou d'une commune voisine autorisée s'inscrit librement et crée sa boutique (nom, présentation, commune, adresse de collecte, coordonnées) ; elle est active immédiatement. Il indique son mode de reversement : virement bancaire (avec coordonnées bancaires) ou espèces.
Objectif : O1, O2
Entrées : identité/raison sociale, téléphone, commune, adresse de collecte, mode de reversement, coordonnées bancaires si virement, présentation. Liste exacte : MANQUANT (Q22).
Sorties : boutique active ; accès à l'espace vendeur.
Règles métier : RG-004, RG-005, RG-016, RG-018, RG-023
Exceptions : informations obligatoires manquantes, donc inscription impossible ; virement choisi sans coordonnées bancaires, donc inscription impossible ; commune hors liste autorisée, donc inscription impossible avec message ; vendeur suspendu, donc boutique et produits invisibles (RG-015).
Critères d'acceptation : CA-F002-1, CA-F002-2, CA-F002-3
```

```text
F003 — Gestion des produits par le vendeur
Module : M02 | Statut : CONFIRMÉ — S1, D40 | Priorité : MUST
Acteur(s) : Vendeur
Description : ajouter, modifier, masquer ou supprimer ses produits ; gérer prix et stock ; signaler si le produit est périssable ou personnalisé (exclusion légale du droit de retour, D40).
Objectif : O1, O2
Entrées : nom, description, photos (au moins une — HYPOTHÈSE), prix en dirhams, catégorie, quantité en stock, origine (ville/région — HYPOTHÈSE), caractère périssable ou personnalisé.
Sorties : produit publié et visible dans le catalogue.
Règles métier : RG-006, RG-007, RG-015, RG-016, RG-019
Exceptions : stock à 0, donc produit affiché « indisponible » et non commandable ; prix ≤ 0, donc refusé ; produit présent dans une commande en cours, donc une modification de prix est sans effet sur cette commande.
Critères d'acceptation : CA-F003-1, CA-F003-2, CA-F003-3
```

```text
F004 — Catalogue, recherche et catégories
Module : M03 | Statut : HYPOTHÈSE H1 (déduit de « parcourir », S1) | Priorité : MUST
Acteur(s) : Visiteur, Client
Description : parcourir les produits disponibles, rechercher par mot-clé, filtrer par catégorie.
Objectif : O1, O3
Entrées : mot-clé, catégorie.
Sorties : liste de produits (photo, nom, prix, vendeur, note moyenne).
Règles métier : RG-006
Exceptions : aucun résultat, donc message et suggestion de catégories.
Critères d'acceptation : CA-F004-1, CA-F004-2
```

```text
F005 — Fiche produit
Module : M03 | Statut : CONFIRMÉ — S1 (parcourir), D13 (avis) ; affichage des conditions de retour HYPOTHÈSE (R1) | Priorité : MUST
Acteur(s) : Visiteur, Client
Description : afficher description, photos, prix, disponibilité, vendeur (nom, commune), conditions de retour (délai de 7 jours, frais en cas de changement d'avis, exclusion éventuelle), note moyenne et avis.
Objectif : O1, O3, O4
Sorties : informations du produit ; action « ajouter au panier » si disponible.
Règles métier : RG-006, RG-011, RG-019
Exceptions : produit masqué ou vendeur suspendu, donc page indisponible.
Critères d'acceptation : CA-F005-1
```

```text
F006 — Panier multi-vendeurs
Module : M04 | Statut : CONFIRMÉ — S1, D12 | Priorité : MUST
Acteur(s) : Visiteur (HYPOTHÈSE), Client
Description : ajouter des produits d'un ou plusieurs vendeurs, modifier les quantités, en retirer ; voir le sous-total par vendeur et le total des produits.
Objectif : O3
Règles métier : RG-003, RG-006
Exceptions : quantité demandée supérieure au stock, donc quantité limitée au stock avec message ; produit devenu indisponible, donc signalé et exclu du total.
Critères d'acceptation : CA-F006-1, CA-F006-2
```

```text
F007 — Passage de commande avec paiement à la livraison
Module : M04 | Statut : CONFIRMÉ — D6, D12, D18, D20, D41 | Priorité : MUST
Acteur(s) : Client (connecté)
Description : valider le panier en une commande unique, avec adresse de livraison à Tanger, téléphone, récapitulatif (produits par vendeur, frais de livraison à la charge du client, total, conditions de retour) et paiement à la livraison comme seul mode ; envoi d'une confirmation écrite. Un compte est obligatoire.
Objectif : O3
Entrées : adresse (quartier, adresse, repères — HYPOTHÈSE), téléphone, note de livraison éventuelle.
Sorties : commande « En attente d'acceptation des vendeurs » ; sous-commandes créées par vendeur ; confirmation écrite au client.
Règles métier : RG-001, RG-002, RG-003, RG-007, RG-008, RG-009, RG-017, RG-026, RG-028
Exceptions : visiteur non connecté, donc connexion ou création de compte demandée avant de poursuivre ; adresse hors de Tanger, donc commande impossible avec message ; stock insuffisant au moment de valider, donc validation bloquée et panier mis à jour.
Critères d'acceptation : CA-F007-1, CA-F007-2, CA-F007-3, CA-F007-4
```

```text
F008 — Suivi et annulation de commande par le client
Module : M04 | Statut : HYPOTHÈSE | Priorité : MUST
Acteur(s) : Client
Description : consulter ses commandes et leur statut ; annuler une commande tant qu'aucune sous-commande n'a été collectée.
Objectif : O3
Règles métier : RG-010
Exceptions : annulation demandée après le début de la collecte, donc refusée avec message (le client peut ensuite exercer son droit de retour après réception).
Critères d'acceptation : CA-F008-1, CA-F008-2
```

```text
F009 — Traitement des sous-commandes par le vendeur
Module : M05 | Statut : CONFIRMÉ (refus = annulation totale — D22) ; reste HYPOTHÈSE | Priorité : MUST
Acteur(s) : Vendeur
Description : voir ses sous-commandes (uniquement ses produits), les accepter ou les refuser (avec motif), les déclarer « prêtes pour collecte ». Le vendeur est averti qu'un refus annule la commande entière du client.
Objectif : O2
Règles métier : RG-003, RG-008, RG-011b
Exceptions : refus d'un vendeur, donc commande entière annulée, client et autres vendeurs informés, stocks restitués (D22) ; absence de réponse dans le délai (Q19), donc traitée comme un refus (HYPOTHÈSE).
Critères d'acceptation : CA-F009-1, CA-F009-2, CA-F009-3
```

```text
F010 — Collecte, livraison groupée et encaissement
Module : M06 | Statut : CONFIRMÉ — D12, D14, D19, D38, D44 | Priorité : MUST
Acteur(s) : Administrateur (principal) ; Société de livraison (acteur externe, sans accès à la Plateforme)
Description : l'administrateur voit les commandes prêtes ; les transmet à la société de livraison (la commande passe « En collecte ») ; saisit, à partir des informations de la société de livraison, chaque sous-commande collectée, la commande « en livraison », puis « livrée et payée » avec le montant encaissé et la date de réception (point de départ du délai de retour), ou « échec de livraison » avec motif ; rapproche les montants remis par la société de livraison avec les montants dus.
Objectif : O2, O3
Règles métier : RG-002, RG-008, RG-013, RG-020, RG-029
Exceptions : montant encaissé différent du montant dû, donc écart signalé à l'administrateur ; client injoignable ou refus, donc échec de livraison.
Critères d'acceptation : CA-F010-1, CA-F010-2, CA-F010-3, CA-F010-4
```

```text
F011 — Retenue, reversement hebdomadaire et régularisation des montants vendeurs
Module : M07 | Statut : CONFIRMÉ — D12, D16, D21, D29, D34 | Priorité : MUST
Acteur(s) : Vendeur, Administrateur
Description : pour chaque commande livrée et payée, calculer le montant dû à chaque vendeur ; le retenir jusqu'à la fin du délai de retour ; le rendre disponible ensuite ; chaque semaine, calculer pour chaque vendeur le montant à reverser (montants disponibles − remboursements et frais de retour imputés non encore déduits) ; l'administrateur enregistre le reversement effectué par virement bancaire ou en espèces ; le vendeur consulte ses montants retenus, disponibles, reversés et déduits.
Objectif : O2
Règles métier : RG-005, RG-012, RG-018, RG-021, RG-024, RG-025
Exceptions : commande en échec ou annulée, donc aucun montant dû ; retour en cours à la fin du délai, donc le montant du produit concerné reste retenu jusqu'à la clôture du retour (HYPOTHÈSE) ; aucun montant disponible une semaine donnée, donc pas de reversement ; solde vendeur négatif après régularisation, donc reporté sur les semaines suivantes et signalé à l'administrateur (HYPOTHÈSE, Q38) ; reversement en espèces, donc preuve de remise enregistrée (HYPOTHÈSE).
Critères d'acceptation : CA-F011-1, CA-F011-2, CA-F011-3, CA-F011-4, CA-F011-5
```

```text
F012 — Avis et notes clients
Module : M08 | Statut : CONFIRMÉ — D13, D37 | Priorité : MUST
Acteur(s) : Client
Description : après livraison, noter (1 à 5 — HYPOTHÈSE) et commenter chaque produit reçu ; seuls les produits effectivement reçus peuvent être notés ; la note moyenne est affichée sur le produit et la boutique.
Objectif : O1, O4
Règles métier : RG-011
Exceptions : produit non reçu, donc avis impossible ; second avis sur le même produit d'une même commande, donc modification de l'avis existant.
Critères d'acceptation : CA-F012-1, CA-F012-2
```

```text
F013 — Administration et modération
Module : M09 | Statut : CONFIRMÉ — D37, D40 ; périmètre de supervision HYPOTHÈSE | Priorité : MUST
Acteur(s) : Administrateur
Description : gérer les catégories et leurs exclusions légales du droit de retour, la zone clients (Tanger) et la liste des communes vendeurs autorisées ; consulter vendeurs, produits, commandes, retours, montants ; masquer un produit non conforme ; suspendre un vendeur ; masquer un avis abusif.
Objectif : O4, O5 (qualité, confiance et conformité, indispensable avec l'inscription libre D9)
Règles métier : RG-001, RG-015, RG-016, RG-019, RG-023
Exceptions : suspension d'un vendeur ayant des sous-commandes ou des retours en cours, donc l'administrateur décide de leur sort (honorer ou annuler) ; les droits de retour des clients restent garantis.
Critères d'acceptation : CA-F013-1, CA-F013-2, CA-F013-3
```

```text
F014 — Notifications essentielles
Module : M10 | Statut : HYPOTHÈSE | Priorité : MUST
Acteur(s) : Client, Vendeur
Description : informer le client (commande reçue, confirmée, annulée et pourquoi, en livraison, livrée, retour enregistré, repris, contesté, remboursé) et le vendeur (nouvelle sous-commande, annulation, collecte, retour à vérifier, issue d'un litige, montant disponible, reversement hebdomadaire). Canal : MANQUANT (SMS, e-mail, WhatsApp… — Q23).
Objectif : O2, O3
Critères d'acceptation : CA-F014-1, CA-F014-2
```

```text
F022 — Retour d'un produit
Module : M11 | Statut : CONFIRMÉ — D23, D25, D30, D31, D32, D35, D39, D40, D42, D43 ; conformité à valider juridiquement (C-08) | Priorité : MUST
Acteur(s) : Client, Vendeur, Administrateur ; Société de livraison (acteur externe)
Description : dans les 7 jours suivant la réception, le client demande le retour d'un ou plusieurs produits non exclus, pour tout motif (changement d'avis, défaut, erreur, non-conformité), et indique un moyen de remboursement traçable. Chaque produit retourné constitue un retour distinct, avec sa quantité, son motif, sa vérification et son remboursement propres. La société de livraison reprend le produit et le remet au vendeur (reprise saisie par l'administrateur) ; le vendeur vérifie le produit, le déclare conforme ou le conteste, et décide de sa remise en vente ; l'administrateur arbitre les litiges et enregistre le remboursement dans le délai légal ; les frais de retour sont imputés selon le motif ; les montants du vendeur sont ajustés.
Objectif : O3, O5
Entrées : commande, produit, quantité, motif, photo (HYPOTHÈSE ; utile pour un défaut), moyen de remboursement et ses coordonnées.
Sorties : retour enregistré et suivi jusqu'au remboursement ou au refus après litige.
Règles métier : RG-017, RG-019, RG-021, RG-022, RG-024, RG-025, RG-027, RG-030
Exceptions : délai de 7 jours dépassé, donc demande impossible ; produit signalé périssable ou personnalisé par le vendeur, ou appartenant à une catégorie exclue par l'administrateur, donc demande impossible avec la raison ; vendeur qui ne vérifie pas dans le délai (Q44), donc l'administrateur prend la décision (HYPOTHÈSE) ; litige tranché en faveur du vendeur, donc retour refusé et produit renvoyé au client (HYPOTHÈSE).
Critères d'acceptation : CA-F022-1 à CA-F022-9
```

## 11. Règles métier

| ID | Règle | Fonctionnalités | Statut |
|---|---|---|---|
| RG-001 | Au lancement, la livraison n'est possible qu'à une adresse **à Tanger**. L'administrateur peut ajouter d'autres villes plus tard. | F007, F013 | CONFIRMÉ — D15, D18 ; ajout de villes : HYPOTHÈSE (ENF-010) |
| RG-002 | Le seul mode de paiement est le paiement à la livraison, encaissé par la société de livraison pour le compte de la Plateforme. | F007, F010 | CONFIRMÉ — D6, D12, D19 |
| RG-003 | Une commande peut contenir des produits de plusieurs vendeurs ; elle est répartie en une sous-commande par vendeur ; chaque vendeur ne voit que sa sous-commande. | F006, F007, F009 | CONFIRMÉ (multi-vendeurs — D12) ; répartition HYPOTHÈSE |
| RG-004 | L'inscription vendeur est libre (dans la zone vendeurs, RG-023) ; la boutique et les produits sont visibles dès leur publication, sans validation préalable. | F002, F003 | CONFIRMÉ — D9 |
| RG-005 | Aucun frais d'inscription, abonnement ni commission n'est prélevé aux vendeurs en V1. Les frais de retour imputés en cas de défaut ou d'erreur (RG-025) ne sont pas une commission. | F002, F011 | CONFIRMÉ — D16, D30 |
| RG-006 | Un produit n'est visible et commandable que s'il est publié, non masqué, que son stock est supérieur à 0 et que son vendeur est actif. | F003–F007 | HYPOTHÈSE (masquage CONFIRMÉ — D37) |
| RG-007 | Les prix sont en dirhams marocains (MAD) ; le prix appliqué est celui affiché au moment de la validation de la commande. | F003, F007 | HYPOTHÈSE |
| RG-008 | **Pas de livraison partielle** : une commande n'est livrée que si **toutes** ses sous-commandes sont acceptées et collectées ; elle est livrée et encaissée en une seule fois. Si un vendeur refuse, la commande entière est annulée. | F007, F009, F010 | CONFIRMÉ — D12, D22 |
| RG-009 | Montant payé par le client = somme des produits + frais de livraison. **Les frais de livraison sont à la charge du client.** Montant des frais : MANQUANT ; un seul forfait par commande, même multi-vendeurs : HYPOTHÈSE. | F007 | CONFIRMÉ — D20 ; montant MANQUANT (Q27) |
| RG-010 | Le client peut annuler sa commande tant qu'aucune sous-commande n'a été collectée. | F008 | HYPOTHÈSE |
| RG-011 | Seul un client dont la commande est « livrée et payée » peut noter/commenter les produits de cette commande ; un avis par produit et par commande. | F005, F012 | CONFIRMÉ — D37 (un avis par produit et par commande : HYPOTHÈSE) |
| RG-011b | Le vendeur doit accepter ou refuser une sous-commande dans un délai défini ; sans réponse dans ce délai, la sous-commande est traitée comme refusée (donc la commande est annulée, RG-008). | F009 | Délai MANQUANT (Q19) ; traitement comme refus HYPOTHÈSE (déduit de D22) |
| RG-012 | Montant dû au vendeur = valeur de ses produits livrés et payés, moins les produits retournés et remboursés, moins les frais de retour qui lui sont imputés (RG-025), sans commission (RG-005). | F011 | CONFIRMÉ (principe — D12, D16, D29, D30) |
| RG-013 | Échec de livraison (client absent, injoignable, refus) : la commande passe en « échec », aucun montant n'est dû aux vendeurs ; nouvelle tentative et retour des produits aux vendeurs à définir. | F010 | HYPOTHÈSE (Q24) |
| RG-014 | Un téléphone valide est obligatoire pour passer commande (livraison et paiement à la livraison). | F001, F007 | HYPOTHÈSE |
| RG-015 | L'administrateur peut **masquer un produit, suspendre un vendeur ou masquer un avis** ; l'élément masqué ou suspendu n'est plus visible publiquement, et le vendeur concerné en est informé. | F002, F003, F013 | CONFIRMÉ — D37 |
| RG-016 | Seuls des produits locaux marocains peuvent être vendus ; définition de « produit local » à préciser. | F002, F003, F013 | CONFIRMÉ (principe — D1) ; définition MANQUANT (Q17) |
| RG-017 | Le stock d'un produit est réservé à la validation de la commande et restitué en cas d'annulation, de refus vendeur ou d'échec de livraison. Pour un produit retourné, le stock n'est restitué que si **le vendeur décide, après vérification, de le remettre en vente**. | F003, F007–F010, F022 | CONFIRMÉ (remise en vente par le vendeur — D43) ; réservation et restitution HYPOTHÈSE |
| RG-018 | Les reversements aux vendeurs ont lieu **chaque semaine**, **uniquement pour les montants disponibles** après la période de retenue (RG-024) et **après déduction des remboursements** et frais de retour imputés. Ils se font par virement bancaire ou en espèces, selon le mode choisi par le vendeur. Jour du reversement : à fixer. | F002, F011 | CONFIRMÉ — D21, D34 ; choix du mode par le vendeur HYPOTHÈSE ; jour MANQUANT (non bloquant) |
| RG-019 | **Droit de retour** : le client peut retourner un produit **dans les 7 jours suivant sa réception, pour tout motif, y compris un simple changement d'avis**, sans avoir à se justifier. **Exclusions uniquement lorsque la loi le permet**, notamment les produits **périssables** et **personnalisés** ; le cas des **cosmétiques ouverts** reste à confirmer juridiquement. Un produit est exclu **si le vendeur l'a signalé périssable ou personnalisé, ou si sa catégorie est marquée exclue par l'administrateur**. Les conditions de retour sont affichées sur la fiche produit et rappelées à la commande. | F003, F005, F007, F013, F022 | CONFIRMÉ — D25, D30, D35, D40 ; cosmétiques ouverts MANQUANT (Q43) ; conformité à valider (C-08) |
| RG-020 | La société de livraison remet à la Plateforme la totalité des montants encaissés ; chaque remise est rapprochée des commandes livrées et payées. | F010 | HYPOTHÈSE (conséquence de D19 + D14) |
| RG-021 | Le montant d'un produit retourné et remboursé est déduit des montants du vendeur : s'il est encore retenu, il est annulé ; s'il a déjà été reversé, il est **régularisé** sur le reversement hebdomadaire suivant. | F011, F022 | CONFIRMÉ — D29, D34 |
| RG-022 | Le client est remboursé **de façon traçable** : par **virement bancaire**, ou par **un autre moyen de paiement traçable et légalement autorisé** s'il n'a pas de compte bancaire. Le remboursement intervient **dans le délai légal** (15 jours après l'exercice du droit selon R1, à confirmer juridiquement). Montant remboursé : prix du produit retourné, **moins les frais de retour en cas de changement d'avis** (déduits, pas facturés à part). Remboursement des frais de livraison initiaux : à confirmer juridiquement (R1 mentionne le « montant total payé »). Aucun remboursement en espèces non traçable. | F022 | CONFIRMÉ — D28, D31, D32, D42 ; liste des moyens alternatifs MANQUANT (Q42) ; frais de livraison initiaux MANQUANT (Q40) |
| RG-023 | Au lancement, seuls les vendeurs situés **à Tanger ou dans une commune voisine figurant sur une liste fixée par l'administrateur** peuvent s'inscrire. La liste exacte est définie avant le lancement ; l'administrateur peut l'étendre. | F002, F013 | CONFIRMÉ — D24, D33 ; liste MANQUANT, à fixer avant lancement (Q41) |
| RG-024 | Les sommes dues à un vendeur pour une commande livrée et payée sont **retenues jusqu'à la fin du délai de retour** (7 jours après la réception), puis deviennent disponibles pour le reversement hebdomadaire. Le montant d'un produit faisant l'objet d'un retour en cours reste retenu jusqu'à la clôture du retour. | F011 | CONFIRMÉ — D29, D34 ; cas du retour en cours HYPOTHÈSE |
| RG-025 | **Frais de retour** : **à la charge du client en cas de changement d'avis** (déduits de son remboursement, RG-022) ; **à la charge du vendeur en cas de défaut ou d'erreur** (produit défectueux, incorrect ou non conforme), lorsque la loi le prévoit. Les frais imputés au vendeur sont déduits de ses montants. Montant des frais de retour : MANQUANT. | F011, F022 | CONFIRMÉ — D27, D30, D42 ; montant MANQUANT (Q45) |
| RG-026 | Après validation, le client reçoit une confirmation écrite de sa commande comprenant au minimum : produits, prix, frais de livraison, identité des vendeurs, existence et conditions du droit de retour. | F007, F014 | HYPOTHÈSE (déduite de R1 ; contenu exact à valider juridiquement) |
| RG-027 | **Vérification et litiges** : le vendeur vérifie chaque produit retourné et le déclare conforme ou le conteste avec motif dans un délai défini ; la qualification du motif (changement d'avis ou défaut/erreur) peut être contestée par le vendeur ; tout désaccord est arbitré par l'administrateur, dont la décision est finale ; le traitement ne doit pas faire dépasser le délai légal de remboursement. | F022 | CONFIRMÉ (rôles — D31) ; délai de vérification MANQUANT (Q44) ; décision finale de l'administrateur HYPOTHÈSE |
| RG-028 | **Un compte client est obligatoire pour passer commande.** Un visiteur peut consulter le catalogue ; il doit se connecter ou créer un compte avant de valider sa commande. | F001, F007 | CONFIRMÉ — D41 |
| RG-029 | **Seul l'administrateur saisit sur la Plateforme** les statuts de collecte, de livraison, d'encaissement et de reprise des retours, à partir des informations transmises par la société de livraison ; celle-ci n'a pas d'accès à la Plateforme en V1. Une commande passe « **En collecte** » dès que l'administrateur l'a transmise à la société de livraison. | F010, F022 | CONFIRMÉ — D38, D44 |
| RG-030 | **Un retour par produit** : lorsqu'un client retourne plusieurs produits d'une même commande, chaque produit (ligne de commande) fait l'objet d'un retour distinct, avec sa quantité, son motif, sa vérification, son éventuel litige et son remboursement propres. | F022 | CONFIRMÉ — D39 |

**Décompte** : 31 règles métier (RG-001 à RG-030, plus RG-011b). La v1.0 en annonçait 27 alors qu'elle en définissait 28 (erreur de décompte relevée par Blueprint, N10) ; la v1.1 ajoute RG-028, RG-029 et RG-030.

## 12. Exigences fonctionnelles — récapitulatif

| ID | Fonctionnalité | Module | Priorité | Statut |
|---|---|---|---|---|
| F001 | Inscription et connexion client (compte obligatoire pour commander) | M01 | MUST | CONFIRMÉ |
| F002 | Inscription vendeur (Tanger et communes voisines) et boutique | M01/M02 | MUST | CONFIRMÉ |
| F003 | Gestion des produits vendeur | M02 | MUST | CONFIRMÉ |
| F004 | Catalogue, recherche, catégories | M03 | MUST | HYPOTHÈSE H1 |
| F005 | Fiche produit | M03 | MUST | CONFIRMÉ |
| F006 | Panier multi-vendeurs | M04 | MUST | CONFIRMÉ |
| F007 | Commande avec paiement à la livraison (Tanger) | M04 | MUST | CONFIRMÉ |
| F008 | Suivi / annulation de commande client | M04 | MUST | HYPOTHÈSE |
| F009 | Traitement des sous-commandes vendeur | M05 | MUST | CONFIRMÉ / HYPOTHÈSE |
| F010 | Collecte, livraison groupée, encaissement (statuts saisis par l'administrateur) | M06 | MUST | CONFIRMÉ |
| F011 | Retenue, reversement hebdomadaire, régularisation | M07 | MUST | CONFIRMÉ |
| F012 | Avis et notes (produits reçus uniquement) | M08 | MUST | CONFIRMÉ |
| F013 | Administration et modération | M09 | MUST | CONFIRMÉ |
| F014 | Notifications essentielles | M10 | MUST | HYPOTHÈSE |
| F022 | Retour d'un produit (7 jours, tout motif, un retour par produit, vérification vendeur, litiges) | M11 | MUST | CONFIRMÉ |
| F015 | Page publique de la boutique (présentation, commune, produits, note moyenne) | M03 | SHOULD | SUGGESTION (renforce O1) |
| F016 | Tableau de bord vendeur simple (commandes, ventes, montants) | M05/M07 | SHOULD | SUGGESTION |
| F017 | Carnet d'adresses client | M04 | SHOULD | SUGGESTION |
| F018 | Recherche / filtre par région ou ville d'origine | M03 | COULD | SUGGESTION |
| F019 | Produits / vendeurs mis en avant en page d'accueil | M03/M09 | COULD | SUGGESTION |
| F020 | Partage d'un produit sur les réseaux sociaux et messageries | M03 | COULD | SUGGESTION |
| F021 | Favoris client | M03 | COULD | SUGGESTION |

## 13. Exigences non fonctionnelles

| ID | Catégorie | Exigence | Statut |
|---|---|---|---|
| ENF-001 | Langues | L'interface est disponible dans les langues retenues ; langues : MANQUANT (proposition : français + arabe). | MANQUANT (Q11) |
| ENF-002 | Accessibilité mobile | Tous les parcours (client, vendeur, administrateur) sont utilisables sur smartphone, écran de 360 px de large minimum. | HYPOTHÈSE |
| ENF-003 | Simplicité vendeur | Un vendeur sans compétence technique publie son premier produit sans assistance, en moins de 10 minutes. | HYPOTHÈSE (valeur à valider) |
| ENF-004 | Performance | Pages catalogue et fiche produit affichées en moins de 3 s sur connexion mobile 4G pour 95 % des consultations. | HYPOTHÈSE (valeur à valider) |
| ENF-005 | Disponibilité | Plateforme disponible 99 % du temps, hors maintenance annoncée. | HYPOTHÈSE (valeur à valider) |
| ENF-006 | Volumes | Nombre de vendeurs, produits et commandes attendus à Tanger à 12 mois : MANQUANT. | MANQUANT (Q21) |
| ENF-007 | Sécurité | Accès par compte personnel ; chaque vendeur n'accède qu'à ses données ; actions d'administration réservées aux administrateurs ; aucun accès de la société de livraison à la Plateforme en V1 (D38) ; mots de passe jamais affichés. | CONFIRMÉ (société de livraison — D38) ; reste HYPOTHÈSE |
| ENF-008 | Traçabilité financière | Chaque encaissement, remise de fonds par la société de livraison, écart, retenue, mise à disposition, remboursement client (moyen, référence, date), frais de retour imputé, décision de litige, régularisation et reversement hebdomadaire (virement ou espèces) est historisé (qui, quand, montant, motif) et consultable par l'administrateur. Chaque saisie de statut de livraison par l'administrateur est historisée. | CONFIRMÉ (remboursement traçable — D28, D32 ; régularisation — D29) ; périmètre détaillé HYPOTHÈSE |
| ENF-009 | Conformité légale | Les parcours de commande et de retour respectent la loi 31-08 sur la protection du consommateur (information précontractuelle, confirmation écrite, droit de rétractation de 7 jours, exclusions, délais de remboursement, frais de retour) et la loi 09-08 sur les données personnelles (CNDP). **Validation juridique obligatoire avant lancement.** | CONFIRMÉ — D30 ; exigences précises à confirmer (R1) |
| ENF-010 | Évolutivité fonctionnelle | De nouvelles villes clients, de nouvelles communes vendeurs, le paiement en ligne, la livraison internationale, un modèle de revenus vendeur, un accès direct de la société de livraison et d'autres modes de livraison doivent pouvoir être ajoutés sans refondre les parcours V1. | CONFIRMÉ (principe — D5, D24) |
| ENF-011 | Lisibilité des photos | Photos produits affichées de façon lisible sur mobile. | HYPOTHÈSE |
| ENF-012 | Délai de remboursement | 100 % des remboursements de retours sont enregistrés dans le délai légal (15 jours après la demande selon R1, à confirmer) ; tout retour approchant ce délai est signalé à l'administrateur. | CONFIRMÉ (délai légal — D31) ; valeur exacte et alerte HYPOTHÈSE |

## 14. User Stories

```text
US-001 — Ouvrir ma boutique sans aide  (F002, MUST)
En tant que petit vendeur local de Tanger ou d'une commune voisine,
je veux créer ma boutique en ligne par moi-même,
afin d'être visible par des clients au-delà de mon entourage.

US-002 — Publier un produit  (F003, MUST)
En tant que vendeur,
je veux publier un produit avec photos, prix et stock,
afin que des clients puissent le découvrir et le commander.

US-003 — Trouver un produit local  (F004, MUST)
En tant que visiteur à Tanger,
je veux rechercher et filtrer les produits par catégorie,
afin de trouver rapidement le produit local que je cherche.

US-004 — Choisir en confiance  (F005, F012, MUST)
En tant que client,
je veux voir la note moyenne, les avis et les conditions de retour d'un produit,
afin de choisir un vendeur que je ne connais pas sans prendre de risque.

US-005 — Commander chez plusieurs vendeurs en une fois  (F006, F007, MUST)
En tant que client à Tanger,
je veux regrouper dans un seul panier des produits de plusieurs vendeurs et tout payer une seule fois à la livraison, frais de livraison compris,
afin de ne pas multiplier les commandes ni payer en ligne.

US-006 — Savoir où en est ma commande  (F008, F014, MUST)
En tant que client,
je veux connaître l'état de ma commande, y compris son annulation éventuelle et sa raison,
afin de savoir quand préparer le paiement et être disponible à la livraison.

US-007 — Traiter mes commandes  (F009, MUST)
En tant que vendeur,
je veux être averti d'une nouvelle commande et l'accepter ou la refuser,
afin de ne m'engager que sur ce que je peux réellement préparer.

US-008 — Rendre compte des livraisons et des encaissements  (F010, MUST)
En tant qu'administrateur,
je veux saisir la collecte, la livraison et le montant encaissé que me transmet la société de livraison,
afin de savoir précisément ce qui a été livré, payé et ce que je dois à chaque vendeur.

US-009 — Être payé chaque semaine  (F011, MUST)
En tant que vendeur,
je veux voir quels montants sont retenus, disponibles et déjà versés, et recevoir chaque semaine mes montants disponibles par virement ou en espèces,
afin de savoir quand et combien je serai payé.

US-010 — Partager mon expérience  (F012, MUST)
En tant que client ayant reçu ma commande,
je veux noter et commenter les produits reçus,
afin d'aider les autres clients et de récompenser les bons vendeurs.

US-011 — Protéger le catalogue  (F013, MUST)
En tant qu'administrateur,
je veux masquer un produit non local, suspendre un vendeur abusif ou masquer un avis abusif,
afin de préserver la confiance des clients malgré l'inscription libre.

US-012 — Annuler une commande  (F008, MUST)
En tant que client,
je veux annuler ma commande avant sa collecte,
afin de ne pas être livré d'une commande que je ne veux plus.

US-013 — Retourner un produit  (F022, MUST)
En tant que client ayant reçu un produit qui ne me convient pas, quelle qu'en soit la raison,
je veux demander son retour dans les 7 jours et être remboursé de façon traçable,
afin d'acheter à un vendeur inconnu sans craindre de perdre mon argent.

US-014 — Vérifier un produit retourné  (F022, MUST)
En tant que vendeur,
je veux vérifier l'état d'un produit qui m'est retourné, contester un retour abusif et décider s'il peut être remis en vente,
afin de ne pas supporter le coût d'un produit endommagé ou d'un motif injustifié.

US-015 — Arbitrer un litige de retour  (F022, MUST)
En tant qu'administrateur,
je veux trancher les désaccords entre client et vendeur sur un retour et enregistrer le remboursement,
afin que chaque client soit remboursé équitablement dans le délai légal.
```

## 15. Critères d'acceptation (fonctionnalités MUST)

| ID | Critère (Étant donné / Quand / Alors) |
|---|---|
| CA-F001-1 | Étant donné un visiteur sans compte, quand il s'inscrit avec un téléphone valide et non utilisé, alors son compte client est créé et il est connecté. |
| CA-F001-2 | Étant donné un téléphone déjà utilisé, quand un visiteur tente de s'inscrire avec, alors l'inscription est refusée et la connexion lui est proposée. |
| CA-F001-3 | Étant donné un visiteur non connecté avec un panier rempli, quand il veut valider sa commande, alors il doit se connecter ou créer un compte, et retrouve son panier ensuite. |
| CA-F002-1 | Étant donné un visiteur situé dans une commune autorisée, quand il complète l'inscription vendeur avec toutes les informations obligatoires, alors sa boutique est active immédiatement, sans validation (RG-004). |
| CA-F002-2 | Étant donné un vendeur qui choisit le reversement par virement, quand il valide son inscription sans coordonnées bancaires, alors l'inscription est refusée et le champ manquant est indiqué. |
| CA-F002-3 | Étant donné une commune absente de la liste des communes autorisées, quand le visiteur valide son inscription vendeur, alors l'inscription est refusée avec un message indiquant que la Plateforme n'accepte pour le moment que les vendeurs de Tanger et des communes voisines. |
| CA-F003-1 | Étant donné un vendeur actif, quand il publie un produit complet avec un stock supérieur à 0, alors le produit apparaît dans le catalogue public. |
| CA-F003-2 | Étant donné un produit publié, quand son stock passe à 0, alors il s'affiche « indisponible » et ne peut pas être ajouté au panier. |
| CA-F003-3 | Étant donné un vendeur A, quand il consulte la gestion des produits, alors il ne voit et ne modifie que ses propres produits. |
| CA-F004-1 | Étant donné des produits publiés, quand un visiteur recherche un mot présent dans le nom d'un produit, alors ce produit figure dans les résultats. |
| CA-F004-2 | Étant donné un produit masqué ou d'un vendeur suspendu, quand un visiteur parcourt ou recherche, alors ce produit n'apparaît pas. |
| CA-F005-1 | Étant donné un produit ayant des avis, quand un visiteur ouvre sa fiche, alors il voit la note moyenne, le nombre d'avis, les avis, le vendeur, sa commune et les conditions de retour (délai de 7 jours, frais en cas de changement d'avis, exclusion éventuelle). |
| CA-F006-1 | Étant donné un panier contenant des produits de deux vendeurs, quand le client l'affiche, alors il voit les produits regroupés par vendeur, le sous-total de chacun et le total. |
| CA-F006-2 | Étant donné un produit au stock de 3, quand le client demande 5 unités, alors la quantité est limitée à 3 avec un message. |
| CA-F007-1 | Étant donné un client connecté avec un panier valide et une adresse à Tanger, quand il confirme, alors une commande unique est créée avec paiement à la livraison, une sous-commande par vendeur, et le client reçoit une confirmation écrite conforme à RG-026. |
| CA-F007-2 | Étant donné une adresse hors de Tanger, quand le client tente de confirmer, alors la commande est refusée avec un message indiquant que seule Tanger est desservie pour le moment. |
| CA-F007-3 | Étant donné l'écran de confirmation, quand le client choisit le paiement, alors seul « paiement à la livraison » est proposé. |
| CA-F007-4 | Étant donné un panier de 200 MAD de produits, quand le client affiche le récapitulatif, alors il voit les frais de livraison séparément et un total égal à 200 MAD + frais de livraison. |
| CA-F008-1 | Étant donné une commande dont aucune sous-commande n'est collectée, quand le client l'annule, alors elle passe « annulée », les vendeurs sont informés et le stock est restitué. |
| CA-F008-2 | Étant donné une commande en collecte, quand le client tente de l'annuler, alors l'annulation est refusée avec un message. |
| CA-F009-1 | Étant donné une commande contenant des produits des vendeurs A et B, quand A consulte ses sous-commandes, alors il ne voit que ses produits, les quantités et les informations nécessaires à la préparation. |
| CA-F009-2 | Étant donné une sous-commande acceptée, quand le vendeur la déclare prête, alors elle apparaît « prête pour collecte » pour l'administrateur. |
| CA-F009-3 | Étant donné une commande des vendeurs A et B, quand B refuse sa sous-commande, alors la commande entière passe « annulée », le client et A sont informés, et le stock des produits de A et de B est restitué. |
| CA-F010-1 | Étant donné une commande dont toutes les sous-commandes sont collectées, quand l'administrateur la marque « livrée et payée » avec le montant encaissé, alors la commande est close, la date de réception est enregistrée et les montants des vendeurs sont calculés au statut « retenu ». |
| CA-F010-2 | Étant donné un montant encaissé différent du montant dû, quand il est enregistré, alors l'écart est signalé à l'administrateur. |
| CA-F010-3 | Étant donné un client absent ou refusant le colis, quand l'administrateur déclare l'échec avec un motif, alors la commande passe « échec de livraison » et aucun montant n'est dû aux vendeurs. |
| CA-F010-4 | Étant donné une commande dont toutes les sous-commandes sont prêtes, quand l'administrateur la transmet à la société de livraison, alors la commande passe « En collecte » et le client ne peut plus l'annuler. |
| CA-F011-1 | Étant donné une commande reçue le jour J contenant 300 MAD de produits du vendeur A et sans demande de retour, quand le délai de retour de 7 jours expire, alors les 300 MAD passent de « retenu » à « disponible », sans commission ni frais de livraison. |
| CA-F011-2 | Étant donné un reversement enregistré par l'administrateur, quand le vendeur consulte son historique, alors il voit le montant, la date, le mode (virement ou espèces) et les commandes concernées. |
| CA-F011-3 | Étant donné un produit de 100 MAD retourné pour défaut et remboursé alors que son montant est encore retenu, quand le remboursement est enregistré, alors les 100 MAD et les frais de retour imputés au vendeur sont déduits de ses montants retenus. |
| CA-F011-4 | Étant donné un vendeur déjà payé pour un produit de 100 MAD ensuite remboursé, quand son reversement hebdomadaire suivant est calculé, alors 100 MAD (et les frais de retour imputés, le cas échéant) en sont déduits et la régularisation apparaît dans son historique. |
| CA-F011-5 | Étant donné un vendeur ayant 500 MAD disponibles et 80 MAD de déductions en attente au moment du reversement hebdomadaire, quand le reversement est calculé, alors le montant à reverser est de 420 MAD et les montants encore retenus ne sont pas inclus. |
| CA-F012-1 | Étant donné une commande livrée et payée, quand le client note un produit reçu, alors la note est enregistrée et la moyenne du produit est mise à jour. |
| CA-F012-2 | Étant donné un client n'ayant pas reçu un produit, quand il consulte ce produit, alors l'action « noter » ne lui est pas proposée. |
| CA-F013-1 | Étant donné un produit signalé comme non local, quand l'administrateur le masque, alors il disparaît du catalogue et le vendeur en est informé. |
| CA-F013-2 | Étant donné un vendeur suspendu, quand un visiteur parcourt la Plateforme, alors ni la boutique ni ses produits ne sont visibles. |
| CA-F013-3 | Étant donné un avis jugé abusif, quand l'administrateur le masque, alors il n'est plus affiché et la note moyenne du produit est recalculée sans lui. |
| CA-F014-1 | Étant donné une commande passée, quand elle est créée, alors le client et chaque vendeur concerné reçoivent une notification. |
| CA-F014-2 | Étant donné une commande annulée suite au refus d'un vendeur, quand l'annulation intervient, alors le client reçoit une notification indiquant que la commande est annulée parce qu'un produit n'est pas disponible. |
| CA-F022-1 | Étant donné un produit non exclu reçu depuis 7 jours ou moins, quand le client demande son retour pour changement d'avis, alors la demande est enregistrée sans justification supplémentaire, les frais de retour qui seront déduits de son remboursement lui sont indiqués avant confirmation, et le vendeur et l'administrateur sont informés. |
| CA-F022-2 | Étant donné un produit reçu depuis plus de 7 jours, quand le client consulte la commande, alors la demande de retour ne lui est pas proposée. |
| CA-F022-3 | Étant donné un produit marqué périssable ou personnalisé par le vendeur, quand le client consulte la commande, alors la demande de retour n'est pas proposée pour ce produit et la raison est indiquée. |
| CA-F022-4 | Étant donné un client sans compte bancaire, quand il demande un retour, alors il peut choisir un autre moyen de remboursement traçable autorisé, et aucun remboursement en espèces non traçable n'est proposé. |
| CA-F022-5 | Étant donné un produit de 100 MAD retourné pour défaut, repris et déclaré conforme au motif par le vendeur, quand l'administrateur enregistre le remboursement, alors le client est remboursé de 100 MAD, les frais de retour sont imputés au vendeur, et le moyen, la référence et la date du remboursement sont enregistrés. |
| CA-F022-6 | Étant donné un produit retourné que le vendeur conteste avec motif, quand la contestation est enregistrée, alors le retour passe « Litige », l'administrateur est informé, et sa décision fixe le remboursement et l'imputation des frais. |
| CA-F022-7 | Étant donné un retour dont la demande date de plus de 12 jours sans remboursement enregistré, quand l'administrateur consulte les retours, alors ce retour est signalé comme proche du délai légal (ENF-012). |
| CA-F022-8 | Étant donné un produit non signalé par le vendeur mais appartenant à une catégorie marquée exclue par l'administrateur, quand le client consulte la commande, alors la demande de retour n'est pas proposée pour ce produit et la raison est indiquée. |
| CA-F022-9 | Étant donné une commande contenant les produits P1 (vendeur A) et P2 (vendeur B), quand le client demande le retour des deux, alors deux retours distincts sont créés, chacun vérifié par son vendeur et remboursé séparément. |

## 16. MVP (MoSCoW)

**Méthode** : MoSCoW (produit non lancé, aucune donnée d'usage, besoin de trancher vite, cf. `prioritization-advisor`).

| Priorité | Contenu | Justification |
|---|---|---|
| **MUST** | F001–F014, F022 | Plus petit ensemble permettant le parcours complet à Tanger : le vendeur publie, le client découvre, commande multi-vendeurs, la société de livraison collecte, livre et encaisse, l'administrateur saisit les statuts, la Plateforme retient puis reverse chaque semaine, le client donne son avis et peut exercer son droit de retour. F012 répond à D13, F013 est nécessaire car l'inscription est libre (D9, D37), F011 car la Plateforme détient l'argent des vendeurs (D29, D34), F022 car le droit de retour est une décision confirmée (D30) et une obligation légale (R1). |
| **SHOULD** | F015 page boutique, F016 tableau de bord vendeur, F017 carnet d'adresses | Renforcent la visibilité (O1) et le confort, mais le parcours fonctionne sans. |
| **COULD** | F018 filtre par région, F019 mises en avant, F020 partage social, F021 favoris | Leviers de visibilité proposés mais non retenus au tour 2 (seuls les avis l'ont été, D13). |
| **FUTURE** | Voir §21 | Reports explicites (D10, D15, D16, D18, D24) ou hors V1. |

> **Points d'attention**
> - **Pas de livraison partielle** (D22) : avec plusieurs vendeurs dans une commande, un seul refus annule tout. Le délai de réponse vendeur (Q19) devient important.
> - **Calendrier vendeur** : un vendeur est payé au plus tôt 7 jours après la réception par le client, puis au reversement hebdomadaire suivant, soit 7 à 14 jours après la livraison. C'est à expliquer clairement dès l'inscription.
> - **Délai légal de remboursement** : la vérification par le vendeur et l'arbitrage éventuel doivent tenir dans le délai légal (15 jours selon R1). Le délai de vérification vendeur (Q44) doit être court.
> - **Charge de l'administrateur** (D38) : toutes les mises à jour de livraison et de reprise passent par lui. Avec la croissance, un accès direct de la société de livraison pourra devenir nécessaire (§21).

**MVP en un paragraphe** : en V1, des petits vendeurs de Tanger et des communes voisines s'inscrivent librement et publient leurs produits. Les clients de Tanger les trouvent par le catalogue, la recherche et les catégories, consultent notes, avis et conditions de retour, et, une fois connectés à leur compte, commandent chez plusieurs vendeurs dans un panier unique payé à la livraison, frais de livraison à leur charge. Chaque vendeur accepte et prépare sa part ; si l'un refuse, la commande est annulée. Une société de livraison partenaire collecte, livre en une fois et encaisse ; l'administrateur saisit les statuts qu'elle lui transmet. Le client peut retourner chaque produit dans les 7 jours suivant sa réception, même par changement d'avis, sauf exceptions légales ; le vendeur vérifie le produit et décide de sa remise en vente, l'administrateur arbitre les litiges et rembourse le client de façon traçable dans le délai légal. La Plateforme retient les sommes des vendeurs jusqu'à la fin du délai de retour, puis les reverse chaque semaine, sans commission, par virement ou en espèces. Le client note les produits reçus ; l'administrateur modère produits, vendeurs et avis.

## 17. Hors périmètre (V1)

| Élément | Raison | Statut |
|---|---|---|
| Paiement en ligne (carte, portefeuille mobile, virement) | Paiement à la livraison uniquement au lancement | CONFIRMÉ — D6 |
| Commande sans compte (invité) | Compte obligatoire pour commander | CONFIRMÉ — D41 |
| Accès direct de la société de livraison à la Plateforme | Statuts saisis par l'administrateur | CONFIRMÉ — D38 |
| Livraison hors de Tanger | Tanger est la première ville | CONFIRMÉ — D18 |
| Vendeurs hors de Tanger et communes voisines | Simplifier la collecte avant l'extension nationale | CONFIRMÉ — D24, D33 |
| Clients et livraison hors du Maroc (diaspora) | Reporté après V1 | CONFIRMÉ — D15 |
| Abonnement, commission ou frais d'inscription vendeurs | Gratuit au lancement | CONFIRMÉ — D16 |
| Livraison partielle d'une commande | Refus d'un vendeur = annulation de la commande | CONFIRMÉ — D22 |
| Remboursement client en espèces non traçable | Remboursements obligatoirement traçables | CONFIRMÉ — D28, D32 |
| Livraison par le vendeur, retrait chez le vendeur | Toutes les livraisons passent par la société de livraison | HYPOTHÈSE (déduit de D14, D19 ; Q12) |
| Messagerie client ↔ vendeur | Non demandé | HYPOTHÈSE |
| Application mobile native | Non demandé ; ENF-002 couvre l'usage mobile | HYPOTHÈSE |
| Outils marketing (codes promo, campagnes) | Non demandé | HYPOTHÈSE |

## 18. Contraintes

| ID | Contrainte | Statut |
|---|---|---|
| C-01 | Paiement à la livraison uniquement en V1 | CONFIRMÉ — D6 |
| C-02 | Livraison et encaissement assurés par une société de livraison partenaire dès le lancement ; statuts saisis par l'administrateur | CONFIRMÉ — D14, D19, D38 |
| C-03 | Zone clients V1 : Tanger ; zone vendeurs V1 : Tanger et communes voisines (liste fixée avant lancement) | CONFIRMÉ — D18, D24, D33 |
| C-04 | V1 simple et extensible | CONFIRMÉ — D5 |
| C-05 | Société de livraison partenaire : non encore choisie ; ses conditions (communes de collecte, tarifs de livraison et de reprise, délais de remise des fonds, moyen de transmission des statuts à l'administrateur) influencent RG-009, RG-020, RG-023, RG-025, RG-029 et Q27 | MANQUANT |
| C-06 | Budget, délais, date de lancement | MANQUANT (Q25) |
| C-07 | Aucune contrainte technique imposée par le porteur de projet | CONFIRMÉ (aucune exprimée) |
| C-08 | **Validation juridique avant lancement** : conformité à la loi 31-08 (protection du consommateur, vente à distance, droit de retour, exclusions, frais et délais de remboursement) et à la loi 09-08 (données personnelles) | CONFIRMÉ — D30 ; exigences exactes à confirmer (R1) |

## 19. Sécurité et données (besoins)

- **Données personnelles traitées** : clients (nom, téléphone, adresses, commandes, retours, coordonnées de remboursement, avis) ; vendeurs (identité, coordonnées, commune, adresse de collecte, coordonnées bancaires si virement). [HYPOTHÈSE]
- **Société de livraison** : sans accès à la Plateforme (D38) ; l'administrateur lui communique uniquement les informations nécessaires à ses missions (adresses de collecte et de livraison, téléphone du client, montant à encaisser). [CONFIRMÉ — D38 ; liste des informations HYPOTHÈSE]
- **Cloisonnement** : un vendeur ne voit que les données nécessaires à la préparation de ses sous-commandes et à la vérification de ses retours ; l'adresse et le téléphone du client sont accessibles uniquement à l'administrateur (SUGGESTION : la Plateforme livrant elle-même, le vendeur n'a pas besoin de l'adresse du client).
- **Coordonnées de paiement** (vendeurs payés par virement, clients remboursés) : accessibles uniquement à l'administrateur et à la personne concernée. [HYPOTHÈSE]
- **Argent** : la Plateforme détient les sommes encaissées, retient les montants vendeurs pendant le délai de retour, rembourse les clients, régularise et reverse chaque semaine, d'où une traçabilité complète (ENF-008). [CONFIRMÉ — D28, D29, D32, D34]
- **Conformité** : loi 09-08 (données personnelles, CNDP) et loi 31-08 (protection du consommateur), validation juridique avant lancement (C-08). Question juridique ouverte : dans une marketplace, qui est le « fournisseur » au sens de la loi 31-08, la Plateforme ou chaque vendeur ? [MANQUANT, Q39]
- **Conservation des données** : durées MANQUANTES.
- **Obligations légales des vendeurs** (statut juridique, facturation) : MANQUANT (Q22).

## 20. Indicateurs de réussite

| ID | KPI | Objectif | Cible |
|---|---|---|---|
| K1 | Part des vendeurs inscrits ayant réalisé au moins une vente dans les 60 jours | O1 | MANQUANT |
| K2 | Nombre de visiteurs uniques par mois | O1 | MANQUANT |
| K3 | Nombre de vendeurs actifs (au moins un produit publié) | O2 | MANQUANT |
| K4 | Délai médian entre l'inscription vendeur et le premier produit publié | O2 | MANQUANT (ENF-003 propose < 10 min) |
| K5 | Nombre de commandes livrées et payées par mois à Tanger | O3 | MANQUANT |
| K6 | Taux de réussite des commandes (livrées et payées / passées), en isolant les annulations dues à un refus vendeur | O3 | MANQUANT |
| K7 | Part des commandes livrées ayant reçu au moins un avis ; note moyenne ; nombre d'avis masqués | O4 | MANQUANT |
| K8 | Taux de retour (produits retournés / produits livrés), par motif (changement d'avis, défaut, erreur, non-conformité) ; taux de litiges | O3 | MANQUANT |
| K9 | Délai moyen entre la réception et le reversement au vendeur ; délai moyen de remboursement client ; part des remboursements dans le délai légal | O2, O3, O5 | 100 % dans le délai légal (ENF-012) ; autres MANQUANT |

## 21. Évolutions futures

| Évolution | Origine |
|---|---|
| Ouverture à d'autres villes marocaines (clients) | D18 (Tanger = première ville) |
| Ouverture aux vendeurs de tout le Maroc | D24 |
| Ouverture à la diaspora / livraison internationale | D10, D15 |
| Paiement en ligne | D6 (« au démarrage ») |
| Modèle de revenus vendeur (abonnement ou commission) | D16 ; « abonnement » évoqué en S2 |
| Accès direct de la société de livraison à la Plateforme (saisie de ses propres statuts) | D38 (exclu en V1) |
| Commande sans compte (invité) | D41 (exclue en V1) |
| Livraison par le vendeur et retrait chez le vendeur (modèle mixte) | D7 (remplacé pour la V1 par D14) |
| Livraison partielle d'une commande | D22 (exclue en V1) |
| Leviers de visibilité F015–F021 | SUGGESTION |

## 22. Synthèse

### Résumé
Marketplace de produits locaux marocains, lancée à Tanger avec des vendeurs de Tanger et des communes voisines, inscription vendeur libre et gratuite, compte client obligatoire pour commander, panier multi-vendeurs sans livraison partielle, paiement à la livraison avec frais de livraison à la charge du client, collecte, livraison et encaissement par une société de livraison partenaire dont l'administrateur saisit les statuts, droit de retour de 7 jours pour tout motif sauf exceptions légales (un retour par produit), vérification et remise en vente décidées par le vendeur, arbitrage par l'administrateur, remboursement traçable dans le délai légal, retenue des fonds vendeurs puis reversement hebdomadaire, avis réservés aux produits reçus, modération, validation juridique avant lancement. 15 fonctionnalités MUST, 3 SHOULD, 4 COULD ; 15 user stories ; 31 règles métier ; 48 critères d'acceptation.

### Contradictions

| ID | Conflit | Statut |
|---|---|---|
| C1 | D11 « pas de livraison plateforme au lancement » vs D12 « la plateforme livre les paniers multi-vendeurs » | Résolue — D14 (S4) |
| C2 | D10 « clients diaspora » vs D6 « paiement à la livraison » | Résolue — D15 (S4), précisé par D18 |
| C3 | D26 « retours pour défaut uniquement » vs D27 « changement d'avis » vs R1 « rétractation sans justification » | Résolue — D30 (S8) |
| C4 | RG-015 (modération) et RG-011 (avis réservés aux produits reçus) marqués SUGGESTION alors que US-011, CA-F013-1/2, CA-F004-2 et CA-F012-2, validés, les exigeaient (relevé par Blueprint, B1) | Résolue — D37 (S10) : confirmées |

**Aucune contradiction ouverte.**

### Points à régler avant le lancement

Ces points ne remettent pas en cause la structure validée. Ils doivent être tranchés par le porteur de projet avant la mise en service ; le développement peut prévoir les paramètres correspondants.

**Avis juridique (C-08)**

| ID | Question | Impact |
|---|---|---|
| Q39 | **Qui est le « fournisseur »** responsable vis-à-vis du client au sens de la loi 31-08 : la Plateforme ou chaque vendeur ? | C-08, RG-026, F022 |
| Q40 | **Frais de livraison initiaux** : remboursés en cas de retour (R1 mentionne le « montant total payé ») ? | RG-022 |
| Q42 | **Moyens de remboursement alternatifs** au virement pour les clients sans compte bancaire | RG-022, F022 |
| Q43 | **Cosmétiques ouverts** : exclus du droit de retour ou non ? | RG-019 |

**Paramètres métier**

| ID | Question | Impact |
|---|---|---|
| Q41 | **Liste exacte des communes voisines** autorisées pour les vendeurs | RG-023, F002 |
| Q44 | **Délai de vérification** du produit retourné par le vendeur (ex. 48 h après réception du retour) ; au-delà, l'administrateur décide-t-il ? | RG-027, ENF-012 |
| Q45 | **Montant des frais de retour** (forfait ou tarif de la société de livraison) | RG-025, F022 |
| Q27 | **Montant des frais de livraison** : forfait unique à Tanger, ou variable ? | RG-009, F007 |
| Q19 | **Délai de réponse vendeur** à une sous-commande (ex. 24 h) | RG-011b, risque d'annulation |
| Q38 | Que faire si un vendeur a un **solde négatif** après régularisation (plus de ventes à venir) ? | F011 |
| Q24 | Échec de livraison : nouvelle tentative ? retour des produits aux vendeurs ? frais perdus à la charge de qui ? | RG-013 |
| Q17 | Définition de « **produit local marocain** » et contrôle associé | RG-016, F013 |
| Q22 | Informations et statut légal exigés des vendeurs | F002, F011 |
| Q10 | Profil des vendeurs (artisans, coopératives, commerces) | Catégories, parcours vendeur |
| Q11 | Langues de l'interface | ENF-001 |
| Q23 | Canal des notifications (SMS, e-mail, WhatsApp…) | F014 |
| Q21 | Volumes attendus et cibles des KPI | ENF-006, §20 |
| Q25 | Budget, délais, date de lancement | C-06 |
| C-05 | Choix de la société de livraison partenaire et moyen de transmission de ses statuts à l'administrateur | RG-009, RG-020, RG-023, RG-025, RG-029 |

Questions résolues en v1.1 : Q16 (compte obligatoire — D41), Q30 (statuts saisis par l'administrateur — D38).

### Hypothèses à confirmer (principales)
H1 recherche et catégories en MUST · panier accessible sans compte · répartition en sous-commandes · absence de réponse vendeur = refus · un seul forfait de livraison par commande · étapes des cycles de vie (hors « En collecte », confirmé) · annulation client avant collecte · stock réservé à la commande · demande de retour enregistrée sans acceptation préalable · décision finale de l'administrateur en cas de litige · montant d'un retour en cours retenu jusqu'à sa clôture · contenu minimal de la confirmation écrite (RG-026) · mode de reversement choisi par le vendeur · remise intégrale des fonds par la société de livraison · un avis par produit et par commande · prix en MAD · usage mobile prioritaire · valeurs ENF-003/004/005 · alerte de délai à 12 jours (CA-F022-7).

### Suggestions de l'analyste (non retenues tant qu'elles ne sont pas acceptées)
Adresse client non communiquée au vendeur · message et liste d'attente pour les vendeurs hors zone · information du vendeur sur le calendrier de paiement dès l'inscription · F015–F021. (S-1 et la restriction des avis aux produits reçus ont été acceptées : D37.)

### Risques

| Risque | Effet | Piste (à décider par le porteur) |
|---|---|---|
| Retours pour changement d'avis | Coûts de reprise, produits abîmés, litiges | Frais de retour déduits du remboursement (RG-025, D42) ; vérification vendeur et arbitrage (RG-027) |
| Dépassement du délai légal de remboursement | Non-conformité, intérêts dus | Délai de vérification vendeur court (Q44) ; alerte administrateur (ENF-012) |
| Charge de saisie de l'administrateur | Retards de statuts, erreurs de saisie, retards de reversement | Historisation (ENF-008) ; accès direct de la société de livraison en évolution (§21) |
| Remboursement des clients sans compte bancaire | Remboursements impossibles ou retardés | Moyens alternatifs traçables (Q42) |
| Refus à la livraison (paiement à la livraison) | Frais de livraison perdus, stock immobilisé | Confirmation téléphonique avant collecte (SUGGESTION) |
| Pas de livraison partielle + paniers multi-vendeurs | Annulations fréquentes si un vendeur ne répond pas | Délai de réponse court (Q19) ; stock tenu à jour par les vendeurs |
| Attente de 7 à 14 jours pour les vendeurs | Vendeurs mécontents | Calendrier expliqué dès l'inscription (SUGGESTION) |
| Dépendance à une société de livraison | Qualité de service et remise des fonds hors de votre contrôle | Rapprochement systématique (RG-020) ; choix du partenaire (C-05) |
| Inscription libre | Produits non locaux ou de mauvaise qualité | Modération F013, définition Q17 |
| Gratuité sans modèle de revenus | Coûts de fonctionnement non couverts | Modèle futur (D16) |

## 23. Validation

| Version | Rôle | Nom | Date | Décision |
|---|---|---|---|---|
| 1.0 | Porteur du projet | Non communiqué | Session 1 | **Validé** — « passe au statut validé » (S9, D36) |
| 1.1 | Porteur du projet | Anass | 2026-10-12 | **Validé** — « v1.1 validée » (S11, D45) |

*Seul le porteur du projet peut valider ce document. Toute modification ultérieure donnera lieu à une nouvelle version consignée dans le journal des modifications.*

---

## Annexes

### A. Glossaire métier

| Terme | Définition |
|---|---|
| Commande | Achat validé par un client connecté, pouvant regrouper plusieurs vendeurs, livré et payé en une seule fois |
| Sous-commande | Partie d'une commande concernant un seul vendeur |
| Boutique | Espace public d'un vendeur présentant ses produits |
| Paiement à la livraison | Paiement en espèces remis au livreur de la société de livraison à la réception |
| Frais de livraison | Montant payé par le client pour la livraison de sa commande |
| Société de livraison | Entreprise partenaire chargée de la collecte, de la livraison, de l'encaissement et de la reprise des retours ; sans accès à la Plateforme en V1 |
| Collecte | Récupération des produits préparés chez le vendeur par la société de livraison |
| En collecte | Statut d'une commande transmise par l'administrateur à la société de livraison |
| Zone vendeurs | Communes où doit se trouver un vendeur (V1 : Tanger et communes voisines, liste fixée par l'administrateur) |
| Retour | Renvoi d'un produit (une ligne de commande) par le client dans les 7 jours suivant sa réception, pour tout motif, suivi d'un remboursement |
| Exclusion | Produit pour lequel la loi permet de ne pas accepter le retour : signalé périssable/personnalisé par le vendeur, ou appartenant à une catégorie exclue par l'administrateur |
| Vérification | Contrôle par le vendeur de l'état d'un produit retourné et de la cohérence du motif ; il décide aussi de sa remise en vente |
| Remise en vente | Décision du vendeur de remettre en stock un produit retourné après vérification |
| Litige | Désaccord sur un retour, arbitré par l'administrateur |
| Modération | Masquage d'un produit ou d'un avis, ou suspension d'un vendeur, par l'administrateur |
| Frais de retour | Coût de la reprise d'un produit retourné ; à la charge du client en cas de changement d'avis (déduits du remboursement), du vendeur en cas de défaut ou d'erreur |
| Montant retenu | Somme due à un vendeur, conservée par la Plateforme jusqu'à la fin du délai de retour |
| Montant disponible | Somme due à un vendeur, libérée après le délai de retour et prête à être reversée |
| Reversement | Versement hebdomadaire par la Plateforme au vendeur, par virement ou en espèces, des montants disponibles après déductions |
| Régularisation | Déduction, sur un reversement futur, d'un remboursement ou de frais de retour intervenus après un reversement |

### B. Journal des modifications

| Version | Date | Modification |
|---|---|---|
| 0.1 | session 1 | Première rédaction à partir de S1–S5 ; points non tranchés en HYPOTHÈSE (autorisation S5) |
| 0.2 | session 1 | Intégration de S6 : Tanger (D18) ; société de livraison (D19) ; frais de livraison client (D20) ; reversements virement/espèces (D21) ; pas de livraison partielle (D22) ; retours acceptés (D23) : M11, F022, US-013, RG-019 à RG-022, K8 |
| 0.3 | session 1 | Intégration de S7 : vendeurs Tanger et environs (D24) ; retours 7 jours (D25) ; motifs (D26) ; frais de retour (D27) ; remboursement traçable (D28) ; retenue et régularisation (D29) ; référence R1 ; RG-023 à RG-026 ; C-08 ; K9 ; contradiction C3 ouverte |
| 0.4 | session 1 | Intégration de S8 : C3 résolue (D30) ; vérification vendeur et supervision administrateur (D31, RG-027, US-014, US-015) ; remboursement traçable alternatif (D32) ; communes voisines (D33) ; reversements hebdomadaires (D34) ; exclusions légales (D35) ; ENF-012 ; questions Q40–Q45 |
| 1.0 | session 1 | Validation par le porteur du projet (S9, D36). Aucune modification de fond par rapport à la v0.4. |
| **1.1** | session 1 | **Révision suite à l'étape A de Blueprint (S10).** Corrections : incohérence C4/B1 (RG-015 et RG-011 passées de SUGGESTION à CONFIRMÉ, D37) ; décompte des règles métier (la v1.0 en définissait 28, pas 27). Décisions intégrées : statuts de livraison saisis par l'administrateur seul, société de livraison sans accès (D38, RG-029, matrice des permissions, F010, US-008, ENF-007, §19) ; un retour par produit (D39, RG-030, CA-F022-9) ; exclusion par le vendeur et par la catégorie (D40, RG-019, CA-F022-8) ; compte client obligatoire (D41, RG-028, CA-F001-3) ; frais de retour déduits du remboursement (D42, RG-022, RG-025) ; remise en vente décidée par le vendeur (D43, RG-017, US-014) ; « En collecte » à la transmission (D44, RG-029, CA-F010-4). Ajout de CA-F013-3 (masquage d'avis). Totaux : 31 règles métier, 48 critères d'acceptation. Statut repassé à *Brouillon* jusqu'à revalidation. |
| 1.1 | 2026-10-12 | Validation de la v1.1 par le porteur du projet, Anass (S11, D45). Aucune modification de fond ; statut *Brouillon* → *Validé*. |
