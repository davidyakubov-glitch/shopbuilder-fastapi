def list_orders_query(store_id: str) -> dict:
    return {"store_id": store_id, "query_shape": "cursor_orders"}
