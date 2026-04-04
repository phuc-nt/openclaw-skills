[🇻🇳 Tiếng Việt](vi/index.md)

# OpenClaw Multi-Agent System — Build Guide

> Build a personal AI agent system on macOS that runs 24/7, managed via Telegram.

This guide documents real-world experience building and operating a multi-agent system with OpenClaw on a Mac Mini. Every lesson comes from production use — not theory.

## What You'll Build

3 AI agents that automate your daily life, split by domain of concern:

- **Personal Agent** — email triage, calendar, meeting prep, expenses, Goodreads, Typefully
- **Research Agent** — web research (Crawl4AI), Reddit/YouTube/Facebook digests, critical writing
- **Kioku Agent** — emotional companion, health check-ins, long-term memory (knowledge graph)

All controlled via Telegram. All running on your Mac. ~$11/month API cost.

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
7. [Multi-Agent Design](07-multi-agent.md) — 3-agent split by domain of concern
8. [3 Agent Profiles](11-agent-profiles.md) — Detailed tools, workflows & diagrams for each agent
9. [Model Selection](08-model-selection.md) — Unified M2.7, fallback chains, local models
10. [Memory System](09-memory-system.md) — Kioku-lite, tri-hybrid search, knowledge graph
11. [Operational Playbook](10-operations.md) — Debugging, common errors, maintenance

### Recipes
12. [Recipe: Morning Briefing](recipes/morning-briefing.md)
13. [Recipe: Email Triage](recipes/email-triage.md)
14. [Recipe: Content Digest](recipes/content-digest.md)
15. [Recipe: Book Tracker](recipes/book-tracker.md)
16. [Recipe: Expense Tracker](recipes/expense-tracker.md)

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
