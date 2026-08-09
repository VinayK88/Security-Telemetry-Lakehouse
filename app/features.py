from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, Iterable, List, Tuple

from .models import FeatureWindow


SENSITIVE_ACTIONS = {
    "role_assignment",
    "oauth_consent",
    "bulk_download",
    "disable_mfa",
    "create_access_key",
}


def _hour_bucket(ts: datetime) -> datetime:
    return ts.replace(minute=0, second=0, microsecond=0)


def build_hourly_features(events: Iterable[dict]) -> List[FeatureWindow]:
    buckets: Dict[Tuple[str, datetime], dict] = defaultdict(
        lambda: {
            "event_count": 0,
            "failed_logins": 0,
            "ips": set(),
            "sensitive_actions": 0,
            "risk_sum": 0.0,
        }
    )

    for row in events:
        principal = row.get("principal")
        if not principal:
            continue

        ts = row["event_time"]
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))

        key = (principal, _hour_bucket(ts))
        b = buckets[key]
        b["event_count"] += 1
        if row.get("outcome") == "failure":
            b["failed_logins"] += 1
        if row.get("src_ip"):
            b["ips"].add(row["src_ip"])
        if row.get("action") in SENSITIVE_ACTIONS:
            b["sensitive_actions"] += 1
        b["risk_sum"] += float(row.get("risk", 0.0))

    result = []
    for (principal, window_start), b in buckets.items():
        result.append(
            FeatureWindow(
                principal=principal,
                window_start=window_start,
                event_count=b["event_count"],
                failed_logins=b["failed_logins"],
                distinct_ips=len(b["ips"]),
                sensitive_actions=b["sensitive_actions"],
                average_risk=round(b["risk_sum"] / max(1, b["event_count"]), 4),
            )
        )

    return sorted(result, key=lambda x: x.window_start, reverse=True)
