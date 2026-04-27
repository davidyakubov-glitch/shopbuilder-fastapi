from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlmodel import Session, select

from app.config import settings
from app.core.errors import DomainError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User


def _build_token_response(user_id: str, role: str, refresh_token: str) -> dict:
    return {
        "access_token": create_access_token(subject=user_id, role=role),
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_ttl_minutes * 60,
    }


def register_user(session: Session, email: str, password: str) -> dict:
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user is not None:
        raise DomainError("conflict", "A user with this email already exists.", 409)

    user = User(
        id=f"user_{uuid4().hex}",
        email=email,
        password_hash=hash_password(password),
    )
    raw_refresh_token, refresh_token_hash = create_refresh_token()
    refresh_token = RefreshToken(
        id=f"rt_{uuid4().hex}",
        user_id=user.id,
        token_jti=uuid4().hex,
        token_hash=refresh_token_hash,
        expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_ttl_days),
    )
    session.add(user)
    session.add(refresh_token)
    session.commit()
    return _build_token_response(user.id, "user", raw_refresh_token)


def login_user(session: Session, email: str, password: str) -> dict:
    user = session.exec(select(User).where(User.email == email, User.is_active.is_(True))).first()
    if user is None or not verify_password(password, user.password_hash):
        raise DomainError("unauthorized", "Invalid email or password.", 401)

    raw_refresh_token, refresh_token_hash = create_refresh_token()
    refresh_token = RefreshToken(
        id=f"rt_{uuid4().hex}",
        user_id=user.id,
        token_jti=uuid4().hex,
        token_hash=refresh_token_hash,
        expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_ttl_days),
    )
    session.add(refresh_token)
    session.commit()
    return _build_token_response(user.id, "user", raw_refresh_token)


def refresh_access_token(session: Session, refresh_token_value: str) -> dict:
    from app.core.security import hash_token

    token_hash = hash_token(refresh_token_value)
    refresh_token = session.exec(select(RefreshToken).where(RefreshToken.token_hash == token_hash)).first()

    if refresh_token is None:
        raise DomainError("unauthorized", "Refresh token is invalid.", 401)
    if refresh_token.revoked_at is not None:
        raise DomainError("unauthorized", "Refresh token has been revoked.", 401)
    if refresh_token.expires_at < datetime.now(UTC):
        raise DomainError("unauthorized", "Refresh token has expired.", 401)

    user = session.get(User, refresh_token.user_id)
    if user is None or not user.is_active:
        raise DomainError("unauthorized", "User account is inactive.", 401)

    refresh_token.last_used_at = datetime.now(UTC)
    session.add(refresh_token)
    session.commit()

    return _build_token_response(user.id, "user", refresh_token_value)


def logout_user(session: Session, refresh_token_value: str) -> None:
    from app.core.security import hash_token

    token_hash = hash_token(refresh_token_value)
    refresh_token = session.exec(select(RefreshToken).where(RefreshToken.token_hash == token_hash)).first()
    if refresh_token is None:
        raise DomainError("unauthorized", "Refresh token is invalid.", 401)
    if refresh_token.revoked_at is None:
        refresh_token.revoked_at = datetime.now(UTC)
        refresh_token.revoked_reason = "logout"
        session.add(refresh_token)
        session.commit()
