# Convention de socle — Format d'erreur JSON

**Portée** : convention transverse de structure de réponse d'erreur, appliquée par tous les points
d'accès `/api/v1/...`, quel que soit le module métier qui répond. Aucun point d'accès métier n'est
listé ici (T-003).

## Enveloppe d'erreur

Toute réponse d'erreur (code HTTP ≥ 400) renvoie un corps JSON de la forme :

```json
{
  "error": {
    "code": "chaine_stable_identifiant_le_type_d_erreur",
    "message": "Message explicite, destiné à l'affichage ou au journal (FR-040)",
    "details": {}
  }
}
```

- `code` : chaîne stable, indépendante de la langue, utilisée par le frontend pour une logique
  conditionnelle (ex. `validation_echouee`, `acces_refuse`, `ressource_introuvable`, `fichier_refuse`).
  Elle ne change pas si le texte de `message` est reformulé.
- `message` : texte explicite (FR-040 exige un message explicite de refus pour les fichiers non
  conformes ; ce principe s'étend à toute erreur fonctionnelle visible par l'utilisateur).
- `details` : objet optionnel, structuré, notamment pour les erreurs de validation (ex. liste des champs
  en erreur) ; absent si non pertinent. Ne doit jamais contenir de donnée personnelle sensible
  (mot de passe, coordonnée bancaire — ENF-008, FR-057) ni de trace technique interne (requête SQL,
  chemin de fichier serveur) en dehors de l'environnement local.

## Règles transverses

- Un mot de passe n'apparaît **jamais** dans `message` ni `details`, sous aucune forme, y compris haché
  (FR-054).
- En environnement de production, aucune trace de pile (stack trace) n'est renvoyée dans la réponse ;
  elle est uniquement consignée dans les journaux d'exploitation (FR-004), eux-mêmes exempts de donnée
  personnelle sensible en clair (FR-057).
- Les erreurs d'autorisation (cloisonnement par rôle, FR-051/FR-052) et les erreurs d'authentification
  utilisent des codes distincts (voir `authentification.md`) pour permettre au frontend de distinguer
  « non connecté » de « non autorisé ».

## Correspondance indicative avec les statuts HTTP

Voir `statuts-http.md` pour la table de correspondance entre catégories d'erreur fonctionnelle et code
HTTP ; ce document ne fixe que la forme du corps JSON.
