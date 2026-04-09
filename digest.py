import os
import re
import datetime
from pathlib import Path
from google import genai
from google.genai import types

# ── Config ────────────────────────────────────────────────────────────────────
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

TODAY = datetime.date.today()
DOCS_DIR = Path("docs")
ARCHIVE_DIR = DOCS_DIR / "archive"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

# ── Markdown → clean HTML ─────────────────────────────────────────────────────
def md_to_html(text: str) -> str:
    """Convert Gemini markdown output to safe inline HTML."""
    # Remove horizontal rules
    text = re.sub(r'\n?---+\n?', '\n', text)
    # Bold **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    # Italic *text* or _text_
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    # Inline code `code`
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    # Headers → bold paragraph
    text = re.sub(r'^#{1,4}\s+(.+)$', r'<strong>\1</strong>', text, flags=re.MULTILINE)
    # Bullet points → inline with dash
    text = re.sub(r'^\s*[\*\-]\s+', '• ', text, flags=re.MULTILINE)
    # Numbered lists → keep number
    text = re.sub(r'^\s*\d+\.\s+', lambda m: m.group(0).strip() + ' ', text, flags=re.MULTILINE)
    # Paragraph breaks
    text = re.sub(r'\n{2,}', '</p><p>', text)
    text = re.sub(r'\n', ' ', text)
    return text.strip()

# ── Topic Definitions ─────────────────────────────────────────────────────────
TOPICS = [
    {
        "key": "bug_bounty",
        "icon": "🐛",
        "label": "Bug Bounty",
        "depth": "deep",
        "prompt": """Search Google for the latest bug bounty news as of {date}.
Find recent vulnerability disclosures, researcher writeups, HackerOne/Bugcrowd/Intigriti 
program updates, notable payouts, and new researcher techniques.

Write EXACTLY 2 short paragraphs (4-5 sentences each). Be specific: name vulnerabilities,
affected systems, CVSS scores, researcher names. NO bullet points. NO markdown headers.
NO bold text. Plain prose only. Keep total response under 200 words."""
    },
    {
        "key": "hardware_hacking",
        "icon": "⚙️",
        "label": "Hardware Hacking",
        "depth": "deep",
        "prompt": """Search Google for the latest hardware hacking and embedded security news as of {date}.
Find firmware vulnerabilities, IoT security research, side-channel attacks, fault injection,
RF hacking, supply chain security, and new hardware hacking tools or publications.

Write EXACTLY 2 short paragraphs (4-5 sentences each). Be specific: name chips,
architectures, attack vectors, and affected devices. NO bullet points. NO markdown headers.
NO bold text. Plain prose only. Keep total response under 200 words."""
    },
    {
        "key": "exploit_dev",
        "icon": "💥",
        "label": "Exploit Development",
        "depth": "deep",
        "prompt": """Search Google for the latest exploit development news as of {date}.
Find new exploit techniques, public PoC releases, kernel/browser exploits, memory corruption
research, mitigation bypasses, CTF writeups, and Project Zero or ZDI publications.

Write EXACTLY 2 short paragraphs (4-5 sentences each). Be specific: name CVEs, affected
versions, exploit primitives. NO bullet points. NO markdown headers. NO bold text.
Plain prose only. Keep total response under 200 words."""
    },
    {
        "key": "cve_threats",
        "icon": "🔍",
        "label": "CVE & Threat Analysis",
        "depth": "moderate",
        "prompt": """Search Google for today's most critical CVEs and active threat intelligence as of {date}.
Find high/critical severity CVEs being exploited, CISA KEV additions, active threat actor
campaigns, ransomware activity, and significant malware campaigns.

Write EXACTLY 2 short paragraphs (4-5 sentences each). Name specific CVE IDs, CVSS scores,
affected products, threat actors. NO bullet points. NO markdown headers. NO bold text.
Plain prose only. Keep total response under 200 words."""
    },
    {
        "key": "ai_cyber",
        "icon": "🤖",
        "label": "AI × Cybersecurity",
        "depth": "deep",
        "prompt": """Search Google for the latest AI and cybersecurity intersection news as of {date}.
Find LLM vulnerabilities, prompt injection research, AI-powered attacks, defensive AI tools,
AI red teaming findings, and research on securing AI pipelines or RAG systems.

Write EXACTLY 2 short paragraphs (4-5 sentences each). Name models, attack techniques,
researchers, organizations. NO bullet points. NO markdown headers. NO bold text.
Plain prose only. Keep total response under 200 words."""
    },
    {
        "key": "ai_tech",
        "icon": "💡",
        "label": "AI & Tech",
        "depth": "moderate",
        "prompt": """Search Google for the most important AI and technology news as of {date}.
Find major model releases, research breakthroughs, significant funding or acquisitions,
developer tool updates, and AI policy or regulation news.

Write EXACTLY 2 short paragraphs (4-5 sentences each). Be specific with model names,
company names, dollar amounts. NO bullet points. NO markdown headers. NO bold text.
Plain prose only. Keep total response under 200 words."""
    },
    {
        "key": "finance",
        "icon": "💰",
        "label": "Business & Finance",
        "depth": "broad",
        "prompt": """Search Google for today's most important global business and finance news as of {date}.
Find market movements, major earnings or M&A, central bank decisions, commodity prices,
and key macroeconomic developments.

Write EXACTLY 2 short paragraphs (4-5 sentences each). Include specific index levels,
percentages, company names. NO bullet points. NO markdown headers. NO bold text.
Plain prose only. Keep total response under 150 words."""
    },
    {
        "key": "geopolitics",
        "icon": "🌍",
        "label": "Geopolitics & Policy",
        "depth": "broad",
        "prompt": """Search Google for today's most important geopolitical news as of {date}.
Cover three areas: (1) Nepal — political developments, economy, government decisions,
(2) Canada — federal politics, US-Canada relations, major policy decisions,
(3) Global — significant conflicts, diplomacy, elections, UN developments.

Write EXACTLY 3 short paragraphs, one per area (3-4 sentences each). Be specific with
names and locations. NO bullet points. NO markdown headers. NO bold text.
Plain prose only. Keep total response under 200 words."""
    },
    {
        "key": "science",
        "icon": "🔬",
        "label": "Science & Research",
        "depth": "broad",
        "prompt": """Search Google for today's most notable science and research news as of {date}.
Find breakthrough papers, space exploration news, medical research advances,
climate science developments, and notable discoveries in physics or biology.

Write EXACTLY 2 short paragraphs (4-5 sentences each). Name researchers, institutions,
journals where possible. NO bullet points. NO markdown headers. NO bold text.
Plain prose only. Keep total response under 150 words."""
    },
]

# ── Fetch + Summarize via Gemini Search Grounding ─────────────────────────────
def fetch_and_summarize(topic: dict) -> dict:
    """Single Gemini call that searches + summarizes a topic."""
    prompt = topic["prompt"].format(date=TODAY.strftime("%B %d, %Y"))

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=1.0,
                max_output_tokens=600,   # tight cap to enforce brevity
            )
        )

        raw = response.text.strip() if response.text else ""
        print(f"     raw length: {len(raw)} chars")

        if not raw:
            print(f"     [WARN] empty response — retrying without grounding...")
            # Fallback: ask without search grounding using training knowledge
            fallback = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt.replace("Search Google for", "Based on your knowledge, summarize"),
                config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=400)
            )
            raw = fallback.text.strip() if fallback.text else "No content available today."

        # Convert markdown to clean HTML
        summary_html = md_to_html(raw)

        # Extract grounding source links
        links = []
        try:
            chunks = response.candidates[0].grounding_metadata.grounding_chunks
            for chunk in chunks:
                if hasattr(chunk, "web") and chunk.web.uri:
                    links.append({
                        "title": chunk.web.title or chunk.web.uri,
                        "url": chunk.web.uri
                    })
            print(f"     links: {len(links)}")
        except Exception as e:
            print(f"     grounding metadata unavailable: {e}")

        return {"summary": summary_html, "links": links[:6]}

    except Exception as e:
        print(f"  [ERROR] {topic['key']}: {type(e).__name__}: {e}")
        return {"summary": f"Unavailable today ({type(e).__name__}).", "links": []}

# ── Build HTML ─────────────────────────────────────────────────────────────────
def build_html(date: datetime.date, sections: dict, archive_links: str) -> str:
    date_str = date.strftime("%B %d, %Y")
    date_iso = date.isoformat()

    sections_html = ""
    for topic in TOPICS:
        key = topic["key"]
        data = sections.get(key, {"summary": "No content.", "links": []})
        depth = topic["depth"]
        links_html = "".join(
            f'<a href="{l["url"]}" target="_blank" rel="noopener">'
            f'<span class="link-arrow">↗</span>{l["title"]}</a>'
            for l in data.get("links", [])
        )
        sections_html += f"""
        <section class="section depth-{depth}" id="{key}">
          <div class="section-header">
            <span class="section-icon">{topic["icon"]}</span>
            <h2>{topic["label"]}</h2>
            <span class="depth-badge">{depth}</span>
          </div>
          <div class="section-body"><p>{data["summary"]}</p></div>
          {'<div class="section-links">' + links_html + '</div>' if links_html else ''}
        </section>"""

    nav_links = "".join(f'<a href="#{t["key"]}">{t["label"]}</a>' for t in TOPICS)

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
      --bg:#0d0f0e;--surface:#131614;--border:#1e2320;--border-bright:#2a302c;
      --text:#c8d4c9;--text-dim:#5a6b5c;--text-bright:#e8f0e9;
      --accent:#4ade80;--accent-dim:#166534;
      --red:#f87171;--amber:#fbbf24;--blue:#60a5fa;
      --mono:'IBM Plex Mono',monospace;--serif:'Libre Baskerville',serif;
    }}
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:var(--bg);color:var(--text);font-family:var(--serif);font-size:16px;line-height:1.75;min-height:100vh}}
    header{{border-bottom:1px solid var(--border);padding:2rem 0 1.5rem;position:sticky;top:0;background:rgba(13,15,14,0.95);backdrop-filter:blur(8px);z-index:100}}
    .header-inner{{max-width:860px;margin:0 auto;padding:0 2rem;display:flex;align-items:baseline;gap:1.5rem}}
    .header-label{{font-family:var(--mono);font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--accent)}}
    .header-date{{font-family:var(--mono);font-size:0.8rem;color:var(--text-dim);margin-left:auto}}
    nav{{background:var(--surface);border-bottom:1px solid var(--border);overflow-x:auto;scrollbar-width:none}}
    nav::-webkit-scrollbar{{display:none}}
    .nav-inner{{max-width:860px;margin:0 auto;padding:0 2rem;display:flex}}
    nav a{{font-family:var(--mono);font-size:0.7rem;color:var(--text-dim);text-decoration:none;padding:0.75rem 1rem;white-space:nowrap;border-bottom:2px solid transparent;transition:color 0.15s,border-color 0.15s}}
    nav a:hover{{color:var(--text-bright);border-color:var(--accent)}}
    main{{max-width:860px;margin:0 auto;padding:3rem 2rem 6rem}}
    .section{{border:1px solid var(--border);border-radius:4px;margin-bottom:2rem;overflow:hidden;transition:border-color 0.2s}}
    .section:hover{{border-color:var(--border-bright)}}
    .section-header{{display:flex;align-items:center;gap:0.75rem;padding:1rem 1.5rem;background:var(--surface);border-bottom:1px solid var(--border)}}
    .section-icon{{font-size:1.1rem}}
    .section-header h2{{font-family:var(--mono);font-size:0.85rem;font-weight:500;letter-spacing:0.05em;color:var(--text-bright)}}
    .depth-badge{{margin-left:auto;font-family:var(--mono);font-size:0.6rem;letter-spacing:0.1em;text-transform:uppercase;padding:0.2rem 0.5rem;border-radius:2px}}
    .depth-deep .depth-badge{{background:rgba(248,113,113,0.1);color:var(--red);border:1px solid rgba(248,113,113,0.2)}}
    .depth-moderate .depth-badge{{background:rgba(251,191,36,0.1);color:var(--amber);border:1px solid rgba(251,191,36,0.2)}}
    .depth-broad .depth-badge{{background:rgba(96,165,250,0.1);color:var(--blue);border:1px solid rgba(96,165,250,0.2)}}
    .section-body{{padding:1.5rem;font-size:0.95rem;color:var(--text)}}
    .section-body p{{margin:0}}
    .section-body p+p{{margin-top:1rem}}
    .section-body strong{{color:var(--text-bright)}}
    .section-body em{{color:var(--text-dim);font-style:italic}}
    .section-body code{{font-family:var(--mono);font-size:0.8rem;background:var(--surface);padding:0.1rem 0.3rem;border-radius:2px;color:var(--accent)}}
    .section-links{{padding:1rem 1.5rem;border-top:1px solid var(--border);display:flex;flex-direction:column;gap:0.4rem}}
    .section-links a{{font-family:var(--mono);font-size:0.72rem;color:var(--text-dim);text-decoration:none;display:flex;align-items:center;gap:0.4rem;transition:color 0.15s;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
    .section-links a:hover{{color:var(--accent)}}
    .link-arrow{{color:var(--accent);flex-shrink:0}}
    .archive-bar{{font-family:var(--mono);font-size:0.7rem;color:var(--text-dim);margin-bottom:2.5rem;display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap}}
    .archive-bar span{{color:var(--border-bright)}}
    .archive-bar a{{color:var(--text-dim);text-decoration:none;padding:0.2rem 0.4rem;border:1px solid var(--border);border-radius:2px;transition:color 0.15s,border-color 0.15s}}
    .archive-bar a:hover{{color:var(--accent);border-color:var(--accent-dim)}}
    footer{{border-top:1px solid var(--border);padding:1.5rem 2rem;max-width:860px;margin:0 auto;font-family:var(--mono);font-size:0.65rem;color:var(--text-dim);display:flex;justify-content:space-between}}
    @media(max-width:600px){{.header-inner,.nav-inner,main,footer{{padding-left:1rem;padding-right:1rem}}}}
  </style>
</head>
<body>
  <header>
    <div class="header-inner">
      <span class="header-label">Daily Briefing</span>
      <span class="header-date">{date_str}</span>
    </div>
  </header>
  <nav><div class="nav-inner">{nav_links}</div></nav>
  <main>
    <div class="archive-bar">ARCHIVE <span>·</span> {archive_links}</div>
    {sections_html}
  </main>
  <footer>
    <span>generated {date_iso}</span>
    <span>gemini-2.5-flash · google search grounding</span>
  </footer>
</body>
</html>"""

# ── Archive links ──────────────────────────────────────────────────────────────
def get_archive_links(current_date: datetime.date) -> str:
    links = []
    for i in range(1, 16):
        d = current_date - datetime.timedelta(days=i)
        path = ARCHIVE_DIR / f"{d.isoformat()}.html"
        if path.exists():
            links.append(f'<a href="archive/{d.isoformat()}.html">{d.strftime("%b %d")}</a>')
    return " ".join(links) if links else "<span>no archive yet</span>"

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print(f"[INFO] Running digest for {TODAY}\n")

    sections = {}
    for topic in TOPICS:
        print(f"  → [{topic['key']}]")
        sections[topic["key"]] = fetch_and_summarize(topic)
        print()

    print("[INFO] Building HTML...")
    archive_links = get_archive_links(TODAY)
    html = build_html(TODAY, sections, archive_links)

    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
    (ARCHIVE_DIR / f"{TODAY.isoformat()}.html").write_text(html, encoding="utf-8")

    all_archive = sorted(ARCHIVE_DIR.glob("*.html"))
    for old in all_archive[:-15]:
        old.unlink()
        print(f"[INFO] Removed old archive: {old.name}")

    print(f"\n[DONE] → docs/index.html")

if __name__ == "__main__":
    main()
