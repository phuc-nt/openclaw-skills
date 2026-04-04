[🇬🇧 English](../06-cron-jobs.md)

[← Trang chủ](index.md) · [Cài đặt](01-installation.md) · [Kiến trúc](02-architecture.md) · [Agent đầu tiên](03-first-agent.md) · [Google](04-google-workspace.md) · [Trình duyệt](05-browser-automation.md) · [Cron](06-cron-jobs.md) · [Multi-Agent](07-multi-agent.md) · [Hồ sơ Agent](11-agent-profiles.md) · [Model](08-model-selection.md) · [Bộ nhớ](09-memory-system.md) · [Vận hành](10-operations.md)


# Cron Jobs & Lập lịch

Tự động hóa tác vụ định kỳ — bản tin buổi sáng, phân loại email, tổng hợp nội dung.

## Cấu trúc Cron Job

Sửa `~/.openclaw/cron/jobs.json`:

```json
{
  "version": 1,
  "jobs": [
    {
      "id": "morning-briefing",
      "agentId": "personal",
      "name": "Bản tin Buổi sáng - 7h Hàng ngày",
      "enabled": true,
      "schedule": {
        "kind": "cron",
        "expr": "0 7 * * *",
        "tz": "Asia/Ho_Chi_Minh"
      },
      "sessionTarget": "isolated",
      "wakeMode": "now",
      "payload": {
        "kind": "agentTurn",
        "message": "Prompt của bạn ở đây — agent sẽ thực hiện gì",
        "timeoutSeconds": 180
      },
      "delivery": {
        "mode": "announce",
        "channel": "telegram",
        "to": "TELEGRAM_USER_ID_CUA_BAN",
        "bestEffort": true
      }
    }
  ]
}
```

### Các Trường Chính

| Trường | Mô tả |
|---|---|
| `id` | Định danh duy nhất |
| `agentId` | Agent nào chạy job này |
| `schedule.expr` | Biểu thức cron 5 trường tiêu chuẩn |
| `schedule.tz` | Múi giờ (vd: `Asia/Ho_Chi_Minh`, `America/New_York`) |
| `sessionTarget` | `"isolated"` — session mới mỗi lần chạy (khuyến nghị cho cron) |
| `payload.message` | Prompt gửi đến agent |
| `payload.timeoutSeconds` | Thời gian tối đa trước khi hủy |
| `delivery.to` | Telegram user ID **dạng số** (KHÔNG phải username) |
| `delivery.mode` | `"announce"` — gửi kết quả đến Telegram |

### Tìm Telegram User ID

Nhắn tin cho `@userinfobot` trên Telegram — bot sẽ trả lời ID dạng số của bạn.

## Ví dụ: Bản tin Buổi sáng

```json
{
  "id": "morning-briefing",
  "agentId": "personal",
  "name": "Bản tin Buổi sáng - 7h Hàng ngày",
  "enabled": true,
  "schedule": { "kind": "cron", "expr": "0 7 * * *", "tz": "Asia/Ho_Chi_Minh" },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "Tạo bản tin buổi sáng:\n1. gws calendar +agenda --today\n2. gws gmail +triage --max 10\n3. gws tasks tasks list --params '{\"tasklist\": \"@default\"}'\nĐịnh dạng thành tin nhắn Telegram ngắn gọn.",
    "timeoutSeconds": 180
  },
  "delivery": { "mode": "announce", "channel": "telegram", "to": "YOUR_ID", "bestEffort": true }
}
```

## Ví dụ: Kiểm tra Im lặng (Không Thông báo)

Cho job chỉ thông báo khi phát hiện vấn đề:

```json
{
  "payload": {
    "message": "Kiểm tra xung đột lịch trong 7 ngày tới.\nNếu KHÔNG có xung đột → trả lời 'ok' và DỪNG.\nNếu có xung đột → gửi chi tiết qua Telegram."
  }
}
```

Agent tự quyết định có gửi tin nhắn Telegram hay không dựa trên kết quả.

## Chạy Thủ công

```bash
eval "$(/opt/homebrew/bin/brew shellenv)"
openclaw cron run morning-briefing
```

## Lưu Ý Quan Trọng

### 1. Session Riêng biệt Không Có Ngữ cảnh Chat

Cron job chạy trong session mới — chúng không thấy lịch sử chat trước đó. Agent chỉ biết những gì có trong:
- SOUL.md + TOOLS.md (load khi bắt đầu session)
- Payload message của cron

**Hàm ý**: Đưa TẤT CẢ ngữ cảnh vào payload message. Đừng giả định agent nhớ bất cứ điều gì.

### 2. Dùng Telegram ID Dạng Số, Không Phải Username

```json
// Sai — sẽ lỗi
"to": "MyUsername"

// Đúng — user ID dạng số
"to": "1234567890"
```

### 3. Cache Trạng thái Sau Khi Đổi Lịch

Sau khi sửa `schedule.expr`, bạn PHẢI:
1. Reset trạng thái: đặt `"state": {}` trong job
2. Khởi động lại gateway: `openclaw gateway restart`

Nếu không, lịch cũ vẫn được cache.

### 4. Timeout cho Job Phức tạp

Tổng hợp Reddit/YouTube có thể mất 5+ phút. Đặt timeout đủ lớn:

```json
"timeoutSeconds": 900  // 15 phút cho tổng hợp nội dung
```

Timeout mặc định có thể quá ngắn — job bị hủy âm thầm.

### 5. Nhiều Job Xếp hàng

Job chạy tuần tự trong cron lane. Nếu 5 job kích hoạt cùng lúc, job sau phải đợi. Phân bổ lịch:

```
7:00 — Bản tin buổi sáng      → personal
7:15 — Xung đột lịch          → personal
7:30 — Check-in sức khỏe      → kioku
9:00 — Phân loại email        → personal
10:00 — Tổng hợp Reddit       → research
```

**Lưu ý**: Với kiến trúc 3 agent, route cron digest sang agent `research`, tác vụ cá nhân sang `personal`. Job trên agent khác nhau có thể chạy song song.

## Giám sát Cron Job

```bash
# Kiểm tra job nào đang lỗi
cat ~/.openclaw/cron/jobs.json | python3 -c "
import sys,json
for j in json.load(sys.stdin)['jobs']:
    s = j.get('state',{})
    if s.get('consecutiveErrors',0) > 0:
        print(f\"FAILING: {j['id']} — {s.get('lastError','unknown')}\")"

# Kiểm tra log lỗi gateway
tail -20 ~/.openclaw/logs/gateway.err.log

# Kiểm tra session mới nhất của job
ls -t ~/.openclaw/agents/personal/sessions/*.jsonl | head -1
```

## Tiếp theo: [Thiết kế Multi-Agent →](07-multi-agent.md)
