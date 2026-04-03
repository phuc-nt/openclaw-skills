[🇻🇳 Tiếng Việt](vi/01-installation.md)

# Prerequisites & Installation

## Hardware

- **Mac Mini M1/M2/M4** (or any Mac running 24/7)
- 8GB RAM minimum, 16GB+ recommended
- Stable internet connection

## Software Requirements

| Software | Purpose | Install |
|---|---|---|
| Homebrew | Package manager | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| OpenClaw | Agent framework | `brew install openclaw` |
| Node.js 20+ | Runtime for skills | `brew install node` |
| Python 3.12+ | Scripts & tools | `brew install python@3.12` |
| uv | Python package installer | `brew install uv` |
| jq | JSON processing | `brew install jq` |

## Accounts Needed

| Account | Purpose | Cost |
|---|---|---|
| **Anthropic API** | Claude models (primary) | Pay-per-use (~$5-20/month) |
| **Telegram Bot** | User interface | Free (create via @BotFather) |
| **OpenRouter** (optional) | Alternative models (Gemini, Kimi, MiniMax) | Pay-per-use |

## Step 1: Install OpenClaw

```bash
eval "$(/opt/homebrew/bin/brew shellenv)"
brew install openclaw
```

## Step 2: Initialize

```bash
openclaw init
```

This creates:
```
~/.openclaw/
├── openclaw.json          # Master config
├── agents/                # Agent session storage
├── workspace-personal/    # Default agent workspace
├── cron/jobs.json         # Scheduled tasks
└── logs/                  # Error logs
```

## Step 3: Add API Key

```bash
# Create auth profile for your agent
mkdir -p ~/.openclaw/agents/personal/agent
cat > ~/.openclaw/agents/personal/agent/auth-profiles.json << 'EOF'
{
  "profiles": {
    "default": {
      "provider": "anthropic",
      "apiKey": "sk-ant-YOUR_KEY_HERE"
    }
  }
}
EOF
chmod 600 ~/.openclaw/agents/personal/agent/auth-profiles.json
```

> **Security**: Always `chmod 600` files containing API keys.

## Step 4: Create Telegram Bot

1. Open Telegram, search for `@BotFather`
2. Send `/newbot`, follow prompts
3. Copy the bot token (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Add to `~/.openclaw/openclaw.json`:

```json
{
  "channels": {
    "telegram": {
      "accounts": {
        "personal": {
          "botToken": "YOUR_BOT_TOKEN"
        }
      }
    }
  },
  "bindings": [
    {
      "accountId": "personal",
      "agentId": "personal"
    }
  ]
}
```

## Step 5: Start Gateway

```bash
openclaw gateway start
```

The gateway runs as a macOS LaunchAgent — it auto-starts on boot.

## Step 6: Verify

```bash
# Check status
openclaw status

# Check for errors
tail ~/.openclaw/logs/gateway.err.log
```

Now message your bot on Telegram — it should reply!

## Common Issues

| Problem | Cause | Fix |
|---|---|---|
| "No API key found" | Missing `auth-profiles.json` | Create file per Step 3 |
| Bot doesn't reply | Gateway not running | `openclaw gateway restart` |
| "Unknown model" | Stale model cache | `openclaw gateway restart` |
| Web UI unauthorized | Need password | Check `gateway.password` in config |

## Next: [Architecture Overview →](02-architecture.md)
