"""Stripe billing integration."""

from __future__ import annotations

from typing import Optional
from .config import settings


PLAN_LIMITS = {
    "free": {"monitors": 5, "interval_min": 5, "regions": 1},
    "starter": {"monitors": 25, "interval_min": 1, "regions": 2},
    "team": {"monitors": 100, "interval_min": 1, "regions": 3},
    "business": {"monitors": 500, "interval_min": 0.5, "regions": 5},
}

PLAN_PRICES = {
    "starter": settings.stripe_price_starter,
    "team": settings.stripe_price_team,
    "business": settings.stripe_price_business,
}


def stripe_configured() -> bool:
    return bool(settings.stripe_secret_key)


def get_stripe():
    if not stripe_configured():
        return None
    import stripe
    stripe.api_key = settings.stripe_secret_key
    return stripe


def create_checkout_session(user_email: str, plan: str, success_url: str, cancel_url: str) -> dict:
    stripe = get_stripe()
    if not stripe:
        return {"error": "Stripe not configured", "mock": True,
                "checkout_url": f"https://checkout.mock/{plan}"}
    price_id = PLAN_PRICES.get(plan)
    if not price_id:
        return {"error": f"Unknown plan {plan}"}
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer_email=user_email,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"plan": plan},
    )
    return {"checkout_url": session.url, "session_id": session.id}


def create_customer_portal(customer_id: str, return_url: str) -> dict:
    stripe = get_stripe()
    if not stripe:
        return {"error": "Stripe not configured", "mock": True,
                "portal_url": "https://billing.mock/portal"}
    session = stripe.billing_portal.Session.create(customer=customer_id, return_url=return_url)
    return {"portal_url": session.url}


def handle_webhook(payload: bytes, sig_header: str) -> dict:
    stripe = get_stripe()
    if not stripe:
        return {"received": True, "mock": True}
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except Exception as e:
        return {"error": str(e)}
    # Handle events
    etype = event["type"]
    if etype == "checkout.session.completed":
        session = event["data"]["object"]
        plan = session.get("metadata", {}).get("plan", "starter")
        return {"event": etype, "plan": plan, "customer": session.get("customer")}
    if etype == "customer.subscription.deleted":
        return {"event": etype, "status": "cancelled"}
    if etype == "invoice.payment_failed":
        return {"event": etype, "status": "payment_failed"}
    return {"event": etype, "received": True}


def check_plan_limit(plan: str, resource: str, current_count: int) -> bool:
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
    limit = limits.get(resource)
    if limit is None:
        return True
    return current_count < limit


def get_plan_features(plan: str) -> dict:
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])