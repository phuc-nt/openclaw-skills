[🇬🇧 English](../../recipes/email-triage.md)

[← Trang chủ](../index.md) · [Cài đặt](../01-installation.md) · [Kiến trúc](../02-architecture.md) · [Agent đầu tiên](../03-first-agent.md) · [Google](../04-google-workspace.md) · [Trình duyệt](../05-browser-automation.md) · [Cron](../06-cron-jobs.md) · [Multi-Agent](../07-multi-agent.md) · [Hồ sơ Agent](../11-agent-profiles.md) · [Model](../08-model-selection.md) · [Bộ nhớ](../09-memory-system.md) · [Vận hành](../10-operations.md)


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
