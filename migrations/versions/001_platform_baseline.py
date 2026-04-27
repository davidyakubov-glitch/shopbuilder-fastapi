"""Platform baseline migration artifact.

Creates core platform tables:
- users
- stores
- store_memberships
- refresh_tokens
- audit_logs

This file documents the baseline migration expected for Alembic.
"""

revision = "001_platform_baseline"
down_revision = None
branch_labels = ("platform",)
depends_on = None
