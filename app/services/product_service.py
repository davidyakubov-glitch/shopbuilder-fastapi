from datetime import UTC, datetime
from itertools import product as cartesian_product
from uuid import uuid4

from sqlmodel import Session, select

from app.core.errors import DomainError
from app.models.product import Product, ProductOption, ProductOptionValue, ProductStatus
from app.models.store import Store
from app.models.variant import InventoryLevel, InventoryLocation, ProductVariant, VariantOptionLink
from app.services.pagination_service import decode_cursor, encode_cursor


def _slugify_fragment(value: str) -> str:
    return "".join(character.upper() if character.isalnum() else "-" for character in value).replace("--", "-")


def generate_attribute_combinations(attributes: list) -> list[tuple[str, ...]]:
    option_values_list = [axis.values for axis in attributes]
    return list(cartesian_product(*option_values_list))


def build_variant_sku(base_sku: str, combination: tuple[str, ...]) -> str:
    option_fragments = [_slugify_fragment(value) for value in combination]
    return f"{base_sku}-{'-'.join(option_fragments)}"


def create_variant_matrix(platform_session: Session, store_id: str, payload) -> dict:
    store = platform_session.get(Store, store_id)
    if store is None:
        raise DomainError("not_found", "Store was not found.", 404)

    from app.database import get_tenant_session

    option_names = [axis.name for axis in payload.attributes]
    combinations = generate_attribute_combinations(payload.attributes)
    now = datetime.now(UTC)

    with get_tenant_session(store.tenant_key) as tenant_session:
        existing_product = tenant_session.exec(select(Product).where(Product.handle == payload.handle)).first()
        if existing_product is not None:
            raise DomainError("conflict", "Product handle already exists for this merchant.", 409)

        try:
            product_row = Product(
                id=f"prod_{uuid4().hex}",
                store_id=store_id,
                title=payload.title,
                handle=payload.handle,
                status=ProductStatus.active,
                description_html=payload.description_html,
                vendor=payload.vendor,
                created_at=now,
                updated_at=now,
            )
            tenant_session.add(product_row)
            tenant_session.flush()

            option_value_map: dict[tuple[str, str], str] = {}
            for position, axis in enumerate(payload.attributes, start=1):
                option_row = ProductOption(
                    id=f"opt_{uuid4().hex}",
                    product_id=product_row.id,
                    position=position,
                    name=axis.name,
                )
                tenant_session.add(option_row)
                tenant_session.flush()

                for value_position, value in enumerate(axis.values, start=1):
                    option_value = ProductOptionValue(
                        id=f"optval_{uuid4().hex}",
                        product_option_id=option_row.id,
                        value=value,
                        position=value_position,
                    )
                    tenant_session.add(option_value)
                    option_value_map[(axis.name, value)] = option_value.id

            location_rows: list[InventoryLocation] = []
            for location in payload.locations:
                location_row = InventoryLocation(
                    id=f"loc_{uuid4().hex}",
                    store_id=store_id,
                    name=location.name,
                    city=location.city,
                    is_active=True,
                )
                tenant_session.add(location_row)
                location_rows.append(location_row)

            generated_variants = []
            seen_skus: set[str] = set()
            for combination in combinations:
                sku = build_variant_sku(payload.base_sku, combination)
                title = " / ".join(combination)

                if sku in seen_skus:
                    raise DomainError("conflict", "Duplicate SKU generated from attribute inputs.", 409)
                seen_skus.add(sku)

                variant_row = ProductVariant(
                    id=f"var_{uuid4().hex}",
                    store_id=store_id,
                    product_id=product_row.id,
                    sku=sku,
                    title=title,
                    price_amount=payload.price_amount,
                    is_active=True,
                    created_at=now,
                    updated_at=now,
                )
                tenant_session.add(variant_row)
                tenant_session.flush()

                variant_inventory = []
                for position, value in enumerate(combination, start=1):
                    tenant_session.add(
                        VariantOptionLink(
                            id=f"vol_{uuid4().hex}",
                            variant_id=variant_row.id,
                            option_value_id=option_value_map[(option_names[position - 1], value)],
                            option_position=position,
                        )
                    )

                for location_row, location_input in zip(location_rows, payload.locations, strict=True):
                    inventory_level = InventoryLevel(
                        id=f"inv_{uuid4().hex}",
                        store_id=store_id,
                        location_id=location_row.id,
                        variant_id=variant_row.id,
                        available_qty=location_input.default_quantity_per_variant,
                        reserved_qty=0,
                        updated_at=now,
                    )
                    tenant_session.add(inventory_level)
                    variant_inventory.append(
                        {
                            "location_name": location_row.name,
                            "available_qty": location_input.default_quantity_per_variant,
                        }
                    )

                generated_variants.append(
                    {
                        "sku": sku,
                        "title": title,
                        "price_amount": payload.price_amount,
                        "inventory": variant_inventory,
                    }
                )

            tenant_session.commit()
        except Exception:
            tenant_session.rollback()
            raise

    return {
        "product_id": product_row.id,
        "generated_variant_count": len(generated_variants),
        "variants": generated_variants,
    }


def list_products(platform_session: Session, store_id: str, cursor: str | None, limit: int) -> dict:
    store = platform_session.get(Store, store_id)
    if store is None:
        raise DomainError("not_found", "Store was not found.", 404)

    from app.database import get_tenant_session

    with get_tenant_session(store.tenant_key) as tenant_session:
        statement = (
            select(Product)
            .where(Product.store_id == store_id)
            .order_by(Product.created_at.desc(), Product.id.desc())
        )
        rows = list(tenant_session.exec(statement).all())

    cursor_payload = decode_cursor(cursor)
    if cursor_payload is not None:
        cursor_created_at, cursor_id = cursor_payload
        rows = [
            row
            for row in rows
            if (row.created_at < cursor_created_at) or (row.created_at == cursor_created_at and row.id < cursor_id)
        ]

    selected_rows = rows[:limit]
    next_cursor = None
    if len(rows) > limit and selected_rows:
        next_cursor = encode_cursor(selected_rows[-1].created_at, selected_rows[-1].id)

    return {
        "items": selected_rows,
        "page": {"next_cursor": next_cursor, "has_more": len(rows) > limit},
    }
