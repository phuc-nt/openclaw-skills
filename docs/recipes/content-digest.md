[🇻🇳 Tiếng Việt](../vi/recipes/content-digest.md)

[← Home](../index.md) · [Installation](../01-installation.md) · [Architecture](../02-architecture.md) · [First Agent](../03-first-agent.md) · [Google](../04-google-workspace.md) · [Browser](../05-browser-automation.md) · [Cron](../06-cron-jobs.md) · [Multi-Agent](../07-multi-agent.md) · [Profiles](../11-agent-profiles.md) · [Models](../08-model-selection.md) · [Memory](../09-memory-system.md) · [Ops](../10-operations.md)


# Recipe: Content Digest (Reddit + YouTube)

Automated daily digest of Reddit posts and YouTube videos, translated and summarized.

## Architecture

```
Cron trigger → Agent runs script → Script fetches content →
Agent translates/summarizes → Upload to Google Drive → Send Telegram summary
```

## Reddit Digest

### Script Structure

```
~/.openclaw/common-scripts/reddit/
├── digest-workflow.sh           # Orchestrator
├── generate-detailed-digest.js  # Fetch + format to markdown
└── (node_modules via shared .venv)
```

### Cron Job

```json
{
  "id": "reddit-digest",
  "agentId": "personal",
  "schedule": { "kind": "cron", "expr": "0 10 * * *", "tz": "Your/Timezone" },
  "payload": {
    "kind": "agentTurn",
    "message": "Run Reddit digest:\n1. Execute: bash ~/.openclaw/common-scripts/reddit/digest-workflow.sh ~/.openclaw/workspace-personal reddit\n2. Read the generated markdown\n3. Translate headlines and summarize each post\n4. Re-upload to Google Drive\n5. Send Telegram with Doc link + top trends",
    "timeoutSeconds": 900
  },
  "delivery": { "mode": "announce", "channel": "telegram", "to": "YOUR_ID", "bestEffort": true }
}
```

### Rate Limiting
- Reddit API: Use `reddit-readonly` skill (no auth needed for public content)
- Don't scrape more than 5 posts × 10 comments per subreddit per run

## YouTube Digest

### Transcript Pipeline

```
yt-dlp (list videos) → youtube-transcript-api (subtitles) → MLX Whisper (fallback)
```

- Free transcripts via `youtube-transcript-api` (no API key)
- Fallback: MLX Whisper runs locally on Apple Silicon (~30-90s per video)
- Rate limit: 5s sleep between transcript requests, max 24/session

### Tips
- Monitor channel via RSS — cheaper than API
- Cache seen video IDs in `memory/seen-videos.txt` to avoid re-processing
- Long videos (>30min): Use transcript, don't try to summarize from title alone
