from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List

from .detection import score_features
from .features import build_hourly_features
from .models import FeatureWindow, PipelineMetrics
from .normalize import normalize_event
from .storage import LakehouseStore


class TelemetryPipeline:
    def __init__(self, store: LakehouseStore, allowed_lateness_minutes: int = 30):
        self.store = store
        self.allowed_lateness = timedelta(minutes=allowed_lateness_minutes)
        self.metrics = PipelineMetrics()
        self.dead_letters: List[dict] = []

    def ingest(self, raw_events: Iterable[Dict]) -> PipelineMetrics:
        now = datetime.now(timezone.utc)

        for raw in raw_events:
            self.metrics.received += 1

            try:
                event = normalize_event(raw, ingest_time=now)
            except Exception as exc:
                self.metrics.dead_letter += 1
                self.dead_letters.append({"event": raw, "error": str(exc)})
                continue

            if self.store.event_exists(event.event_id):
                self.metrics.duplicates += 1
                continue

            if event.event_time < now - self.allowed_lateness:
                self.metrics.late_events += 1

            self.store.insert_event(event)
            self.metrics.accepted += 1

        self.refresh_analytics()
        return self.metrics

    def refresh_analytics(self) -> None:
        features = self.features()
        findings = score_features(features)
        self.store.replace_findings(findings)
        self.metrics.findings = len(findings)

    def features(self) -> List[FeatureWindow]:
        return build_hourly_features(self.store.events_for_features())
