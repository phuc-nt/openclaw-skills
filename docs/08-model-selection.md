[🇻🇳 Tiếng Việt](vi/08-model-selection.md)

# Model Selection

Choose the right model for cost, quality, and reliability.

## Pricing Comparison (per 1M tokens)

| Model | Provider | Input | Output | Context | Tool Calling | Best For |
|---|---|---|---|---|---|---|
| Claude Haiku 4.5 | Anthropic | $1.00 | $5.00 | 200K | Excellent | Quality baseline |
| Claude Sonnet 4.5 | Anthropic | $3.00 | $15.00 | 200K | Excellent | Complex reasoning |
| Gemini 2.0 Flash | OpenRouter | $0.10 | $0.40 | 1M | Good | High-volume, cheap |
| Gemini 2.5 Flash | OpenRouter | $0.30 | $2.50 | 1M | Good | Large context |
| Kimi K2.5 | OpenRouter | $0.38 | $1.91 | 262K | Good | Instruction following |
| MiniMax M2.7 | OpenRouter | $0.30 | $1.20 | 204K | Good | Balance cost/quality |
| Qwen3 235B | OpenRouter | $0.07 | $0.10 | 262K | Decent | Ultra-cheap |

## Recommended: Unified M2.7 for All Agents

After testing multiple configurations, **one model for all agents** is the simplest and most cost-effective:

```json
"model": {
  "primary": "openrouter/minimax/minimax-m2.7",
  "fallbacks": [
    "openrouter/google/gemini-2.0-flash-001",
    "anthropic/claude-haiku-4-5"
  ]
}
```

All 3 agents (personal, research, kioku) use the same chain. M2.7 handles tool calling, Vietnamese, SOUL.md following well enough for all use cases.

**Why not different models per agent?** Tested Claude Haiku for research, Ollama local for digest — marginal quality gains didn't justify the complexity. M2.7 at $0.30/$1.20 per 1M tokens is the sweet spot.

### Local Models (Optional)

For offline/cost-zero operation, Ollama can serve as primary:

```json
"model": {
  "primary": "ollama/qwen3:4b",
  "fallbacks": ["openrouter/minimax/minimax-m2.7"]
}
```

**Caveat**: Local models are 5-10x slower and may timeout on complex cron jobs. Best used for simple chat, not tool-heavy workflows. Requires `OLLAMA_API_KEY` env var (any dummy value) and `brew services start ollama`.

## OpenRouter Setup

Add API key to `~/.openclaw/openclaw.json`:

```json
{
  "env": {
    "OPENROUTER_API_KEY": "sk-or-v1-YOUR_KEY"
  }
}
```

Model IDs use `openrouter/` prefix: `openrouter/minimax/minimax-m2.7`

## Model Quality Matrix

| Capability | Haiku 4.5 | M2.7 | Gemini Flash | Kimi K2.5 | Qwen3 |
|---|---|---|---|---|---|
| SOUL.md following | ★★★★★ | ★★★★ | ★★★ | ★★★★ | ★★★ |
| Tool calling | ★★★★★ | ★★★★ | ★★★★ | ★★★★ | ★★★ |
| Vietnamese | ★★★★★ | ★★★★ | ★★★ | ★★★ | ★★★★ |
| Speed | Fast | Fast | Very fast | Medium | Slow |
| Cron reliability | ★★★★★ | ★★★ | ★★★★ | ★★★★ | ★★★ |

## Known Issues

### Gemini 3 Flash: Session Bug
After ~50 tool calls in same session: `400 function_response.name mismatch`. Use Gemini **2.0** Flash for long sessions.

### OpenRouter Timeouts
Peak hours (UTC 0:00-06:00) may cause timeouts. Mitigation:
- Set `timeoutSeconds: 180` (not 120)
- Add Anthropic direct as final fallback
- Cron jobs retry on next schedule

### M2.7 Reasoning Mode
M2.7 sometimes returns `"content": null` with only reasoning tokens. OpenClaw may not parse this correctly. Fallback chain handles it.

## Cost Estimation

For a typical daily operation:

| Cron Job | Runs/day | Tokens/run | Model | Cost/day |
|---|---|---|---|---|
| Morning briefing | 1 | ~25K | M2.7 | $0.04 |
| Email triage | 2 | ~25K | M2.7 | $0.07 |
| Meeting prep | 10 | ~5K (most: no_meeting) | M2.7 | $0.02 |
| Reddit digest | 1 | ~100K | M2.7 | $0.15 |
| Weekly review | 0.14 | ~50K | M2.7 | $0.01 |
| Ad-hoc chat | ~10 | ~20K | M2.7 | $0.08 |
| **Total** | | | | **~$0.37/day ≈ $11/month** |

Compare: Same workload on Haiku 4.5 ≈ $40/month.

## Next: [Memory System →](09-memory-system.md)
