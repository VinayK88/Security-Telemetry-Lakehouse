from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List


USERS = [
    "finance.user@example.com",
    "engineer@example.com",
    "admin@example.com",
    "analyst@example.com",
    "sales@example.com",
]
SOURCES = ["entra", "endpoint", "dns", "saas", "cloud"]
ACTIONS = {
    "entra": ["login", "mfa_challenge", "oauth_consent", "role_assignment"],
    "endpoint": ["process_start", "file_read", "usb_mount", "login"],
    "dns": ["dns_query"],
    "saas": ["file_read", "bulk_download", "share"],
    "cloud": ["api_call", "create_access_key", "object_read"],
}


def generate_events(count: int, seed: int = 42) -> List[Dict]:
    rnd = random.Random(seed)
    now = datetime.now(timezone.utc)
    events: List[Dict] = []

    for i in range(count):
        source = rnd.choice(SOURCES)
        principal = rnd.choice(USERS)
        action = rnd.choice(ACTIONS[source])
        event_time = now - timedelta(seconds=rnd.randint(0, 7200))

        # Inject a deterministic suspicious cluster for the finance identity.
        suspicious = i % 37 == 0
        if suspicious:
            principal = "finance.user@example.com"
            source = "entra"
            action = rnd.choice(["login", "oauth_consent", "role_assignment"])
            outcome = "failure" if action == "login" else "success"
            risk = rnd.uniform(0.7, 0.98)
            src_ip = f"198.51.100.{rnd.randint(10, 220)}"
        else:
            outcome = "failure" if rnd.random() < 0.05 else "success"
            risk = rnd.uniform(0.01, 0.35)
            src_ip = f"203.0.113.{rnd.randint(1, 40)}"

        events.append(
            {
                "timestamp": event_time.isoformat(),
                "source": source,
                "type": (
                    "authentication" if action in {"login", "mfa_challenge"} else "activity"
                ),
                "user": principal,
                "device": f"device-{rnd.randint(1, 25):03d}",
                "ip": src_ip,
                "resource": rnd.choice(
                    ["sharepoint", "github", "snowflake", "m365", "azure-storage"]
                ),
                "action": action,
                "result": outcome,
                "risk": round(risk, 4),
            }
        )

    return events
