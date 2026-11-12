"""SEO content generator: template-based articles targeting uptime keywords."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

KEYWORDS = [
    "uptime monitor",
    "website uptime monitoring",
    "status page",
    "website monitoring tool",
    "free uptime monitor",
    "uptime robot alternative",
    "statuspage alternative",
    "server monitoring",
    "api monitoring",
    "ssl certificate monitoring",
    "downtime alert",
    "website down alert",
    "pingdom alternative",
    "uptime kuma alternative",
    "public status page",
]

ARTICLE_TEMPLATE = """# {title}

> {meta_description}

## Introduction

If you run a website, API, or online service, you already know that **downtime costs money**.
Studies show that even a few minutes of downtime can cost small businesses hundreds of dollars
in lost revenue and damaged reputation. That's where **{keyword}** comes in.

In this guide we'll cover everything you need to know about {keyword}: what it is, why it matters,
how to choose the right tool, and how to set it up in under 5 minutes.

## What is {keyword}?

{keyword_cap} is the practice of continuously checking whether your website or service is
reachable and responding correctly. A good {keyword} tool will:

- Check your endpoints every 1–5 minutes from multiple global regions
- Alert you instantly via email, Slack, SMS, or webhook when something breaks
- Track response times so you can spot slowdowns before they become outages
- Provide a public status page your customers can check

## Why {keyword} matters

1. **Revenue protection** — every minute of downtime is lost sales.
2. **Customer trust** — a public status page shows transparency.
3. **SEO** — Google penalizes slow/unavailable sites.
4. **SLA compliance** — many B2B contracts require 99.9% uptime.

## How to choose a {keyword} tool

Look for these features:

- **Multi-region checks** — avoid false positives from a single bad node
- **Fast alerting** — under 60 seconds from failure to notification
- **Status pages** — branded, public, with incident history
- **Integrations** — Slack, PagerDuty, webhooks, email
- **Fair pricing** — free tier for small projects, paid for teams

## Getting started with Uptime Pro

Uptime Pro gives you all of the above in a simple, affordable package:

- Free tier: 5 monitors, 5-minute intervals
- Paid plans from $9/month
- Multi-region checks out of the box
- Branded status pages with custom domains
- Email, Slack, and webhook alerts

[Start monitoring for free →](https://uptimepro.app/signup)

## Conclusion

Don't wait for a customer to tell you your site is down. Set up {keyword} today and get
peace of mind. With tools like Uptime Pro, it takes less than 5 minutes.

---

*Keywords: {keyword}, uptime monitoring, status page, website monitoring, downtime alert*
"""


@dataclass
class Article:
    slug: str
    title: str
    keyword: str
    meta_description: str
    body: str
    word_count: int


class SEOGenerator:
    def __init__(self, brand: str = "Uptime Pro", base_url: str = "https://uptimepro.app"):
        self.brand = brand
        self.base_url = base_url

    def make_title(self, keyword: str) -> str:
        return f"The Complete Guide to {keyword.title()} (2026)"

    def make_slug(self, keyword: str) -> str:
        return keyword.lower().replace(" ", "-")

    def make_meta(self, keyword: str) -> str:
        return (f"Learn everything about {keyword}: what it is, why it matters, and how to "
                f"choose the best {keyword} tool for your website or API.")

    def generate(self, keyword: str) -> Article:
        title = self.make_title(keyword)
        slug = self.make_slug(keyword)
        meta = self.make_meta(keyword)
        body = ARTICLE_TEMPLATE.format(
            title=title,
            meta_description=meta,
            keyword=keyword,
            keyword_cap=keyword.capitalize(),
        )
        return Article(slug=slug, title=title, keyword=keyword,
                       meta_description=meta, body=body, word_count=len(body.split()))

    def generate_all(self, keywords: list[str] | None = None) -> list[Article]:
        kws = keywords or KEYWORDS
        return [self.generate(k) for k in kws]

    def generate_landing(self, keyword: str) -> str:
        """Generate a short landing-page hero section for a keyword."""
        return (f"# {keyword.title()}\n\n"
                f"Monitor your website and API uptime with {self.brand}. "
                f"Get instant alerts when things break. Free tier available.\n\n"
                f"[Start free →]({self.base_url}/signup)")


def keyword_difficulty(keyword: str) -> str:
    """Rough heuristic: longer tail = easier."""
    words = len(keyword.split())
    if words >= 4:
        return "easy"
    if words == 3:
        return "medium"
    return "hard"


def content_calendar(keywords: list[str], posts_per_week: int = 3) -> list[dict]:
    """Build a publishing schedule."""
    from datetime import date, timedelta
    schedule = []
    d = date.today()
    for i, kw in enumerate(keywords):
        week = i // posts_per_week
        day_offset = (i % posts_per_week) * 2
        pub_date = d + timedelta(weeks=week, days=day_offset)
        schedule.append({"date": pub_date.isoformat(), "keyword": kw,
                         "difficulty": keyword_difficulty(kw)})
    return schedule
