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

## Recommended: Fallback Chain

```json
"model": {
  "primary": "openrouter/minimax/minimax-m2.7",
  "fallbacks": [
    "openrouter/google/gemini-2.0-flash-001",
    "openrouter/qwen/qwen3-235b-a22b-2507",
    "anthropic/claude-haiku-4-5"
  ]
}
```

**Why**: M2.7 is 3-4x cheaper than Haiku with comparable quality. If it times out, Gemini Flash picks up. If OpenRouter is down entirely, Haiku (Anthropic direct) is the safety net.

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
