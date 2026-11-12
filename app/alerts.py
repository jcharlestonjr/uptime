"""Alert dispatcher: templates, cooldown, escalation, multi-channel."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from .core import Alert, Monitor, Incident


# ---------------------------------------------------------------------------
# Templates (email / slack / webhook / sms)
# ---------------------------------------------------------------------------
EMAIL_DOWN = """Subject: 🔴 {monitor_name} is DOWN

Hi,

Your monitor "{monitor_name}" ({url}) is DOWN as of {started_at}.

Cause: {cause}
Region(s) affected: {regions}

We'll notify you when it recovers.

— Uptime Pro
Status page: {status_page_url}
"""

EMAIL_UP = """Subject: ✅ {monitor_name} is back UP

Hi,

Your monitor "{monitor_name}" ({url}) recovered at {resolved_at}.

Downtime: {duration} minutes.

— Uptime Pro
"""

SLACK_DOWN = ":rotating_light: *{monitor_name}* is DOWN\nURL: {url}\nCause: {cause}\nStarted: {started_at}"
SLACK_UP = ":white_check_mark: *{monitor_name}* recovered\nDowntime: {duration} min"

SMS_DOWN = "ALERT: {monitor_name} DOWN - {url} - {cause}"
WEBHOOK_PAYLOAD = {
    "event": "{event}",
    "monitor": {"id": "{monitor_id}", "name": "{monitor_name}", "url": "{url}"},
    "incident": {"id": "{incident_id}", "started_at": "{started_at}",
                 "resolved_at": "{resolved_at}", "duration_min": "{duration}"},
    "cause": "{cause}",
}


class AlertDispatcher:
    """Decides when to alert, applies cooldown, renders templates, dispatches."""

    def __init__(self, cooldown_min: int = 5):
        self.cooldown_min = cooldown_min
        self._last_sent: dict[str, datetime] = {}  # monitor_id -> last alert time

    def should_alert(self, monitor: Monitor, incident: Incident,
                     now: datetime | None = None) -> bool:
        now = now or datetime.utcnow()
        if incident.notified:
            return False
        last = self._last_sent.get(monitor.id)
        if last and (now - last).total_seconds() < self.cooldown_min * 60:
            return False
        return True

    def mark_sent(self, monitor_id: str, now: datetime | None = None):
        self._last_sent[monitor_id] = now or datetime.utcnow()

    def render_down(self, monitor: Monitor, incident: Incident,
                    regions: list[str], status_page_url: str = "") -> dict[str, str]:
        ctx = {
            "monitor_name": monitor.name,
            "url": monitor.url,
            "started_at": incident.started_at.isoformat(),
            "cause": incident.cause,
            "regions": ", ".join(regions),
            "status_page_url": status_page_url,
        }
        return {
            "email": EMAIL_DOWN.format(**ctx),
            "slack": SLACK_DOWN.format(**ctx),
            "sms": SMS_DOWN.format(**ctx),
        }

    def render_up(self, monitor: Monitor, incident: Incident) -> dict[str, str]:
        ctx = {
            "monitor_name": monitor.name,
            "url": monitor.url,
            "resolved_at": (incident.resolved_at.isoformat() if incident.resolved_at else ""),
            "duration": incident.duration_min,
        }
        return {
            "email": EMAIL_UP.format(**ctx),
            "slack": SLACK_UP.format(**ctx),
        }

    def build_alerts(self, monitor: Monitor, incident: Incident,
                     event: str, regions: list[str],
                     status_page_url: str = "") -> list[Alert]:
        alerts = []
        if event == "down":
            rendered = self.render_down(monitor, incident, regions, status_page_url)
            severity = "critical"
            title = f"{monitor.name} is DOWN"
            body = rendered.get("email", "")
        else:
            rendered = self.render_up(monitor, incident)
            severity = "info"
            title = f"{monitor.name} recovered"
            body = rendered.get("email", "")
        for ch in monitor.alert_channels:
            alerts.append(Alert(monitor_id=monitor.id, channel=ch, severity=severity,
                                title=title, body=body))
        return alerts

    def escalate(self, incident: Incident, monitor: Monitor,
                now: datetime | None = None) -> list[str]:
        """Return escalation actions if incident open too long."""
        now = now or datetime.utcnow()
        actions = []
        if incident.open:
            mins = (now - incident.started_at).total_seconds() / 60.0
            if mins >= 30 and "sms" not in monitor.alert_channels:
                actions.append("add_sms_channel")
            if mins >= 60:
                actions.append("page_oncall")
            if mins >= 120:
                actions.append("create_war_room")
        return actions
