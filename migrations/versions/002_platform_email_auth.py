"""Add email verification and password reset tokens."""

import sqlalchemy as sa
from alembic import op

revision = "002_platform_email_auth"
down_revision = "001_platform_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(length=32), nullable=False, server_default="merchant"))
    op.add_column("users", sa.Column("is_email_verified", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_is_email_verified", "users", ["is_email_verified"])

    op.create_table(
        "email_tokens",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("purpose", sa.String(length=40), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_email_tokens_user_id", "email_tokens", ["user_id"])
    op.create_index("ix_email_tokens_purpose", "email_tokens", ["purpose"])
    op.create_index("ix_email_tokens_token_hash", "email_tokens", ["token_hash"], unique=True)
    op.create_index("ix_email_tokens_created_at", "email_tokens", ["created_at"])
    op.create_index("ix_email_tokens_expires_at", "email_tokens", ["expires_at"])
    op.create_index("ix_email_tokens_used_at", "email_tokens", ["used_at"])


def downgrade() -> None:
    op.drop_table("email_tokens")
    op.drop_index("ix_users_is_email_verified", table_name="users")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_column("users", "is_email_verified")
    op.drop_column("users", "role")
