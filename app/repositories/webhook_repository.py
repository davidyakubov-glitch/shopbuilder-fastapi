def pending_webhooks_query(store_id: str) -> dict:
    return {"store_id": store_id, "query_shape": "pending_webhooks"}
