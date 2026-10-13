# Convention de socle — Statuts HTTP

**Portée** : table de correspondance transverse entre catégories de résultat fonctionnel et code de
statut HTTP, applicable à tout point d'accès `/api/v1/...`. Ne fixe aucun point d'accès métier (T-003).

| Catégorie fonctionnelle | Code HTTP | Remarque |
|---|---|---|
| Succès avec contenu | 200 | Lecture ou action réussie renvoyant une ressource/liste. |
| Création réussie | 201 | Réservé aux créations de ressource. |
| Succès sans contenu | 204 | Ex. suppression réussie, action sans donnée de retour utile. |
| Requête mal formée | 400 | Entrée techniquement invalide (JSON mal formé, paramètre absent requis). |
| Non authentifié | 401 | Jeton absent, invalide ou expiré — distinct de 403 (voir `authentification.md`). |
| Accès refusé (rôle ou propriété) | 403 | Authentifié mais non autorisé pour cette ressource/action (FR-051, FR-052). |
| Ressource introuvable | 404 | — |
| Conflit d'état | 409 | Ex. tentative de transition d'état non valide depuis l'état courant (Constitution Principe III). |
| Échec de validation métier | 422 | Ex. fichier photo refusé (FR-040), champ de formulaire invalide. |
| Trop de requêtes | 429 | Protection anti-abus ; seuils non fixés par ce document. |
| Erreur interne | 500 | Ne renvoie jamais de détail d'implémentation (voir `format-erreur.md`). |

## Règle de cohérence

Le corps JSON d'une réponse en erreur (tout code ≥ 400) suit systématiquement l'enveloppe décrite dans
`format-erreur.md`. Le choix entre 403 et 404 pour masquer ou non l'existence d'une ressource à un
titulaire non autorisé est une décision à documenter au cas par cas en T-003, pas une règle générale de
ce socle.
