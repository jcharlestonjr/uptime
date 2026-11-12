"""Checker worker entrypoint — runs checks on a schedule."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from .checker import Checker
from .core import Monitor

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("uptime-worker")

# In-memory monitor registry (replace with DB in prod)
_MONITORS: list[Monitor] = []


def register(monitor: Monitor):
    _MONITORS.append(monitor)


async def _fetcher_factory(region: str):
    """Returns a fetcher for a region. Replace with real httpx call."""
    import httpx

    async def fetcher(url: str, timeout: float):
        async with httpx.AsyncClient(timeout=timeout) as client:
            start = datetime.utcnow()
            try:
                resp = await client.get(url, follow_redirects=True)
                elapsed = (datetime.utcnow() - start).total_seconds() * 1000
                return resp.status_code, elapsed, None
            except Exception as e:
                elapsed = (datetime.utcnow() - start).total_seconds() * 1000
                return 0, elapsed, str(e)

    return fetcher


async def run_once(checker: Checker):
    for m in _MONITORS:
        if not m.active:
            continue
        outcome = await checker.check_monitor(m, _fetcher_factory)
        log.info("monitor=%s status=%s regions=%s", m.id, outcome.quorum_status,
                 {r: c.status for r, c in outcome.region_results.items()})


async def main():
    checker = Checker(retries=2, backoff_s=1.0, concurrency=50)
    log.info("Uptime worker started. monitors=%d", len(_MONITORS))
    while True:
        await run_once(checker)
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
