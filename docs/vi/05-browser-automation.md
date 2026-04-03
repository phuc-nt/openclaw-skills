[🇬🇧 English](../05-browser-automation.md)

# Tự động hóa Trình duyệt

Dùng Playwright để tự động hóa các website không có API — Goodreads, Facebook, v.v.

## Thiết lập

```bash
# Tạo venv dùng chung cho tất cả script
python3 -m venv ~/.openclaw/common-scripts/.venv
source ~/.openclaw/common-scripts/.venv/bin/activate
pip install playwright playwright-stealth
playwright install chromium
```

## Chống Phát hiện Bot

Website phát hiện trình duyệt headless. Các biện pháp đối phó thiết yếu:

```python
from playwright.async_api import async_playwright

context = await playwright.chromium.launch_persistent_context(
    user_data_dir="~/.openclaw/common-scripts/<service>/.browser-data",
    headless=True,
    viewport={"width": 1280, "height": 800},
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
               "AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/131.0.0.0 Safari/537.36",
    args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
    ignore_default_args=["--enable-automation"],
)

# Áp dụng stealth plugin
from playwright_stealth import stealth_async
await stealth_async(page)
```

Kỹ thuật chính:
- **Persistent context**: Cookie tồn tại qua nhiều lần chạy (hàng tuần/tháng)
- **Stealth plugin**: Che dấu fingerprint WebDriver
- **User agent thật**: Khớp với phiên bản Chrome hiện tại
- **Tắt cờ automation**: Loại bỏ `--enable-automation`

## Mẫu: Đăng nhập Một lần, Tự động Mãi mãi

```python
# Lần đầu: headless=False, người dùng đăng nhập thủ công
# Sau đó: headless=True, cookie được giữ lại

async def cmd_login():
    context = await create_browser_context(headless=False)  # Hiện trình duyệt
    page = context.pages[0]
    await page.goto("https://service.com/login")
    input("Nhấn Enter sau khi đăng nhập...")  # Đợi người dùng
    await context.close()  # Cookie đã lưu!

async def cmd_action():
    context = await create_browser_context(headless=True)   # Không hiện cửa sổ
    # Cookie tự động load từ persistent context
    page = context.pages[0]
    await page.goto("https://service.com/protected-page")
    # ... thực hiện thao tác
```

## Mẫu: Output JSON cho Tích hợp Agent

Tất cả script tự động hóa nên xuất JSON:

```python
import json, sys

def result_json(success, action, **kwargs):
    data = {"success": success, "action": action, **kwargs}
    print(json.dumps(data, ensure_ascii=False, indent=2))
    sys.exit(0 if success else 1)

# Sử dụng
result_json(True, "rate", book_id="123", stars=5,
            message="Đã đánh giá 5 sao cho 'Project Hail Mary'")
```

Agent đọc output JSON để xác nhận thành công và báo lại người dùng.

## Mẫu: Xác minh qua RSS

Sau thao tác trình duyệt (đổi kệ sách, đánh giá), xác minh qua RSS/API:

```python
def verify_shelf_rss(user_id, book_id, expected_shelf):
    import urllib.request, xml.etree.ElementTree as ET
    url = f"https://www.goodreads.com/review/list_rss/{user_id}?shelf={expected_shelf}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        root = ET.fromstring(r.read().decode("utf-8"))
    for item in root.findall(".//item"):
        if item.findtext("book_id") == str(book_id):
            return True
    return False
```

## Lưu Ý Quan Trọng

### Selector DOM Thay đổi
Website cập nhật HTML thường xuyên. Chiến lược phòng thủ:
- Dùng selector `aria-label` (ổn định hơn CSS class)
- Thêm nhiều selector dự phòng
- Log nội dung trang thực tế khi selector không tìm thấy

### Screenshot Phải Nằm trong Workspace
OpenClaw sandbox giới hạn truy cập file. Screenshot phải lưu vào workspace agent:
```bash
--shots-dir ~/.openclaw/workspace-personal/temp-screenshots
```

### Giới hạn Tốc độ
```python
await page.wait_for_timeout(2000)  # 2 giây giữa các thao tác
```
Đừng spam — Goodreads/Facebook sẽ block bạn.

### Goodreads: Chuyển hướng Trang Edit
Goodreads chuyển hướng `/review/edit/{id}` → `/review/new/{id}` cho sách chưa có review. Chấp nhận cả hai mẫu URL:
```python
is_review_page = "/review/edit" in url or "/review/new" in url
```

## Tiếp theo: [Cron Jobs & Lập lịch →](06-cron-jobs.md)
