[🇻🇳 Tiếng Việt](../vi/recipes/book-tracker.md)

# Recipe: Goodreads Book Tracker

Rate, review, and track reading via Telegram commands.

## How It Works

```
User: "Finished reading Project Hail Mary, 5 stars"
Agent: searches Goodreads → finds book → marks as Read → rates 5 stars
Agent: "✅ Done! Rated 5⭐ for Project Hail Mary by Andy Weir"
```

## Setup

1. Install Playwright + stealth in shared venv
2. Run login once (opens browser):
   ```bash
   source ~/.openclaw/common-scripts/.venv/bin/activate
   python3 ~/.openclaw/common-scripts/goodreads/goodreads-writer.py login
   ```
3. Copy skill to agent workspace:
   ```bash
   cp -r /path/to/goodreads-write ~/.openclaw/workspace-personal/skills/
   cp -r /path/to/goodreads-read ~/.openclaw/workspace-personal/skills/
   ```

## Available Commands

| Action | Script Command |
|---|---|
| Search book | `python3 goodreads-rss.py search "book title"` |
| View shelf | `python3 goodreads-rss.py shelf USER_ID --shelf currently-reading` |
| Start reading | `goodreads-write.sh start BOOK_ID` |
| Finish reading | `goodreads-write.sh finish BOOK_ID` |
| Rate | `goodreads-write.sh edit BOOK_ID --stars 5` |
| Review | `goodreads-write.sh edit BOOK_ID --review "Great book!"` |
| Edit dates | `goodreads-write.sh edit BOOK_ID --start-date 2026-01-01 --end-date 2026-02-15` |

## Typical Workflow

```
1. Search: python3 goodreads-rss.py search "Project Hail Mary"
   → Returns book_id: 54493401

2. Finish: goodreads-write.sh finish 54493401
   → Shelf changed to "Read" (RSS verified)

3. Rate + Review: goodreads-write.sh edit 54493401 --stars 5 --review "Amazing sci-fi"
   → Rating and review saved
```

## Known Gotchas

- **Edit page redirect**: Goodreads sends `/review/edit/` → `/review/new/` for first reviews. Script handles both.
- **Session expiry**: Cookies last weeks/months. If actions fail, re-run `login`.
- **RSS verification delay**: Shelf changes take 5-10 minutes to appear in RSS.
- **DOM changes**: Goodreads updates UI periodically. Check selectors if actions fail.
