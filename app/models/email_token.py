from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class EmailTokenPurpose(str, Enum):
    email_verification = "email_verification"
    password_reset = "password_reset"


class EmailToken(SQLModel, table=True):
    __tablename__ = "email_tokens"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    user_id: str = Field(index=True, foreign_key="users.id", max_length=64)
    purpose: EmailTokenPurpose = Field(index=True, max_length=40)
    token_hash: str = Field(index=True, unique=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    expires_at: datetime = Field(index=True)
    used_at: Optional[datetime] = Field(default=None, index=True)
