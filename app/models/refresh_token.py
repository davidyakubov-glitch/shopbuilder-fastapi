from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    user_id: str = Field(foreign_key="users.id", index=True)
    token_jti: str = Field(index=True, unique=True, max_length=128)
    token_hash: str = Field(index=True, unique=True, max_length=255)
    issued_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    expires_at: datetime = Field(index=True)
    last_used_at: Optional[datetime] = Field(default=None, index=True)
    revoked_at: Optional[datetime] = Field(default=None, index=True)
    revoked_reason: Optional[str] = Field(default=None, max_length=255)
    user_agent: Optional[str] = Field(default=None, max_length=255)
    ip_address: Optional[str] = Field(default=None, max_length=64)
