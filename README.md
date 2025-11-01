# QR Code 尾牙報到/簽退 API 系統

這是一個專為中小型活動設計的輕量級、易於部署的 QR Code 報到/簽退系統。它使用 FastAPI 作為後端，Google Sheets 作為資料庫，並提供一個純前端的 HTML 掃描器。

## ✨ 功能特色

- **低成本**：完全基於免費服務 (Google Sheets, Render, Netlify)。
- **快速部署**：從設定到上線，流程清晰簡單。
- **事前準備自動化**：提供 Python 腳本，自動初始化資料庫並寄送 QR Code。
- **專業郵件寄送**：整合 Mailgun API，確保 QR Code 郵件穩定送達，避免被視為垃圾郵件。
- **即時狀態儀表板**：提供 API 端點，即時追蹤報到與簽退人數。
- **前後端分離**：可獨立部署後端 API 與前端掃描器。
- **高穩健性**：所有 Google Sheet 欄位名稱、Mailgun API 位址皆可透過環境變數配置，系統更具彈性。

## 🛠️ 技術棧

- **後端**: Python 3.10+, FastAPI
- **資料庫**: Google Sheets (`gspread`)
- **郵件寄送**: Mailgun API (`requests`)
- **QR Code 產生**: `qrcode`
- **前端**: HTML5, JavaScript, `html5-qrcode`
- **測試**: `pytest`, `pytest-mock`
- **後端部署**: Render
- **前端部署**: Netlify / GitHub Pages

---

## 🚀 專案設定指南 (最終流程)

**重要：** 為了確保系統的穩定性並避免 Google API 的配額問題，我們將採用「**由您建立檔案，由程式讀寫**」的最佳實踐模式。

### 步驟 1: 設定 Mailgun (用於寄送 QR Code)

1.  **註冊 Mailgun 帳戶**：前往 [Mailgun](https://www.mailgun.com/) 官網註冊一個免費帳戶。
2.  **新增並驗證您的網域**：
    - 登入後，在左側選單進入 `Sending` > `Domains` > `Add New Domain`。
    - 輸入您擁有的一個網域名稱 (例如 `mg.yourcompany.com`)。**Mailgun 的免費方案需要您使用自己的網域**。
    - Mailgun 會提供數個 DNS 紀錄 (TXT, CNAME, MX)，請您到您的網域供應商 (例如 GoDaddy, Cloudflare) 的後台，完成這些 DNS 設定。
    - 等待幾分鐘到數小時，直到 Mailgun 的儀表板顯示您的網域已成功驗證 (Verified)。
3.  **取得 API Key, Domain Name, 與 API URL**：
    - 在左側選單進入 `Settings` > `API Keys`。
    - 找到您的 **Private API key** (通常以 `key-` 開頭)，並將其複製下來。
    - 您的 **Domain Name** 就是您在第 2 步中驗證的網域。
    - **重要：** 請檢查您的 **API Base URL**。在 API Keys 頁面的頂部，它會顯示您的 URL。
        - 如果您的帳戶在 **美國 (US)**，它會是 `https://api.mailgun.net/v3`
        - 如果您的帳戶在 **歐盟 (EU)**，它會是 `https://api.eu.mailgun.net/v3`

### 步驟 2: 設定 Google Sheets (用於儲存資料)

1.  **手動建立 Google Sheet**：
    -   前往您的個人 [Google Drive](https://drive.google.com/)。
    -   建立一個**全新的、空白的** Google 試算表。
    -   將其命名為 `尾牙報到系統` (或您希望在 `.env` 中設定的任何名稱)。
2.  **取得 GCP 服務帳戶金鑰**：
    - **啟用 API**：前往 [Google Cloud Console API Library](https://console.cloud.google.com/apis/library)，搜尋並啟用 **Google Sheets API** 和 **Google Drive API**。
    - **建立服務帳戶**：前往 [服務帳戶頁面](https://console.cloud.google.com/iam-admin/serviceaccounts)，建立一個服務帳戶並給予 **編輯者 (Editor)** 角色。
    - **產生金鑰**：為該服務帳戶建立一個 **JSON** 格式的金鑰，並下載 `service_account.json` 檔案。
3.  **分享 Google Sheet 給服務帳戶**：
    -   打開您下載的 `service_account.json` 檔案，複製 `client_email` 的值。
    -   回到您在步驟 1 建立的 Google Sheet，點擊右上角的 **共用 (Share)** 按鈕。
    -   將 `client_email` 的值貼上，並確保給予 **編輯者 (Editor)** 權限。

---

## 💻 本地開發與執行

### 1. 複製專案與安裝依賴

```bash
git clone https://github.com/your-repo/qr-code-checkin-system.git
cd qr-code-checkin-system

# 建議使用虛擬環境
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### 2. 設定環境變數

將 `.env.example` 複製為 `.env`，並填入您從各大平台取得的金鑰。

**注意：** 如果您是從舊版本升級，可以安全地刪除 `.env` 檔案中所有與 Gmail 相關的變數。

```ini
# --- Google Cloud ---
# 將 service_account.json 內容轉換為 Base64 字串
# Linux/macOS: base64 -i service_account.json
GOOGLE_SERVICE_ACCOUNT_JSON_BASE64=...

# --- Mailgun Configuration ---
MAILGUN_API_KEY=key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MAILGUN_DOMAIN=mg.yourcompany.com
MAILGUN_SENDER_EMAIL="[您的公司] 尾牙籌備組 <event@mg.yourcompany.com>"
# 根據您 Mailgun 帳戶的區域 (US/EU) 填寫正確的 URL
MAILGUN_API_BASE_URL="https://api.mailgun.net/v3"

# --- API Security & Google Sheet Name ---
API_KEY=my-super-secret-key
# 確保此名稱與您手動建立的 Google Sheet 名稱完全一致
SPREADSHEET_NAME=尾牙報到系統

# --- (可選) Google Sheets 欄位名稱 ---
# 如果您修改了 Google Sheet 中的欄位名稱，請在此處進行對應的更新。
COL_UNIQUE_ID="UniqueID"
...
```

### 3. 執行腳本

```bash
# 步驟 1: 初始化 Google Sheets 資料庫
# 這個腳本會找到您分享給它的檔案，並將 attendees.csv 的資料寫入其中。
python scripts/1_setup_database.py

# 步驟 2: 透過 Mailgun 寄送 QR Code 給賓客
python scripts/2_send_qr_codes.py
```

### 4. 啟動 FastAPI 伺服器 & 開啟前端

```bash
# 啟動後端 API
uvicorn app.main:app --reload

# 在瀏覽器中直接打開 frontend/index.html 檔案即可使用掃描器
```

---

## ☁️ 部署指南

(部署指南與前一版本類似，請確保在 Render 的環境變數中設定所有必要的 `MAILGUN_*` 和 `GOOGLE_*` 變數。)

---

## 🧪 測試指南

若要執行單元測試，請在專案根目錄執行：

```bash
PYTHONPATH=. pytest
```
