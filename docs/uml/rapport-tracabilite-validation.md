# Étape B — Rapport de traçabilité et de validation UML
**Projet** : Marketplace de produits locaux marocains · **Auteur** : Blueprint (UML Architect)  
**Source** : `cahier-des-charges-v1.1.md` (**Brouillon**, en attente de revalidation par le porteur) + `decisions.md` (D1–D44) + Stage A `00-etape-A-analyse-et-proposition.md` §10 (décisions b1-a … n7-a).  
**Réserve** : la v1.0 reste la référence validée tant que le porteur n'a pas revalidé la v1.1. Les écarts v1.0 → v1.1 proviennent tous de décisions du porteur (D37–D44) ; si la revalidation modifie ces points, les diagrammes concernés devront être régénérés.

Toutes les valeurs PASS/WARN/FAIL ci-dessous proviennent d'une exécution réelle : `validate.py` (drawio-skill v3.4.0), export PNG draw.io 32.4.1 sans écran (xvfb), inspection visuelle de chaque aperçu, et `_sources/audit.py` (extraction des ID depuis les propriétés `req` et les libellés des fichiers .drawio).

## 1. Livrables

| ID | Fichier .drawio (éditable) | Éléments | `validate.py` | Rendu PNG | Inspection visuelle |
|---|---|---|---|---|---|
| UC-DIAG-01 | `01-cas-utilisation/UC-DIAG-01-achat.drawio` | 34 | PASS (0 err, 0 warn) | PASS | PASS |
| UC-DIAG-02 | `01-cas-utilisation/UC-DIAG-02-vente.drawio` | 21 | PASS (0 err, 0 warn) | PASS | PASS |
| UC-DIAG-03 | `01-cas-utilisation/UC-DIAG-03-exploitation.drawio` | 31 | PASS (0 err, 0 warn) | PASS | PASS |
| CLASS-01 | `02-classes/CLASS-01-comptes-catalogue-commandes.drawio` | 56 | PASS (0 err, 0 warn) | PASS | PASS |
| CLASS-02 | `02-classes/CLASS-02-retours-argent.drawio` | 64 | PASS (0 err, 0 warn) | PASS | PASS |
| SEQ-001 | `03-sequences/SEQ-001-commande-multi-vendeurs.drawio` | 33 | WARN (0 err, 4 warn) | PASS | PASS |
| SEQ-002 | `03-sequences/SEQ-002-collecte-livraison-encaissement.drawio` | 38 | WARN (0 err, 2 warn) | PASS | PASS |
| SEQ-003 | `03-sequences/SEQ-003-retour-litige-remboursement.drawio` | 52 | WARN (0 err, 4 warn) | PASS | PASS |
| ACTIVITY-001 | `04-activites/ACTIVITY-001-cycle-commande.drawio` | 52 | PASS (0 err, 0 warn) | PASS | PASS |
| ACTIVITY-002 | `04-activites/ACTIVITY-002-processus-retour.drawio` | 58 | PASS (0 err, 0 warn) | PASS | PASS |
| ACTIVITY-003 | `04-activites/ACTIVITY-003-retenue-reversement.drawio` | 47 | PASS (0 err, 0 warn) | PASS | PASS |
| STATE-001 | `05-etats/STATE-001-commande.drawio` | 27 | PASS (0 err, 0 warn) | PASS | PASS |
| STATE-002 | `05-etats/STATE-002-sous-commande.drawio` | 25 | PASS (0 err, 0 warn) | PASS | PASS |
| STATE-003 | `05-etats/STATE-003-retour.drawio` | 27 | PASS (0 err, 0 warn) | PASS | PASS |
| STATE-004 | `05-etats/STATE-004-montant-vendeur.drawio` | 20 | PASS (0 err, 0 warn) | PASS | PASS |

Aperçus de contrôle (brouillons non éditables) : `_previews/*.png`. Générateurs reproductibles : `_sources/*.py` (régénération explicite avec `BP_REGEN=1`, sinon refus d'écraser un fichier existant).

**Avertissements résiduels SEQ-001/002/003 (WARN, accepté)** : `W-OVERLAP` entre une note et la ligne de vie qu'elle commente (notes posées volontairement sur la ligne de vie, convention UML). Aucun chevauchement de messages, cadres ou libellés n'a été constaté à l'inspection visuelle.

## 2. Couverture des exigences (extraction automatique)

| Famille | Définies dans le CDC v1.1 | Couvertes | Manquantes | Statut |
|---|---|---|---|---|
| Fonctionnalités MUST | 15 | 15 | — | PASS |
| Règles métier | 31 | 31 | — | PASS |
| Critères d'acceptation | 48 | 48 | — | PASS |
| User stories | 15 | 15 | — | PASS |
| Exigences non fonctionnelles | 12 | 5 | ENF-001, ENF-002, ENF-003, ENF-004, ENF-005, ENF-006, ENF-011 | WARN (hors UML, voir §4) |

Les SHOULD/COULD F015–F021 (toutes SUGGESTION) sont **exclues** par décision Stage A et ne figurent dans aucun diagramme.

## 3. Matrice de traçabilité

### 3.1 Fonctionnalités → diagrammes

| Exigence | Diagrammes |
|---|---|
| F001 | ACTIVITY-001, CLASS-01, UC-DIAG-01 |
| F002 | CLASS-01, UC-DIAG-02 |
| F003 | CLASS-01, UC-DIAG-02 |
| F004 | CLASS-01, UC-DIAG-01 |
| F005 | CLASS-01, UC-DIAG-01 |
| F006 | ACTIVITY-001, CLASS-01, SEQ-001, UC-DIAG-01 |
| F007 | ACTIVITY-001, CLASS-01, SEQ-001, STATE-001, UC-DIAG-01 |
| F008 | ACTIVITY-001, CLASS-01, STATE-001, UC-DIAG-01 |
| F009 | ACTIVITY-001, CLASS-01, SEQ-001, SEQ-002, STATE-001, STATE-002, UC-DIAG-02 |
| F010 | ACTIVITY-001, ACTIVITY-003, CLASS-01, CLASS-02, SEQ-002, STATE-001, STATE-002, STATE-004, UC-DIAG-03 |
| F011 | ACTIVITY-002, ACTIVITY-003, CLASS-02, SEQ-002, SEQ-003, STATE-004, UC-DIAG-02, UC-DIAG-03 |
| F012 | CLASS-01, UC-DIAG-01 |
| F013 | CLASS-01, STATE-002, UC-DIAG-03 |
| F014 | ACTIVITY-001, ACTIVITY-003, SEQ-001, SEQ-002, SEQ-003, STATE-001, STATE-002, UC-DIAG-01 |
| F022 | ACTIVITY-002, CLASS-02, SEQ-003, STATE-003, UC-DIAG-01, UC-DIAG-02, UC-DIAG-03 |

### 3.2 Règles métier → diagrammes

| Règle | Diagrammes |
|---|---|
| RG-001 | ACTIVITY-001, CLASS-01, SEQ-001, UC-DIAG-01, UC-DIAG-03 |
| RG-002 | ACTIVITY-001, CLASS-01, SEQ-002, UC-DIAG-01 |
| RG-003 | ACTIVITY-001, CLASS-01, SEQ-001, STATE-001, STATE-002, UC-DIAG-01, UC-DIAG-02 |
| RG-004 | UC-DIAG-02 |
| RG-005 | ACTIVITY-003, STATE-004, UC-DIAG-02 |
| RG-006 | CLASS-01, UC-DIAG-01, UC-DIAG-02 |
| RG-007 | CLASS-01, SEQ-001, UC-DIAG-01, UC-DIAG-02 |
| RG-008 | ACTIVITY-001, CLASS-01, SEQ-001, SEQ-002, STATE-001, STATE-002, UC-DIAG-01, UC-DIAG-02, UC-DIAG-03 |
| RG-009 | CLASS-01, SEQ-002, UC-DIAG-01 |
| RG-010 | ACTIVITY-001, STATE-001, STATE-002, UC-DIAG-01 |
| RG-011 | CLASS-01, UC-DIAG-01 |
| RG-011b | ACTIVITY-001, SEQ-001, STATE-001, STATE-002, UC-DIAG-02 |
| RG-012 | ACTIVITY-003, CLASS-02, STATE-004, UC-DIAG-02 |
| RG-013 | ACTIVITY-001, CLASS-01, SEQ-002, STATE-001, UC-DIAG-03 |
| RG-014 | ACTIVITY-001, CLASS-01, UC-DIAG-01 |
| RG-015 | CLASS-01, UC-DIAG-02, UC-DIAG-03 |
| RG-016 | UC-DIAG-02 |
| RG-017 | ACTIVITY-001, ACTIVITY-002, CLASS-01, CLASS-02, SEQ-001, SEQ-002, SEQ-003, STATE-001, STATE-003, UC-DIAG-01, UC-DIAG-02 |
| RG-018 | ACTIVITY-003, CLASS-01, CLASS-02, STATE-004, UC-DIAG-02, UC-DIAG-03 |
| RG-019 | ACTIVITY-002, CLASS-01, CLASS-02, SEQ-003, STATE-003, UC-DIAG-01, UC-DIAG-02, UC-DIAG-03 |
| RG-020 | CLASS-02, SEQ-002, UC-DIAG-03 |
| RG-021 | ACTIVITY-002, ACTIVITY-003, CLASS-02, SEQ-003, STATE-003, STATE-004, UC-DIAG-02, UC-DIAG-03 |
| RG-022 | ACTIVITY-002, CLASS-02, SEQ-003, STATE-003, UC-DIAG-01, UC-DIAG-03 |
| RG-023 | CLASS-01, UC-DIAG-02, UC-DIAG-03 |
| RG-024 | ACTIVITY-001, ACTIVITY-003, CLASS-02, SEQ-002, STATE-004, UC-DIAG-02, UC-DIAG-03 |
| RG-025 | ACTIVITY-002, ACTIVITY-003, CLASS-02, SEQ-003, STATE-003, STATE-004, UC-DIAG-01, UC-DIAG-03 |
| RG-026 | ACTIVITY-001, SEQ-001, UC-DIAG-01 |
| RG-027 | ACTIVITY-002, CLASS-02, SEQ-003, STATE-003, UC-DIAG-02, UC-DIAG-03 |
| RG-028 | ACTIVITY-001, CLASS-01, SEQ-001, UC-DIAG-01 |
| RG-029 | ACTIVITY-001, ACTIVITY-002, SEQ-002, SEQ-003, STATE-001, STATE-002, STATE-003, UC-DIAG-03 |
| RG-030 | ACTIVITY-002, CLASS-02, SEQ-003, STATE-003, UC-DIAG-01 |

### 3.3 User stories et critères d'acceptation → diagrammes

| ID | Diagrammes |
|---|---|
| US-001 | UC-DIAG-02 |
| US-002 | UC-DIAG-02 |
| US-003 | UC-DIAG-01 |
| US-004 | UC-DIAG-01 |
| US-005 | UC-DIAG-01 |
| US-006 | UC-DIAG-01 |
| US-007 | UC-DIAG-02 |
| US-008 | ACTIVITY-001, UC-DIAG-03 |
| US-009 | ACTIVITY-003, UC-DIAG-02 |
| US-010 | UC-DIAG-01 |
| US-011 | UC-DIAG-03 |
| US-012 | UC-DIAG-01 |
| US-013 | UC-DIAG-01 |
| US-014 | ACTIVITY-002, CLASS-02, UC-DIAG-02 |
| US-015 | ACTIVITY-002, CLASS-02, UC-DIAG-03 |
| CA-F001-1 | UC-DIAG-01 |
| CA-F001-2 | UC-DIAG-01 |
| CA-F001-3 | ACTIVITY-001, CLASS-01, UC-DIAG-01 |
| CA-F002-1 | UC-DIAG-02 |
| CA-F002-2 | CLASS-01, UC-DIAG-02 |
| CA-F002-3 | UC-DIAG-02 |
| CA-F003-1 | UC-DIAG-02 |
| CA-F003-2 | UC-DIAG-02 |
| CA-F003-3 | UC-DIAG-02 |
| CA-F004-1 | UC-DIAG-01 |
| CA-F004-2 | UC-DIAG-01 |
| CA-F005-1 | UC-DIAG-01 |
| CA-F006-1 | CLASS-01 |
| CA-F006-2 | CLASS-01 |
| CA-F007-1 | ACTIVITY-001, SEQ-001, STATE-001 |
| CA-F007-2 | ACTIVITY-001, SEQ-001 |
| CA-F007-3 | ACTIVITY-001 |
| CA-F007-4 | ACTIVITY-001 |
| CA-F008-1 | STATE-001, UC-DIAG-01 |
| CA-F008-2 | ACTIVITY-001, STATE-001, UC-DIAG-01 |
| CA-F009-1 | CLASS-01, UC-DIAG-02 |
| CA-F009-2 | ACTIVITY-001, SEQ-001, SEQ-002, STATE-002 |
| CA-F009-3 | ACTIVITY-001, SEQ-001, STATE-001, STATE-002 |
| CA-F010-1 | ACTIVITY-001, ACTIVITY-003, CLASS-01, CLASS-02, SEQ-002, STATE-001, STATE-004, UC-DIAG-03 |
| CA-F010-2 | ACTIVITY-001, CLASS-02, SEQ-002, STATE-001, UC-DIAG-03 |
| CA-F010-3 | ACTIVITY-001, CLASS-01, SEQ-002, STATE-001, UC-DIAG-03 |
| CA-F010-4 | ACTIVITY-001, SEQ-002, STATE-001, STATE-002, UC-DIAG-03 |
| CA-F011-1 | ACTIVITY-003, CLASS-02, STATE-004 |
| CA-F011-2 | ACTIVITY-003, CLASS-02, STATE-004, UC-DIAG-03 |
| CA-F011-3 | ACTIVITY-002, ACTIVITY-003, CLASS-02, SEQ-003, STATE-004 |
| CA-F011-4 | ACTIVITY-002, ACTIVITY-003, CLASS-02, SEQ-003, STATE-004 |
| CA-F011-5 | ACTIVITY-003, CLASS-02, STATE-004, UC-DIAG-03 |
| CA-F012-1 | UC-DIAG-01 |
| CA-F012-2 | UC-DIAG-01 |
| CA-F013-1 | UC-DIAG-03 |
| CA-F013-2 | UC-DIAG-03 |
| CA-F013-3 | CLASS-01, UC-DIAG-03 |
| CA-F014-1 | ACTIVITY-001, SEQ-001, STATE-002 |
| CA-F014-2 | ACTIVITY-001, SEQ-001, STATE-001 |
| CA-F022-1 | ACTIVITY-002, CLASS-02, SEQ-003, STATE-003 |
| CA-F022-2 | ACTIVITY-002, SEQ-003, STATE-003 |
| CA-F022-3 | ACTIVITY-002, SEQ-003, STATE-003 |
| CA-F022-4 | ACTIVITY-002, CLASS-02, SEQ-003 |
| CA-F022-5 | ACTIVITY-002, CLASS-02, SEQ-003, STATE-003, UC-DIAG-03 |
| CA-F022-6 | ACTIVITY-002, CLASS-02, SEQ-003, STATE-003, UC-DIAG-03 |
| CA-F022-7 | ACTIVITY-002, CLASS-02, SEQ-003, STATE-003, UC-DIAG-03 |
| CA-F022-8 | ACTIVITY-002, SEQ-003, STATE-003 |
| CA-F022-9 | ACTIVITY-002, CLASS-02, SEQ-003 |

### 3.4 Éléments Blueprint → sources

| Élément | Diagramme | Source principale |
|---|---|---|
| ACT-001 Visiteur [I] | UC-DIAG-01 | §5 (navigation sans compte = HYPOTHÈSE) |
| ACT-002 Client | UC-DIAG-01, SEQ-001/003, ACTIVITY-001/002 | §5, D41 |
| ACT-003 Vendeur | UC-DIAG-02, SEQ, ACTIVITY | §5, D31, D33, D43 |
| ACT-004 Administrateur | UC-DIAG-03, SEQ-002/003, ACTIVITY | §5, D31, D37, D38 |
| ACT-005 Société de livraison «externe», sans association | UC-DIAG-03, SEQ-002/003, ACTIVITY-001/002 | D19, D38, RG-029 |
| UC-001 … UC-023 | UC-DIAG-01/02/03 | voir propriété `req` de chaque cas |
| ENT-001 … ENT-021 + 10 énumérations | CLASS-01/02 | Stage A §5 ; attributs du CDC uniquement |
| SEQ-001 / 002 / 003 | 03-sequences | P2/P4 ; P5 ; P3 |
| ACTIVITY-001 / 002 / 003 | 04-activites | P2/P4/P5 ; P3 ; F011 |
| STATE-001 … 004 | 05-etats | §7 cycles de vie |

## 4. Exigences non fonctionnelles

| ENF | Traitement | Statut |
|---|---|---|
| ENF-001 Langues | Hors UML (qualité d'interface) | WARN — hors UML, MANQUANT Q11 |
| ENF-002 Mobile | Hors UML | WARN — hors UML |
| ENF-003 Simplicité vendeur | Hors UML | WARN — hors UML |
| ENF-004 Performance | Hors UML | WARN — hors UML |
| ENF-005 Disponibilité | Hors UML | WARN — hors UML |
| ENF-006 Volumes | Hors UML | WARN — hors UML, MANQUANT Q21 |
| ENF-007 Sécurité / cloisonnement | Notes UC-DIAG-02 et UC-DIAG-03 ; société de livraison sans association | PASS |
| ENF-008 Traçabilité financière | Classes RemiseDeFonds, Écart, Déduction, Remboursement, Reversement (CLASS-02) | PASS |
| ENF-009 Conformité légale | Confirmation écrite (SEQ-001) ; délais légaux (ACTIVITY-002, STATE-003) | PASS (validation juridique C-08 hors modèle) |
| ENF-010 Évolutivité | VilleDesservie, CommuneVendeur paramétrables (CLASS-01) ; UC-021 | PASS |
| ENF-011 Photos | Hors UML | WARN — hors UML |
| ENF-012 Délai de remboursement | Événement temporel ACTIVITY-002, note STATE-003, attribut /procheDélaiLégal | PASS |

## 5. Contrôles de qualité (§8 du rôle Blueprint)

| Contrôle | Résultat | Preuve |
|---|---|---|
| Toutes les fonctionnalités MUST considérées | PASS | 15/15 (audit.json) |
| Acteurs justifiés par la source ou marqués inférés | PASS | ACT-001 marqué [I] ; ACT-005 «externe» sans accès (D38) |
| Cas d'utilisation = objectifs réels (pas de boutons) | PASS | 23 cas ; accepter/refuser regroupés (UC-012) |
| «include»/«extend» justifiés | PASS | UC-005 «include» UC-004 (RG-028) ; UC-007 «extend» UC-006 avec condition RG-010 |
| Relations de classes justifiées | PASS / WARN | compositions Commande→SousCommande→LigneCommande, Retour→Vérif./Litige/Remb. ; 6 associations inférées en pointillé |
| Aucun attribut / opération inventé | PASS | attributs issus du CDC ; [I]/[U] signalés ; aucune opération |
| Séquences dans l'ordre chronologique du scénario | PASS | P2/P4 (SEQ-001), P5 (SEQ-002), P3 (SEQ-003) |
| Activités conformes aux parcours | PASS | couloirs Client/Plateforme/Vendeur/Admin/Société de livraison |
| Transitions d'états appuyées par des règles | PASS / WARN | §7 ; transitions [I] signalées (ex. STATE-004 t1b, t4) |
| Décisions du porteur appliquées (B1–B5, N5–N7) | PASS | RG-011/015 confirmées ; admin seul (RG-029) ; 1 retour/produit (RG-030) ; exclusion produit ∨ catégorie (RG-019) ; compte obligatoire ; frais déduits ; remise en vente vendeur ; « En collecte » à la transmission |
| Contradictions et manques documentés | PASS | notes WARN dans 13 diagrammes (SEQ-001 et SEQ-003 : réserves en notes jaunes) ; §6 ci-dessous |
| Fichiers éditables | PASS | XML draw.io non compressé ; ouverts et rendus par draw.io 32.4.1 |
| Aucun diagramme écrasé silencieusement | PASS | dossiers créés vides ; seuls les fichiers de cette génération ont été régénérés (BP_REGEN=1) |
| Validation structurelle | PASS / WARN | 0 erreur sur 15 fichiers ; 10 avertissements note/ligne de vie (SEQ) |
| Inspection visuelle | PASS | 15 aperçus PNG inspectés ; défauts corrigés en 1 à 2 itérations |

## 6. Hypothèses, limites et questions ouvertes portées par les diagrammes

- **Version de référence** : modèles fondés sur la v1.1 Brouillon (voir réserve en tête).
- **Délais non chiffrés**, modélisés comme événements paramétrés : réponse vendeur (Q19), vérification du retour (Q44), jour du reversement, délai légal de 15 j (R1, à valider C-08).
- **Q24** : suite d'un échec de livraison non définie → état final provisoire dans STATE-001.
- **Q38** : solde vendeur négatif → report signalé, HYPOTHÈSE (ACTIVITY-003).
- **Q40 / Q42 / Q43 / Q45 / Q27** : montants et moyens portés comme attributs sans valeur.
- **Q44 au-delà du délai** : décision de l'administrateur [I], transition non dessinée dans STATE-003 faute de cible définie.
- **Cycles de vie §7** : HYPOTHÈSE, sauf « En collecte » (D44) et le cycle Montant vendeur (D29, D34).
- **Inférences Blueprint** (pointillés [I]) : une boutique par vendeur ; MontantVendeur porté par LigneCommande ; RemiseDeFonds/Écart ; Client spécialise Visiteur ; Panier 0..1 par client.
- **N8 / Q39** (identité du « fournisseur », loi 31-08) et **N9** (en-cours d'un vendeur suspendu) : notes, sans effet structurel.
- **Non produits, conformément à la proposition** : diagrammes de composants et de déploiement (C-07).

## 7. Environnement et méthode

- Génération : `_sources/umlkit.py` (styles UML de `drawio-skill/references/diagram-types.md`) + un script par famille. Chaque élément porte les propriétés `req` (ID sources) et `statut` (E / I / WARN), consultables dans draw.io via *Édition > Modifier les données*.
- Validation : `python3 drawio-skill/scripts/validate.py <fichier> --score` (aussi en `--json` dans `_sources/audit.json`).
- Rendu : `xvfb-run -a drawio -x -f png … --disable-gpu --no-sandbox --disable-dev-shm-usage`. Sans `--disable-dev-shm-usage`, le moteur de rendu plante sur les grandes pages (/dev/shm = 64 Mo).
- La matrice §3 est extraite automatiquement des propriétés `req` et des libellés ; elle indique où un ID est référencé, et non une preuve sémantique en soi. Les vérifications sémantiques figurent au §5.
