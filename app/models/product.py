from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class ProductStatus(str, Enum):
    draft = "draft"
    active = "active"
    archived = "archived"


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    store_id: str = Field(index=True, max_length=64)
    title: str = Field(index=True, max_length=200)
    handle: str = Field(index=True, max_length=200)
    status: ProductStatus = Field(default=ProductStatus.draft, index=True)
    description_html: Optional[str] = None
    vendor: Optional[str] = Field(default=None, index=True, max_length=120)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class ProductOption(SQLModel, table=True):
    __tablename__ = "product_options"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    product_id: str = Field(index=True, max_length=64)
    position: int = Field(index=True)
    name: str = Field(max_length=80)


class ProductOptionValue(SQLModel, table=True):
    __tablename__ = "product_option_values"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    product_option_id: str = Field(index=True, max_length=64)
    value: str = Field(index=True, max_length=80)
    position: int = Field(index=True)
