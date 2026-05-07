from app.config import settings
from app.services.email_service import send_email
from app.workers.celery_app import celery_app


def _send_email_task(to_email: str, subject: str, html: str, text: str | None = None) -> dict:
    return send_email(to_email, subject, html, text)


if celery_app is not None:

    @celery_app.task(name="email.send")
    def send_email_task(to_email: str, subject: str, html: str, text: str | None = None) -> dict:
        return _send_email_task(to_email, subject, html, text)

else:

    class _InlineEmailTask:
        @staticmethod
        def delay(to_email: str, subject: str, html: str, text: str | None = None) -> dict:
            return _send_email_task(to_email, subject, html, text)

    send_email_task = _InlineEmailTask()


def enqueue_email(to_email: str, subject: str, html: str, text: str | None = None) -> None:
    if settings.email_delivery_mode in {"sync", "log"} or settings.app_env == "test":
        _send_email_task(to_email, subject, html, text)
        return
    send_email_task.delay(to_email, subject, html, text)
