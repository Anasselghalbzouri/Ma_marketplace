# Convention de socle — Versionnage de l'API

**Portée** : convention transverse applicable à tous les points d'accès métier qui seront définis en
T-003. Ce document ne liste aucun point d'accès métier.

## Règle

- Toute l'API REST exposée au frontend React est préfixée par une version explicite : `/api/v1/...`.
- Le numéro de version change uniquement en cas de rupture de compatibilité (suppression d'un champ,
  changement de type, changement de sémantique d'un champ existant). Un ajout de champ optionnel ou de
  point d'accès n'impose pas de nouvelle version.
- Tant qu'une seule version est exposée (V1 du produit), seule `/api/v1` existe ; l'introduction d'une
  `/api/v2` n'a lieu que si une rupture de compatibilité est requise par une évolution (ENF-010), et
  s'accompagne d'une période de dépréciation documentée de `/api/v1` avant son retrait (durée de
  dépréciation : **[NEEDS CLARIFICATION: aucune durée de dépréciation n'est fixée par le cahier ; à
  définir par l'architecte/porteur le jour où une v2 est nécessaire]**).
- Le frontend cible toujours une version explicite ; il n'existe pas d'alias `/api/latest`.

## Conséquences pour les modules

- Chaque module (M01–M11) expose ses points d'accès sous `/api/v1/<ressource>` ; l'attribution des
  chemins de ressources relève de T-003, pas de ce document.
- Un changement interne à un module (refactoring, changement de service propriétaire FR-012) ne doit
  jamais, à lui seul, justifier un changement de version si le contrat observable par le frontend ne
  change pas.
