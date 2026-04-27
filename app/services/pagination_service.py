import base64
import json
from datetime import datetime


def encode_cursor(created_at: datetime, item_id: str) -> str:
    payload = {"created_at": created_at.isoformat(), "id": item_id}
    return base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")


def decode_cursor(cursor: str | None) -> tuple[datetime, str] | None:
    if not cursor:
        return None
    raw = base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8")
    payload = json.loads(raw)
    return datetime.fromisoformat(payload["created_at"]), payload["id"]
