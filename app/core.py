"""Core domain models (enhanced from MVP)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


@dataclass
class Monitor:
    id: str
    name: str
    url: str
    interval_min: int = 5
    timeout_s: float = 10.0
    expected_status: int = 200
    regions: list[str] = field(default_factory=lambda: ["us-east", "eu-west"])
    active: bool = True
    alert_channels: list[str] = field(default_factory=lambda: ["email"])
    cooldown_min: int = 5
    consecutive_failures_threshold: int = 2  # debounce


@dataclass
class CheckResult:
    monitor_id: str
    region: str
    timestamp: datetime
    status: str  # up | down | degraded
    response_time_ms: float
    status_code: int | None = None
    error: str | None = None


@dataclass
class Incident:
    id: str
    monitor_id: str
    started_at: datetime
    resolved_at: datetime | None = None
    cause: str = ""
    notified: bool = False
    post_mortem: str = ""

    @property
    def duration_min(self) -> float:
        end = self.resolved_at or datetime.utcnow()
        return round((end - self.started_at).total_seconds() / 60.0, 1)

    @property
    def open(self) -> bool:
        return self.resolved_at is None


@dataclass
class Alert:
    monitor_id: str
    channel: str  # email | slack | webhook | sms
    severity: str  # info | warning | critical
    title: str
    body: str
    sent_at: datetime | None = None
    delivered: bool = False


@dataclass
class RegionQuorum:
    """Quorum decision across regions: down only if >= quorum regions agree."""
    regions: list[str]
    quorum: int = 1

    def decide(self, results: dict[str, str]) -> str:
        downs = sum(1 for r in results.values() if r == "down")
        if downs >= self.quorum:
            return "down"
        if any(r == "degraded" for r in results.values()):
            return "degraded"
        return "up"
