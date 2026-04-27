def list_products_query(store_id: str) -> dict:
    return {"store_id": store_id, "query_shape": "cursor_products"}
