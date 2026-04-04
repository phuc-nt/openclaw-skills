# 🦞 OpenClaw Skills

Community skills for [OpenClaw](https://openclaw.ai) agents.
Published on [ClawHub](https://clawhub.ai) and mirrored here for backup & offline access.

**📖 [Build Guide](https://phuc-nt.github.io/openclaw-skills/)** | **🇻🇳 [Hướng dẫn tiếng Việt](https://phuc-nt.github.io/openclaw-skills/vi/)**

---

## What's Inside

### Skills (Installable)

| Skill | Description | Version |
|-------|-------------|---------|
| [facebook-group-monitor](./facebook-group-monitor/) | Monitor Facebook groups with Playwright. Scrapes posts, captures feed strip screenshot for LLM vision analysis. | 1.3.0 |
| [goodreads](./goodreads/) | Full Goodreads integration: read shelves/search via RSS + write (rate, shelf, review, dates) via Playwright. | 1.1.0 |

### Build Guide (Documentation)

A step-by-step guide to building a personal multi-agent system on macOS — from real production experience running 3 AI agents 24/7 on a Mac Mini.

**Architecture: 3 Agents Split by Domain**

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   PERSONAL   │  │   RESEARCH   │  │    KIOKU     │
│   "My life"  │  │ "The world"  │  │ "Inner self" │
├──────────────┤  ├──────────────┤  ├──────────────┤
│ Email/Gmail  │  │ Crawl4AI     │  │ kioku-lite   │
│ Calendar     │  │ Reddit digest│  │ Emotions     │
│ Tasks        │  │ YouTube      │  │ Health       │
│ Expenses     │  │ Facebook     │  │ Memories     │
│ Goodreads    │  │ Web research │  │ Knowledge    │
│ Typefully    │  │ Critical     │  │ Graph        │
│              │  │ writing      │  │              │
├──────────────┤  ├──────────────┤  ├──────────────┤
│ 19 skills    │  │ 9 skills +   │  │ 0 skills     │
│ 6 cron jobs  │  │ crawl4ai     │  │ (CLI only)   │
│              │  │ 1 cron job   │  │ 1 cron job   │
└──────────────┘  └──────────────┘  └──────────────┘
         All running MiniMax M2.7 (~$11/month)
```

**Guide Chapters:**

| # | Topic | What you'll learn |
|---|-------|-------------------|
| 1 | [Installation](https://phuc-nt.github.io/openclaw-skills/01-installation) | Hardware, software, first agent |
| 2 | [Architecture](https://phuc-nt.github.io/openclaw-skills/02-architecture) | Gateway, sessions, SOUL.md |
| 3 | [First Agent](https://phuc-nt.github.io/openclaw-skills/03-first-agent) | SOUL.md, TOOLS.md, Telegram |
| 4 | [Google Workspace](https://phuc-nt.github.io/openclaw-skills/04-google-workspace) | Gmail, Calendar, Drive, Sheets |
| 5 | [Browser Automation](https://phuc-nt.github.io/openclaw-skills/05-browser-automation) | Playwright, anti-bot, cookies |
| 6 | [Cron Jobs](https://phuc-nt.github.io/openclaw-skills/06-cron-jobs) | Scheduling, delivery, gotchas |
| 7 | [Multi-Agent Design](https://phuc-nt.github.io/openclaw-skills/07-multi-agent) | 3-agent split by domain |
| 8 | [Agent Profiles](https://phuc-nt.github.io/openclaw-skills/11-agent-profiles) | Detailed tools & workflow diagrams |
| 9 | [Model Selection](https://phuc-nt.github.io/openclaw-skills/08-model-selection) | M2.7, fallbacks, cost ($11/mo) |
| 10 | [Memory System](https://phuc-nt.github.io/openclaw-skills/09-memory-system) | kioku-lite, tri-hybrid search |
| 11 | [Operations](https://phuc-nt.github.io/openclaw-skills/10-operations) | Debugging, maintenance |

**Recipes:** [Morning Briefing](https://phuc-nt.github.io/openclaw-skills/recipes/morning-briefing) · [Email Triage](https://phuc-nt.github.io/openclaw-skills/recipes/email-triage) · [Content Digest](https://phuc-nt.github.io/openclaw-skills/recipes/content-digest) · [Book Tracker](https://phuc-nt.github.io/openclaw-skills/recipes/book-tracker) · [Expense Tracker](https://phuc-nt.github.io/openclaw-skills/recipes/expense-tracker)

---

## Installation

### Option A: Via ClawHub (recommended)

```bash
clawhub install facebook-group-monitor
```

### Option B: Manual install

```bash
git clone https://github.com/phuc-nt/openclaw-skills.git /tmp/openclaw-skills
cp -r /tmp/openclaw-skills/facebook-group-monitor \
      ~/.openclaw/workspace-YOUR-AGENT/skills/facebook-group-monitor
```

> **No restart needed** — OpenClaw auto-detects new skills.

### Option C: Ask your agent

> Install skill from https://github.com/phuc-nt/openclaw-skills/tree/main/facebook-group-monitor

---

## Skill Structure

```
skill-name/
├── SKILL.md              ← Required: agent instructions
├── scripts/              ← Executable code
├── references/           ← On-demand docs
└── assets/               ← Templates, images
```

## Contributing

1. Fork this repo
2. Create your skill following the structure above
3. Submit a PR

## License

MIT
