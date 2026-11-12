"""In-memory store for Uptime Pro (prod-shaped)."""

from __future__ import annotations

from threading import Lock
from .core import Monitor, CheckResult, Incident
from .incidents import IncidentManager
from .alerts import AlertDispatcher


class Store:
    def __init__(self):
        self.monitors: dict[str, Monitor] = {}
        self.checks: dict[str, list[CheckResult]] = {}
        self.incidents: list[Incident] = []
        self.status_pages: dict[str, str] = {}
        self.incident_manager = IncidentManager()
        self.alert_dispatcher = AlertDispatcher(cooldown_min=5)
        self._counters = {"mon": 0, "inc": 0}
        self._lock = Lock()

    def _next(self, k):
        with self._lock:
            self._counters[k] += 1
            return self._counters[k]

    def add_monitor(self, **kw) -> str:
        mid = f"m_{self._next('mon')}"
        self.monitors[mid] = Monitor(id=mid, **kw)
        self.checks[mid] = []
        return mid

    def get_monitor(self, mid):
        return self.monitors.get(mid)

    def record_check(self, r: CheckResult):
        self.checks.setdefault(r.monitor_id, []).append(r)

    def get_checks(self, mid):
        return self.checks.get(mid, [])

    def add_incident(self, inc: Incident) -> Incident:
        if not inc.id:
            inc.id = f"i_{self._next('inc')}"
        self.incidents.append(inc)
        self.incident_manager.incidents.append(inc)
        return inc

    def incidents_for(self, mid):
        return [i for i in self.incidents if i.monitor_id == mid]

    def open_incident_for(self, mid):
        return next((i for i in self.incidents if i.monitor_id == mid and i.open), None)

    def create_status_page(self, slug, monitor_id):
        self.status_pages[slug] = monitor_id

    def status_page_monitor(self, slug):
        mid = self.status_pages.get(slug)
        return self.monitors.get(mid) if mid else None


store = Store()
