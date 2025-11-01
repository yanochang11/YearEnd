# QR Code 尾牙報到/簽退 API 系統
... (此處內容與前一版本相同) ...

## 💻 本地開發與執行

### 1. 複製專案與安裝依賴
... (此處內容與前一版本相同) ...

### 2. 設定環境變數

將 `.env.example` 複製為 `.env`，並填入您從各大平台取得的金鑰。

**注意：** 如果您是從舊版本升級，可以安全地刪除 `.env` 檔案中所有與 Gmail 相關的變數 (`GMAIL_SENDER`, `GMAIL_APP_PASSWORD`)。

```ini
# ... Google Cloud 相關設定 ...

# --- Mailgun Configuration ---
MAILGUN_API_KEY=key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MAILGUN_DOMAIN=mg.yourcompany.com
MAILGUN_SENDER_EMAIL="[您的公司] 尾牙籌備組 <event@mg.yourcompany.com>"
...
```
... (文件其餘部分保持不變) ...
