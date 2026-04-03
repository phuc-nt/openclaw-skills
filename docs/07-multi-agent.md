[🇻🇳 Tiếng Việt](vi/07-multi-agent.md)

# Multi-Agent Design

When to use one agent vs many, and how they communicate.

## Design Principle: Start with One, Split When Needed

**Start**: One `personal` agent that does everything.

**Split when**:
- Agent has conflicting personalities (assistant vs emotional companion)
- Context window fills up (too many skills loaded)
- Different models needed (cheap for digest, smart for memory)
- You want separate Telegram bots for different purposes

## Recommended: 2 Agent Architecture

| Agent | Purpose | Telegram Bot | Model |
|---|---|---|---|
| **personal** | Daily tasks, all automation, digests | Bot A | Fast + cheap (MiniMax M2.7, Gemini Flash) |
| **memory** | Second brain, emotional journal, health | Bot B | Smart + empathetic (Claude Haiku) |

### Why This Works

- **personal** handles high-volume, low-stakes tasks (email triage, calendar, digests)
- **memory** handles low-volume, high-importance tasks (memories, reflections)
- Cron jobs use **isolated sessions** → don't pollute chat context
- Cross-agent communication via CLI: personal calls `kioku-lite search` when needed

## Cross-Agent Communication

Agents don't talk to each other directly. Instead, they share tools:

```bash
# Personal agent queries memory agent's data
kioku-lite search "meeting with client" --limit 5 --entities

# Memory agent has no access to personal's Gmail/Calendar
# (by design — separation of concerns)
```

In SOUL.md of personal agent:
```markdown
## Cross-agent: Memory (kioku-lite)
When you need past context, query:
kioku-lite search "query" --limit 10 --entities
```

## Routing: One Bot Per Agent

```json
{
  "channels": {
    "telegram": {
      "accounts": {
        "assistant": { "botToken": "BOT_A_TOKEN" },
        "memory": { "botToken": "BOT_B_TOKEN" }
      }
    }
  },
  "bindings": [
    { "accountId": "assistant", "agentId": "personal" },
    { "accountId": "memory", "agentId": "kioku" }
  ]
}
```

User messages Bot A → personal agent. Messages Bot B → memory agent.

## Cron Jobs: All on Personal

Even digest jobs (Reddit, YouTube) run on `personal` agent — they use isolated sessions so they don't interfere with chat. Only `health-checkin` runs on memory agent (needs emotional context).

```json
// All these go to personal agent
morning-briefing → personal (isolated)
email-triage → personal (isolated)
reddit-digest → personal (isolated)
weekly-review → personal (isolated)

// This one goes to memory agent
health-checkin → kioku (isolated)
```

## Anti-Pattern: Too Many Agents

**Don't** create separate agents for: email, calendar, books, reddit, youtube.

Problems:
- 5+ Telegram bots = confusing UX
- Duplicated SOUL.md rules across agents
- Model costs multiply (each agent loads full context)
- Cron job management becomes complex

**Instead**: One personal agent with multiple skills, using cron isolated sessions.

## Next: [Model Selection →](08-model-selection.md)
