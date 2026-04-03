# Recipe: Morning Briefing

Daily summary of calendar, email, tasks, and reading at 7 AM.

## Prerequisites
- Google Workspace skills installed (calendar, gmail, tasks)
- Goodreads read skill (optional)

## SOUL.md Addition

```markdown
## Morning Briefing
When triggered by cron, gather and summarize:
1. Today's calendar events
2. Unread important emails
3. Pending tasks
4. Currently reading (optional)
```

## Cron Job

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
    "message": "Create morning briefing. Run these commands and summarize:\n\n1. gws calendar +agenda --today\n2. gws gmail +triage --max 10\n3. gws tasks tasks list --params '{\"tasklist\": \"@default\", \"showCompleted\": false}'\n\nFormat as concise message with emoji section headers. If a section is empty, note it briefly.",
    "timeoutSeconds": 180
  },
  "delivery": { "mode": "announce", "channel": "telegram", "to": "YOUR_ID", "bestEffort": true }
}
```

## Expected Output

```
☀️ Morning Briefing — Thu 03/04

📅 Calendar:
  • 10:00 — Team standup
  • 14:00 — Client review

📧 Email (3 unread):
  • boss@work.com — Q1 Report (urgent)
  • newsletter@tech.com — Weekly digest

✅ Tasks:
  • Deploy staging (due today)
  • Review PR #42
```

## Tips
- Increase timeout to 180s if it times out
- Agent calls tools in parallel — faster than sequential
