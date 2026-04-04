[🇻🇳 Tiếng Việt](../vi/recipes/email-triage.md)

[← Home](../index.md) · [Installation](../01-installation.md) · [Architecture](../02-architecture.md) · [First Agent](../03-first-agent.md) · [Google](../04-google-workspace.md) · [Browser](../05-browser-automation.md) · [Cron](../06-cron-jobs.md) · [Multi-Agent](../07-multi-agent.md) · [Profiles](../11-agent-profiles.md) · [Models](../08-model-selection.md) · [Memory](../09-memory-system.md) · [Ops](../10-operations.md)


# Recipe: Email Triage

Classify unread emails into Urgent / Action / FYI / Noise twice daily.

## Cron Job

```json
{
  "id": "email-triage",
  "agentId": "personal",
  "name": "Email Triage - 9AM & 3PM",
  "enabled": true,
  "schedule": { "kind": "cron", "expr": "0 9,15 * * *", "tz": "Your/Timezone" },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "Classify unread emails. Run:\n\n1. gws gmail +triage --max 20\n\nClassify each into:\n- 🚨 Urgent: needs reply today\n- 📋 Action: needs handling, not urgent\n- 📰 FYI: newsletters, notifications\n- 🗑 Noise: spam, irrelevant promotions\n\nFormat as Telegram message. Urgent first. If inbox empty: send '📧 Inbox clear!'",
    "timeoutSeconds": 180
  },
  "delivery": { "mode": "announce", "channel": "telegram", "to": "YOUR_ID", "bestEffort": true }
}
```
