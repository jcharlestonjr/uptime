"""Email delivery via Resend."""

from __future__ import annotations

from .config import settings


def email_configured() -> bool:
    return bool(settings.resend_api_key)


def send_email(to: str, subject: str, html: str, text: str = None) -> dict:
    if not email_configured():
        return {"sent": False, "mock": True, "to": to, "subject": subject}
    import resend
    resend.api_key = settings.resend_api_key
    params = {"from": settings.email_from, "to": [to], "subject": subject, "html": html}
    if text:
        params["text"] = text
    try:
        result = resend.Emails.send(params)
        return {"sent": True, "id": result.get("id")}
    except Exception as e:
        return {"sent": False, "error": str(e)}


def send_alert_email(to: str, monitor_name: str, status: str, details: str) -> dict:
    subject = f"{'🔴' if status == 'down' else '✅'} {monitor_name} is {status.upper()}"
    html = f"<h2>{monitor_name} is {status}</h2><p>{details}</p>"
    return send_email(to, subject, html)