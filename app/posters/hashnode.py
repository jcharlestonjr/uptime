"""Hashnode blog publishing via GraphQL."""

from __future__ import annotations

import os
import json
import urllib.request
import urllib.error

HASHNODE_GQL = "https://gql.hashnode.com"


def hashnode_configured() -> bool:
    return bool(os.getenv("HASHNODE_TOKEN") and os.getenv("HASHNODE_PUBLICATION_ID"))


def _gql(query: str, variables: dict = None) -> dict:
    token = os.getenv("HASHNODE_TOKEN")
    if not token:
        return {"error": "HASHNODE_TOKEN not set", "mock": True}
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        HASHNODE_GQL,
        data=data,
        headers={
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "UptimePro/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {body}"}
    except Exception as e:
        return {"error": str(e)}


def get_publication_id() -> str:
    return os.getenv("HASHNODE_PUBLICATION_ID", "")


def publish_post(title: str, content_markdown: str, tags: list[str] = None,
                 published: bool = False) -> dict:
    """Publish a post to Hashnode."""
    pub_id = get_publication_id()
    if not pub_id:
        return {"error": "HASHNODE_PUBLICATION_ID not set", "mock": True}

    mutation = """
    mutation PublishPost($input: PublishPostInput!) {
        publishPost(input: $input) {
            post {
                id
                url
                title
            }
        }
    }
    """
    variables = {
        "input": {
            "title": title,
            "contentMarkdown": content_markdown,
            "publicationId": pub_id,
            "tags": [{"slug": t, "name": t} for t in (tags or ["technology"])],
        }
    }
    result = _gql(mutation, variables)
    if "error" in result:
        return result
    post = result.get("data", {}).get("publishPost", {}).get("post", {})
    if post:
        return {"success": True, "id": post.get("id"), "url": post.get("url"),
                "title": post.get("title")}
    return {"error": "Failed to publish", "response": result, "success": False}


def publish_from_file(filepath: str, tags: list[str] = None,
                     published: bool = False) -> dict:
    """Read a markdown file and publish to Hashnode."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

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
    if not title:
        for line in body.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break
    if not title:
        title = os.path.basename(filepath).replace(".md", "").replace("-", " ").title()

    return publish_post(title, body, tags=tags, published=published)


def get_my_publications() -> dict:
    """List your publications (to find publication ID)."""
    query = """
    query Me {
        me {
            publications(first: 10) {
                edges {
                    node {
                        id
                        title
                        url
                    }
                }
            }
        }
    }
    """
    return _gql(query)