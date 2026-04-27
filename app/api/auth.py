from fastapi import APIRouter, Depends, Request, status
from sqlmodel import Session

from app.core.rate_limit import rate_limit_login, rate_limit_register
from app.dependencies import db_session
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    LogoutResponse,
    RefreshRequest,
    RegisterRequest,
    TokenPairResponse,
)
from app.services.auth_service import login_user, logout_user, refresh_access_token, register_user


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=TokenPairResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(
    payload: RegisterRequest,
    request: Request,
    session: Session = Depends(db_session),
) -> TokenPairResponse:
    rate_limit_register(request)
    return TokenPairResponse(**register_user(session, payload.email, payload.password))


@router.post("/login", response_model=TokenPairResponse, summary="Authenticate and receive access/refresh tokens")
def login(
    payload: LoginRequest,
    request: Request,
    session: Session = Depends(db_session),
) -> TokenPairResponse:
    rate_limit_login(request)
    return TokenPairResponse(**login_user(session, payload.email, payload.password))


@router.post("/refresh", response_model=TokenPairResponse, summary="Exchange a valid refresh token for a new access token")
def refresh(
    payload: RefreshRequest,
    session: Session = Depends(db_session),
) -> TokenPairResponse:
    return TokenPairResponse(**refresh_access_token(session, payload.refresh_token))


@router.post("/logout", response_model=LogoutResponse, summary="Revoke a refresh token and log out")
def logout(
    payload: LogoutRequest,
    session: Session = Depends(db_session),
) -> LogoutResponse:
    logout_user(session, payload.refresh_token)
    return LogoutResponse()
