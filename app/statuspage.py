"""Static status page renderer + custom domain provisioning helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .core import Monitor


STATUS_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — Status</title>
<style>
:root{{--primary:{primary};--bg:{bg};--text:{text};}}
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:Inter,system-ui,sans-serif;background:var(--bg);color:var(--text);padding:2rem;max-width:760px;margin:0 auto;}}
h1{{font-size:1.5rem;margin-bottom:.25rem;}}
.sub{{opacity:.6;margin-bottom:1.5rem;font-size:.9rem;}}
.card{{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:1.25rem;margin-bottom:1rem;box-shadow:0 1px 2px rgba(0,0,0,.04);}}
.status{{display:flex;align-items:center;gap:.6rem;font-weight:600;}}
.dot{{width:10px;height:10px;border-radius:50%;}}
.up{{background:#22c55e;}}.down{{background:#ef4444;}}.degraded{{background:#f59e0b;}}
.metrics{{display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem;margin-top:1rem;}}
.metric{{text-align:center;}}
.metric .v{{font-size:1.25rem;font-weight:700;}}
.metric .l{{font-size:.75rem;opacity:.6;}}
.incident{{border-left:3px solid #ef4444;padding:.75rem 1rem;margin-top:.75rem;background:#fef2f2;border-radius:6px;}}
.incident.resolved{{border-color:#22c55e;background:#f0fdf4;}}
.footer{{margin-top:2rem;text-align:center;font-size:.75rem;opacity:.5;}}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="sub">{subtitle}</p>
<div class="card">
  <div class="status"><span class="dot {current_class}"></span>{current_label}</div>
  <div class="metrics">
    <div class="metric"><div class="v">{uptime_24h}%</div><div class="l">24h uptime</div></div>
    <div class="metric"><div class="v">{uptime_7d}%</div><div class="l">7d uptime</div></div>
    <div class="metric"><div class="v">{avg_ms}ms</div><div class="l">avg response</div></div>
  </div>
</div>
{incidents_html}
<div class="footer">Powered by Uptime Pro</div>
</body>
</html>"""


def render_status_page(title: str, current: str, uptime_24h: float, uptime_7d: float,
                       avg_ms: float, incidents: list[dict], primary: str = "#2563eb") -> str:
    current_class = current if current in ("up", "down", "degraded") else "up"
    current_label = {"up": "All systems operational", "down": "Major outage",
                     "degraded": "Degraded performance"}.get(current, "Unknown")
    inc_html = ""
    for inc in incidents:
        cls = "resolved" if inc.get("resolved_at") else ""
        inc_html += (f'<div class="incident {cls}"><strong>{inc.get("cause","Incident")}</strong>'
                     f'<br><small>{inc.get("started_at","")} → {inc.get("resolved_at") or "ongoing"} '
                     f'({inc.get("duration_min","?")} min)</small></div>')
    if not inc_html:
        inc_html = '<div class="card"><em>No recent incidents.</em></div>'
    return STATUS_PAGE_HTML.format(
        title=title, subtitle="Real-time status", primary=primary,
        bg="#f9fafb", text="#111827", current_class=current_class,
        current_label=current_label, uptime_24h=uptime_24h, uptime_7d=uptime_7d,
        avg_ms=avg_ms, incidents_html=inc_html)


def custom_domain_instructions(domain: str, cname_target: str = "status.uptimepro.app") -> dict:
    """Return DNS setup instructions for a custom domain."""
    return {
        "domain": domain,
        "steps": [
            {"type": "CNAME", "name": domain, "value": cname_target,
             "ttl": 300},
            {"type": "TXT", "name": f"_uptime-verify.{domain}",
             "value": f"uptime-verify={domain}", "ttl": 300},
        ],
        "notes": "After DNS propagates, SSL is provisioned automatically via Let's Encrypt.",
    }


def cache_key(slug: str, updated_at: datetime) -> str:
    return f"statuspage:{slug}:{updated_at.isoformat()}"


@dataclass
class PageCache:
    """Simple in-memory cache for rendered status pages."""
    _store: dict = None

    def __post_init__(self):
        if self._store is None:
            self._store = {}

    def get(self, key: str) -> str | None:
        return self._store.get(key)

    def set(self, key: str, value: str):
        self._store[key] = value

    def invalidate(self, slug: str):
        for k in list(self._store.keys()):
            if k.startswith(f"statuspage:{slug}:"):
                del self._store[k]
