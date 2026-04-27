# ShopBuilder Architecture Decisions

## Multi-tenancy

- Strategy: database-per-tenant for merchant business data.
- Central platform database stores authentication and platform metadata.
- Tenant routing uses `store.tenant_key` and a configured map of tenant DSNs.
- Two mock tenants are supported immediately: `merchant_alpha` and `merchant_beta`.

## Connection pooling

- Max pool size per engine: `10`
- Max overflow per engine: `20`
- Pool timeout: `30s`
- Rationale: tenant engines are cached and reused to avoid creating a new engine per request.
- This avoids exhausting PostgreSQL connections during morning traffic bursts because each tenant database has a bounded pool rather than unbounded ad hoc connections.

## Authentication

- Access tokens: JWT, short-lived
- Refresh tokens: database-backed, reusable, revocable, hashed before persistence
- Password hashing: bcrypt
- RBAC: store membership roles `owner` and `staff`

## Rate limiting

- Redis-backed request counters on `/auth/register` and `/auth/login`
- Limit: 5 attempts per minute per IP

## Webhook reliability

- Webhook events are persisted before later processing
- Schema includes `event_type`, `attempt_count`, `next_attempt_at`, and `backoff_seconds`
- Backoff state is stored explicitly for retry workers

## Migrations

- Baseline migration artifacts are included under `migrations/versions`
- Runtime table creation is also called on startup so `docker compose up` remains frictionless for this milestone environment
