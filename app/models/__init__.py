from app.models.audit_log import AuditLog
from app.models.customer import Customer
from app.models.email_token import EmailToken, EmailTokenPurpose
from app.models.membership import MembershipRole, StoreMembership
from app.models.order import Fulfillment, Order, OrderItem, OrderStatus, Refund
from app.models.product import Product, ProductOption, ProductOptionValue, ProductStatus
from app.models.refresh_token import RefreshToken
from app.models.store import Store, StoreStatus
from app.models.theme import Theme, ThemeAsset, ThemeStatus
from app.models.user import User
from app.models.variant import InventoryLevel, InventoryLocation, ProductVariant, VariantOptionLink
from app.models.webhook import WebhookEvent, WebhookStatus

__all__ = [
    "AuditLog",
    "Customer",
    "EmailToken",
    "EmailTokenPurpose",
    "Fulfillment",
    "InventoryLevel",
    "InventoryLocation",
    "MembershipRole",
    "Order",
    "OrderItem",
    "OrderStatus",
    "Product",
    "ProductOption",
    "ProductOptionValue",
    "ProductStatus",
    "ProductVariant",
    "RefreshToken",
    "Refund",
    "Store",
    "StoreMembership",
    "StoreStatus",
    "Theme",
    "ThemeAsset",
    "ThemeStatus",
    "User",
    "VariantOptionLink",
    "WebhookEvent",
    "WebhookStatus",
    "platform_tables",
    "tenant_tables",
]


def platform_tables():
    return [
        User.__table__,
        EmailToken.__table__,
        Store.__table__,
        StoreMembership.__table__,
        RefreshToken.__table__,
        AuditLog.__table__,
    ]


def tenant_tables():
    return [
        Product.__table__,
        ProductOption.__table__,
        ProductOptionValue.__table__,
        ProductVariant.__table__,
        VariantOptionLink.__table__,
        InventoryLocation.__table__,
        InventoryLevel.__table__,
        Theme.__table__,
        ThemeAsset.__table__,
        WebhookEvent.__table__,
        Customer.__table__,
        Order.__table__,
        OrderItem.__table__,
        Fulfillment.__table__,
        Refund.__table__,
    ]
