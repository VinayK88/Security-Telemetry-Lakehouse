from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, List

from .models import Finding, FeatureWindow, SecurityEvent


class LakehouseStore:
    def __init__(self, db_path: str = "data/lakehouse.db"):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init()

    def _init(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                event_time TEXT NOT NULL,
                ingest_time TEXT NOT NULL,
                event_date TEXT NOT NULL,
                event_hour INTEGER NOT NULL,
                source TEXT NOT NULL,
                event_type TEXT NOT NULL,
                principal TEXT,
                device_id TEXT,
                src_ip TEXT,
                destination TEXT,
                action TEXT NOT NULL,
                outcome TEXT NOT NULL,
                risk REAL NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_events_partition
            ON events(event_date, source, event_hour);

            CREATE INDEX IF NOT EXISTS idx_events_principal_time
            ON events(principal, event_time);

            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                principal TEXT NOT NULL,
                finding_type TEXT NOT NULL,
                score REAL NOT NULL,
                reason TEXT NOT NULL,
                window_start TEXT NOT NULL
            );
            """
        )
        self.conn.commit()

    def event_exists(self, event_id: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM events WHERE event_id = ?", (event_id,)
        ).fetchone()
        return row is not None

    def insert_event(self, e: SecurityEvent) -> None:
        self.conn.execute(
            """
            INSERT INTO events (
                event_id, event_time, ingest_time, event_date, event_hour,
                source, event_type, principal, device_id, src_ip, destination,
                action, outcome, risk
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                e.event_id,
                e.event_time.isoformat(),
                e.ingest_time.isoformat(),
                e.event_time.date().isoformat(),
                e.event_time.hour,
                e.source,
                e.event_type,
                e.principal,
                e.device_id,
                e.src_ip,
                e.destination,
                e.action,
                e.outcome,
                e.risk,
            ),
        )
        self.conn.commit()

    def recent_events(self, limit: int = 100) -> List[dict]:
        rows = self.conn.execute(
            "SELECT * FROM events ORDER BY event_time DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def events_for_features(self, limit: int = 100000) -> List[dict]:
        rows = self.conn.execute(
            """
            SELECT event_time, principal, src_ip, action, outcome, risk, event_type
            FROM events
            WHERE principal IS NOT NULL
            ORDER BY event_time DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def replace_findings(self, findings: Iterable[Finding]) -> None:
        self.conn.execute("DELETE FROM findings")
        self.conn.executemany(
            """
            INSERT INTO findings(principal, finding_type, score, reason, window_start)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    f.principal,
                    f.finding_type,
                    f.score,
                    f.reason,
                    f.window_start.isoformat(),
                )
                for f in findings
            ],
        )
        self.conn.commit()

    def recent_findings(self, limit: int = 100) -> List[dict]:
        rows = self.conn.execute(
            "SELECT * FROM findings ORDER BY score DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def close(self) -> None:
        self.conn.close()
