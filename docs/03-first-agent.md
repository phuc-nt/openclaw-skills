[🇻🇳 Tiếng Việt](vi/03-first-agent.md)

# Your First Agent

## Step 1: Write SOUL.md

Create `~/.openclaw/workspace-personal/SOUL.md`:

```markdown
# Personal Assistant

You are a helpful personal assistant.

## Personality
- Friendly, concise
- Reply in the user's language
- Ask for clarification if unsure

## Capabilities
- Answer questions, search the web
- Run terminal commands
- Manage tasks and reminders

## Rules
- Check TOOLS.md for available tools before using them
- Never run destructive commands without confirmation
- Keep responses short and actionable
```

## Step 2: Write TOOLS.md

Create `~/.openclaw/workspace-personal/TOOLS.md`:

```markdown
# Tools

No external tools configured yet. Use built-in capabilities:
- `web_search` — Search the web
- `web_fetch` — Fetch URL content
- `exec` — Run terminal commands

See skills/ directory for installable tools.
```

## Step 3: Configure Model

Edit `~/.openclaw/openclaw.json`:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-haiku-4-5",
        "fallbacks": ["anthropic/claude-sonnet-4-5"]
      }
    },
    "list": [
      {
        "id": "personal",
        "model": {
          "primary": "anthropic/claude-haiku-4-5"
        }
      }
    ]
  }
}
```

### Model Format

**Correct** (object with primary + fallbacks):
```json
"model": {
  "primary": "anthropic/claude-haiku-4-5",
  "fallbacks": ["anthropic/claude-sonnet-4-5"]
}
```

**Wrong** (string — will cause errors):
```json
"model": "anthropic/claude-haiku-4-5"
```

## Step 4: Restart & Test

```bash
eval "$(/opt/homebrew/bin/brew shellenv)" && openclaw gateway restart
```

Message your Telegram bot: "Hello, what can you do?"

## Step 5: Install Your First Skill

Install the Google Calendar skill:

```bash
# Download from ClawHub
clawhub install gws-calendar

# Or copy manually
cp -r /path/to/gws-calendar ~/.openclaw/workspace-personal/skills/
```

Update TOOLS.md to reference the new skill:

```markdown
# Tools

| Tool | Path | Purpose |
|---|---|---|
| gws-calendar | skills/gws-calendar/ | View and manage Google Calendar |
```

Update SOUL.md to mention the capability:

```markdown
## Capabilities
- Google Calendar — view events, create meetings
```

> **No restart needed** — OpenClaw auto-detects new skills.

## Debugging

### Agent doesn't reply?

```bash
# Check gateway is running
openclaw status

# Check error log (most important!)
tail -20 ~/.openclaw/logs/gateway.err.log

# Check agent session log
ls -t ~/.openclaw/agents/personal/sessions/*.jsonl | head -1 | xargs tail -5
```

### Agent replies but ignores SOUL.md?

Some models are better at following multi-hop instructions. Ranking:

1. **Claude Sonnet/Haiku 4.5+** — excellent instruction following
2. **Kimi K2.5** — reads SKILL.md before executing, good
3. **Gemini Flash** — decent, may skip complex chains
4. **GLM** — often ignores SOUL.md entirely

If your agent ignores instructions, try a stronger model first before rewriting SOUL.md.

## Next: [Google Workspace Integration →](04-google-workspace.md)
