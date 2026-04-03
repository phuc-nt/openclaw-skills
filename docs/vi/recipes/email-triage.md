[🇬🇧 English](../../recipes/email-triage.md)

# Công thức: Phân loại Email

Phân loại email chưa đọc thành Khẩn cấp / Cần xử lý / Thông tin / Rác, hai lần mỗi ngày.

## Cron Job

```json
{
  "id": "email-triage",
  "agentId": "personal",
  "name": "Phân loại Email - 9h & 15h",
  "enabled": true,
  "schedule": { "kind": "cron", "expr": "0 9,15 * * *", "tz": "Asia/Ho_Chi_Minh" },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "Phân loại email chưa đọc. Chạy:\n\n1. gws gmail +triage --max 20\n\nPhân loại mỗi email thành:\n- 🚨 Khẩn cấp: cần trả lời hôm nay\n- 📋 Cần xử lý: cần xử lý, không gấp\n- 📰 Thông tin: bản tin, thông báo\n- 🗑 Rác: spam, quảng cáo không liên quan\n\nĐịnh dạng thành tin nhắn Telegram. Khẩn cấp lên trước. Nếu inbox trống: gửi '📧 Inbox sạch!'",
    "timeoutSeconds": 180
  },
  "delivery": { "mode": "announce", "channel": "telegram", "to": "YOUR_ID", "bestEffort": true }
}
```
