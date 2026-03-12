---
name: facebook-group-monitor
description: >-
  Monitor Facebook groups for new posts using Playwright browser automation
  with stealth mode and persistent login session. Scrapes group feed, tracks
  seen posts, reports only new ones. Captures a single stitched "feed strip"
  screenshot (viewport scroll + Pillow stitch) for efficient LLM vision
  analysis — one image covers the full feed. Use when: monitoring Facebook
  groups, scraping FB posts, checking new group activity, Facebook automation,
  marketplace monitoring, book sale tracking, competitor group monitoring.
  Triggers: 'check Facebook group', 'scrape FB posts', 'new posts in group',
  'monitor group', 'Facebook marketplace', 'group update'.
metadata:
  openclaw:
    category: "social"
    shared: true
---

# Facebook Group Monitor Skill

## Overview

Playwright-based headless browser scraper for Facebook groups. Default behavior:
**captures a stitched "feed strip"** (scrolls 3× viewport, crops to feed column,
stitches into 1 JPEG) → agent calls vision model once with a custom prompt to
extract and interpret all new posts in a single LLM call.

Requires one-time manual login via terminal to establish a persistent browser session.

## Setup

See [references/SETUP.md](references/SETUP.md) for installation and first-time login instructions.

## File Locations (after install)

- **Script**: `scripts/fb-group-monitor.py`
- **Shell wrapper**: `scripts/fb-group-monitor.sh`
- **Browser session**: auto-created at `scripts/.browser-data/` (persistent login)
- **Seen posts**: auto-created at `scripts/.seen-posts.json` (dedup tracking)
- **Screenshots**: `scripts/screenshots/` or custom `--shots-dir`

## Commands

### 1. Check login session
```bash
scripts/fb-group-monitor.sh status
```
Output:
```json
{"success": true, "action": "status", "message": "Session active — logged in to Facebook."}
```

### 2. Scrape new posts (with feed strip screenshot)
```bash
scripts/fb-group-monitor.sh scrape <GROUP_URL> [--limit N] [--shots-dir <PATH>]
```

**Parameters:**
- `GROUP_URL`: Full URL (https://www.facebook.com/groups/123456) or just group ID
- `--limit N`: Max posts to scrape (default: 10)
- `--shots-dir <PATH>`: ⚠️ **REQUIRED for vision** — save screenshots in agent workspace so image tool can read them
- `--no-shots`: Skip screenshots (faster, text-only mode)

**Example:**
```bash
scripts/fb-group-monitor.sh scrape "https://www.facebook.com/groups/123456789" --limit 10 --shots-dir ./temp-screenshots
```

**Output JSON (with feed strip screenshot):**
```json
{
  "success": true,
  "action": "scrape",
  "group_name": "Example Group Name",
  "group_url": "https://www.facebook.com/groups/123456789",
  "total_scraped": 6,
  "new_count": 3,
  "feed_screenshot": "/path/to/temp-screenshots/feed_abc12345_1741800000.jpg",
  "posts": [
    {
      "author": "Poster Name",
      "text": "Post content (may be truncated by Facebook's 'See more')...",
      "url": "https://facebook.com/groups/123456/posts/789",
      "images": 3
    },
    {
      "author": "Another Poster",
      "text": "Text-only post, no images...",
      "url": "https://facebook.com/groups/123456/posts/790",
      "images": 0
    }
  ],
  "message": "Found 3 new posts / 6 total."
}
```

> **Note**: `feed_screenshot` is a single stitched JPEG covering the full feed (3 viewport scrolls).
> Individual posts no longer have a `screenshot_path` — use `feed_screenshot` (top-level) instead.

### 3. Clean old screenshots
```bash
scripts/fb-group-monitor.sh clean-shots
```
Auto-removes screenshots older than 48h and caps at 100 max. Script also auto-cleans before each scrape.

### 4. Login (one-time, from terminal)
```bash
scripts/fb-group-monitor.sh login
```
Opens browser, login manually, press Enter to save session. Session lasts weeks/months.

## Agent Workflow

When triggered by cron or user request to check a group:

### Step 1: Scrape
```bash
scripts/fb-group-monitor.sh scrape "<GROUP_URL>" --limit 10 --shots-dir ./temp-screenshots
```
> ⚠️ **Use `--shots-dir`** pointing to a path within the workspace so the image tool can access screenshots.

### Step 2: Analyze feed screenshot + combine with text

**If `feed_screenshot` is present** (1 stitched image covering the full feed):
- Compose a dynamic prompt using the author list from the JSON, so vision focuses on the correct new posts (the feed strip also contains already-seen posts)
- Call image tool with **both** `image` and `prompt` parameters:
  ```
  image tool:
    image: <feed_screenshot path>
    prompt: "Facebook group feed. Find and analyze posts by these people (new posts to process):
    - [Author 1]: "[first few words of text from JSON]" — N images
    - [Author 2]: "[first few words of text from JSON]"
    ...
    For EACH post, do 2 things:
    1. EXTRACT: book/product name, author/publisher (read from cover), price (including handwritten prices), condition (new/used/marked/yellowed).
    2. INTERPRET: is the deal worth it (price vs market if known), is the item rare/valuable, actual condition assessment from photos."
  ```
- ⚠️ **NEVER call image tool with empty `{}`** — default prompt just describes the image generically
- ⚠️ **Feed strip includes old posts** — always include author + text snippet so vision targets the right posts
- After getting vision result: match by author, add `url` from JSON
- Prioritize image content over truncated `text` field ("see more" posts)

**If `feed_screenshot` is absent** (screenshot failed):
- Read directly from `text` field of each post
- Summarize available information, note "no screenshot available"

### Step 3: Report to user

**MUST** include the original post link in each item for verification.

```
Format per new post:

📌 *[Title/Summary]*
👤 Author: [author]
💰 Price: [price or "unknown"]
📝 Condition: [description]
💡 Note: [deal assessment or insight, if any]
🔗 [post URL]
```

### Step 4: If no new posts → stay silent (no notification)
### Step 5: If `success == false` → report error briefly

### ⚠️ Anti-duplicate rule
- **Send Telegram only ONCE** per run, regardless of whether vision succeeded or failed
- If `message` tool returns an error → report once and stop, do NOT retry
- If vision fails → fallback to text, send once with note "⚠️ Vision unavailable, text only"

## Important Notes

- **Rate limiting**: Recommended cron interval ≥ 2 hours — safe for Facebook
- **Session expired**: If error "Not logged in" → run `login` from terminal
- **UI changes**: Facebook updates DOM frequently → selectors may need updates
- **"See more"**: Text is truncated — feed strip screenshot usually has complete content
- **Feed strip**: Scrolls 3× viewport height, crops to feed column, stitches 1 JPEG — reduces vision calls from N to 1
- **Screenshot quality**: JPEG 82% — sufficient for LLM vision to read text and identify product images
- **Vision model**: Use a vision-capable model (e.g. Gemini Flash) for the image tool call
