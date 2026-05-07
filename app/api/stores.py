from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.dependencies import current_user_id, db_session
from app.schemas.store import MerchantOnboardRequest, StoreListResponse, StoreRead
from app.services.store_service import list_user_stores, onboard_merchant

router = APIRouter(tags=["Stores"])


@router.get("/stores", response_model=StoreListResponse, summary="List merchants available to the current user")
def list_stores(
    user_id: str = Depends(current_user_id),
    session: Session = Depends(db_session),
) -> StoreListResponse:
    stores = list_user_stores(session, user_id)
    return StoreListResponse(items=[StoreRead.model_validate(store) for store in stores])


@router.post(
    "/stores/onboard",
    response_model=StoreRead,
    status_code=status.HTTP_201_CREATED,
    summary="Onboard a new merchant and assign a tenant database dynamically",
)
def create_store(
    payload: MerchantOnboardRequest,
    user_id: str = Depends(current_user_id),
    session: Session = Depends(db_session),
) -> StoreRead:
    store = onboard_merchant(session, user_id, payload)
    return StoreRead.model_validate(store)
