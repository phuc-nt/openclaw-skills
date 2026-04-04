[🇻🇳 Tiếng Việt](vi/11-agent-profiles.md)

[← Home](index.md) · [Installation](01-installation.md) · [Architecture](02-architecture.md) · [First Agent](03-first-agent.md) · [Google](04-google-workspace.md) · [Browser](05-browser-automation.md) · [Cron](06-cron-jobs.md) · [Multi-Agent](07-multi-agent.md) · [Profiles](11-agent-profiles.md) · [Models](08-model-selection.md) · [Memory](09-memory-system.md) · [Ops](10-operations.md)


# 3 Agent Profiles — Tools & Workflows in Detail

After optimizing from 7 agents down to 3, the system is organized by **domain of concern**:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Telegram                                 │
│     ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│     │ Personal │    │ Research │    │  Kioku   │               │
│     │   Bot    │    │   Bot    │    │   Bot    │               │
│     └────┬─────┘    └────┬─────┘    └────┬─────┘               │
│          ▼               ▼               ▼                      │
│   ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│   │  PERSONAL  │  │  RESEARCH  │  │   KIOKU    │              │
│   │  My life   │  │  The world │  │ Inner self │              │
│   └──────┬─────┘  └──────┬─────┘  └──────┬─────┘              │
│   ┌──────┴──────┐  ┌─────┴───────┐  ┌────┴──────┐             │
│   │ gws-* (15)  │  │ crawl4ai    │  │kioku-lite │             │
│   │ goodreads   │  │ reddit      │  │  CLI      │             │
│   │ typefully   │  │ youtube     │  │           │             │
│   └─────────────┘  └─────────────┘  └───────────┘             │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │     Gateway — MiniMax M2.7 → Gemini Flash → Haiku 4.5  │  │
│   └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Personal Agent — "My Life"

| Property | Value |
|---|---|
| **ID** | `personal` |
| **Telegram** | Personal Bot |
| **Model** | MiniMax M2.7 → Gemini Flash → Haiku 4.5 |
| **Skills** | 19 |
| **Cron** | 6 jobs |

### Tools (19 Skills)

Google Workspace (15): gmail, gmail-send, gmail-triage, calendar, calendar-agenda, calendar-insert, drive, drive-upload, sheets, sheets-append, sheets-read, docs, docs-write, tasks, shared.

Plus: goodreads-read, goodreads-write, typefully, academic-research.

### Key Workflows

**Email Triage** (cron 9h & 15h): `gws gmail +triage --max 20` → classify Urgent/Action/FYI/Noise → Telegram.

**Morning Briefing** (cron 7h): calendar agenda + gmail triage + tasks → single Telegram summary.

**Expense Tracker** (ad-hoc): "tiêu 85k cà phê" → parse amount/category → `gws sheets +append` → confirm.

**Goodreads** (ad-hoc): "đọc xong X, 5 sao" → search → finish → rate → RSS verify → confirm.

**Calendar Conflict** (cron 7:15): check 7 days → detect double-booking → alert or stay silent.

---

## 2. Research Agent — "The World"

| Property | Value |
|---|---|
| **ID** | `research` |
| **Telegram** | Research Bot |
| **Model** | MiniMax M2.7 → Gemini Flash → Haiku 4.5 |
| **Skills** | 9 + crawl4ai + common-scripts |
| **Cron** | 1 job (reddit digest) |

### Tools (4 Tiers)

- **Tier 1**: `web_search` (built-in)
- **Tier 2**: `crawl-web.py` — Crawl4AI wrapper, HTML → clean Markdown (**default for reading web**)
- **Tier 3**: reddit-readonly, youtube transcripts, facebook-group, MLX Whisper, academic-research
- **Tier 4**: gws-drive-upload, gws-docs-write, kioku-lite

### Key Workflows

**Deep Research** (ad-hoc): web_search → crawl-web.py → reddit-readonly → synthesize report → upload Drive.

**Reddit Digest** (cron 10h): `digest-workflow.sh` → 20 posts from 4 subreddits → translate Vietnamese → upload Drive → Telegram summary.

**Ad-hoc YouTube** (ad-hoc): paste link → `get-transcript.sh` (fallback: MLX Whisper local) → summarize → Telegram + Drive.

**Read Later** (ad-hoc): "đọc sau URL" → crawl-web.py → summarize 3-5 bullets → kioku-lite save.

**Critical Writing** (ad-hoc): research first → write 1500-word article with citations → ask approval → upload Drive.

---

## 3. Kioku Agent — "Inner Self"

| Property | Value |
|---|---|
| **ID** | `kioku` |
| **Telegram** | Kioku Bot |
| **Model** | MiniMax M2.7 → Gemini Flash → Haiku 4.5 |
| **Skills** | 0 (kioku-lite CLI directly) |
| **Cron** | 1 job (health check-in) |

### Tools

`kioku-lite` CLI: save, kg-index, search (tri-hybrid: BM25 + Vector + KG), recall, timeline, entities, kg-alias.

### Personality

Not a task bot — an **emotional companion**: validates feelings first, never advises unless asked, uses warm tone, saves everything verbatim.

### Key Workflows

**Health Check-in** (cron 7:30): send 3 questions (sleep/mood/exercise) → save answers → detect patterns (low sleep → warning).

**Emotional Chat** (ad-hoc): listen → validate → save to kioku-lite with mood + tags → kg-index entities.

**Memory Save** (ad-hoc): "remember this..." → save verbatim → index entities + relationships.

**Memory Recall** (ad-hoc): "what did I say about X?" → tri-hybrid search → summarize findings.

---

## Comparison

| Aspect | Personal | Research | Kioku |
|---|---|---|---|
| **Domain** | My daily life | Internet & knowledge | Emotions & memories |
| **Tone** | Quick, practical | Academic, sourced | Warm, empathetic |
| **Skills** | 19 | 9 + crawl4ai | 0 (CLI) |
| **Cron** | 6 | 1 | 1 |
| **Key tool** | gws CLI | crawl-web.py | kioku-lite |
| **When to use** | Email, calendar, expenses | Research, digests, read later | Feelings, health, memories |

## Next: [Model Selection →](08-model-selection.md)
