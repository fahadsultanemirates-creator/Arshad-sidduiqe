# Arshad Siddique · Independent Bitget Affiliate — Website

A small, fast, static website (3 pages) for Arshad Siddique, an independent Bitget affiliate based in Dubai.
Arshad Siddique is an independent Bitget affiliate and is not Bitget official.

## Pages

| File | Route | Content |
|------|-------|---------|
| `src/pages/index.html` | `/` | Hero, About Arshad, Team mosaic, Why Bitget preview, CTA with QR + referral code |
| `src/pages/bitget.html` | `/bitget.html` | Bitget ecosystem features, Wallet Card, Copy Trading, Affiliate program, Welcome rewards |
| `src/pages/join.html` | `/join.html` | Community photo story, "What brings you here?" selector, How to Join, campaign creatives, FAQ, Contact |

The shared head (SEO tags, structured data), header, footer, floating WhatsApp button and icons live in `scripts/build.py`.

## Build

No dependencies beyond Python 3.

```bash
SITE_URL=https://your-domain.com python3 scripts/build.py
```

Output goes to `public/` (deploy that folder). `SITE_URL` is used for canonical URLs, Open Graph tags, structured data, `sitemap.xml` and `robots.txt` — **set it to the real domain before deploying**.

Preview locally:

```bash
cd public && python3 -m http.server 8000
```

## Editing

- Registration link, referral code and WhatsApp number: constants at the top of `scripts/build.py`.
- Social media links: `CONFIG.social` in `assets/js/main.js` (links stay hidden until a URL is filled in).
- Images: `assets/img/*-sm.webp` (480px) and `*-lg.webp`; sizes are listed in `IMAGES` in `scripts/build.py`.
- To add a new photo: create `name-sm.webp` and `name-lg.webp`, add it to `IMAGES`, then use `{{img:name|alt text|sizes}}` in a page.

## Analytics hooks

Clicks on elements with `data-track` fire a `site:track` DOM event and push to `window.dataLayer` **only if** an analytics tool created it (after consent). Events: `join_affiliate_click`, `whatsapp_click`, `qr_view`, `referral_code_copy`, `explore_bitget_click`, `copy_trading_interest`, `card_interest`, `affiliate_interest`. No tracking is installed.

## Deploy

`netlify.toml` is included (build command + `public` publish dir + security headers). Any static host works (Netlify, Vercel, GitHub Pages, Cloudflare Pages).
