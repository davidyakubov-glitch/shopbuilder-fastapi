from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.dependencies import db_session, load_store_membership, owner_membership
from app.schemas.product import ProductListResponse, ProductRead, ProductVariantMatrixRequest, VariantMatrixResponse
from app.services.product_service import create_variant_matrix, list_products


router = APIRouter(tags=["Products"])


@router.get(
    "/stores/{store_id}/products",
    response_model=ProductListResponse,
    summary="List products for a merchant using cursor pagination",
)
def get_products(
    store_id: str,
    cursor: str | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    _: object = Depends(load_store_membership),
    session: Session = Depends(db_session),
) -> ProductListResponse:
    data = list_products(session, store_id, cursor, limit)
    return ProductListResponse(
        items=[ProductRead.model_validate(item) for item in data["items"]],
        page=data["page"],
    )


@router.post(
    "/stores/{store_id}/products/variant-matrix",
    response_model=VariantMatrixResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate all SKU combinations from attribute axes with independent inventory counts",
)
def create_store_product_matrix(
    store_id: str,
    payload: ProductVariantMatrixRequest,
    _: object = Depends(owner_membership),
    session: Session = Depends(db_session),
) -> VariantMatrixResponse:
    data = create_variant_matrix(session, store_id, payload)
    return VariantMatrixResponse(**data)
