import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_monitor_full_flow():
    m = client.post("/monitors", json={"name": "Site", "url": "https://example.com",
                                       "regions": ["us-east", "eu-west"]}).json()["id"]
    # up check
    r = client.post(f"/monitors/{m}/check", json={"status_code": 200, "elapsed_ms": 120}).json()
    assert r["status"] == "up"
    # down check (debounced first time -> degraded, not incident)
    r2 = client.post(f"/monitors/{m}/check", json={"status_code": 0, "elapsed_ms": 0,
                                                   "error": "timeout"}).json()
    # with threshold=2, first down is degraded
    assert r2["status"] in ("degraded", "down")
    # second down -> down + incident
    r3 = client.post(f"/monitors/{m}/check", json={"status_code": 0, "elapsed_ms": 0,
                                                   "error": "timeout"}).json()
    assert r3["status"] == "down"
    assert r3["new_incident"] is not None
    # recovery resolves
    r4 = client.post(f"/monitors/{m}/check", json={"status_code": 200, "elapsed_ms": 100}).json()
    incs = client.get(f"/monitors/{m}/incidents").json()
    assert incs[0]["open"] is False
    assert incs[0]["has_post_mortem"] is True
    # post-mortem endpoint
    pm = client.get(f"/monitors/{m}/incidents/{incs[0]['id']}/post-mortem").json()
    assert "Post-Mortem" in pm["post_mortem"]
    # uptime
    u = client.get(f"/monitors/{m}/uptime").json()
    assert "uptime_percent" in u
    assert "mttr_min" in u
    # metrics
    met = client.get(f"/monitors/{m}/metrics").json()
    assert met["total_checks"] >= 4
    # get monitor
    g = client.get(f"/monitors/{m}").json()
    assert g["last_status"] == "up"


def test_status_page_flow():
    m = client.post("/monitors", json={"name": "Site2", "url": "https://example.com"}).json()["id"]
    client.post(f"/monitors/{m}/check", json={"status_code": 200, "elapsed_ms": 100})
    client.post("/status-pages", json={"slug": "acme", "monitor_id": m})
    html = client.get("/status/acme")
    assert html.status_code == 200
    assert "All systems operational" in html.text
    # domain provisioning
    d = client.post("/status-pages/acme/domain", json={"domain": "status.acme.com"}).json()
    assert d["domain"] == "status.acme.com"
    # 404 for unknown
    assert client.get("/status/nope").status_code == 404


def test_seo_endpoints():
    r = client.post("/seo/generate", json={"keywords": ["uptime monitor", "status page"]}).json()
    assert r["count"] == 2
    art = client.get("/seo/article/uptime-monitor").json()
    assert "body" in art
    cal = client.get("/seo/calendar").json()
    assert len(cal) > 0
    diff = client.get("/seo/difficulty/uptime%20monitor%20for%20saas").json()
    assert diff["difficulty"] == "easy"


def test_outreach_endpoints():
    seq = client.post("/outreach/sequence", json={"name": "Bob", "company": "Acme"}).json()
    assert len(seq["sequence"]) == 3
    cp = client.get("/outreach/community-post").json()
    assert "uptime" in cp["post"].lower()
    hn = client.get("/outreach/hn-post").json()
    assert "Show HN" in hn["post"]


def test_lifecycle_emails():
    w = client.get("/emails/welcome/Bob").json()
    d = client.get("/emails/dunning/Bob").json()
    assert len(w["emails"]) == 3
    assert len(d["emails"]) == 3


def test_self_status():
    r = client.get("/self/status").json()
    assert r["status"] == "operational"


def test_billing_webhook():
    r = client.post("/billing/webhook", json={"type": "invoice.paid"}).json()
    assert r["received"] is True


def test_checks_list():
    m = client.post("/monitors", json={"name": "S3", "url": "https://example.com",
                                       "regions": ["us-east"]}).json()["id"]
    client.post(f"/monitors/{m}/check", json={"status_code": 200, "elapsed_ms": 50})
    checks = client.get(f"/monitors/{m}/checks").json()
    assert len(checks) == 1
    assert checks[0]["status"] == "up"


def test_incidents_list():
    m = client.post("/monitors", json={"name": "S4", "url": "https://example.com"}).json()["id"]
    client.post(f"/monitors/{m}/check", json={"status_code": 0, "error": "down"})
    client.post(f"/monitors/{m}/check", json={"status_code": 0, "error": "down"})
    incs = client.get(f"/monitors/{m}/incidents").json()
    assert len(incs) >= 1
    assert incs[0]["open"] is True
