# OpenClaw Skills — Agent Instructions

Public skill repository: GitHub `phuc-nt/openclaw-skills` + ClawHub (clawhub.ai).

When opened from `openclaw-workspace/`, the parent CLAUDE.md defines admin identity and universal rules.

## Skill Structure

```
skill-name/
├── SKILL.md          ← Required: frontmatter + agent instructions
├── scripts/          ← Executable code (Python, Bash, JS)
├── references/       ← On-demand documentation
└── assets/           ← Templates, images, fonts
```

## Publishing Workflow

1. Develop in `/tmp/` or working directory
2. **Security scan** — grep for API keys, bot tokens, personal paths, chatId
3. **Validate** — `python3 /opt/homebrew/lib/node_modules/openclaw/skills/skill-creator/scripts/quick_validate.py <skill_folder>`
4. Copy to this repo: `./<skill-name>/`
5. `git commit` + `git push` to GitHub
6. `clawhub publish ./<skill-name> --slug <skill-name> --version X.Y.Z`

## Critical Rules

- **No personal info**: chatId, group URLs, GDrive folder IDs, hardcoded user paths → use generic placeholders
- **Relative paths only**: scripts must use `scripts/`, never `~/.openclaw/common-scripts/`
- **Flexible venv**: shell wrappers must support env var or co-located `.venv`
