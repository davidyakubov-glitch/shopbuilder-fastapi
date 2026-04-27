from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WebhookInbound(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider_name": "kaspi_pay",
                "provider_event_id": "evt_123456",
                "event_type": "payment.succeeded",
                "occurred_at": "2026-04-24T10:33:00Z",
                "signature": "t=1713954780,v1=deadbeef",
                "payload": {"order_id": "ord_001", "status": "captured"},
            }
        }
    )

    provider_name: str
    provider_event_id: str
    event_type: str
    occurred_at: str
    signature: str
    payload: dict


class WebhookAccepted(BaseModel):
    event_id: str
    status: str


class WebhookEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    provider_name: str
    provider_event_id: str
    event_type: str
    status: str
    attempt_count: int
    backoff_seconds: int
    received_at: datetime
