from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .generator import generate_events
from .pipeline import TelemetryPipeline
from .storage import LakehouseStore


app = FastAPI(
    title="Security Telemetry Lakehouse",
    version="0.1.0",
    description="Defensive reference implementation for scalable security telemetry processing.",
)

store = LakehouseStore()
pipeline = TelemetryPipeline(store)


class DemoRequest(BaseModel):
    events: int = Field(default=1000, ge=1, le=100000)
    seed: int = 42


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!doctype html>
<html>
<head>
  <title>Security Telemetry Lakehouse</title>
  <meta charset="utf-8" />
  <style>
    body { font-family: ui-sans-serif, system-ui; max-width: 1000px; margin: 40px auto; padding: 0 20px; }
    button { padding: 10px 16px; cursor: pointer; }
    pre { background: #111; color: #eee; padding: 16px; overflow: auto; border-radius: 8px; }
    .grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
    .card { border:1px solid #ddd; border-radius:8px; padding:14px; }
  </style>
</head>
<body>
  <h1>Security Telemetry Lakehouse</h1>
  <p>Normalize → deduplicate → watermark → aggregate → detect.</p>
  <button onclick="runDemo()">Generate + ingest 5,000 events</button>
  <h2>Pipeline metrics</h2>
  <pre id="metrics">Click the button to run the demo.</pre>
  <h2>Highest-risk findings</h2>
  <pre id="findings"></pre>
<script>
async function runDemo() {
  const r = await fetch('/demo/ingest', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({events:5000, seed:42})
  });
  document.getElementById('metrics').textContent =
    JSON.stringify(await r.json(), null, 2);

  const f = await fetch('/findings?limit=10');
  document.getElementById('findings').textContent =
    JSON.stringify(await f.json(), null, 2);
}
</script>
</body>
</html>
"""


@app.post("/demo/ingest")
def demo_ingest(req: DemoRequest):
    events = generate_events(req.events, seed=req.seed)
    return pipeline.ingest(events).model_dump()


@app.get("/metrics")
def metrics():
    return pipeline.metrics.model_dump()


@app.get("/events")
def events(limit: int = 100):
    return store.recent_events(min(max(limit, 1), 1000))


@app.get("/features")
def features(limit: int = 100):
    return [f.model_dump() for f in pipeline.features()[: min(max(limit, 1), 1000)]]


@app.get("/findings")
def findings(limit: int = 100):
    return store.recent_findings(min(max(limit, 1), 1000))


@app.get("/dead-letter")
def dead_letter(limit: int = 100):
    return pipeline.dead_letters[-min(max(limit, 1), 1000):]
