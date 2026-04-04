[🇻🇳 Tiếng Việt](vi/05-browser-automation.md)

[← Home](index.md) · [Installation](01-installation.md) · [Architecture](02-architecture.md) · [First Agent](03-first-agent.md) · [Google](04-google-workspace.md) · [Browser](05-browser-automation.md) · [Cron](06-cron-jobs.md) · [Multi-Agent](07-multi-agent.md) · [Profiles](11-agent-profiles.md) · [Models](08-model-selection.md) · [Memory](09-memory-system.md) · [Ops](10-operations.md)


# Browser Automation

Use Playwright to automate websites that don't have APIs — Goodreads, Facebook, etc.

## Setup

```bash
# Create shared venv for all scripts
python3 -m venv ~/.openclaw/common-scripts/.venv
source ~/.openclaw/common-scripts/.venv/bin/activate
pip install playwright playwright-stealth
playwright install chromium
```

## Anti-bot Protection

Websites detect headless browsers. Essential countermeasures:

```python
from playwright.async_api import async_playwright

context = await playwright.chromium.launch_persistent_context(
    user_data_dir="~/.openclaw/common-scripts/<service>/.browser-data",
    headless=True,
    viewport={"width": 1280, "height": 800},
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
               "AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/131.0.0.0 Safari/537.36",
    args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
    ignore_default_args=["--enable-automation"],
)

# Apply stealth plugin
from playwright_stealth import stealth_async
await stealth_async(page)
```

Key techniques:
- **Persistent context**: Cookies survive across runs (weeks/months)
- **Stealth plugin**: Masks WebDriver fingerprint
- **Real user agent**: Match current Chrome version
- **Disable automation flags**: Remove `--enable-automation`

## Pattern: Login Once, Automate Forever

```python
# First time: headless=False, user logs in manually
# After that: headless=True, cookies persist

async def cmd_login():
    context = await create_browser_context(headless=False)  # Shows browser
    page = context.pages[0]
    await page.goto("https://service.com/login")
    input("Press Enter after logging in...")  # Wait for user
    await context.close()  # Cookies saved!

async def cmd_action():
    context = await create_browser_context(headless=True)   # No browser window
    # Cookies loaded automatically from persistent context
    page = context.pages[0]
    await page.goto("https://service.com/protected-page")
    # ... do stuff
```

## Pattern: JSON Output for Agent Integration

All automation scripts should output JSON:

```python
import json, sys

def result_json(success, action, **kwargs):
    data = {"success": success, "action": action, **kwargs}
    print(json.dumps(data, ensure_ascii=False, indent=2))
    sys.exit(0 if success else 1)

# Usage
result_json(True, "rate", book_id="123", stars=5,
            message="Rated 5 stars for 'Project Hail Mary'")
```

Agent reads JSON output to confirm success and report to user.

## Pattern: RSS Verification

After browser actions (shelf change, rating), verify via RSS/API:

```python
def verify_shelf_rss(user_id, book_id, expected_shelf):
    import urllib.request, xml.etree.ElementTree as ET
    url = f"https://www.goodreads.com/review/list_rss/{user_id}?shelf={expected_shelf}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        root = ET.fromstring(r.read().decode("utf-8"))
    for item in root.findall(".//item"):
        if item.findtext("book_id") == str(book_id):
            return True
    return False
```

## Gotchas

### DOM Selectors Change
Websites update their HTML frequently. Defensive strategies:
- Use `aria-label` selectors (more stable than CSS classes)
- Add multiple fallback selectors
- Log the actual page content when selectors fail

### Screenshots Must Be in Workspace
OpenClaw sandbox restricts file access. Screenshots must be saved to agent workspace:
```bash
--shots-dir ~/.openclaw/workspace-personal/temp-screenshots
```

### Rate Limiting
```python
await page.wait_for_timeout(2000)  # 2s between actions
```
Don't hammer — Goodreads/Facebook will block you.

### Goodreads-Specific: Edit Page Redirect
Goodreads redirects `/review/edit/{id}` → `/review/new/{id}` for books without prior reviews. Accept both URL patterns:
```python
is_review_page = "/review/edit" in url or "/review/new" in url
```

## Next: [Cron Jobs & Scheduling →](06-cron-jobs.md)
