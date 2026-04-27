from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class MembershipRole(str, Enum):
    owner = "owner"
    staff = "staff"


class StoreMembership(SQLModel, table=True):
    __tablename__ = "store_memberships"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    store_id: str = Field(foreign_key="stores.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    role: MembershipRole = Field(default=MembershipRole.staff, index=True)
    permissions_json: str = Field(default="[]")
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
