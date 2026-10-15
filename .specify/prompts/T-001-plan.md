/speckit-plan Architecture du socle technique — marketplace-produits-locaux-maroc

Direction technique à retenir (décisions de l'architecte, C-07 : aucune contrainte imposée par le porteur ; à tracer en ADR « Proposé » dans docs/architecture/DECISIONS.md) :

1. Application : monolithe modulaire Laravel 11 sur PHP 8.3. Un seul déployable. Les modules M01–M11 du cahier §9 sont des namespaces/contextes du même déploiement, pas des services séparés.
2. Interface : React 18 + Vite, mobile-first 360 px, servie en statique ; API REST JSON versionnée (`/api/v1`) consommée par le front. Le contrat d'API détaillé est hors de cette tâche (T-003 du plan) : n'inventer aucun point d'accès métier ici, seulement les conventions de socle (format d'erreur, pagination, authentification, versionnage).
3. Base de données : MySQL 8 (utf8mb4), transactions pour toute opération d'argent ou de stock. Le schéma physique est hors de cette tâche (T-002).
4. Traitements différés : file d'attente + planificateur (Laravel queue/scheduler) ; les traitements périodiques sont idempotents, rejouables, et testables avec une horloge simulée (exigence des tâches T-005/T-034/T-050/T-053/T-054 du plan).
5. Photos produits : stockage sur volume monté, servi par l'application/le serveur web, variantes redimensionnées pour mobile, contrôle type/taille, convention de nommage ; option stockage objet compatible S3 documentée comme évolution sans changement de code métier (ENF-010, ENF-011).
6. Exécution : Docker Compose (app + base + serveur web + worker de file) pour le local, la recette et la production ; un seul hôte Linux suffit au lancement (volumes HYPOTHÈSE H-11 / Q21 MANQUANT), montée en charge par réplique de l'app et worker à file séparée.
7. Exploitation : sauvegardes quotidiennes de la base et des fichiers avec restauration documentée, sonde de disponibilité, journalisation applicative, supervision d'indisponibilité (ENF-005).
8. Sécurité : authentification par téléphone + mot de passe, autorisation par rôles et par propriété, cloisonnement par requêtes, mots de passe hachés jamais renvoyés, aucun secret dans le dépôt (.env.example uniquement), journaux sans données sensibles (ENF-007, ENF-008, §19).
9. Tests : PHPUnit/Pest pour le backend (unitaires + fonctionnels), Vitest + Playwright pour le frontend, un pipeline CI qui exécute lint + tests + build ; les critères d'acceptation du cahier §15 sont la base des tests fonctionnels.

Produis via .specify :
- specs/001-architecture-socle/plan.md (Technical Context rempli, structure du projet, arborescence cible du dépôt, frontières de modules, contrat de socle entre modules, phase de livraison alignée sur les vagues V1–V5 du plan §4)
- specs/001-architecture-socle/research.md (arbitrages : monolithe modulaire vs services, MySQL vs autres, file+scheduler vs cron dispersé, stockage local vs objet, hébergement VPS Docker vs PaaS — avec options, choix, conséquences, et ce qui est HYPOTHÈSE à confirmer par le porteur)
- specs/001-architecture-socle/data-model.md (vue de socle seulement : les entités métier relèvent de T-002 — ici uniquement les tables de socle : paramètres, journal d'audit, notifications, tâches planifiées, fichiers/photos, comptes)
- specs/001-architecture-socle/contracts/ (conventions de socle : format d'erreur JSON, pagination, authentification, versionnage, statuts — PAS les points d'accès métier de T-003)
- specs/001-architecture-socle/quickstart.md (mise en route de l'environnement local reproductible, commandes de test et de build, à destination de la tâche T-004)

Contraintes de rédaction :
- Français. Aucun secret, aucune valeur métier inventée, aucune valeur des questions ouvertes Q19/Q21/Q24/Q27/Q38/Q40–Q45.
- Ne pas écrire de migrations exécutables, de code de fonctionnalité ni de tâches d'implémentation.
- Toute hypothèse non validée est marquée HYPOTHÈSE ou [NEEDS CLARIFICATION].
- La constitution .specify/memory/constitution.md s'applique (monolithe modulaire, une seule porte par état métier, argent traçable, cloisonnement testé, aucun secret, validation juridique avant lancement).
