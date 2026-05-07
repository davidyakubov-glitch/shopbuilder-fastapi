from fastapi import Depends, Header, HTTPException, Path, status
from sqlmodel import Session, select

from app.core.permissions import ensure_role
from app.core.security import decode_access_token
from app.database import get_platform_session, get_tenant_session
from app.models.membership import StoreMembership
from app.models.store import Store


def db_session(session: Session = Depends(get_platform_session)) -> Session:
    return session


def current_access_payload(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.replace("Bearer ", "", 1)
    return decode_access_token(token)


def current_user_id(payload: dict = Depends(current_access_payload)) -> str:
    subject = payload.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    return subject


def current_role(payload: dict = Depends(current_access_payload)) -> str:
    role = payload.get("role")
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token role")
    return role


def require_owner(role: str = Depends(current_role)) -> str:
    ensure_role(role, {"owner"})
    return role


def load_store_membership(
    store_id: str = Path(...),
    user_id: str = Depends(current_user_id),
    session: Session = Depends(db_session),
) -> StoreMembership:
    statement = select(StoreMembership).where(
        StoreMembership.store_id == store_id,
        StoreMembership.user_id == user_id,
        StoreMembership.is_active.is_(True),
    )
    membership = session.exec(statement).first()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Membership does not grant access to this store.",
        )
    return membership


def owner_membership(membership: StoreMembership = Depends(load_store_membership)) -> StoreMembership:
    ensure_role(membership.role.value, {"owner"})
    return membership


def tenant_session_for_store(
    store_id: str,
    session: Session,
):
    store = session.get(Store, store_id)
    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store was not found.")
    return get_tenant_session(store.tenant_key), store
