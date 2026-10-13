/speckit-constitution

Projet : marketplace-produits-locaux-maroc — marketplace B2C multi-vendeurs de produits locaux marocains, lancement à Tanger.

Rédige la constitution du projet en FRANÇAIS. Elle est la référence pour toutes les tâches d'ingénierie du plan `/opt/data/uml/marketplace-produits-locaux-maroc/plan/plan-marketplace-produits-locaux-maroc.md`.

Sources validées (ne rien inventer au-delà) :
- Cahier des charges v1.1 VALIDÉ : /opt/data/cahiers/marketplace-produits-locaux-maroc/cahier-des-charges-v1.1.md
- Décisions D1–D45 : /opt/data/cahiers/marketplace-produits-locaux-maroc/decisions.md
- UML approuvés (15 diagrammes) : /opt/data/uml/marketplace-produits-locaux-maroc/
- Plan de tâches : /opt/data/uml/marketplace-produits-locaux-maroc/plan/plan-marketplace-produits-locaux-maroc.md

Faits CONFIRMÉS à inscrire :
- C-07 : aucune contrainte technique imposée par le porteur. Stack retenue par l'architecte (décision technique, ADR « Proposé ») : Laravel 11 (PHP 8.3) + React 18 (Vite) + MySQL 8 + Docker Compose ; API REST interne.
- C-01 : paiement à la livraison uniquement en V1 (aucun paiement en ligne).
- C-02 : livraison et encaissement par une société de livraison partenaire ; seul l'administrateur saisit les statuts (D38) ; la société de livraison n'a aucun accès à la Plateforme.
- C-03 : zone clients Tanger, vendeurs Tanger + communes voisines (référentiel paramétrable).
- C-04 : V1 simple et extensible.
- ENF-002 : tous les parcours utilisables à 360 px de large (mobile-first).
- ENF-007 : accès par compte ; un vendeur n'accède qu'à ses données ; actions d'administration réservées aux administrateurs ; mots de passe jamais affichés.
- ENF-008 : toute opération financière et toute saisie de statut de livraison sont historisées (qui, quand, montant, motif) et consultables par l'administrateur.
- ENF-009 / C-08 : validation juridique obligatoire avant lancement ; aucun développement ne peut contourner cette porte.
- ENF-010 / §21 : évolutivité sans refonte (autres villes, paiement en ligne, accès société de livraison, commission).
- Deux actions de notification jamais confondues, aucun envoi externe en V1 sauf décision du porteur (Q23 MANQUANT).
- Aucune valeur métier inventée : les valeurs non tranchées (Q19, Q21, Q24, Q27, Q38, Q40–Q45) sont des paramètres configurables par l'administrateur sans redéploiement.

Principes attendus (adapte les noms, garde ce sens) :
1. Le métier d'abord : le cahier des charges validé (v1.1) est la source ; aucun comportement métier inventé, les questions ouvertes restent [NEEDS CLARIFICATION] ou paramètres.
2. Simplicité extensible : monolithe modulaire Laravel, découpage par modules M01–M11 du cahier ; pas de microservices, pas de complexité non justifiée par un besoin validé.
3. Une seule porte par état métier : les statuts de Commande/SousCommande, de MontantVendeur et de Retour sont modifiés uniquement par leur service dédié (voir plan §4) ; aucun autre module n'écrit ces champs.
4. Argent et traçabilité non négociables : toute opération financière est historisée et non modifiable ; aucune commission, aucun frais non paramétré.
5. Cloisonnement par rôle testé : chaque capacité de la matrice §5 du cahier a un test autorisé ET un test interdit.
6. Tests obligatoires : chaque tâche livrée avec ses tests automatisés (unitaires + fonctionnels) ; aucune fonctionnalité sans test de ses critères d'acceptation ; les montants sont vérifiés au dirham près.
7. Mobile-first et performance : toute interface est conçue d'abord à 360 px ; budget de performance ENF-004 (p95 < 3 s sur 4G simulée pour catalogue et fiche produit).
8. Aucun secret dans le dépôt : uniquement des variables d'environnement documentées (.env.example) ; jamais de mot de passe, clé ou jeton en clair.
9. Langue : code, schéma, API et commits en anglais ; documentation d'architecture, messages utilisateur et rapports en français.
10. Validation juridique avant lancement (C-08) : porte bloquante, non contournable par le développement.

Ajoute la section gouvernance : la constitution prime sur les préférences d'implémentation ; toute exception doit être écrite dans un ADR `docs/architecture/DECISIONS.md` au statut « Proposé » ; seul le porteur du projet (@user, Anass) valide ; aucun agent ne change un statut de tâche.

Écris le fichier .specify/memory/constitution.md (remplace le gabarit). N'invente aucune valeur chiffrée non citée ci-dessus.
