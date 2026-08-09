# Security Telemetry Lakehouse

> **Turn massive security telemetry into normalized, queryable, detection-ready signals.**

A defensive, GitHub-ready reference implementation for a security telemetry platform designed around the same engineering problems that appear at very large scale: schema normalization, deduplication, late-arriving events, partitioning, behavioral aggregation, anomaly scoring, observability, and cost-aware storage tiers.

The default demo runs locally with Python + SQLite so anyone can evaluate it in minutes. The repository also documents how the same contracts map to Kafka / Spark / object storage / BigQuery or ClickHouse in production.

## Why this project exists

Security platforms routinely ingest endpoint, identity, DNS, proxy, cloud, SaaS, and authentication telemetry at enormous volume. The hard part is not simply "put events in Kafka." The platform must preserve correctness while keeping latency and cost under control.

This project demonstrates a concrete answer to:

> **How would you process billions of security telemetry events per day?**

## Architecture

```text
Endpoint / Identity / DNS / SaaS / Cloud / Proxy
                     |
                     v
              Event Ingestion
                     |
                     v
          Canonical Normalization
                     |
          +----------+-----------+
          |                      |
          v                      v
      Deduplication          Dead Letter
          |
          v
      Event-time Watermark
          |
          v
    Partitioned Raw Telemetry
    date/source/hour partitions
          |
          v
    Behavioral Aggregations
 user / device / IP / app windows
          |
          v
       Detection Layer
  anomaly + policy + heuristics
          |
          v
        FastAPI
          |
          v
  Analyst / SOC / dashboards
```

## What the MVP implements

- Canonical security event schema
- Synthetic endpoint, identity, DNS, cloud, and SaaS telemetry
- Deterministic event IDs
- Deduplication
- Event-time vs ingestion-time handling
- Configurable lateness watermark
- Dead-letter handling for malformed events
- Partition-aware local storage
- Hourly behavioral feature aggregation
- Baseline anomaly scoring
- Detection findings with explanations
- Pipeline health metrics
- FastAPI endpoints
- Browser demo
- Unit tests
- Dockerfile
- Production scaling design notes

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

Generate and ingest 10,000 synthetic events:

```bash
python scripts/run_demo.py --events 10000
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Example event

```json
{
  "event_id": "93bde8...",
  "event_time": "2026-08-10T10:21:31+00:00",
  "ingest_time": "2026-08-10T10:21:34+00:00",
  "source": "entra",
  "event_type": "authentication",
  "principal": "finance.user@example.com",
  "device_id": "mac-fin-014",
  "src_ip": "203.0.113.24",
  "action": "login",
  "outcome": "success",
  "risk": 0.14
}
```

## Example analytic

The feature layer can derive observations like:

```text
finance.user@example.com
  logins_last_hour:       18
  distinct_ips:            7
  failed_logins:          11
  countries_seen:          4
  sensitive_actions:       2
```

The baseline scorer can then produce:

```text
Finding: unusual_identity_behavior
Score:   0.89

Why:
- failed login count is 4.1x baseline
- distinct source IPs is 3.5x baseline
- privileged activity occurred in the same window
```

## Scaling to billions of events

The local implementation intentionally keeps infrastructure small, but the contracts are production-oriented.

### Ingestion

At large scale:

```text
Producers
   |
   v
Regional Kafka / Pub/Sub
   |
   +--> validation / normalization
   |
   +--> replayable raw topic
```

Partition by a high-cardinality routing key such as tenant + source + time bucket rather than by a single user, which can create hot partitions.

### Stream processing

Use Spark Structured Streaming, Flink, Dataflow, or Kafka Streams for:

- schema normalization
- deduplication
- event-time windows
- watermarking
- enrichment
- feature computation
- routing

Stateful operators should use bounded TTLs and checkpointing.

### Storage tiers

```text
HOT
ClickHouse / BigQuery / Elasticsearch
hours to days

WARM
Parquet / Delta / Iceberg
days to months

COLD
compressed object storage
months to years
```

Raw immutable events should be retained separately from enriched or aggregated datasets so the system can replay history when detection logic changes.

### Partitioning

A common layout:

```text
/security_events/
    event_date=2026-08-10/
      source=entra/
        hour=10/
          part-0001.parquet
```

Avoid excessively small partitions. Compaction should merge small files asynchronously.

### Exactly-once thinking

Perfect exactly-once delivery across a distributed system is often expensive. A more practical pattern is:

```text
at-least-once delivery
        +
deterministic event IDs
        +
idempotent sinks
        +
deduplication windows
```

### Late events

Security events frequently arrive late because endpoints are offline or upstream systems batch data.

Track both:

```text
event_time
ingest_time
```

and define explicit watermarks so late telemetry is handled deterministically rather than silently dropped.

### Cost controls

At very large scale:

- aggregate before long-term storage when raw fidelity is not required
- compress columnar data
- tier old data
- separate interactive and archival workloads
- avoid indexing every field
- sample low-value diagnostic telemetry
- retain high-value security events at full fidelity

## Repository structure

```text
security-telemetry-lakehouse/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── normalize.py
│   ├── pipeline.py
│   ├── storage.py
│   ├── features.py
│   ├── detection.py
│   └── generator.py
├── scripts/
│   └── run_demo.py
├── tests/
│   ├── test_pipeline.py
│   └── test_features.py
├── docs/
│   ├── production-architecture.md
│   └── interview-walkthrough.md
├── data/
│   └── .gitkeep
├── Dockerfile
├── requirements.txt
├── SECURITY.md
├── CONTRIBUTING.md
├── LICENSE
└── .gitignore
```

## API

### `POST /demo/ingest`

Generate and ingest synthetic telemetry.

```json
{
  "events": 5000,
  "seed": 42
}
```

### `GET /metrics`

Pipeline metrics.

### `GET /findings`

Highest-risk findings.

### `GET /features`

Recent behavioral feature windows.

### `GET /events`

Recent normalized events.

## Production roadmap

- Kafka / Pub/Sub ingestion adapter
- Spark Structured Streaming implementation
- Iceberg / Delta / BigQuery sink
- OCSF-compatible schema adapter
- schema registry support
- tenant isolation
- entity resolution
- ATT&CK enrichment
- streaming feature store
- ML-based anomaly detection
- graph-ready security entities
- OpenTelemetry metrics
- backpressure controller
- replay / backfill orchestrator
- data quality SLAs

## Security

This repository is defensive and uses synthetic telemetry. It does not exploit systems or provide offensive capabilities.

See [SECURITY.md](SECURITY.md).

## License

MIT.
