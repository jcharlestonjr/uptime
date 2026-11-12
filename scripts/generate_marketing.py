"""Generate all marketing content for Uptime Pro."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.seo import SEOGenerator, KEYWORDS, content_calendar
import json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MKT = os.path.join(BASE, "marketing")

# --- SEO Articles (humanized) ---
gen = SEOGenerator()
articles = gen.generate_all()
for a in articles:
    # Humanize: replace AI-sounding phrases
    body = a.body
    body = body.replace("In this guide we'll cover everything you need to know about",
                        "Here's a quick rundown of")
    body = body.replace("studies show that", "in my experience")
    body = body.replace("That's where", "That's exactly what")
    body = body.replace("## Conclusion\n", "## Wrapping up\n")
    body = body.replace("Don't wait for a customer to tell you your site is down.",
                        "Don't find out your site is down from a customer tweet.")
    path = os.path.join(MKT, "seo-articles", f"{a.slug}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"---\ntitle: {a.title}\nmeta_description: {a.meta_description}\nkeyword: {a.keyword}\nslug: {a.slug}\nword_count: {a.word_count}\n---\n\n{body}")
print(f"Generated {len(articles)} SEO articles")

# --- Content Calendar ---
cal = content_calendar(KEYWORDS, posts_per_week=3)
with open(os.path.join(MKT, "seo-articles", "_calendar.json"), "w", encoding="utf-8") as f:
    json.dump(cal, f, indent=2)
print(f"Generated content calendar ({len(cal)} posts)")

# --- Social Media Posts (human, no AI tells) ---
social = """# Social Media Posts

## Twitter/X - Post 1

Just shipped Uptime Pro. Simple uptime monitoring + status pages.

Free tier: 5 monitors, 5-min checks, email alerts. No credit card.

https://uptime-pro.fly.dev

## Twitter/X - Post 2

Why I built this:

1. UptimeRobot's dashboard hasn't changed since 2015
2. Pingdom charges $15/mo for 10 monitors
3. I wanted something that just works

Free tier available.

https://uptime-pro.fly.dev

## Twitter/X - Post 3

Your customers shouldn't be the ones telling you your site is down.

Set up monitoring in 2 minutes:
- Add your URL
- Pick where alerts go
- Done

https://uptime-pro.fly.dev

## Twitter/X - Post 4

Status pages build trust.

When things break (they will), a public status page shows:
- You know about it
- You're fixing it
- You're not hiding anything

Build one in 60 seconds: https://uptime-pro.fly.dev

## LinkedIn

I just launched Uptime Pro - a lightweight uptime monitoring tool with public status pages.

After years of using overpriced, overcomplicated monitoring tools, I built something simple:

- Multi-region HTTP checks (no false positives from one bad node)
- Instant alerts via email, Slack, or webhook
- Branded public status pages
- Free tier, no credit card

If you run a website or API, downtime costs money. Uptime Pro helps you catch it before your customers do.

Try it free: https://uptime-pro.fly.dev

#saas #monitoring #uptime #webdev #indiehacker

## Reddit r/selfhosted

I built a free uptime monitor + status page tool

Hey everyone - I've been working on Uptime Pro, a lightweight uptime monitor.

What it does:
- Multi-region checks every 1-5 min
- Email/Slack/webhook alerts
- Branded public status pages
- Free tier (5 monitors)

I'm a solo dev. Would love feedback. What's missing? What would make you switch from UptimeRobot or Pingdom?

Link: https://uptime-pro.fly.dev

## Reddit r/webdev

Show: Uptime Pro - simple uptime monitoring with status pages

Built this because UptimeRobot's UI feels dated and Pingdom's pricing is steep for small projects.

Does the basics: multi-region HTTP checks, instant alerts, clean public status page.

Free tier: 5 monitors, 5-min checks. Paid from $9/mo.

Tech: Python/FastAPI, Postgres, runs on Fly.io. Happy to answer questions.

https://uptime-pro.fly.dev

## Indie Hackers

Launched Uptime Pro today.

Simple uptime monitoring + public status pages. Free tier with 5 monitors. Paid from $9/mo.

Looking for feedback from the community. What features matter most to you?

https://uptime-pro.fly.dev
"""
with open(os.path.join(MKT, "social", "social-posts.md"), "w", encoding="utf-8") as f:
    f.write(social)
print("Generated 8 social posts (humanized, no mangled emojis)")

# --- Cold Outreach (human, conversational) ---
outreach = """# Cold Outreach Email Sequence

## Email 1 (Day 0)

Subject: Quick question about {company}'s uptime

Hi {name},

How do you currently find out when {company}'s site goes down?

Most teams I talk to either rely on customers complaining or have a clunky setup cobbled together from 3 different tools.

I built Uptime Pro to fix that - multi-region checks, instant Slack/email alerts, and a public status page. Free to start.

Worth a 10-min chat? Or just try it: https://uptime-pro.fly.dev

- James

## Email 2 (Day 3)

Subject: Re: Quick question about {company}'s uptime

Hi {name},

Following up - did you get a chance to look?

Happy to set up monitoring for {company} in 2 minutes if it helps. No credit card needed.

- James

## Email 3 (Day 7)

Subject: Last note

Hi {name},

Last note from me. If {company} ever has an outage you didn't catch in time, that's the moment this matters.

Free tier covers 5 monitors. Takes 2 minutes to set up.

https://uptime-pro.fly.dev

- James
"""
with open(os.path.join(MKT, "outreach", "cold-email-sequence.md"), "w", encoding="utf-8") as f:
    f.write(outreach)
print("Generated cold email sequence (humanized)")

# --- Community Posts (human, no AI tells) ---
community = """# Community Posts

## Reddit r/selfhosted

**I built a free uptime monitor - feedback welcome**

Hey everyone. I've been working on Uptime Pro, a lightweight uptime monitor + status page tool.

What it does:
- Multi-region checks every 1-5 min
- Email/Slack/webhook alerts
- Branded public status pages
- Free tier (5 monitors)

I'm a solo dev. Would love feedback from this community. What's missing? What would make you switch from UptimeRobot or Pingdom?

Link: https://uptime-pro.fly.dev

---

## Reddit r/webdev

**Show: Uptime Pro - simple uptime monitoring with status pages**

Built this because UptimeRobot's UI feels dated and Pingdom's pricing is steep for small projects.

Does the basics: multi-region HTTP checks, instant alerts, clean public status page.

Free tier: 5 monitors, 5-min checks. Paid from $9/mo.

Tech: Python/FastAPI, Postgres, runs on Fly.io. Happy to answer questions.

https://uptime-pro.fly.dev

---

## Hacker News (Show HN)

Show HN: Uptime Pro - Simple uptime monitoring with status pages

I built this because I was tired of UptimeRobot's UI and Pingdom's pricing. Uptime Pro does the basics well: multi-region HTTP checks, instant alerts (email/Slack/webhook), and a clean public status page.

Free tier: 5 monitors, 5-min checks. Paid from $9/mo.

Tech: Python/FastAPI, Postgres, runs on Fly.io. Checker runs in 3 regions.

Happy to answer questions. https://uptime-pro.fly.dev

---

## Product Hunt Tagline

Uptime monitoring + status pages that just work
"""
with open(os.path.join(MKT, "outreach", "community-posts.md"), "w", encoding="utf-8") as f:
    f.write(community)
print("Generated community posts (humanized)")

# --- Product Hunt Launch Kit ---
ph = """# Product Hunt Launch Kit

## Tagline
Uptime monitoring + status pages that just work

## Description
Uptime Pro is a lightweight uptime monitoring tool with public status pages.

Monitor your websites and APIs with multi-region checks, get instant alerts via email, Slack, or webhook, and publish a branded status page for your customers.

Free tier: 5 monitors, 5-minute checks, email alerts. Paid plans from $9/month.

## First Comment
Hey Product Hunt!

I'm James. I built Uptime Pro because I was frustrated with existing uptime monitoring tools. UptimeRobot's UI feels dated, and Pingdom costs $15/mo for basic features.

Uptime Pro focuses on doing the essentials well:
- Multi-region HTTP checks (no false positives from one bad node)
- Instant alerts (email, Slack, webhook)
- Clean, branded public status pages
- Free tier with no credit card required

I'd love your feedback. What features would make this a must-have for you?

Try it free: https://uptime-pro.fly.dev

## Topics
SaaS, Developer Tools, Monitoring, Web Development

## Launch Checklist
- [ ] Schedule launch for Tuesday or Wednesday
- [ ] Prepare 5-10 upvotes from friends/community
- [ ] Have first comment ready
- [ ] Respond to every comment within 1 hour
- [ ] Share on Twitter, LinkedIn, Reddit, Indie Hackers
"""
with open(os.path.join(MKT, "product-hunt", "launch-kit.md"), "w", encoding="utf-8") as f:
    f.write(ph)
print("Generated Product Hunt launch kit")

# --- Landing Page Copy ---
lp = """# Landing Page Copy

## Hero
Headline: Never miss downtime again.
Subheadline: Multi-region uptime monitoring + public status pages. Free to start.
CTA: Start monitoring for free
Secondary: No credit card required

## Features
- Multi-region checks: Monitor from 3 global regions. No false positives from a single bad node.
- Instant alerts: Get notified via email, Slack, or webhook the moment something breaks.
- Public status pages: Branded status pages your customers can check.
- SSL monitoring: Get warned before your SSL certificate expires.
- Response time tracking: Spot slowdowns before they become outages.

## Pricing
Free - $0/mo: 5 monitors, 5-min checks, email alerts, 1 status page
Starter - $9/mo: 25 monitors, 1-min checks, email + Slack, 3 status pages, custom domain
Team - $29/mo: 100 monitors, 30s checks, all alert channels, unlimited status pages
Business - $49/mo: 500 monitors, 30s checks, SMS alerts, priority support, API access

## FAQ
Q: How fast are alerts?
A: Under 60 seconds from failure to notification.

Q: Can I monitor APIs?
A: Yes - any HTTP/HTTPS endpoint.

Q: Is there a free tier?
A: Yes. 5 monitors, 5-minute checks, email alerts. No credit card required.

Q: Can I use a custom domain for my status page?
A: Yes, on Starter plan and above.

## Footer CTA
Ready to stop guessing if your site is up?
Start monitoring for free
"""
with open(os.path.join(MKT, "landing-page", "copy.md"), "w", encoding="utf-8") as f:
    f.write(lp)
print("Generated landing page copy")

# --- Email Sequences (human) ---
welcome = """# Welcome Email Sequence

## Day 0: Welcome to Uptime Pro

Hi {name},

Welcome! Your account is ready. Here's how to get started:

1. Add your first monitor (takes 30 seconds)
2. Set up alert channels (email, Slack, or webhook)
3. Share your status page link

Docs: https://uptime-pro.fly.dev/docs

Reply to this email if you get stuck. I read every one.

- James

## Day 1: Tip - Add a status page

Hi {name},

Did you know you can publish a public status page for your monitors?

Customers appreciate transparency. When things break, a status page shows you're on it.

Set it up: https://uptime-pro.fly.dev/docs

- James

## Day 7: How's it going?

Hi {name},

You've been using Uptime Pro for a week. Any feedback?

What's working? What's missing? Reply to this email - I read every one.

- James
"""
with open(os.path.join(MKT, "email-sequences", "welcome.md"), "w", encoding="utf-8") as f:
    f.write(welcome)

dunning = """# Dunning (Failed Payment) Sequence

## Day 0: Payment failed

Hi {name},

We couldn't process your payment for Uptime Pro. Your monitors are still running, but please update your card to avoid interruption.

Update payment: https://uptime-pro.fly.dev/billing

- James

## Day 3: Action needed

Hi {name},

Your payment is still outstanding. Your monitors will be paused in 4 days if not resolved.

Update payment: https://uptime-pro.fly.dev/billing

- James

## Day 7: Final notice

Hi {name},

Your account has been paused due to failed payment. Your monitors are no longer running.

Update payment to resume: https://uptime-pro.fly.dev/billing

- James
"""
with open(os.path.join(MKT, "email-sequences", "dunning.md"), "w", encoding="utf-8") as f:
    f.write(dunning)
print("Generated welcome + dunning emails (humanized)")

# --- Blog Posts (human) ---
blogs = [
    ("why-uptime-monitoring-matters.md", """# Why Uptime Monitoring Matters

Downtime costs money. Here's how to catch it before your customers do.

## The cost of downtime

Small businesses lose $100-400 per hour of downtime. E-commerce sites lose thousands per minute. And 98% of organizations say a single hour of downtime costs over $100,000.

The worst part? Most businesses don't find out until a customer complains.

## What uptime monitoring does

Uptime monitoring checks if your website or API is reachable and responding correctly. When something breaks, you get alerted instantly - before your customers notice.

## What to look for in an uptime monitor

1. **Multi-region checks** - single-region checks give false positives
2. **Fast alerting** - under 60 seconds from failure to notification
3. **Public status pages** - transparency builds trust
4. **SSL monitoring** - catch expiring certificates before they break
5. **Response time tracking** - spot slowdowns before they become outages

## Getting started

With Uptime Pro, you can set up monitoring in under 2 minutes:
1. Add your URL
2. Choose where alerts go (email, Slack, webhook)
3. Publish a status page

Free tier: 5 monitors, 5-minute checks. No credit card required.

[Try Uptime Pro free](https://uptime-pro.fly.dev)
"""),
    ("uptime-monitor-vs-status-page.md", """# Uptime Monitor vs Status Page: What's the Difference?

Many people confuse these two. Here's the breakdown.

## Uptime Monitor

- **What it does:** Checks if your site is up every 1-5 minutes
- **Who sees it:** Only you and your team
- **Purpose:** Detect problems fast
- **Alerts:** Email, Slack, SMS, webhook

## Status Page

- **What it does:** Shows current status and incident history publicly
- **Who sees it:** Your customers and users
- **Purpose:** Transparency and trust
- **Updates:** Manual or automated

## Why you need both

Your monitor catches problems before customers notice. Your status page communicates during incidents. Together they reduce support tickets and build trust.

## Uptime Pro gives you both

One tool, one price. Monitor your sites and publish a status page.

Free tier includes both.

[Try Uptime Pro free](https://uptime-pro.fly.dev)
"""),
    ("how-to-choose-uptime-monitor.md", """# How to Choose an Uptime Monitor

Not all uptime monitors are created equal. Here's what to look for.

## 1. Check frequency

1-minute checks catch issues fast. 5-minute checks are fine for non-critical sites. Avoid tools that only check every 10+ minutes.

## 2. Multi-region checks

Single-region checks give false positives. Look for 2-3 regions minimum.

## 3. Alert channels

Email is minimum. Slack/Teams for team awareness. Webhooks for custom integrations. SMS for critical alerts.

## 4. Status pages

Public status pages build trust. Custom domains look professional. Incident history shows reliability.

## 5. Pricing

Free tiers should be genuinely useful. Avoid per-monitor pricing that scales badly. Look for flat-rate plans.

## Our recommendation

Uptime Pro offers all of the above with a generous free tier. 5 monitors, 5-minute checks, email alerts, 1 status page - free.

[Try Uptime Pro free](https://uptime-pro.fly.dev)
"""),
]
for filename, body in blogs:
    with open(os.path.join(MKT, "blog-posts", filename), "w", encoding="utf-8") as f:
        f.write(body)
print(f"Generated {len(blogs)} blog posts (humanized)")

print("\n=== All marketing content regenerated (humanized) ===")
print(f"Location: {MKT}")