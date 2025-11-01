# QR Code 尾牙報到/簽退 API 系統 (v2.2 - UX 優化版)

這是一個使用 FastAPI 和 Google Sheets 打造的完整 QR Code 報到/簽退系統，專為中大型活動設計。系統包含後端 API、前端掃描器以及用於資料庫初始化和 QR Code 郵寄的 Python 腳本。

此版本為整合式部署，由 FastAPI 同時提供 API 服務和託管前端靜態檔案 (`index.html`)，簡化了部署流程並解決了瀏覽器因安全限制（CORS）而無法在 `https://` 協議下啟動相機的問題。

## 🚀 核心功能

- **API**：提供賓客簽到 (`/api/check-in`)、簽退 (`/api/check-out`) 及即時狀態查詢 (`/api/status`) 的端點。
- **資料庫**：使用 Google Sheets 作為即時、可協作的資料庫。
- **QR Code 產生與寄送**：自動為每位賓客產生專屬的 `UniqueID`，並透過 Mailgun API 將 QR Code 寄送至賓客信箱。
- **前端掃描器**：一個 `index.html` 頁面，使用 `html5-qrcode` 函式庫調用裝置相機進行掃描，並與後端 API 互動。
- **安全性**：所有 API 端點皆透過 `X-API-Key` 進行保護。

## ✨ 前端介面優化

此版本針對現場掃描人員的使用者體驗進行了多項優化：

- **佈局調整**：將掃描結果置於畫面頂部，方便快速查看；將較少使用的 API Key 輸入框移至底部。
- **行動裝置優化**：禁止了在手機上點擊輸入框時的頁面自動縮放，避免相機畫面跑位。
- **即時視覺回饋**：在掃描成功或失敗時，整個頁面背景會閃爍綠色或紅色，提供強烈的視覺提示。
- **音效回饋**：為成功和失敗的掃描提供不同的音效，方便操作人員在不看螢幕的情況下也能得知結果。
- **顯示桌號**：成功簽到後，會一併顯示賓客的桌號，方便引導。

## 🔧 技術棧

- **後端**: FastAPI, Uvicorn
- **資料庫**: Google Sheets (`gspread`, `google-auth-oauthlib`)
- **QR Code**: `qrcode`
- **郵件服務**: Mailgun API (`requests`)
- **前端**: HTML, JavaScript (`html5-qrcode`)
- **測試**: Pytest, Pytest-mock
- **配置管理**: Pydantic

---

## 📚 前置設定

### 1. Google Cloud Platform (GCP) 與服務帳戶

1.  **啟用 API**:
    *   前往 [Google Cloud Console](https://console.cloud.google.com/)。
    *   建立一個新的專案。
    *   在「API 和服務」儀表板中，啟用 **Google Drive API** 和 **Google Sheets API**。
2.  **建立服務帳戶**:
    *   在「憑證」頁面，點擊「建立憑證」 -> 「服務帳戶」。
    *   為服務帳戶命名，並授予「編輯者」權限。
    *   建立完成後，進入該服務帳戶的「金鑰」分頁，點擊「新增金鑰」 -> 「建立新的金鑰」，選擇 **JSON** 格式並下載金鑰檔案。
3.  **命名與配置**:
    *   將下載的金鑰檔案重新命名為 `service_account.json`，並放置在專案的根目錄。
    *   **重要**: 將此檔案加入 `.gitignore`，絕對不要將金鑰上傳到版本控制系統。

### 2. 建立 Google Sheet

1.  手動建立一個新的 Google Sheet 文件。
2.  點擊右上角的「共用」按鈕。
3.  將服務帳戶的電子郵件地址（可在 `service_account.json` 中找到，格式為 `...@...gserviceaccount.com`）加入共用清單，並給予「編輯者」權限。
4.  **記下這份 Google Sheet 的 ID** (網址中 `d/` 和 `/edit` 之間的部分)。

### 3. 設定環境變數

在專案根目錄建立一個 `.env` 檔案，並填入以下內容：

```env
# Google Sheet
GOOGLE_SHEET_ID="YOUR_GOOGLE_SHEET_ID" # 填入上一步記下的 Sheet ID
SHEET_NAME="賓客名單" # 工作表名稱，可自訂

# API 安全性
API_KEY="YOUR_SUPER_SECRET_API_KEY" # 設定一個高強度的 API 金鑰

# Mailgun 郵件服務
MAILGUN_API_KEY="YOUR_MAILGUN_API_KEY" # Mailgun 的 API 金鑰
MAILGUN_DOMAIN="YOUR_MAILGUN_DOMAIN" # 例如：sandbox123...mailgun.org
MAILGUN_SENDER_EMAIL="Excited User <mailgun@YOUR_MAILGUN_DOMAIN>" # 寄件人 Email
MAILGUN_SENDER_NAME="尾牙籌備小組" # 寄件人名稱

# QR Code Email 內容
EMAIL_SUBJECT="您的尾牙報到 QR Code"
EMAIL_BODY="您好，<br><br>這是您的尾牙報到 QR Code，請於活動當日出示以供掃描。<br><br>祝您有個愉快的夜晚！<br><br>"
```

### 4. 安裝 Python 依賴

```bash
pip install -r requirements.txt
```

---

## 💻 本地開發與執行

### 1. 準備賓客名單

在 `data/` 資料夾中，建立一個 `attendees.csv` 檔案，需包含以下欄位：
`EmployeeID`, `Name`, `Department`, `Email`, `TableNumber`

### 2. 執行初始化與郵寄腳本

```bash
# 步驟 1: 初始化 Google Sheets 資料庫
# 此腳本會讀取 attendees.csv，並將資料寫入您設定的 Google Sheet。
python scripts/1_setup_database.py

# 步驟 2: 透過 Mailgun 寄送 QR Code 給賓客
# 您可以使用 --limit 參數來分批寄送，以符合 Mailgun 的每日用量限制。
# 例如，每天寄送 100 封：
python scripts/2_send_qr_codes.py --limit 100
```

### 3. 啟動整合式伺服器

```bash
uvicorn app.main:app --reload
```

伺服器啟動後：
-   API 文件位於：`http://127.0.0.1:8000/docs`
-   前端掃描器位於：`http://127.0.0.1:8000/`

---

## 🧪 測試

本專案使用 `pytest` 進行測試。測試檔案位於 `tests/` 目錄下。

若要執行測試，請在專案根目錄執行：

```bash
PYTHONPATH=. pytest
```

---

## 🚀 部署 (以 Render 為例)

1.  **將專案推送到 GitHub Repository**。
2.  **在 Render 建立一個新的 Web Service**，並連接到您的 GitHub Repository。
3.  **設定 Build & Start Commands**:
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4.  **設定環境變數**:
    *   前往 Render 儀表板的 "Environment" 頁面。
    *   **新增 Secret File**:
        *   **Filename**: `service_account.json`
        *   **Contents**: 將您本地 `service_account.json` 檔案的**所有內容**複製並貼上。
    *   **新增 Environment Variables**: 將您在 `.env` 檔案中設定的所有鍵值對（如 `GOOGLE_SHEET_ID`, `API_KEY` 等）逐一加入。
5.  **部署**：點擊 "Create Web Service"，Render 將會自動部署您的應用程式。
