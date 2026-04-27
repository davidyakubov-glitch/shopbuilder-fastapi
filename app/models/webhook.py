from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class WebhookStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    processed = "processed"
    failed = "failed"
    dead_letter = "dead_letter"


class WebhookEvent(SQLModel, table=True):
    __tablename__ = "webhook_events"

    id: Optional[str] = Field(default=None, primary_key=True, max_length=64)
    store_id: str = Field(index=True, max_length=64)
    provider_name: str = Field(index=True, max_length=50)
    provider_event_id: str = Field(index=True, max_length=120)
    event_type: str = Field(index=True, max_length=80)
    status: WebhookStatus = Field(default=WebhookStatus.queued, index=True)
    payload_json: str
    signature_header: Optional[str] = Field(default=None, max_length=255)
    attempt_count: int = Field(default=0, index=True)
    next_attempt_at: Optional[datetime] = Field(default=None, index=True)
    backoff_seconds: int = Field(default=60)
    last_error: Optional[str] = None
    received_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    processed_at: Optional[datetime] = Field(default=None, index=True)
