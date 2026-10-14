# Validation du contrat d'API (T-003)

Outils de documentation, pas des tests applicatifs. Ils ne démarrent ni Laravel ni MySQL.

## Régénérer le contrat

```bash
cd /opt/data/projects/marketplace-produits-locaux-maroc
uv run --no-project --with pyyaml python specs/003-contrat-api/tooling/build_contract.py
```

Écrit, depuis une seule table de définition :
`contracts/openapi.yaml`, `contracts/authorization-matrix.yaml`, `contracts/authorization-matrix.md`,
`contracts/api-reference.md`, `contracts/error-codes.md`. Ces fichiers portent l'en-tête « GÉNÉRÉ » :
on ne les modifie pas à la main.

## Vérifier

```bash
uv run --no-project --with pyyaml --with openapi-spec-validator --with jsonschema \
    python specs/003-contrat-api/validation/check_contract.py
```

| Contrôle | Ce qui est vérifié | Critère couvert |
|---|---|---|
| C1 | `openapi.yaml` est un OpenAPI 3.1 valide (openapi-spec-validator) | forme du contrat |
| C2 | UC-001..UC-023 ont chacun au moins un point d'accès (`x-uc`) | vérification T-003 n° 1, SC-001 |
| C3 | 17/17 lignes §5 (MP) et 5/5 capacités dérivées (MX) couvertes ; chaque rôle autorisé d'une ligne est servi | vérification T-003 n° 2, SC-002 |
| C4 | aucune opération n'ouvre un rôle refusé par ses lignes de matrice | SC-003, Constitution V |
| C5 | exemple de requête, de succès et d'erreur, avec code HTTP, pour chaque opération | exit Software Factory, SC-004 |
| C6 | chaque exemple est valide contre son schéma (JSON Schema 2020-12) | SC-004 |
| C7 | chaque code d'erreur est au catalogue, avec le bon statut HTTP | SC-005, ADR-016 |
| C8 | les énumérations `CHECK … IN (…)` du schéma T-002 sont identiques dans l'API | SC-006 |

Code de retour 0 si tout passe. Dernière sortie : `.specify/logs/T-003-validation.log`.

C8 exclut deux énumérations internes, avec leur raison affichée : `photo_files.check_status`
(un fichier refusé n'est jamais renvoyé ; il produit 422 `file_rejected`) et `photo_variants.variant`
(l'API expose des URL, pas les variantes).
