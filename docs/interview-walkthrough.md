# Interview Walkthrough

## 60-second answer: How would you process billions of telemetry events?

"I would separate the system into ingestion, stream processing, storage, feature computation, and serving. Producers write to a replayable bus such as Kafka or Pub/Sub. I normalize source-specific events into a versioned canonical schema, then perform deterministic deduplication and event-time processing with watermarks so late endpoint events do not corrupt windows.

For storage, I keep immutable raw events in cheap object storage in Parquet/Iceberg and a smaller hot analytical tier in BigQuery, ClickHouse, or a similar system. I partition by time and source/tenant, compact small files, and pre-aggregate high-volume telemetry into behavioral features.

For correctness, I prefer at-least-once delivery with idempotent sinks over trying to make every component globally exactly once. For operations, I monitor consumer lag, malformed-event rate, late events, p99 latency, state size, and cost per million events. The detection layer reads normalized data and streaming features rather than source-specific schemas."

## Why event time matters

Endpoint telemetry can arrive minutes or hours after the actual event. Authentication systems may deliver near-real-time data while laptops reconnect after being offline.

Using ingestion time alone changes the sequence of an investigation.

## Why raw + enriched storage

Detection logic evolves. Retaining immutable raw events allows:

- replay
- backfill
- new features
- incident reconstruction
- auditing

Derived data can be replaced. Raw evidence should not be.

## Why this repository uses SQLite

The goal is to make the project runnable without provisioning a cluster. SQLite models the sink contract; the production document explains the distributed equivalent.
