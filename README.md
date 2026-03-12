# 🦞 OpenClaw Skills

Community skills for [OpenClaw](https://openclaw.ai) agents.  
Published on [ClawHub](https://clawhub.ai) and mirrored here for backup & offline access.

---

## Available Skills

| Skill | Description | Version |
|-------|-------------|---------|
| [facebook-group-monitor](./facebook-group-monitor/) | Monitor Facebook groups with Playwright browser automation. Scrapes new posts, captures a stitched **feed strip** screenshot (1 image covers full feed) for efficient LLM vision analysis. | 1.3.0 |
| [goodreads](./goodreads/) | Full Goodreads integration: read shelves/search/book details via RSS + write (rate, shelf, review, edit dates, progress) via Playwright. | 1.0.0 |

---

## Installation

### Option A: Via ClawHub (recommended)

```bash
clawhub install facebook-group-monitor
```

### Option B: Manual install from this repo

```bash
# Clone this repo
git clone https://github.com/phuc-nt/openclaw-skills.git /tmp/openclaw-skills

# Install per-agent (into a specific agent's workspace)
cp -r /tmp/openclaw-skills/facebook-group-monitor \
      ~/.openclaw/workspace-YOUR-AGENT/skills/facebook-group-monitor

# OR install globally (available to all agents)
cp -r /tmp/openclaw-skills/facebook-group-monitor \
      ~/.openclaw/skills/facebook-group-monitor
```

> **No restart needed** — OpenClaw auto-detects new skills in `skills/` directories.

### Option C: Ask your agent

Paste this in your OpenClaw agent chat:

> Install skill from https://github.com/phuc-nt/openclaw-skills/tree/main/facebook-group-monitor

---

## Skill Structure

Each skill follows the [OpenClaw Skill format](https://docs.openclaw.ai/skills):

```
skill-name/
├── SKILL.md              ← Required: frontmatter + instructions for the agent
├── scripts/              ← Executable code (Python, Bash, JS...)
├── references/           ← Documentation loaded on-demand
└── assets/               ← Templates, images, fonts...
```

## Contributing

1. Fork this repo
2. Create your skill following the structure above
3. Submit a PR

## License

MIT
