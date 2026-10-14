# Risques d'architecture — marketplace-produits-locaux-maroc

**Tâche** : T-001 · **Auteur** : Keystone · **Date** : 2026-10-13 · **Statut** : Proposé
Chaque risque indique sa source (constat du plan, exigence du cahier, décision de ce dossier), son effet, la riposte prévue et qui la porte.

## 1. Risques ouverts

| ID | Risque | Source | Effet | Riposte dans l'architecture | Responsable |
|---|---|---|---|---|---|
| R-01 | **Volumes inconnus** (vendeurs, produits, commandes à 12 mois) | ENF-006, Q21 MANQUANT, H-11 | Dimensionnement possiblement insuffisant ou sur-dimensionné ; décisions de cache et d'index non calibrées | Socle paramétrable, montée en charge par réplication de l'application, worker séparé ; mesure des temps de réponse dès T-067 ; aucun choix figé qui empêcherait la montée en charge | @user (valeur) puis Release (T-069) |
| R-02 | **Hôte unique = point de défaillance** face à un objectif de 99 % de disponibilité | ENF-005 (HYPOTHÈSE), ADR-006 | Indisponibilité en cas de panne matérielle ou de maintenance | Redémarrage automatique, contrôle de santé, sonde externe de disponibilité, fenêtre de maintenance annoncée, sauvegardes quotidiennes et restauration testée | Release (T-069) |
| R-03 | **Valeurs ENF-003/004/005 non validées** : l'architecture est conçue pour des cibles qui peuvent changer | H-11 | Retravail des écrans ou du cache si les cibles sont revues à la hausse | Cibles isolées et mesurables ; aucune optimisation prématurée dépendante d'une valeur non confirmée | @user (validation), QA (T-067) |
| R-04 | **Charge de saisie de l'administrateur** : toutes les mises à jour de livraison et de reprise passent par lui (D38) | Cahier §16 « Points d'attention » | Retards de statuts, erreurs de saisie, retards de reversement | Interfaces de saisie groupée, journal d'audit pour contrôler après coup, transitions interdites par les machines à états (pas d'état incohérent) | Backend (T-037, T-041) |
| R-05 | **Traitements planifiés mal exécutés** (double exécution, échéance manquée) : ils touchent l'argent des vendeurs | ADR-004, ENF-008 | Montants erronés, retours non traités, non-conformité de délai légal | Idempotence obligatoire, verrou d'exécution, journal d'audit, tests à horloge simulée (T-034, T-050, T-053, T-054), alerte d'administrateur | Backend (T-011 et tâches liées) |
| R-06 | **Photos : perte ou service dégradé** (volume non sauvegardé, image trop lourde) | ADR-005, ENF-011, ENF-004 | Fiches produit dégradées, catalogues lents à 360 px | Volume inclus dans la sauvegarde quotidienne et la restauration testée ; variantes générées hors requête utilisateur ; stockage derrière un composant unique | Backend (T-020), Release (T-069) |
| R-07 | **Fuite ou usage indu de données personnelles** (téléphone, adresses, coordonnées bancaires) | ENF-007, cahier §19, loi 09-08 | Sanction, perte de confiance | Autorisation par rôle et par propriété, adresse et téléphone du client invisibles au vendeur, coordonnées bancaires restreintes, aucune donnée sensible dans les journaux ; tests autorisé/interdit par ligne de la matrice §5 (T-066) | Backend, QA (T-066) |
| R-08 | **Durée de conservation des données non fixée** | Cahier §19 MANQUANT | Conservation indue ou purge non conforme | `[NEEDS CLARIFICATION]` maintenu dans la spécification ; aucune purge automatique codée avant décision | @user / juriste |
| R-09 | **Porte juridique mal franchie** (loi 31-08 : information précontractuelle, confirmation écrite, délais de remboursement) | C-08, ENF-009, Q39 | Non-conformité au lancement | Mécanismes prêts (paramètres de délais, gabarit de confirmation, alertes de délai) ; porte de lancement bloquante hors développement (T-070) | @user + conseil juridique |
| R-10 | **Canal de notification externe indisponible** | Q23 MANQUANT, T-010 bloquée | Les acteurs n'apprennent les événements que dans l'application | Notifications internes livrées sans dépendance externe ; adaptateur externe branché plus tard sans toucher aux émetteurs (T-062) | Backend (T-009, T-062) |
| R-11 | **Aucun dépôt ni CI avant T-004** : la vérification des tâches reste « commande à définir » | M-04 | Impossible de prouver que les tâches suivantes sont terminées | Socle de dépôt et commandes de test définis ici (`quickstart.md`) ; T-004 met en œuvre la CI (lint, tests, build) | Release (T-004) |
| R-12 | **Absence de conception d'écrans** : les interfaces seront construites depuis les parcours P1–P5 | HYPOTHÈSE du plan (M-03) | Retravail d'interfaces si une conception arrive ensuite | Socle front (routage, client d'API, cadre i18n, composants à 360 px) séparé des écrans métier ; les écrans restent remplaçables | Frontend (T-012+) |
| R-13 | **Historisation absente du modèle UML** (aucune classe d'audit dans CLASS-01/02) | U-03 (HYPOTHÈSE) | Modèle de données à revoir si l'hypothèse tombe | ADR-008 décide l'historisation transverse ; T-002 intègre les tables d'audit ; Blueprint informé de l'écart (U-03) | Architecte (T-002), Blueprint |
| R-14 | **Dérive d'horloge et fuseau horaire** sur les échéances (délais de 7 j, 12 j, semaine de reversement) | RG-018, RG-024, ENF-012 | Statuts ou alertes calculés à la mauvaise date | Fuseau de la Plateforme explicite (`Africa/Casablanca`), échéances stockées en UTC, calculs de délais via le module Paramètres, tests à horloge simulée | Backend (T-007, T-011) |
| R-19 | **Contraintes `CHECK` perdues lors de l'écriture des migrations** (Laravel ne les génère pas nativement) | T-002, ADR-012/013 | Prix, stock, note ou statuts invalides acceptés en base | T-005 rejoue `specs/002-schema-donnees/validation/coverage.py` et `probe_constraints.py` sur la base migrée | Backend (T-005) |
| R-20 | **Perte ou rotation de la clé `APP_KEY`** : données bancaires et de remboursement illisibles | ADR-014 | Reversements par virement et remboursements bloqués | Clé sauvegardée hors dépôt avec les secrets d'exploitation ; procédure de rechiffrement avant rotation | Release (T-069) |

## 2. Risques fermés ou transmis

| ID | Sujet | Traitement |
|---|---|---|
| R-15 | « La v1.1 est un brouillon » (réserve du rapport UML) | **Fermé** : constat K-01 du plan — la v1.1 est validée par D45 ; la réserve est OBSOLÈTE |
| R-16 | Contradictions du cahier (C1–C4) | **Fermé** : toutes résolues (D14, D15, D30, D37) ; §22 « aucune contradiction ouverte » |
| R-17 | Écarts UML U-01 (transition après délai de vérification) et U-02 (annulation admin) | **Transmis** à Blueprint via Compass (tâches T-046 et T-060 bloquées, hors T-001) |
| R-18 | Choix de la société de livraison partenaire (C-05, Q17, Q24) | **Transmis** à @user ; influence des paramètres (frais, délais de remise des fonds), pas le socle |
