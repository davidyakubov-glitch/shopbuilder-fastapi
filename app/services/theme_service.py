def list_themes(store_id: str) -> list[dict]:
    return [
        {
            "id": f"theme_{store_id[-6:]}_001",
            "name": "Dawn Custom",
            "status": "draft",
            "version_number": 1,
        }
    ]


def publish_theme(store_id: str, theme_id: str) -> dict:
    return {"id": theme_id, "store_id": store_id, "status": "published"}
