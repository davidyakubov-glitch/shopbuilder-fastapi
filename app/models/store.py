from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class StoreStatus(str, Enum):
    draft = "draft"
    active = "active"
    suspended = "suspended"
    archived = "archived"


class Store(SQLModel, table=True):
    __tablename__ = "stores"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    owner_user_id: str = Field(foreign_key="users.id", index=True)
    name: str = Field(index=True, max_length=120)
    subdomain: str = Field(index=True, unique=True, max_length=80)
    custom_domain: Optional[str] = Field(default=None, index=True, unique=True, max_length=255)
    status: StoreStatus = Field(default=StoreStatus.draft, index=True)
    currency_code: str = Field(default="KZT", max_length=3)
    timezone: str = Field(default="Asia/Almaty", max_length=64)
    tenant_key: str = Field(index=True, max_length=64)
    active_theme_id: Optional[str] = Field(default=None, max_length=64)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
