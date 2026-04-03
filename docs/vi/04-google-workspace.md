[🇬🇧 English](../04-google-workspace.md)

# Tích hợp Google Workspace

Kết nối agent với Gmail, Calendar, Drive, Sheets, Docs, và Tasks.

## Thiết lập

### Cài đặt gws CLI

```bash
npm install -g @googleworkspace/cli
```

### Cấu hình OAuth

1. Vào [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project, bật API: Gmail, Calendar, Drive, Sheets, Docs, Tasks
3. Tạo OAuth 2.0 credentials (loại Desktop App)
4. Tải `credentials.json`

```bash
# Xác thực (chạy thủ công — KHÔNG chạy từ agent)
gws auth login
# Mở trình duyệt → cấp quyền → token được lưu
```

### Quan trọng: Publish OAuth lên Production

> **Nếu OAuth consent screen đang ở chế độ "Testing", refresh token hết hạn sau 7 ngày.**

Vào Google Cloud Console → OAuth consent screen → **Publish to Production**.

### Thứ tự ưu tiên Credential (quan trọng!)

CLI `gws` kiểm tra credential theo thứ tự:
1. Biến môi trường `GOOGLE_WORKSPACE_CLI_TOKEN`
2. Biến môi trường `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE`
3. `credentials.enc` mã hóa + OS keyring ← **khuyến nghị**
4. `credentials.json` dạng plain
5. gcloud ADC

**Best practice**: Để `gws auth login` tạo credential mã hóa. KHÔNG đặt biến môi trường trỏ đến file plain.

### Quy tắc Agent: KHÔNG BAO GIỜ `gws auth login`

Agent không thể chạy `gws auth login` — lệnh này khởi động server OAuth localhost và mở trình duyệt, mà agent không có. Quá trình sẽ bị treo.

Thêm vào SOUL.md:
```markdown
## Quy tắc
- KHÔNG BAO GIỜ chạy `gws auth login` — auth đã được cấu hình sẵn
- Nếu gặp lỗi 401, báo người dùng tự sửa auth
```

## Các Thao tác Đã Kiểm chứng (32 tổng cộng)

| Dịch vụ | Thao tác |
|---|---|
| **Gmail** | liệt kê chưa đọc, tìm kiếm, đọc nội dung, gửi, nháp, đánh dấu đã đọc, liệt kê nhãn |
| **Calendar** | liệt kê lịch, liệt kê sự kiện, tạo, sửa, xóa, quickAdd, free/busy |
| **Drive** | liệt kê file, tìm kiếm, upload, xóa, tạo thư mục |
| **Sheets** | tạo, thêm dòng, đọc dữ liệu, xóa |
| **Docs** | tạo, viết text, đọc, xóa |
| **Tasks** | liệt kê danh sách, tạo task, xóa |
| **Slides** | tạo, xóa |

## Mẫu Thường Dùng

### Phân loại Email
```bash
gws gmail +triage --max 20
```

### Lịch Hôm nay
```bash
gws calendar +agenda --today
```

### Upload lên Drive
```bash
gws drive +upload report.md --parent FOLDER_ID --format json
```

### Thêm vào Sheets
```bash
gws sheets +append --spreadsheet-id SHEET_ID --range "Sheet1!A:D" --values '[["2026-04-03", "150000", "Ăn trưa", "Ăn uống"]]'
```

### Cú pháp Helper Command

Tất cả helper command dùng tiền tố `+` với flag `kebab-case`:
```bash
# Đúng
gws gmail +reply --message-id MSG_ID --body "Cảm ơn"

# Sai (thiếu tiền tố +)
gws gmail reply --message-id MSG_ID --body "Cảm ơn"

# Sai (flag camelCase)
gws gmail +reply --messageId MSG_ID --body "Cảm ơn"
```

### Khám phá Lệnh
```bash
gws gmail --help                    # Liệt kê resource & method
gws schema gmail.users.messages.list  # Xem tham số
```

## Cấu trúc SKILL.md

Với mỗi dịch vụ gws, tạo một skill:

```
skills/
├── gws-shared/SKILL.md         # Quy tắc auth, flag chung
├── gws-gmail/SKILL.md          # Lệnh riêng Gmail
├── gws-gmail-send/SKILL.md     # Helper gửi/trả lời
├── gws-gmail-triage/SKILL.md   # Helper phân loại inbox
├── gws-calendar/SKILL.md       # Quản lý lịch
├── gws-calendar-agenda/SKILL.md # Helper xem agenda
├── gws-drive/SKILL.md          # Quản lý file Drive
├── gws-drive-upload/SKILL.md   # Helper upload
├── gws-sheets/SKILL.md         # CRUD Sheets
├── gws-tasks/SKILL.md          # Quản lý task
└── gws-docs/SKILL.md           # Đọc/viết Docs
```

> Chạy `gws generate-skills` để tự động tạo file SKILL.md cho tất cả dịch vụ.

## Lỗi Thường Gặp

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| 401 Unauthorized | Token hết hạn (chế độ Testing) | Publish OAuth lên Production |
| `gws auth login` bị treo | Agent không có trình duyệt | Chạy thủ công trong terminal |
| "unrecognized subcommand" | Tên method sai | Chạy `gws <service> --help` trước |
| Gửi lỗi nhưng đọc được | Thiếu scope | Xác thực lại với đầy đủ scope |

## Tiếp theo: [Tự động hóa Trình duyệt →](05-browser-automation.md)
