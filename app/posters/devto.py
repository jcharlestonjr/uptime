"""Dev.to article publishing."""

from __future__ import annotations

import os
import json
import urllib.request
import urllib.error

DEVTO_API = "https://dev.to/api"


def devto_configured() -> bool:
    return bool(os.getenv("DEVTO_API_KEY"))


def publish_article(title: str, body_markdown: str, tags: list[str] = None,
                   canonical_url: str = None, published: bool = False) -> dict:
    """Publish an article to Dev.to. Returns article data or error."""
    api_key = os.getenv("DEVTO_API_KEY")
    if not api_key:
        return {"error": "DEVTO_API_KEY not set", "mock": True}

    tags = tags or ["uptime", "monitoring", "saas", "webdev"]
    payload = {
        "article": {
            "title": title,
            "body_markdown": body_markdown,
            "published": published,
            "tags": tags[:4],  # Dev.to max 4 tags
        }
    }
    if canonical_url:
        payload["article"]["canonical_url"] = canonical_url

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{DEVTO_API}/articles",
        data=data,
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
            "User-Agent": "UptimePro/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return {
                "success": True,
                "id": result.get("id"),
                "url": result.get("url"),
                "title": result.get("title"),
            }
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {body}", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


def publish_from_file(filepath: str, tags: list[str] = None,
                     published: bool = False) -> dict:
    """Read a markdown file and publish to Dev.to."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract frontmatter
    title = ""
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            body = parts[2].strip()
            for line in frontmatter.split("\n"):
                if line.startswith("title:"):
                    title = line.replace("title:", "").strip()
                if line.startswith("tags:"):
                    tags = [t.strip() for t in line.replace("tags:", "").split(",")]

    if not title:
        # Use first heading
        for line in body.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break
    if not title:
        title = os.path.basename(filepath).replace(".md", "").replace("-", " ").title()

    return publish_article(title, body, tags=tags, published=published)


def list_articles() -> dict:
    """List your published articles."""
    api_key = os.getenv("DEVTO_API_KEY")
    if not api_key:
        return {"error": "DEVTO_API_KEY not set", "mock": True}
    req = urllib.request.Request(
        f"{DEVTO_API}/articles/me",
        headers={"api-key": api_key, "User-Agent": "UptimePro/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {"articles": json.loads(resp.read().decode())}
    except Exception as e:
        return {"error": str(e)}