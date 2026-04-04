[🇬🇧 English](../10-operations.md)

[← Trang chủ](index.md) · [Cài đặt](01-installation.md) · [Kiến trúc](02-architecture.md) · [Agent đầu tiên](03-first-agent.md) · [Google](04-google-workspace.md) · [Trình duyệt](05-browser-automation.md) · [Cron](06-cron-jobs.md) · [Multi-Agent](07-multi-agent.md) · [Hồ sơ Agent](11-agent-profiles.md) · [Model](08-model-selection.md) · [Bộ nhớ](09-memory-system.md) · [Vận hành](10-operations.md)


# Cẩm nang Vận hành

Giám sát, gỡ lỗi, và bảo trì hàng ngày.

## Kiểm tra Hàng ngày

```bash
# 1. Gateway đang chạy?
openclaw status

# 2. Có lỗi không?
tail -20 ~/.openclaw/logs/gateway.err.log

# 3. Cron job khỏe không?
cat ~/.openclaw/cron/jobs.json | python3 -c "
import sys,json
for j in json.load(sys.stdin)['jobs']:
    if not j.get('enabled'): continue
    s = j.get('state',{})
    err = s.get('consecutiveErrors',0)
    status = 'FAILING' if err > 0 else 'OK'
    print(f'{status:8s} {j[\"id\"]:30s} errors={err} last={s.get(\"lastRunStatus\",\"never\")}')"
```

## Gỡ lỗi Hành vi Agent

### Đọc Log Session

```bash
# Tìm session mới nhất
SESSION=$(ls -t ~/.openclaw/agents/personal/sessions/*.jsonl | head -1)

# Xem tin nhắn (user + assistant)
cat "$SESSION" | python3 -c "
import sys, json
for line in sys.stdin:
    obj = json.loads(line.strip())
    msg = obj.get('message', {})
    role = msg.get('role','')
    model = msg.get('model','')
    content = msg.get('content','')
    if role == 'assistant' and isinstance(content, list):
        texts = [c.get('text','')[:200] for c in content if c.get('type')=='text']
        tools = [c.get('name','') for c in content if c.get('type')=='toolCall']
        if texts: print(f'[{model}] {texts[0]}')
        if tools: print(f'[TOOLS] {tools}')
    elif role == 'user':
        txt = content[:100] if isinstance(content,str) else str(content)[:100]
        print(f'[USER] {txt}')
"
```

### Xem Kết quả Tool Call

```bash
cat "$SESSION" | python3 -c "
import sys, json
for line in sys.stdin:
    obj = json.loads(line.strip())
    msg = obj.get('message', {})
    if msg.get('role') == 'toolResult':
        name = msg.get('toolName','')
        content = msg.get('content',[])
        for c in (content if isinstance(content,list) else []):
            t = c.get('text','')[:300]
            if t: print(f'[{name}] {t}')
"
```

## Lỗi Thường Gặp & Cách Sửa

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| **LLM request timed out** | Model/provider chậm | Thêm fallback model; tăng `timeoutSeconds` |
| **cron delivery target is missing** | Thiếu `delivery.to` | Thêm Telegram user ID dạng số |
| **Unknown model** | Cache model cũ | `openclaw gateway restart` |
| **No API key found** | Thiếu auth profile | Tạo `auth-profiles.json` |
| **function_response.name mismatch** | Lỗi Gemini 3 Flash sau nhiều tool call | Chuyển sang Gemini 2.0 Flash |
| **Session hết hạn** (Playwright) | Cookie trình duyệt hết hạn | Chạy lại lệnh login thủ công |
| **No such file or directory** (scripts) | PATH không có trong LaunchAgent | Dùng đường dẫn tuyệt đối hoặc `uv tool install` |

## Quản lý Gateway

```bash
# Khởi động
openclaw gateway start

# Khởi động lại (sau khi đổi config — BẮT BUỘC)
eval "$(/opt/homebrew/bin/brew shellenv)" && openclaw gateway restart

# Kiểm tra process cũ bị kẹt
ps aux | grep openclaw-gateway | grep -v grep

# Force kill + khởi động lại
kill -9 $(pgrep -f openclaw-gateway)
openclaw gateway start

# Chạy chẩn đoán
openclaw doctor
openclaw doctor --fix  # Xóa config key không hợp lệ
```

## Chiến lược Backup

Tạo script backup:
1. Ẩn secret từ `openclaw.json` bằng `jq`
2. Copy file workspace (loại trừ session, dữ liệu trình duyệt)
3. Dùng `rsync` (không dùng `cp -r` — sẽ copy cả file credential ẩn)

```bash
# Ẩn secret từ config
jq 'walk(if type == "object" then
  with_entries(select(.key | test("apiKey|botToken|password|KEY|TOKEN|SECRET") | not))
else . end)' ~/.openclaw/openclaw.json > backup/openclaw.json

# Rsync workspace (loại trừ dữ liệu nhạy cảm)
rsync -av --exclude='sessions/' --exclude='memory/' \
  --exclude='*.jsonl' --exclude='.browser-data/' \
  --exclude='credentials*' --exclude='token*' \
  ~/.openclaw/workspace-personal/ backup/workspace-personal/
```

## Dọn dẹp Session

Session cũ tích lũy. Dọn dẹp tự động qua cron:

```json
{
  "id": "session-cleanup",
  "agentId": "personal",
  "schedule": { "kind": "cron", "expr": "0 3 * * *" },
  "payload": {
    "message": "Run: ~/.openclaw/common-scripts/session-mgmt/cleanup-sessions.sh personal 4"
  }
}
```

Giữ lại chỉ 4 session mới nhất cho mỗi agent.

## Checklist Bảo mật

- [ ] `chmod 600 ~/.openclaw/openclaw.json` (chứa API key)
- [ ] `chmod 600 ~/.openclaw/agents/*/agent/auth-profiles.json`
- [ ] OAuth consent screen đã publish lên Production (Google)
- [ ] `.gitignore` bao gồm: `openclaw.json`, `auth-profiles.json`, `credentials*`, `token*`
- [ ] Script backup ẩn tất cả secret trước khi copy
- [ ] Dữ liệu trình duyệt Playwright loại trừ khỏi backup

## Mẹo Hiệu suất

- **Phân bổ cron job**: Đừng lên lịch 5 job cùng phút
- **Dùng model rẻ cho cron**: Job tổng hợp không cần Sonnet — Haiku hoặc M2.7 là đủ
- **Tăng timeout**: Tổng hợp nội dung cần 5-15 phút, không phải mặc định 2 phút
- **Dọn dẹp session**: Ngăn ổ đĩa phình to từ file `.jsonl`
- **Giới hạn tốc độ script**: Nghỉ 5-30 giây giữa các lệnh gọi API bên ngoài
