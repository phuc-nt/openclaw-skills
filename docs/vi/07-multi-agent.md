[🇬🇧 English](../07-multi-agent.md)

# Thiết kế Multi-Agent

Khi nào dùng một agent vs nhiều, và cách chúng giao tiếp.

## Nguyên tắc: Bắt Đầu Với Một, Tách Khi Cần

**Bắt đầu**: Một agent `personal` làm mọi thứ.

**Tách khi**:
- Agent có tính cách mâu thuẫn (trợ lý vs bạn tâm sự)
- Context window đầy (quá nhiều skill được load)
- Cần model khác nhau (rẻ cho tổng hợp, thông minh cho bộ nhớ)
- Bạn muốn bot Telegram riêng cho mục đích khác nhau

## Khuyến nghị: Kiến trúc 2 Agent

| Agent | Mục đích | Telegram Bot | Model |
|---|---|---|---|
| **personal** | Công việc hàng ngày, tự động hóa, tổng hợp | Bot A | Nhanh + rẻ (MiniMax M2.7, Gemini Flash) |
| **memory** | Bộ não thứ hai, nhật ký cảm xúc, sức khỏe | Bot B | Thông minh + đồng cảm (Claude Haiku) |

### Tại Sao Hiệu Quả

- **personal** xử lý tác vụ khối lượng lớn, rủi ro thấp (phân loại email, lịch, tổng hợp)
- **memory** xử lý tác vụ ít nhưng quan trọng (ký ức, suy ngẫm)
- Cron job dùng **session riêng biệt** → không ảnh hưởng ngữ cảnh chat
- Giao tiếp giữa agent qua CLI: personal gọi `kioku-lite search` khi cần

## Giao tiếp Giữa Agent

Agent không nói chuyện trực tiếp. Thay vào đó, chúng dùng chung công cụ:

```bash
# Agent personal truy vấn dữ liệu agent memory
kioku-lite search "cuộc họp với khách hàng" --limit 5 --entities

# Agent memory không truy cập Gmail/Calendar của personal
# (theo thiết kế — tách biệt mối quan tâm)
```

Trong SOUL.md của agent personal:
```markdown
## Liên agent: Memory (kioku-lite)
Khi cần ngữ cảnh quá khứ, truy vấn:
kioku-lite search "query" --limit 10 --entities
```

## Routing: Một Bot Một Agent

```json
{
  "channels": {
    "telegram": {
      "accounts": {
        "assistant": { "botToken": "BOT_A_TOKEN" },
        "memory": { "botToken": "BOT_B_TOKEN" }
      }
    }
  },
  "bindings": [
    { "accountId": "assistant", "agentId": "personal" },
    { "accountId": "memory", "agentId": "kioku" }
  ]
}
```

Người dùng nhắn Bot A → agent personal. Nhắn Bot B → agent memory.

## Cron Job: Tất cả trên Personal

Ngay cả job tổng hợp (Reddit, YouTube) cũng chạy trên agent `personal` — chúng dùng session riêng biệt nên không ảnh hưởng chat. Chỉ `health-checkin` chạy trên agent memory (cần ngữ cảnh cảm xúc).

```json
// Tất cả đi đến agent personal
morning-briefing → personal (isolated)
email-triage → personal (isolated)
reddit-digest → personal (isolated)
weekly-review → personal (isolated)

// Cái này đi đến agent memory
health-checkin → kioku (isolated)
```

## Anti-Pattern: Quá Nhiều Agent

**Đừng** tạo agent riêng cho: email, lịch, sách, reddit, youtube.

Vấn đề:
- 5+ bot Telegram = UX khó hiểu
- Quy tắc SOUL.md trùng lặp giữa các agent
- Chi phí model nhân lên (mỗi agent load đầy đủ context)
- Quản lý cron job trở nên phức tạp

**Thay vào đó**: Một agent personal với nhiều skill, dùng cron session riêng biệt.

## Tiếp theo: [Lựa chọn Model →](08-model-selection.md)
