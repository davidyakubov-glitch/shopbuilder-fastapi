from app.schemas.order import OrderCreate


def create_checkout_order(payload: OrderCreate, store_id: str) -> dict:
    return {
        "id": f"ord_{store_id[-6:]}",
        "store_id": store_id,
        "customer_email": payload.customer_email,
        "status": "pending_payment",
        "items": [item.model_dump() for item in payload.items],
    }
