/speckit-checklist architecture-socle

Génère deux checklists de qualité dans specs/001-architecture-socle/checklists/ (en français) :

1. `architecture.md` — revue d'architecture du socle : chaque ENF citée par la tâche T-001 (ENF-002, ENF-004, ENF-005, ENF-006, ENF-007, ENF-010) a-t-elle une réponse explicite et vérifiable ? Les 11 modules M01–M11 sont-ils tous définis avec responsabilités et frontières ? La stratégie des tâches planifiées est-elle idempotente et testable à horloge simulée ? La stratégie de stockage des photos couvre-t-elle contrôle, redimensionnement, sauvegarde, évolution ? L'hébergement est-il décrit (local, recette, production, sauvegardes, supervision) ? Chaque décision technique non imposée par le porteur est-elle tracée en ADR « Proposé » (C-07) ? Les hypothèses H-08 et H-11 sont-elles marquées avec leur impact ?

2. `securite.md` — revue sécurité et données : cloisonnement par rôle et par propriété (ENF-007), matrice §5 du cahier couverte, coordonnées bancaires et données personnelles protégées (§19, loi 09-08), aucun secret dans le dépôt, mots de passe jamais affichés, journal d'audit non modifiable (ENF-008), aucune donnée sensible dans les journaux, porte juridique C-08 non contournable.

Chaque item est une case à cocher vérifiable sur les fichiers produits (`specs/001-architecture-socle/spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `docs/architecture/`). Aucun code à produire.
