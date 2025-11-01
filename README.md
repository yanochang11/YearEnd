# QR Code 尾牙報到/簽退 API 系統

這是一個專為中小型活動設計的輕量級、易於部署的 QR Code 報到/簽退系統。它使用 FastAPI 作為後端，Google Sheets 作為資料庫，並提供一個純前端的 HTML 掃描器。

## ✨ 功能特色

- **低成本**：完全基於免費服務 (Google Sheets, Render, Netlify)。
- **快速部署**：從設定到上線，流程清晰簡單。
- **事前準備自動化**：提供 Python 腳本，自動初始化資料庫並寄送 QR Code。
- **即時狀態儀表板**：提供 API 端點，即時追蹤報到與簽退人數。
- **前後端分離**：可獨立部署後端 API 與前端掃描器。
- **高穩健性**：所有 Google Sheet 欄位名稱皆可透過環境變數配置，避免因手動修改欄位名導致系統故障。

## 🛠️ 技術棧

- **後端**: Python 3.10+, FastAPI
- **資料庫**: Google Sheets (`gspread`)
- **QR Code 產生**: `qrcode`
- **Email 寄送**: `smtplib` (Gmail)
- **前端**: HTML5, JavaScript, `html5-qrcode`
- **測試**: `pytest`, `pytest-mock`
- **後端部署**: Render
- **前端部署**: Netlify / GitHub Pages

---

## 🚀 專案設定指南

在開始之前，您需要完成以下幾個平台的帳號設定。

### 1. Google Cloud Platform (GCP) 設定
... (此處內容與前一版本相同) ...

### 2. Google Sheet 分享設定
... (此處內容與前一版本相同) ...

### 3. Gmail 應用程式密碼設定
... (此處內容與前一版本相同) ...

---

## 💻 本地開發與執行

### 1. 複製專案與安裝依賴
... (此處內容與前一版本相同) ...

### 2. 設定環境變數

1.  將您下載的 GCP 服務帳戶 `.json` 檔案重新命名為 `service_account.json` 並放在專案根目錄。
2.  將 `.env.example` 複製為 `.env`：`cp .env.example .env`
3.  編輯 `.env` 檔案：
    ```ini
    # 將 service_account.json 內容轉換為 Base64 字串
    # Linux/macOS: base64 -i service_account.json
    GOOGLE_SERVICE_ACCOUNT_JSON_BASE64=...

    # 您的 Gmail 帳號與剛剛產生的 16 位元應用程式密碼
    GMAIL_SENDER=your-email@gmail.com
    GMAIL_APP_PASSWORD=your16charapppassword

    # 自訂一個安全的 API Key，用於保護 API 端點
    API_KEY=my-secret-api-key

    # --- (可選) Google Sheets 欄位名稱 ---
    # 如果您修改了 Google Sheet 中的欄位名稱，請在此處進行對應的更新。
    COL_UNIQUE_ID="UniqueID"
    COL_CHECK_IN_STATUS="CheckInStatus"
    # ... 其他欄位 ...
    ```

### 3. 執行事前準備腳本
... (此處內容與前一版本相同) ...

---

## ☁️ 部署指南

### 後端部署 (Render)
... (步驟 1-4 與前一版本相同) ...

5.  點擊 **Advanced Settings**，設定環境變數：
    - **Environment Variables**:
        - `PYTHON_VERSION`: `3.10`
        - `GMAIL_SENDER`: `your-email@gmail.com`
        - `GMAIL_APP_PASSWORD`: (您的應用程式密碼)
        - `API_KEY`: (您自訂的 API Key)
        - `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64`: (您的 Base64 編碼金鑰)
        - **(可選)** `COL_UNIQUE_ID`: `UniqueID`
        - **(可選)** `COL_CHECK_IN_STATUS`: `CheckInStatus`
        - *(... 如果您需要自訂其他欄位名稱，也可以在此處新增 ...)*

6.  點擊 **Create Web Service**。Render 會自動開始部署。

### 前端部署 (Netlify)
... (此處內容與前一版本相同) ...

---

## 🧪 測試指南

若要執行單元測試，請在專案根目錄執行：

```bash
PYTHONPATH=. pytest
```
這個指令會將當前目錄加入 Python 的執行路徑，並執行所有測試。
```
