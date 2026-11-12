"""Production endpoints: auth, billing, config, contact. Imported by main."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .auth import get_current_user, create_user, issue_api_key, create_jwt
from .billing import create_checkout_session, create_customer_portal, handle_webhook, get_plan_features
from .config import services_configured, settings
from .posters.devto import devto_configured
from .posters.hashnode import hashnode_configured
from .posters.reddit import reddit_configured
from .emailer import send_email, email_configured
from .sms import send_sms, sms_configured


class SignupIn(BaseModel):
    email: str
    name: str = None
    password: str = None


class LoginIn(BaseModel):
    email: str
    password: str


class CheckoutIn(BaseModel):
    plan: str
    success_url: str = "https://uptimepro.app/success"
    cancel_url: str = "https://uptimepro.app/cancel"


def register(app):
    @app.post("/auth/signup")
    def signup(req: SignupIn, db: Session = Depends(get_db)):
        existing = db.query(User).filter(User.email == req.email).first()
        if existing:
            raise HTTPException(400, "Email already registered")
        user = create_user(db, req.email, req.name, req.password)
        key = issue_api_key(db, user)
        token = create_jwt(user)
        return {"user_id": user.id, "email": user.email, "api_key": key, "jwt": token}

    @app.post("/auth/login")
    def login(req: LoginIn, db: Session = Depends(get_db)):
        user = db.query(User).filter(User.email == req.email).first()
        if not user or not user.password_hash:
            raise HTTPException(401, "Invalid credentials")
        import bcrypt
        if not bcrypt.checkpw(req.password.encode(), user.password_hash.encode()):
            raise HTTPException(401, "Invalid credentials")
        token = create_jwt(user)
        return {"user_id": user.id, "email": user.email, "jwt": token}

    @app.get("/auth/me")
    def me(user: User = Depends(get_current_user)):
        return {"id": user.id, "email": user.email, "name": user.name}

    @app.post("/auth/api-key")
    def new_api_key(name: str = "default", user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
        key = issue_api_key(db, user, name)
        return {"api_key": key}

    @app.post("/billing/checkout")
    def billing_checkout(req: CheckoutIn, user: User = Depends(get_current_user)):
        return create_checkout_session(user.email, req.plan, req.success_url, req.cancel_url)

    @app.post("/billing/portal")
    def billing_portal(return_url: str = "https://uptimepro.app/billing",
                      user: User = Depends(get_current_user)):
        # In prod, look up stripe_customer_id from subscription
        return create_customer_portal("", return_url)

    @app.post("/billing/webhook")
    async def billing_webhook(request: Request):
        body = await request.body()
        sig = request.headers.get("stripe-signature", "")
        return handle_webhook(body, sig)

    @app.get("/config/status")
    def config_status():
        return {"services": services_configured(), "env": settings.env}

    @app.get("/posters/status")
    def poster_status():
        return {
            "devto": devto_configured(),
            "hashnode": hashnode_configured(),
            "reddit": reddit_configured(),
        }

    @app.get("/plans")
    def plans():
        return {k: get_plan_features(k) for k in ["free", "starter", "team", "business"]}

    @app.post("/contact")
    def contact(payload: dict):
        # Send to founder
        send_email("founder@uptimepro.app", f"Contact: {payload.get('subject', '')}",
                   f"<p>From: {payload.get('email')}</p><p>{payload.get('message')}</p>")
        return {"received": True}

    @app.post("/test/email")
    def test_email(to: str):
        return send_email(to, "Test from Uptime Pro", "<p>If you got this, email works.</p>")

    @app.post("/test/sms")
    def test_sms(to: str, body: str = "Test from Uptime Pro"):
        return send_sms(to, body)