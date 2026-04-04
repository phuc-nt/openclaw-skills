[🇬🇧 English](../07-multi-agent.md)

# Thiết kế Multi-Agent

Khi nào dùng một agent vs nhiều, và cách chúng giao tiếp.

## Nguyên tắc: Tách Theo Mối Quan Tâm, Không Theo Tác Vụ

Đừng tạo agent riêng cho mỗi tác vụ. Thay vào đó, tách theo **lĩnh vực quan tâm**:

| Lĩnh vực | Agent | Xử lý gì |
|---|---|---|
| **Cuộc sống của tôi** | `personal` | Email, lịch, task, chi tiêu, sách — mọi thứ về *tôi* |
| **Thế giới bên ngoài** | `research` | Nghiên cứu web, tổng hợp nội dung, Reddit/YouTube/Facebook — mọi thứ từ *internet* |
| **Nội tâm** | `kioku` | Cảm xúc, check-in sức khỏe, ký ức — *tôi cảm thấy thế nào* |

## Khuyến nghị: Kiến trúc 3 Agent

| Agent | Mục đích | Telegram Bot | Model | Skills |
|---|---|---|---|---|
| **personal** | Quản lý cuộc sống hàng ngày | Personal Bot | MiniMax M2.7 | gws-* (15), goodreads, typefully |
| **research** | Nội dung internet & nghiên cứu | Research Bot | MiniMax M2.7 | crawl4ai, reddit, youtube, facebook |
| **kioku** | Bộ nhớ & bạn đồng hành cảm xúc | Kioku Bot | MiniMax M2.7 | kioku-lite CLI |

### Tại Sao 3 Agent?

- **personal** xử lý tác vụ cá nhân khối lượng lớn (email, lịch, chi tiêu)
- **research** xử lý nội dung từ internet (digest, nghiên cứu sâu, phân tích bài viết)
- **kioku** xử lý ngữ cảnh cảm xúc — không nên trộn với agent hướng tác vụ
- Mỗi agent có SOUL.md tập trung → tuân theo hướng dẫn tốt hơn
- Cron job route đến đúng agent theo lĩnh vực

### Lộ trình Phát triển

```
Giai đoạn 1: 1 agent (personal làm mọi thứ)
Giai đoạn 2: 2 agent (tách bộ nhớ → kioku)
Giai đoạn 3: 3 agent (tách nội dung internet → research)  ← hiện tại
```

## Routing Cron Job

Job route đến agent sở hữu lĩnh vực đó:

```json
// Personal agent — cron "cuộc sống của tôi"
morning-briefing → personal (lịch + email + tasks)
email-triage → personal
prep-next-meeting → personal
calendar-conflict → personal
weekly-review → personal

// Research agent — cron "nội dung internet"
reddit-digest → research
youtube-digest → research
fb-group-monitor → research

// Kioku agent — cron "nội tâm"
health-checkin → kioku
```

## Giao tiếp Giữa Agent

Agent chia sẻ công cụ, không chia sẻ cuộc hội thoại:

```bash
# Personal truy vấn bộ nhớ
kioku-lite search "cuộc họp với khách hàng" --limit 5 --entities

# Research lưu phát hiện thú vị
kioku-lite save --content "..." --tags "research,ai"

# Research và kioku KHÔNG truy cập Gmail/Calendar của personal
# (theo thiết kế — tách biệt mối quan tâm)
```

## Routing: Một Bot Một Agent

```json
{
  "bindings": [
    { "accountId": "personal", "agentId": "personal" },
    { "accountId": "research", "agentId": "research" },
    { "accountId": "kioku", "agentId": "kioku" }
  ]
}
```

## Anti-Pattern: Quá Nhiều hoặc Quá Ít

**Đừng** tạo 5+ agent (một cho mỗi tác vụ). Vấn đề: UX khó hiểu, quy tắc trùng lặp, chi phí nhân lên.

**Đừng** nhồi mọi thứ vào 1 agent. Vấn đề: SOUL.md quá lớn, tính cách mâu thuẫn, context window đầy.

**Điểm cân bằng**: 3 agent tách theo lĩnh vực quan tâm.

## Tiếp theo: [Lựa chọn Model →](08-model-selection.md)
