"""Tenant baseline migration artifact.

Creates tenant business tables:
- products
- product_options
- product_option_values
- product_variants
- variant_option_links
- inventory_locations
- inventory_levels
- themes
- theme_assets
- webhook_events
- customers
- orders
- order_items
- fulfillments
- refunds

This file documents the baseline migration expected for Alembic.
"""

revision = "001_tenant_baseline"
down_revision = None
branch_labels = ("tenant",)
depends_on = None
