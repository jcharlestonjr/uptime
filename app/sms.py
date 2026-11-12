"""SMS delivery via Twilio."""

from __future__ import annotations

from .config import settings


def sms_configured() -> bool:
    return bool(settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_from_number)


def send_sms(to: str, body: str) -> dict:
    if not sms_configured():
        return {"sent": False, "mock": True, "to": to}
    from twilio.rest import Client
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    try:
        msg = client.messages.create(body=body, from_=settings.twilio_from_number, to=to)
        return {"sent": True, "sid": msg.sid}
    except Exception as e:
        return {"sent": False, "error": str(e)}