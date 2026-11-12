"""Reddit posting via OAuth2."""

from __future__ import annotations

import os
import json
import urllib.request
import urllib.parse
import urllib.error
import base64

REDDIT_AUTH = "https://www.reddit.com/api/v1/access_token"
REDDIT_API = "https://oauth.reddit.com"


def reddit_configured() -> bool:
    return all(os.getenv(k) for k in ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET",
                                       "REDDIT_USERNAME", "REDDIT_PASSWORD"])


def _get_access_token() -> str:
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")

    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "password",
        "username": username,
        "password": password,
    }).encode()
    req = urllib.request.Request(
        REDDIT_AUTH,
        data=data,
        headers={
            "Authorization": f"Basic {auth}",
            "User-Agent": "UptimePro/1.0 by /u/" + username,
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return result.get("access_token", "")
    except Exception as e:
        return ""


def submit_post(subreddit: str, title: str, text: str = None,
                url: str = None, kind: str = "self") -> dict:
    """Submit a post to a subreddit. kind: 'self' or 'link'."""
    if not reddit_configured():
        return {"error": "Reddit credentials not set", "mock": True}

    token = _get_access_token()
    if not token:
        return {"error": "Failed to get access token", "success": False}

    username = os.getenv("REDDIT_USERNAME")
    data = {
        "sr": subreddit,
        "title": title,
        "kind": kind,
        "resubmit": "true",
        "sendreplies": "true",
    }
    if kind == "self":
        data["text"] = text or ""
    elif kind == "link":
        data["url"] = url or ""

    encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        f"{REDDIT_API}/api/submit",
        data=encoded,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": f"UptimePro/1.0 by /u/{username}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            if result.get("success"):
                return {"success": True, "url": result.get("jquery", [{}])[0].get("data", {}).get("url", ""),
                        "id": result.get("jquery", [{}])[0].get("data", {}).get("id", "")}
            return {"error": str(result), "success": False, "response": result}
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {body}", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


def submit_comment(thing_id: str, text: str) -> dict:
    """Comment on a post or comment."""
    if not reddit_configured():
        return {"error": "Reddit credentials not set", "mock": True}
    token = _get_access_token()
    if not token:
        return {"error": "Failed to get access token", "success": False}
    username = os.getenv("REDDIT_USERNAME")
    data = urllib.parse.urlencode({"thing_id": thing_id, "text": text}).encode()
    req = urllib.request.Request(
        f"{REDDIT_API}/api/comment",
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": f"UptimePro/1.0 by /u/{username}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {"success": True, "response": json.loads(resp.read().decode())}
    except Exception as e:
        return {"error": str(e), "success": False}