[🇬🇧 English](../03-first-agent.md)

# Agent Đầu Tiên

## Bước 1: Viết SOUL.md

Tạo `~/.openclaw/workspace-personal/SOUL.md`:

```markdown
# Trợ lý Cá nhân

Bạn là trợ lý cá nhân hữu ích.

## Tính cách
- Thân thiện, ngắn gọn
- Trả lời bằng ngôn ngữ của người dùng
- Hỏi lại nếu không chắc

## Khả năng
- Trả lời câu hỏi, tìm kiếm web
- Chạy lệnh terminal
- Quản lý tác vụ và nhắc nhở

## Quy tắc
- Kiểm tra TOOLS.md trước khi dùng công cụ
- Không bao giờ chạy lệnh nguy hiểm mà không xác nhận
- Giữ câu trả lời ngắn gọn và thực tế
```

## Bước 2: Viết TOOLS.md

Tạo `~/.openclaw/workspace-personal/TOOLS.md`:

```markdown
# Công cụ

Chưa cấu hình công cụ bên ngoài. Dùng khả năng tích hợp sẵn:
- `web_search` — Tìm kiếm web
- `web_fetch` — Lấy nội dung URL
- `exec` — Chạy lệnh terminal

Xem thư mục skills/ để biết công cụ có thể cài thêm.
```

## Bước 3: Cấu hình Model

Sửa `~/.openclaw/openclaw.json`:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-haiku-4-5",
        "fallbacks": ["anthropic/claude-sonnet-4-5"]
      }
    },
    "list": [
      {
        "id": "personal",
        "model": {
          "primary": "anthropic/claude-haiku-4-5"
        }
      }
    ]
  }
}
```

### Định dạng Model

**Đúng** (object với primary + fallbacks):
```json
"model": {
  "primary": "anthropic/claude-haiku-4-5",
  "fallbacks": ["anthropic/claude-sonnet-4-5"]
}
```

**Sai** (string — sẽ gây lỗi):
```json
"model": "anthropic/claude-haiku-4-5"
```

## Bước 4: Khởi động lại & Kiểm tra

```bash
eval "$(/opt/homebrew/bin/brew shellenv)" && openclaw gateway restart
```

Nhắn tin cho Telegram bot: "Xin chào, bạn có thể làm gì?"

## Bước 5: Cài Skill Đầu Tiên

Cài đặt skill Google Calendar:

```bash
# Tải từ ClawHub
clawhub install gws-calendar

# Hoặc copy thủ công
cp -r /path/to/gws-calendar ~/.openclaw/workspace-personal/skills/
```

Cập nhật TOOLS.md để tham chiếu skill mới:

```markdown
# Công cụ

| Công cụ | Đường dẫn | Mục đích |
|---|---|---|
| gws-calendar | skills/gws-calendar/ | Xem và quản lý Google Calendar |
```

Cập nhật SOUL.md để đề cập khả năng mới:

```markdown
## Khả năng
- Google Calendar — xem sự kiện, tạo cuộc họp
```

> **Không cần khởi động lại** — OpenClaw tự phát hiện skill mới.

## Gỡ lỗi

### Agent không trả lời?

```bash
# Kiểm tra gateway đang chạy
openclaw status

# Kiểm tra log lỗi (quan trọng nhất!)
tail -20 ~/.openclaw/logs/gateway.err.log

# Kiểm tra log session agent
ls -t ~/.openclaw/agents/personal/sessions/*.jsonl | head -1 | xargs tail -5
```

### Agent trả lời nhưng bỏ qua SOUL.md?

Một số model tốt hơn trong việc tuân theo hướng dẫn nhiều bước. Xếp hạng:

1. **Claude Sonnet/Haiku 4.5+** — tuân theo hướng dẫn xuất sắc
2. **Kimi K2.5** — đọc SKILL.md trước khi thực thi, tốt
3. **Gemini Flash** — khá, có thể bỏ qua chuỗi phức tạp
4. **GLM** — thường bỏ qua SOUL.md hoàn toàn

Nếu agent bỏ qua hướng dẫn, hãy thử model mạnh hơn trước khi viết lại SOUL.md.

## Tiếp theo: [Tích hợp Google Workspace →](04-google-workspace.md)
