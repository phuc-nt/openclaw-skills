# Goodreads Skill — Setup Guide

## Prerequisites

- **Python 3.10+**
- **Chromium browser** (installed via Playwright)

## Installation

### 1. Create virtual environment (recommended)

```bash
# In the skill's scripts directory
cd scripts/
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Python dependencies

```bash
pip install playwright playwright-stealth
playwright install chromium
```

### 3. Read commands — no further setup needed

The read commands (shelf, search, book, reviews, activity) use RSS feeds and HTTP scraping.
No login required.

```bash
# Test read access
python3 scripts/goodreads-rss.py search "atomic habits" --limit 3
```

### 4. Write commands — one-time login

Write commands require a one-time browser login:

```bash
./scripts/goodreads-write.sh login
```

This opens a Chromium browser window. Sign in with your Amazon/email credentials.
After seeing the Goodreads homepage, return to terminal and press Enter.

> **Session duration:** Cookies persist for weeks to months via stealth mode.
> You only need to re-login when the session expires.

### 5. RSS verification (optional)

For shelf commands to auto-verify via RSS, set your Goodreads user ID:

```bash
export GOODREADS_USER_ID="<YOUR_USER_ID>"
```

Find your user ID at: `goodreads.com/user/show/<ID>-yourname`

## Virtual Environment Options

The shell wrapper (`goodreads-write.sh`) supports multiple venv locations:

1. **`GR_VENV` environment variable** — highest priority
2. **`scripts/.venv/`** — co-located venv (recommended)
3. **System Python** — fallback (must have playwright installed globally)

```bash
# Option 1: Use a custom venv
export GR_VENV="/path/to/your/venv"

# Option 2: Co-located (default)
cd scripts/ && python3 -m venv .venv
```

## Troubleshooting

### "Session expired" error
```bash
./scripts/goodreads-write.sh login
```

### 403 Forbidden / Access Denied
- Goodreads anti-bot detected the automation
- Wait a few minutes, then try again
- Ensure `playwright-stealth` is installed

### "Chromium not found"
```bash
source scripts/.venv/bin/activate
playwright install chromium
```

### Selectors not found
- Goodreads may have updated their UI
- Check the book page manually to verify element structure
- Open an issue on GitHub with the error details

## File Structure

```
goodreads/
├── SKILL.md                          ← Agent instructions
├── scripts/
│   ├── goodreads-rss.py             ← Read: shelf, search, book, reviews, activity
│   ├── goodreads-writer.py          ← Write: rate, shelf, review, edit, progress
│   └── goodreads-write.sh           ← Shell wrapper with venv support
├── references/
│   └── SETUP.md                     ← This file
└── .browser-data/                   ← Auto-created on first login (gitignored)
```
