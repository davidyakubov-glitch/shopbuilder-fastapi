import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class EmailDeliveryError(RuntimeError):
    pass


def send_email(to_email: str, subject: str, html: str, text: str | None = None) -> dict:
    if settings.email_delivery_mode == "log" or settings.app_env == "test":
        logger.info("Email queued for %s with subject %s", to_email, subject)
        return {"provider": "log", "status": "accepted"}

    if settings.email_provider != "resend":
        raise EmailDeliveryError(f"Unsupported email provider: {settings.email_provider}")
    if not settings.resend_api_key:
        raise EmailDeliveryError("RESEND_API_KEY is required when using Resend email delivery.")

    response = httpx.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {settings.resend_api_key}"},
        json={
            "from": settings.email_from,
            "to": [to_email],
            "subject": subject,
            "html": html,
            "text": text,
        },
        timeout=15,
    )
    if response.status_code >= 400:
        raise EmailDeliveryError(f"Resend rejected email: {response.status_code} {response.text}")
    return response.json()


def verification_email(email: str, token: str) -> tuple[str, str, str]:
    link = f"{settings.app_public_url}/api/v1/auth/email/verify?token={token}"
    subject = "Verify your ShopBuilder account"
    html = f"<p>Welcome to ShopBuilder.</p><p>Verify your email: <a href=\"{link}\">{link}</a></p>"
    text = f"Welcome to ShopBuilder. Verify your email: {link}"
    return subject, html, text


def password_reset_email(email: str, token: str) -> tuple[str, str, str]:
    link = f"{settings.app_public_url}/reset-password?token={token}"
    subject = "Reset your ShopBuilder password"
    html = f"<p>Use this secure link to reset your password: <a href=\"{link}\">{link}</a></p>"
    text = f"Use this secure link to reset your password: {link}"
    return subject, html, text


def order_confirmation_email(order_id: str, email: str) -> tuple[str, str, str]:
    subject = f"ShopBuilder order {order_id} confirmation"
    html = f"<p>Your order <strong>{order_id}</strong> was received and is pending payment.</p>"
    text = f"Your order {order_id} was received and is pending payment."
    return subject, html, text
