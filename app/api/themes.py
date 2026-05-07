from fastapi import APIRouter, Depends

from app.dependencies import load_store_membership, owner_membership
from app.services.theme_service import list_themes, publish_theme

router = APIRouter(tags=["Themes"])


@router.get("/stores/{store_id}/themes")
def get_themes(store_id: str, _: object = Depends(load_store_membership)) -> dict:
    return {"items": list_themes(store_id)}


@router.post("/stores/{store_id}/themes/{theme_id}/publish")
def activate_theme(store_id: str, theme_id: str, _: object = Depends(owner_membership)) -> dict:
    return publish_theme(store_id, theme_id)
