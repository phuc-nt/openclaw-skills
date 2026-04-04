[🇬🇧 English](../09-memory-system.md)

[← Trang chủ](index.md) · [Cài đặt](01-installation.md) · [Kiến trúc](02-architecture.md) · [Agent đầu tiên](03-first-agent.md) · [Google](04-google-workspace.md) · [Trình duyệt](05-browser-automation.md) · [Cron](06-cron-jobs.md) · [Multi-Agent](07-multi-agent.md) · [Hồ sơ Agent](11-agent-profiles.md) · [Model](08-model-selection.md) · [Bộ nhớ](09-memory-system.md) · [Vận hành](10-operations.md)


# Hệ thống Bộ nhớ

Cho agent bộ nhớ lâu dài giữa các session bằng Kioku-lite.

## Kioku-lite là gì?

Engine bộ nhớ cá nhân chạy local. Không Docker, không cloud. Lưu trữ ký ức trong SQLite với tìm kiếm tri-hybrid:

1. **BM25** (từ khóa) — khớp chính xác thực thể
2. **Vector** (ngữ nghĩa) — tương đồng khái niệm qua FastEmbed
3. **Knowledge Graph** — duyệt quan hệ

Kết quả được gộp qua Reciprocal Rank Fusion (RRF).

## Cài đặt

```bash
uv tool install "kioku-agent-kit-lite[cli]"
kioku-lite --help
```

## Lệnh Cốt lõi

### Lưu Ký ức
```bash
kioku-lite save --content "Cuộc họp tuyệt vời với team về mục tiêu Q2" \
  --mood happy --tags "work,meeting,planning"
# Trả về: content_hash (dùng cho kg-index)
```

### Đánh chỉ mục Thực thể (Knowledge Graph)
```bash
kioku-lite kg-index <content_hash> \
  --entities "PERSON:TeamLead,LIFE_EVENT:Q2-planning" \
  --relations "SHARED_MOMENT_WITH:TeamLead"
```

### Tìm kiếm Ký ức
```bash
kioku-lite search "lập kế hoạch Q2" --limit 10 --entities
# Luôn truyền --entities để kích hoạt tìm kiếm graph
```

### Truy hồi theo Thực thể
```bash
kioku-lite recall "TeamLead" --hops 2
# Hiện tất cả ký ức liên quan đến thực thể này trong 2 bước nhảy
```

### Xem Dòng thời gian
```bash
kioku-lite timeline --from 2026-03-01 --to 2026-03-31 --limit 20
```

## Loại Thực thể

| Loại | Ví dụ |
|---|---|
| PERSON | TeamLead, Mẹ, KháchHàng-A |
| EMOTION | vui, lo lắng, biết ơn, tự hào |
| LIFE_EVENT | health-checkin, đọc-xong-sách, ra-mắt-dự-án |
| COPING_MECHANISM | chạy bộ, đọc sách, thiền |
| PLACE | Văn phòng, Nhà, Tokyo |

## Loại Quan hệ

| Quan hệ | Ví dụ |
|---|---|
| TRIGGERED_BY | lo lắng TRIGGERED_BY deadline |
| REDUCED_BY | stress REDUCED_BY chạy bộ |
| BROUGHT_JOY | đọc sách BROUGHT_JOY hạnh phúc |
| SHARED_MOMENT_WITH | cuộc họp SHARED_MOMENT_WITH TeamLead |
| HAPPENED_AT | ăn trưa HAPPENED_AT Văn phòng |

## Quy tắc Quan trọng: Không Tóm tắt

Khi lưu ký ức, lưu **đúng nguyên văn người dùng**. Không tóm tắt, diễn giải, hay cắt bớt.

```bash
# Sai — đã tóm tắt
kioku-lite save --content "Người dùng có ngày tốt lành"

# Đúng — nguyên văn
kioku-lite save --content "Hôm nay tuyệt vời! Cuối cùng cũng ship được feature sau 3 tuần debug. Team ăn mừng bằng pizza. Sarah nói đây là PR sạch nhất cô ấy từng review."
```

Với nội dung dài (>300 ký tự), chia thành nhiều lần lưu theo chủ đề.

## Tích hợp với Agent Personal

Trong TOOLS.md của agent personal:

```markdown
## Liên agent: Memory
kioku-lite search "query" --limit 10 --entities
kioku-lite save --content "..." --tags "tag1,tag2" --mood neutral
```

Trường hợp sử dụng:
- **Review tuần**: `kioku-lite search "tuần này" --limit 10` để đưa ký ức vào bảng điểm
- **Đọc sau**: Lưu tóm tắt bài viết với `--tags "read-later,tech"`
- **Nhật ký sức khỏe**: Lưu check-in hàng ngày với `--tags "health,sleep,mood"`

## Vị trí Dữ liệu

```
~/.kioku/users/<user_id>/
├── memory/           # File markdown nguồn
└── data/
    └── kioku_fts.db  # SQLite FTS5 + vector + graph
```

## Tiếp theo: [Cẩm nang Vận hành →](10-operations.md)
