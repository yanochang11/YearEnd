# QR Code 尾牙報到/簽退 API 系統

這是一個專為中小型活動設計的輕量級、易於部署的 QR Code 報到/簽退系統。它使用 FastAPI 作為後端，Google Sheets 作為資料庫，並提供一個純前端的 HTML 掃描器。

## 🚀 專案設定指南 (新流程)

### 步驟 1: 設定 Mailgun (用於寄送 QR Code)

**為什麼使用 Mailgun？** 直接使用 Gmail 大量寄信，帳號很容易被封鎖。Mailgun 是專業的郵件服務，能確保您的 QR Code 信件穩定送達。

1.  **註冊 Mailgun 帳戶**：前往 [Mailgun](https://www.mailgun.com/) 官網註冊一個免費帳戶。
2.  **新增並驗證您的網域**：
    - 登入後，在左側選單進入 `Sending` > `Domains` > `Add New Domain`。
    - 輸入您擁有的一個網域名稱 (例如 `mg.yourcompany.com`)。**Mailgun 的免費方案需要您使用自己的網域**。
    - Mailgun 會提供數個 DNS 紀錄 (TXT, CNAME, MX)，請您到您的網域供應商 (例如 GoDaddy, Cloudflare) 的後台，完成這些 DNS 設定。
    - 等待幾分鐘到數小時，直到 Mailgun 的儀表板顯示您的網域已成功驗證 (Verified)。
3.  **取得 API Key 與 Domain Name**：
    - 在左側選單進入 `Settings` > `API Keys`。
    - 找到您的 **Private API key** (通常以 `key-` 開頭)，並將其複製下來。
    - 您的 **Domain Name** 就是您在第 2 步中驗證的網域。

### 步驟 2: 設定 Google Sheets (用於儲存資料)
... (此處內容與前一版本相同，指導使用者手動建立 Sheet 並分享) ...

---

## 💻 本地開發與執行

### 1. 複製專案與安裝依賴
... (此處內容與前一版本相同) ...

### 2. 設定環境變數

將 `.env.example` 複製為 `.env`，並填入您從各大平台取得的金鑰：

```ini
# ... Google Cloud 相關設定 ...

# --- Mailgun Configuration ---
MAILGUN_API_KEY=key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MAILGUN_DOMAIN=mg.yourcompany.com
MAILGUN_SENDER_EMAIL="[您的公司] 尾牙籌備組 <event@mg.yourcompany.com>"

# --- API Security & Google Sheet Name ---
API_KEY=my-super-secret-key
SPREADSHEET_NAME=尾牙報到系統
...
```

### 3. 執行腳本

```bash
# 步驟 1: 初始化 Google Sheets 資料庫
python scripts/1_setup_database.py

# 步驟 2: 透過 Mailgun 寄送 QR Code 給賓客
python scripts/2_send_qr_codes.py
```
... (文件其餘部分保持不變) ...
