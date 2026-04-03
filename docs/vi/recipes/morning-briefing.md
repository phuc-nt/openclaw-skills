[🇬🇧 English](../../recipes/morning-briefing.md)

# Công thức: Bản tin Buổi sáng

Tóm tắt hàng ngày về lịch, email, tác vụ, và sách đang đọc lúc 7 giờ sáng.

## Yêu cầu
- Đã cài skill Google Workspace (calendar, gmail, tasks)
- Skill đọc Goodreads (tùy chọn)

## Thêm vào SOUL.md

```markdown
## Bản tin Buổi sáng
Khi được kích hoạt bởi cron, thu thập và tóm tắt:
1. Sự kiện lịch hôm nay
2. Email quan trọng chưa đọc
3. Tác vụ đang chờ
4. Sách đang đọc (tùy chọn)
```

## Cron Job

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
    "message": "Tạo bản tin buổi sáng. Chạy các lệnh sau và tóm tắt:\n\n1. gws calendar +agenda --today\n2. gws gmail +triage --max 10\n3. gws tasks tasks list --params '{\"tasklist\": \"@default\", \"showCompleted\": false}'\n\nĐịnh dạng thành tin nhắn ngắn gọn với emoji làm tiêu đề mục. Nếu mục nào trống, ghi ngắn.",
    "timeoutSeconds": 180
  },
  "delivery": { "mode": "announce", "channel": "telegram", "to": "YOUR_ID", "bestEffort": true }
}
```

## Kết quả Mẫu

```
☀️ Bản tin Buổi sáng — Thứ 5 03/04

📅 Lịch:
  • 10:00 — Standup team
  • 14:00 — Review với khách

📧 Email (3 chưa đọc):
  • sếp@work.com — Báo cáo Q1 (khẩn)
  • newsletter@tech.com — Bản tin tuần

✅ Tác vụ:
  • Deploy staging (hạn hôm nay)
  • Review PR #42
```

## Mẹo
- Tăng timeout lên 180 giây nếu bị timeout
- Agent gọi tool song song — nhanh hơn tuần tự
