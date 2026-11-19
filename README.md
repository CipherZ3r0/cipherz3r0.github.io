# Cipherz3r0 Portfolio

This repository hosts the source for **Nilax Modi (Cipherz3r0)**'s personal engineering portfolio and technical blog.

## Overview

- **Static site** built with a tiny Python build script (`build.py`).
- Content is written in **Markdown** under `content/posts/`.
- Generated HTML lives in the `site/` directory and is served directly by GitHub Pages.
- No server‑side dependencies, only Python 3 and the `markdown` and `jinja2` packages.
- Supports dark / light themes, responsive layout, syntax‑highlighted code, SEO metadata, Open Graph tags, and an RSS feed.

## Quick start

```bash
# Install the build dependencies (once)
python -m pip install -r requirements.txt

# Build the site
python build.py

# Preview locally (any static file server works)
python -m http.server --directory site 8000
```

Add a new article by creating a Markdown file in `content/posts/` – the build script will automatically pick it up, generate a post page, update the archive, tags, categories and the RSS feed.

## Repository layout

```
.
├─ content/                # Source markdown files
│   └─ posts/              # Individual articles
│        └─ 2024-01-01-example.md
├─ src/                    # Templates and static assets
│   ├─ assets/             # CSS, JS, images, icons
│   └─ templates/          # Jinja2 HTML templates
├─ build.py                # Static‑site generator script
├─ requirements.txt        # Python dependencies
├─ .gitignore
└─ README.md               # This file
```

## Publishing

GitHub Pages can serve the `site/` folder directly. After committing new content, run `python build.py` locally or in a CI workflow, push the updated `site/` folder, and GitHub Pages will automatically update the live site.

---

*This README is intentionally minimal – the detailed instructions are in `docs/BUILDING.md`.*