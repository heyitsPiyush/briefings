import os
import json
import datetime
import feedparser
import google.generativeai as genai
from pathlib import Path
from sources import SOURCES

# ── Config ────────────────────────────────────────────────────────────────────
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash-lite")

TODAY = datetime.date.today()
DOCS_DIR = Path("docs")
ARCHIVE_DIR = DOCS_DIR / "archive"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

# ── Fetch RSS feeds ────────────────────────────────────────────────────────────
def fetch_feeds(sources: dict) -> dict:
    """Fetch and return articles grouped by category."""
    results = {}
    for category, feeds in sources.items():
        articles = []
        for url in feeds:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]:  # top 5 per feed
                    articles.append({
                        "title": entry.get("title", ""),
                        "summary": entry.get("summary", entry.get("description", ""))[:500],
                        "link": entry.get("link", ""),
                        "published": entry.get("published", ""),
                    })
            except Exception as e:
                print(f"[WARN] Failed to fetch {url}: {e}")
        results[category] = articles
    return results

# ── Summarize with Gemini ──────────────────────────────────────────────────────
def summarize(category: str, articles: list, depth: str) -> dict:
    """Ask Gemini to summarize articles for a given category."""
    if not articles:
        return {"summary": "No articles found today.", "links": []}

    articles_text = "\n\n".join(
        f"Title: {a['title']}\nSummary: {a['summary']}\nURL: {a['link']}"
        for a in articles
    )

    depth_instruction = {
        "deep": "Provide a detailed technical analysis with specific findings, techniques, CVEs, tools, or researcher insights. Go deep — this reader is an expert practitioner.",
        "moderate": "Provide a solid overview with key details. Include specific names, versions, or numbers where relevant.",
        "broad": "Provide a concise high-level overview. Highlight only the most important developments."
    }.get(depth, "moderate")

    prompt = f"""You are a cybersecurity and technology research analyst writing a daily briefing.

Category: {category}
Depth: {depth_instruction}

Articles:
{articles_text}

Instructions:
- Write a cohesive narrative summary (not bullet points) in 2-4 paragraphs
- Highlight the most significant items with specific details
- End with a "Key Links" section listing the 3-5 most important URLs
- Format the Key Links as: [Title](URL)
- Do not include fluff or filler phrases

Respond in this exact JSON format:
{{
  "summary": "your summary paragraphs here",
  "links": [
    {{"title": "Article title", "url": "https://..."}}
  ]
}}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        print(f"[ERROR] Gemini failed for {category}: {e}")
        return {
            "summary": "Summary unavailable today.",
            "links": [{"title": a["title"], "url": a["link"]} for a in articles[:3]]
        }

# ── Build HTML page ────────────────────────────────────────────────────────────
def build_html(date: datetime.date, sections: dict, is_today: bool = True) -> str:
    """Generate the HTML digest page."""
    date_str = date.strftime("%B %d, %Y")
    date_iso = date.isoformat()

    # Category display config
    category_meta = {
        "bug_bounty":       {"icon": "🐛", "label": "Bug Bounty",          "depth": "deep"},
        "hardware_hacking": {"icon": "⚙️", "label": "Hardware Hacking",    "depth": "deep"},
        "exploit_dev":      {"icon": "💥", "label": "Exploit Development",  "depth": "deep"},
        "cve_threats":      {"icon": "🔍", "label": "CVE & Threat Analysis","depth": "moderate"},
        "ai_cyber":         {"icon": "🤖", "label": "AI × Cybersecurity",   "depth": "deep"},
        "ai_tech":          {"icon": "💡", "label": "AI & Tech",            "depth": "moderate"},
        "finance":          {"icon": "💰", "label": "Business & Finance",   "depth": "broad"},
        "geopolitics":      {"icon": "🌍", "label": "Geopolitics & Policy", "depth": "broad"},
        "science":          {"icon": "🔬", "label": "Science & Research",   "depth": "broad"},
    }

    sections_html = ""
    for key, data in sections.items():
        meta = category_meta.get(key, {"icon": "📌", "label": key, "depth": "moderate"})
        summary_html = data["summary"].replace("\n\n", "</p><p>")
        links_html = "".join(
            f'<a href="{l["url"]}" target="_blank" rel="noopener">'
            f'<span class="link-arrow">↗</span>{l["title"]}</a>'
            for l in data.get("links", [])
        )
        depth_badge = meta["depth"]
        sections_html += f"""
        <section class="section depth-{depth_badge}">
          <div class="section-header">
            <span class="section-icon">{meta["icon"]}</span>
            <h2>{meta["label"]}</h2>
            <span class="depth-badge">{depth_badge}</span>
          </div>
          <div class="section-body">
            <p>{summary_html}</p>
          </div>
          <div class="section-links">
            {links_html}
          </div>
        </section>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <meta name="robots" content="noindex, nofollow"/>
  <title>Briefing — {date_iso}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #0d0f0e;
      --surface: #131614;
      --border: #1e2320;
      --border-bright: #2a302c;
      --text: #c8d4c9;
      --text-dim: #5a6b5c;
      --text-bright: #e8f0e9;
      --accent: #4ade80;
      --accent-dim: #166534;
      --red: #f87171;
      --amber: #fbbf24;
      --blue: #60a5fa;
      --mono: 'IBM Plex Mono', monospace;
      --serif: 'Libre Baskerville', serif;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: var(--serif);
      font-size: 16px;
      line-height: 1.75;
      min-height: 100vh;
    }}

    /* ── Header ── */
    header {{
      border-bottom: 1px solid var(--border);
      padding: 2rem 0 1.5rem;
      position: sticky;
      top: 0;
      background: rgba(13,15,14,0.95);
      backdrop-filter: blur(8px);
      z-index: 100;
    }}
    .header-inner {{
      max-width: 860px;
      margin: 0 auto;
      padding: 0 2rem;
      display: flex;
      align-items: baseline;
      gap: 1.5rem;
    }}
    .header-label {{
      font-family: var(--mono);
      font-size: 0.65rem;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--accent);
    }}
    .header-date {{
      font-family: var(--mono);
      font-size: 0.8rem;
      color: var(--text-dim);
      margin-left: auto;
    }}

    /* ── Nav ── */
    nav {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      overflow-x: auto;
      scrollbar-width: none;
    }}
    nav::-webkit-scrollbar {{ display: none; }}
    .nav-inner {{
      max-width: 860px;
      margin: 0 auto;
      padding: 0 2rem;
      display: flex;
      gap: 0;
    }}
    nav a {{
      font-family: var(--mono);
      font-size: 0.7rem;
      color: var(--text-dim);
      text-decoration: none;
      padding: 0.75rem 1rem;
      white-space: nowrap;
      border-bottom: 2px solid transparent;
      transition: color 0.15s, border-color 0.15s;
    }}
    nav a:hover {{ color: var(--text-bright); border-color: var(--accent); }}

    /* ── Main ── */
    main {{
      max-width: 860px;
      margin: 0 auto;
      padding: 3rem 2rem 6rem;
    }}

    /* ── Section ── */
    .section {{
      border: 1px solid var(--border);
      border-radius: 4px;
      margin-bottom: 2rem;
      overflow: hidden;
      transition: border-color 0.2s;
    }}
    .section:hover {{ border-color: var(--border-bright); }}
    .section-header {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 1rem 1.5rem;
      background: var(--surface);
      border-bottom: 1px solid var(--border);
    }}
    .section-icon {{ font-size: 1.1rem; }}
    .section-header h2 {{
      font-family: var(--mono);
      font-size: 0.85rem;
      font-weight: 500;
      letter-spacing: 0.05em;
      color: var(--text-bright);
    }}
    .depth-badge {{
      margin-left: auto;
      font-family: var(--mono);
      font-size: 0.6rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      padding: 0.2rem 0.5rem;
      border-radius: 2px;
    }}
    .depth-deep .depth-badge {{ background: rgba(248,113,113,0.1); color: var(--red); border: 1px solid rgba(248,113,113,0.2); }}
    .depth-moderate .depth-badge {{ background: rgba(251,191,36,0.1); color: var(--amber); border: 1px solid rgba(251,191,36,0.2); }}
    .depth-broad .depth-badge {{ background: rgba(96,165,250,0.1); color: var(--blue); border: 1px solid rgba(96,165,250,0.2); }}

    .section-body {{
      padding: 1.5rem;
      font-size: 0.95rem;
      color: var(--text);
    }}
    .section-body p + p {{ margin-top: 1rem; }}

    .section-links {{
      padding: 1rem 1.5rem;
      border-top: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
    }}
    .section-links a {{
      font-family: var(--mono);
      font-size: 0.72rem;
      color: var(--text-dim);
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      transition: color 0.15s;
    }}
    .section-links a:hover {{ color: var(--accent); }}
    .link-arrow {{ color: var(--accent); }}

    /* ── Archive ── */
    .archive-bar {{
      font-family: var(--mono);
      font-size: 0.7rem;
      color: var(--text-dim);
      margin-bottom: 2.5rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}
    .archive-bar span {{ color: var(--border-bright); }}
    .archive-bar a {{
      color: var(--text-dim);
      text-decoration: none;
      padding: 0.2rem 0.4rem;
      border: 1px solid var(--border);
      border-radius: 2px;
      transition: color 0.15s, border-color 0.15s;
    }}
    .archive-bar a:hover {{ color: var(--accent); border-color: var(--accent-dim); }}

    /* ── Footer ── */
    footer {{
      border-top: 1px solid var(--border);
      padding: 1.5rem 2rem;
      max-width: 860px;
      margin: 0 auto;
      font-family: var(--mono);
      font-size: 0.65rem;
      color: var(--text-dim);
      display: flex;
      justify-content: space-between;
    }}

    @media (max-width: 600px) {{
      .header-inner, .nav-inner, main, footer {{ padding-left: 1rem; padding-right: 1rem; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-inner">
      <span class="header-label">Daily Briefing</span>
      <span class="header-date">{date_str}</span>
    </div>
  </header>
  <nav>
    <div class="nav-inner">
      <a href="#bug_bounty">Bug Bounty</a>
      <a href="#hardware_hacking">Hardware</a>
      <a href="#exploit_dev">Exploits</a>
      <a href="#cve_threats">CVE</a>
      <a href="#ai_cyber">AI×Cyber</a>
      <a href="#ai_tech">AI & Tech</a>
      <a href="#finance">Finance</a>
      <a href="#geopolitics">Geopolitics</a>
      <a href="#science">Science</a>
    </div>
  </nav>
  <main>
    <div class="archive-bar">
      ARCHIVE <span>·</span>
      {{ARCHIVE_LINKS}}
    </div>
    {sections_html}
  </main>
  <footer>
    <span>generated {date_iso}</span>
    <span>gemini-2.5-flash-lite · rss feeds</span>
  </footer>
</body>
</html>"""

# ── Archive index ──────────────────────────────────────────────────────────────
def get_archive_links(current_date: datetime.date) -> str:
    """Generate archive links for the last 15 days."""
    links = []
    for i in range(1, 16):
        d = current_date - datetime.timedelta(days=i)
        path = ARCHIVE_DIR / f"{d.isoformat()}.html"
        if path.exists():
            links.append(f'<a href="archive/{d.isoformat()}.html">{d.strftime("%b %d")}</a>')
    return " ".join(links) if links else "<span>no archive yet</span>"

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"[INFO] Running digest for {TODAY}")

    # 1. Fetch all feeds
    print("[INFO] Fetching RSS feeds...")
    raw = fetch_feeds(SOURCES)

    # 2. Summarize each category
    print("[INFO] Summarizing with Gemini...")
    depth_map = {
        "bug_bounty": "deep",
        "hardware_hacking": "deep",
        "exploit_dev": "deep",
        "cve_threats": "moderate",
        "ai_cyber": "deep",
        "ai_tech": "moderate",
        "finance": "broad",
        "geopolitics": "broad",
        "science": "broad",
    }
    sections = {}
    for category, articles in raw.items():
        print(f"  → {category} ({len(articles)} articles)")
        sections[category] = summarize(category, articles, depth_map.get(category, "moderate"))

    # 3. Build archive links
    archive_links = get_archive_links(TODAY)

    # 4. Generate HTML
    html = build_html(TODAY, sections)
    html = html.replace("{ARCHIVE_LINKS}", archive_links)

    # 5. Save today as index.html and archive
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
    (ARCHIVE_DIR / f"{TODAY.isoformat()}.html").write_text(html, encoding="utf-8")

    # 6. Clean up old archive (keep 15 days)
    all_archive = sorted(ARCHIVE_DIR.glob("*.html"))
    for old in all_archive[:-15]:
        old.unlink()
        print(f"[INFO] Removed old archive: {old.name}")

    print(f"[DONE] Digest saved → docs/index.html + docs/archive/{TODAY.isoformat()}.html")

if __name__ == "__main__":
    main()
