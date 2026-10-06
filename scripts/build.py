#!/usr/bin/env python3
"""Static site builder for the Arshad Siddique affiliate website.

Composes src/pages/*.html with the shared head, header, footer and icons,
then writes the finished site (plus assets, sitemap and robots) to public/.

Usage:
    SITE_URL=https://your-domain.com python3 scripts/build.py
"""
import html
import json
import os
import re
import shutil
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "pages"
OUT = ROOT / "public"

# ---------------------------------------------------------------- settings
# Set SITE_URL to the production domain before deploying (used for canonical
# URLs, Open Graph, structured data and sitemap.xml).
SITE_URL = os.environ.get("SITE_URL", "https://arshad-siddique-bitget.netlify.app").rstrip("/")

REG_URL = "https://partner.bitget.site/bg/ZGRSVM"
REG_LABEL = "partner.bitget.site/bg/ZGRSVM"
REF_CODE = "su87"
WA_NUMBER = "971527065971"
WA_DISPLAY = "+971 52 706 5971"
WA_TEXT = "Hello Arshad, I found your website and would like to learn more about joining Bitget through you."
WA_URL = f"https://wa.me/{WA_NUMBER}?text={quote(WA_TEXT)}"

PAGES = {
    "index.html": {
        "title": "Arshad Siddique | Independent Bitget Affiliate in Dubai",
        "description": "Meet Arshad Siddique, an independent Bitget affiliate based in Dubai, building an international community around the Bitget ecosystem. Join through Arshad with referral code su87.",
        "path": "/",
        "nav": "home",
        "crumbs": None,
    },
    "bitget.html": {
        "title": "Bitget Ecosystem & Benefits | Copy Trading, Wallet Card, Affiliate Program",
        "description": "An independent overview of Bitget spot, futures, copy trading, Bitget Wallet, the Bitget Wallet Card and the Bitget Affiliate Program, presented by Dubai-based affiliate Arshad Siddique.",
        "path": "/bitget.html",
        "nav": "bitget",
        "crumbs": [("Home", "/"), ("Bitget & Benefits", "/bitget.html")],
    },
    "join.html": {
        "title": "Join Through Arshad | Bitget Referral Code su87 & Community",
        "description": "Register on Bitget through Arshad Siddique's affiliate link (referral code su87), explore the community, find your path and contact Arshad on WhatsApp.",
        "path": "/join.html",
        "nav": "join",
        "crumbs": [("Home", "/"), ("Join & Community", "/join.html")],
    },
}

# ------------------------------------------------------------------- icons
def _s(body, fill=False):
    attrs = 'fill="currentColor"' if fill else 'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
    return f'<svg viewBox="0 0 24 24" {attrs} aria-hidden="true" focusable="false">{body}</svg>'

ICONS = {
    "whatsapp": _s('<path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38a9.9 9.9 0 0 0 4.74 1.21h.01c5.46 0 9.91-4.45 9.91-9.91A9.86 9.86 0 0 0 12.04 2Zm0 18.15h-.01a8.23 8.23 0 0 1-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.21 8.21 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.25-8.24a8.2 8.2 0 0 1 5.83 2.42 8.18 8.18 0 0 1 2.41 5.83c0 4.54-3.7 8.23-8.23 8.23Zm4.52-6.16c-.25-.12-1.47-.72-1.69-.81-.23-.08-.39-.12-.56.13-.16.24-.64.8-.78.97-.15.16-.29.18-.54.06-.25-.12-1.05-.39-1.99-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.01-.38.11-.5.11-.11.25-.29.37-.43.13-.15.17-.25.25-.41.08-.17.04-.31-.02-.43-.06-.12-.56-1.34-.76-1.84-.2-.48-.41-.42-.56-.43h-.48c-.17 0-.43.06-.66.31-.22.25-.86.85-.86 2.07 0 1.22.89 2.4 1.01 2.56.12.17 1.75 2.67 4.23 3.74.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.67-1.18.21-.58.21-1.07.15-1.18-.06-.1-.22-.16-.47-.28Z"/>', fill=True),
    "shield": _s('<path d="M12 3 4.5 6v5.5c0 4.6 3.2 8.4 7.5 9.5 4.3-1.1 7.5-4.9 7.5-9.5V6L12 3Z"/><path d="m9 12 2 2 4-4"/>'),
    "pin": _s('<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.5"/>'),
    "globe": _s('<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>'),
    "users": _s('<circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14.2c2.9.3 5 2.6 5 5.8"/>'),
    "copy": _s('<circle cx="8" cy="7" r="3"/><circle cx="17" cy="8" r="2.4"/><path d="M2.5 18c0-3 2.5-5.5 5.5-5.5S13.5 15 13.5 18"/><path d="M14 17.5h7m0 0-2.5-2.5M21 17.5 18.5 20"/>'),
    "coin": _s('<circle cx="12" cy="12" r="9"/><path d="M9.5 7.5h4a2 2 0 0 1 0 4h-4m0 0h4.5a2 2 0 0 1 0 4h-4.5m0-8v8m1.5-9.5v1.5m0 8v1.5"/>'),
    "candles": _s('<path d="M6 4v3m0 8v5M18 3v4m0 6v8M12 7v2m0 8v3"/><rect x="4" y="7" width="4" height="8" rx="1"/><rect x="10" y="9" width="4" height="8" rx="1"/><rect x="16" y="7" width="4" height="6" rx="1"/>'),
    "chart": _s('<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 6-7"/><path d="M15 7h5v5"/>'),
    "wallet": _s('<path d="M4 7.5A2.5 2.5 0 0 1 6.5 5H18v3"/><rect x="3.5" y="8" width="17" height="11" rx="2.5"/><path d="M16 13.5h2"/>'),
    "card": _s('<rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M2.5 10h19M6.5 15h4"/>'),
    "network": _s('<circle cx="12" cy="5" r="2.5"/><circle cx="5" cy="18" r="2.5"/><circle cx="19" cy="18" r="2.5"/><path d="M12 7.5v4m0 0-5.5 4.5M12 11.5l5.5 4.5"/>'),
    "gift": _s('<rect x="3.5" y="9" width="17" height="4" rx="1"/><path d="M5 13v7h14v-7M12 9v11M12 9S10.5 4 8 4.5 7 9 12 9Zm0 0s1.5-5 4-4.5S17 9 12 9Z"/>'),
    "arrow": _s('<path d="M5 12h14m-6-6 6 6-6 6"/>'),
    "plus": _s('<path d="M12 5v14M5 12h14"/>'),
    "info": _s('<circle cx="12" cy="12" r="9"/><path d="M12 11v5m0-8h.01"/>'),
    "book": _s('<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5v-15Z"/><path d="M4 20.5A2.5 2.5 0 0 1 6.5 18H20v3H6.5"/>'),
    "link": _s('<path d="M10 14a4 4 0 0 0 5.66 0l3-3a4 4 0 0 0-5.66-5.66l-1 1"/><path d="M14 10a4 4 0 0 0-5.66 0l-3 3a4 4 0 0 0 5.66 5.66l1-1"/>'),
    "hash": _s('<path d="M5 9h14M5 15h14M10 3 8 21M16 3l-2 18"/>'),
    "plane": _s('<path d="M10.5 13.5 3 11l1.5-1.5 8 1 4-4.5a2 2 0 0 1 3 3l-4.5 4 1 8L14.5 22 12 14.5"/>'),
    "bag": _s('<path d="M5 8h14l-1 13H6L5 8Z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>'),
    "dining": _s('<path d="M7 3v8m-3-8v5a3 3 0 0 0 6 0V3M7 11v10M17 3c-2 0-3 2.5-3 6s1.5 4 3 4v8"/>'),
    "repeat": _s('<path d="M17 3l3 3-3 3"/><path d="M4 11V9a3 3 0 0 1 3-3h13M7 21l-3-3 3-3"/><path d="M20 13v2a3 3 0 0 1-3 3H4"/>'),
    "monitor": _s('<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8m-4-4v4"/>'),
    "search": _s('<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/>'),
    "scale": _s('<path d="M12 3v18M7 21h10M4 7h16M4 7l-2 6a3 3 0 0 0 4 0L4 7Zm16 0-2 6a3 3 0 0 0 4 0l-2-6Z"/>'),
    "eye": _s('<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>'),
    "bot": _s('<rect x="4" y="8" width="16" height="11" rx="3"/><path d="M12 4v4M9 13h.01M15 13h.01M9.5 16.5h5"/>'),
    "handshake": _s('<path d="m11 17 2 2a1.4 1.4 0 0 0 2-2"/><path d="m14 14 2.5 2.5a1.4 1.4 0 0 0 2-2L15 11l-1.5 1.5a2 2 0 0 1-3-3L13 7h3l3 3h2M3 10l3-3h4"/><path d="m3 10 7 7a1.4 1.4 0 0 0 2-2"/>'),
    "spark": _s('<path d="M12 3v4m0 10v4M3 12h4m10 0h4M6 6l2.5 2.5m7 7L18 18M6 18l2.5-2.5m7-7L18 6"/>'),
    "qr": _s('<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 14h3v3h-3zM20 14v.01M17 20h4v-3"/>'),
}

# ---------------------------------------------------------------- helpers
def img(name, alt, sizes, w_lg, h_lg, cls="", eager=False):
    """Responsive WebP <img> with sm (480w) and lg variants."""
    h_ratio = h_lg / w_lg
    loading = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (
        f'<img{c} src="assets/img/{name}-lg.webp" '
        f'srcset="assets/img/{name}-sm.webp 480w, assets/img/{name}-lg.webp {w_lg}w" '
        f'sizes="{sizes}" width="{w_lg}" height="{round(w_lg * h_ratio)}" alt="{html.escape(alt)}" {loading}>'
    )

IMAGES = {
    # name: (width, height) of the -lg variant
    "arshad-office": (960, 764),
    "arshad-gala": (960, 1369),
    "arshad-atlantis": (840, 1080),
    "arshad-yacht": (736, 786),
    "arshad-burj": (936, 1580),
    "arshad-tablet": (936, 1580),
    "arshad-palm": (736, 786),
    "team-dubai": (960, 717),
    "team-lounge": (1200, 894),
    "community-event": (1200, 894),
    "poster-copy-the-pros": (960, 1200),
    "poster-join-today": (960, 1200),
    "poster-your-future": (960, 1200),
    "poster-trade-smarter": (960, 1200),
    "poster-spend-crypto": (960, 1200),
}

def img_tag(match):
    # {{img:name|alt text|sizes|class|eager}}
    parts = match.group(1).split("|")
    name, alt = parts[0], parts[1]
    sizes = parts[2] if len(parts) > 2 and parts[2] else "100vw"
    cls = parts[3] if len(parts) > 3 else ""
    eager = len(parts) > 4 and parts[4] == "eager"
    w, h = IMAGES[name]
    return img(name, alt, sizes, w, h, cls, eager)


def head(meta):
    url = SITE_URL + meta["path"]
    og_img = SITE_URL + "/assets/img/og-image.jpg"
    graph = [
        {
            "@type": "Person",
            "@id": SITE_URL + "/#arshad",
            "name": "Arshad Siddique",
            "jobTitle": "Independent Bitget Affiliate",
            "description": "Independent Bitget affiliate based in Dubai, serving an international community. Not Bitget official.",
            "image": SITE_URL + "/assets/img/arshad-office-lg.webp",
            "url": SITE_URL + "/",
            "telephone": WA_DISPLAY.replace(" ", ""),
            "address": {"@type": "PostalAddress", "addressLocality": "Dubai", "addressCountry": "AE"},
        },
        {
            "@type": "WebSite",
            "@id": SITE_URL + "/#website",
            "url": SITE_URL + "/",
            "name": "Arshad Siddique · Independent Bitget Affiliate",
            "inLanguage": "en",
            "publisher": {"@id": SITE_URL + "/#arshad"},
        },
        {
            "@type": "WebPage",
            "@id": url + "#webpage",
            "url": url,
            "name": meta["title"],
            "description": meta["description"],
            "isPartOf": {"@id": SITE_URL + "/#website"},
            "about": {"@id": SITE_URL + "/#arshad"},
        },
    ]
    if meta["crumbs"]:
        graph.append({
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + p}
                for i, (n, p) in enumerate(meta["crumbs"])
            ],
        })
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    t = html.escape(meta["title"])
    d = html.escape(meta["description"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#050a18">
<meta name="author" content="Arshad Siddique">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Arshad Siddique · Independent Bitget Affiliate">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Arshad Siddique, independent Bitget affiliate, in Dubai">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{og_img}">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Poppins:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="assets/css/style.css">
<script>document.documentElement.classList.add("js")</script>
<script type="application/ld+json">{ld}</script>
"""


def header(active):
    def a(href, label, key=None):
        cur = ' aria-current="page"' if key and key == active else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="index.html" aria-label="Arshad Siddique, Independent Bitget Affiliate, home">
      <span class="brand-mark" aria-hidden="true">AS</span>
      <span class="brand-text"><span class="brand-name">Arshad Siddique</span><span class="brand-sub">Independent Bitget Affiliate</span></span>
    </a>
    <nav class="nav" id="site-nav" aria-label="Main">
      {a("index.html", "Home", "home")}
      {a("index.html#about", "About Arshad")}
      {a("bitget.html", "Why Bitget", "bitget")}
      {a("bitget.html#card", "Benefits")}
      {a("join.html#community", "Community", "join")}
      {a("join.html#how-to-join", "How to Join")}
      {a("join.html#contact", "Contact")}
      <a class="btn btn--whatsapp nav-mobile-only" href="{WA_URL}" target="_blank" rel="noopener noreferrer" data-track="whatsapp_click" data-track-loc="mobile_menu">{ICONS["whatsapp"]}Chat on WhatsApp</a>
    </nav>
    <div class="header-cta">
      <a class="btn btn--primary btn--sm" href="{REG_URL}" target="_blank" rel="noopener noreferrer" data-track="join_affiliate_click" data-track-loc="header">Join Now</a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Open menu"><span></span></button>
    </div>
  </div>
</header>
"""


def footer():
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a class="brand" href="index.html">
          <span class="brand-mark" aria-hidden="true">AS</span>
          <span class="brand-text"><span class="brand-name">Arshad Siddique</span><span class="brand-sub">Independent Bitget Affiliate</span></span>
        </a>
        <p>Based in Dubai, UAE · Serving an international community.</p>
        <div class="socials" data-socials style="margin-top:16px"></div>
      </div>
      <div>
        <h2>Explore</h2>
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="index.html#about">About Arshad</a></li>
          <li><a href="bitget.html">Why Bitget</a></li>
          <li><a href="bitget.html#card">Benefits</a></li>
          <li><a href="join.html#community">Community</a></li>
          <li><a href="join.html#how-to-join">How to Join</a></li>
          <li><a href="join.html#faq">FAQ</a></li>
        </ul>
      </div>
      <div>
        <h2>Join &amp; Contact</h2>
        <ul>
          <li><a class="ext" href="{REG_URL}" target="_blank" rel="noopener noreferrer" data-track="join_affiliate_click" data-track-loc="footer">Register on Bitget via Arshad</a></li>
          <li>Referral code: <strong class="accent">{REF_CODE}</strong></li>
          <li><a href="{WA_URL}" target="_blank" rel="noopener noreferrer" data-track="whatsapp_click" data-track-loc="footer">WhatsApp {WA_DISPLAY}</a></li>
          <li><a href="join.html#contact">Contact details</a></li>
        </ul>
      </div>
    </div>
    <div class="disclosure">
      <p><strong>Arshad Siddique is an independent Bitget affiliate and is not Bitget official.</strong> This website is not operated by Bitget and does not provide financial, investment or legal advice.</p>
      <p><strong>Risk disclosure:</strong> Crypto and derivatives trading involve substantial risk and may result in loss. Past performance does not guarantee future results. Products, promotions, rewards, card availability and eligibility are subject to Bitget's terms and applicable jurisdiction.</p>
    </div>
    <div class="copyright">
      <span>© <span data-year>2026</span> Arshad Siddique · Independent Bitget Affiliate · Dubai, UAE</span>
      <span>Bitget is a trademark of its respective owner.</span>
    </div>
  </div>
</footer>
<a class="wa-float" href="{WA_URL}" target="_blank" rel="noopener noreferrer" aria-label="Chat with Arshad on WhatsApp" data-track="whatsapp_click" data-track-loc="floating">{ICONS["whatsapp"]}<span class="wa-label">WhatsApp</span></a>
<script src="assets/js/main.js" defer></script>
</body>
</html>
"""


def render(body):
    body = re.sub(r"\{\{icon:([a-z-]+)\}\}", lambda m: ICONS[m.group(1)], body)
    body = re.sub(r"\{\{img:([^}]+)\}\}", img_tag, body)
    return (body.replace("{{REG_URL}}", REG_URL)
                .replace("{{REG_LABEL}}", REG_LABEL)
                .replace("{{REF_CODE}}", REF_CODE)
                .replace("{{WA_URL}}", WA_URL)
                .replace("{{WA_DISPLAY}}", WA_DISPLAY))


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")

    for fname, meta in PAGES.items():
        src = (SRC / fname).read_text(encoding="utf-8")
        extra_head = ""
        m = re.search(r"<!--HEAD(.*?)HEAD-->", src, re.S)
        if m:
            extra_head = m.group(1).strip() + "\n"
            src = src.replace(m.group(0), "")
        page = head(meta) + extra_head + "</head>\n<body>\n" + header(meta["nav"]) + render(src) + footer()
        assert "{{" not in page, f"Unrendered placeholder in {fname}"
        (OUT / fname).write_text(page, encoding="utf-8")
        print("built", fname)

    urls = "\n".join(
        f"  <url><loc>{SITE_URL}{m['path']}</loc><changefreq>monthly</changefreq><priority>{'1.0' if m['path'] == '/' else '0.8'}</priority></url>"
        for m in PAGES.values()
    )
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n',
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    print("SITE_URL =", SITE_URL)
    if "YOUR-DOMAIN" in SITE_URL:
        print("WARNING: SITE_URL is a placeholder. Set SITE_URL=https://your-domain before deploying.")


if __name__ == "__main__":
    main()
