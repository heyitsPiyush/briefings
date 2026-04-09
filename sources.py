# ── RSS Feed Sources ──────────────────────────────────────────────────────────
# Add or remove feeds freely. Each category maps to a list of RSS URLs.

SOURCES = {

    # ── Bug Bounty (Deep) ──────────────────────────────────────────────────────
    "bug_bounty": [
        "https://feeds.feedburner.com/PentestTools",          # Pentest Tools blog
        "https://portswigger.net/daily-swig/rss",             # Daily Swig - PortSwigger
        "https://www.hackerone.com/blog.rss",                 # HackerOne blog
        "https://infosecwriteups.com/feed",                   # InfoSec writeups (Medium)
        "https://feeds.feedburner.com/BugCrowd",              # Bugcrowd blog
    ],

    # ── Hardware Hacking (Deep) ────────────────────────────────────────────────
    "hardware_hacking": [
        "https://hackaday.com/blog/feed/",                    # Hackaday
        "https://wrongbaud.github.io/feed.xml",               # Hardware hacking blog
        "https://riverloopsecurity.com/blog/feed.xml",        # River Loop Security
        "https://limitedresults.com/feed/",                   # LimitedResults hardware
        "https://www.embedded.com/rss/",                      # Embedded.com
    ],

    # ── Exploit Development (Deep) ─────────────────────────────────────────────
    "exploit_dev": [
        "https://googleprojectzero.blogspot.com/feeds/posts/default",  # Project Zero
        "https://blog.ret2.io/feed.xml",                      # ret2 systems
        "https://www.zerodayinitiative.com/blog/rss",         # ZDI blog
        "https://research.checkpoint.com/feed/",              # Check Point Research
        "https://github.blog/feed/",                          # GitHub Security Lab
    ],

    # ── CVE & Threat Analysis (Moderate) ──────────────────────────────────────
    "cve_threats": [
        "https://feeds.feedburner.com/TheHackersNews",        # The Hacker News
        "https://www.bleepingcomputer.com/feed/",             # BleepingComputer
        "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss-analyzed.xml",  # NIST NVD
        "https://www.cisa.gov/cybersecurity-advisories/all.xml",  # CISA advisories
        "https://isc.sans.edu/rssfeed_full.xml",              # SANS ISC
    ],

    # ── AI × Cybersecurity (Deep) ─────────────────────────────────────────────
    "ai_cyber": [
        "https://embracethered.com/blog/rss.xml",             # AI/LLM security research
        "https://www.anthropic.com/rss.xml",                  # Anthropic research
        "https://openai.com/blog/rss.xml",                    # OpenAI blog
        "https://blog.trailofbits.com/feed/",                 # Trail of Bits
        "https://security.googleblog.com/feeds/posts/default",# Google Security blog
    ],

    # ── AI & Tech (Moderate) ──────────────────────────────────────────────────
    "ai_tech": [
        "https://techcrunch.com/feed/",                       # TechCrunch
        "https://www.technologyreview.com/feed/",             # MIT Tech Review
        "https://venturebeat.com/feed/",                      # VentureBeat AI
        "https://arstechnica.com/feed/",                      # Ars Technica
        "https://www.wired.com/feed/rss",                     # Wired
    ],

    # ── Business & Finance (Broad) ────────────────────────────────────────────
    "finance": [
        "https://feeds.bloomberg.com/markets/news.rss",       # Bloomberg Markets
        "https://www.ft.com/?format=rss",                     # Financial Times
        "https://feeds.reuters.com/reuters/businessNews",     # Reuters Business
        "https://www.cnbc.com/id/10001147/device/rss/rss.html",  # CNBC Finance
        "https://fortune.com/feed/",                          # Fortune
    ],

    # ── Geopolitics & Policy (Broad) ──────────────────────────────────────────
    "geopolitics": [
        "https://www.aljazeera.com/xml/rss/all.xml",          # Al Jazeera (global)
        "https://www.theguardian.com/world/rss",              # The Guardian World
        "https://feeds.bbci.co.uk/news/world/rss.xml",        # BBC World
        "https://www.onlinekhabar.com/feed",                  # OnlineKhabar (Nepal)
        "https://kathmandupost.com/rss",                      # Kathmandu Post (Nepal)
        "https://www.cbc.ca/cmlink/rss-world",                # CBC News (Canada)
        "https://globalnews.ca/feed/",                        # Global News (Canada)
    ],

    # ── Science & Research (Broad) ────────────────────────────────────────────
    "science": [
        "https://www.sciencedaily.com/rss/all.xml",           # ScienceDaily
        "https://feeds.nature.com/nature/rss/current",        # Nature
        "https://www.newscientist.com/feed/home/",            # New Scientist
        "https://phys.org/rss-feed/",                         # Phys.org
        "https://arxiv.org/rss/cs.CR",                        # arXiv - CS Security
    ],
}
