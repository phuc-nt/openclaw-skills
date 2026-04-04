[🇻🇳 Tiếng Việt](vi/10-operations.md)

[← Home](index.md) · [Installation](01-installation.md) · [Architecture](02-architecture.md) · [First Agent](03-first-agent.md) · [Google](04-google-workspace.md) · [Browser](05-browser-automation.md) · [Cron](06-cron-jobs.md) · [Multi-Agent](07-multi-agent.md) · [Profiles](11-agent-profiles.md) · [Models](08-model-selection.md) · [Memory](09-memory-system.md) · [Ops](10-operations.md)


# Operational Playbook

Day-to-day monitoring, debugging, and maintenance.

## Daily Checks

```bash
# 1. Gateway running?
openclaw status

# 2. Any errors?
tail -20 ~/.openclaw/logs/gateway.err.log

# 3. Cron jobs healthy?
cat ~/.openclaw/cron/jobs.json | python3 -c "
import sys,json
for j in json.load(sys.stdin)['jobs']:
    if not j.get('enabled'): continue
    s = j.get('state',{})
    err = s.get('consecutiveErrors',0)
    status = 'FAILING' if err > 0 else 'OK'
    print(f'{status:8s} {j[\"id\"]:30s} errors={err} last={s.get(\"lastRunStatus\",\"never\")}')"
```

## Debugging Agent Behavior

### Read Session Logs

```bash
# Find latest session
SESSION=$(ls -t ~/.openclaw/agents/personal/sessions/*.jsonl | head -1)

# View messages (user + assistant)
cat "$SESSION" | python3 -c "
import sys, json
for line in sys.stdin:
    obj = json.loads(line.strip())
    msg = obj.get('message', {})
    role = msg.get('role','')
    model = msg.get('model','')
    content = msg.get('content','')
    if role == 'assistant' and isinstance(content, list):
        texts = [c.get('text','')[:200] for c in content if c.get('type')=='text']
        tools = [c.get('name','') for c in content if c.get('type')=='toolCall']
        if texts: print(f'[{model}] {texts[0]}')
        if tools: print(f'[TOOLS] {tools}')
    elif role == 'user':
        txt = content[:100] if isinstance(content,str) else str(content)[:100]
        print(f'[USER] {txt}')
"
```

### View Tool Call Results

```bash
cat "$SESSION" | python3 -c "
import sys, json
for line in sys.stdin:
    obj = json.loads(line.strip())
    msg = obj.get('message', {})
    if msg.get('role') == 'toolResult':
        name = msg.get('toolName','')
        content = msg.get('content',[])
        for c in (content if isinstance(content,list) else []):
            t = c.get('text','')[:300]
            if t: print(f'[{name}] {t}')
"
```

## Common Errors & Fixes

| Error | Cause | Fix |
|---|---|---|
| **LLM request timed out** | Model/provider slow | Add fallback models; increase `timeoutSeconds` |
| **cron delivery target is missing** | Missing `delivery.to` | Add numeric Telegram user ID |
| **Unknown model** | Stale model cache | `openclaw gateway restart` |
| **No API key found** | Missing auth profile | Create `auth-profiles.json` |
| **function_response.name mismatch** | Gemini 3 Flash bug after many tool calls | Switch to Gemini 2.0 Flash |
| **Session hết hạn** (Playwright) | Browser cookies expired | Re-run login command manually |
| **No such file or directory** (scripts) | PATH not available in LaunchAgent | Use absolute paths or `uv tool install` |

## Gateway Management

```bash
# Start
openclaw gateway start

# Restart (after config changes — REQUIRED)
eval "$(/opt/homebrew/bin/brew shellenv)" && openclaw gateway restart

# Check if old process stuck
ps aux | grep openclaw-gateway | grep -v grep

# Force kill + restart
kill -9 $(pgrep -f openclaw-gateway)
openclaw gateway start

# Run diagnostics
openclaw doctor
openclaw doctor --fix  # Remove invalid config keys
```

## Backup Strategy

Create a backup script that:
1. Redacts secrets from `openclaw.json` using `jq`
2. Copies workspace files (excluding sessions, browser data)
3. Uses `rsync` (not `cp -r` — which copies hidden credential files)

```bash
# Redact secrets from config
jq 'walk(if type == "object" then
  with_entries(select(.key | test("apiKey|botToken|password|KEY|TOKEN|SECRET") | not))
else . end)' ~/.openclaw/openclaw.json > backup/openclaw.json

# Rsync workspaces (exclude sensitive data)
rsync -av --exclude='sessions/' --exclude='memory/' \
  --exclude='*.jsonl' --exclude='.browser-data/' \
  --exclude='credentials*' --exclude='token*' \
  ~/.openclaw/workspace-personal/ backup/workspace-personal/
```

## Session Cleanup

Old sessions accumulate. Auto-cleanup via cron:

```json
{
  "id": "session-cleanup",
  "agentId": "personal",
  "schedule": { "kind": "cron", "expr": "0 3 * * *" },
  "payload": {
    "message": "Run: ~/.openclaw/common-scripts/session-mgmt/cleanup-sessions.sh personal 4"
  }
}
```

Keeps only the 4 most recent sessions per agent.

## Security Checklist

- [ ] `chmod 600 ~/.openclaw/openclaw.json` (contains API keys)
- [ ] `chmod 600 ~/.openclaw/agents/*/agent/auth-profiles.json`
- [ ] OAuth consent screen published to Production (Google)
- [ ] `.gitignore` covers: `openclaw.json`, `auth-profiles.json`, `credentials*`, `token*`
- [ ] Backup script redacts all secrets before copying
- [ ] Playwright browser data excluded from backups

## Performance Tips

- **Stagger cron jobs**: Don't schedule 5 jobs at the same minute
- **Use cheap models for cron**: Digest jobs don't need Sonnet — Haiku or M2.7 works fine
- **Increase timeouts**: Content digests need 5-15 minutes, not the default 2
- **Session cleanup**: Prevent disk bloat from `.jsonl` files
- **Rate limit scripts**: 5-30s sleep between external API calls
