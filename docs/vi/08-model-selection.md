[🇬🇧 English](../08-model-selection.md)

[← Trang chủ](index.md) · [Cài đặt](01-installation.md) · [Kiến trúc](02-architecture.md) · [Agent đầu tiên](03-first-agent.md) · [Google](04-google-workspace.md) · [Trình duyệt](05-browser-automation.md) · [Cron](06-cron-jobs.md) · [Multi-Agent](07-multi-agent.md) · [Hồ sơ Agent](11-agent-profiles.md) · [Model](08-model-selection.md) · [Bộ nhớ](09-memory-system.md) · [Vận hành](10-operations.md)


# Lựa chọn Model

Chọn model phù hợp về chi phí, chất lượng, và độ tin cậy.

## So sánh Giá (mỗi 1M token)

| Model | Provider | Input | Output | Context | Tool Calling | Phù hợp cho |
|---|---|---|---|---|---|---|
| Claude Haiku 4.5 | Anthropic | $1.00 | $5.00 | 200K | Xuất sắc | Baseline chất lượng |
| Claude Sonnet 4.5 | Anthropic | $3.00 | $15.00 | 200K | Xuất sắc | Suy luận phức tạp |
| Gemini 2.0 Flash | OpenRouter | $0.10 | $0.40 | 1M | Tốt | Khối lượng lớn, rẻ |
| Gemini 2.5 Flash | OpenRouter | $0.30 | $2.50 | 1M | Tốt | Context lớn |
| Kimi K2.5 | OpenRouter | $0.38 | $1.91 | 262K | Tốt | Tuân theo hướng dẫn |
| MiniMax M2.7 | OpenRouter | $0.30 | $1.20 | 204K | Tốt | Cân bằng chi phí/chất lượng |
| Qwen3 235B | OpenRouter | $0.07 | $0.10 | 262K | Khá | Siêu rẻ |

## Khuyến nghị: Thống nhất M2.7 cho Tất cả Agent

Sau khi thử nhiều cấu hình, **một model cho tất cả agent** là đơn giản và tiết kiệm nhất:

```json
"model": {
  "primary": "openrouter/minimax/minimax-m2.7",
  "fallbacks": [
    "openrouter/google/gemini-2.0-flash-001",
    "anthropic/claude-haiku-4-5"
  ]
}
```

Cả 3 agent (personal, research, kioku) dùng cùng chuỗi. M2.7 xử lý tốt tool calling, tiếng Việt, tuân theo SOUL.md cho mọi use case.

**Tại sao không dùng model khác cho mỗi agent?** Đã test Claude Haiku cho research, Ollama local cho digest — chất lượng tăng nhẹ không đáng đổi lại độ phức tạp. M2.7 ở mức $0.30/$1.20 mỗi 1M token là điểm cân bằng tốt nhất.

### Model Local (Tùy chọn)

Cho vận hành offline/miễn phí, Ollama có thể làm primary:

```json
"model": {
  "primary": "ollama/qwen3:4b",
  "fallbacks": ["openrouter/minimax/minimax-m2.7"]
}
```

**Lưu ý**: Model local chậm hơn 5-10 lần, có thể timeout với cron job phức tạp. Phù hợp cho chat đơn giản, không cho workflow nặng tool. Cần `OLLAMA_API_KEY` (giá trị bất kỳ) và `brew services start ollama`.

## Thiết lập OpenRouter

Thêm API key vào `~/.openclaw/openclaw.json`:

```json
{
  "env": {
    "OPENROUTER_API_KEY": "sk-or-v1-KEY_CUA_BAN"
  }
}
```

Model ID dùng tiền tố `openrouter/`: `openrouter/minimax/minimax-m2.7`

## Ma trận Chất lượng Model

| Khả năng | Haiku 4.5 | M2.7 | Gemini Flash | Kimi K2.5 | Qwen3 |
|---|---|---|---|---|---|
| Tuân theo SOUL.md | ★★★★★ | ★★★★ | ★★★ | ★★★★ | ★★★ |
| Gọi tool | ★★★★★ | ★★★★ | ★★★★ | ★★★★ | ★★★ |
| Tiếng Việt | ★★★★★ | ★★★★ | ★★★ | ★★★ | ★★★★ |
| Tốc độ | Nhanh | Nhanh | Rất nhanh | Trung bình | Chậm |
| Độ tin cậy cron | ★★★★★ | ★★★ | ★★★★ | ★★★★ | ★★★ |

## Vấn đề Đã Biết

### Gemini 3 Flash: Lỗi Session
Sau ~50 lệnh tool trong cùng session: `400 function_response.name mismatch`. Dùng Gemini **2.0** Flash cho session dài.

### OpenRouter Timeout
Giờ cao điểm (UTC 0:00-06:00) có thể gây timeout. Biện pháp:
- Đặt `timeoutSeconds: 180` (không phải 120)
- Thêm Anthropic trực tiếp làm fallback cuối
- Cron job tự chạy lại lần lịch tiếp theo

### M2.7 Chế độ Reasoning
M2.7 đôi khi trả về `"content": null` chỉ có reasoning token. OpenClaw có thể không parse đúng. Chuỗi fallback xử lý được.

## Ước tính Chi phí

Cho vận hành hàng ngày điển hình:

| Cron Job | Lần/ngày | Token/lần | Model | Chi phí/ngày |
|---|---|---|---|---|
| Bản tin buổi sáng | 1 | ~25K | M2.7 | $0.04 |
| Phân loại email | 2 | ~25K | M2.7 | $0.07 |
| Chuẩn bị họp | 10 | ~5K (đa số: không có họp) | M2.7 | $0.02 |
| Tổng hợp Reddit | 1 | ~100K | M2.7 | $0.15 |
| Review tuần | 0.14 | ~50K | M2.7 | $0.01 |
| Chat tự do | ~10 | ~20K | M2.7 | $0.08 |
| **Tổng cộng** | | | | **~$0.37/ngày ≈ $11/tháng** |

So sánh: Cùng khối lượng công việc trên Haiku 4.5 ≈ $40/tháng.

## Tiếp theo: [Hệ thống Bộ nhớ →](09-memory-system.md)
