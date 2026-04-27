def list_orders(store_id: str) -> list[dict]:
    return [
        {
            "id": f"ord_{store_id[-6:]}_001",
            "order_number": "SB-2026-0001",
            "status": "pending_payment",
            "total_amount": 40480,
        }
    ]
