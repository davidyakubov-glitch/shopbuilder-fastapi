from sqlmodel import Session, select

from app.database import platform_engine
from app.models.membership import MembershipRole, StoreMembership
from app.models.user import User


def register_and_login(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "StrongPass!2026"},
    )
    assert register_response.status_code == 201
    return register_response.json()


def create_store(client, access_token: str):
    response = client.post(
        "/api/v1/stores/onboard",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "Nomad Home",
            "subdomain": "nomad-home",
            "custom_domain": "shop.nomad-home.kz",
            "currency_code": "KZT",
            "timezone": "Asia/Almaty",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_full_auth_flow_register_login_refresh_logout(client):
    register_payload = register_and_login(client)

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "StrongPass!2026"},
    )
    assert login_response.status_code == 200
    login_payload = login_response.json()
    assert login_payload["access_token"]
    assert login_payload["refresh_token"]

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_payload["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    refreshed_payload = refresh_response.json()
    assert refreshed_payload["access_token"]
    assert refreshed_payload["refresh_token"] == login_payload["refresh_token"]

    logout_response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": login_payload["refresh_token"]},
    )
    assert logout_response.status_code == 200

    revoked_refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_payload["refresh_token"]},
    )
    assert revoked_refresh_response.status_code == 401

    assert register_payload["access_token"]


def test_email_verification_and_password_reset(client, monkeypatch):
    sent_messages = []

    def capture_email(to_email, subject, html, text=None):
        sent_messages.append({"to": to_email, "subject": subject, "text": text or html})

    monkeypatch.setattr("app.services.auth_service.enqueue_email", capture_email)

    register_and_login(client)
    verification_token = sent_messages[-1]["text"].split("token=", 1)[1]

    verify_response = client.post("/api/v1/auth/email/verify", json={"token": verification_token})
    assert verify_response.status_code == 200

    with Session(platform_engine) as session:
        user = session.exec(select(User).where(User.email == "owner@example.com")).first()
        assert user.is_email_verified is True

    forgot_response = client.post("/api/v1/auth/password/forgot", json={"email": "owner@example.com"})
    assert forgot_response.status_code == 200
    reset_token = sent_messages[-1]["text"].split("token=", 1)[1]

    reset_response = client.post(
        "/api/v1/auth/password/reset",
        json={"token": reset_token, "new_password": "NewStrongPass!2026"},
    )
    assert reset_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "NewStrongPass!2026"},
    )
    assert login_response.status_code == 200


def test_protected_endpoint_rejects_missing_and_invalid_token(client):
    missing_token_response = client.get("/api/v1/stores")
    assert missing_token_response.status_code == 401

    invalid_token_response = client.get(
        "/api/v1/stores",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert invalid_token_response.status_code == 401


def test_wrong_role_receives_403_for_owner_only_endpoint(client):
    auth_payload = register_and_login(client)
    store_payload = create_store(client, auth_payload["access_token"])

    with Session(platform_engine) as session:
        statement = select(StoreMembership).where(StoreMembership.store_id == store_payload["id"])
        membership = session.exec(statement).first()
        membership.role = MembershipRole.staff
        session.add(membership)
        session.commit()

    response = client.post(
        f"/api/v1/stores/{store_payload['id']}/products/variant-matrix",
        headers={"Authorization": f"Bearer {auth_payload['access_token']}"},
        json={
            "title": "Minimal Hoodie",
            "handle": "minimal-hoodie",
            "vendor": "Nomad Essentials",
            "base_sku": "NH-HOODIE",
            "price_amount": 18990,
            "attributes": [
                {"name": "Size", "values": ["S", "M"]},
                {"name": "Color", "values": ["Black"]},
                {"name": "Material", "values": ["Cotton"]},
            ],
            "locations": [{"name": "Almaty Warehouse", "city": "Almaty", "default_quantity_per_variant": 10}],
        },
    )
    assert response.status_code == 403
