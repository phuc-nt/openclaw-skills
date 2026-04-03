# OpenClaw Multi-Agent System — Build Guide

> Build a personal AI agent system on macOS that runs 24/7, managed via Telegram.

This guide documents real-world experience building and operating a multi-agent system with OpenClaw on a Mac Mini. Every lesson comes from production use — not theory.

## What You'll Build

A system of AI agents that automate your daily life:

- **Personal Assistant** — email triage, calendar management, meeting prep, expense tracking
- **Content Digest** — automated Reddit, YouTube, Facebook summaries in your language
- **Memory Agent** — second brain that remembers everything you tell it
- **Book Tracker** — Goodreads automation (rate, review, track reading)
- **Health Journal** — daily check-ins with weekly scorecards

All controlled via Telegram. All running on your Mac.

## Guide Structure

### Getting Started
1. [Prerequisites & Installation](01-installation.md) — Hardware, software, first agent
2. [Architecture Overview](02-architecture.md) — How OpenClaw works, key concepts
3. [Your First Agent](03-first-agent.md) — SOUL.md, TOOLS.md, Telegram bot setup

### Core Skills
4. [Google Workspace Integration](04-google-workspace.md) — Gmail, Calendar, Drive, Sheets, Tasks
5. [Browser Automation](05-browser-automation.md) — Playwright for Goodreads, Facebook
6. [Cron Jobs & Scheduling](06-cron-jobs.md) — Automated workflows, delivery, troubleshooting

### Advanced
7. [Multi-Agent Design](07-multi-agent.md) — When to split vs merge agents, routing
8. [Model Selection](08-model-selection.md) — Pricing, benchmarks, fallback chains
9. [Memory System](09-memory-system.md) — Kioku-lite, tri-hybrid search, knowledge graph
10. [Operational Playbook](10-operations.md) — Debugging, common errors, maintenance

### Recipes
11. [Recipe: Morning Briefing](recipes/morning-briefing.md)
12. [Recipe: Email Triage](recipes/email-triage.md)
13. [Recipe: Content Digest](recipes/content-digest.md)
14. [Recipe: Book Tracker](recipes/book-tracker.md)
15. [Recipe: Expense Tracker](recipes/expense-tracker.md)

---

## Quick Start (5 minutes)

```bash
# Install OpenClaw
brew install openclaw

# Create your first agent
openclaw init

# Start the gateway
openclaw gateway start

# Chat with your agent on Telegram!
```

Read [Prerequisites & Installation](01-installation.md) for the full setup.

---

Built with lessons from 2+ months of daily production use. [Contribute on GitHub](https://github.com/phuc-nt/openclaw-skills).
