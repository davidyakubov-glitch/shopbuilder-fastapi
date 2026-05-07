import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlmodel import Session, select

from app.config import settings
from app.core.errors import DomainError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.email_token import EmailToken, EmailTokenPurpose
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.services.email_service import password_reset_email, verification_email
from app.workers.email_worker import enqueue_email


def _build_token_response(user_id: str, role: str, refresh_token: str) -> dict:
    return {
        "access_token": create_access_token(subject=user_id, role=role),
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_ttl_minutes * 60,
    }


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _new_raw_email_token() -> str:
    return secrets.token_urlsafe(48)


def _create_email_token(session: Session, user_id: str, purpose: EmailTokenPurpose, ttl_minutes: int) -> str:
    raw_token = _new_raw_email_token()
    email_token = EmailToken(
        id=f"et_{uuid4().hex}",
        user_id=user_id,
        purpose=purpose,
        token_hash=hash_token(raw_token),
        expires_at=datetime.now(UTC) + timedelta(minutes=ttl_minutes),
    )
    session.add(email_token)
    return raw_token


def _consume_email_token(session: Session, raw_token: str, purpose: EmailTokenPurpose) -> User:
    token_hash = hash_token(raw_token)
    email_token = session.exec(
        select(EmailToken).where(EmailToken.token_hash == token_hash, EmailToken.purpose == purpose)
    ).first()

    if email_token is None:
        raise DomainError("unauthorized", "Token is invalid.", 401)
    if email_token.used_at is not None:
        raise DomainError("unauthorized", "Token has already been used.", 401)
    if _as_aware_utc(email_token.expires_at) < datetime.now(UTC):
        raise DomainError("unauthorized", "Token has expired.", 401)

    user = session.get(User, email_token.user_id)
    if user is None or not user.is_active:
        raise DomainError("unauthorized", "User account is inactive.", 401)

    email_token.used_at = datetime.now(UTC)
    session.add(email_token)
    return user


def _queue_verification_email(session: Session, user: User) -> None:
    raw_token = _create_email_token(
        session,
        user.id,
        EmailTokenPurpose.email_verification,
        settings.email_token_ttl_minutes,
    )
    subject, html, text = verification_email(user.email, raw_token)
    enqueue_email(user.email, subject, html, text)


def register_user(session: Session, email: str, password: str) -> dict:
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user is not None:
        raise DomainError("conflict", "A user with this email already exists.", 409)

    user = User(
        id=f"user_{uuid4().hex}",
        email=email,
        password_hash=hash_password(password),
        role="merchant",
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
    _queue_verification_email(session, user)
    session.commit()
    return _build_token_response(user.id, user.role, raw_refresh_token)


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
    return _build_token_response(user.id, user.role, raw_refresh_token)


def refresh_access_token(session: Session, refresh_token_value: str) -> dict:
    token_hash = hash_token(refresh_token_value)
    refresh_token = session.exec(select(RefreshToken).where(RefreshToken.token_hash == token_hash)).first()

    if refresh_token is None:
        raise DomainError("unauthorized", "Refresh token is invalid.", 401)
    if refresh_token.revoked_at is not None:
        raise DomainError("unauthorized", "Refresh token has been revoked.", 401)
    if _as_aware_utc(refresh_token.expires_at) < datetime.now(UTC):
        raise DomainError("unauthorized", "Refresh token has expired.", 401)

    user = session.get(User, refresh_token.user_id)
    if user is None or not user.is_active:
        raise DomainError("unauthorized", "User account is inactive.", 401)

    refresh_token.last_used_at = datetime.now(UTC)
    session.add(refresh_token)
    session.commit()

    return _build_token_response(user.id, user.role, refresh_token_value)


def logout_user(session: Session, refresh_token_value: str) -> None:
    token_hash = hash_token(refresh_token_value)
    refresh_token = session.exec(select(RefreshToken).where(RefreshToken.token_hash == token_hash)).first()
    if refresh_token is None:
        raise DomainError("unauthorized", "Refresh token is invalid.", 401)
    if refresh_token.revoked_at is None:
        refresh_token.revoked_at = datetime.now(UTC)
        refresh_token.revoked_reason = "logout"
        session.add(refresh_token)
        session.commit()


def verify_email(session: Session, token: str) -> None:
    user = _consume_email_token(session, token, EmailTokenPurpose.email_verification)
    user.is_email_verified = True
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()


def resend_verification_email(session: Session, email: str) -> None:
    user = session.exec(select(User).where(User.email == email, User.is_active.is_(True))).first()
    if user is None:
        return
    if user.is_email_verified:
        return
    _queue_verification_email(session, user)
    session.commit()


def request_password_reset(session: Session, email: str) -> None:
    user = session.exec(select(User).where(User.email == email, User.is_active.is_(True))).first()
    if user is None:
        return
    raw_token = _create_email_token(
        session,
        user.id,
        EmailTokenPurpose.password_reset,
        settings.password_reset_token_ttl_minutes,
    )
    subject, html, text = password_reset_email(user.email, raw_token)
    enqueue_email(user.email, subject, html, text)
    session.commit()


def reset_password(session: Session, token: str, new_password: str) -> None:
    user = _consume_email_token(session, token, EmailTokenPurpose.password_reset)
    user.password_hash = hash_password(new_password)
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
