[🇬🇧 English](../../recipes/content-digest.md)

# Công thức: Tổng hợp Nội dung (Reddit + YouTube)

Tự động tổng hợp bài Reddit và video YouTube hàng ngày, dịch và tóm tắt.

## Kiến trúc

```
Cron trigger → Agent chạy script → Script lấy nội dung →
Agent dịch/tóm tắt → Upload lên Google Drive → Gửi tóm tắt Telegram
```

## Tổng hợp Reddit

### Cấu trúc Script

```
~/.openclaw/common-scripts/reddit/
├── digest-workflow.sh           # Điều phối
├── generate-detailed-digest.js  # Lấy + format thành markdown
└── (node_modules qua shared .venv)
```

### Cron Job

```json
{
  "id": "reddit-digest",
  "agentId": "personal",
  "schedule": { "kind": "cron", "expr": "0 10 * * *", "tz": "Asia/Ho_Chi_Minh" },
  "payload": {
    "kind": "agentTurn",
    "message": "Chạy tổng hợp Reddit:\n1. Thực thi: bash ~/.openclaw/common-scripts/reddit/digest-workflow.sh ~/.openclaw/workspace-personal reddit\n2. Đọc markdown đã tạo\n3. Dịch tiêu đề và tóm tắt từng bài\n4. Upload lại lên Google Drive\n5. Gửi Telegram với link Doc + xu hướng nổi bật",
    "timeoutSeconds": 900
  },
  "delivery": { "mode": "announce", "channel": "telegram", "to": "YOUR_ID", "bestEffort": true }
}
```

### Giới hạn Tốc độ
- Reddit API: Dùng skill `reddit-readonly` (không cần xác thực cho nội dung công khai)
- Không scrape quá 5 bài × 10 bình luận mỗi subreddit mỗi lần chạy

## Tổng hợp YouTube

### Pipeline Phụ đề

```
yt-dlp (liệt kê video) → youtube-transcript-api (phụ đề) → MLX Whisper (dự phòng)
```

- Phụ đề miễn phí qua `youtube-transcript-api` (không cần API key)
- Dự phòng: MLX Whisper chạy local trên Apple Silicon (~30-90 giây/video)
- Giới hạn tốc độ: nghỉ 5 giây giữa các lần lấy phụ đề, tối đa 24/session

### Mẹo
- Theo dõi kênh qua RSS — rẻ hơn API
- Cache ID video đã xem trong `memory/seen-videos.txt` để tránh xử lý lại
- Video dài (>30 phút): Dùng phụ đề, đừng cố tóm tắt chỉ từ tiêu đề
