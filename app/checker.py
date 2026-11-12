"""Multi-region checker worker with retry, debounce, and quorum."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Awaitable

from .core import Monitor, CheckResult, RegionQuorum


@dataclass
class CheckOutcome:
    monitor_id: str
    region_results: dict[str, CheckResult]
    quorum_status: str  # up | down | degraded
    timestamp: datetime


class Checker:
    """Runs checks across regions with retry + debounce.

    - Retries a failed check up to `retries` times with backoff.
    - Requires `consecutive_failures_threshold` consecutive downs before declaring down (debounce).
    - Uses regional quorum to avoid false positives from a single bad region.
    """

    def __init__(self, retries: int = 2, backoff_s: float = 1.0,
                 concurrency: int = 50):
        self.retries = retries
        self.backoff_s = backoff_s
        self.concurrency = concurrency
        self._failure_counts: dict[str, int] = {}
        self._sem = asyncio.Semaphore(concurrency)

    async def _fetch(self, fetcher: Callable[[str, float], Awaitable[tuple[int, float, str | None]]],
                     url: str, timeout: float) -> tuple[int, float, str | None]:
        last = (0, 0.0, "no attempt")
        for attempt in range(self.retries + 1):
            try:
                code, elapsed, err = await fetcher(url, timeout)
                if err is None and code and code < 500:
                    return code, elapsed, err
                last = (code, elapsed, err or f"http {code}")
            except Exception as e:
                last = (0, 0.0, str(e))
            if attempt < self.retries:
                await asyncio.sleep(self.backoff_s * (attempt + 1))
        return last

    async def check_region(self, monitor: Monitor, region: str,
                           fetcher_factory: Callable[[str], Any],
                           now: datetime | None = None) -> CheckResult:
        now = now or datetime.utcnow()
        _r = fetcher_factory(region)
        fetcher = await _r if asyncio.iscoroutine(_r) else _r
        async with self._sem:
            code, elapsed, err = await self._fetch(fetcher, monitor.url, monitor.timeout_s)
        status = "up"
        if err:
            status = "down"
        elif code != monitor.expected_status:
            status = "down"
            err = err or f"unexpected status {code}"
        # degraded if slow (> 2x typical) but up
        if status == "up" and elapsed > 5000:
            status = "degraded"
        return CheckResult(monitor_id=monitor.id, region=region, timestamp=now,
                          status=status, response_time_ms=round(elapsed, 1),
                          status_code=code, error=err)

    async def check_monitor(self, monitor: Monitor,
                            fetcher_factory: Callable[[str], Any],
                            now: datetime | None = None) -> CheckOutcome:
        now = now or datetime.utcnow()
        quorum = RegionQuorum(regions=monitor.regions,
                              quorum=max(1, len(monitor.regions) // 2 + 1) if len(monitor.regions) > 1 else 1)
        # run all regions concurrently
        tasks = [self.check_region(monitor, r, fetcher_factory, now) for r in monitor.regions]
        results = await asyncio.gather(*tasks)
        region_map = {r.region: r for r in results}
        status_map = {r.region: r.status for r in results}
        raw_status = quorum.decide(status_map)

        # debounce: require consecutive failures
        key = monitor.id
        if raw_status == "down":
            self._failure_counts[key] = self._failure_counts.get(key, 0) + 1
        else:
            self._failure_counts[key] = 0

        if raw_status == "down" and self._failure_counts[key] < monitor.consecutive_failures_threshold:
            # not yet declared down; treat as degraded/up to avoid flapping
            final_status = "degraded"
        else:
            final_status = raw_status

        # if recovered, reset
        if final_status in ("up", "degraded") and raw_status != "down":
            self._failure_counts[key] = 0

        return CheckOutcome(monitor_id=monitor.id, region_results=region_map,
                           quorum_status=final_status, timestamp=now)

    def failure_count(self, monitor_id: str) -> int:
        return self._failure_counts.get(monitor_id, 0)

    def reset_failures(self, monitor_id: str):
        self._failure_counts.pop(monitor_id, None)
