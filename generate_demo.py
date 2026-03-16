#!/usr/bin/env python3
"""
Quiet Made — Demo Site Generator
工房URLを受け取り、スクレイピング → HTML デモサイト自動生成

Usage:
    python generate_demo.py --url https://www.tujiwa-kanaami.com --shop https://tsujiwa.base.shop
    python generate_demo.py --url https://example-workshop.com
"""

import os
import sys
import json
import argparse
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ── Optional: Claude API for intelligent extraction ──────────────────────────
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    print("[warn] anthropic package not found. Running without AI extraction.")

# ── Config ────────────────────────────────────────────────────────────────────
CLAUDE_MODEL = "claude-haiku-4-5-20251001"  # fast+cheap for extraction
OUTPUT_DIR   = Path(__file__).parent
HEADERS      = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    )
}

# ── 1. Scraper ────────────────────────────────────────────────────────────────

def fetch_page(url: str, timeout: int = 15) -> tuple[str, BeautifulSoup | None]:
    """Fetch a URL and return (raw_text, soup). Returns ('', None) on error."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        return r.text, soup
    except Exception as e:
        print(f"  [fetch error] {url}: {e}")
        return "", None


def extract_images(soup: BeautifulSoup, base_url: str) -> list[str]:
    """Return absolute image URLs from a page, filtering tiny icons."""
    imgs = []
    for tag in soup.find_all("img"):
        src = tag.get("src") or tag.get("data-src") or ""
        if not src or src.startswith("data:"):
            continue
        abs_url = urljoin(base_url, src)
        # Skip obvious icons/logos under 40px
        w = tag.get("width", "")
        h = tag.get("height", "")
        if w and int(re.sub(r"\D", "", w or "0") or 0) < 40:
            continue
        if h and int(re.sub(r"\D", "", h or "0") or 0) < 40:
            continue
        imgs.append(abs_url)
    return list(dict.fromkeys(imgs))  # dedupe, preserve order


def scrape_workshop(main_url: str, shop_url: str | None = None) -> dict:
    """
    Scrape workshop site(s) and return structured data dict.
    Falls back gracefully if pages are unavailable.
    """
    data = {
        "name_ja": "",
        "name_en": "",
        "tagline": "",
        "location": "",
        "phone": "",
        "hours": "",
        "instagram": "",
        "story_text": "",
        "images": [],
        "products": [],
        "raw_text": "",
    }

    # ── Main site ──
    print(f"[1/3] Fetching main site: {main_url}")
    raw, soup = fetch_page(main_url)
    if soup:
        data["raw_text"] = soup.get_text(separator="\n", strip=True)[:6000]
        data["images"] += extract_images(soup, main_url)

        # Title heuristic
        title = soup.find("title")
        if title:
            data["name_ja"] = title.get_text(strip=True).split("—")[0].split("|")[0].strip()

        # Phone
        phone_match = re.search(r"(?:TEL|Tel|電話|☎)[\s:：]*([0-9\-]{10,15})", raw)
        if phone_match:
            data["phone"] = phone_match.group(1)

        # Address / hours patterns
        addr_match = re.search(r"(?:〒\d{3}-\d{4}|京都|東京|大阪|愛知)[^\n]{5,60}", raw)
        if addr_match:
            data["location"] = addr_match.group(0).strip()

        hours_match = re.search(r"\d{1,2}:\d{2}[〜～\-]\d{1,2}:\d{2}", raw)
        if hours_match:
            data["hours"] = hours_match.group(0)

        # Instagram
        ig = re.search(r"instagram\.com/([\w.]+)", raw)
        if ig:
            data["instagram"] = f"https://www.instagram.com/{ig.group(1)}/"

    # ── Shop site (BASE, Shopify, etc.) ──
    if shop_url:
        print(f"[2/3] Fetching shop: {shop_url}")
        time.sleep(1)  # polite delay
        _, shop_soup = fetch_page(shop_url)
        if shop_soup:
            data["images"] += extract_images(shop_soup, shop_url)

            # Try to extract product names + prices
            for item in shop_soup.select("[class*='item'], [class*='product'], [class*='goods']"):
                name_el = item.select_one(
                    "h2, h3, [class*='name'], [class*='title'], [class*='item-name']"
                )
                price_el = item.select_one(
                    "[class*='price'], [class*='cost']"
                )
                if name_el:
                    product = {"name": name_el.get_text(strip=True), "price": ""}
                    if price_el:
                        product["price"] = price_el.get_text(strip=True)
                    data["products"].append(product)

    # Deduplicate images
    data["images"] = list(dict.fromkeys(data["images"]))
    print(f"  Found {len(data['images'])} images, {len(data['products'])} products")
    return data


# ── 2. Claude AI Extraction ───────────────────────────────────────────────────

def extract_with_claude(raw_data: dict) -> dict:
    """
    Use Claude to intelligently fill in workshop metadata from raw text.
    Only runs if ANTHROPIC_API_KEY is set and anthropic package is installed.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not CLAUDE_AVAILABLE or not api_key:
        print("[2b] Skipping Claude extraction (no API key or package).")
        return raw_data

    print("[2b] Running Claude extraction…")
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""以下は日本の工芸工房ウェブサイトから取得したテキストです。
このテキストから以下の情報をJSON形式で抽出してください。
情報がなければ空文字にしてください。英語が必要な場合は自然な翻訳を作成してください。

抽出項目:
- name_ja: 工房名（日本語）
- name_en: 工房名（英語 or ローマ字）
- tagline: キャッチコピー or 一行説明（英語）
- location: 所在地（例: Kyoto, Shimogyo-ku）
- craft_type: 工芸の種類（英語, 例: Wire Craft, Ceramics）
- story_short: 工房の説明2〜3文（英語）
- hero_keyword: ヒーローに使う漢字1文字（その工芸を象徴するもの）
- hero_sub: ヒーローサブコピー（日本語、15文字以内）
- process_steps: 制作工程4段階（各: name_ja, name_en, desc_ja）

テキスト（最大6000文字）:
{raw_data.get('raw_text', '')[:4000]}
"""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    text = message.content[0].text
    # Extract JSON block
    json_match = re.search(r"\{[\s\S]+\}", text)
    if json_match:
        try:
            enriched = json.loads(json_match.group(0))
            raw_data.update({k: v for k, v in enriched.items() if v})
            print("  Claude extraction successful.")
        except json.JSONDecodeError as e:
            print(f"  [warn] Could not parse Claude JSON: {e}")
    return raw_data


# ── 3. HTML Generator ─────────────────────────────────────────────────────────

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name_ja} — {name_en}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Noto+Serif+JP:wght@200;300;400&family=Bebas+Neue&display=swap" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
:root {{
  --black: #0a0908;
  --dark: #141210;
  --mid: #242018;
  --paper: #f2ede5;
  --gold: {accent_color};
  --stone: #7a7268;
}}
body {{
  background: var(--black);
  color: var(--paper);
  font-family: 'Noto Serif JP', serif;
  overflow-x: hidden;
}}
nav {{
  position: fixed; top: 0; left: 0; right: 0;
  z-index: 100; padding: 2rem 3rem;
  display: flex; justify-content: space-between; align-items: center;
  background: linear-gradient(to bottom, rgba(10,9,8,0.8) 0%, transparent 100%);
}}
.nav-logo {{
  font-family: 'Bebas Neue', sans-serif; font-size: 1.4rem;
  letter-spacing: 0.25em; color: var(--paper); text-decoration: none;
}}
.nav-logo span {{ color: var(--gold); }}
.nav-links {{ display: flex; gap: 2.5rem; list-style: none; }}
.nav-links a {{
  font-size: 0.62rem; letter-spacing: 0.3em; text-transform: uppercase;
  color: rgba(242,237,229,0.5); text-decoration: none; transition: color 0.3s;
}}
.nav-links a:hover {{ color: var(--paper); }}

.hero {{
  height: 100vh; position: relative; overflow: hidden;
  display: flex; align-items: center;
}}
.hero-slides {{ position: absolute; inset: 0; }}
.hero-slide {{
  position: absolute; inset: 0;
  background-size: cover; background-position: center;
  opacity: 0; transition: opacity 1.4s ease;
  filter: brightness(0.4) saturate(0.75);
}}
.hero-slide.active {{ opacity: 1; }}
.hero-slide-1 {{ background-image: url('{img0}'); background-color: var(--dark); }}
.hero-slide-2 {{ background-image: url('{img1}'); background-color: var(--dark); }}
.hero-slide-3 {{ background-image: url('{img2}'); background-color: var(--dark); }}
.hero-overlay {{
  position: absolute; inset: 0; z-index: 1;
  background: linear-gradient(135deg, rgba(10,9,8,0.7) 0%, rgba(10,9,8,0.3) 60%, rgba(10,9,8,0.65) 100%);
}}
.hero-content {{ position: relative; z-index: 2; padding: 0 3rem; width: 100%; }}
.hero-accent {{
  display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem;
  opacity: 0; animation: fadeIn 1s ease 0.5s forwards;
}}
.hero-slash {{ font-family: 'Bebas Neue', sans-serif; font-size: 1.5rem; color: var(--gold); }}
.hero-label {{ font-size: 0.62rem; letter-spacing: 0.4em; text-transform: uppercase; color: rgba(242,237,229,0.55); }}
.hero-keyword {{
  font-family: 'Bebas Neue', sans-serif; font-size: clamp(5rem, 15vw, 14rem);
  line-height: 0.85; color: var(--paper);
  opacity: 0; animation: fadeUp 1s ease 0.7s forwards;
}}
.hero-keyword .accent {{ color: var(--gold); }}
.hero-sub {{
  font-size: 1rem; font-weight: 300; color: rgba(242,237,229,0.65);
  margin-top: 1.5rem; letter-spacing: 0.18em;
  opacity: 0; animation: fadeUp 1s ease 1s forwards;
}}
.hero-scroll {{
  position: absolute; bottom: 3rem; right: 3rem; z-index: 2;
  display: flex; align-items: center; gap: 1rem;
  font-size: 0.6rem; letter-spacing: 0.3em; text-transform: uppercase;
  color: rgba(242,237,229,0.35); opacity: 0; animation: fadeIn 1s ease 1.5s forwards;
}}
.hero-scroll-line {{ width: 40px; height: 1px; background: var(--gold); }}
.hero-indicators {{
  position: absolute; bottom: 3rem; left: 3rem; z-index: 2;
  display: flex; gap: 0.5rem;
  opacity: 0; animation: fadeIn 1s ease 1.5s forwards;
}}
.indicator {{ width: 24px; height: 2px; background: rgba(242,237,229,0.2); cursor: pointer; transition: background 0.3s, width 0.3s; }}
.indicator.active {{ background: var(--gold); width: 40px; }}

.stats {{
  background: var(--mid); padding: 2.5rem 3rem; display: flex;
  border-top: 1px solid rgba(255,255,255,0.08);
  border-bottom: 1px solid rgba(255,255,255,0.08);
}}
.stat {{ flex: 1; padding: 0 2rem; border-right: 1px solid rgba(242,237,229,0.06); display: flex; align-items: center; gap: 1.5rem; }}
.stat:first-child {{ padding-left: 0; }}
.stat:last-child {{ border-right: none; }}
.stat-num {{ font-family: 'Bebas Neue', sans-serif; font-size: 2.8rem; color: var(--gold); line-height: 1; }}
.stat-text {{ display: flex; flex-direction: column; gap: 0.2rem; }}
.stat-label {{ font-size: 0.6rem; letter-spacing: 0.3em; text-transform: uppercase; color: rgba(242,237,229,0.35); }}
.stat-desc {{ font-size: 0.82rem; font-weight: 300; color: rgba(242,237,229,0.65); letter-spacing: 0.05em; }}

.section-num {{
  font-family: 'Bebas Neue', sans-serif; font-size: 0.75rem;
  letter-spacing: 0.4em; color: var(--gold); margin-bottom: 1rem;
  display: flex; align-items: center; gap: 0.75rem;
}}
.section-num::after {{ content: ''; height: 1px; width: 40px; background: var(--gold); }}

.story {{
  padding: 9rem 3rem; display: grid; grid-template-columns: 1fr 1fr;
  gap: 7rem; align-items: center; max-width: 1300px; margin: 0 auto;
}}
.story-heading {{
  font-family: 'Cormorant Garamond', serif; font-size: clamp(2.2rem, 4vw, 3.2rem);
  font-weight: 300; line-height: 1.35; color: var(--paper); margin-top: 1.5rem;
}}
.story-heading em {{ font-style: italic; color: var(--gold); }}
.story-body {{ font-size: 0.88rem; line-height: 2.2; color: rgba(242,237,229,0.5); font-weight: 300; margin-top: 2rem; letter-spacing: 0.06em; }}
.story-img-wrap {{ position: relative; }}
.story-img-wrap::before {{
  content: ''; position: absolute; top: -1.5rem; left: -1.5rem; right: 1.5rem; bottom: 1.5rem;
  border: 1px solid rgba(255,255,255,0.08); pointer-events: none;
}}
.story-img {{ width: 100%; aspect-ratio: 4/5; object-fit: cover; display: block; filter: sepia(0.1) contrast(1.05); }}

.works {{ padding: 0 3rem 9rem; max-width: 1300px; margin: 0 auto; }}
.works-header {{ display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 3rem; }}
.works-heading {{ font-family: 'Bebas Neue', sans-serif; font-size: clamp(2rem, 5vw, 4rem); letter-spacing: 0.05em; line-height: 1; }}
.works-link {{ font-size: 0.65rem; letter-spacing: 0.3em; text-transform: uppercase; color: var(--gold); text-decoration: none; border-bottom: 1px solid rgba(255,255,255,0.12); padding-bottom: 0.2rem; }}
.works-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }}
.work-card {{ cursor: pointer; overflow: hidden; }}
.work-card-img {{ width: 100%; aspect-ratio: 4/5; object-fit: cover; display: block; background: var(--mid); transition: transform 0.6s ease; filter: sepia(0.1) brightness(0.92); }}
.work-card:hover .work-card-img {{ transform: scale(1.04); filter: sepia(0) brightness(1); }}
.work-card-info {{ padding: 1.2rem 0 0; display: flex; justify-content: space-between; align-items: baseline; }}
.work-card-name {{ font-size: 0.82rem; font-weight: 300; letter-spacing: 0.08em; color: rgba(242,237,229,0.75); }}
.work-card-price {{ font-family: 'Cormorant Garamond', serif; font-size: 1rem; color: var(--gold); }}
.work-card-large {{ grid-column: span 2; }}
.work-card-large .work-card-img {{ aspect-ratio: 16/10; }}

.process {{ background: var(--dark); border-top: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05); }}
.process-inner {{ padding: 7rem 3rem; max-width: 1300px; margin: 0 auto; }}
.process-header {{ margin-bottom: 4rem; }}
.process-title {{ font-family: 'Bebas Neue', sans-serif; font-size: clamp(2rem, 5vw, 4rem); letter-spacing: 0.05em; margin-top: 0.5rem; }}
.process-steps {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0; }}
.process-step {{ padding: 2.5rem 2rem; border-right: 1px solid rgba(242,237,229,0.05); }}
.process-step:last-child {{ border-right: none; }}
.process-step-num {{ font-family: 'Bebas Neue', sans-serif; font-size: 4rem; color: rgba(255,255,255,0.06); line-height: 1; margin-bottom: 1.5rem; }}
.process-step-name {{ font-size: 1.1rem; font-weight: 300; color: var(--paper); margin-bottom: 0.3rem; letter-spacing: 0.1em; }}
.process-step-en {{ font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 0.8rem; color: var(--gold); margin-bottom: 1rem; }}
.process-step-desc {{ font-size: 0.8rem; line-height: 1.9; color: rgba(242,237,229,0.38); font-weight: 300; }}

.contact {{ padding: 9rem 3rem; max-width: 1300px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 8rem; align-items: start; }}
.contact-heading {{ font-family: 'Bebas Neue', sans-serif; font-size: clamp(3rem, 6vw, 5rem); letter-spacing: 0.05em; color: var(--paper); line-height: 1; margin-top: 1.5rem; }}
.contact-heading span {{ color: var(--gold); }}
.contact-body {{ font-size: 0.88rem; line-height: 2.1; color: rgba(242,237,229,0.45); font-weight: 300; margin-top: 2rem; }}
.contact-info {{ margin-top: 2rem; display: flex; flex-direction: column; gap: 0.6rem; }}
.contact-info-line {{ font-size: 0.75rem; letter-spacing: 0.1em; color: rgba(242,237,229,0.5); display: flex; gap: 1rem; }}
.contact-info-label {{ font-family: 'Bebas Neue', sans-serif; font-size: 0.6rem; letter-spacing: 0.3em; color: var(--gold); min-width: 50px; }}
.contact-form {{ display: flex; flex-direction: column; gap: 1.5rem; }}
.form-field {{ display: flex; flex-direction: column; gap: 0.6rem; }}
.form-field label {{ font-size: 0.6rem; letter-spacing: 0.35em; text-transform: uppercase; color: rgba(242,237,229,0.3); }}
.form-field input, .form-field textarea {{
  background: transparent; border: none; border-bottom: 1px solid rgba(242,237,229,0.1);
  padding: 0.8rem 0; font-family: 'Noto Serif JP', serif; font-size: 0.88rem;
  font-weight: 300; color: var(--paper); outline: none; transition: border-color 0.3s;
}}
.form-field input:focus, .form-field textarea:focus {{ border-color: var(--gold); }}
.form-field textarea {{ height: 100px; resize: none; }}
.form-submit {{
  align-self: flex-start; background: transparent; border: 1px solid var(--gold);
  color: var(--gold); padding: 1rem 2.5rem; font-family: 'Bebas Neue', sans-serif;
  font-size: 0.85rem; letter-spacing: 0.3em; cursor: pointer; transition: background 0.3s, color 0.3s;
}}
.form-submit:hover {{ background: var(--gold); color: var(--black); }}

footer {{
  background: var(--dark); padding: 3rem;
  display: flex; justify-content: space-between; align-items: center;
  border-top: 1px solid rgba(255,255,255,0.06);
}}
.footer-logo {{ font-family: 'Bebas Neue', sans-serif; font-size: 1.3rem; letter-spacing: 0.25em; }}
.footer-logo span {{ color: var(--gold); }}
.footer-copy {{ font-size: 0.62rem; letter-spacing: 0.15em; color: rgba(242,237,229,0.2); }}

.qm-badge {{
  position: fixed; bottom: 2rem; right: 2rem; z-index: 200;
  background: rgba(10,9,8,0.9); border: 1px solid rgba(255,255,255,0.1);
  padding: 0.75rem 1.25rem; text-align: center;
  backdrop-filter: blur(8px);
}}
.qm-badge-label {{ font-size: 0.45rem; letter-spacing: 0.4em; text-transform: uppercase; color: rgba(242,237,229,0.3); display: block; }}
.qm-badge-name {{ font-family: 'Bebas Neue', sans-serif; font-size: 0.75rem; letter-spacing: 0.3em; color: var(--gold); display: block; }}

@keyframes fadeUp {{ from {{ opacity:0; transform:translateY(28px); }} to {{ opacity:1; transform:none; }} }}
@keyframes fadeIn {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
.reveal {{ opacity:0; transform:translateY(30px); transition: opacity 0.9s ease, transform 0.9s ease; }}
.reveal.visible {{ opacity:1; transform:none; }}

@media (max-width: 768px) {{
  nav {{ padding: 1.5rem; }}
  .nav-links {{ display: none; }}
  .stats {{ flex-direction: column; gap: 1.5rem; padding: 2rem 1.5rem; }}
  .stat {{ border: none; border-bottom: 1px solid rgba(242,237,229,0.06); padding: 0 0 1.5rem; }}
  .story, .works-grid, .process-steps, .contact {{ grid-template-columns: 1fr; }}
  .story, .contact {{ gap: 3rem; padding: 5rem 1.5rem; }}
  .works {{ padding: 0 1.5rem 5rem; }}
  .work-card-large {{ grid-column: span 1; }}
  .work-card-large .work-card-img {{ aspect-ratio: 4/5; }}
  .process-inner {{ padding: 5rem 1.5rem; }}
  footer {{ flex-direction: column; gap: 1.5rem; text-align: center; }}
}}
</style>
</head>
<body>

<nav>
  <a href="#" class="nav-logo">{nav_name}</a>
  <ul class="nav-links">
    <li><a href="#story">工房</a></li>
    <li><a href="#works">作品</a></li>
    <li><a href="#process">制作工程</a></li>
    <li><a href="#contact">お問い合わせ</a></li>
  </ul>
</nav>

<section class="hero">
  <div class="hero-slides">
    <div class="hero-slide hero-slide-1 active"></div>
    <div class="hero-slide hero-slide-2"></div>
    <div class="hero-slide hero-slide-3"></div>
  </div>
  <div class="hero-overlay"></div>
  <div class="hero-content">
    <div class="hero-accent">
      <span class="hero-slash">/</span>
      <span class="hero-label">{name_en} — {location}</span>
    </div>
    <div class="hero-keyword" id="heroKeyword">
      {hero_keyword}<span class="accent">.</span>
    </div>
    <p class="hero-sub">{hero_sub}</p>
  </div>
  <div class="hero-scroll"><span class="hero-scroll-line"></span>Scroll</div>
  <div class="hero-indicators">
    <div class="indicator active" data-index="0"></div>
    <div class="indicator" data-index="1"></div>
    <div class="indicator" data-index="2"></div>
  </div>
</section>

<div class="stats reveal">
  <div class="stat"><span class="stat-num">{stat1_num}</span><div class="stat-text"><span class="stat-label">{stat1_label}</span><span class="stat-desc">{stat1_desc}</span></div></div>
  <div class="stat"><span class="stat-num">{stat2_num}</span><div class="stat-text"><span class="stat-label">{stat2_label}</span><span class="stat-desc">{stat2_desc}</span></div></div>
  <div class="stat"><span class="stat-num">{stat3_num}</span><div class="stat-text"><span class="stat-label">{stat3_label}</span><span class="stat-desc">{stat3_desc}</span></div></div>
  <div class="stat"><span class="stat-num">{stat4_num}</span><div class="stat-text"><span class="stat-label">{stat4_label}</span><span class="stat-desc">{stat4_desc}</span></div></div>
</div>

<section class="story" id="story">
  <div class="story-left reveal">
    <div class="section-num">01 / Story</div>
    <h2 class="story-heading">{story_heading}</h2>
    <p class="story-body">{story_body}</p>
  </div>
  <div class="story-right reveal">
    <div class="story-img-wrap">
      <img class="story-img" src="{story_img}" alt="{name_ja}" loading="lazy">
    </div>
  </div>
</section>

<section class="works" id="works">
  <div class="works-header reveal">
    <div>
      <div class="section-num">02 / Works</div>
      <h2 class="works-heading">Selected Products</h2>
    </div>
    <a href="{shop_url}" target="_blank" class="works-link">View All →</a>
  </div>
  <div class="works-grid">
{product_cards}
  </div>
</section>

<section class="process" id="process">
  <div class="process-inner">
    <div class="process-header reveal">
      <div class="section-num">03 / Process</div>
      <h2 class="process-title">The Craft</h2>
    </div>
    <div class="process-steps">
{process_steps}
    </div>
  </div>
</section>

<section class="contact" id="contact">
  <div class="reveal">
    <div class="section-num">04 / Contact</div>
    <h2 class="contact-heading">Get in<br><span>Touch</span></h2>
    <p class="contact-body">{contact_body}</p>
    <div class="contact-info">
      <div class="contact-info-line"><span class="contact-info-label">Address</span><span>{location}</span></div>
      <div class="contact-info-line"><span class="contact-info-label">Tel</span><span>{phone}</span></div>
      <div class="contact-info-line"><span class="contact-info-label">Hours</span><span>{hours}</span></div>
      <div class="contact-info-line"><span class="contact-info-label">SNS</span><span>{instagram}</span></div>
    </div>
  </div>
  <div class="contact-form reveal" style="transition-delay:0.15s">
    <div class="form-field"><label>Your Name</label><input type="text"></div>
    <div class="form-field"><label>Email</label><input type="email"></div>
    <div class="form-field"><label>Subject</label><input type="text"></div>
    <div class="form-field"><label>Message</label><textarea></textarea></div>
    <button class="form-submit">Send Message</button>
  </div>
</section>

<footer>
  <div class="footer-logo">{nav_name}</div>
  <p class="footer-copy">© {name_en}. All Rights Reserved.</p>
</footer>

<div class="qm-badge">
  <span class="qm-badge-label">Demo by</span>
  <span class="qm-badge-name">Quiet Made</span>
</div>

<script>
const kws = {keywords_json};
let ki = 0;
const kwEl = document.getElementById('heroKeyword');
setInterval(() => {{
  ki = (ki+1) % kws.length;
  kwEl.style.opacity = '0'; kwEl.style.transform = 'translateY(20px)';
  setTimeout(() => {{
    kwEl.innerHTML = kws[ki] + '<span class="accent">.</span>';
    kwEl.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    kwEl.style.opacity = '1'; kwEl.style.transform = 'none';
  }}, 400);
}}, 3200);

const slides = document.querySelectorAll('.hero-slide');
const inds   = document.querySelectorAll('.indicator');
let cur = 0;
function goTo(n) {{
  slides[cur].classList.remove('active'); inds[cur].classList.remove('active');
  cur = n; slides[cur].classList.add('active'); inds[cur].classList.add('active');
}}
inds.forEach((d,i) => d.addEventListener('click', () => goTo(i)));
setInterval(() => goTo((cur+1) % slides.length), 5000);

const obs = new IntersectionObserver(es => es.forEach(e => {{
  if (e.isIntersecting) {{ e.target.classList.add('visible'); obs.unobserve(e.target); }}
}}), {{threshold: 0.12}});
document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
</script>
</body>
</html>
"""


def pick_images(images: list[str], n: int = 10) -> list[str]:
    """Pick up to n images, preferring those likely to be product/hero shots."""
    scored = []
    for url in images:
        score = 0
        # Prefer larger images (item/ over w220/ thumbnails)
        if "/item/" in url: score += 3
        if "shop_photo" in url: score += 5
        if re.search(r"\.(jpg|jpeg|png|webp)$", url, re.I): score += 1
        # Avoid obvious thumbnails
        if "_s\." in url or "thumb" in url.lower(): score -= 2
        scored.append((score, url))
    scored.sort(reverse=True)
    return [url for _, url in scored[:n]]


def build_product_cards(products: list[dict], images: list[str]) -> str:
    """Generate HTML product card blocks."""
    cards = []
    # Use scraped products if available, else create placeholders from images
    items = products[:6] if products else []

    # Pad with image-only entries
    for i, img in enumerate(images[:6]):
        if i >= len(items):
            items.append({"name": f"Product {i+1}", "price": "", "image": img})
        elif "image" not in items[i]:
            items[i]["image"] = img

    for i, item in enumerate(items[:6]):
        large = "work-card-large" if i == 0 else ""
        delay = f'style="transition-delay:{i*0.05:.2f}s"' if i else ""
        img_src = item.get("image", "")
        name = item.get("name", "")
        price = item.get("price", "")
        price_html = f'<span class="work-card-price">{price}</span>' if price else ""
        cards.append(f"""\
    <div class="work-card {large} reveal" {delay}>
      <img class="work-card-img" src="{img_src}" alt="{name}" loading="lazy">
      <div class="work-card-info">
        <span class="work-card-name">{name}</span>{price_html}
      </div>
    </div>""")
    return "\n".join(cards)


def build_process_steps(steps: list[dict]) -> str:
    """Generate HTML process step blocks."""
    default_steps = [
        {"name_ja": "素材選び", "name_en": "Material Selection", "desc_ja": "最適な素材と技法を選ぶ。"},
        {"name_ja": "下準備",   "name_en": "Preparation",        "desc_ja": "素材を加工・形成する準備をする。"},
        {"name_ja": "製作",     "name_en": "Crafting",           "desc_ja": "職人が一点一点、手で仕上げる。"},
        {"name_ja": "仕上げ",   "name_en": "Finishing",          "desc_ja": "最終確認と磨き上げを行う。"},
    ]
    use_steps = steps[:4] if steps else default_steps
    # Pad if needed
    while len(use_steps) < 4:
        use_steps.append(default_steps[len(use_steps)])

    html = []
    for i, s in enumerate(use_steps[:4]):
        delay = f'style="transition-delay:{i*0.1}s"' if i else ""
        html.append(f"""\
      <div class="process-step reveal" {delay}>
        <div class="process-step-num">0{i+1}</div>
        <div class="process-step-name">{s.get('name_ja','')}</div>
        <div class="process-step-en">{s.get('name_en','')}</div>
        <div class="process-step-desc">{s.get('desc_ja','')}</div>
      </div>""")
    return "\n".join(html)


def build_nav_name(name_ja: str) -> str:
    """Turn workshop name into a nav logo with gold slash accent."""
    if len(name_ja) >= 4:
        mid = len(name_ja) // 2
        return f'{name_ja[:mid]}<span>/</span>{name_ja[mid:]}'
    return f'{name_ja}<span>/</span>'


def generate_html(data: dict, shop_url: str = "#") -> str:
    """Fill the HTML template with scraped/enriched data."""
    imgs = pick_images(data.get("images", []))

    # Product images for hero slides
    img0 = imgs[0] if len(imgs) > 0 else ""
    img1 = imgs[1] if len(imgs) > 1 else img0
    img2 = imgs[2] if len(imgs) > 2 else img0

    # Story image — pick a non-hero one if available
    story_img = imgs[3] if len(imgs) > 3 else img0

    # Products: merge scraped products with images
    products_with_imgs = []
    product_imgs = [i for i in imgs if "/item/" in i]
    for i, p in enumerate(data.get("products", [])[:6]):
        entry = dict(p)
        if not entry.get("image") and i < len(product_imgs):
            entry["image"] = product_imgs[i]
        products_with_imgs.append(entry)

    # Keywords for hero rotation
    craft_kw = data.get("hero_keyword", "技")
    keywords = [craft_kw, "技", "手", "匠"]

    # Defaults for missing fields
    name_ja   = data.get("name_ja", "工房")
    name_en   = data.get("name_en", "Workshop")
    location  = data.get("location", "Japan")
    phone     = data.get("phone", "—")
    hours     = data.get("hours", "—")
    instagram = data.get("instagram", "—")

    story_heading = data.get("story_heading",
        f"職人の手だけが<br><em>知っている形。</em>")
    story_body = data.get("story_body",
        f"{name_ja}の職人が、一点一点丁寧に手仕事で生み出す作品。<br>機械では出せない温かさと強さを持つ。")

    return HTML_TEMPLATE.format(
        name_ja       = name_ja,
        name_en       = name_en,
        nav_name      = build_nav_name(name_ja),
        location      = location,
        hero_keyword  = keywords[0],
        hero_sub      = data.get("hero_sub", "手仕事の、誇り。"),
        accent_color  = data.get("accent_color", "#b87333"),

        img0 = img0, img1 = img1, img2 = img2,
        story_img = story_img,

        stat1_num="京", stat1_label="Location",  stat1_desc=location,
        stat2_num="手", stat2_label="Handmade",   stat2_desc="すべて手仕事",
        stat3_num="0",  stat3_label="Shortcuts",  stat3_desc="妥協なき職人技",
        stat4_num="∞",  stat4_label="Unique",     stat4_desc="同じものはひとつもない",

        story_heading = story_heading,
        story_body    = story_body,

        shop_url       = shop_url or "#",
        product_cards  = build_product_cards(products_with_imgs, product_imgs),
        process_steps  = build_process_steps(data.get("process_steps", [])),

        contact_body = f"{name_ja}へのお問い合わせ・ご注文はこちらから。<br>海外からのお問い合わせも歓迎いたします。",
        phone        = phone,
        hours        = hours,
        instagram    = instagram,

        keywords_json = json.dumps(keywords),
    )


# ── 4. CLI entry point ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Quiet Made — Demo Site Generator")
    parser.add_argument("--url",    required=True, help="Workshop main URL")
    parser.add_argument("--shop",   default=None,  help="Online shop URL (BASE, Shopify, etc.)")
    parser.add_argument("--out",    default=None,  help="Output HTML filename (auto-generated if omitted)")
    parser.add_argument("--no-ai",  action="store_true", help="Skip Claude AI extraction")
    args = parser.parse_args()

    domain = urlparse(args.url).netloc.replace("www.", "").split(".")[0]
    out_name = args.out or f"{domain}-demo.html"
    out_path = OUTPUT_DIR / out_name

    print(f"\n{'='*50}")
    print(f"  Quiet Made — Demo Generator")
    print(f"  Target: {args.url}")
    print(f"  Output: {out_path}")
    print(f"{'='*50}\n")

    # Step 1: Scrape
    data = scrape_workshop(args.url, args.shop)

    # Step 2: AI enrichment
    if not args.no_ai:
        data = extract_with_claude(data)

    # Step 3: Generate HTML
    print("[3/3] Generating HTML…")
    html = generate_html(data, shop_url=args.shop or args.url)

    out_path.write_text(html, encoding="utf-8")
    print(f"\n✓ Demo saved to: {out_path}")
    print(f"  Open in browser: file://{out_path.resolve()}\n")


if __name__ == "__main__":
    main()
