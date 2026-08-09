from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from app.generator import generate_events
from app.pipeline import TelemetryPipeline
from app.storage import LakehouseStore


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    db_path = Path("data/demo-lakehouse.db")
    store = LakehouseStore(str(db_path))
    pipeline = TelemetryPipeline(store)

    metrics = pipeline.ingest(generate_events(args.events, args.seed))
    print("METRICS")
    print(json.dumps(metrics.model_dump(), indent=2))
    print("\nTOP FINDINGS")
    print(json.dumps(store.recent_findings(10), indent=2))


if __name__ == "__main__":
    main()
