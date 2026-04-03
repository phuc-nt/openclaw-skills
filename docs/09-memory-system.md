# Memory System

Give your agent persistent memory across sessions using Kioku-lite.

## What is Kioku-lite?

A local-first personal memory engine. Zero Docker, zero cloud. Stores memories in SQLite with tri-hybrid search:

1. **BM25** (keyword) — exact entity matches
2. **Vector** (semantic) — conceptual similarity via FastEmbed
3. **Knowledge Graph** — relationship traversal

Results merged via Reciprocal Rank Fusion (RRF).

## Installation

```bash
uv tool install "kioku-agent-kit-lite[cli]"
kioku-lite --help
```

## Core Commands

### Save a Memory
```bash
kioku-lite save --content "Had a great meeting with team about Q2 goals" \
  --mood happy --tags "work,meeting,planning"
# Returns: content_hash (use for kg-index)
```

### Index Entities (Knowledge Graph)
```bash
kioku-lite kg-index <content_hash> \
  --entities "PERSON:TeamLead,LIFE_EVENT:Q2-planning" \
  --relations "SHARED_MOMENT_WITH:TeamLead"
```

### Search Memories
```bash
kioku-lite search "Q2 planning" --limit 10 --entities
# Always pass --entities to activate graph search
```

### Recall by Entity
```bash
kioku-lite recall "TeamLead" --hops 2
# Shows all memories connected to this entity within 2 hops
```

### Timeline View
```bash
kioku-lite timeline --from 2026-03-01 --to 2026-03-31 --limit 20
```

## Entity Types

| Type | Examples |
|---|---|
| PERSON | TeamLead, Mom, Client-A |
| EMOTION | happy, anxious, grateful, proud |
| LIFE_EVENT | health-checkin, book-finished, project-launch |
| COPING_MECHANISM | running, reading, meditation |
| PLACE | Office, Home, Tokyo |

## Relationship Types

| Relation | Example |
|---|---|
| TRIGGERED_BY | anxiety TRIGGERED_BY deadline |
| REDUCED_BY | stress REDUCED_BY running |
| BROUGHT_JOY | reading BROUGHT_JOY happiness |
| SHARED_MOMENT_WITH | meeting SHARED_MOMENT_WITH TeamLead |
| HAPPENED_AT | lunch HAPPENED_AT Office |

## Critical Rule: Never Summarize

When saving memories, store the **exact user text**. Never summarize, paraphrase, or trim.

```bash
# Wrong — summarized
kioku-lite save --content "User had a good day"

# Correct — verbatim
kioku-lite save --content "Today was amazing! Finally shipped the feature after 3 weeks of debugging. The team celebrated with pizza. Sarah said it was the cleanest PR she's ever reviewed."
```

For long content (>300 chars), split into multiple saves by topic.

## Integration with Personal Agent

In personal agent's TOOLS.md:

```markdown
## Cross-agent: Memory
kioku-lite search "query" --limit 10 --entities
kioku-lite save --content "..." --tags "tag1,tag2" --mood neutral
```

Use cases:
- **Weekly Review**: `kioku-lite search "this week" --limit 10` to include memories in scorecard
- **Read Later**: Save article summaries with `--tags "read-later,tech"`
- **Health Journal**: Save daily check-ins with `--tags "health,sleep,mood"`

## Data Location

```
~/.kioku/users/<user_id>/
├── memory/           # Markdown source files
└── data/
    └── kioku_fts.db  # SQLite FTS5 + vector + graph
```

## Next: [Operational Playbook →](10-operations.md)
