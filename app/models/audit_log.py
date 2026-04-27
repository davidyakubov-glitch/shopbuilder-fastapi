from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    store_id: Optional[str] = Field(default=None, foreign_key="stores.id", index=True)
    actor_user_id: Optional[str] = Field(default=None, foreign_key="users.id", index=True)
    action: str = Field(index=True, max_length=80)
    entity_type: str = Field(index=True, max_length=80)
    entity_id: str = Field(index=True, max_length=80)
    changes_json: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
