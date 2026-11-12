"""Post marketing content to configured platforms.

Usage:
  python scripts/post_to_platforms.py --platform devto --file marketing/seo-articles/uptime-monitor.md
  python scripts/post_to_platforms.py --platform hashnode --file marketing/blog-posts/why-uptime-monitoring-matters.md
  python scripts/post_to_platforms.py --platform reddit --subreddit selfhosted --title "I built a free uptime monitor" --text "..."
  python scripts/post_to_platforms.py --status  (check which platforms are configured)
"""

import sys, os, argparse, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.posters.devto import devto_configured, publish_from_file as devto_publish, list_articles
from app.posters.hashnode import hashnode_configured, publish_from_file as hashnode_publish, get_my_publications
from app.posters.reddit import reddit_configured, submit_post

# Load .env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())


def check_status():
    print("Platform configuration status:")
    print(f"  Dev.to:    {'CONFIGURED' if devto_configured() else 'NOT configured (set DEVTO_API_KEY)'}")
    print(f"  Hashnode:  {'CONFIGURED' if hashnode_configured() else 'NOT configured (set HASHNODE_TOKEN + HASHNODE_PUBLICATION_ID)'}")
    print(f"  Reddit:    {'CONFIGURED' if reddit_configured() else 'NOT configured (set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD)'}")


def post_devto(filepath, published=False):
    if not devto_configured():
        print("Dev.to not configured. Set DEVTO_API_KEY in .env")
        return
    result = devto_publish(filepath, published=published)
    print(json.dumps(result, indent=2))


def post_hashnode(filepath, published=False):
    if not hashnode_configured():
        print("Hashnode not configured. Set HASHNODE_TOKEN and HASHNODE_PUBLICATION_ID in .env")
        # Try to get publication ID
        pubs = get_my_publications()
        print("Your publications:", json.dumps(pubs, indent=2))
        return
    result = hashnode_publish(filepath, published=published)
    print(json.dumps(result, indent=2))


def post_reddit(subreddit, title, text=None, url=None):
    if not reddit_configured():
        print("Reddit not configured. Set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD in .env")
        return
    kind = "link" if url else "self"
    result = submit_post(subreddit, title, text=text, url=url, kind=kind)
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Post marketing content to platforms")
    parser.add_argument("--status", action="store_true", help="Check platform configuration")
    parser.add_argument("--platform", choices=["devto", "hashnode", "reddit"], help="Platform to post to")
    parser.add_argument("--file", help="Markdown file to publish (for devto/hashnode)")
    parser.add_argument("--published", action="store_true", help="Publish immediately (default: draft)")
    parser.add_argument("--subreddit", help="Subreddit name (for reddit)")
    parser.add_argument("--title", help="Post title (for reddit)")
    parser.add_argument("--text", help="Post text (for reddit)")
    parser.add_argument("--url", help="Post URL (for reddit link posts)")
    args = parser.parse_args()

    if args.status:
        check_status()
        return

    if not args.platform:
        parser.print_help()
        return

    if args.platform == "devto":
        if not args.file:
            print("Error: --file required for devto")
            return
        post_devto(args.file, published=args.published)
    elif args.platform == "hashnode":
        if not args.file:
            print("Error: --file required for hashnode")
            return
        post_hashnode(args.file, published=args.published)
    elif args.platform == "reddit":
        if not args.subreddit or not args.title:
            print("Error: --subreddit and --title required for reddit")
            return
        post_reddit(args.subreddit, args.title, text=args.text, url=args.url)


if __name__ == "__main__":
    main()