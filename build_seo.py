#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_seo.py — Endüstri Yatırım Gündemi
--------------------------------------
posts.json'u okur ve Google'ın indeksleyebileceği SEO çıktılarını üretir:
  1) haber/<slug>.html   → her haber için gerçek, taranabilir statik sayfa
  2) sitemap.xml         → ana sayfa + tüm haber sayfaları
  3) robots.txt          → sitemap referansı ile

Kullanım:  python3 build_seo.py
(posts.json ve index.html ile ayni klasörde çalıştırın.)
"""

import json, os, html, datetime, urllib.parse, re

# ---- ayarlar ----------------------------------------------------------------
DOMAIN   = "https://www.endustriyatirim.com.tr"   # CNAME: www kanonik
POSTS    = "posts.json"
OUT_DIR  = "haber"        # statik haber sayfalari bu klasöre yazilir
SITE     = "Endüstri Yatırım Gündemi"

EMOJI  = {"yol":"🛣️","su":"💧","enerji":"⚡","osb":"🏭","bina":"🏥","uluslararasi":"🌍","sirket":"🏢"}
CATLABEL = {"yol":"YOL / ULAŞTIRMA","su":"SU & ATIKSU","enerji":"ENERJİ","osb":"OSB / SANAYİ",
            "bina":"BİNA","uluslararasi":"ULUSLARARASI","sirket":"ŞİRKET & EKONOMİ"}
CATHUE = {"yol":"#b0812a","su":"#2f7d84","enerji":"#c0662a","osb":"#565aa0",
          "bina":"#3a8064","uluslararasi":"#9a4f79","sirket":"#5c7089"}

TR_MONTHS = ["","Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz",
             "Ağustos","Eylül","Ekim","Kasım","Aralık"]

def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)

def slug_of(p):
    if p.get("slug"): return p["slug"]
    b = p.get("baslik","").lower()
    b = re.sub(r"[^a-z0-9ığüşöç]+","-",b); return b.strip("-")

def abs_img(gorsel, cat):
    """gorsel göreli 'images/..' → mutlak URL. Boşsa kategori kapak SVG'si."""
    g = (gorsel or "").strip()
    if g:
        if g.startswith("http"): return g
        return f"{DOMAIN}/{g.lstrip('/')}"
    return f"{DOMAIN}/images/_placeholder-{cat}.jpg"   # yoksa da OG boş kalmasin

def fmt_date(iso):
    try:
        d = datetime.datetime.fromisoformat(iso)
        return f"{d.day} {TR_MONTHS[d.month]} {d.year}"
    except Exception:
        return iso

def iso_date(iso):
    try:
        return datetime.datetime.fromisoformat(iso).date().isoformat()
    except Exception:
        return datetime.date.today().isoformat()

# ---- statik sayfa şablonu ---------------------------------------------------
PAGE_CSS = """
:root{--paper:#faf8f4;--card:#fff;--ink:#14202e;--ink-soft:#3c4a5a;--muted:#75828f;
--line:#e7e2d8;--navy:#0e2038;--amber-deep:#916a1f}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--paper);color:var(--ink);line-height:1.62;
font-family:"Inter",system-ui,-apple-system,Segoe UI,Roboto,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
img{display:block;max-width:100%}
.serif{font-family:"Source Serif 4",Georgia,serif}
.mono{font-family:"IBM Plex Mono",ui-monospace,monospace}
.wrap{max-width:760px;margin:0 auto;padding:0 22px}
.topbar{background:var(--navy);color:#c7d2df;font-size:12.5px}
.topbar .wrap{display:flex;align-items:center;justify-content:space-between;height:40px}
.mast{border-bottom:1px solid var(--line);background:var(--card)}
.mast .wrap{padding:18px 22px}
.mast .brand{font-weight:700;font-size:22px;letter-spacing:-.01em}
.mast .brand .dot{color:var(--amber-deep)}
.mast .tag{color:var(--muted);font-size:12.5px;margin-top:2px}
article{background:var(--card);border:1px solid var(--line);border-radius:14px;
margin:26px auto;padding:34px 34px 30px;border-left:5px solid var(--spine,#b0812a)}
.kicker{font-family:"IBM Plex Mono",monospace;font-size:12px;font-weight:600;
letter-spacing:.06em;text-transform:uppercase}
h1{font-family:"Source Serif 4",Georgia,serif;font-weight:700;font-size:31px;
line-height:1.22;margin:12px 0 14px;letter-spacing:-.01em}
.spot{font-size:18px;color:var(--ink-soft);font-weight:500;margin-bottom:16px}
.amet{display:flex;gap:10px;flex-wrap:wrap;color:var(--muted);font-size:13px;
font-family:"IBM Plex Mono",monospace;margin-bottom:20px}
.hero{border-radius:10px;overflow:hidden;margin-bottom:24px;border:1px solid var(--line)}
.hero img{width:100%;height:auto}
.body p{margin:0 0 16px;font-size:16.5px}
.detail{background:#faf8f2;border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:22px 0}
.detail .dt{font-family:"IBM Plex Mono",monospace;font-size:12px;font-weight:600;
letter-spacing:.06em;text-transform:uppercase;color:var(--amber-deep);margin-bottom:10px}
.detail .row{display:flex;gap:14px;padding:7px 0;border-top:1px solid var(--line);font-size:14.5px}
.detail .row:first-of-type{border-top:0}
.detail .k{flex:0 0 116px;color:var(--muted);font-weight:600}
.detail .v{flex:1}
.detail ul{margin:0;padding-left:18px}
.tags{display:flex;flex-wrap:wrap;gap:7px;margin:22px 0 4px}
.tags a{font-size:12px;color:var(--amber-deep);background:#f3e8cd;
border-radius:20px;padding:4px 11px}
.src{margin-top:22px;padding-top:16px;border-top:1px solid var(--line);
display:flex;justify-content:space-between;align-items:center;gap:14px;
color:var(--muted);font-size:13.5px;flex-wrap:wrap}
.li{display:inline-flex;align-items:center;gap:6px;color:#0a66c2;font-weight:600}
.li svg{width:17px;height:17px}
.cta{display:block;text-align:center;background:var(--navy);color:#fff;
border-radius:10px;padding:13px;margin:26px auto 0;max-width:760px;font-weight:600;font-size:14.5px}
.back{color:var(--muted);font-size:13.5px;font-weight:600}
footer{border-top:1px solid var(--line);background:var(--card);margin-top:30px;
padding:26px 0;color:var(--muted);font-size:12.5px}
footer .wrap{display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap}
@media(max-width:640px){article{padding:24px 20px}h1{font-size:25px}.spot{font-size:16px}}
"""

def detail_box(p):
    rows=[]
    def row(k,v): rows.append(f'<div class="row"><span class="k">{k}</span><span class="v">{v}</span></div>')
    if p.get("ikn"):   row("İKN", f'<span class="mono">{esc(p["ikn"])}</span>')
    if p.get("idare"): row("İdare", esc(p["idare"]))
    if p.get("yer"):   row("Yer", esc(p["yer"]))
    if p.get("kapsam"):
        lis="".join(f"<li>{esc(x)}</li>" for x in p["kapsam"])
        row("Kapsam", f"<ul>{lis}</ul>")
    if p.get("sure"):  row("Süre", esc(p["sure"]))
    if p.get("ihaleTarihi"): row("İhale Tarihi", esc(p["ihaleTarihi"]))
    if p.get("usul"):  row("Usul", esc(p["usul"]))
    if p.get("dokuman") and p["dokuman"] not in ("—","-",""):
        row("Doküman", f'<a href="{esc(p["dokuman"])}" target="_blank" rel="noopener" style="color:var(--amber-deep)">İhale dokümanı →</a>')
    if not (p.get("ikn") or p.get("idare") or p.get("kapsam")): return ""
    return f'<div class="detail"><div class="dt">İhale Bilgileri</div>{"".join(rows)}</div>'

LI_SVG = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.63-1.85 3.36-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29zM5.34 7.43a2.06 2.06 0 110-4.13 2.06 2.06 0 010 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.72v20.56C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.72V1.72C24 .77 23.2 0 22.22 0z"/></svg>'

def article_page(p):
    slug = slug_of(p)
    cat  = p.get("cat","sirket")
    url  = f"{DOMAIN}/haber/{slug}.html"
    img  = abs_img(p.get("gorsel"), cat)
    title = f'{p.get("baslik","")} — {SITE}'
    desc  = p.get("spot","") or (p.get("govde",[""])[0] if p.get("govde") else "")
    desc  = re.sub(r"\s+"," ",desc).strip()[:300]
    body  = "".join(f"<p>{esc(x)}</p>" for x in p.get("govde",[])) or f"<p>{esc(p.get('spot',''))}</p>"
    tags  = "".join(f"<a>{esc(t)}</a>" for t in p.get("hashtags",[]))
    hue   = CATHUE.get(cat,"#b0812a")
    catlbl= f'{EMOJI.get(cat,"📌")} {esc(p.get("kategori", CATLABEL.get(cat,"")))}'

    ld = {
        "@context":"https://schema.org","@type":"NewsArticle",
        "headline": p.get("baslik",""),
        "description": desc,
        "image":[img],
        "datePublished": p.get("tarih",""),
        "dateModified": p.get("tarih",""),
        "author":{"@type":"Organization","name":SITE},
        "publisher":{"@type":"Organization","name":SITE,
                     "url":DOMAIN},
        "mainEntityOfPage":{"@type":"WebPage","@id":url},
        "url":url,
    }
    ldjson = json.dumps(ld, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}"/>
<link rel="canonical" href="{esc(url)}"/>
<meta name="robots" content="index,follow,max-image-preview:large"/>
<meta property="og:type" content="article"/>
<meta property="og:site_name" content="{esc(SITE)}"/>
<meta property="og:title" content="{esc(p.get('baslik',''))}"/>
<meta property="og:description" content="{esc(desc)}"/>
<meta property="og:url" content="{esc(url)}"/>
<meta property="og:image" content="{esc(img)}"/>
<meta property="article:published_time" content="{esc(p.get('tarih',''))}"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{esc(p.get('baslik',''))}"/>
<meta name="twitter:description" content="{esc(desc)}"/>
<meta name="twitter:image" content="{esc(img)}"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600;8..60,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet"/>
<style>{PAGE_CSS}</style>
<script type="application/ld+json">{ldjson}</script>
</head>
<body>
<div class="topbar"><div class="wrap"><span class="mono">{esc(fmt_date(p.get('tarih','')))}</span><a href="{DOMAIN}/">endustriyatirim.com.tr</a></div></div>
<header class="mast"><div class="wrap">
  <a href="{DOMAIN}/"><div class="brand serif">Endüstri Yatırım<span class="dot">.</span></div></a>
  <div class="tag">İhale ve Yatırım Haberleri</div>
</div></header>

<main class="wrap">
  <article style="--spine:{hue}">
    <a class="back" href="{DOMAIN}/">← Tüm Haberler</a>
    <div class="kicker" style="color:{hue};margin-top:14px">{catlbl}</div>
    <h1>{esc(p.get('baslik',''))}</h1>
    <p class="spot">{esc(p.get('spot',''))}</p>
    <div class="amet"><span>{esc(fmt_date(p.get('tarih','')))}</span><span>·</span><span>{esc(p.get('kaynak',''))}</span></div>
    <div class="hero"><img src="{esc(img)}" alt="{esc(p.get('baslik',''))}" width="900" height="506"/></div>
    <div class="body">{body}</div>
    {detail_box(p)}
    <div class="tags">{tags}</div>
    <div class="src">
      <span>Kaynak: {esc(p.get('kaynak','—'))}</span>
      <a class="li" href="{esc(p.get('linkedinUrl','https://www.linkedin.com/company/endustriyatirim'))}" target="_blank" rel="noopener">{LI_SVG} LinkedIn'de görüntüle</a>
    </div>
  </article>
  <a class="cta" href="{DOMAIN}/#haber/{esc(slug)}">Bu haberi portalda aç →</a>
</main>

<footer><div class="wrap">
  <span>© {datetime.date.today().year} {esc(SITE)}</span>
  <span><a href="{DOMAIN}/">Ana sayfa</a></span>
</div></footer>
</body>
</html>"""

# ---- sitemap + robots -------------------------------------------------------
def build_sitemap(posts):
    today = datetime.date.today().isoformat()
    urls = [(f"{DOMAIN}/", today, "1.0", "hourly")]
    for p in posts:
        urls.append((f"{DOMAIN}/haber/{slug_of(p)}.html", iso_date(p.get("tarih","")), "0.8", "monthly"))
    body = "".join(
        f"  <url>\n    <loc>{esc(u)}</loc>\n    <lastmod>{lm}</lastmod>\n"
        f"    <changefreq>{cf}</changefreq>\n    <priority>{pr}</priority>\n  </url>\n"
        for (u, lm, pr, cf) in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{body}</urlset>\n")

def build_robots():
    return ("User-agent: *\n"
            "Allow: /\n\n"
            f"Sitemap: {DOMAIN}/sitemap.xml\n")

# ---- çalıştır ---------------------------------------------------------------
def main():
    posts = json.load(open(POSTS, encoding="utf-8"))
    os.makedirs(OUT_DIR, exist_ok=True)
    for p in posts:
        slug = slug_of(p)
        with open(os.path.join(OUT_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
            f.write(article_page(p))
    with open("sitemap.xml","w",encoding="utf-8") as f: f.write(build_sitemap(posts))
    with open("robots.txt","w",encoding="utf-8") as f: f.write(build_robots())
    print(f"OK  {len(posts)} haber sayfasi → {OUT_DIR}/")
    print("OK  sitemap.xml")
    print("OK  robots.txt")

if __name__ == "__main__":
    main()
