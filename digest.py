import os
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

# ── Topic Definitions ─────────────────────────────────────────────────────────
TOPICS = [
    {
        "key": "bug_bounty",
        "icon": "🐛",
        "label": "Bug Bounty",
        "depth": "deep",
        "prompt": """You are a senior bug bounty researcher writing a daily briefing for {date}.
Search for today's most significant bug bounty news. Focus on:
- New vulnerability disclosures and writeups from researchers
- HackerOne, Bugcrowd, Intigriti program updates or payouts
- Interesting CVEs that originated from bounty programs
- Researcher techniques, methodologies, and tooling
- Notable bug bounty wins or record payouts
Write 3 detailed paragraphs. Be technically specific — name vulnerabilities,
affected systems, CVSS scores, and researcher names where available."""
    },
    {
        "key": "hardware_hacking",
        "icon": "⚙️",
        "label": "Hardware Hacking",
        "depth": "deep",
        "prompt": """You are a hardware security researcher writing a daily briefing for {date}.
Search for today's most significant hardware hacking news. Focus on:
- Firmware vulnerabilities and reverse engineering findings
- Embedded systems and IoT security research
- Side-channel attacks, fault injection, RF hacking
- Physical security bypasses and supply chain attacks
- New hardware hacking tools, techniques, and publications
Write 3 detailed paragraphs. Name chips, architectures, attack vectors,
affected devices, and researchers where available."""
    },
    {
        "key": "exploit_dev",
        "icon": "💥",
        "label": "Exploit Development",
        "depth": "deep",
        "prompt": """You are an exploit development researcher writing a daily briefing for {date}.
Search for today's most significant exploit development news. Focus on:
- New exploit techniques, bypasses, and primitives
- Public PoC releases and proof of concept code
- Kernel exploits, browser exploits, memory corruption research
- Mitigation bypasses (ASLR, CFI, stack canaries, etc.)
- CTF writeups with deep exploit development content
- Project Zero, ZDI, and security lab publications
Write 3 detailed paragraphs. Name CVEs, affected versions, exploit
primitives used, and researchers where available."""
    },
    {
        "key": "cve_threats",
        "icon": "🔍",
        "label": "CVE & Threat Analysis",
        "depth": "moderate",
        "prompt": """You are a threat intelligence analyst writing a daily briefing for {date}.
Search for today's most significant CVEs and threat activity. Focus on:
- Critical and high severity CVEs published or exploited today
- CISA KEV (Known Exploited Vulnerabilities) additions
- Active threat actor campaigns and TTPs
- Malware campaigns and ransomware activity
Write 2-3 paragraphs. Name specific CVE IDs, CVSS scores, affected products,
and threat actor groups where available."""
    },
    {
        "key": "ai_cyber",
        "icon": "🤖",
        "label": "AI × Cybersecurity",
        "depth": "deep",
        "prompt": """You are an AI security researcher writing a daily briefing for {date}.
Search for today's most significant AI and cybersecurity intersection news. Focus on:
- LLM vulnerabilities — prompt injection, jailbreaks, model inversion
- AI-powered attacks and offensive security tools
- Defensive AI — detection models, AI-driven SOC tools
- Research on securing AI pipelines, RAG, vector databases
- AI red teaming techniques and findings
Write 3 detailed paragraphs. Name models, attack techniques, researchers,
and organizations where available."""
    },
    {
        "key": "ai_tech",
        "icon": "💡",
        "label": "AI & Tech",
        "depth": "moderate",
        "prompt": """You are a technology analyst writing a daily briefing for {date}.
Search for today's most notable AI and technology developments. Focus on:
- Major AI model releases, updates, or announcements
- Significant research papers and breakthroughs
- Industry moves — funding, acquisitions, partnerships
- Developer tools, frameworks, and platform updates
Write 2-3 paragraphs. Be specific with model names, company names, and numbers."""
    },
    {
        "key": "finance",
        "icon": "💰",
        "label": "Business & Finance",
        "depth": "broad",
        "prompt": """You are a financial analyst writing a daily market briefing for {date}.
Search for today's most important business and finance news. Focus on:
- Global market movements and key indices
- Major corporate earnings, mergers, acquisitions
- Central bank decisions and macroeconomic indicators
- Commodity prices (oil, gold) and currency moves
Write 2 concise paragraphs. Include specific numbers, percentages, and company names."""
    },
    {
        "key": "geopolitics",
        "icon": "🌍",
        "label": "Geopolitics & Policy",
        "depth": "broad",
        "prompt": """You are a geopolitical analyst writing a daily briefing for {date}.
Search for today's most important geopolitical and policy news. Cover:
- Nepal: political developments, economy, government decisions, significant local events
- Canada: federal/provincial politics, major policy decisions, US-Canada relations
- Global: significant international conflicts, diplomacy, elections, UN developments
Write 2-3 paragraphs covering Nepal, Canada, and global highlights.
Be specific with names, locations, and context."""
    },
    {
        "key": "science",
        "icon": "🔬",
        "label": "Science & Research",
        "depth": "broad",
        "prompt": """You are a science journalist writing a daily briefing for {date}.
Search for today's most notable science and research developments. Focus on:
- Breakthrough research papers and findings
- Space exploration and astronomy news
- Medical and health research advances
- Climate and environmental science
Write 2 concise paragraphs. Name specific researchers, institutions, and journals."""
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
                max_output_tokens=2000,
            )
        )

        summary = response.text.strip() if response.text else "No content returned."
        print(f"     summary length: {len(summary)} chars")

        # Extract grounding source links from metadata
        links = []
        try:
            chunks = response.candidates[0].grounding_metadata.grounding_chunks
            for chunk in chunks:
                if hasattr(chunk, "web") and chunk.web.uri:
                    links.append({
                        "title": chunk.web.title or chunk.web.uri,
                        "url": chunk.web.uri
                    })
            print(f"     grounding links found: {len(links)}")
        except Exception as e:
            print(f"     grounding metadata unavailable: {e}")

        return {"summary": summary, "links": links[:6]}

    except Exception as e:
        print(f"  [ERROR] {topic['key']}: {type(e).__name__}: {e}")
        return {"summary": f"Error: {type(e).__name__}: {str(e)[:300]}", "links": []}

# ── Build HTML ─────────────────────────────────────────────────────────────────
def build_html(date: datetime.date, sections: dict, archive_links: str) -> str:
    date_str = date.strftime("%B %d, %Y")
    date_iso = date.isoformat()

    sections_html = ""
    for topic in TOPICS:
        key = topic["key"]
        data = sections.get(key, {"summary": "No content.", "links": []})
        depth = topic["depth"]
        summary_html = data["summary"].replace("\n\n", "</p><p>").replace("\n", "<br>")
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
          <div class="section-body"><p>{summary_html}</p></div>
          <div class="section-links">{links_html}</div>
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
    .section-body p+p{{margin-top:1rem}}
    .section-links{{padding:1rem 1.5rem;border-top:1px solid var(--border);display:flex;flex-direction:column;gap:0.4rem}}
    .section-links a{{font-family:var(--mono);font-size:0.72rem;color:var(--text-dim);text-decoration:none;display:flex;align-items:center;gap:0.4rem;transition:color 0.15s}}
    .section-links a:hover{{color:var(--accent)}}
    .link-arrow{{color:var(--accent)}}
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
    print(f"[INFO] Running digest for {TODAY}")
    print(f"[INFO] SDK: google-genai (new unified SDK)")
    print(f"[INFO] Processing {len(TOPICS)} topics...\n")

    sections = {}
    for topic in TOPICS:
        print(f"  → [{topic['key']}] calling Gemini with search grounding...")
        sections[topic["key"]] = fetch_and_summarize(topic)
        print(f"     ✓ done\n")

    print("[INFO] Building HTML...")
    archive_links = get_archive_links(TODAY)
    html = build_html(TODAY, sections, archive_links)

    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
    (ARCHIVE_DIR / f"{TODAY.isoformat()}.html").write_text(html, encoding="utf-8")

    all_archive = sorted(ARCHIVE_DIR.glob("*.html"))
    for old in all_archive[:-15]:
        old.unlink()
        print(f"[INFO] Removed old archive: {old.name}")

    print(f"\n[DONE] → docs/index.html + docs/archive/{TODAY.isoformat()}.html")

if __name__ == "__main__":
    main()
