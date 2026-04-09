# Daily Briefing

A self-hosted daily digest — automatically generated every morning via GitHub Actions,
summarized by Gemini AI, and published to GitHub Pages.

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
