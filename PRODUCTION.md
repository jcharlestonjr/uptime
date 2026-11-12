# Uptime Pro — Production Readiness Checklist

This document lists everything needed to take Uptime Pro to production, split into
**what I (the AI agent) can do autonomously** vs **what requires your accounts/keys/payment**.

---

## ✅ Already built (no action needed)

- FastAPI app with all endpoints (monitors, checks, incidents, status pages, SEO, outreach, emails)
- Multi-region checker with retry/debounce/quorum
- Alert dispatcher (cooldown, escalation, templates)
- Incident manager + auto post-mortem drafts
- Static status page renderer + custom domain DNS instructions
- SEO content generator (15 keywords) + content calendar
- Cold-outreach + lifecycle email sequences
- SQLAlchemy models for all entities (User, ApiKey, Subscription, Monitor, Check, Incident, StatusPage, Lead)
- Alembic migrations setup + initial schema
- Auth: signup/login, API keys, JWT
- Stripe billing module (checkout, portal, webhooks, plan limits)
- Email (Resend) + SMS (Twilio) delivery modules (mocked when unconfigured)
- Rate limiting middleware
- Security headers middleware
- Request logging
- CORS configuration
- Health + config status endpoints
- Dockerfile + docker-compose + GitHub Actions CI/CD
- 39 passing tests (core + API + production)

---

## 🔐 What I need from you (accounts, keys, domains)

To make this fully autonomous in production, I need the following. Once you provide them,
I can wire everything up and deploy without further input.

### 1. Cloud hosting account (pick one)
- **Fly.io** (recommended, cheapest for this stack) — `flyctl auth login` + `FLY_API_TOKEN`
- OR Railway / Render / AWS / GCP
- *I need:* account + API token

### 2. Database
- **Neon** (recommended, free tier, Postgres) or Supabase or RDS
- *I need:* `DATABASE_URL` connection string

### 3. Redis (for rate limiting + queue)
- **Upstash** (free tier) or Redis Cloud
- *I need:* `REDIS_URL`

### 4. Stripe account (billing)
- Create account at stripe.com
- Create products/prices for Starter/Team/Business plans
- Set up webhook endpoint pointing to `https://yourdomain.com/billing/webhook`
- *I need:* `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_STARTER`, `STRIPE_PRICE_TEAM`, `STRIPE_PRICE_BUSINESS`

### 5. Email delivery (Resend)
- Create account at resend.com
- Verify your sending domain (DNS records)
- *I need:* `RESEND_API_KEY`, `EMAIL_FROM` (e.g., alerts@uptimepro.app)

### 6. SMS delivery (Twilio) — optional but recommended
- Create account at twilio.com
- Buy a phone number
- *I need:* `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`

### 7. Domain
- Register `uptimepro.app` (or your choice) at Namecheap/Cloudflare/Porkbun
- Point DNS to your hosting provider
- *I need:* domain name + DNS access (or you add CNAME/A records I specify)

### 8. Observability (optional)
- **Sentry** for error tracking — *I need:* `SENTRY_DSN`

### 9. Slack (optional)
- Incoming webhook URL for your own alerts
- *I need:* `SLACK_WEBHOOK_URL`

### 10. GitHub repository
- Create a repo and push this code
- *I need:* repo URL + push access (or I can init locally and you push)

---

## 🔧 What I can do autonomously once you give me the above

With the credentials above, I can without further input:

1. **Wire up real Stripe** — replace mock checkout with live sessions, handle real webhooks, sync subscription status to DB, enforce plan limits
2. **Wire up real email** — send actual alert emails, welcome/dunning sequences, password resets
3. **Wire up real SMS** — send actual alert SMS
4. **Deploy to production** — `flyctl deploy` or equivalent, set all env vars, run migrations
5. **Configure custom domain + SSL** — DNS records, Let's Encrypt cert
6. **Set up monitoring** — Sentry integration, health checks, self-monitoring
7. **Run migrations** — `alembic upgrade head` on prod DB
8. **Generate & publish SEO content** — 15 articles to your blog/CMS
9. **Schedule the checker worker** — as a separate process/service
10. **Set up backups** — daily Postgres dumps to R2/S3
11. **Configure CI/CD** — GitHub Actions with secrets
12. **Create the first admin user** — so you can log in immediately

---

## 📋 Minimal viable "go live" (if you want to start small)

If you want to launch with minimal setup, I only need:
1. **Fly.io account + token** (hosting)
2. **Neon DATABASE_URL** (database)
3. **Domain name** (DNS)
4. **Resend API key** (email alerts — the core product feature)

Stripe, Twilio, Sentry, Slack, Redis can be added later. The app gracefully degrades when these aren't configured (mocks + in-memory rate limiting).

---

## 🚀 Estimated timeline once you provide credentials

| Step | Time |
|------|------|
| Wire real services + deploy | 1–2 hours (me) |
| DNS propagation | 1–24 hours (automatic) |
| Stripe product setup | 30 min (you, one-time) |
| First paying customer | 1–4 weeks (marketing) |
| $10k cumulative revenue | 3–6 months |

---

## 💡 What I cannot do (ever, without you)

- Create accounts on your behalf (legal/identity)
- Make payments for hosting/domains
- Verify email domains (requires DNS access I don't have)
- Sign up for Stripe (requires business identity + bank account)
- Push to a GitHub repo you own (needs your auth token)

Everything else — code, config, deploy scripts, content, automation — I can do.