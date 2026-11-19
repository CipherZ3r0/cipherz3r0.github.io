#!/usr/bin/env python3
"""Static site generator for Nilax Modi's portfolio.
Creates HTML pages from markdown posts using Jinja2 templates.
"""

import os
import re
import sys
import shutil
import datetime
from pathlib import Path
import yaml
try:
    import markdown
    def render_markdown(text: str) -> str:
        return markdown.markdown(text, extensions=["fenced_code", "tables", "toc"])
except ImportError:
    def render_markdown(text: str) -> str:
        # Fallback if markdown library is missing
        def repl_heading(m):
            level = len(m.group(1))
            return f"<h{level}>" + m.group(2).strip() + f"</h{level}>"
        text = re.sub(r'^(#{1,6})\s+(.*)$', repl_heading, text, flags=re.MULTILINE)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'`([^`]+?)`', r'<code>\1</code>', text)
        lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
        html = ''
        for ln in lines:
            if ln.startswith('<h') or ln.startswith('<ul>') or ln.startswith('<li>'):
                html += ln
            elif ln.startswith('- ') or ln.startswith('* '):
                html += f'<li>{ln[2:]}</li>'
            else:
                html += f'<p>{ln}</p>'
        return html
from jinja2 import Environment, FileSystemLoader, select_autoescape

# ---------------------------------------------------------------------------
# Data for homepage
hero = {
    "headline": "Understanding systems. Building things. Sharing what I learn.",
    "intro": "I\'m Nilax Modi, an engineer interested in the internals of software, backend systems, open source, and security. I enjoy investigating complex problems, understanding why things work the way they do, and turning those discoveries into practical solutions."
}

exploration_log = [
    {"topic": "AI Security & Security Auditing", "current": False},
    {"topic": "C++ & Systems Programming", "current": True},
    {"topic": "LLMs & RAG Architecture", "current": False},
    {"topic": "Database Internals & Query Optimization", "current": False},
    {"topic": "Python Runtime & C Extensions", "current": False},
    {"topic": "Memcached Internals", "current": False},
]

projects = [
    {
        "title": "Medibo",
        "url": "https://github.com/CipherZ3r0/medibo",
        "tags": ["Python", "RAG", "Retrieval", "Provenance", "Reranking"],
        "description": "An evidence-grounded medical knowledge and RAG platform focused on reliable retrieval, source provenance, reranking, and healthcare information."
    },
    {
        "title": "Potbot",
        "url": "https://github.com/CipherZ3r0/Potbot",
        "tags": ["Python", "Hybrid Search", "BM25", "Vector Search", "RRF"],
        "description": "A hybrid retrieval system combining vector search, BM25, Reciprocal Rank Fusion (RRF), and cross-encoder reranking for context-relevant AI responses."
    },
    {
        "title": "Project-Nika",
        "url": "https://github.com/CipherZ3r0/nikka",
        "demo_url": "https://nikka-topaz.vercel.app/",
        "tags": ["TypeScript", "AI Security", "Prompt Injection", "Red Teaming", "Defenses"],
        "description": "An AI security playground exploring prompt injection vectors, jailbreak challenges, and defensive alignment mechanisms."
    },
    {
        "title": "Cryptices",
        "url": "https://github.com/CipherZ3r0/cryptices",
        "tags": ["Python", "CLI", "Bitcoin", "Cryptography", "Blockchain"],
        "description": "A Python command-line utility for decoding, validating, and identifying Bitcoin address types and inspecting blockchain data."
    }
]

contributions = [
    {
        "title": "Open Library",
        "repo": "Open Library",
        "description": "Investigated database performance, N+1 queries, and concurrency issues."
    },
    {
        "title": "emcache",
        "repo": "emcache",
        "description": "Added Python 3.15 compatibility, macOS support, CI pipelines, and benchmark infrastructure."
    }
]

# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.yaml"
DEFAULT_CFG = {
    "site_name": "Nilax Modi",
    "author": "Nilax Modi",
    "base_url": "https://cipherz3r0.github.io",
    "theme": {"default": "light", "options": ["light", "dark"]},
    "posts_path": "content/posts",
    "output_path": "site",
}
if CONFIG_PATH.is_file():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = {**DEFAULT_CFG, **yaml.safe_load(f)}
else:
    cfg = DEFAULT_CFG

POSTS_DIR = BASE_DIR / cfg["posts_path"]
OUTPUT_DIR = BASE_DIR / cfg["output_path"]
TEMPLATE_DIR = BASE_DIR / "src" / "templates"
ASSET_SRC = BASE_DIR / "src" / "assets"

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------
def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "-", text).strip("-")

def reading_time(text: str) -> int:
    words = len(text.split())
    return max(1, words // 200)

def extract_front_matter(md_path: Path):
    raw = md_path.read_text(encoding="utf-8")
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        meta = yaml.safe_load(parts[1]) or {}
        body = parts[2].lstrip("\n")
    else:
        meta = {}
        body = raw
    return meta, body

# ---------------------------------------------------------------------------
# Build steps
# ---------------------------------------------------------------------------
def build_post_page(env, meta, html_body, slug):
    tmpl = env.get_template("post.html")
    out_path = OUTPUT_DIR / "posts" / slug / "index.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = tmpl.render(
        title=meta.get("title", "Untitled"),
        description=meta.get("description", ""),
        content=html_body,
        url=f"{cfg['base_url']}/posts/{slug}/",
        author=cfg["author"],
        date=meta.get("date", ""),
        tags=meta.get("tags", []),
        reading_time=reading_time(html_body),
        year=datetime.datetime.now().year,
    )
    out_path.write_text(rendered, encoding="utf-8")

def build_index(env, recent_posts, projects, contributions, hero, exploration_log):
    tmpl = env.get_template("index.html")
    out_path = OUTPUT_DIR / "index.html"
    rendered = tmpl.render(
        site_name=cfg["site_name"],
        title="Nilax Modi (CipherZ3r0)",
        recent_posts=recent_posts,
        projects=projects,
        contributions=contributions,
        hero=hero,
        exploration_log=exploration_log,
        year=datetime.datetime.now().year,
    )
    out_path.write_text(rendered, encoding="utf-8")

def build_archive(env, all_posts):
    tmpl = env.get_template("archive.html")
    out_path = OUTPUT_DIR / "posts" / "index.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = tmpl.render(
        posts=all_posts,
        year=datetime.datetime.now().year,
    )
    out_path.write_text(rendered, encoding="utf-8")

def build_rss(all_posts):
    from xml.sax.saxutils import escape
    items = []
    for p in all_posts:
        items.append(f"""
        <item>
            <title>{escape(p['title'])}</title>
            <link>{cfg['base_url']}/posts/{p['slug']}/</link>
            <guid>{cfg['base_url']}/posts/{p['slug']}/</guid>
            <pubDate>{p['date'].strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate>
            <description>{escape(p['description'])}</description>
        </item>""")
    rss = f"""<?xml version='1.0' encoding='UTF-8'?>
    <rss version='2.0'><channel>
        <title>{cfg['site_name']}</title>
        <link>{cfg['base_url']}</link>
        <description>{cfg['site_name']} – engineering portfolio & blog</description>
        <language>en-us</language>
        {''.join(items)}
    </channel></rss>"""
    (OUTPUT_DIR / "feed.xml").write_text(rss.strip(), encoding="utf-8")

def copy_assets():
    dest = OUTPUT_DIR / "assets"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(ASSET_SRC, dest)
    # Ensure GitHub Pages doesn't run Jekyll
    (OUTPUT_DIR / ".nojekyll").touch()

def main():
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    posts = []
    for md_file in sorted(POSTS_DIR.glob("*.md")):
        meta, body = extract_front_matter(md_file)
        title = meta.get("title", md_file.stem)
        date_str = meta.get("date", datetime.date.today().isoformat())
        try:
            date = datetime.datetime.fromisoformat(date_str)
        except Exception:
            date = datetime.datetime.now()
        slug = slugify(title)
        html_body = render_markdown(body)
        posts.append({
            "title": title,
            "description": meta.get("description", ""),
            "date": date,
            "slug": slug,
            "tags": meta.get("tags", []),
            "html": html_body,
        })
        build_post_page(env, meta, html_body, slug)

    # newest first
    posts.sort(key=lambda x: x["date"], reverse=True)

    build_index(env, posts[:3], projects, contributions, hero, exploration_log)
    build_archive(env, posts)
    build_rss(posts)
    copy_assets()
    print(f"✅ Site generated at {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
