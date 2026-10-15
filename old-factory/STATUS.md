# STATUS — marketplace-produits-locaux-maroc

Dernière mise à jour : 2026-10-13 — Maestro

## Étape courante
**Étape 3 — Design (en cours)**. Aucun développement démarré.

| Étape | État | Preuve |
|---|---|---|
| 1. Besoin | ✅ | CDC v1.1 §3 (problem statement), acteurs identifiés |
| 2. Spécification | ✅ CDC validé (D45, 2026-10-12) — ⚠️ backlog Ledger absent | 15 stories US-001..015, 52 scénarios Given/When/Then dans le CDC |
| 3a. UML (blueprint) | ✅ approuvé par Anass 2026-10-12 | 15 diagrammes |
| 3b. Plan (compass) | ✋ Proposition, non validé | 70 tâches T-001..T-070 |
| 3c. Architecture (keystone) | 🟡 T-001 done | 9 ADR dans docs/architecture/DECISIONS.md (pas encore dans docs/adr/) |
| 3d. Contrats d'API | ❌ T-003 non démarrée | Seuls contrats transverses (auth, pagination, erreurs, versionnage) |
| 4. Dev | — | dépôt : 1 commit docs |
| 5. QA | — | |
| 6-7. CI/CD, prod | ⏸ pause | |
| 8. Amélioration | — | |

## Bot actif
Aucun en cours. Dernier : keystone (T-001, terminé).

## Critère exit de l'étape 3
Chaque endpoint a un exemple requête/réponse + ADR dans docs/adr/ + plan Compass validé par Anass. **Non atteint.**

## Emplacements (hors arborescence factory)
- Cahier des charges : /opt/data/cahiers/marketplace-produits-locaux-maroc/ (v1.1 validée + decisions.md D1–D45)
- UML : /opt/data/uml/marketplace-produits-locaux-maroc/
- Plan Compass : /opt/data/uml/marketplace-produits-locaux-maroc/plan/plan-marketplace-produits-locaux-maroc.md
- Dépôt Git (04-dev) : /opt/data/projects/marketplace-produits-locaux-maroc/
- Remote GitHub : https://github.com/Anasselghalbzouri/Ma_marketplace (public, vide au 2026-10-13)
- Kanban : board `marketplace-maroc` (1 done, 3 ready, 66 todo ; aucune tâche backlog/ledger)

## Blocages
1. Keystone attend Anass : stack/découpage M01–M11 ; emplacement projet ; volumes 12 mois + conservation.
2. Questions métier ouvertes : Q23 (T-010), M-06 (T-015), Q24 (T-040), Q44 (T-046), Q11 (T-013).
3. UML : transitions manquantes STATE-001 (annulation admin) et STATE-003 (délai vérif.) → blueprint.
4. Kanban : T-002, T-004, T-070 « ready » sans assignee → non dispatchées.
5. T-004 inclut la CI → étape 6 en pause, à retirer du périmètre.
6. Backlog Ledger absent (aucune tâche Kanban correspondante).

## Compteur de boucles
| Problème | Retours |
|---|---|
| — | 0 |
