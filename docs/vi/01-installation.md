[🇬🇧 English](../01-installation.md)

# Yêu cầu & Cài đặt

## Phần cứng

- **Mac Mini M1/M2/M4** (hoặc bất kỳ Mac nào chạy 24/7)
- RAM tối thiểu 8GB, khuyến nghị 16GB+
- Kết nối internet ổn định

## Yêu cầu Phần mềm

| Phần mềm | Mục đích | Cài đặt |
|---|---|---|
| Homebrew | Quản lý package | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| OpenClaw | Framework agent | `brew install openclaw` |
| Node.js 20+ | Runtime cho skills | `brew install node` |
| Python 3.12+ | Script & công cụ | `brew install python@3.12` |
| uv | Cài đặt Python package | `brew install uv` |
| jq | Xử lý JSON | `brew install jq` |

## Tài khoản Cần thiết

| Tài khoản | Mục đích | Chi phí |
|---|---|---|
| **Anthropic API** | Model Claude (chính) | Trả theo dùng (~$5-20/tháng) |
| **Telegram Bot** | Giao diện người dùng | Miễn phí (tạo qua @BotFather) |
| **OpenRouter** (tùy chọn) | Model thay thế (Gemini, Kimi, MiniMax) | Trả theo dùng |

## Bước 1: Cài đặt OpenClaw

```bash
eval "$(/opt/homebrew/bin/brew shellenv)"
brew install openclaw
```

## Bước 2: Khởi tạo

```bash
openclaw init
```

Lệnh này tạo:
```
~/.openclaw/
├── openclaw.json          # Cấu hình chính
├── agents/                # Lưu trữ session agent
├── workspace-personal/    # Workspace agent mặc định
├── cron/jobs.json         # Tác vụ đã lên lịch
└── logs/                  # Log lỗi
```

## Bước 3: Thêm API Key

```bash
# Tạo auth profile cho agent
mkdir -p ~/.openclaw/agents/personal/agent
cat > ~/.openclaw/agents/personal/agent/auth-profiles.json << 'EOF'
{
  "profiles": {
    "default": {
      "provider": "anthropic",
      "apiKey": "sk-ant-KEY_CUA_BAN"
    }
  }
}
EOF
chmod 600 ~/.openclaw/agents/personal/agent/auth-profiles.json
```

> **Bảo mật**: Luôn `chmod 600` các file chứa API key.

## Bước 4: Tạo Telegram Bot

1. Mở Telegram, tìm `@BotFather`
2. Gửi `/newbot`, làm theo hướng dẫn
3. Copy bot token (định dạng: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Thêm vào `~/.openclaw/openclaw.json`:

```json
{
  "channels": {
    "telegram": {
      "accounts": {
        "personal": {
          "botToken": "BOT_TOKEN_CUA_BAN"
        }
      }
    }
  },
  "bindings": [
    {
      "accountId": "personal",
      "agentId": "personal"
    }
  ]
}
```

## Bước 5: Khởi động Gateway

```bash
openclaw gateway start
```

Gateway chạy dưới dạng macOS LaunchAgent — tự khởi động khi bật máy.

## Bước 6: Kiểm tra

```bash
# Kiểm tra trạng thái
openclaw status

# Kiểm tra lỗi
tail ~/.openclaw/logs/gateway.err.log
```

Giờ hãy nhắn tin cho bot trên Telegram — bot sẽ trả lời!

## Lỗi Thường Gặp

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| "No API key found" | Thiếu `auth-profiles.json` | Tạo file theo Bước 3 |
| Bot không trả lời | Gateway chưa chạy | `openclaw gateway restart` |
| "Unknown model" | Cache model cũ | `openclaw gateway restart` |
| Web UI unauthorized | Cần mật khẩu | Kiểm tra `gateway.password` trong config |

## Tiếp theo: [Tổng quan Kiến trúc →](02-architecture.md)
