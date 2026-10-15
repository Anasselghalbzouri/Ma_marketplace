<!--
Sync Impact Report
Version: [TEMPLATE] → 1.0.0 (adoption initiale)
Principes :
  - ajout : I. Le métier d'abord
  - ajout : II. Simplicité extensible
  - ajout : III. Une seule porte par état métier
  - ajout : IV. Argent et traçabilité non négociables
  - ajout : V. Cloisonnement par rôle testé
  - ajout : VI. Tests obligatoires
  - ajout : VII. Mobile-first et performance
  - ajout : VIII. Aucun secret dans le dépôt
  - ajout : IX. Langue du code et de la documentation
  - ajout : X. Validation juridique avant lancement
Sections ajoutées : Contraintes et stack technique ; Modules et découpage ; Gouvernance
Sections supprimées : aucune (gabarit initial, jamais rempli)
Modèles dépendants : .specify/templates/*.md non vérifiés dans cette passe (hors périmètre de cette commande) — à contrôler lors de la prochaine utilisation de /speckit-plan ou /speckit-tasks.
Suivi différé : aucun TODO(champ) laissé ; toutes les valeurs proviennent du cahier des charges v1.1, de decisions.md (D1–D45) ou du plan de tâches.
-->

# Constitution — marketplace-produits-locaux-maroc

## Contexte

La Plateforme est une marketplace B2C multi-vendeurs de produits locaux marocains, lancée à
Tanger. Des clients à Tanger commandent, dans un panier unique pouvant contenir plusieurs
vendeurs, auprès de petits vendeurs situés à Tanger et dans les communes voisines ; ils paient à
la livraison. La livraison et l'encaissement sont assurés par une société de livraison
partenaire, qui n'a aucun accès à la Plateforme : seul l'administrateur saisit les statuts qu'elle
lui transmet (D38). Cette constitution régit toutes les tâches d'ingénierie du plan
`/opt/data/uml/marketplace-produits-locaux-maroc/plan/plan-marketplace-produits-locaux-maroc.md`,
lui-même fondé sur le cahier des charges v1.1 validé et le journal de décisions D1–D45.

## Principes fondamentaux

### I. Le métier d'abord

Le cahier des charges v1.1 validé (`/opt/data/cahiers/marketplace-produits-locaux-maroc/cahier-des-charges-v1.1.md`)
et le journal de décisions D1–D45 (`decisions.md`) sont l'unique source du comportement métier.
Aucun agent n'invente une règle, un montant, un délai ou un parcours qui n'y figure pas. Les
points encore marqués MANQUANT, HYPOTHÈSE ou SUGGESTION (notamment Q19, Q21, Q24, Q27, Q38,
Q40–Q45) restent non tranchés : ils sont implémentés soit comme paramètre configurable par
l'administrateur, soit explicitement marqués `[NEEDS CLARIFICATION]` dans les spécifications
produites par les agents. Les éléments SUGGESTION du cahier des charges ne sont développés qu'après
accord explicite du porteur du projet.

**Raison** : le cahier des charges a été validé par le porteur (Anass, S11/D45) après plusieurs
tours de clarification ; le réintroduire par des décisions techniques non tracées romprait la
chaîne de validation et pourrait créer un comportement que personne n'a approuvé.

### II. Simplicité extensible

L'architecture est un monolithe modulaire Laravel, découpé selon les modules M01–M11 du cahier
des charges (§9) : M01 Comptes et accès, M02 Boutique et catalogue vendeur, M03 Découverte, M04
Panier et commande, M05 Commandes vendeur, M06 Livraison et encaissement, M07 Reversements
vendeurs, M08 Avis et notes, M09 Administration et modération, M10 Notifications, M11 Retours. Pas
de microservices, pas de file de messages distribuée, pas de couche d'abstraction supplémentaire
tant qu'aucun besoin validé ne l'exige. Toute complexité ajoutée (nouveau service externe, nouvelle
couche, nouveau pattern) doit être justifiée par une exigence du cahier des charges ou une décision
D1–D45, et documentée dans un ADR.

**Raison** : C-04 et D5 demandent une V1 simple et extensible ; ENF-010 exige que les évolutions
futures (autres villes, paiement en ligne, accès société de livraison, commission) ne nécessitent
pas de refonte des parcours V1 — un découpage modulaire clair permet cette extension sans
sur-ingénierie initiale.

### III. Une seule porte par état métier

Les statuts de Commande et de SousCommande, de MontantVendeur et de Retour ne sont modifiés que
par leur service dédié, conformément au plan §4 :
- Commande / SousCommande : seul le service de transitions correspondant (T-027 du plan) modifie
  ces statuts ; tout autre module l'appelle sans écrire directement le champ de statut.
- MontantVendeur : seul le service Montants (T-036 du plan) modifie ses statuts (Retenu,
  Disponible, Reversé, Déduit).
- Retour : seul le service Retour (T-043 du plan) modifie ses statuts.

Toute nouvelle transition d'état (y compris une annulation administrateur ou un cas non encore
modélisé) passe par une revue du service propriétaire concerné, et non par une écriture directe
depuis un autre module.

**Raison** : les machines à états Commande/SousCommande, MontantVendeur et Retour (STATE-001 à
STATE-004 des diagrammes UML approuvés) portent des garanties métier et financières ; des
écritures concurrentes depuis plusieurs modules produiraient des statuts incohérents et des
montants faux, impossibles à auditer.

### IV. Argent et traçabilité non négociables

Toute opération financière — encaissement, remise de fonds par la société de livraison, écart,
retenue, mise à disposition, remboursement client, frais de retour imputé, décision de litige,
régularisation, reversement hebdomadaire — est historisée (qui, quand, montant, motif) et n'est
jamais modifiable après coup ; seule une nouvelle entrée peut la corriger ou la régulariser. Toute
saisie de statut de livraison par l'administrateur est historisée de la même façon (ENF-008). Aucun
frais, aucune commission vendeur n'est prélevé en dehors de ce qui est explicitement paramétré
(RG-005) : la V1 est gratuite pour les vendeurs, et les frais de retour imputés (RG-025) ne
constituent pas une commission.

**Raison** : ENF-008 exige une traçabilité complète et consultable par l'administrateur de tout
mouvement financier et de toute saisie de statut ; D16 confirme la gratuité vendeur en V1. Sans
historisation immuable, un litige financier avec un vendeur ou un client ne pourrait pas être
tranché de façon fiable.

### V. Cloisonnement par rôle testé

Chaque capacité de la matrice des permissions du cahier des charges (§5) est couverte par au moins
un test autorisé (le rôle habilité peut agir) et un test interdit (un autre rôle, ou un autre
titulaire du même rôle, ne le peut pas). Un vendeur n'accède qu'à ses propres données (boutique,
produits, sous-commandes, montants, retours) ; les actions d'administration sont réservées aux
administrateurs ; la société de livraison n'a aucun accès à la Plateforme en V1 (D38) ; les mots de
passe ne sont jamais affichés, ni renvoyés par l'API (ENF-007).

**Raison** : ENF-007 impose un accès par compte avec cloisonnement strict ; l'inscription vendeur
étant libre et sans validation préalable (D9), le cloisonnement est la seule garantie qu'un
vendeur A ne puisse jamais lire ou modifier les données du vendeur B.

### VI. Tests obligatoires

Chaque tâche livrée inclut ses tests automatisés (unitaires et fonctionnels), conformément à la
convention du plan de tâches : « chaque tâche Backend inclut ses tests automatisés ». Aucune
fonctionnalité n'est considérée terminée sans un test couvrant chacun de ses critères
d'acceptation (CA-F00x) et chacune de ses règles métier (RG-0xx) associées. Les montants
financiers sont vérifiés au dirham près dans les tests (retenue, disponibilité, reversement,
remboursement, régularisation).

**Raison** : le cahier des charges définit 48 critères d'acceptation et 31 règles métier précises ;
sans test systématique par critère, une régression sur une règle de retour ou de reversement
passerait inaperçue jusqu'à un litige réel avec un client ou un vendeur.

### VII. Mobile-first et performance

Tous les parcours (client, vendeur, administrateur) sont conçus et utilisables dès une largeur
d'écran de 360 px (ENF-002). Les pages catalogue et fiche produit respectent le budget de
performance ENF-004 : affichage en moins de 3 secondes sur connexion mobile 4G simulée, pour 95 %
des consultations (p95 < 3 s). Toute interface est pensée mobile en premier ; une adaptation
desktop ultérieure ne doit pas casser le parcours 360 px.

**Raison** : ENF-002 et ENF-004 sont des exigences non fonctionnelles confirmées du cahier des
charges ; les clients et vendeurs visés (Tanger et communes voisines) accèdent majoritairement à
la Plateforme depuis un smartphone.

### VIII. Aucun secret dans le dépôt

Aucun mot de passe, clé d'API, jeton ou identifiant de connexion n'est commité en clair. Seules des
variables d'environnement documentées dans un `.env.example` sont utilisées pour la configuration
sensible (base de données, stockage de photos, futur canal de notification externe). Les
coordonnées bancaires des vendeurs et les moyens de remboursement des clients sont traités comme
des données sensibles, accessibles uniquement à l'administrateur et à la personne concernée.

**Raison** : complément direct d'ENF-007 (sécurité des accès) et des besoins de sécurité et
données du cahier des charges (§19) ; un secret commité expose immédiatement les comptes
vendeurs, clients et administrateur.

### IX. Langue du code et de la documentation

Le code source, le schéma de données, les contrats d'API et les messages de commit sont rédigés en
anglais. La documentation d'architecture, les messages affichés aux utilisateurs et les rapports
d'ingénierie (comptes rendus, ADR, revues) sont rédigés en français.

**Raison** : cohérence avec les conventions usuelles de l'écosystème Laravel/PHP et de l'open
source (code en anglais), tout en gardant la documentation et la relation avec le porteur du
projet, francophone, dans sa langue de travail.

### X. Validation juridique avant lancement

La conformité à la loi 31-08 (protection du consommateur : vente à distance, droit de rétractation
de 7 jours, exclusions, délais et frais de remboursement) et à la loi 09-08 (données personnelles,
CNDP) doit être validée par un conseil juridique avant tout lancement en production (C-08,
ENF-009, D30, D45). Cette porte est bloquante : aucune tâche de développement, aucun déploiement en
production, aucune décision technique ne peut la contourner ou en dispenser le projet. Tant que
cette validation n'a pas eu lieu, le travail d'ingénierie peut se poursuivre en environnement de
développement et de recette, mais pas en production.

**Raison** : C-08 et ENF-009 sont des exigences confirmées et non négociables du cahier des
charges ; le modèle de retour (7 jours, tout motif, exclusions légales) touche directement au droit
de la consommation marocain, dont la lecture définitive relève d'un juriste et non des équipes
d'ingénierie.

## Contraintes et stack technique

- **C-07** — Aucune contrainte technique n'a été imposée par le porteur du projet ; le choix de
  stack relève de l'architecte. La stack retenue (décision technique, à documenter par un ADR au
  statut « Proposé ») est : **Laravel 11 (PHP 8.3) + React 18 (Vite) + MySQL 8 + Docker Compose**,
  avec une **API REST interne** entre le frontend React et le backend Laravel.
- **C-01** — Paiement à la livraison uniquement en V1 ; aucun paiement en ligne.
- **C-02** — Livraison et encaissement assurés par une société de livraison partenaire ; celle-ci
  n'a aucun accès à la Plateforme ; seul l'administrateur saisit les statuts qu'elle lui transmet
  (D38).
- **C-03** — Zone clients V1 : Tanger. Zone vendeurs V1 : Tanger et communes voisines, selon un
  référentiel paramétrable géré par l'administrateur (liste exacte à fixer avant lancement, Q41).
- **C-04** — La V1 doit rester simple et extensible (voir Principe II).
- Les deux actions de notification (interne à l'application, et éventuel canal externe) ne doivent
  jamais être confondues dans le code ni dans les spécifications. Aucun envoi externe (SMS, e-mail,
  WhatsApp…) n'a lieu en V1 tant que le porteur du projet n'en a pas décidé le canal (Q23
  MANQUANT) : l'adaptateur de canal externe reste une tâche bloquée jusqu'à cette décision.

## Modules et découpage (M01–M11)

Référence unique pour le découpage fonctionnel : le tableau du cahier des charges §9 (M01 Comptes
et accès, M02 Boutique et catalogue vendeur, M03 Découverte, M04 Panier et commande, M05 Commandes
vendeur, M06 Livraison et encaissement, M07 Reversements vendeurs, M08 Avis et notes, M09
Administration et modération, M10 Notifications, M11 Retours). Tout module supplémentaire créé en
cours de projet doit être justifié par rapport à ce découpage et, si besoin, documenté dans un ADR.

## Gouvernance

- **Préséance** : cette constitution prime sur toute préférence d'implémentation individuelle, tout
  gabarit de prompt, et toute convention non écrite. En cas de conflit entre une tâche du plan et un
  principe de cette constitution, le principe l'emporte et la tâche doit être corrigée ou soumise au
  porteur du projet avant exécution.
- **Exceptions** : toute dérogation à un principe de cette constitution doit être écrite dans un ADR
  (`docs/architecture/DECISIONS.md`), avec son statut initial fixé à **« Proposé »**. Un agent ne
  peut jamais faire passer un ADR de « Proposé » à un autre statut (« Accepté », « Rejeté »,
  « Remplacé ») : seul le porteur du projet (@user, Anass) décide de ce changement de statut.
- **Statuts de tâches** : aucun agent ne modifie le statut d'une tâche du plan de tâches
  (`pending`, `blocked`, etc.) ; ce changement relève exclusivement du porteur du projet.
- **Amendement** : toute modification de cette constitution (ajout, suppression ou reformulation
  d'un principe) requiert une nouvelle version selon le versionnage sémantique ci-dessous, et la
  validation du porteur du projet avant d'être considérée en vigueur pour les tâches d'ingénierie.
- **Versionnage** : MAJEUR pour une suppression ou une redéfinition incompatible d'un principe ;
  MINEUR pour l'ajout d'un principe ou d'une section, ou un enrichissement matériel d'un principe
  existant ; CORRECTIF pour une clarification de formulation sans changement de sens.
- **Conformité** : toute revue de code ou de spécification doit vérifier la conformité aux dix
  principes ci-dessus ; toute complexité non justifiée par le cahier des charges, les décisions
  D1–D45 ou un ADR validé doit être signalée et simplifiée avant fusion.

**Version** : 1.0.0 | **Ratifiée** : 2026-10-13 | **Dernier amendement** : 2026-10-13
