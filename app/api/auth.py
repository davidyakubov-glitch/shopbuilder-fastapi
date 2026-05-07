from fastapi import APIRouter, Depends, Request, status
from sqlmodel import Session

from app.core.rate_limit import rate_limit_login, rate_limit_register
from app.dependencies import db_session
from app.schemas.auth import (
    EmailVerificationRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    LogoutResponse,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenPairResponse,
)
from app.services.auth_service import (
    login_user,
    logout_user,
    refresh_access_token,
    register_user,
    request_password_reset,
    resend_verification_email,
    reset_password,
    verify_email,
)

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


@router.post(
    "/refresh",
    response_model=TokenPairResponse,
    summary="Exchange a valid refresh token for a new access token",
)
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


@router.post("/email/verify", response_model=MessageResponse, summary="Verify an email address with a one-time token")
def verify_email_address(
    payload: EmailVerificationRequest,
    session: Session = Depends(db_session),
) -> MessageResponse:
    verify_email(session, payload.token)
    return MessageResponse(message="Email address verified.")


@router.post(
    "/email/resend",
    response_model=MessageResponse,
    summary="Send a new email verification token",
)
def resend_email_verification(
    payload: ResendVerificationRequest,
    request: Request,
    session: Session = Depends(db_session),
) -> MessageResponse:
    rate_limit_register(request)
    resend_verification_email(session, payload.email)
    return MessageResponse(message="If the account exists, a verification email has been queued.")


@router.post(
    "/password/forgot",
    response_model=MessageResponse,
    summary="Queue a password reset email",
)
def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    session: Session = Depends(db_session),
) -> MessageResponse:
    rate_limit_login(request)
    request_password_reset(session, payload.email)
    return MessageResponse(message="If the account exists, a password reset email has been queued.")


@router.post(
    "/password/reset",
    response_model=MessageResponse,
    summary="Reset password using a one-time token",
)
def complete_password_reset(
    payload: ResetPasswordRequest,
    session: Session = Depends(db_session),
) -> MessageResponse:
    reset_password(session, payload.token, payload.new_password)
    return MessageResponse(message="Password has been reset.")
