from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class OrderStatus(str, Enum):
    pending_payment = "pending_payment"
    paid = "paid"
    partially_fulfilled = "partially_fulfilled"
    fulfilled = "fulfilled"
    cancelled = "cancelled"
    refunded = "refunded"


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    store_id: str = Field(index=True, max_length=64)
    customer_id: Optional[str] = Field(default=None, index=True, max_length=64)
    order_number: str = Field(index=True, max_length=40)
    status: OrderStatus = Field(default=OrderStatus.pending_payment, index=True)
    currency_code: str = Field(default="KZT", max_length=3)
    subtotal_amount: int
    discount_amount: int = 0
    shipping_amount: int = 0
    total_amount: int = Field(index=True)
    placed_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    paid_at: Optional[datetime] = Field(default=None, index=True)


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    order_id: str = Field(index=True, max_length=64)
    variant_id: Optional[str] = Field(default=None, index=True, max_length=64)
    quantity: int
    snapshot_title: str = Field(max_length=255)
    snapshot_sku: Optional[str] = Field(default=None, max_length=80)
    snapshot_price_amount: int
    line_total_amount: int


class Fulfillment(SQLModel, table=True):
    __tablename__ = "fulfillments"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    order_id: str = Field(index=True, max_length=64)
    status: str = Field(index=True, max_length=40)
    carrier: Optional[str] = Field(default=None, max_length=80)
    tracking_number: Optional[str] = Field(default=None, index=True, max_length=120)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class Refund(SQLModel, table=True):
    __tablename__ = "refunds"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    order_id: str = Field(index=True, max_length=64)
    amount: int = Field(index=True)
    reason: Optional[str] = Field(default=None, max_length=255)
    created_by_user_id: str = Field(index=True, max_length=64)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
