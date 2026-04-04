[🇻🇳 Tiếng Việt](vi/07-multi-agent.md)

# Multi-Agent Design

When to use one agent vs many, and how they communicate.

## Design Principle: Separate by Concern, Not by Task

Don't create one agent per task. Instead, split by **domain of concern**:

| Domain | Agent | What it handles |
|---|---|---|
| **My life** | `personal` | Email, calendar, tasks, expenses, books — everything about *me* |
| **The world** | `research` | Web research, content digests, Reddit/YouTube/Facebook — everything from *the internet* |
| **Inner self** | `kioku` | Emotions, health check-ins, memories — *how I feel* |

## Recommended: 3 Agent Architecture

| Agent | Purpose | Telegram Bot | Model | Skills |
|---|---|---|---|---|
| **personal** | Daily life management | Personal Bot | MiniMax M2.7 | gws-* (15), goodreads, typefully |
| **research** | Internet content & research | Research Bot | MiniMax M2.7 | crawl4ai, reddit, youtube, facebook |
| **kioku** | Memory & emotional companion | Kioku Bot | MiniMax M2.7 | kioku-lite CLI |

### Why 3 Agents?

- **personal** handles high-volume personal tasks (email triage, calendar, expenses)
- **research** handles content ingestion from the internet (digests, deep research, article analysis)
- **kioku** handles emotional context that shouldn't mix with task-oriented agents
- Each agent has a focused SOUL.md — better instruction following
- Cron jobs route to the right agent by domain

### Evolution Path

```
Stage 1: 1 agent (personal does everything)
Stage 2: 2 agents (split memory → kioku)
Stage 3: 3 agents (split internet content → research)  ← current
```

## Cron Job Routing

Jobs route to the agent that owns that domain:

```json
// Personal agent — "my life" cron jobs
morning-briefing → personal (calendar + email + tasks)
email-triage → personal
prep-next-meeting → personal
calendar-conflict → personal
weekly-review → personal

// Research agent — "internet content" cron jobs
reddit-digest → research
youtube-digest → research
fb-group-monitor → research

// Kioku agent — "inner self" cron jobs
health-checkin → kioku
```

## Cross-Agent Communication

Agents share tools, not conversations:

```bash
# Personal agent queries memory
kioku-lite search "meeting with client" --limit 5 --entities

# Research agent saves interesting findings
kioku-lite save --content "..." --tags "research,ai"

# Neither research nor kioku access personal's Gmail/Calendar
# (by design — separation of concerns)
```

## Routing: One Bot Per Agent

```json
{
  "bindings": [
    { "accountId": "personal", "agentId": "personal" },
    { "accountId": "research", "agentId": "research" },
    { "accountId": "kioku", "agentId": "kioku" }
  ]
}
```

## Anti-Pattern: Too Many or Too Few

**Don't** create 5+ agents (one per task). Problems: confusing UX, duplicated rules, multiplied costs.

**Don't** keep everything in one agent. Problems: SOUL.md becomes huge, conflicting personalities, context window fills up.

**Sweet spot**: 3 agents split by domain of concern.

## Next: [Model Selection →](08-model-selection.md)
