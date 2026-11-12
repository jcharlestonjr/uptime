"""Generate all marketing content for Uptime Pro."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.seo import SEOGenerator, KEYWORDS, content_calendar, keyword_difficulty
from app.outreach import OutreachEngine, LifecycleEmails, COLD_SEQUENCE, DEV_COMMUNITY_POST, HACKERNEWS_POST, PRODUCTHUNT_TAGLINE
import json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MKT = os.path.join(BASE, "marketing")

# --- SEO Articles ---
gen = SEOGenerator()
articles = gen.generate_all()
for a in articles:
    path = os.path.join(MKT, "seo-articles", f"{a.slug}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"---\ntitle: {a.title}\nmeta_description: {a.meta_description}\nkeyword: {a.keyword}\nslug: {a.slug}\nword_count: {a.word_count}\n---\n\n{a.body}")
print(f"Generated {len(articles)} SEO articles")

# --- Content Calendar ---
cal = content_calendar(KEYWORDS, posts_per_week=3)
with open(os.path.join(MKT, "seo-articles", "_calendar.json"), "w", encoding="utf-8") as f:
    json.dump(cal, f, indent=2)
print(f"Generated content calendar ({len(cal)} posts)")

# --- Outreach Emails ---
engine = OutreachEngine(sender="James", signup_url="https://uptime-pro.fly.dev/auth/signup")
seq = engine.render_sequence("Founder", "YourCompany")
with open(os.path.join(MKT, "outreach", "cold-email-sequence.md"), "w", encoding="utf-8") as f:
    f.write("# Cold Outreach Email Sequence\n\n")
    for step in seq:
        f.write(f"## Day {step['day']}: {step['subject']}\n\n{step['body']}\n\n---\n\n")
print("Generated cold email sequence")

# Community posts
with open(os.path.join(MKT, "outreach", "community-posts.md"), "w", encoding="utf-8") as f:
    f.write("# Community Posts\n\n")
    f.write("## Reddit (r/selfhosted, r/webdev, r/SaaS)\n\n")
    f.write(engine.community_post("https://uptime-pro.fly.dev") + "\n\n---\n\n")
    f.write("## Hacker News (Show HN)\n\n")
    f.write(engine.hn_post("https://uptime-pro.fly.dev") + "\n\n---\n\n")
    f.write(f"## Product Hunt Tagline\n\n{PRODUCTHUNT_TAGLINE}\n")
print("Generated community posts")

# --- Lifecycle Emails ---
lc = LifecycleEmails()
welcome = lc.welcome("Customer")
dunning = lc.dunning("Customer")
with open(os.path.join(MKT, "email-sequences", "welcome.md"), "w", encoding="utf-8") as f:
    f.write("# Welcome Email Sequence\n\n")
    for e in welcome:
        f.write(f"## Day {e['day']}: {e['subject']}\n\n{e['body']}\n\n---\n\n")
with open(os.path.join(MKT, "email-sequences", "dunning.md"), "w", encoding="utf-8") as f:
    f.write("# Dunning (Failed Payment) Sequence\n\n")
    for e in dunning:
        f.write(f"## Day {e['day']}: {e['subject']}\n\n{e['body']}\n\n---\n\n")
print("Generated welcome + dunning emails")

# --- Social Media Content ---
social_posts = [
    ("Twitter/X", "🚀 Just launched Uptime Pro — simple uptime monitoring + status pages.\n\nFree tier: 5 monitors, 5-min checks, email alerts.\n\nMulti-region checks, Slack/webhook alerts, branded status pages.\n\nTry it free: https://uptime-pro.fly.dev\n\n#uptime #monitoring #saas #indiehacker"),
    ("Twitter/X", "Why I built Uptime Pro:\n\n1. UptimeRobot's UI is clunky\n2. Pingdom costs $15/mo for basics\n3. I wanted something simple that just works\n\nFree tier available. No credit card.\n\nhttps://uptime-pro.fly.dev"),
    ("Twitter/X", "Your customers shouldn't be the ones telling you your site is down.\n\nSet up uptime monitoring in 2 minutes:\n→ Add your URL\n→ Pick alert channels\n→ Get notified instantly\n\nFree: https://uptime-pro.fly.dev"),
    ("Twitter/X", "Status pages build trust.\n\nWhen things go wrong (and they will), a public status page shows:\n✅ You know about it\n✅ You're working on it\n✅ You're transparent\n\nBuild one in 60 seconds: https://uptime-pro.fly.dev"),
    ("LinkedIn", "I just launched Uptime Pro — a lightweight uptime monitoring tool with public status pages.\n\nAfter years of using overpriced, overcomplicated monitoring tools, I built something simple:\n\n• Multi-region HTTP checks\n• Instant email/Slack/webhook alerts\n• Branded public status pages\n• Free tier (no credit card)\n\nIf you run a website or API, downtime costs money. Uptime Pro helps you catch it before your customers do.\n\nTry it free: https://uptime-pro.fly.dev\n\n#saas #monitoring #uptime #webdev #indiehacker"),
    ("Reddit r/selfhosted", "I built a free uptime monitor + status page tool\n\nHey everyone — I've been working on Uptime Pro, a lightweight uptime monitor.\n\nFeatures:\n- Multi-region checks every 1-5 min\n- Email/Slack/webhook alerts\n- Branded public status pages with custom domains\n- Free tier (5 monitors)\n\nI'm a solo dev and would love feedback. What's missing? What would make you switch from UptimeRobot/Pingdom?\n\nLink: https://uptime-pro.fly.dev"),
    ("Reddit r/webdev", "Show: Uptime Pro — simple uptime monitoring with status pages\n\nI built this because I was tired of UptimeRobot's UI and Pingdom's pricing.\n\nDoes the basics well: multi-region HTTP checks, instant alerts, clean public status page.\n\nFree tier: 5 monitors, 5-min checks. Paid from $9/mo.\n\nTech: Python/FastAPI, Postgres, runs on Fly.io.\n\nHappy to answer questions. https://uptime-pro.fly.dev"),
    ("Indie Hackers", "Launched Uptime Pro today 🚀\n\nSimple uptime monitoring + public status pages.\n\nFree tier: 5 monitors. Paid from $9/mo.\n\nLooking for feedback from the community. What features matter most to you?\n\nhttps://uptime-pro.fly.dev"),
]
with open(os.path.join(MKT, "social", "social-posts.md"), "w", encoding="utf-8") as f:
    f.write("# Social Media Posts\n\n")
    for platform, post in social_posts:
        f.write(f"## {platform}\n\n{post}\n\n---\n\n")
print(f"Generated {len(social_posts)} social posts")

# --- Product Hunt Launch Kit ---
ph = """# Product Hunt Launch Kit

## Tagline
Uptime monitoring + status pages that just work

## Description
Uptime Pro is a lightweight uptime monitoring tool with public status pages.
Monitor your websites and APIs with multi-region checks, get instant alerts via
email/Slack/webhook, and publish a branded status page for your customers.

Free tier: 5 monitors, 5-minute checks, email alerts.
Paid plans from $9/month.

## First Comment (maker comment)
Hey Product Hunt! 👋

I'm James, and I built Uptime Pro because I was frustrated with existing uptime
monitoring tools. UptimeRobot's UI feels dated, and Pingdom costs $15/month for
basic features.

Uptime Pro focuses on doing the essentials well:
- Multi-region HTTP checks (avoid false positives)
- Instant alerts (email, Slack, webhook)
- Clean, branded public status pages
- Free tier with no credit card required

I'd love your feedback. What features would make this a must-have for you?

Try it free: https://uptime-pro.fly.dev

## Topics
SaaS, Developer Tools, Monitoring, Web Development, Productivity

## Launch Checklist
- [ ] Schedule launch for Tuesday/Wednesday
- [ ] Prepare 5-10 upvotes from friends/community
- [ ] Have first comment ready
- [ ] Respond to every comment within 1 hour
- [ ] Share on Twitter, LinkedIn, Reddit, Indie Hackers
- [ ] Email existing users (if any)
"""
with open(os.path.join(MKT, "product-hunt", "launch-kit.md"), "w", encoding="utf-8") as f:
    f.write(ph)
print("Generated Product Hunt launch kit")

# --- Landing Page Copy ---
lp = """# Landing Page Copy

## Hero
**Headline:** Never miss downtime again.
**Subheadline:** Multi-region uptime monitoring + public status pages. Free to start.
**CTA:** Start monitoring for free →
**Secondary:** No credit card required

## Features
### Multi-region checks
Monitor from 3 global regions. No false positives from a single bad node.

### Instant alerts
Get notified via email, Slack, or webhook the moment something breaks. Under 60 seconds.

### Public status pages
Branded status pages your customers can check. Builds trust and transparency.

### SSL monitoring
Get warned before your SSL certificate expires.

### Response time tracking
Spot slowdowns before they become outages.

## Pricing
### Free — $0
5 monitors, 5-min checks, email alerts, 1 status page

### Starter — $9/mo
25 monitors, 1-min checks, email + Slack alerts, 3 status pages, custom domain

### Team — $29/mo
100 monitors, 30s checks, all alert channels, unlimited status pages, multi-user

### Business — $49/mo
500 monitors, 30s checks, SMS alerts, priority support, API access

## FAQ
**Q: How fast are alerts?**
A: Under 60 seconds from failure to notification.

**Q: Can I monitor APIs?**
A: Yes — any HTTP/HTTPS endpoint.

**Q: Is there a free tier?**
A: Yes. 5 monitors, 5-minute checks, email alerts. No credit card required.

**Q: Can I use a custom domain for my status page?**
A: Yes, on Starter plan and above.

## Social Proof (placeholder)
"Uptime Pro caught a 3am outage before any customer noticed." — Early user

## Footer CTA
Ready to stop guessing if your site is up?
[Start monitoring for free →]
"""
with open(os.path.join(MKT, "landing-page", "copy.md"), "w", encoding="utf-8") as f:
    f.write(lp)
print("Generated landing page copy")

# --- Blog Posts ---
blog_posts = [
    ("why-uptime-monitoring-matters.md", "Why Uptime Monitoring Matters for Your Business", """
# Why Uptime Monitoring Matters for Your Business

Downtime costs money. Here's how to prevent it.

## The cost of downtime
- Small businesses lose $100-400 per hour of downtime
- E-commerce sites lose $4,000+ per minute
- 98% of organizations say a single hour of downtime costs over $100,000

## What uptime monitoring does
Uptime monitoring continuously checks if your website or API is reachable and responding correctly.
When something breaks, you get alerted instantly — before your customers notice.

## Key features to look for
1. Multi-region checks (avoid false positives)
2. Fast alerting (under 60 seconds)
3. Public status pages (transparency builds trust)
4. SSL certificate monitoring
5. Response time tracking

## Getting started
With Uptime Pro, you can set up monitoring in under 2 minutes:
1. Add your URL
2. Choose alert channels (email, Slack, webhook)
3. Publish a status page

Free tier: 5 monitors, 5-minute checks. No credit card required.

[Try Uptime Pro free →](https://uptime-pro.fly.dev)
"""),
    ("uptime-monitor-vs-status-page.md", "Uptime Monitor vs Status Page: What's the Difference?", """
# Uptime Monitor vs Status Page: What's the Difference?

Many people confuse these two. Here's the breakdown.

## Uptime Monitor
- **What it does:** Checks if your site is up every 1-5 minutes
- **Who sees it:** Only you (and your team)
- **Purpose:** Detect problems fast
- **Alerts:** Email, Slack, SMS, webhook

## Status Page
- **What it does:** Shows current status and incident history publicly
- **Who sees it:** Your customers and users
- **Purpose:** Transparency and trust
- **Updates:** Manual or automated

## Why you need both
- Monitor catches problems before customers notice
- Status page communicates during incidents
- Together they reduce support tickets and build trust

## Uptime Pro gives you both
One tool, one price. Monitor your sites AND publish a status page.
Free tier includes both.

[Try Uptime Pro free →](https://uptime-pro.fly.dev)
"""),
    ("how-to-choose-uptime-monitor.md", "How to Choose an Uptime Monitor", """
# How to Choose an Uptime Monitor

Not all uptime monitors are created equal. Here's what to look for.

## 1. Check frequency
- 1-minute checks catch issues fast
- 5-minute checks are fine for non-critical sites
- Avoid tools that only check every 10+ minutes

## 2. Multi-region checks
- Single-region checks give false positives
- Look for 2-3 regions minimum
- Global distribution matters

## 3. Alert channels
- Email is minimum
- Slack/Teams for team awareness
- Webhooks for custom integrations
- SMS for critical alerts

## 4. Status pages
- Public status pages build trust
- Custom domains look professional
- Incident history shows reliability

## 5. Pricing
- Free tiers should be genuinely useful
- Avoid per-monitor pricing that scales badly
- Look for flat-rate plans

## Our recommendation
Uptime Pro offers all of the above with a generous free tier.
5 monitors, 5-minute checks, email alerts, 1 status page — free.

[Try Uptime Pro free →](https://uptime-pro.fly.dev)
"""),
]
for filename, title, body in blog_posts:
    with open(os.path.join(MKT, "blog-posts", filename), "w", encoding="utf-8") as f:
        f.write(f"# {title}\n{body}")
print(f"Generated {len(blog_posts)} blog posts")

# --- Summary ---
print("\n=== Marketing content generated ===")
print(f"SEO articles: {len(articles)}")
print(f"Social posts: {len(social_posts)}")
print(f"Blog posts: {len(blog_posts)}")
print(f"Email sequences: welcome (3) + dunning (3)")
print(f"Product Hunt: launch kit")
print(f"Landing page: copy")
print(f"Location: {MKT}")