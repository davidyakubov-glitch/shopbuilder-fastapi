from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Customer(SQLModel, table=True):
    __tablename__ = "customers"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    store_id: str = Field(index=True, max_length=64)
    email: str = Field(index=True, max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=80)
    last_name: Optional[str] = Field(default=None, max_length=80)
    phone: Optional[str] = Field(default=None, index=True, max_length=40)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
