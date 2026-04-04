[🇻🇳 Tiếng Việt](vi/06-cron-jobs.md)

# Cron Jobs & Scheduling

Automate recurring tasks — morning briefings, email triage, content digests.

## Cron Job Structure

Edit `~/.openclaw/cron/jobs.json`:

```json
{
  "version": 1,
  "jobs": [
    {
      "id": "morning-briefing",
      "agentId": "personal",
      "name": "Morning Briefing - 7AM Daily",
      "enabled": true,
      "schedule": {
        "kind": "cron",
        "expr": "0 7 * * *",
        "tz": "Asia/Ho_Chi_Minh"
      },
      "sessionTarget": "isolated",
      "wakeMode": "now",
      "payload": {
        "kind": "agentTurn",
        "message": "Your prompt here — what the agent should do",
        "timeoutSeconds": 180
      },
      "delivery": {
        "mode": "announce",
        "channel": "telegram",
        "to": "YOUR_TELEGRAM_USER_ID",
        "bestEffort": true
      }
    }
  ]
}
```

### Key Fields

| Field | Description |
|---|---|
| `id` | Unique identifier |
| `agentId` | Which agent runs this job |
| `schedule.expr` | Standard 5-field cron expression |
| `schedule.tz` | Timezone (e.g., `Asia/Ho_Chi_Minh`, `America/New_York`) |
| `sessionTarget` | `"isolated"` — fresh session each run (recommended for cron) |
| `payload.message` | The prompt sent to the agent |
| `payload.timeoutSeconds` | Max execution time before abort |
| `delivery.to` | **Numeric** Telegram user ID (NOT username) |
| `delivery.mode` | `"announce"` — send result to Telegram |

### Finding Your Telegram User ID

Message `@userinfobot` on Telegram — it replies with your numeric ID.

## Example: Morning Briefing

```json
{
  "id": "morning-briefing",
  "agentId": "personal",
  "name": "Morning Briefing - 7AM Daily",
  "enabled": true,
  "schedule": { "kind": "cron", "expr": "0 7 * * *", "tz": "Your/Timezone" },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "Create a morning briefing:\n1. gws calendar +agenda --today\n2. gws gmail +triage --max 10\n3. gws tasks tasks list --params '{\"tasklist\": \"@default\"}'\nFormat as a concise Telegram message.",
    "timeoutSeconds": 180
  },
  "delivery": { "mode": "announce", "channel": "telegram", "to": "YOUR_ID", "bestEffort": true }
}
```

## Example: Silent Check (No Notification)

For jobs that only notify when something is found:

```json
{
  "payload": {
    "message": "Check calendar for conflicts in next 7 days.\nIf NO conflicts → reply 'ok' and STOP.\nIf conflicts found → send details via Telegram."
  }
}
```

The agent decides whether to send a Telegram message based on results.

## Manual Trigger

```bash
eval "$(/opt/homebrew/bin/brew shellenv)"
openclaw cron run morning-briefing
```

## Critical Gotchas

### 1. Isolated Sessions Have No Chat Context

Cron jobs run in fresh sessions — they don't see previous chat history. The agent only knows what's in:
- SOUL.md + TOOLS.md (loaded at session start)
- The cron payload message

**Implication**: Include ALL context in the payload message. Don't assume the agent remembers anything.

### 2. Use Numeric Telegram ID, Not Username

```json
// Wrong — will fail
"to": "MyUsername"

// Correct — numeric user ID
"to": "1234567890"
```

### 3. State Cache After Schedule Changes

After editing `schedule.expr`, you MUST:
1. Reset the state: set `"state": {}` in the job
2. Restart gateway: `openclaw gateway restart`

Without this, the old schedule remains cached.

### 4. Timeout for Complex Jobs

Reddit/YouTube digests can take 5+ minutes. Set adequate timeout:

```json
"timeoutSeconds": 900  // 15 minutes for content digests
```

Default timeout may be too short — job gets aborted silently.

### 5. Multiple Jobs Queuing

Jobs run sequentially in the cron lane. If 5 jobs trigger at similar times, later jobs wait. Stagger schedules:

```
7:00 — Morning briefing      → personal
7:15 — Calendar conflict      → personal
7:30 — Health check-in        → kioku
9:00 — Email triage           → personal
10:00 — Reddit digest         → research
```

**Note**: In a 3-agent setup, route digest cron jobs to the `research` agent and personal tasks to `personal`. Jobs on different agents can run in parallel.

## Monitoring Cron Jobs

```bash
# Check which jobs are failing
cat ~/.openclaw/cron/jobs.json | python3 -c "
import sys,json
for j in json.load(sys.stdin)['jobs']:
    s = j.get('state',{})
    if s.get('consecutiveErrors',0) > 0:
        print(f\"FAILING: {j['id']} — {s.get('lastError','unknown')}\")"

# Check gateway error log
tail -20 ~/.openclaw/logs/gateway.err.log

# Check a specific job's latest session
ls -t ~/.openclaw/agents/personal/sessions/*.jsonl | head -1
```

## Next: [Multi-Agent Design →](07-multi-agent.md)
