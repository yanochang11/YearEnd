# QR Code 尾牙報到/簽退 API 系統 (v2.1 - 桌號顯示功能)

這是一個專為中小型活動設計的輕量級、易於部署的 QR Code 報到/簽退系統。它使用 FastAPI 作為後端，Google Sheets 作為資料庫，並且由 FastAPI 直接提供前端掃描器介面。

## ✨ 功能特色

- **單體式部署**：後端 API 與前端介面整合在同一個應用程式中，只需啟動一個伺服器，簡化了本地開發與雲端部署的流程。
- **顯示桌號**：在來賓成功簽到時，前端介面會即時顯示其對應的桌號，方便現場引導。
- **低成本**：完全基於免費服務 (Google Sheets, Render)。
- **專業郵件寄送**：整合 Mailgun API，確保 QR Code 郵件穩定送達。
- **即時狀態儀表板**：提供 API 端點，即時追蹤報到與簽退人數。
- **高穩健性**：所有 Google Sheet 欄位名稱、Mailgun API 位址皆可透過環境變數配置，系統更具彈性。

## 🛠️ 技術棧

- **後端**: Python 3.10+, FastAPI
- **資料庫**: Google Sheets (`gspread`)
- **郵件寄送**: Mailgun API (`requests`)
- **QR Code 產生**: `qrcode`
- **前端**: HTML5, JavaScript, `html5-qrcode`, Web Audio API
- **測試**: `pytest`, `pytest-mock`
- **部署**: Render

---

## 🚀 專案設定指南

### 步驟 1: 設定 Mailgun (用於寄送 QR Code)

1.  **註冊 Mailgun 帳戶**：前往 [Mailgun](https://www.mailgun.com/) 官網註冊一個免費帳戶。
2.  **新增並驗證您的網域**：
    - 登入後，在左側選單進入 `Sending` > `Domains` > `Add New Domain`。
    - 輸入您擁有的一個網域名稱 (例如 `mg.yourcompany.com`)。
    - Mailgun 會提供數個 DNS 紀錄，請您到您的網域供應商後台完成設定。
3.  **取得 API Key, Domain Name, 與 API URL**：
    - 進入 `Settings` > `API Keys`，複製您的 **Private API key**。
    - 您的 **Domain Name** 就是您驗證的網域。
    - 檢查您的 **API Base URL** (美國區為 `https://api.mailgun.net/v3`，歐盟區為 `https://api.eu.mailgun.net/v3`)。

### 步驟 2: 設定 Google Sheets (用於儲存資料)

1.  **手動建立 Google Sheet**：
    -   前往您的個人 [Google Drive](https://drive.google.com/)，建立一個**全新的、空白的** Google 試算表。
    -   將其命名為 `尾牙報到系統`。
2.  **取得 GCP 服務帳戶金鑰**：
    -   在 [Google Cloud Console](https://console.cloud.google.com/) 中，啟用 **Google Sheets API** 和 **Google Drive API**。
    -   建立一個服務帳戶並給予 **編輯者** 角色。
    -   產生一個 **JSON** 格式的金鑰並下載。
3.  **分享 Google Sheet 給服務帳戶**：
    -   從下載的金鑰檔案中複製 `client_email`。
    -   將您的 Google Sheet **分享**給這個 email，並給予 **編輯者** 權限。

---

## 💻 本地開發與執行

### 1. 準備賓客名單 (`attendees.csv`)

在執行腳本之前，請先編輯 `attendees.csv` 檔案。請確保檔案中包含以下欄位：
- `EmployeeID`
- `Name`
- `Department`
- `Email`
- `TableNumber`

### 2. 設定環境變數 (`.env`)

將 `.env.example` 複製為 `.env`，並填入您的所有金鑰與設定。如果您希望在 Google Sheet 中使用不同的欄位名稱（例如，將 `TableNumber` 改為 `桌號`），您可以在 `.env` 檔案中修改 `COL_TABLE_NUMBER` 的值。

### 3. 執行初始化與郵寄腳本

```bash
# 步驟 1: 初始化 Google Sheets 資料庫
python scripts/1_setup_database.py

# 步驟 2: 透過 Mailgun 寄送 QR Code 給賓客
python scripts/2_send_qr_codes.py
```

### 4. 啟動整合式伺服器

只需要執行 **一個** 指令即可同時啟動後端 API 和前端介面：
```bash
uvicorn app.main:app --reload
```
- **前端掃描器**：請在瀏覽器中開啟 `http://localhost:8000`
- **API 文件**：您可以在 `http://localhost:8000/docs` 查看 Swagger UI

---

## ☁️ 部署指南 (Render)

由於前後端已整合，只需將整個專案部署到 Render 的一個 Web Service 上即可。

1.  建立一個新的 **Web Service**，並連接您的 GitHub 帳戶。
2.  設定服務：
    - **Environment**: `Python 3`
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3.  在 **Environment** 標籤頁中，設定您在 `.env` 中使用的所有環境變數。
4.  點擊 **Create Web Service**。

---

## 🧪 測試指南

若要執行單元測試，請在專案根目錄執行：
```bash
PYTHONPATH=. pytest
```
