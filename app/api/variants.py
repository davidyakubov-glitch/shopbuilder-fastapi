from fastapi import APIRouter, Depends

from app.dependencies import load_store_membership

router = APIRouter(tags=["Variants"])


@router.get("/stores/{store_id}/variants")
def list_variants(store_id: str, _: object = Depends(load_store_membership)) -> dict:
    return {"items": [], "store_id": store_id}
