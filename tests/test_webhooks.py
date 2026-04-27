def register_and_store(client):
    auth_response = client.post(
        "/api/v1/auth/register",
        json={"email": "merchant@example.com", "password": "StrongPass!2026"},
    )
    token = auth_response.json()["access_token"]
    store_response = client.post(
        "/api/v1/stores/onboard",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Webhook Store",
            "subdomain": "webhook-store",
            "custom_domain": "shop.webhook-store.kz",
            "currency_code": "KZT",
            "timezone": "Asia/Almaty",
        },
    )
    return token, store_response.json()


def test_webhook_event_persistence(client):
    token, store = register_and_store(client)

    response = client.post(
        f"/api/v1/stores/{store['id']}/webhooks/inbound",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "provider_name": "kaspi_pay",
            "provider_event_id": "evt_123456",
            "event_type": "payment.succeeded",
            "occurred_at": "2026-04-24T10:33:00Z",
            "signature": "t=1713954780,v1=deadbeef",
            "payload": {"order_id": "ord_001", "status": "captured"},
        },
    )
    assert response.status_code == 202

    list_response = client.get(
        f"/api/v1/stores/{store['id']}/webhooks/events",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
