from app.schemas.order import OrderCreate
from app.services.email_service import order_confirmation_email
from app.workers.email_worker import enqueue_email


def create_checkout_order(payload: OrderCreate, store_id: str) -> dict:
    order_id = f"ord_{store_id[-6:]}"
    subject, html, text = order_confirmation_email(order_id, payload.customer_email)
    enqueue_email(payload.customer_email, subject, html, text)
    return {
        "id": order_id,
        "store_id": store_id,
        "customer_email": payload.customer_email,
        "status": "pending_payment",
        "items": [item.model_dump() for item in payload.items],
    }
