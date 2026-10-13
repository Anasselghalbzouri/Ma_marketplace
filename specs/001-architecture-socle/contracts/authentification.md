# Convention de socle — Authentification et autorisation

**Portée** : convention transverse d'authentification/autorisation pour l'API `/api/v1`, consommée par
tous les modules métier. Ne décrit pas les points d'accès métier eux-mêmes (T-003) ni le détail du
module M01 (Comptes et accès, relève de T-002/T-014 à T-019).

## Authentification

- L'identifiant de connexion est le numéro de téléphone (FR-050, ENF-007) ; le mot de passe est vérifié
  contre sa forme hachée.
- Après connexion réussie, un jeton porteur (bearer token) est émis et doit être transmis par le
  frontend dans l'en-tête `Authorization: Bearer <jeton>` à chaque requête authentifiée.
- Le jeton a une durée de validité paramétrable (voir `Parametre`, `data-model.md`) ; sa valeur exacte
  n'est pas fixée ici.
- Une connexion échouée (téléphone inconnu ou mot de passe incorrect) renvoie une erreur générique
  (`identifiants_invalides`) sans préciser laquelle des deux informations est fautive, afin de ne pas
  faciliter l'énumération de comptes.
- Le mot de passe (en clair ou haché) **n'apparaît jamais** dans une réponse API, un journal
  d'exploitation ou le journal d'audit, pour aucun rôle, y compris l'administrateur (FR-054,
  Constitution Principe VIII).

## Autorisation

- Chaque requête authentifiée porte un rôle unique parmi Client, Vendeur, Administrateur (FR-050,
  cahier §5).
- L'autorisation est vérifiée à deux niveaux, systématiquement :
  1. **Par rôle** : certaines actions sont réservées à un rôle (ex. saisie de statuts de livraison
     réservée à l'Administrateur, FR-052).
  2. **Par propriété** : un Vendeur n'accède qu'aux ressources dont il est propriétaire (sa boutique, ses
     produits, ses sous-commandes, ses montants, ses retours — FR-051) ; cette vérification se fait sur
     chaque requête, jamais seulement à l'affichage du menu ou du frontend.
- Une tentative d'accès à une ressource d'un autre titulaire du même rôle (ex. Vendeur A sur une
  ressource de Vendeur B) renvoie une erreur d'autorisation (`acces_refuse`), jamais une erreur
  « ressource introuvable » qui masquerait la distinction (à moins qu'une exigence de confidentialité
  explicite impose de ne pas révéler l'existence de la ressource — à trancher au niveau de chaque
  contrat métro en T-003, pas ici).
- La société de livraison, acteur externe, ne dispose d'aucun compte ni jeton : aucun point d'accès ne
  lui est exposé (FR-053, D38).

## Conséquence pour le cloisonnement testé (Constitution Principe V)

Pour chaque ligne de la matrice des permissions du cahier §5, un test d'accès autorisé et un test
d'accès interdit doivent pouvoir s'appuyer sur ces deux mécanismes (rôle, propriété) sans logique
d'autorisation ad hoc par point d'accès (FR-058, SC-007).
