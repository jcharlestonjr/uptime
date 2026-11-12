import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app.core import Monitor, CheckResult, Incident, RegionQuorum
from app.checker import Checker
from app.alerts import AlertDispatcher
from app.incidents import IncidentManager
from app.statuspage import render_status_page, custom_domain_instructions, PageCache
from app.seo import SEOGenerator, content_calendar, keyword_difficulty
from app.outreach import OutreachEngine, LifecycleEmails


def test_region_quorum_down():
    q = RegionQuorum(regions=["a", "b", "c"], quorum=2)
    assert q.decide({"a": "down", "b": "down", "c": "up"}) == "down"
    assert q.decide({"a": "down", "b": "up", "c": "up"}) == "up"
    assert q.decide({"a": "degraded", "b": "up", "c": "up"}) == "degraded"


def test_checker_debounce():
    import asyncio
    checker = Checker(retries=0, backoff_s=0, concurrency=10)

    async def fetcher_factory(region):
        async def f(url, timeout):
            return 0, 0.0, "timeout"
        return f

    async def run():
        m = Monitor(id="m1", name="S", url="https://x.com", regions=["us-east"],
                    consecutive_failures_threshold=2)
        o1 = await checker.check_monitor(m, fetcher_factory)
        assert o1.quorum_status == "degraded"  # first failure debounced
        o2 = await checker.check_monitor(m, fetcher_factory)
        assert o2.quorum_status == "down"  # second failure -> down
        # recovery
        async def ok_factory(region):
            async def f(url, timeout):
                return 200, 100.0, None
            return f
        o3 = await checker.check_monitor(m, ok_factory)
        assert o3.quorum_status == "up"

    asyncio.run(run())


def test_alert_dispatcher_cooldown():
    disp = AlertDispatcher(cooldown_min=5)
    m = Monitor(id="m1", name="S", url="https://x.com")
    inc = Incident(id="i1", monitor_id="m1", started_at=datetime.utcnow(), cause="down")
    now = datetime.utcnow()
    assert disp.should_alert(m, inc, now=now) is True
    disp.mark_sent("m1", now=now)
    assert disp.should_alert(m, inc, now=now) is False
    later = now + timedelta(minutes=10)
    assert disp.should_alert(m, inc, now=later) is True


def test_alert_render():
    disp = AlertDispatcher()
    m = Monitor(id="m1", name="Site", url="https://x.com")
    inc = Incident(id="i1", monitor_id="m1", started_at=datetime.utcnow(), cause="timeout")
    r = disp.render_down(m, inc, ["us-east"])
    assert "Site" in r["email"]
    assert "timeout" in r["slack"]
    alerts = disp.build_alerts(m, inc, "down", ["us-east"])
    assert len(alerts) == len(m.alert_channels)


def test_escalate():
    disp = AlertDispatcher()
    m = Monitor(id="m1", name="S", url="https://x.com", alert_channels=["email"])
    now = datetime.utcnow()
    inc = Incident(id="i1", monitor_id="m1", started_at=now - timedelta(minutes=45), cause="down")
    acts = disp.escalate(inc, m, now=now)
    assert "add_sms_channel" in acts


def test_incident_manager_postmortem():
    mgr = IncidentManager()
    m = Monitor(id="m1", name="S", url="https://x.com")
    now = datetime.utcnow()
    inc = mgr.open_incident(m, "timeout", now)
    checks = [CheckResult(monitor_id="m1", region="us-east", timestamp=now,
                         status="down", response_time_ms=0, error="timeout")]
    mgr.resolve_incident(inc, now + timedelta(minutes=5), checks=checks)
    assert inc.post_mortem != ""
    assert "Post-Mortem" in inc.post_mortem
    assert "timeout" in inc.post_mortem
    assert inc.open is False


def test_incident_mttr():
    mgr = IncidentManager()
    m = Monitor(id="m1", name="S", url="https://x.com")
    now = datetime.utcnow()
    i1 = mgr.open_incident(m, "x", now)
    mgr.resolve_incident(i1, now + timedelta(minutes=10))
    assert mgr.mttr("m1") == 10.0
    assert mgr.incident_frequency("m1", 30) == 1


def test_status_page_render():
    html = render_status_page(title="Acme", current="up", uptime_24h=99.9,
                              uptime_7d=99.95, avg_ms=120.0, incidents=[])
    assert "All systems operational" in html
    assert "99.9" in html
    assert "Uptime Pro" in html


def test_custom_domain_instructions():
    d = custom_domain_instructions("status.acme.com")
    assert d["domain"] == "status.acme.com"
    assert len(d["steps"]) == 2
    assert d["steps"][0]["type"] == "CNAME"


def test_page_cache():
    c = PageCache()
    c.set("k1", "v1")
    assert c.get("k1") == "v1"
    c.invalidate("slug")  # no-op for different key
    assert c.get("k1") == "v1"


def test_seo_generator():
    gen = SEOGenerator()
    art = gen.generate("uptime monitor")
    assert art.slug == "uptime-monitor"
    assert "uptime monitor" in art.body.lower()
    assert art.word_count > 100
    all_arts = gen.generate_all(["uptime monitor", "status page"])
    assert len(all_arts) == 2


def test_content_calendar():
    cal = content_calendar(["uptime monitor", "status page"], posts_per_week=2)
    assert len(cal) == 2
    assert "date" in cal[0]
    assert "difficulty" in cal[0]


def test_keyword_difficulty():
    assert keyword_difficulty("uptime monitor for saas apps") == "easy"
    assert keyword_difficulty("uptime") == "hard"


def test_outreach_sequence():
    eng = OutreachEngine()
    seq = eng.render_sequence("Bob", "Acme")
    assert len(seq) == 3
    assert "Acme" in seq[0]["body"]
    assert seq[0]["day"] == 0
    assert "uptime" in eng.community_post("https://x.com").lower()


def test_lifecycle_emails():
    lc = LifecycleEmails()
    w = lc.welcome("Bob")
    d = lc.dunning("Bob")
    assert len(w) == 3
    assert len(d) == 3
    assert "Bob" in w[0]["body"]
    assert "Bob" in d[0]["body"]
