# Backend — Marketplace Produits Locaux Maroc

Application backend construite avec Laravel 11 (PHP ≥ 8.3).

## Prérequis

- PHP 8.3+ avec les extensions : mbstring, openssl, pdo, pdo_mysql, xml, zip, bcmath.
- Composer 2.
- (Optionnel) Docker Compose pour l'environnement complet (MySQL + Redis + Nginx).

## Démarrage rapide (hors Docker)

```bash
cd backend
cp .env.example .env
composer install
php artisan key:generate
php artisan migrate
php artisan serve
```

L'API est accessible sur `http://localhost:8000/api/v1` (les routes métier seront ajoutées par les tâches Compass suivantes).

## Tests

```bash
php artisan test
```

La suite utilise une base SQLite in-memory en environnement `testing` (voir `phpunit.xml`).

## Démarrage avec Docker Compose

```bash
docker compose up -d
```

Services : `app` (PHP-FPM), `web` (Nginx sur le port 8080), `db` (MySQL 8.0), `redis`, `worker`.

## Structure

- `app/` : code métier Laravel.
- `database/migrations/` : migrations de base.
- `routes/` : définitions des routes.
- `tests/` : tests PHPUnit/Pest.

## Notes T-004

- Le Docker daemon n'est pas disponible sur la machine de développement actuelle ; l'environnement Docker est livré mais non validé en exécution.
- Les tests backend passent en SQLite in-memory.
