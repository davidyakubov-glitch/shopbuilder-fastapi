from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ProductVariant(SQLModel, table=True):
    __tablename__ = "product_variants"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    store_id: str = Field(index=True, max_length=64)
    product_id: str = Field(index=True, max_length=64)
    sku: str = Field(index=True, max_length=80)
    barcode: Optional[str] = Field(default=None, index=True, max_length=120)
    title: str = Field(max_length=200)
    price_amount: int = Field(index=True)
    compare_at_amount: Optional[int] = None
    weight_grams: Optional[int] = None
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class VariantOptionLink(SQLModel, table=True):
    __tablename__ = "variant_option_links"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    variant_id: str = Field(index=True, max_length=64)
    option_value_id: str = Field(index=True, max_length=64)
    option_position: int = Field(index=True)


class InventoryLocation(SQLModel, table=True):
    __tablename__ = "inventory_locations"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    store_id: str = Field(index=True, max_length=64)
    name: str = Field(max_length=120)
    city: Optional[str] = Field(default=None, max_length=120)
    is_active: bool = Field(default=True, index=True)


class InventoryLevel(SQLModel, table=True):
    __tablename__ = "inventory_levels"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    store_id: str = Field(index=True, max_length=64)
    location_id: str = Field(index=True, max_length=64)
    variant_id: str = Field(index=True, max_length=64)
    available_qty: int = 0
    reserved_qty: int = 0
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
