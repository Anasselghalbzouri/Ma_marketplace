/speckit-specify Architecture du socle technique de la marketplace de produits locaux marocains (dossier d'architecture T-001)

Cadre : tâche T-001 du plan `/opt/data/uml/marketplace-produits-locaux-maroc/plan/plan-marketplace-produits-locaux-maroc.md`. Portée : le socle TRANSVERSE sur lequel s'appuient les 70 tâches du plan — pas les fonctionnalités métier elles-mêmes.

Entrées à citer (ne pas recopier le cahier, y renvoyer) :
- Cahier des charges v1.1 VALIDÉ : /opt/data/cahiers/marketplace-produits-locaux-maroc/cahier-des-charges-v1.1.md — §5 (acteurs + matrice des permissions), §6 (périmètre), §9 (modules M01–M11), §13 (ENF-001..012), §16 (MVP), §17 (hors périmètre), §18 (contraintes C-01..C-08), §19 (sécurité et données), §22 (questions ouvertes)
- Décisions : /opt/data/cahiers/marketplace-produits-locaux-maroc/decisions.md (D1–D45)
- UML approuvés : /opt/data/uml/marketplace-produits-locaux-maroc/ (CLASS-01/02, SEQ-001..003, STATE-001..004, ACTIVITY-001..003)
- Plan : plan-marketplace-produits-locaux-maroc.md — §3 (tâches), §4 (vagues, ordre d'exécution, coordination sur fichiers partagés), §2 (constats M-01..M-09, H-08, H-11)
- Constitution : .specify/memory/constitution.md

Exigences à couvrir explicitement (chacune doit avoir une réponse dans la spécification) :
- ENF-002 : mobile-first 360 px pour les trois profils (client, vendeur, administrateur).
- ENF-004 : catalogue et fiche produit affichés en moins de 3 s sur 4G pour 95 % des consultations — décrire ce que le socle doit fournir pour l'atteindre (rendu, cache, poids des images) sans inventer de valeur validée.
- ENF-005 : disponibilité 99 % hors maintenance annoncée — décrire exigences de déploiement, sauvegarde, supervision ; les valeurs sont HYPOTHÈSE (H-11) à confirmer.
- ENF-006 : volumes (vendeurs, produits, commandes à 12 mois) = MANQUANT (Q21) → la spécification doit prévoir un dimensionnement révisable et marquer [NEEDS CLARIFICATION].
- ENF-007 : cloisonnement par rôle — un vendeur ne voit que ses données ; l'administrateur seul saisit les statuts de livraison ; la société de livraison n'a aucun accès ; les mots de passe ne sont jamais affichés.
- ENF-010 : évolutivité sans refonte (nouvelles villes clients, nouvelles communes vendeurs, paiement en ligne, commission/abonnement, accès société de livraison, livraison internationale).
- C-07 : aucune contrainte technique imposée par le porteur → toute décision technique est un ADR « Proposé » (docs/architecture/DECISIONS.md), révisable.

Éléments que la spécification doit décrire (WHAT/WHY, pas de code) :
1. Socle d'exécution : conteneur applicatif unique (monolithe modulaire) et ses responsabilités ; environnement local reproductible ; environnements recette et production ; exploitation (journaux, sauvegardes, supervision d'indisponibilité).
2. Découpage en modules M01–M11 (noms du cahier §9) : responsabilités, données possédées, frontières, dépendances autorisées entre modules, et rattachement des tâches du plan §3/§4 à chaque module.
3. Services transverses : comptes et accès, paramètres métier configurables (aucune valeur métier inventée), journal d'audit (ENF-008), notifications internes, planificateur de tâches temporelles.
4. Stratégie des tâches planifiées : quels traitements doivent s'exécuter en temps différé (expiration du délai de réponse vendeur, fin du délai de retour → montants disponibles, alerte de délai légal de remboursement, calcul hebdomadaire des reversements), idempotence, horloge simulable en test (les tâches T-005/T-034/T-050/T-053/T-054 du plan exigent des tests à horloge simulée).
5. Stratégie de stockage et de service des photos produits : téléversement, contrôle de type et de taille, redimensionnement pour mobile, nommage, sauvegarde, service des fichiers ; ENF-011.
6. Sécurité et données : authentification par téléphone, rôles Client/Vendeur/Administrateur, cloisonnement par propriété, protection des coordonnées bancaires et des données personnelles (loi 09-08), aucun secret dans le dépôt, journalisation sans données sensibles, conservation des données [NEEDS CLARIFICATION].
7. Cibles et critères de recette du socle transverses aux fonctionnalités.

Règles de rédaction :
- La spécification décrit QUOI et POURQUOI, jamais le code, jamais les migrations, jamais les tâches d'implémentation.
- Chaque exigence porte un identifiant (FR-…/NFR-…) et cite sa source (ENF-…, C-…, D…, section du cahier).
- Les valeurs non validées restent [NEEDS CLARIFICATION: …] ; les hypothèses restent marquées HYPOTHÈSE avec leur impact (H-08, H-11).
- Aucune contradiction avec le cahier des charges validé : en cas de doute, le cahier prime.
- Tout en français, avec la terminologie du cahier (commande, sous-commande, retour, montant vendeur, reversement).

Crée le dossier de spécification `specs/001-architecture-socle/spec.md` via le script .specify.
