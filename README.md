# Daily Briefing

A self-hosted daily digest — automatically generated every morning via GitHub Actions,
summarized by Gemini AI, and published to GitHub Pages.

## Topics Covered

| Category | Depth |
|---|---|
| 🐛 Bug Bounty | Deep |
| ⚙️ Hardware Hacking | Deep |
| 💥 Exploit Development | Deep |
| 🔍 CVE & Threat Analysis | Moderate |
| 🤖 AI × Cybersecurity | Deep |
| 💡 AI & Tech | Moderate |
| 💰 Business & Finance | Broad |
| 🌍 Geopolitics & Policy | Broad |
| 🔬 Science & Research | Broad |

## Setup Guide

### 1. Fork or clone this repo

Make sure the repo is **public** (required for free GitHub Actions + Pages).

### 2. Get a Gemini API key

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **Get API Key** → **Create API key**
3. Copy the key

### 3. Add the secret to GitHub

1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `GEMINI_API_KEY`
4. Value: paste your key

### 4. Enable GitHub Pages

1. Go to your repo → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / folder: `/docs`
4. Save

### 5. Run it manually (first time)

1. Go to **Actions** tab in your repo
2. Click **Daily Digest**
3. Click **Run workflow**
4. Wait ~2 minutes
5. Visit `https://yourusername.github.io/your-repo-name`

After that, it runs automatically every day at **7:00 AM EST**.

## Customizing Sources

Edit `sources.py` to add/remove RSS feeds per category.
Each feed list accepts any valid RSS/Atom URL.

## Cost

| Service | Usage | Cost |
|---|---|---|
| Gemini API (Flash-Lite) | 1 request/day | ✅ Free |
| GitHub Actions | ~3 min/day | ✅ Free (public repo) |
| GitHub Pages | static HTML | ✅ Free |
| RSS feeds | unlimited | ✅ Free |
| **Total** | | **$0/month** |

## File Structure

```
.
├── .github/
│   └── workflows/
│       └── digest.yml      # Scheduled GitHub Actions workflow
├── docs/
│   ├── index.html          # Today's digest (GitHub Pages root)
│   └── archive/
│       └── YYYY-MM-DD.html # Last 15 days of digests
├── digest.py               # Main script
├── sources.py              # RSS feed sources
├── requirements.txt
└── README.md
```
