[🇬🇧 English](../../recipes/book-tracker.md)

# Công thức: Theo dõi Sách Goodreads

Đánh giá, review, và theo dõi tiến độ đọc qua lệnh Telegram.

## Cách Hoạt Động

```
Người dùng: "Đọc xong Project Hail Mary, 5 sao"
Agent: tìm Goodreads → tìm sách → đánh dấu Đã đọc → đánh giá 5 sao
Agent: "✅ Xong! Đã đánh giá 5⭐ cho Project Hail Mary của Andy Weir"
```

## Thiết lập

1. Cài Playwright + stealth trong shared venv
2. Chạy đăng nhập một lần (mở trình duyệt):
   ```bash
   source ~/.openclaw/common-scripts/.venv/bin/activate
   python3 ~/.openclaw/common-scripts/goodreads/goodreads-writer.py login
   ```
3. Copy skill vào workspace agent:
   ```bash
   cp -r /path/to/goodreads-write ~/.openclaw/workspace-personal/skills/
   cp -r /path/to/goodreads-read ~/.openclaw/workspace-personal/skills/
   ```

## Lệnh Có Sẵn

| Thao tác | Lệnh Script |
|---|---|
| Tìm sách | `python3 goodreads-rss.py search "tên sách"` |
| Xem kệ sách | `python3 goodreads-rss.py shelf USER_ID --shelf currently-reading` |
| Bắt đầu đọc | `goodreads-write.sh start BOOK_ID` |
| Đọc xong | `goodreads-write.sh finish BOOK_ID` |
| Đánh giá | `goodreads-write.sh edit BOOK_ID --stars 5` |
| Viết review | `goodreads-write.sh edit BOOK_ID --review "Sách hay!"` |
| Sửa ngày | `goodreads-write.sh edit BOOK_ID --start-date 2026-01-01 --end-date 2026-02-15` |

## Quy trình Điển hình

```
1. Tìm: python3 goodreads-rss.py search "Project Hail Mary"
   → Trả về book_id: 54493401

2. Đọc xong: goodreads-write.sh finish 54493401
   → Kệ chuyển sang "Read" (đã xác minh qua RSS)

3. Đánh giá + Review: goodreads-write.sh edit 54493401 --stars 5 --review "Sci-fi tuyệt vời"
   → Đã lưu đánh giá và review
```

## Lưu Ý

- **Chuyển hướng trang edit**: Goodreads chuyển `/review/edit/` → `/review/new/` cho review đầu tiên. Script đã xử lý cả hai.
- **Session hết hạn**: Cookie tồn tại hàng tuần/tháng. Nếu thao tác lỗi, chạy lại `login`.
- **Độ trễ xác minh RSS**: Thay đổi kệ sách mất 5-10 phút để hiện trong RSS.
- **DOM thay đổi**: Goodreads cập nhật UI định kỳ. Kiểm tra selector nếu thao tác lỗi.
