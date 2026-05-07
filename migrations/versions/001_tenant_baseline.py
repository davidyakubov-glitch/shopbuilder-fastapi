"""Create tenant baseline schema."""

import sqlalchemy as sa
from alembic import op

revision = "001_tenant_baseline"
down_revision = None
branch_labels = ("tenant",)
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("store_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("handle", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("description_html", sa.Text(), nullable=True),
        sa.Column("vendor", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_products_store_id", "products", ["store_id"])
    op.create_index("ix_products_title", "products", ["title"])
    op.create_index("ix_products_handle", "products", ["handle"])
    op.create_index("ix_products_status", "products", ["status"])
    op.create_index("ix_products_vendor", "products", ["vendor"])
    op.create_index("ix_products_created_at", "products", ["created_at"])
    op.create_index("ix_products_updated_at", "products", ["updated_at"])

    op.create_table(
        "product_options",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("product_id", sa.String(length=64), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
    )
    op.create_index("ix_product_options_product_id", "product_options", ["product_id"])
    op.create_index("ix_product_options_position", "product_options", ["position"])

    op.create_table(
        "product_option_values",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("product_option_id", sa.String(length=64), nullable=False),
        sa.Column("value", sa.String(length=80), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
    )
    op.create_index("ix_product_option_values_product_option_id", "product_option_values", ["product_option_id"])
    op.create_index("ix_product_option_values_value", "product_option_values", ["value"])
    op.create_index("ix_product_option_values_position", "product_option_values", ["position"])

    op.create_table(
        "product_variants",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("store_id", sa.String(length=64), nullable=False),
        sa.Column("product_id", sa.String(length=64), nullable=False),
        sa.Column("sku", sa.String(length=80), nullable=False),
        sa.Column("barcode", sa.String(length=120), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("price_amount", sa.Integer(), nullable=False),
        sa.Column("compare_at_amount", sa.Integer(), nullable=True),
        sa.Column("weight_grams", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_product_variants_store_id", "product_variants", ["store_id"])
    op.create_index("ix_product_variants_product_id", "product_variants", ["product_id"])
    op.create_index("ix_product_variants_sku", "product_variants", ["sku"])
    op.create_index("ix_product_variants_barcode", "product_variants", ["barcode"])
    op.create_index("ix_product_variants_price_amount", "product_variants", ["price_amount"])
    op.create_index("ix_product_variants_is_active", "product_variants", ["is_active"])
    op.create_index("ix_product_variants_created_at", "product_variants", ["created_at"])

    op.create_table(
        "variant_option_links",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("variant_id", sa.String(length=64), nullable=False),
        sa.Column("option_value_id", sa.String(length=64), nullable=False),
        sa.Column("option_position", sa.Integer(), nullable=False),
    )
    op.create_index("ix_variant_option_links_variant_id", "variant_option_links", ["variant_id"])
    op.create_index("ix_variant_option_links_option_value_id", "variant_option_links", ["option_value_id"])
    op.create_index("ix_variant_option_links_option_position", "variant_option_links", ["option_position"])

    op.create_table(
        "inventory_locations",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("store_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_inventory_locations_store_id", "inventory_locations", ["store_id"])
    op.create_index("ix_inventory_locations_is_active", "inventory_locations", ["is_active"])

    op.create_table(
        "inventory_levels",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("store_id", sa.String(length=64), nullable=False),
        sa.Column("location_id", sa.String(length=64), nullable=False),
        sa.Column("variant_id", sa.String(length=64), nullable=False),
        sa.Column("available_qty", sa.Integer(), nullable=False),
        sa.Column("reserved_qty", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_inventory_levels_store_id", "inventory_levels", ["store_id"])
    op.create_index("ix_inventory_levels_location_id", "inventory_levels", ["location_id"])
    op.create_index("ix_inventory_levels_variant_id", "inventory_levels", ["variant_id"])
    op.create_index("ix_inventory_levels_updated_at", "inventory_levels", ["updated_at"])

    op.create_table(
        "themes",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("store_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(length=128), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_themes_store_id", "themes", ["store_id"])
    op.create_index("ix_themes_status", "themes", ["status"])
    op.create_index("ix_themes_checksum", "themes", ["checksum"])
    op.create_index("ix_themes_created_by_user_id", "themes", ["created_by_user_id"])
    op.create_index("ix_themes_created_at", "themes", ["created_at"])

    op.create_table(
        "theme_assets",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("theme_id", sa.String(length=64), nullable=False),
        sa.Column("asset_key", sa.String(length=255), nullable=False),
        sa.Column("asset_type", sa.String(length=50), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("checksum", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_theme_assets_theme_id", "theme_assets", ["theme_id"])
    op.create_index("ix_theme_assets_asset_key", "theme_assets", ["asset_key"])
    op.create_index("ix_theme_assets_asset_type", "theme_assets", ["asset_type"])
    op.create_index("ix_theme_assets_checksum", "theme_assets", ["checksum"])
    op.create_index("ix_theme_assets_created_at", "theme_assets", ["created_at"])

    op.create_table(
        "webhook_events",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("store_id", sa.String(length=64), nullable=False),
        sa.Column("provider_name", sa.String(length=50), nullable=False),
        sa.Column("provider_event_id", sa.String(length=120), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("signature_header", sa.String(length=255), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("next_attempt_at", sa.DateTime(), nullable=True),
        sa.Column("backoff_seconds", sa.Integer(), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("received_at", sa.DateTime(), nullable=False),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_webhook_events_store_id", "webhook_events", ["store_id"])
    op.create_index("ix_webhook_events_provider_name", "webhook_events", ["provider_name"])
    op.create_index("ix_webhook_events_provider_event_id", "webhook_events", ["provider_event_id"])
    op.create_index("ix_webhook_events_event_type", "webhook_events", ["event_type"])
    op.create_index("ix_webhook_events_status", "webhook_events", ["status"])
    op.create_index("ix_webhook_events_attempt_count", "webhook_events", ["attempt_count"])
    op.create_index("ix_webhook_events_next_attempt_at", "webhook_events", ["next_attempt_at"])
    op.create_index("ix_webhook_events_received_at", "webhook_events", ["received_at"])
    op.create_index("ix_webhook_events_processed_at", "webhook_events", ["processed_at"])

    op.create_table(
        "customers",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("store_id", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=80), nullable=True),
        sa.Column("last_name", sa.String(length=80), nullable=True),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_customers_store_id", "customers", ["store_id"])
    op.create_index("ix_customers_email", "customers", ["email"])
    op.create_index("ix_customers_phone", "customers", ["phone"])
    op.create_index("ix_customers_created_at", "customers", ["created_at"])

    op.create_table(
        "orders",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("store_id", sa.String(length=64), nullable=False),
        sa.Column("customer_id", sa.String(length=64), nullable=True),
        sa.Column("order_number", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False),
        sa.Column("subtotal_amount", sa.Integer(), nullable=False),
        sa.Column("discount_amount", sa.Integer(), nullable=False),
        sa.Column("shipping_amount", sa.Integer(), nullable=False),
        sa.Column("total_amount", sa.Integer(), nullable=False),
        sa.Column("placed_at", sa.DateTime(), nullable=False),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_orders_store_id", "orders", ["store_id"])
    op.create_index("ix_orders_customer_id", "orders", ["customer_id"])
    op.create_index("ix_orders_order_number", "orders", ["order_number"])
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_total_amount", "orders", ["total_amount"])
    op.create_index("ix_orders_placed_at", "orders", ["placed_at"])
    op.create_index("ix_orders_paid_at", "orders", ["paid_at"])

    op.create_table(
        "order_items",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("order_id", sa.String(length=64), nullable=False),
        sa.Column("variant_id", sa.String(length=64), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("snapshot_title", sa.String(length=255), nullable=False),
        sa.Column("snapshot_sku", sa.String(length=80), nullable=True),
        sa.Column("snapshot_price_amount", sa.Integer(), nullable=False),
        sa.Column("line_total_amount", sa.Integer(), nullable=False),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])
    op.create_index("ix_order_items_variant_id", "order_items", ["variant_id"])

    op.create_table(
        "fulfillments",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("order_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("carrier", sa.String(length=80), nullable=True),
        sa.Column("tracking_number", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_fulfillments_order_id", "fulfillments", ["order_id"])
    op.create_index("ix_fulfillments_status", "fulfillments", ["status"])
    op.create_index("ix_fulfillments_tracking_number", "fulfillments", ["tracking_number"])
    op.create_index("ix_fulfillments_created_at", "fulfillments", ["created_at"])

    op.create_table(
        "refunds",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("order_id", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("created_by_user_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_refunds_order_id", "refunds", ["order_id"])
    op.create_index("ix_refunds_amount", "refunds", ["amount"])
    op.create_index("ix_refunds_created_by_user_id", "refunds", ["created_by_user_id"])
    op.create_index("ix_refunds_created_at", "refunds", ["created_at"])


def downgrade() -> None:
    op.drop_table("refunds")
    op.drop_table("fulfillments")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("customers")
    op.drop_table("webhook_events")
    op.drop_table("theme_assets")
    op.drop_table("themes")
    op.drop_table("inventory_levels")
    op.drop_table("inventory_locations")
    op.drop_table("variant_option_links")
    op.drop_table("product_variants")
    op.drop_table("product_option_values")
    op.drop_table("product_options")
    op.drop_table("products")
