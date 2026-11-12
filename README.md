# Uptime Pro — Production-Grade, Self-Running Uptime Monitor

Built on top of the `uptime-monitor` MVP. Adds multi-region checking with debounce/quorum,
incident lifecycle with auto post-mortems, alert dispatching with cooldown + escalation,
static status pages with custom-domain provisioning, SEO content generation, cold-outreach
and lifecycle email sequences, deploy configs, and a checker worker.

## Run

```powershell
cd uptime-pro
python -m pytest
python -m uvicorn app.main:app --reload --port 8000
# worker (separate process):
python -m app.worker
```

## Automation surface (what runs without you)

- **Checker worker** (`app/worker.py`) — async multi-region checks with retry + debounce + quorum
- **Alerts** (`app/alerts.py`) — cooldown, escalation, email/Slack/SMS/webhook templates
- **Incidents** (`app/incidents.py`) — auto open/resolve + post-mortem draft generator
- **Status pages** (`app/statuspage.py`) — static HTML renderer + custom domain DNS instructions + cache
- **SEO** (`app/seo.py`) — 15-keyword article generator + content calendar
- **Outreach** (`app/outreach.py`) — 3-step cold email sequence + HN/PH/community posts
- **Lifecycle emails** (`app/outreach.py`) — welcome + dunning sequences
- **Deploy** (`deploy/`) — Dockerfile, docker-compose, GitHub Actions

## Key endpoints (additions over MVP)

- `POST /monitors/{id}/check` — multi-region check with incident + alert + escalation
- `GET /monitors/{id}/incidents/{iid}/post-mortem`
- `GET /monitors/{id}/metrics` — p95, MTTR, incident frequency
- `GET /status/{slug}` — rendered HTML status page
- `POST /status-pages/{slug}/domain` — DNS instructions
- `POST /seo/generate`, `GET /seo/article/{slug}`, `GET /seo/calendar`
- `POST /outreach/sequence`, `GET /outreach/community-post`, `GET /outreach/hn-post`
- `GET /emails/welcome/{name}`, `GET /emails/dunning/{name}`
- `GET /self/status`

## Tests: 25 passing.