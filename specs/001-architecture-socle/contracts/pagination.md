# Convention de socle — Pagination

**Portée** : convention transverse appliquée par tout point d'accès `/api/v1/...` qui renvoie une liste
(catalogue, résultats de recherche, listes administratives, etc. — T-003 fixera quels points d'accès
sont concernés). Aucun point d'accès métier n'est listé ici.

## Paramètres de requête

- `page` : numéro de page, entier ≥ 1, valeur par défaut 1.
- `par_page` : nombre d'éléments par page, entier positif, borné par une valeur maximale paramétrable
  (voir `Parametre` dans `data-model.md`) pour éviter qu'une requête ne charge un volume disproportionné
  sur un écran mobile (ENF-002/ENF-004) ; la valeur par défaut et la borne maximale exactes ne sont pas
  fixées par ce document (paramètre configurable, FR-021).

## Enveloppe de réponse

```json
{
  "data": [],
  "meta": {
    "page": 1,
    "par_page": 20,
    "total": 0,
    "total_pages": 0
  }
}
```

- `data` : tableau des éléments de la page courante, structure propre à chaque ressource métier (définie
  en T-003).
- `meta` : métadonnées de pagination, identiques en forme pour toute ressource paginée du socle.

## Règles transverses

- Une page au-delà de `total_pages` renvoie une liste `data` vide avec un code de succès (pas une erreur),
  pour simplifier la navigation côté frontend.
- Le format de pagination est identique pour toutes les ressources paginées, qu'il s'agisse du catalogue
  (M03), des listes administratives (M09) ou de tout autre module : aucune variante par module n'est
  introduite sans ADR documentant la raison (Constitution — Gouvernance).
