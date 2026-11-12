"""FastAPI app for Uptime Pro (production-grade)."""

from __future__ import annotations

from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .core import Monitor, CheckResult
from .checker import Checker
from .alerts import AlertDispatcher
from .incidents import IncidentManager
from .statuspage import render_status_page, custom_domain_instructions, PageCache
from .seo import SEOGenerator, content_calendar, keyword_difficulty
from .outreach import OutreachEngine, LifecycleEmails
from .store import store
from .prod_endpoints import register as register_prod
from .middleware import SecurityHeadersMiddleware, RequestLoggingMiddleware
from .rl_middleware import RateLimitMiddleware
from .auth import get_current_user, create_user, issue_api_key, create_jwt
from .billing import (create_checkout_session, create_customer_portal,
                      handle_webhook, get_plan_features)
from .emailer import send_email, email_configured
from .sms import send_sms, sms_configured
from .config import settings, services_configured
from .database import init_db

app = FastAPI(title="Uptime Pro", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_methods=["*"], allow_headers=["*"])
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

@app.on_event("startup")
def _startup():
    init_db()

checker = Checker(retries=2, backoff_s=0.5, concurrency=50)
page_cache = PageCache()

# Register production endpoints (auth, billing, config, contact)
register_prod(app)


# ---------- helpers ----------
def _uptime_percent(checks, window_min, now=None):
    now = now or datetime.utcnow()
    from datetime import timedelta
    cutoff = now - timedelta(minutes=window_min)
    relevant = [c for c in checks if c.timestamp >= cutoff]
    if not relevant:
        return 100.0
    up = sum(1 for c in relevant if c.status == "up")
    return round(100.0 * up / len(relevant), 2)


def _avg_ms(checks, window_min, now=None):
    now = now or datetime.utcnow()
    from datetime import timedelta
    cutoff = now - timedelta(minutes=window_min)
    relevant = [c for c in checks if c.timestamp >= cutoff and c.status == "up"]
    if not relevant:
        return 0.0
    return round(sum(c.response_time_ms for c in relevant) / len(relevant), 1)


# ---------- schemas ----------
class MonitorIn(BaseModel):
    name: str
    url: str
    interval_min: int = 5
    timeout_s: float = 10.0
    expected_status: int = 200
    regions: list[str] = ["us-east", "eu-west"]
    alert_channels: list[str] = ["email"]
    cooldown_min: int = 5
    consecutive_failures_threshold: int = 2


class CheckIn(BaseModel):
    region: str = "us-east"
    status_code: int = 200
    elapsed_ms: float = 120.0
    error: str | None = None
    now: str | None = None


class StatusPageIn(BaseModel):
    slug: str
    monitor_id: str
    title: str | None = None


class DomainIn(BaseModel):
    domain: str


class SeoGenIn(BaseModel):
    keywords: list[str] | None = None


class OutreachIn(BaseModel):
    name: str
    company: str


# ---------- health ----------
@app.get("/health")
def health():
    return {"status": "ok", "service": "uptime-pro", "version": "1.0.0"}


# ---------- monitors ----------
@app.post("/monitors")
def create_monitor(req: MonitorIn):
    mid = store.add_monitor(**req.model_dump())
    return {"id": mid}


@app.get("/monitors")
def list_monitors():
    return [{"id": m.id, "name": m.name, "url": m.url, "active": m.active,
             "regions": m.regions} for m in store.monitors.values()]


@app.get("/monitors/{mid}")
def get_monitor(mid: str):
    m = store.get_monitor(mid)
    if not m:
        raise HTTPException(404, "Monitor not found")
    checks = store.get_checks(mid)
    return {"id": m.id, "name": m.name, "url": m.url, "active": m.active,
            "uptime_24h": _uptime_percent(checks, 1440),
            "uptime_7d": _uptime_percent(checks, 10080),
            "avg_ms_24h": _avg_ms(checks, 1440),
            "last_status": checks[-1].status if checks else "unknown",
            "open_incidents": len(store.incident_manager.open_for(mid) and [1] or [])}


@app.post("/monitors/{mid}/check")
async def run_a_check(mid: str, req: CheckIn):
    m = store.get_monitor(mid)
    if not m:
        raise HTTPException(404, "Monitor not found")

    async def fetcher_factory(region):
        sc, el, err = req.status_code, req.elapsed_ms, req.error
        async def f(url, timeout):
            return sc, el, err
        return f

    now = datetime.fromisoformat(req.now) if req.now else None
    outcome = await checker.check_monitor(m, fetcher_factory, now=now)
    for r in outcome.region_results.values():
        store.record_check(r)

    # incident management
    inc_mgr = store.incident_manager
    open_inc = inc_mgr.open_for(mid)
    new_incident = None
    alerts = []
    if outcome.quorum_status == "down":
        if open_inc is None:
            new_incident = inc_mgr.open_incident(m, outcome.region_results[list(outcome.region_results)[0]].error or "down",
                                                started_at=outcome.timestamp)
            store.add_incident(new_incident)
            regions_down = [r for r, c in outcome.region_results.items() if c.status == "down"]
            if store.alert_dispatcher.should_alert(m, new_incident, now=outcome.timestamp):
                alerts = store.alert_dispatcher.build_alerts(m, new_incident, "down", regions_down)
                store.alert_dispatcher.mark_sent(mid, now=outcome.timestamp)
                new_incident.notified = True
    else:
        if open_inc is not None:
            checks = store.get_checks(mid)
            inc_mgr.resolve_incident(open_inc, resolved_at=outcome.timestamp, checks=checks)
            alerts = store.alert_dispatcher.build_alerts(m, open_inc, "up", [])
            store.alert_dispatcher.mark_sent(mid, now=outcome.timestamp)

    # escalation
    escalations = []
    if open_inc and open_inc.open:
        escalations = store.alert_dispatcher.escalate(open_inc, m, now=outcome.timestamp)

    return {
        "status": outcome.quorum_status,
        "region_results": {r: c.status for r, c in outcome.region_results.items()},
        "failure_count": checker.failure_count(mid),
        "new_incident": new_incident.id if new_incident else None,
        "alerts_sent": len(alerts),
        "escalations": escalations,
    }


@app.get("/monitors/{mid}/checks")
def list_checks(mid: str, limit: int = 50):
    checks = store.get_checks(mid)[-limit:]
    return [{"timestamp": c.timestamp.isoformat(), "region": c.region,
             "status": c.status, "response_time_ms": c.response_time_ms,
             "status_code": c.status_code, "error": c.error} for c in checks]


@app.get("/monitors/{mid}/incidents")
def list_incidents(mid: str):
    return [{"id": i.id, "started_at": i.started_at.isoformat(),
             "resolved_at": i.resolved_at.isoformat() if i.resolved_at else None,
             "duration_min": i.duration_min, "open": i.open, "cause": i.cause,
             "has_post_mortem": bool(i.post_mortem)} for i in store.incidents_for(mid)]


@app.get("/monitors/{mid}/incidents/{iid}/post-mortem")
def get_post_mortem(mid: str, iid: str):
    inc = next((i for i in store.incidents_for(mid) if i.id == iid), None)
    if not inc:
        raise HTTPException(404, "Incident not found")
    if not inc.post_mortem:
        checks = store.get_checks(mid)
        inc.post_mortem = store.incident_manager.draft_post_mortem(inc, checks)
    return {"incident_id": inc.id, "post_mortem": inc.post_mortem}


@app.get("/monitors/{mid}/uptime")
def uptime(mid: str, window_min: int = 1440):
    m = store.get_monitor(mid)
    if not m:
        raise HTTPException(404, "Monitor not found")
    checks = store.get_checks(mid)
    up = _uptime_percent(checks, window_min)
    return {"uptime_percent": up, "avg_response_ms": _avg_ms(checks, window_min),
            "sla_breach": store.incident_manager.sla_breach(mid, up),
            "mttr_min": store.incident_manager.mttr(mid),
            "incident_count_30d": store.incident_manager.incident_frequency(mid, 30)}


@app.get("/monitors/{mid}/metrics")
def metrics(mid: str):
    m = store.get_monitor(mid)
    if not m:
        raise HTTPException(404, "Monitor not found")
    checks = store.get_checks(mid)
    return {
        "total_checks": len(checks),
        "up_checks": sum(1 for c in checks if c.status == "up"),
        "down_checks": sum(1 for c in checks if c.status == "down"),
        "avg_ms_24h": _avg_ms(checks, 1440),
        "p95_ms": _percentile([c.response_time_ms for c in checks if c.status == "up"], 95),
        "mttr_min": store.incident_manager.mttr(mid),
    }


def _percentile(vals, p):
    if not vals:
        return 0.0
    s = sorted(vals)
    k = (len(s) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return round(s[f], 1)
    return round(s[f] + (s[c] - s[f]) * (k - f), 1)


# ---------- status pages ----------
@app.post("/status-pages")
def create_status_page(req: StatusPageIn):
    m = store.get_monitor(req.monitor_id)
    if not m:
        raise HTTPException(404, "Monitor not found")
    store.create_status_page(req.slug, req.monitor_id)
    return {"slug": req.slug, "url": f"/status/{req.slug}"}


@app.get("/status/{slug}", response_class=HTMLResponse)
def status_page(slug: str):
    m = store.status_page_monitor(slug)
    if not m:
        raise HTTPException(404, "Status page not found")
    checks = store.get_checks(m.id)
    incidents = store.incidents_for(m.id)
    current = checks[-1].status if checks else "up"
    uptime_24 = _uptime_percent(checks, 1440)
    uptime_7 = _uptime_percent(checks, 10080)
    avg = _avg_ms(checks, 1440)
    inc_data = [{"cause": i.cause, "started_at": i.started_at.isoformat(),
                 "resolved_at": i.resolved_at.isoformat() if i.resolved_at else None,
                 "duration_min": i.duration_min} for i in incidents[-5:]]
    html = render_status_page(title=m.name, current=current, uptime_24h=uptime_24,
                             uptime_7d=uptime_7, avg_ms=avg, incidents=inc_data,
                             primary="#2563eb")
    return HTMLResponse(content=html)


@app.post("/status-pages/{slug}/domain")
def provision_domain(slug: str, req: DomainIn):
    m = store.status_page_monitor(slug)
    if not m:
        raise HTTPException(404, "Status page not found")
    return custom_domain_instructions(req.domain)


# ---------- SEO ----------
@app.post("/seo/generate")
def seo_generate(req: SeoGenIn):
    gen = SEOGenerator()
    articles = gen.generate_all(req.keywords)
    return {"count": len(articles),
            "articles": [{"slug": a.slug, "title": a.title, "keyword": a.keyword,
                          "word_count": a.word_count, "meta_description": a.meta_description}
                         for a in articles]}


@app.get("/seo/article/{slug}")
def seo_article(slug: str):
    gen = SEOGenerator()
    # find keyword by slug
    kw = slug.replace("-", " ")
    article = gen.generate(kw)
    return {"slug": article.slug, "title": article.title, "body": article.body}


@app.get("/seo/calendar")
def seo_calendar(posts_per_week: int = 3):
    from .seo import content_calendar, KEYWORDS
    return content_calendar(KEYWORDS, posts_per_week)


@app.get("/seo/difficulty/{keyword}")
def seo_difficulty(keyword: str):
    return {"keyword": keyword, "difficulty": keyword_difficulty(keyword)}


# ---------- outreach ----------
@app.post("/outreach/sequence")
def outreach_sequence(req: OutreachIn):
    engine = OutreachEngine()
    return {"sequence": engine.render_sequence(req.name, req.company)}


@app.get("/outreach/community-post")
def community_post(url: str = "https://uptimepro.app"):
    engine = OutreachEngine()
    return {"post": engine.community_post(url)}


@app.get("/outreach/hn-post")
def hn_post(url: str = "https://uptimepro.app"):
    engine = OutreachEngine()
    return {"post": engine.hn_post(url)}


# ---------- lifecycle emails ----------
@app.get("/emails/welcome/{name}")
def welcome_emails(name: str):
    return {"emails": LifecycleEmails().welcome(name)}


@app.get("/emails/dunning/{name}")
def dunning_emails(name: str):
    return {"emails": LifecycleEmails().dunning(name)}


# ---------- billing webhook ----------
@app.post("/billing/webhook")
def billing_webhook(payload: dict):
    # Mock Stripe webhook: upgrade/downgrade monitor limits
    return {"received": True, "event": payload.get("type", "unknown")}


# ---------- self-monitoring ----------
@app.get("/self/status")
def self_status():
    return {"service": "uptime-pro", "status": "operational",
            "monitors": len(store.monitors), "checks": sum(len(v) for v in store.checks.values())}
