from datetime import UTC, datetime
from uuid import uuid4

from sqlmodel import Session, select

from app.config import settings
from app.core.errors import DomainError
from app.database import get_tenant_session
from app.models.membership import MembershipRole, StoreMembership
from app.models.store import Store, StoreStatus
from app.models.theme import Theme, ThemeStatus


def _choose_tenant_key(session: Session) -> str:
    tenant_keys = list(settings.parsed_tenant_database_urls.keys())
    stores = session.exec(select(Store)).all()
    usage_count = {tenant_key: 0 for tenant_key in tenant_keys}
    for store in stores:
        usage_count[store.tenant_key] = usage_count.get(store.tenant_key, 0) + 1
    return min(usage_count, key=usage_count.get)


def onboard_merchant(session: Session, user_id: str, payload) -> Store:
    existing_store = session.exec(select(Store).where(Store.subdomain == payload.subdomain)).first()
    if existing_store is not None:
        raise DomainError("conflict", "Subdomain is already reserved.", 409)

    tenant_key = _choose_tenant_key(session)
    now = datetime.now(UTC)

    store = Store(
        id=f"store_{uuid4().hex}",
        owner_user_id=user_id,
        name=payload.name,
        subdomain=payload.subdomain,
        custom_domain=payload.custom_domain,
        status=StoreStatus.draft,
        currency_code=payload.currency_code,
        timezone=payload.timezone,
        tenant_key=tenant_key,
        created_at=now,
        updated_at=now,
    )
    membership = StoreMembership(
        id=f"membership_{uuid4().hex}",
        store_id=store.id,
        user_id=user_id,
        role=MembershipRole.owner,
        permissions_json='["catalog","inventory","orders","themes","settings"]',
        created_at=now,
    )

    with get_tenant_session(tenant_key) as tenant_session:
        default_theme = Theme(
            id=f"theme_{uuid4().hex}",
            store_id=store.id,
            name="Default Theme",
            status=ThemeStatus.draft,
            version_number=1,
            checksum=f"sha256:{uuid4().hex}",
            created_by_user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        tenant_session.add(default_theme)
        tenant_session.commit()
        store.active_theme_id = default_theme.id

    session.add(store)
    session.add(membership)
    session.commit()
    session.refresh(store)
    return store


def list_user_stores(session: Session, user_id: str) -> list[Store]:
    statement = (
        select(Store)
        .join(StoreMembership, StoreMembership.store_id == Store.id)
        .where(StoreMembership.user_id == user_id, StoreMembership.is_active.is_(True))
        .order_by(Store.created_at.desc())
    )
    return list(session.exec(statement).all())
