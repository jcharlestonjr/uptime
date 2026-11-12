# Uptime Pro — Marketing Kit

All marketing content is generated and ready to use. No manual writing needed.

## Contents

| Folder | Files | Description |
|--------|-------|-------------|
| `seo-articles/` | 15 .md files | SEO-optimized articles targeting uptime keywords |
| `seo-articles/_calendar.json` | 1 | Publishing schedule (3 posts/week) |
| `social/` | social-posts.md | 8 posts for Twitter/X, LinkedIn, Reddit, Indie Hackers |
| `outreach/` | cold-email-sequence.md | 3-step cold email sequence |
| `outreach/` | community-posts.md | Reddit, HN, PH posts ready to copy-paste |
| `product-hunt/` | launch-kit.md | Full PH launch kit (tagline, description, first comment, checklist) |
| `landing-page/` | copy.md | Complete landing page copy |
| `email-sequences/` | welcome.md, dunning.md | Welcome (3 emails) + dunning (3 emails) |
| `blog-posts/` | 3 .md files | Blog posts for your site |

## Quick Actions

### 1. Publish SEO articles (free traffic)
- Host on Hashnode, Dev.to, or your own blog
- 15 articles targeting "uptime monitor", "status page", etc.
- Content calendar in `_calendar.json` (3/week for 5 weeks)

### 2. Post to communities (free traffic)
Copy-paste from `outreach/community-posts.md`:
- Reddit: r/selfhosted, r/webdev, r/SaaS
- Hacker News: Show HN post
- Indie Hackers: launch post

### 3. Social media (free traffic)
Post from `social/social-posts.md`:
- Twitter/X: 4 tweets
- LinkedIn: 1 post
- Reddit: 2 posts

### 4. Cold outreach (direct sales)
Use `outreach/cold-email-sequence.md`:
- Find SaaS founders on Twitter/LinkedIn
- Send 3-email sequence over 7 days
- Target: 50 founders/week

### 5. Product Hunt launch
Follow `product-hunt/launch-kit.md`:
- Schedule for Tuesday or Wednesday
- Prepare 5-10 upvotes
- Respond to every comment

### 6. Email sequences
- Welcome: `email-sequences/welcome.md` (trigger on signup)
- Dunning: `email-sequences/dunning.md` (trigger on payment failure)

## Regenerate content
```powershell
python scripts/generate_marketing.py
```

## Live product
https://uptime-pro.fly.dev/