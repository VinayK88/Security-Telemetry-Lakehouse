from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SecurityEvent(BaseModel):
    event_id: str
    event_time: datetime
    ingest_time: datetime
    source: str
    event_type: str
    principal: Optional[str] = None
    device_id: Optional[str] = None
    src_ip: Optional[str] = None
    destination: Optional[str] = None
    action: str
    outcome: str
    risk: float = Field(default=0.0, ge=0.0, le=1.0)
    attributes: Dict[str, Any] = Field(default_factory=dict)


class PipelineMetrics(BaseModel):
    received: int = 0
    accepted: int = 0
    duplicates: int = 0
    late_events: int = 0
    dead_letter: int = 0
    findings: int = 0


class FeatureWindow(BaseModel):
    principal: str
    window_start: datetime
    event_count: int
    failed_logins: int
    distinct_ips: int
    sensitive_actions: int
    average_risk: float


class Finding(BaseModel):
    principal: str
    finding_type: str
    score: float
    reason: str
    window_start: datetime
