from sqlmodel import Session, select

from app.database import platform_engine, tenant_engines
from app.models.product import Product
from app.models.store import Store
from app.services.product_service import build_variant_sku, generate_attribute_combinations


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
            "name": "Nomad Home",
            "subdomain": "nomad-home",
            "custom_domain": "shop.nomad-home.kz",
            "currency_code": "KZT",
            "timezone": "Asia/Almaty",
        },
    )
    return token, store_response.json()


def test_build_variant_sku_unit():
    sku = build_variant_sku("NH-HOODIE", ("Black", "M", "Cotton"))
    assert sku == "NH-HOODIE-BLACK-M-COTTON"


def test_generate_attribute_combinations_unit():
    class Axis:
        def __init__(self, values):
            self.values = values

    combinations = generate_attribute_combinations([Axis(["S", "M"]), Axis(["Black", "White"]), Axis(["Cotton"])])
    assert len(combinations) == 4


def test_variant_matrix_generation_and_cursor_pagination(client):
    token, store = register_and_store(client)

    matrix_response = client.post(
        f"/api/v1/stores/{store['id']}/products/variant-matrix",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Minimal Hoodie",
            "handle": "minimal-hoodie",
            "vendor": "Nomad Essentials",
            "base_sku": "NH-HOODIE",
            "price_amount": 18990,
            "attributes": [
                {"name": "Size", "values": ["S", "M"]},
                {"name": "Color", "values": ["Black", "White"]},
                {"name": "Material", "values": ["Cotton"]},
            ],
            "locations": [{"name": "Almaty Warehouse", "city": "Almaty", "default_quantity_per_variant": 10}],
        },
    )
    assert matrix_response.status_code == 201
    payload = matrix_response.json()
    assert payload["generated_variant_count"] == 4

    list_response = client.get(
        f"/api/v1/stores/{store['id']}/products?limit=1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    page = list_response.json()["page"]
    assert "has_more" in page


def test_variant_matrix_is_atomic_when_duplicate_skus_are_generated(client):
    token, store = register_and_store(client)

    response = client.post(
        f"/api/v1/stores/{store['id']}/products/variant-matrix",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Broken Hoodie",
            "handle": "broken-hoodie",
            "vendor": "Nomad Essentials",
            "base_sku": "NH-HOODIE",
            "price_amount": 18990,
            "attributes": [
                {"name": "Size", "values": ["M", "M"]},
                {"name": "Color", "values": ["Black"]},
                {"name": "Material", "values": ["Cotton"]},
            ],
            "locations": [{"name": "Almaty Warehouse", "city": "Almaty", "default_quantity_per_variant": 10}],
        },
    )
    assert response.status_code == 409

    with Session(platform_engine) as platform_session:
        store_row = platform_session.get(Store, store["id"])
        tenant_engine = tenant_engines[store_row.tenant_key]
        with Session(tenant_engine) as tenant_session:
            products = tenant_session.exec(select(Product).where(Product.handle == "broken-hoodie")).all()
            assert products == []
