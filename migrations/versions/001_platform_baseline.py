"""Create platform baseline schema."""

import sqlalchemy as sa
from alembic import op

revision = "001_platform_baseline"
down_revision = None
branch_labels = ("platform",)
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_is_active", "users", ["is_active"])
    op.create_index("ix_users_created_at", "users", ["created_at"])

    op.create_table(
        "stores",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("subdomain", sa.String(length=80), nullable=False),
        sa.Column("custom_domain", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("tenant_key", sa.String(length=64), nullable=False),
        sa.Column("active_theme_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_stores_owner_user_id", "stores", ["owner_user_id"])
    op.create_index("ix_stores_name", "stores", ["name"])
    op.create_index("ix_stores_subdomain", "stores", ["subdomain"], unique=True)
    op.create_index("ix_stores_custom_domain", "stores", ["custom_domain"], unique=True)
    op.create_index("ix_stores_status", "stores", ["status"])
    op.create_index("ix_stores_tenant_key", "stores", ["tenant_key"])
    op.create_index("ix_stores_created_at", "stores", ["created_at"])

    op.create_table(
        "store_memberships",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("store_id", sa.String(length=64), sa.ForeignKey("stores.id"), nullable=False),
        sa.Column("user_id", sa.String(length=64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("permissions_json", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_store_memberships_store_id", "store_memberships", ["store_id"])
    op.create_index("ix_store_memberships_user_id", "store_memberships", ["user_id"])
    op.create_index("ix_store_memberships_role", "store_memberships", ["role"])
    op.create_index("ix_store_memberships_is_active", "store_memberships", ["is_active"])
    op.create_index("ix_store_memberships_created_at", "store_memberships", ["created_at"])

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_jti", sa.String(length=128), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("issued_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_reason", sa.String(length=255), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_token_jti", "refresh_tokens", ["token_jti"], unique=True)
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)
    op.create_index("ix_refresh_tokens_issued_at", "refresh_tokens", ["issued_at"])
    op.create_index("ix_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"])
    op.create_index("ix_refresh_tokens_last_used_at", "refresh_tokens", ["last_used_at"])
    op.create_index("ix_refresh_tokens_revoked_at", "refresh_tokens", ["revoked_at"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("store_id", sa.String(length=64), sa.ForeignKey("stores.id"), nullable=True),
        sa.Column("actor_user_id", sa.String(length=64), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.String(length=80), nullable=False),
        sa.Column("changes_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_audit_logs_store_id", "audit_logs", ["store_id"])
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"])
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("refresh_tokens")
    op.drop_table("store_memberships")
    op.drop_table("stores")
    op.drop_table("users")
