from datetime import UTC, datetime
from uuid import uuid4

from sqlmodel import Session, select

from app.core.errors import DomainError
from app.models.store import Store
from app.models.webhook import WebhookEvent, WebhookStatus


def accept_webhook(platform_session: Session, store_id: str, payload) -> dict:
    store = platform_session.get(Store, store_id)
    if store is None:
        raise DomainError("not_found", "Store was not found.", 404)

    from app.database import get_tenant_session

    with get_tenant_session(store.tenant_key) as tenant_session:
        existing_event = tenant_session.exec(
            select(WebhookEvent).where(
                WebhookEvent.store_id == store_id,
                WebhookEvent.provider_name == payload.provider_name,
                WebhookEvent.provider_event_id == payload.provider_event_id,
            )
        ).first()
        if existing_event is not None:
            raise DomainError("conflict", "Webhook event already exists.", 409)

        event = WebhookEvent(
            id=f"wh_{uuid4().hex}",
            store_id=store_id,
            provider_name=payload.provider_name,
            provider_event_id=payload.provider_event_id,
            event_type=payload.event_type,
            status=WebhookStatus.queued,
            payload_json=str(payload.payload),
            signature_header=payload.signature,
            attempt_count=0,
            backoff_seconds=60,
            received_at=datetime.now(UTC),
        )
        tenant_session.add(event)
        tenant_session.commit()
        return {"event_id": event.id, "status": event.status.value}


def list_webhook_events(platform_session: Session, store_id: str) -> list[WebhookEvent]:
    store = platform_session.get(Store, store_id)
    if store is None:
        raise DomainError("not_found", "Store was not found.", 404)

    from app.database import get_tenant_session

    with get_tenant_session(store.tenant_key) as tenant_session:
        statement = (
            select(WebhookEvent)
            .where(WebhookEvent.store_id == store_id)
            .order_by(WebhookEvent.received_at.desc())
        )
        return list(tenant_session.exec(statement).all())
