[🇬🇧 English](../../recipes/expense-tracker.md)

# Công thức: Theo dõi Chi tiêu

Ghi chi tiêu bằng ngôn ngữ tự nhiên qua tin nhắn Telegram.

## Cách Hoạt Động

```
Người dùng: "chi 150k ăn trưa"
Agent: Phân tích → 150.000 VND, "ăn trưa", danh mục: Ăn uống
Agent: Thêm vào Google Sheets
Agent: "✅ Đã ghi: 150k — Ăn trưa (Ăn uống)"
```

## Thêm vào SOUL.md

```markdown
## Theo dõi Chi tiêu
Khi người dùng đề cập chi tiêu ("chi", "trả", "mua", "tốn"):
1. Phân tích: số tiền, mô tả, danh mục (Ăn uống/Di chuyển/Hóa đơn/Mua sắm/Giải trí/Khác)
2. Thêm vào Google Sheets qua: gws sheets +append
3. Xác nhận bằng tin nhắn ngắn

Danh mục: Ăn uống, Di chuyển, Hóa đơn, Mua sắm, Giải trí, Sức khỏe, Giáo dục, Khác
```

## Thiết lập Google Sheets

Tạo bảng tính "Chi tiêu 2026" với các cột:

| Ngày | Số tiền | Mô tả | Danh mục |
|---|---|---|---|
| 2026-04-03 | 150000 | Ăn trưa | Ăn uống |

Agent tự tạo sheet lần đầu sử dụng nếu chưa có.

## Xử lý Hóa đơn (Bonus)

Với ảnh hóa đơn:

```markdown
## Xử lý Hóa đơn
Khi người dùng gửi ảnh hóa đơn/biên lai:
1. Đọc ảnh bằng vision
2. Trích xuất: ngày, số tiền, đơn vị, loại
3. Thêm vào Sheets + upload bản gốc lên Drive
4. Xác nhận: "✅ Hóa đơn: 800k — Tiền điện (04/2026)"
```

Không cần script mới — dùng vision tích hợp + skill gws có sẵn.

## Tóm tắt Hàng tuần

Thêm vào cron Review tuần:

```
"6. Chi tiêu: gws sheets +read --spreadsheet-id SHEET_ID --range 'Sheet1!A:D'"
```

Agent tính tổng theo danh mục và đưa vào bảng điểm tuần.
