from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class ThemeStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class Theme(SQLModel, table=True):
    __tablename__ = "themes"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    store_id: str = Field(index=True, max_length=64)
    name: str = Field(max_length=120)
    status: ThemeStatus = Field(default=ThemeStatus.draft, index=True)
    version_number: int = 1
    checksum: str = Field(index=True, max_length=128)
    created_by_user_id: str = Field(index=True, max_length=64)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ThemeAsset(SQLModel, table=True):
    __tablename__ = "theme_assets"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    theme_id: str = Field(index=True, max_length=64)
    asset_key: str = Field(index=True, max_length=255)
    asset_type: str = Field(index=True, max_length=50)
    content_text: str
    checksum: str = Field(index=True, max_length=128)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
