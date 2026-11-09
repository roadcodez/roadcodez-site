#!/usr/bin/env python3
"""
Static-site builder for roadcodez.com (no dependencies, Python 3 only).

  src/_header.html, src/_footer.html   shared on EVERY page (logo -> Home lives here)
  src/<page>.html                      page body with a small front-matter block
  site/                                the deployable output (this is what you upload)

Run:  python3 build.py
Edit pages in src/, then rebuild. Do not hand-edit site/*.html (it is overwritten).
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC, OUT = ROOT / "src", ROOT / "site"
DOMAIN = "https://roadcodez.com"

ICONS = {
 "truck": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 6.5h11v9H2z"/><path d="M13 9.5h4.2l3.3 3.3v2.7H13"/><circle cx="6.5" cy="17.5" r="1.9"/><circle cx="16.5" cy="17.5" r="1.9"/></svg>',
 "wheel": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2.4"/><path d="M12 14.4V21M3.4 10.4l6.2 1.2M20.6 10.4l-6.2 1.2"/></svg>',
 "chip": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/><path d="M9 3v3M15 3v3M9 18v3M15 18v3M3 9h3M3 15h3M18 9h3M18 15h3"/></svg>',
 "warn": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 2.5 20h19z"/><path d="M12 10v5M12 17.6v.1"/></svg>',
 "lock": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/></svg>',
 "coin": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M14.6 9.2c-.5-.9-1.5-1.3-2.6-1.3-1.5 0-2.6.8-2.6 2s1 1.7 2.6 2.1 2.6.9 2.6 2.1-1.1 2-2.6 2c-1.1 0-2.1-.5-2.6-1.4M12 6.5v1.4M12 16.1v1.4"/></svg>',
 "swap": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8h13l-3-3M20 16H7l3 3"/></svg>',
 "list": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6h11M9 12h11M9 18h11"/><path d="M4 6h.01M4 12h.01M4 18h.01"/></svg>',
}

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="theme-color" content="#07080b">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="RoadCodez">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{domain}/assets/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="48x48" href="assets/favicon-48.png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Michroma&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/styles.css">
<script>document.documentElement.classList.add('js')</script>
{extra_head}</head>
<body>
"""

TAIL = """
<script src="js/site.js" defer></script>
</body>
</html>
"""

ORG_LD = """<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Organization","name":"RoadCodez","url":"https://roadcodez.com","logo":"https://roadcodez.com/assets/icon-512.png","description":"Trucking and driver training for Prime Inc., plus AI-built agents, apps and creative work."}
</script>
"""

def parse(path):
    text = path.read_text()
    meta, _, body = text.partition("\n---\n")
    fm = dict(re.findall(r"^(\w+):\s*(.+)$", meta, re.M))
    return fm, body

def build():
    header = (SRC / "_header.html").read_text()
    footer = (SRC / "_footer.html").read_text()
    pages = sorted(p for p in SRC.glob("*.html") if not p.name.startswith("_"))
    for p in pages:
        fm, body = parse(p)
        nav = fm.get("nav", "")
        h = header
        for key in ("home", "trucking", "training", "ai", "about"):
            h = h.replace("{{nav_%s}}" % key, ' aria-current="page"' if nav == key else "")
        # generated artwork lives in src/_parts (made by tools/*.py); {{include:name.svg}} pastes it in
        body = re.sub(r"\{\{include:([\w.\-]+)\}\}", lambda m: (SRC / "_parts" / m.group(1)).read_text(), body)
        for k, v in ICONS.items():
            body = body.replace("{{icon_%s}}" % k, v)
        name = "index.html" if p.name == "index.html" else p.name
        canon = DOMAIN + ("/" if name == "index.html" else "/" + name)
        extra = ORG_LD if name == "index.html" else ""
        if fm.get("noindex"):
            extra += '<meta name="robots" content="noindex">\n'
        head = HEAD.format(title=fm["title"], description=fm["description"], canon=canon, domain=DOMAIN, extra_head=extra)
        html = head + h + '<main id="main">\n' + body.strip() + "\n</main>\n" + footer + TAIL
        (OUT / name).write_text(html)
        print("built", name)
    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % DOMAIN)
    urls = ["/"] + ["/" + p.name for p in pages if p.name not in ("index.html", "404.html")]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join("  <url><loc>%s%s</loc></url>\n" % (DOMAIN, u) for u in urls) + "</urlset>\n"
    (OUT / "sitemap.xml").write_text(sm)
    print("built robots.txt, sitemap.xml")

if __name__ == "__main__":
    build()
