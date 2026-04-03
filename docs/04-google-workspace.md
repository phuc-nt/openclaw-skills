[🇻🇳 Tiếng Việt](vi/04-google-workspace.md)

# Google Workspace Integration

Connect your agent to Gmail, Calendar, Drive, Sheets, Docs, and Tasks.

## Setup

### Install gws CLI

```bash
npm install -g @googleworkspace/cli
```

### Configure OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project, enable APIs: Gmail, Calendar, Drive, Sheets, Docs, Tasks
3. Create OAuth 2.0 credentials (Desktop App type)
4. Download `credentials.json`

```bash
# Authenticate (run manually — NOT from agent)
gws auth login
# Opens browser → grant permissions → token saved
```

### Critical: Publish OAuth to Production

> **If your OAuth consent screen is in "Testing" mode, refresh tokens expire after 7 days.**

Go to Google Cloud Console → OAuth consent screen → **Publish to Production**.

### Credential Precedence (important!)

The `gws` CLI checks credentials in this order:
1. `GOOGLE_WORKSPACE_CLI_TOKEN` env var
2. `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` env var
3. Encrypted `credentials.enc` + OS keyring ← **recommended**
4. Plain `credentials.json`
5. gcloud ADC

**Best practice**: Let `gws auth login` create encrypted credentials. Do NOT set env vars pointing to plain files.

### Agent Rule: NEVER `gws auth login`

Agents cannot run `gws auth login` — it starts a localhost OAuth server and opens a browser, which agents don't have. The process will hang.

Add to SOUL.md:
```markdown
## Rules
- NEVER run `gws auth login` — auth is pre-configured
- If you get 401 errors, tell the user to fix auth manually
```

## Verified Actions (32 total)

| Service | Actions |
|---|---|
| **Gmail** | list unread, search, read content, send, draft, mark read, list labels |
| **Calendar** | list calendars, list events, create, edit, delete, quickAdd, free/busy |
| **Drive** | list files, search, upload, delete, create folder |
| **Sheets** | create, append rows, read data, delete |
| **Docs** | create, write text, read, delete |
| **Tasks** | list task lists, create task, delete |
| **Slides** | create, delete |

## Common Patterns

### Email Triage
```bash
gws gmail +triage --max 20
```

### Today's Calendar
```bash
gws calendar +agenda --today
```

### Upload to Drive
```bash
gws drive +upload report.md --parent FOLDER_ID --format json
```

### Append to Sheets
```bash
gws sheets +append --spreadsheet-id SHEET_ID --range "Sheet1!A:D" --values '[["2026-04-03", "150000", "Lunch", "Food"]]'
```

### Helper Command Syntax

All helper commands use `+` prefix with `kebab-case` flags:
```bash
# Correct
gws gmail +reply --message-id MSG_ID --body "Thanks"

# Wrong (no + prefix)
gws gmail reply --message-id MSG_ID --body "Thanks"

# Wrong (camelCase flag)
gws gmail +reply --messageId MSG_ID --body "Thanks"
```

### Discover Commands
```bash
gws gmail --help                    # List resources & methods
gws schema gmail.users.messages.list  # See parameters
```

## SKILL.md Structure

For each gws service, create a skill:

```
skills/
├── gws-shared/SKILL.md         # Auth rules, global flags
├── gws-gmail/SKILL.md          # Gmail-specific commands
├── gws-gmail-send/SKILL.md     # Send/reply helpers
├── gws-gmail-triage/SKILL.md   # Inbox triage helper
├── gws-calendar/SKILL.md       # Calendar management
├── gws-calendar-agenda/SKILL.md # Agenda view helper
├── gws-drive/SKILL.md          # Drive file management
├── gws-drive-upload/SKILL.md   # Upload helper
├── gws-sheets/SKILL.md         # Sheets CRUD
├── gws-tasks/SKILL.md          # Task management
└── gws-docs/SKILL.md           # Docs read/write
```

> Run `gws generate-skills` to auto-generate SKILL.md files for all services.

## Common Issues

| Problem | Cause | Fix |
|---|---|---|
| 401 Unauthorized | Token expired (Testing mode) | Publish OAuth to Production |
| `gws auth login` hangs | Agent has no browser | Run manually in terminal |
| "unrecognized subcommand" | Wrong method name | Run `gws <service> --help` first |
| Send fails but read works | Insufficient scopes | Re-auth with all scopes |

## Next: [Browser Automation →](05-browser-automation.md)
