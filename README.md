# QR Code 尾牙報到/簽退 API 系統

這是一個專為中小型活動設計的輕量級、易於部署的 QR Code 報到/簽退系統。它使用 FastAPI 作為後端，Google Sheets 作為資料庫，並提供一個純前端的 HTML 掃描器。

## ✨ 功能特色

- **低成本**：完全基於免費服務 (Google Sheets, Render, Netlify)。
- **快速部署**：從設定到上線，流程清晰簡單。
- **事前準備自動化**：提供 Python 腳本，自動初始化資料庫並寄送 QR Code。
- **即時狀態儀表板**：提供 API 端點，即時追蹤報到與簽退人數。
- **前後端分離**：可獨立部署後端 API 與前端掃描器。

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

您需要一個服務帳戶金鑰 (JSON 格式) 來授權您的應用程式存取 Google Sheets。

1.  **啟用 API**：
    - 前往 [Google Cloud Console API Library](https://console.cloud.google.com/apis/library)。
    - 搜尋並啟用 **Google Drive API** 和 **Google Sheets API**。
2.  **建立服務帳戶**：
    - 前往 [服務帳戶頁面](https://console.cloud.google.com/iam-admin/serviceaccounts)。
    - 點擊 **建立服務帳戶**。
    - 輸入服務帳戶名稱 (例如 `qr-code-checkin-system`)，然後點擊 **建立並繼續**。
    - 在「授予此服務帳戶對專案的存取權」步驟中，選擇 **編輯者 (Editor)** 角色，然後點擊 **完成**。
3.  **產生金鑰**：
    - 找到您剛剛建立的服務帳戶，點擊它。
    - 進入 **金鑰 (KEYS)** 標籤頁。
    - 點擊 **新增金鑰 (ADD KEY)** > **建立新的金鑰 (Create new key)**。
    - 選擇 **JSON** 格式，然後點擊 **建立**。
    - 瀏覽器會自動下載一個 `.json` 檔案 (例如 `your-project-name-12345.json`)。**請妥善保管此檔案，不要上傳到 Git**。

### 2. Google Sheet 分享設定

當您執行 `1_setup_database.py` 腳本後，它會建立一個新的 Google Sheet。您需要將這個 Sheet **分享** 給您的服務帳戶。

1.  打開您下載的 `.json` 金鑰檔案。
2.  找到 `client_email` 欄位的值 (例如 `..._system@..._project.iam.gserviceaccount.com`)。
3.  在 Google Sheet 的右上角，點擊 **共用 (Share)** 按鈕。
4.  將 `client_email` 的值貼上，並確保給予 **編輯者 (Editor)** 權限。

### 3. Gmail 應用程式密碼設定

為了讓 `2_send_qr_codes.py` 腳本能透過您的 Gmail 帳號寄信，您需要設定「應用程式密碼」。

1.  **啟用兩步驟驗證**：前往 [Google 帳戶安全性設定](https://myaccount.google.com/security)，確保您的帳戶已啟用「兩步驟驗證」。
2.  **產生應用程式密碼**：
    - 在同一個安全性頁面，找到並點擊 **應用程式密碼**。
    - 在「選取應用程式」下拉選單中選擇 **郵件 (Mail)**。
    - 在「選取裝置」下拉選單中選擇 **其他 (自訂名稱)**，並輸入 `QRCodeSystem`。
    - 點擊 **產生**。
    - Google 會顯示一個 **16 個字元**的密碼。**請立即將它複製下來**，因為這個畫面關閉後就不會再顯示。

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
    ```

### 3. 執行事前準備腳本

```bash
# 步驟 1: 初始化 Google Sheets 資料庫
python scripts/1_setup_database.py

# 步驟 2: 寄送 QR Code 給賓客
python scripts/2_send_qr_codes.py
```

### 4. 啟動 FastAPI 伺服器

```bash
uvicorn app.main:app --reload
```
API 會在 `http://127.0.0.1:8000` 上運行。

### 5. 開啟前端掃描器

直接在瀏覽器中打開 `frontend/index.html` 檔案。輸入您在 `.env` 中設定的 `API_KEY`，即可開始掃描。

---

## ☁️ 部署指南

### 後端部署 (Render)

1.  **註冊並登入 Render**。
2.  在 Dashboard 點擊 **New +** > **Web Service**。
3.  連接您的 GitHub/GitLab 帳戶，並選擇此專案。
4.  設定服務：
    - **Name**: `qr-code-api` (或您喜歡的名稱)
    - **Root Directory**: `.`
    - **Environment**: `Python 3`
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5.  點擊 **Advanced Settings**，設定環境變數：
    - **Secret Files**:
        - **Filename**: `service_account.json`
        - **Contents**: 貼上您 GCP 金鑰 JSON 檔案的**完整內容**。
        Render 會將它作為一個檔案儲存，但我們在此專案中使用 Base64，因此請看下一個步驟。
    - **Environment Variables**:
        - `PYTHON_VERSION`: `3.10` (或您選擇的版本)
        - `GMAIL_SENDER`: `your-email@gmail.com`
        - `GMAIL_APP_PASSWORD`: (您的應用程式密碼)
        - `API_KEY`: (您自訂的 API Key)
        - `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64`: 在您的本地端執行 `base64 -i service_account.json`，並將輸出的**單行字串**貼到這裡。
6.  點擊 **Create Web Service**。Render 會自動開始部署。

### 前端部署 (Netlify)

1.  **註冊並登入 Netlify**。
2.  將專案的 `frontend/index.html` 中的 `apiUrl` 變數從 `http://127.0.0.1:8000` 改成您在 Render 上部署的 API 網址 (例如 `https://qr-code-api.onrender.com`)。
3.  將您的專案推送到 GitHub。
4.  在 Netlify 選擇 **Add new site** > **Import an existing project**。
5.  連接 GitHub 並選擇您的專案。
6.  部署設定：
    - **Publish directory**: `frontend`
    - **Build command**: (留空)
7.  點擊 **Deploy site**。

---

## 🧪 測試指南

若要執行單元測試，請在專案根目錄執行：

```bash
pytest
```
測試使用 `pytest-mock` 來模擬對 Google Sheets 的呼叫，確保測試的獨立性與速度。
```
