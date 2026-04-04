[🇬🇧 English](../11-agent-profiles.md)

[← Trang chủ](index.md) · [Cài đặt](01-installation.md) · [Kiến trúc](02-architecture.md) · [Agent đầu tiên](03-first-agent.md) · [Google](04-google-workspace.md) · [Trình duyệt](05-browser-automation.md) · [Cron](06-cron-jobs.md) · [Multi-Agent](07-multi-agent.md) · [Hồ sơ Agent](11-agent-profiles.md) · [Model](08-model-selection.md) · [Bộ nhớ](09-memory-system.md) · [Vận hành](10-operations.md)


# Hồ sơ 3 Agent — Chi tiết Công cụ & Workflow

Sau quá trình tối ưu từ 7 agent xuống 3, hệ thống được tổ chức theo **lĩnh vực quan tâm**:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Telegram                                 │
│     ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│     │ Personal │    │ Research │    │  Kioku   │               │
│     │   Bot    │    │   Bot    │    │   Bot    │               │
│     └────┬─────┘    └────┬─────┘    └────┬─────┘               │
│          │               │               │                      │
├──────────┼───────────────┼───────────────┼──────────────────────┤
│          ▼               ▼               ▼                      │
│   ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│   │  PERSONAL  │  │  RESEARCH  │  │   KIOKU    │              │
│   │            │  │            │  │            │              │
│   │ Cuộc sống  │  │ Thế giới   │  │  Nội tâm  │              │
│   │  của tôi   │  │ bên ngoài  │  │           │              │
│   └──────┬─────┘  └──────┬─────┘  └──────┬─────┘              │
│          │               │               │                      │
│   ┌──────┴──────┐  ┌─────┴───────┐  ┌────┴──────┐             │
│   │ gws-* (15)  │  │ crawl4ai    │  │kioku-lite │             │
│   │ goodreads   │  │ reddit      │  │  CLI      │             │
│   │ typefully   │  │ youtube     │  │           │             │
│   │ sheets      │  │ facebook    │  │           │             │
│   └─────────────┘  └─────────────┘  └───────────┘             │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │              OpenClaw Gateway (localhost:18789)          │  │
│   │              Model: MiniMax M2.7 (tất cả agent)         │  │
│   │              Fallback: Gemini Flash → Haiku 4.5          │  │
│   └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Personal Agent — "Cuộc sống của tôi"

### Tổng quan

| Thuộc tính | Giá trị |
|---|---|
| **ID** | `personal` |
| **Bot Telegram** | Personal Bot |
| **Model** | MiniMax M2.7 → Gemini Flash → Haiku 4.5 |
| **Skills** | 19 skills |
| **Cron jobs** | 6 (morning briefing, email triage ×2, prep meeting, calendar conflict, session cleanup) |
| **Vai trò** | Quản lý email, lịch, task, chi tiêu, sách, SNS |

### Công cụ (19 Skills)

```
skills/
├── gws-shared/          # Auth, global flags cho tất cả gws commands
├── gws-gmail/           # Đọc, tìm kiếm email
├── gws-gmail-send/      # Gửi, reply email
├── gws-gmail-triage/    # Tóm tắt inbox
├── gws-calendar/        # Quản lý lịch
├── gws-calendar-agenda/ # Xem agenda
├── gws-calendar-insert/ # Tạo event
├── gws-drive/           # Quản lý Drive
├── gws-drive-upload/    # Upload file
├── gws-sheets/          # CRUD Sheets
├── gws-sheets-append/   # Thêm rows
├── gws-sheets-read/     # Đọc data
├── gws-docs/            # Đọc Docs
├── gws-docs-write/      # Ghi Docs
├── gws-tasks/           # Google Tasks
├── goodreads-read/      # Tìm, xem shelf (RSS)
├── goodreads-write/     # Rate, review, shelve (Playwright)
├── typefully/           # Đăng X/LinkedIn
└── academic-research/   # Tìm papers (OpenAlex)
```

### Workflows & Use Cases

#### Email Triage (cron 9h & 15h)

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│  Cron    │────▶│ gws gmail    │────▶│  Phân loại   │
│ trigger  │     │ +triage --20 │     │  4 nhóm      │
└──────────┘     └──────────────┘     └──────┬───────┘
                                              │
                                    ┌─────────┴─────────┐
                                    │  🚨 Urgent        │
                                    │  📋 Action         │
                                    │  📰 FYI            │
                                    │  🗑 Noise          │
                                    └─────────┬─────────┘
                                              │
                                    ┌─────────▼─────────┐
                                    │  Telegram message  │
                                    └───────────────────┘
```

**Ví dụ Telegram output:**
```
📧 Email Triage — 20 unread
🚨 Urgent: (không có)
📋 Action:
  • Substack — New subscriber
  • SSI — Cập nhật tài khoản
📰 FYI: The Economist, TechCrunch
🗑 Noise: 12 promotional
```

#### Morning Briefing (cron 7h)

```
┌──────────┐
│  Cron 7h │
└────┬─────┘
     │  Chạy song song:
     ├──▶ gws calendar +agenda --today
     ├──▶ gws gmail +triage --max 10
     └──▶ gws tasks list
           │
     ┌─────▼──────┐
     │ Tổng hợp   │──▶ Telegram
     │ 1 message   │
     └────────────┘
```

#### Expense Tracker (ad-hoc Telegram)

```
User: "tiêu 85k cà phê Highland"
  │
  ▼
┌────────────┐     ┌─────────────────┐     ┌──────────┐
│ Parse:     │────▶│ gws sheets      │────▶│ Xác nhận │
│ 85000 VND  │     │ +append          │     │ Telegram │
│ cà phê     │     │ → "Chi tiêu 2026"│     │          │
│ Ăn uống    │     └─────────────────┘     └──────────┘
└────────────┘
```

#### Goodreads (ad-hoc Telegram)

```
User: "đọc xong Project Hail Mary, 5 sao"
  │
  ├──▶ goodreads-read: search → book_id
  ├──▶ goodreads-write: finish BOOK_ID
  ├──▶ goodreads-write: edit --stars 5
  └──▶ Verify RSS → Telegram "✅ Rated 5⭐"
```

#### Calendar Conflict (cron 7:15)

```
gws calendar +agenda --days 7
  │
  ├─ Double-booking? → Telegram cảnh báo
  ├─ >4 meetings/ngày? → Telegram cảnh báo
  ├─ Gap <15 phút? → Telegram cảnh báo
  └─ Sạch → im lặng
```

---

## 2. Research Agent — "Thế giới bên ngoài"

### Tổng quan

| Thuộc tính | Giá trị |
|---|---|
| **ID** | `research` |
| **Bot Telegram** | Research Bot |
| **Model** | MiniMax M2.7 → Gemini Flash → Haiku 4.5 |
| **Skills** | 9 skills + crawl4ai + common-scripts |
| **Cron jobs** | 1 (reddit digest) |
| **Vai trò** | Web research, content digest, viết phản biện |

### Công cụ

```
Tier 1 — Tìm kiếm (built-in):
├── web_search          # Tìm URL, khảo sát rộng

Tier 2 — Đọc Web (Crawl4AI):
├── crawl-web.py        # HTML → Markdown sạch cho LLM
│   ├── markdown <url>  # Đọc 1 trang
│   ├── multi <urls>    # Đọc nhiều trang song song
│   └── extract <url>   # Extract data cấu trúc (CSS/XPath)

Tier 3 — Nguồn chuyên biệt:
├── reddit-readonly/    # Reddit posts, comments, search
├── youtube-ultimate/   # YouTube framework
├── facebook-group/     # Facebook group monitor (Playwright)
├── get-transcript.sh   # YouTube transcript (free API)
├── search-videos.sh    # Tìm video YouTube
├── mlx-whisper-*.sh    # Transcribe local (Apple Silicon)
└── academic-research/  # Papers (OpenAlex)

Tier 4 — Lưu trữ:
├── gws-drive-upload/   # Upload reports lên Drive
├── gws-docs-write/     # Ghi vào Google Docs
└── kioku-lite          # Lưu findings vào memory
```

### Workflows & Use Cases

#### Deep Research (ad-hoc Telegram)

```
User: "Nghiên cứu về X"
  │
  ▼
┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│ web_search   │────▶│ crawl-web.py  │────▶│ Đối chiếu    │
│ 3-5 queries  │     │ markdown URLs │     │ ≥3 nguồn     │
└──────────────┘     └───────┬───────┘     └──────┬───────┘
                             │                     │
                    ┌────────▼────────┐   ┌───────▼────────┐
                    │ reddit-readonly │   │ Tổng hợp báo   │
                    │ (nếu cần)      │   │ cáo tiếng Việt │
                    └────────────────┘   └───────┬────────┘
                                                  │
                                         ┌───────▼────────┐
                                         │ Hỏi Phúc →     │
                                         │ Upload Drive    │
                                         └────────────────┘
```

**Decision tree đọc web:**
```
Cần đọc nội dung?
  ├─ LUÔN thử crawl-web.py trước (Markdown sạch, tiết kiệm token)
  ├─ Fail? → web_fetch fallback
  └─ Nhiều URL? → crawl-web.py multi url1 url2 ...
```

#### Reddit Digest (cron 10h)

```
┌──────────┐     ┌────────────────────┐     ┌──────────────┐
│ Cron 10h │────▶│ digest-workflow.sh │────▶│ Agent đọc    │
│          │     │ → fetch 20 posts   │     │ markdown     │
│          │     │ → tạo markdown     │     │ → dịch VN    │
│          │     │ → upload Drive     │     │ → tóm tắt    │
└──────────┘     └────────────────────┘     └──────┬───────┘
                                                    │
                                           ┌───────▼───────┐
                                           │ Re-upload     │
                                           │ Drive + Tele  │
                                           └───────────────┘
```

**Telegram output:**
```
📰 Reddit Digest — 04/04/2026
📎 Google Doc: [link]
🔥 Top xu hướng:
1. Gemma 4 release — frontier open model
2. MLX vs llama.cpp benchmark M4
📊 Tổng: 20 bài từ 4 subreddits
```

#### Ad-hoc YouTube (nhắn Research Bot)

```
User paste link YouTube
  │
  ▼
┌────────────────┐     ┌──────────────┐     ┌──────────────┐
│get-transcript  │────▶│ Tóm tắt VN   │────▶│ Upload Drive │
│.sh <VIDEO_ID>  │     │ key insights │     │ + Telegram   │
│                │     │ + verdict    │     │              │
│ fallback:      │     └──────────────┘     └──────────────┘
│ MLX Whisper    │
│ (~30-90s local)│
└────────────────┘
```

**Telegram output:**
```
🎬 [Tiêu đề] | 📺 [Kênh] | ⏱ 15:30
📌 Key insights:
1. ...
2. ...
3. ...
💡 Verdict: Đáng xem full
📄 Full notes: [gdoc_link]
```

#### Facebook Group Monitor (cron, hiện disabled)

```
fb-group-monitor.sh scrape "<url>" --limit 10
  │
  ├──▶ Screenshots → Vision analysis
  │     → Extract: tên sách, tác giả, giá, tình trạng
  │
  └──▶ Telegram:
       📚 Nhà Giả Kim — Paulo Coelho
       💰 Pass | Cũ, bìa xanh
       👤 Người đăng: Nguyen Huy Thanh
       🔗 Bài gốc: <link>
```

#### Read Later (ad-hoc Telegram)

```
User: "đọc sau https://..."
  │
  ▼
┌────────────┐     ┌──────────┐     ┌──────────────┐
│crawl-web.py│────▶│ Tóm tắt  │────▶│ kioku-lite   │
│ markdown   │     │ 3-5 điểm │     │ save --tags  │
│            │     │ tiếng VN  │     │ "read-later" │
└────────────┘     └──────────┘     └──────────────┘
```

#### Critical Writing (ad-hoc Telegram)

```
User: "Viết bài phản biện về X"
  │
  ▼
┌──────────┐     ┌───────────┐     ┌──────────────┐
│ Research  │────▶│ Viết bài  │────▶│ Hỏi duyệt   │
│ Tier 1-3 │     │ ~1500 chữ │     │ → Upload     │
│ tools    │     │ I, II, III│     │   Drive      │
└──────────┘     │ + trích dẫn     └──────────────┘
                 └───────────┘
```

---

## 3. Kioku Agent — "Nội tâm"

### Tổng quan

| Thuộc tính | Giá trị |
|---|---|
| **ID** | `kioku` |
| **Bot Telegram** | Kioku Bot |
| **Model** | MiniMax M2.7 → Gemini Flash → Haiku 4.5 |
| **Skills** | 0 (dùng kioku-lite CLI trực tiếp) |
| **Cron jobs** | 1 (health check-in 7:30 sáng) |
| **Vai trò** | Bạn đồng hành cảm xúc, bộ nhớ dài hạn, theo dõi sức khỏe |

### Công cụ

```
kioku-lite CLI:
├── save           # Lưu ký ức (content + mood + tags)
├── kg-index       # Index entities vào Knowledge Graph
├── search         # Tri-hybrid search (BM25 + Vector + KG)
├── recall         # Recall theo entity
├── timeline       # Xem dòng thời gian
├── entities       # Liệt kê entities
└── kg-alias       # Đăng ký alias
```

### Tính cách đặc biệt

```
Kioku KHÔNG phải chatbot hỗ trợ — Kioku là BẠN ĐỒNG HÀNH:

┌────────────────────────────────────────────┐
│  "Anh ơi, nghe mà em thương quá..."       │
│                                            │
│  • Validate cảm xúc TRƯỚC                 │
│  • KHÔNG đưa lời khuyên trừ khi được hỏi  │
│  • Gọi "anh/Phúc", dùng emoji ấm áp      │
│  • Lưu MỌI THỨ — không tóm tắt, giữ      │
│    nguyên văn                              │
│  • Phát hiện pattern sức khỏe tự động     │
└────────────────────────────────────────────┘
```

### Workflows & Use Cases

#### Health Check-in (cron 7:30)

```
┌──────────┐     ┌──────────────────┐     ┌──────────────┐
│ Cron     │────▶│ Gửi Telegram:    │────▶│ User reply   │
│ 7:30 AM  │     │ "🌅 Check-in!    │     │ → kioku-lite │
│          │     │ 1. Ngủ mấy giờ?  │     │   save       │
│          │     │ 2. Tâm trạng?    │     │ → kg-index   │
│          │     │ 3. Tập thể dục?" │     │              │
└──────────┘     └──────────────────┘     └──────┬───────┘
                                                  │
                                         ┌───────▼────────┐
                                         │ Phát hiện       │
                                         │ pattern:        │
                                         │ ngủ ít → ⚠️     │
                                         │ mood thấp → 💛   │
                                         └────────────────┘
```

#### Emotional Companion (ad-hoc Telegram)

```
User: "Mệt quá, làm việc từ sáng"
  │
  ▼
┌──────────────────┐     ┌──────────────┐
│ 1. Validate:     │     │ 3. Save:     │
│ "Nghe mà thương" │     │ kioku-lite   │
│                  │     │ --mood tired │
│ 2. Lắng nghe,   │     │ --tags work  │
│ KHÔNG tư vấn    │     │              │
│ (trừ khi hỏi)  │     │ 4. kg-index  │
└──────────────────┘     │ entities     │
                         └──────────────┘
```

#### Memory Save (ad-hoc Telegram)

```
User: "Nhớ giúp: hôm nay setup xong 3 agent..."
  │
  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ kioku-lite   │────▶│ kg-index     │────▶│ Xác nhận     │
│ save         │     │ entities:    │     │ "Đã lưu! 🧠" │
│ --content    │     │ LIFE_EVENT:  │     │              │
│ --mood proud │     │ agent-optim  │     │              │
│ --tags work  │     │ RELATES_TO:  │     │              │
│              │     │ openclaw     │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

#### Memory Recall (ad-hoc Telegram)

```
User: "Tôi đã nói gì về công việc?"
  │
  ▼
┌──────────────┐     ┌──────────────┐
│ kioku-lite   │────▶│ Tổng hợp     │
│ search       │     │ kết quả      │
│ "công việc"  │     │ → Telegram   │
│ --entities   │     │              │
│ --limit 10   │     │              │
└──────────────┘     └──────────────┘
```

---

## Data Flow Tổng thể

```
                    ┌─────────────────┐
                    │    INTERNET     │
                    │ Reddit, YouTube │
                    │ Facebook, Web   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │    RESEARCH     │
                    │ crawl4ai, reddit│
                    │ youtube, fb     │
                    │                 │
                    │ Output:         │
                    │ • Google Drive  │
                    │ • Telegram      │
                    │ • kioku-lite    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───────┐     │     ┌────────▼────────┐
     │   PERSONAL     │     │     │     KIOKU       │
     │ Gmail,Calendar │     │     │ Memories,Health │
     │ Tasks,Expenses │     │     │ Emotions        │
     │ Books,SNS      │     │     │                 │
     │                │     │     │ Output:         │
     │ Output:        │     │     │ • kioku-lite DB │
     │ • Google Drive │     │     │ • Telegram      │
     │ • Sheets       │     │     └─────────────────┘
     │ • Telegram     │     │
     └────────────────┘     │
                             │
                    ┌────────▼────────┐
                    │   kioku-lite    │
                    │   (shared DB)   │
                    │ Cả 3 agent đều  │
                    │ có thể search   │
                    └─────────────────┘
```

---

## Bảng So sánh

| Khía cạnh | Personal | Research | Kioku |
|---|---|---|---|
| **Lĩnh vực** | Cuộc sống cá nhân | Internet & tri thức | Cảm xúc & ký ức |
| **Giọng** | Nhanh gọn, thực tế | Học thuật, có nguồn | Ấm áp, đồng cảm |
| **Skills** | 19 | 9 + crawl4ai | 0 (CLI) |
| **Cron** | 6 jobs | 1 job | 1 job |
| **Tool chính** | gws CLI | crawl-web.py | kioku-lite |
| **Output** | Sheets, Drive, Telegram | Drive, Telegram, kioku | kioku DB, Telegram |
| **Khi nào dùng** | Email, lịch, chi tiêu, sách | Nghiên cứu, digest, đọc sau | Tâm sự, sức khỏe, ghi nhớ |

## Tiếp theo: [Lựa chọn Model →](08-model-selection.md)
