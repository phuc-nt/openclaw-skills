# Setup Guide — Facebook Group Monitor

## Prerequisites

- **Python** 3.10+
- **Chromium** browser (installed via Playwright)

## Installation

### 1. Create virtual environment (recommended)

```bash
# Navigate to the scripts directory of this skill
cd <skill_path>/scripts

# Create and activate venv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install playwright playwright-stealth Pillow
```

> **Pillow** is required for stitching viewport screenshots into a single feed strip image.

### 2. Install Chromium browser

```bash
playwright install chromium
```

> **Note**: This downloads a Chromium binary (~150MB) managed by Playwright.
> It does NOT affect your system Chrome installation.

### 3. First-time login

```bash
# From terminal (NOT from agent — needs interactive browser)
./fb-group-monitor.sh login
```

This will:
1. Open a Chromium browser window
2. Navigate to facebook.com
3. **You login manually** (email + password + any 2FA)
4. Press Enter in terminal to save session

The session is stored in `scripts/.browser-data/` and typically lasts **weeks to months**.

### 4. Verify session

```bash
./fb-group-monitor.sh status
```

Expected output:
```json
{"success": true, "action": "status", "message": "Session active — logged into Facebook."}
```

## Cron Setup (Optional)

To set up periodic monitoring via OpenClaw cron:

```bash
openclaw cron add \
  --name "FB Group Monitor" \
  --agent <YOUR_AGENT_ID> \
  --schedule "0 */4 8-22 * *" \
  --timezone "YOUR/TIMEZONE" \
  --message "Check Facebook group <GROUP_URL> for new posts"
```

Adjust the schedule as needed. `0 */4 8-22 * *` = every 4 hours between 8am-10pm.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Not logged in` error | Run `login` command from terminal |
| `Facebook verification required` | Session expired — re-login needed |
| No posts found | Facebook may have changed DOM selectors |
| Screenshots not readable by agent | Use `--shots-dir` pointing to agent workspace |
| `playwright not found` | Activate venv or install: `pip install playwright` |
| `chromium not found` | Run: `playwright install chromium` |
| `ModuleNotFoundError: PIL` | Install Pillow: `pip install Pillow` |
| Feed screenshot missing / no `feed_screenshot` key | Pillow not installed or import error — check Python env |

## Alternative venv location

If you prefer a shared venv (e.g., for multiple skills), set the `FBMON_VENV` environment variable:

```bash
export FBMON_VENV="$HOME/.openclaw/common-scripts/.venv"
```

The shell wrapper checks `FBMON_VENV` first, then falls back to `scripts/.venv/`, then system Python.
