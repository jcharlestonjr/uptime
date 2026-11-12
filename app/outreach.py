"""Cold-outreach email sequences for dev/SaaS founders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EmailStep:
    day: int
    subject: str
    body: str


COLD_SEQUENCE = [
    EmailStep(0, "Quick question about {company}'s uptime",
              "Hi {name},\n\nI noticed {company} serves customers online. Quick question: "
              "how do you currently find out when your site goes down?\n\nMost teams I talk to "
              "either rely on customers complaining or have a clunky setup. I built Uptime Pro "
              "to fix that — multi-region checks, instant Slack/email alerts, and a public "
              "status page, free to start.\n\nWorth a 10-min chat? Or just try it: {signup_url}\n\n— {sender}"),
    EmailStep(3, "Re: Quick question about {company}'s uptime",
              "Hi {name},\n\nFollowing up — did you get a chance to look? Happy to set up "
              "monitoring for {company} in 2 minutes if it helps.\n\n— {sender}"),
    EmailStep(7, "Last note — free uptime monitoring",
              "Hi {name},\n\nLast note from me. If {company} ever has an outage you didn't catch "
              "in time, that's the moment this matters. Free tier covers 5 monitors.\n\n"
              "{signup_url}\n\n— {sender}"),
]

DEV_COMMUNITY_POST = """**I built a free uptime monitor — feedback welcome**

Hey everyone — I've been working on Uptime Pro, a lightweight uptime monitor + status page tool.

Features:
- Multi-region checks every 1-5 min
- Email/Slack/webhook alerts
- Branded public status pages with custom domains
- Free tier (5 monitors)

I'm a solo dev and would love feedback from this community. What's missing? What would make you switch from UptimeRobot/Pingdom?

Link: {url}
"""

HACKERNEWS_POST = """Show HN: Uptime Pro – Simple uptime monitoring with status pages

I built this because I was tired of UptimeRobot's UI and Pingdom's pricing. Uptime Pro does
the basics well: multi-region HTTP checks, instant alerts (email/Slack/webhook), and a clean
public status page you can put on a custom domain.

Free tier: 5 monitors, 5-min checks. Paid from $9/mo.

Tech: Python/FastAPI, Postgres, runs on Fly.io. Checker runs in 3 regions.

Happy to answer questions. {url}"""

PRODUCTHUNT_TAGLINE = "Uptime monitoring + status pages that just work"


class OutreachEngine:
    def __init__(self, sender: str = "Founder", signup_url: str = "https://uptimepro.app/signup"):
        self.sender = sender
        self.signup_url = signup_url

    def render_sequence(self, name: str, company: str) -> list[dict]:
        out = []
        for step in COLD_SEQUENCE:
            out.append({
                "day": step.day,
                "subject": step.subject.format(company=company, name=name, sender=self.sender,
                                              signup_url=self.signup_url),
                "body": step.body.format(company=company, name=name, sender=self.sender,
                                         signup_url=self.signup_url),
            })
        return out

    def community_post(self, url: str) -> str:
        return DEV_COMMUNITY_POST.format(url=url)

    def hn_post(self, url: str) -> str:
        return HACKERNEWS_POST.format(url=url)


DUNNING_SEQUENCE = [
    EmailStep(0, "Payment failed for Uptime Pro",
              "Hi {name},\n\nWe couldn't process your payment for Uptime Pro. "
              "Please update your card to keep your monitors running.\n\n"
              "Update payment: {billing_url}\n\n— Uptime Pro"),
    EmailStep(3, "Action needed: Uptime Pro payment",
              "Hi {name},\n\nYour payment is still outstanding. Your monitors will be "
              "paused in 4 days if not resolved.\n\nUpdate payment: {billing_url}\n\n— Uptime Pro"),
    EmailStep(7, "Final notice: Uptime Pro account paused",
              "Hi {name},\n\nYour account has been paused due to failed payment. "
              "Your monitors are no longer running. Update payment to resume.\n\n"
              "{billing_url}\n\n— Uptime Pro"),
]

WELCOME_SEQUENCE = [
    EmailStep(0, "Welcome to Uptime Pro 🎉",
              "Hi {name},\n\nWelcome! Your account is ready. Here's how to get started:\n"
              "1. Add your first monitor\n2. Set up alert channels\n3. Share your status page\n\n"
              "Docs: {docs_url}\n\n— Uptime Pro"),
    EmailStep(1, "Tip: Add a status page",
              "Hi {name},\n\nDid you know you can publish a public status page for your "
              "monitors? Customers love transparency.\n\nSet it up: {status_url}\n\n— Uptime Pro"),
    EmailStep(7, "How's it going?",
              "Hi {name},\n\nYou've been using Uptime Pro for a week. Any feedback? "
              "Reply to this email — I read every one.\n\n— Uptime Pro"),
]


class LifecycleEmails:
    def __init__(self, billing_url: str = "https://uptimepro.app/billing",
                 docs_url: str = "https://uptimepro.app/docs",
                 status_url: str = "https://uptimepro.app/status"):
        self.billing_url = billing_url
        self.docs_url = docs_url
        self.status_url = status_url

    def dunning(self, name: str) -> list[dict]:
        return [{"day": s.day,
                 "subject": s.subject.format(name=name),
                 "body": s.body.format(name=name, billing_url=self.billing_url)}
                for s in DUNNING_SEQUENCE]

    def welcome(self, name: str) -> list[dict]:
        return [{"day": s.day,
                 "subject": s.subject.format(name=name),
                 "body": s.body.format(name=name, docs_url=self.docs_url,
                                       status_url=self.status_url)}
                for s in WELCOME_SEQUENCE]
