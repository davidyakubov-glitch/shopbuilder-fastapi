# ShopBuilder FastAPI

Production-style backend milestone for the final project track `ShopBuilder`.

## What is implemented in this sprint

- Environment validation with Pydantic Settings
- Central PostgreSQL database for authentication and platform metadata
- Database-per-tenant routing for merchant business data
- Full auth baseline:
  - register
  - login
  - refresh token
  - logout
  - bcrypt password hashing
  - JWT access tokens
  - refresh token revocation
  - RBAC with `owner` and `staff`
  - Redis-backed rate limiting on auth endpoints
- ShopBuilder milestone business logic:
  - merchant onboarding
  - dynamic routing to at least 2 tenant databases
  - variant matrix generation from attributes such as Size x Color x Material
  - independent inventory counts per variant and per location
  - webhook event persistence schema and endpoints
- FastAPI Swagger docs at `/docs`
- Cursor-based pagination on product listing
- Tests and CI pipeline files

## Architecture summary

- `platform_database_url`: users, stores, memberships, refresh tokens, audit logs
- `tenant_database_urls`: merchant product, inventory, theme, order, and webhook tables
- Redis is used for rate limiting and can later be extended for background jobs

See [ARCHITECTURE.md](./ARCHITECTURE.md) and [CHANGELOG.md](./CHANGELOG.md) for details.

## Run with Docker

```bash
docker compose up --build
```

After startup:

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Local environment variables

Use `.env.example` as the source of truth.

Critical variables:

- `PLATFORM_DATABASE_URL`
- `TENANT_DATABASE_URLS`
- `REDIS_URL`
- `JWT_SECRET_KEY`
- `JWT_REFRESH_SECRET_KEY`
- `WEBHOOK_SIGNING_SECRET`

The app refuses to boot if required secrets are missing or invalid.

## Example auth flow

1. `POST /api/v1/auth/register`
2. `POST /api/v1/auth/login`
3. Use `Authorization: Bearer <access_token>` on protected endpoints
4. `POST /api/v1/auth/refresh`
5. `POST /api/v1/auth/logout`

## Main business endpoints

- `POST /api/v1/stores/onboard`
- `GET /api/v1/stores`
- `POST /api/v1/stores/{store_id}/products/variant-matrix`
- `GET /api/v1/stores/{store_id}/products`
- `POST /api/v1/stores/{store_id}/webhooks/inbound`
- `GET /api/v1/stores/{store_id}/webhooks/events`

## Tests

```bash
pytest
```

## Lint

```bash
ruff check .
```
