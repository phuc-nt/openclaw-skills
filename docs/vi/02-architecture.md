[🇬🇧 English](../02-architecture.md)

[← Trang chủ](index.md) · [Cài đặt](01-installation.md) · [Kiến trúc](02-architecture.md) · [Agent đầu tiên](03-first-agent.md) · [Google](04-google-workspace.md) · [Trình duyệt](05-browser-automation.md) · [Cron](06-cron-jobs.md) · [Multi-Agent](07-multi-agent.md) · [Hồ sơ Agent](11-agent-profiles.md) · [Model](08-model-selection.md) · [Bộ nhớ](09-memory-system.md) · [Vận hành](10-operations.md)


# Tổng quan Kiến trúc

## Cách OpenClaw Hoạt Động

```
┌──────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│ Telegram  │────▶│   Gateway    │────▶│    Agent    │────▶│   LLM    │
│   User    │◀────│ (localhost)  │◀────│  (session)  │◀────│ Provider │
└──────────┘     └──────────────┘     └─────────────┘     └──────────┘
                        │                     │
                        │              ┌──────┴──────┐
                        │              │  Workspace   │
                  ┌─────┴─────┐       │  SOUL.md     │
                  │  Cron     │       │  TOOLS.md    │
                  │  Scheduler│       │  skills/     │
                  └───────────┘       └──────────────┘
```

### Gateway
- HTTP server trên `localhost:18789` (chỉ loopback — không expose ra mạng)
- Chuyển tiếp tin nhắn Telegram đến agent qua mapping account→binding
- Quản lý session, cron scheduler, model fallback
- Chạy dưới dạng macOS LaunchAgent (tự khởi động khi bật máy)

### Agent
- Mỗi agent có workspace riêng biệt tại `~/.openclaw/workspace-<id>/`
- Danh tính được định nghĩa bởi `SOUL.md` (tính cách + quy tắc)
- Công cụ được liệt kê trong `TOOLS.md` (danh mục + cú pháp)
- Tài liệu chi tiết công cụ trong `skills/<name>/SKILL.md`

### Session
- Lịch sử hội thoại lưu trong file `.jsonl`
- Cron job chạy trong **session riêng biệt** (không có chat history)
- Session tự động nén khi gần đạt giới hạn context

## Khái Niệm Chính

### SOUL.md — Danh tính Agent

File quan trọng nhất. Định nghĩa agent của bạn LÀ AI và HÀNH XỬ như thế nào:

```markdown
# Trợ lý Cá nhân

Bạn là trợ lý cá nhân. Bạn giúp xử lý công việc hàng ngày.

## Quy tắc
- Trả lời bằng tiếng Việt
- Luôn xác nhận trước khi gửi email
- Kiểm tra TOOLS.md để biết công cụ khả dụng

## Khả năng
- Quản lý email (Gmail)
- Quản lý lịch
- Theo dõi công việc
```

> **80% chất lượng agent phụ thuộc vào cách viết SOUL.md, không phải model.**

### TOOLS.md — Danh mục Công cụ

Tham chiếu nhanh tất cả công cụ khả dụng:

```markdown
# Công cụ

| Công cụ | Đường dẫn | Mục đích |
|---|---|---|
| gmail | skills/gws-gmail/ | Đọc, tìm kiếm, quản lý email |
| calendar | skills/gws-calendar/ | Xem và tạo sự kiện |

Khi dùng công cụ → đọc SKILL.md của nó trước để biết cú pháp chính xác.
```

### SKILL.md — Tài liệu Chi tiết Công cụ

Tài liệu từng công cụ với tham số, ví dụ, lưu ý:

```markdown
---
name: gws-gmail
version: 1.0.0
description: "Gmail: Gửi, đọc, quản lý email."
---

# Gmail

## Cách dùng
gws gmail <resource> <method> [flags]

## Ví dụ
gws gmail +triage --max 10
gws gmail +send --to user@example.com --subject "Hi" --body "Xin chào"
```

### Bindings — Chuyển tiếp Tin nhắn đến Agent

```json
{
  "channels": {
    "telegram": {
      "accounts": {
        "personal": { "botToken": "..." },
        "memory": { "botToken": "..." }
      }
    }
  },
  "bindings": [
    { "accountId": "personal", "agentId": "personal" },
    { "accountId": "memory", "agentId": "kioku" }
  ]
}
```

Mỗi Telegram bot → một account → một agent. Người dùng nhắn tin cho các bot khác nhau để dùng các agent khác nhau.

## Cấu trúc File

```
~/.openclaw/
├── openclaw.json                    # Cấu hình chính
├── cron/jobs.json                   # Tác vụ đã lên lịch
├── logs/gateway.err.log             # Log lỗi
├── agents/
│   └── <agent-id>/
│       ├── agent/auth-profiles.json # API key (chmod 600)
│       └── sessions/                # Log hội thoại
├── workspace-personal/
│   ├── SOUL.md                      # Danh tính agent
│   ├── TOOLS.md                     # Danh mục công cụ
│   ├── skills/                      # Skill đã cài
│   ├── config/                      # Cấu hình riêng agent
│   └── memory/                      # Trạng thái lưu trữ
└── common-scripts/                  # Script dùng chung (tất cả agent)
    ├── goodreads/
    ├── facebook/
    ├── reddit/
    └── youtube/
```

### Tại sao `common-scripts/`?

Script đặt trong `~/.openclaw/common-scripts/<category>/`, KHÔNG đặt trong workspace agent.
- Tái sử dụng được giữa các agent
- Nhận đường dẫn workspace làm tham số
- Tránh trùng lặp code giữa các agent

## Tiếp theo: [Agent Đầu Tiên →](03-first-agent.md)
