# Architecture Overview

## How OpenClaw Works

```
┌──────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│ Telegram  │────▶│   Gateway    │────▶│    Agent    │────▶│   LLM    │
│   User    │◀────│ (localhost)  │◀────│  (session)  │◀────│ Provider │
└──────────┘     └──────────────┘     └─────────────┘     └──────────┘
                        │                     │
                        │              ┌──────┴──────┐
                        │              │  Workspace   │
                  ┌─────┴─────┐       │  SOUL.md     │
                  │  Cron     │       │  TOOLS.md    │
                  │  Scheduler│       │  skills/     │
                  └───────────┘       └──────────────┘
```

### Gateway
- HTTP server on `localhost:18789` (loopback only — not exposed to network)
- Routes Telegram messages to agents via account→binding mappings
- Manages sessions, cron scheduler, model fallback
- Runs as macOS LaunchAgent (auto-start on boot)

### Agent
- Each agent has an isolated workspace at `~/.openclaw/workspace-<id>/`
- Identity defined by `SOUL.md` (personality + rules)
- Tools listed in `TOOLS.md` (inventory + syntax)
- Detailed tool docs in `skills/<name>/SKILL.md`

### Session
- Conversation history persisted in `.jsonl` files
- Cron jobs run in **isolated sessions** (no chat history)
- Sessions auto-compact when approaching context limit

## Key Concepts

### SOUL.md — Agent Identity

The most important file. Defines WHO your agent is and HOW it behaves:

```markdown
# Personal Assistant

You are a personal assistant. You help with daily tasks.

## Rules
- Reply in Vietnamese
- Always confirm before sending emails
- Check TOOLS.md for available tools

## Capabilities
- Email management (Gmail)
- Calendar management
- Task tracking
```

> **80% of agent quality depends on SOUL.md writing, not the model.**

### TOOLS.md — Tool Inventory

Quick reference for all available tools:

```markdown
# Tools

| Tool | Path | Purpose |
|---|---|---|
| gmail | skills/gws-gmail/ | Read, search, manage email |
| calendar | skills/gws-calendar/ | View and create events |

When using a tool → read its SKILL.md first for exact syntax.
```

### SKILL.md — Detailed Tool Docs

Per-tool documentation with parameters, examples, gotchas:

```markdown
---
name: gws-gmail
version: 1.0.0
description: "Gmail: Send, read, and manage email."
---

# Gmail

## Usage
gws gmail <resource> <method> [flags]

## Examples
gws gmail +triage --max 10
gws gmail +send --to user@example.com --subject "Hi" --body "Hello"
```

### Bindings — Routing Messages to Agents

```json
{
  "channels": {
    "telegram": {
      "accounts": {
        "personal": { "botToken": "..." },
        "memory": { "botToken": "..." }
      }
    }
  },
  "bindings": [
    { "accountId": "personal", "agentId": "personal" },
    { "accountId": "memory", "agentId": "kioku" }
  ]
}
```

Each Telegram bot → one account → one agent. Users message different bots for different agents.

## File Structure

```
~/.openclaw/
├── openclaw.json                    # Master config
├── cron/jobs.json                   # Scheduled tasks
├── logs/gateway.err.log             # Error diagnostics
├── agents/
│   └── <agent-id>/
│       ├── agent/auth-profiles.json # API keys (chmod 600)
│       └── sessions/                # Conversation logs
├── workspace-personal/
│   ├── SOUL.md                      # Agent identity
│   ├── TOOLS.md                     # Tool inventory
│   ├── skills/                      # Installed skills
│   ├── config/                      # Agent-specific config
│   └── memory/                      # Persistent state
└── common-scripts/                  # Shared scripts (all agents)
    ├── goodreads/
    ├── facebook/
    ├── reddit/
    └── youtube/
```

### Why `common-scripts/`?

Scripts go in `~/.openclaw/common-scripts/<category>/`, NOT in agent workspaces.
- Reusable across agents
- Accept workspace path as argument
- Avoids duplicating code per agent

## Next: [Your First Agent →](03-first-agent.md)
