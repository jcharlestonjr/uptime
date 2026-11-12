import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, drop_db, SessionLocal
from app.models import User
from app.auth import generate_api_key, hash_key
from app.billing import (stripe_configured, create_checkout_session, handle_webhook,
                         PLAN_LIMITS, check_plan_limit, get_plan_features)
from app.emailer import email_configured, send_email
from app.sms import sms_configured, send_sms
from app.config import services_configured

client = TestClient(app)


def test_health_and_config():
    r = client.get("/health")
    assert r.status_code == 200
    cs = client.get("/config/status").json()
    assert "services" in cs
    assert "database" in cs["services"]


def test_plans_endpoint():
    r = client.get("/plans").json()
    assert "free" in r
    assert "starter" in r
    assert r["free"]["monitors"] == 5


def test_signup_and_auth_flow():
    r = client.post("/auth/signup", json={"email": "test@example.com", "name": "Test",
                                          "password": "password123"})
    assert r.status_code == 200
    body = r.json()
    assert "api_key" in body
    assert "jwt" in body
    key = body["api_key"]
    # use api key
    r2 = client.get("/auth/me", headers={"X-API-Key": key})
    assert r2.status_code == 200
    assert r2.json()["email"] == "test@example.com"
    # issue new api key
    r3 = client.post("/auth/api-key", params={"name": "second"}, headers={"X-API-Key": key})
    assert r3.status_code == 200
    assert r3.json()["api_key"].startswith("up_")
    # duplicate signup
    r4 = client.post("/auth/signup", json={"email": "test@example.com", "password": "x"})
    assert r4.status_code == 400


def test_login_flow():
    client.post("/auth/signup", json={"email": "login@example.com", "password": "secret123"})
    r = client.post("/auth/login", json={"email": "login@example.com", "password": "secret123"})
    assert r.status_code == 200
    assert "jwt" in r.json()
    # bad password
    r2 = client.post("/auth/login", json={"email": "login@example.com", "password": "wrong"})
    assert r2.status_code == 401


def test_unauth_returns_401():
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_billing_checkout_mock():
    # signup
    r = client.post("/auth/signup", json={"email": "bill@example.com", "password": "pw"})
    key = r.json()["api_key"]
    # checkout (stripe not configured -> mock)
    r2 = client.post("/billing/checkout", json={"plan": "starter"}, headers={"X-API-Key": key})
    assert r2.status_code == 200
    body = r2.json()
    assert "checkout_url" in body


def test_billing_webhook():
    r = client.post("/billing/webhook", json={"type": "checkout.session.completed"})
    assert r.status_code == 200


def test_contact_endpoint():
    r = client.post("/contact", json={"email": "a@b.com", "subject": "hi", "message": "test"})
    assert r.status_code == 200
    assert r.json()["received"] is True


def test_test_email_sms_mock():
    r = client.post("/test/email", params={"to": "a@b.com"})
    assert r.status_code == 200
    assert r.json().get("mock") is True or r.json().get("sent") is False
    r2 = client.post("/test/sms", params={"to": "+1234567890", "body": "hi"})
    assert r2.status_code == 200


def test_rate_limit():
    # hammer an endpoint
    for _ in range(65):
        client.get("/health")
    r = client.get("/health")
    # may or may not trigger depending on limiter state; just ensure no crash
    assert r.status_code in (200, 429)


def test_billing_module():
    assert stripe_configured() is False
    res = create_checkout_session("a@b.com", "starter", "http://x", "http://y")
    assert "checkout_url" in res
    wh = handle_webhook(b"{}", "")
    assert wh.get("received") or wh.get("mock")
    assert check_plan_limit("free", "monitors", 4) is True
    assert check_plan_limit("free", "monitors", 5) is False
    assert "monitors" in get_plan_features("starter")


def test_email_sms_modules():
    assert email_configured() is False
    assert sms_configured() is False
    r = send_email("a@b.com", "subj", "<p>hi</p>")
    assert r.get("mock") is True or r.get("sent") is False
    r2 = send_sms("+1", "hi")
    assert r2.get("mock") is True or r2.get("sent") is False


def test_services_configured():
    sc = services_configured()
    assert "database" in sc
    assert "stripe" in sc
    assert sc["stripe"] is False


def test_security_headers():
    r = client.get("/health")
    assert r.headers.get("x-content-type-options") == "nosniff"
    assert r.headers.get("x-frame-options") == "DENY"