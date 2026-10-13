# Sécurité et données — marketplace-produits-locaux-maroc

**Tâche** : T-001 · **Auteur** : Keystone · **Date** : 2026-10-13 · **Statut** : Proposé
Portée : exigences de sécurité et de protection des données que le socle doit satisfaire. Ce document **ne remplace pas** la validation juridique (C-08, ENF-009), qui reste obligatoire avant le lancement.

## 1. Sources

- Cahier des charges v1.1 : ENF-007 (sécurité), ENF-008 (traçabilité), ENF-009 (conformité), §19 (sécurité et données), §5 (matrice des permissions), §18 (C-08).
- Décisions : D28/D32 (remboursement traçable), D31 (vérification et litiges), D37 (modération), D38 (la société de livraison n'accède pas à la Plateforme), D41 (compte client obligatoire), D42 (frais de retour), D45 (validation du cahier).
- Constitution du projet : principes IV (argent et traçabilité), V (cloisonnement testé), VIII (aucun secret dans le dépôt), X (validation juridique avant lancement).

## 2. Acteurs, accès et cloisonnement (ENF-007)

| Acteur | Accès à la Plateforme | Données accessibles | Données interdites |
|---|---|---|---|
| Visiteur | Consultation | Catalogue, fiches produits, avis publiés, panier | Toute donnée de compte, toute commande |
| Client | Compte personnel | Ses commandes, ses retours, ses avis, son moyen de remboursement | Données d'un autre client, données de vendeurs autres que publiques |
| Vendeur | Compte personnel | Ses produits, ses sous-commandes (quantités et informations de préparation), ses retours, ses montants | **Adresse et téléphone du client**, données d'un autre vendeur, données d'administration |
| Administrateur | Compte personnel | Supervision complète : vendeurs, produits, commandes, retours, montants, coordonnées bancaires, journal d'audit | Rien de prévu par le cahier |
| Société de livraison | **Aucun accès** (D38) | — (informations transmises hors Plateforme par l'administrateur) | Toute la Plateforme |

**Règles d'implémentation attendues** :
1. Autorisation à deux niveaux : **rôle** (une capacité de la matrice §5 s'exerce ou non) **et propriété** (une ressource appartient à l'acteur). Aucune ressource n'est exposée sans les deux contrôles.
2. Le cloisonnement est appliqué **côté serveur** dans les requêtes (filtre par propriétaire), jamais seulement par l'interface.
3. La société de livraison n'obtient ni compte ni jeton.
4. Les capacités du tableau ci-dessus sont couvertes une par une par un test autorisé **et** un test interdit (T-066), matrice de référence : cahier §5.

## 3. Authentification et secrets

- Identifiant principal : **téléphone** (RG-014), mot de passe personnel ; mot de passe **haché**, jamais stocké ni affiché en clair, jamais renvoyé par l'API, jamais journalisé.
- Message d'erreur de connexion **sans préciser** quel champ est faux (critère CA-F001-2 et plan T-014).
- La récupération d'accès dépend d'un canal externe non tranché (Q23, M-06) : **bloquée**, tâche T-015 ; aucun mécanisme provisoire non traçable ne doit être introduit.
- **Aucun secret dans le dépôt** : ni mot de passe, ni clé d'API, ni jeton, ni identifiant de base. Uniquement des variables d'environnement, documentées sans valeur réelle (`.env.example`). Les valeurs de production sont saisies hors dépôt.
- Le contrôle d'accès est revérifié à chaque requête (pas de confiance dans un état stocké côté client).

## 4. Données personnelles et sensibles (cahier §19, loi 09-08)

| Catégorie | Exemples | Protection attendue |
|---|---|---|
| Identité et contact client | nom, téléphone, adresse de livraison | Accès administrateur et titulaire uniquement ; adresse et téléphone invisibles au vendeur |
| Données de remboursement client | moyen et référence de remboursement | Accès administrateur et titulaire ; traçabilité (ENF-008) |
| Données vendeur | identité, commune, adresse de collecte, coordonnées bancaires | Coordonnées bancaires visibles par l'administrateur et le titulaire seulement |
| Données de commande et de retour | commandes, retours, motifs | Cloisonnement par propriété |
| Journal d'audit | qui, quand, montant, motif | Consultation administrateur ; non modifiable |

- **Minimisation** : seules les données nécessaires à chaque mission sont accessibles ; l'administrateur ne transmet à la société de livraison que ce dont elle a besoin (adresses, téléphone du client, montant à encaisser).
- **Durées de conservation** : **MANQUANT** dans le cahier (§19) → `[NEEDS CLARIFICATION]` dans la spécification ; aucune purge automatique n'est codée avant la décision.
- **Droits des personnes** (accès, rectification) : la procédure n'est pas définie par le cahier ; à traiter avec le conseil juridique avant lancement.
- **Transferts** : aucun transfert de données hors du périmètre V1 (Maroc) prévu ; toute évolution (livraison internationale, §21) devra être réexaminée au regard de la loi 09-08.

## 5. Traçabilité financière et non-répudiation (ENF-008)

- Chaque **encaissement, remise de fonds, écart, retenue, mise à disposition, remboursement (moyen, référence, date), frais de retour imputé, décision de litige, régularisation et reversement** est historisé avec qui, quand, montant et motif.
- Chaque **saisie de statut de livraison ou de reprise** par l'administrateur est historisée.
- Les entrées d'audit sont en **ajout seul** : aucune modification ni suppression depuis l'interface d'administration (ADR-008).
- Aucune valeur métier n'est écrite en dur : délais, frais et seuils viennent du module **Paramètres** (T-007), ce qui rend les règles auditables et modifiables sans redéploiement (H-08).

## 6. Intégrité des opérations sensibles

- **Stock et argent** : toute réservation ou restitution de stock et toute écriture de montant s'effectuent dans une **transaction** ; en cas de concurrence sur le dernier article, une seule commande réussit (vérification de T-028).
- **États métier** : un seul service écrit chaque famille de statuts (commande/sous-commande, montant vendeur, retour) ; une transition interdite produit une erreur, jamais un état incohérent.
- **Idempotence** : les traitements planifiés ne produisent ni doublon de statut ni doublon de montant (voir `ARCHITECTURE.md` §6).
- **Moyens de remboursement** : un remboursement en espèces non traçable est refusé (D28, D32).

## 7. Application, dépendances et exploitation

- Toute entrée utilisateur est validée côté serveur (type, taille des fichiers photos, formats autorisés, longueurs) ; les fichiers non conformes sont refusés avec un message explicite.
- Les listes et formulaires d'administration sont filtrés par rôle **et** par propriété, y compris en cas d'appel direct de l'API.
- Les dépendances suivent les correctifs de sécurité ; une revue de sécurité est faite avant lancement (recette) : aucun accès interdit réussi, aucun secret dans le dépôt ou son historique.
- Transport chiffré (HTTPS) sur tous les environnements exposés ; accès à la base non exposé publiquement.
- Journaux applicatifs : événements techniques et erreurs, **sans** mot de passe, jeton, coordonnées bancaires ni données de santé/financières détaillées.
- Sauvegardes : quotidiennes (base + fichiers photos), stockées hors de l'hôte applicatif si possible, restauration testée au moins une fois (T-069).

## 8. Conformité et porte de lancement

- **Loi 31-08** (protection du consommateur, vente à distance) : information précontractuelle, confirmation écrite de commande, droit de rétractation de 7 jours, exclusions légales, frais de retour, délais de remboursement. Les mécanismes sont prévus (gabarit de confirmation T-029, paramètres de délais, alertes T-050, gestion des exclusions T-042).
- **Loi 09-08** (données personnelles, CNDP) : minimisation, cloisonnement, durées de conservation (à décider), droits des personnes (à décider).
- **Question ouverte Q39** : qui est le « fournisseur » au sens de la loi 31-08 (la Plateforme ou chaque vendeur) — décision du porteur, impacte le contenu de la confirmation écrite.
- **C-08** : la validation juridique est une **porte de lancement bloquante** ; aucun développement ne peut la contourner, et un lancement sans avis juridique n'est pas couvert par ce dossier.

## 9. Points à décider par @user (rappel)

1. Durée de conservation des données personnelles (cahier §19).
2. Procédure des droits d'accès et de rectification des personnes.
3. Canal externe de notification (Q23) — impacte la récupération d'accès (M-06, T-015 bloquée).
4. Identité du « fournisseur » au sens de la loi 31-08 (Q39).
