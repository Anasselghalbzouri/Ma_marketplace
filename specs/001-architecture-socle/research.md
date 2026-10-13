# Research — Architecture du socle technique (T-001)

**Feature** : `001-architecture-socle` | **Date** : 2026-10-13

**Portée de ce document** : il consolide les arbitrages nécessaires au socle transverse, imposés par
l'absence de contrainte technique du porteur (C-07, Constitution §Contraintes et stack technique) et
confirmés par les décisions de l'architecte reçues en entrée de cette tâche. Chaque arbitrage est
documenté sous forme Décision / Raison / Alternatives envisagées / Conséquences / Statut, puis repris
en ADR « Proposé » dans `docs/architecture/DECISIONS.md` (FR-007). Aucune valeur métier n'est fixée ici ;
seules les options d'architecte tranchées par la Constitution (§Contraintes et stack technique) et les
directives transmises pour cette tâche sont consolidées.

---

## R1 — Monolithe modulaire vs services séparés

- **Décision** : monolithe modulaire Laravel 11 / PHP 8.3, un seul déployable applicatif ; les modules
  M01–M11 du cahier §9 sont des namespaces/contextes internes (`app/Modules/...`), pas des services
  réseau séparés.
- **Raison** : Constitution Principe II (Simplicité extensible) et C-04 imposent une V1 simple et
  extensible sans sur-ingénierie ; ENF-010 (évolutivité) est obtenue par des frontières de module
  claires et un graphe de dépendances documenté (spec FR-014), pas par un découpage réseau. Aucun besoin
  validé (volumétrie, équipe, disponibilité différenciée par module) ne justifie le coût opérationnel de
  services séparés.
- **Alternatives envisagées** :
  - *Microservices par module* — rejeté : complexité de déploiement, de transaction distribuée (en
    particulier pour l'argent, Constitution Principe IV) et d'exploitation disproportionnée pour une V1
    de lancement local (zone Tanger), sans exigence du cahier qui l'impose.
  - *Monolithe non modulaire (sans frontières)* — rejeté : violerait Constitution Principe III (une
    seule porte par état métier) et FR-011/FR-012, qui exigent une propriété exclusive des données par
    module.
- **Conséquences** : un seul pipeline de build/déploiement ; la discipline de frontière entre modules
  (pas d'accès direct aux données d'un autre module, FR-011) devient une règle de revue de code, pas une
  barrière réseau — donc plus facile à contourner par erreur, d'où l'exigence de gouvernance (Constitution
  — Gouvernance, FR-013/FR-014).
- **Statut** : décision d'architecte (C-07), **ADR « Proposé »** — révisable par le porteur du projet.

---

## R2 — MySQL 8 vs autres moteurs de base de données

- **Décision** : MySQL 8, encodage `utf8mb4`, transactions explicites pour toute opération affectant un
  montant ou un stock.
- **Raison** : compatibilité native avec l'écosystème Laravel (migrations, Eloquent, transactions ACID),
  support des caractères multilingues (noms de produits, avis en arabe/français) via `utf8mb4` ; aucune
  exigence du cahier n'impose un moteur spécifique (C-07).
- **Alternatives envisagées** :
  - *PostgreSQL* — solution également viable et pleinement supportée par Laravel ; non retenue faute de
    besoin différenciant (ex. types JSON avancés, contraintes d'exclusion) exprimé par le cahier ;
    changement de moteur resterait possible via la couche d'abstraction Eloquent si un besoin apparaît,
    mais n'est pas prévu en l'état.
  - *Moteur NoSQL (document)* — rejeté : incompatible avec Constitution Principe IV (traçabilité
    financière, contraintes d'intégrité relationnelle fortes entre Commande/SousCommande/MontantVendeur/
    Retour) et Principe III (une seule porte par état métier, modélisation relationnelle naturelle).
- **Conséquences** : le schéma physique détaillé (entités métier) relève de T-002 ; ce document ne fixe
  que le socle (voir `data-model.md`). Les opérations financières et de stock doivent systématiquement
  être enveloppées dans des transactions explicites (`DB::transaction` ou équivalent), conformément à
  Constitution Principe IV.
- **Statut** : décision d'architecte (C-07), **ADR « Proposé »**.

---

## R3 — File d'attente + planificateur intégrés vs cron dispersés

- **Décision** : mécanisme natif Laravel — file d'attente (queue) pour le travail asynchrone, et
  planificateur (scheduler, un point d'entrée unique `app/Console/Kernel`) pour les traitements
  périodiques ; chaque traitement planifié est idempotent, rejouable et testable avec une horloge
  simulée (FR-030 à FR-033, SC-004, SC-005).
- **Raison** : les tâches T-005, T-034, T-050, T-053, T-054 du plan exigent explicitement cette
  propriété de test ; un cron dispersé (scripts système indépendants, sans registre central) ne permet ni
  un point d'audit unique, ni une simulation d'horloge en test, ni une garantie d'idempotence
  homogène — chaque script devrait réinventer sa propre protection contre les doublons.
- **Alternatives envisagées** :
  - *Cron système par script indépendant* — rejeté : pas de registre central des tâches planifiées, pas
    de mécanisme de test à horloge simulée commun, risque de divergence de convention entre les quatre
    traitements (FR-030).
  - *Orchestrateur de workflow externe (ex. outil de CI dédié, planificateur distribué)* — rejeté à ce
    stade : complexité disproportionnée pour quatre traitements périodiques sur un seul hôte (Constitution
    Principe II) ; réévaluable si la montée en charge (FR-070) l'exige.
- **Conséquences** : chaque exécution de traitement planifié qui modifie un statut ou un montant doit
  produire une entrée dans le journal d'audit transverse (FR-033) ; un verrou d'idempotence par
  exécution (ex. identifiant de période traitée) est nécessaire pour satisfaire FR-031 ; le worker de
  file est un service Docker Compose séparé du serveur web (point 6 des directives), pour isoler sa
  charge.
- **Statut** : décision d'architecte (C-07), **ADR « Proposé »**.

---

## R4 — Stockage des photos : volume local monté vs objet (S3) dès le lancement

- **Décision** : stockage sur volume monté, servi par l'application/le serveur web, avec variantes
  redimensionnées pour mobile, contrôle de type/taille et convention de nommage (FR-040 à FR-044).
  L'option de stockage objet compatible S3 est documentée comme évolution possible, sans changement du
  code métier, via la couche d'abstraction de système de fichiers (pilote interchangeable).
- **Raison** : ENF-010/ENF-011 exigent une évolutivité sans refonte ; un stockage local est suffisant et
  moins coûteux pour un lancement mono-hôte (zone Tanger, volumétrie non connue — ENF-006/Q21
  MANQUANT) ; l'abstraction du système de fichiers permet de reporter le choix d'un stockage objet sans
  bloquer le lancement.
- **Alternatives envisagées** :
  - *Stockage objet S3 (ou compatible) dès le lancement* — non retenu comme choix par défaut : introduit
    une dépendance externe et un coût récurrent non justifiés avant connaissance de la volumétrie réelle
    (HYPOTHÈSE H-11, Q21 MANQUANT) ; reste l'option recommandée dès que la réplique de l'application en
    plusieurs instances (montée en charge, point 6) rendrait un volume local partagé entre instances plus
    complexe à maintenir que du stockage objet.
  - *Stockage en base de données (BLOB)* — rejeté : dégrade les performances de lecture (contraire à
    ENF-004) et complique les sauvegardes et la mise en cache.
- **Conséquences** : la convention de nommage doit, dès l'origine, éviter toute collision inter-vendeurs
  et toute déduction d'un autre produit par manipulation du nom de fichier (FR-042) — condition
  nécessaire pour que la bascule ultérieure vers un stockage objet ne nécessite pas de renommage ni de
  changement de code métier. Les photos doivent être couvertes par la stratégie de sauvegarde (FR-043).
- **Statut** : décision d'architecte (C-07), **ADR « Proposé »** ; le passage à un stockage objet reste
  **HYPOTHÈSE** à confirmer par le porteur selon la volumétrie réelle observée après lancement.

---

## R5 — Hébergement : VPS + Docker Compose vs PaaS managé

- **Décision** : Docker Compose (services : application, base de données, serveur web, worker de file)
  pour le local, la recette et la production ; un seul hôte Linux suffit au lancement ; la montée en
  charge se fait par réplique des services application et worker.
- **Raison** : aucune contrainte d'hébergement n'est imposée par le porteur (C-07) ; Docker Compose donne
  un environnement reproductible identique entre local/recette/production (FR-002, FR-003), sans
  dépendance à un fournisseur PaaS propriétaire, et à un coût maîtrisé pour un lancement de portée
  restreinte (zone Tanger).
- **Alternatives envisagées** :
  - *PaaS managé (type plateforme applicative Laravel, hébergement géré)* — non retenu par défaut :
    simplifie certaines opérations (bascule, mise à l'échelle automatique) mais introduit un coût
    récurrent et une dépendance fournisseur non justifiés tant que la volumétrie (ENF-006, Q21 MANQUANT)
    n'est pas connue ; reste une option de repli si l'exploitation (sauvegardes, supervision, ENF-005)
    s'avère trop coûteuse à opérer en interne.
  - *Hébergement multi-hôtes dès le lancement (orchestrateur de conteneurs type cluster)* — rejeté à ce
    stade : complexité disproportionnée (Constitution Principe II) pour un volume de lancement modeste ;
    réévaluable après mesure réelle de charge.
- **Conséquences** : les sauvegardes quotidiennes (base + fichiers), la sonde de disponibilité et la
  supervision (FR-005, FR-006, ENF-005) doivent être opérées par l'équipe elle-même (pas de délégation à
  un PaaS managé) ; ceci est tracé comme exigence d'exploitation, pas comme détail d'implémentation.
- **Statut** : décision d'architecte (C-07), **ADR « Proposé »** ; le nombre d'hôtes et les ressources
  exactes restent **HYPOTHÈSE H-11 / [NEEDS CLARIFICATION: Q21 — volumes à 12 mois non fournis par le
  porteur, ENF-006]**.

---

## R6 — Authentification et contrat API : conventions de socle

- **Décision** : authentification par jeton porteur (bearer token) émis après connexion
  téléphone + mot de passe, consommée par le frontend React via l'API REST versionnée `/api/v1` ;
  conventions détaillées dans `contracts/`.
- **Raison** : ENF-007 exige un cloisonnement par compte et par rôle ; un jeton par requête permet un
  contrôle d'autorisation centralisé (service de comptes et d'accès M01, FR-020) sans état de session
  partagé entre répliques de l'application (condition nécessaire à la montée en charge par réplique,
  point 6).
- **Alternatives envisagées** :
  - *Session serveur avec cookie* — non retenu par défaut : complique le partage d'état entre répliques
    de l'application sans magasin de session externe supplémentaire (complexité non justifiée à ce
    stade, Constitution Principe II) ; reste une option si un besoin de compatibilité navigateur
    spécifique apparaît.
- **Conséquences** : voir `contracts/authentification.md` pour le détail des conventions (pas des points
  d'accès métier, qui relèvent de T-003).
- **Statut** : décision d'architecte (C-07), **ADR « Proposé »**.

---

## Synthèse des points non tranchés (à confirmer par le porteur)

| Point | Référence | Statut |
|---|---|---|
| Volumétrie à 12 mois (nombre de vendeurs, produits, commandes) | ENF-006, Q21 | [NEEDS CLARIFICATION] — dimensionnement de lancement modeste retenu par défaut (FR-070) |
| Valeur cible précise de disponibilité et de performance (99 %, 3 s) | ENF-004/005 | HYPOTHÈSE H-11 — mécanisme de mesure prévu, valeur à confirmer avant lancement |
| Bascule vers stockage objet (S3) | ENF-010/011 | HYPOTHÈSE — dépend de la volumétrie réelle observée |
| Nombre d'hôtes et ressources exactes de production | H-11, Q21 | [NEEDS CLARIFICATION] — un seul hôte Linux retenu par défaut au lancement |

Aucune autre question ouverte du cahier (Q19, Q24, Q27, Q38, Q40, Q42–Q45) n'est tranchée ni approchée
par ce document : elles restent portées par le service de paramètres métier configurables (FR-021), hors
du socle d'infrastructure décrit ici.
