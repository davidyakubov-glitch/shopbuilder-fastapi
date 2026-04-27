# CHANGELOG

## Architectural deviation from blueprint

- The original blueprint used row-based multi-tenancy with `store_id` filters.
- This milestone implementation switches ShopBuilder to **database-per-tenant** routing because the assignment explicitly requires true multi-tenancy for this sprint.
- A central platform database stores users, stores, memberships, refresh tokens, and audit logs.
- Merchant-specific business tables such as products, variants, inventory, themes, orders, and webhooks live in tenant databases selected dynamically by `tenant_key`.
- We still keep `store_id` on tenant tables as a defense-in-depth identifier even though each merchant is routed to a tenant database.
- Runtime Swagger documentation is generated from FastAPI route and schema definitions for this coding milestone, while `openapi.yaml` remains the original blueprint contract artifact from the planning phase.
