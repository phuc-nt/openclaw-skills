[🇬🇧 English](../index.md)

# OpenClaw Hệ Thống Multi-Agent — Hướng Dẫn Xây Dựng

> Xây dựng hệ thống AI agent cá nhân trên macOS, chạy 24/7, quản lý qua Telegram.

Hướng dẫn này được viết từ kinh nghiệm thực tế xây dựng và vận hành hệ thống multi-agent với OpenClaw trên Mac Mini. Mọi bài học đều từ production — không phải lý thuyết.

## Bạn Sẽ Xây Dựng Gì

Một hệ thống AI agent tự động hóa cuộc sống hàng ngày:

- **Trợ lý Cá nhân** — phân loại email, quản lý lịch, chuẩn bị họp, theo dõi chi tiêu
- **Tổng hợp Nội dung** — tự động tóm tắt Reddit, YouTube, Facebook bằng ngôn ngữ của bạn
- **Agent Bộ nhớ** — bộ não thứ hai ghi nhớ mọi thứ bạn nói
- **Theo dõi Sách** — tự động hóa Goodreads (đánh giá, review, theo dõi tiến độ đọc)
- **Nhật ký Sức khỏe** — check-in hàng ngày với báo cáo hàng tuần

Tất cả điều khiển qua Telegram. Tất cả chạy trên Mac của bạn.

## Cấu Trúc Hướng Dẫn

### Bắt Đầu
1. [Yêu cầu & Cài đặt](01-installation.md) — Phần cứng, phần mềm, agent đầu tiên
2. [Tổng quan Kiến trúc](02-architecture.md) — Cách OpenClaw hoạt động, các khái niệm chính
3. [Agent Đầu Tiên](03-first-agent.md) — SOUL.md, TOOLS.md, thiết lập Telegram bot

### Kỹ Năng Cốt Lõi
4. [Tích hợp Google Workspace](04-google-workspace.md) — Gmail, Calendar, Drive, Sheets, Tasks
5. [Tự động hóa Trình duyệt](05-browser-automation.md) — Playwright cho Goodreads, Facebook
6. [Cron Jobs & Lập lịch](06-cron-jobs.md) — Tự động hóa workflow, gửi kết quả, xử lý lỗi

### Nâng Cao
7. [Thiết kế Multi-Agent](07-multi-agent.md) — Khi nào tách vs gộp agent, routing
8. [Hồ sơ 3 Agent](11-agent-profiles.md) — Chi tiết công cụ, workflow & diagram từng agent
9. [Lựa chọn Model](08-model-selection.md) — Giá cả, benchmark, fallback chain
9. [Hệ thống Bộ nhớ](09-memory-system.md) — Kioku-lite, tìm kiếm tri-hybrid, knowledge graph
10. [Cẩm nang Vận hành](10-operations.md) — Debug, lỗi thường gặp, bảo trì

### Công Thức
11. [Công thức: Bản tin Buổi sáng](recipes/morning-briefing.md)
12. [Công thức: Phân loại Email](recipes/email-triage.md)
13. [Công thức: Tổng hợp Nội dung](recipes/content-digest.md)
14. [Công thức: Theo dõi Sách](recipes/book-tracker.md)
15. [Công thức: Theo dõi Chi tiêu](recipes/expense-tracker.md)

---

## Bắt Đầu Nhanh (5 phút)

```bash
# Cài đặt OpenClaw
brew install openclaw

# Tạo agent đầu tiên
openclaw init

# Khởi động gateway
openclaw gateway start

# Chat với agent trên Telegram!
```

Đọc [Yêu cầu & Cài đặt](01-installation.md) để xem hướng dẫn đầy đủ.

---

Được xây dựng từ hơn 2 tháng sử dụng production hàng ngày. [Đóng góp trên GitHub](https://github.com/phuc-nt/openclaw-skills).
