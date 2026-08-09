import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.pipeline import TelemetryPipeline
from app.storage import LakehouseStore


class PipelineTests(unittest.TestCase):
    def test_deduplication_and_dead_letter(self):
        with tempfile.TemporaryDirectory() as td:
            store = LakehouseStore(str(Path(td) / "test.db"))
            pipeline = TelemetryPipeline(store)

            now = datetime.now(timezone.utc)
            event = {
                "event_id": "same-id",
                "event_time": now.isoformat(),
                "source": "entra",
                "event_type": "authentication",
                "principal": "u@example.com",
                "action": "login",
                "outcome": "success",
                "risk": 0.1,
            }

            metrics = pipeline.ingest([event, event, {"source": "entra"}])
            self.assertEqual(metrics.received, 3)
            self.assertEqual(metrics.accepted, 1)
            self.assertEqual(metrics.duplicates, 1)
            self.assertEqual(metrics.dead_letter, 1)

    def test_late_event_is_counted_but_stored(self):
        with tempfile.TemporaryDirectory() as td:
            store = LakehouseStore(str(Path(td) / "test.db"))
            pipeline = TelemetryPipeline(store, allowed_lateness_minutes=5)

            event = {
                "event_id": "late-1",
                "event_time": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "source": "endpoint",
                "event_type": "activity",
                "principal": "u@example.com",
                "action": "file_read",
                "outcome": "success",
                "risk": 0.1,
            }

            metrics = pipeline.ingest([event])
            self.assertEqual(metrics.late_events, 1)
            self.assertEqual(metrics.accepted, 1)
            self.assertEqual(len(store.recent_events()), 1)


if __name__ == "__main__":
    unittest.main()
