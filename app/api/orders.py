from fastapi import APIRouter, Depends

from app.dependencies import load_store_membership
from app.schemas.order import OrderCreate
from app.services.checkout_service import create_checkout_order
from app.services.order_service import list_orders


router = APIRouter(tags=["Orders"])


@router.get("/stores/{store_id}/orders")
def get_orders(store_id: str, _: object = Depends(load_store_membership)) -> dict:
    return {"items": list_orders(store_id)}


@router.post("/stores/{store_id}/orders")
def create_order(store_id: str, payload: OrderCreate, _: object = Depends(load_store_membership)) -> dict:
    return create_checkout_order(payload, store_id)
