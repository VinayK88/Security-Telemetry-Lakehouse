from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict

from .models import SecurityEvent


def _stable_id(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def normalize_event(raw: Dict[str, Any], ingest_time: datetime | None = None) -> SecurityEvent:
    """Normalize several synthetic source shapes into one canonical schema."""
    ingest_time = ingest_time or datetime.now(timezone.utc)
    source = str(raw.get("source", "unknown")).lower()

    event_time_raw = raw.get("event_time") or raw.get("timestamp")
    if not event_time_raw:
        raise ValueError("missing event_time")

    if isinstance(event_time_raw, str):
        event_time = datetime.fromisoformat(event_time_raw.replace("Z", "+00:00"))
    else:
        event_time = event_time_raw

    if event_time.tzinfo is None:
        event_time = event_time.replace(tzinfo=timezone.utc)

    fields = {
        "source": source,
        "event_type": raw.get("event_type") or raw.get("type") or "generic",
        "principal": raw.get("principal") or raw.get("user") or raw.get("actor"),
        "device_id": raw.get("device_id") or raw.get("device"),
        "src_ip": raw.get("src_ip") or raw.get("ip"),
        "destination": raw.get("destination") or raw.get("resource"),
        "action": raw.get("action") or "observe",
        "outcome": raw.get("outcome") or raw.get("result") or "unknown",
        "risk": float(raw.get("risk", 0.0)),
        "attributes": raw.get("attributes", {}),
    }

    id_payload = {"event_time": event_time.isoformat(), **fields}
    event_id = str(raw.get("event_id") or _stable_id(id_payload))

    return SecurityEvent(
        event_id=event_id,
        event_time=event_time,
        ingest_time=ingest_time,
        **fields,
    )
