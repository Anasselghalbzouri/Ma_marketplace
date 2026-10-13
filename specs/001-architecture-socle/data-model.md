# Data Model — Socle transverse (T-001)

**Feature** : `001-architecture-socle` | **Date** : 2026-10-13

**Portée** : ce document décrit uniquement les entités du **socle transverse** (paramètres, journal
d'audit, notifications internes, tâches planifiées, fichiers/photos, comptes — vue technique). Les
entités métier (Commande, SousCommande, Produit, Boutique, MontantVendeur, Retour, Avis, etc.) relèvent
du schéma physique de la tâche **T-002**, hors périmètre de ce document (Constitution Principe I — aucune
valeur métier inventée ici).

Aucune migration exécutable n'est produite ici : ce sont des définitions conceptuelles destinées à
cadrer T-002 et les tâches de socle (T-007, T-008, T-009, T-011, T-012, T-013).

---

## Vue d'ensemble

```text
Compte (socle) ──< Session
Compte (socle) ──< EntreeJournalAudit (acteur)
Compte (socle) ──< NotificationInterne (destinataire)
Parametre (indépendant, référencé par clé depuis les modules métier)
ExecutionTachePlanifiee ──> EntreeJournalAudit (si modification de statut/montant)
FichierPhoto ──< VarianteFichierPhoto
FichierPhoto ──> Compte (propriétaire technique, ex. vendeur — référence, pas de duplication des
                 données métier du Produit/Boutique qui relèvent de T-002)
```

---

## Compte (vue socle)

Représente uniquement les attributs techniques nécessaires à l'authentification et à l'autorisation
transverses (FR-020, FR-050). Les attributs métier du profil (boutique, préférences, etc.) relèvent de
T-002 et des modules propriétaires (M01 pour le détail du compte).

| Champ | Type | Règle |
|---|---|---|
| `id` | identifiant technique | Clé primaire. |
| `telephone` | chaîne, unique | Identifiant de connexion (ENF-007, FR-050). Jamais journalisé en clair hors besoin de support (FR-057). |
| `mot_de_passe_hash` | chaîne | Haché (algorithme standard de hachage de mot de passe) ; **ne doit jamais être lu ni renvoyé en clair par aucun service, y compris à l'administrateur** (FR-054). |
| `role` | énumération : Client, Vendeur, Administrateur | FR-050, ENF-007. Un compte porte exactement un rôle en V1 (cahier §5). |
| `cree_le` | horodatage | — |
| `derniere_connexion_le` | horodatage, nullable | Utile à la supervision (FR-004), ne contient aucune donnée personnelle sensible additionnelle. |
| `suspendu` | booléen | Capacité d'administration (M09) ; le socle expose le champ, la décision métier reste M09/T-061. |

**Validation** : le mot de passe n'est jamais stocké ni transmis en clair après hachage (FR-054,
Constitution Principe VIII). Aucune valeur de rôle autre que les trois rôles listés n'est acceptée
(cahier §5).

**Relation avec T-002** : cette vue socle est un sous-ensemble des attributs que T-002 détaillera
(profil complet, coordonnées bancaires vendeur, moyens de remboursement client — FR-055). Le socle ne
fixe pas ces attributs métier supplémentaires.

---

## Session

| Champ | Type | Règle |
|---|---|---|
| `id` | identifiant technique (jeton) | Jeton d'authentification porteur (voir `contracts/authentification.md`). |
| `compte_id` | référence → Compte | — |
| `cree_le` | horodatage | — |
| `expire_le` | horodatage | Durée de validité paramétrable (voir Parametre), jamais codée en dur. |
| `revoque_le` | horodatage, nullable | Permet une déconnexion explicite ou une révocation administrative. |

---

## Parametre

Toute valeur marquée MANQUANT ou HYPOTHÈSE dans le cahier et non tranchée (FR-021) — par exemple le
délai de réponse vendeur (Q19), le jour de reversement, le seuil d'alerte de délai légal — est portée
par cette entité générique, jamais codée en dur dans le code métier.

| Champ | Type | Règle |
|---|---|---|
| `cle` | chaîne, unique | Identifiant stable du paramètre (ex. convention `module.nom_parametre`). |
| `valeur` | chaîne/JSON | Typage applicatif selon le paramètre ; validation à la saisie par l'administrateur. |
| `type` | énumération : entier, durée, montant, liste, booléen, texte | Guide la validation de `valeur`. |
| `description` | texte | Explique l'usage du paramètre, à destination de l'administrateur (FR-021). |
| `modifie_par` | référence → Compte (rôle Administrateur) | Traçabilité de la dernière modification. |
| `modifie_le` | horodatage | — |

**Validation** : seule une saisie par un compte de rôle Administrateur peut modifier un paramètre
(FR-052 par analogie de cloisonnement, FR-021). Aucune valeur par défaut d'un paramètre représentant une
question ouverte du cahier (Q19, Q27, Q40, Q42, Q44, Q45, etc.) n'est pré-remplie par ce document — le
socle prévoit seulement le mécanisme.

---

## EntreeJournalAudit

Historise toute saisie de statut de livraison et tout mouvement financier (FR-022, Constitution
Principe IV). **Immuable** : une correction se fait uniquement par une nouvelle entrée référençant
l'entrée corrigée, jamais par mise à jour de l'existante.

| Champ | Type | Règle |
|---|---|---|
| `id` | identifiant technique | — |
| `acteur_compte_id` | référence → Compte, nullable | Nullable uniquement pour une action système (ex. traitement planifié) ; voir `acteur_systeme`. |
| `acteur_systeme` | chaîne, nullable | Nom du traitement planifié à l'origine de l'entrée, si `acteur_compte_id` est vide (FR-033). |
| `horodatage` | horodatage | — |
| `type_action` | énumération | Catégorie de l'action auditée : saisie de statut de livraison, encaissement, remise de fonds, écart, retenue, mise à disposition, remboursement, frais imputé, décision de litige, régularisation, reversement, exécution de traitement planifié (FR-022, FR-030). |
| `cible_type` | chaîne | Type de l'objet métier concerné (ex. SousCommande, MontantVendeur, Retour) — référence logique vers une entité de T-002, pas une clé étrangère base-de-données inter-module (FR-011). |
| `cible_id` | identifiant | — |
| `montant` | décimal, nullable | Renseigné uniquement si l'action porte un montant (Constitution Principe IV). |
| `motif` | texte | Justification lisible par un humain (obligatoire pour toute régularisation/correction). |
| `entree_corrigee_id` | référence → EntreeJournalAudit, nullable | Référence l'entrée que celle-ci corrige, le cas échéant ; **aucune entrée n'est jamais modifiée ou supprimée**. |

**Validation** : `montant` et `motif` sont obligatoires pour les types d'action financière ; aucune
opération d'écriture (UPDATE/DELETE) n'est autorisée sur cette table après création d'une ligne
(contrainte applicative, vérifiée par test — FR-022, Constitution Principe IV).

---

## NotificationInterne

Service de notification interne à l'application (M10, FR-023), distinct par construction de tout canal
externe (SMS, e-mail, WhatsApp — Q23 MANQUANT, hors socle).

| Champ | Type | Règle |
|---|---|---|
| `id` | identifiant technique | — |
| `destinataire_compte_id` | référence → Compte | — |
| `type_evenement` | chaîne | Identifie l'événement métier source (ex. nom de l'événement émis par un module, FR-014 : M10 consomme, n'écrit jamais dans les données des autres modules). |
| `contenu` | texte | Message affiché dans l'application ; pas de donnée personnelle sensible en clair (ENF-008, FR-057). |
| `cree_le` | horodatage | — |
| `lu_le` | horodatage, nullable | — |

**Validation** : ce service ne déclenche aucun envoi externe (SMS/e-mail/WhatsApp) ; l'éventuel
adaptateur externe est une extension séparée et non bloquante (Constitution §Contraintes et stack
technique).

---

## TachePlanifiee / ExecutionTachePlanifiee

Registre des traitements périodiques du planificateur (FR-024, FR-030 à FR-033). `TachePlanifiee` décrit
la définition (une par traitement), `ExecutionTachePlanifiee` historise chaque passage, pour garantir
l'idempotence et la rejouabilité testable avec horloge simulée.

### TachePlanifiee

| Champ | Type | Règle |
|---|---|---|
| `code` | chaîne, unique | Identifie le traitement (ex. les quatre traitements de FR-030 : expiration réponse vendeur, passage Retenu→Disponible, alerte délai légal, reversement hebdomadaire). |
| `module_proprietaire` | chaîne | Module M01–M11 propriétaire du traitement (FR-030 : M05, M07, M11, M07). |
| `frequence` | chaîne | Expression de planification (ex. cadence définie par paramètre, pas codée en dur si elle dépend d'une question ouverte). |
| `actif` | booléen | — |

### ExecutionTachePlanifiee

| Champ | Type | Règle |
|---|---|---|
| `id` | identifiant technique | — |
| `tache_code` | référence → TachePlanifiee | — |
| `cle_idempotence` | chaîne, unique par tâche | Identifie la période/l'état traité (ex. semaine de reversement) ; une seconde exécution avec la même clé ne doit produire aucun effet supplémentaire (FR-031, SC-005). |
| `demarree_le` | horodatage | Horloge pouvant être simulée en test (FR-032). |
| `terminee_le` | horodatage, nullable | — |
| `statut` | énumération : en cours, réussie, échouée | — |
| `resultat_resume` | texte | Résumé exploitable par l'équipe (nombre d'éléments traités, etc.), sans donnée personnelle sensible (FR-057). |

**Validation** : toute exécution qui modifie un statut ou un montant métier doit produire, en plus de
cette entrée, une ou plusieurs entrées dans `EntreeJournalAudit` (FR-033). L'unicité de `cle_idempotence`
par tâche est la garantie technique de FR-031.

---

## FichierPhoto / VarianteFichierPhoto

Fichier image associé à un produit (FR-040 à FR-044). Le lien vers le Produit propriétaire relève du
schéma métier de T-002 ; le socle ne fixe que la structure de stockage, de contrôle et de variantes.

### FichierPhoto

| Champ | Type | Règle |
|---|---|---|
| `id` | identifiant technique | — |
| `nom_stocke` | chaîne, unique | Nom de fichier généré (jamais dérivé d'une donnée prévisible permettant de déduire un autre produit ou vendeur — FR-042). |
| `proprietaire_vendeur_id` | référence logique → Compte (rôle Vendeur) | Permet le cloisonnement (FR-051) sans dupliquer la donnée métier Produit/Boutique de T-002. |
| `type_mime` | chaîne | Doit être un type image autorisé ; tout autre type est refusé (FR-040). |
| `taille_octets` | entier | Doit respecter la limite autorisée (valeur de la limite : voir Parametre ; non fixée ici) ; tout dépassement est refusé (FR-040). |
| `statut_controle` | énumération : accepte, refuse | Avec motif de refus explicite si refusé (FR-040). |
| `cree_le` | horodatage | — |

### VarianteFichierPhoto

| Champ | Type | Règle |
|---|---|---|
| `fichier_photo_id` | référence → FichierPhoto | — |
| `variante` | énumération : originale, mobile | Au moins une variante « mobile » lisible sur un écran de 360 px doit exister pour tout fichier accepté (FR-041, SC-006). |
| `chemin_stockage` | chaîne | Chemin sur le volume monté (ou clé d'objet si bascule vers un stockage S3-compatible, R4 de `research.md`) ; l'abstraction de système de fichiers masque cette différence au code métier. |
| `largeur_px` / `hauteur_px` | entier | — |

**Validation** : toute paire (fichier refusé) doit conserver le motif de refus pour restitution à
l'utilisateur (FR-040, SC-006) ; les fichiers acceptés sont inclus dans la stratégie de sauvegarde
(FR-043).

---

## Environnement d'exécution (référence de configuration, pas une table)

Chaque environnement (local, recette, production) porte sa propre configuration et ses propres secrets
(FR-003), jamais partagés ni commités (FR-056, Constitution Principe VIII). Ce n'est pas une entité
persistée en base mais une convention de configuration (voir `quickstart.md`).

---

## ADR (décision d'architecture) — référence

Les décisions techniques nécessaires au socle (R1–R6 de `research.md`) sont des documents, pas des
entités du modèle de données ; elles sont tenues dans `docs/architecture/DECISIONS.md`, au statut
initial « Proposé » (FR-007), hors du schéma de données applicatif.
