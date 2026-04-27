from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.dependencies import db_session, load_store_membership, owner_membership
from app.schemas.webhook import WebhookAccepted, WebhookEventRead, WebhookInbound
from app.services.webhook_service import accept_webhook, list_webhook_events


router = APIRouter(tags=["Webhooks"])


@router.get("/stores/{store_id}/webhooks/events", response_model=list[WebhookEventRead], summary="List webhook events for a merchant")
def get_webhook_events(
    store_id: str,
    _: object = Depends(load_store_membership),
    session: Session = Depends(db_session),
) -> list[WebhookEventRead]:
    events = list_webhook_events(session, store_id)
    return [WebhookEventRead.model_validate(event) for event in events]


@router.post(
    "/stores/{store_id}/webhooks/inbound",
    response_model=WebhookAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Persist an inbound webhook event for retryable asynchronous processing",
)
def receive_webhook(
    store_id: str,
    payload: WebhookInbound,
    _: object = Depends(owner_membership),
    session: Session = Depends(db_session),
) -> WebhookAccepted:
    return WebhookAccepted(**accept_webhook(session, store_id, payload))
