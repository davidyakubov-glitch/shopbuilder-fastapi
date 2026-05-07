try:
    from celery import Celery
except ImportError:  # pragma: no cover - keeps local tests usable before installing worker deps
    Celery = None

from app.config import settings

if Celery is not None:
    celery_app = Celery(
        "shopbuilder",
        broker=settings.resolved_celery_broker_url,
        backend=settings.resolved_celery_result_backend,
    )
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
else:
    celery_app = None
