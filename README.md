# QR Code 尾牙報到/簽退 API 系統 (v2 - 前後端整合版)

這是一個專為中小型活動設計的輕量級、易於部署的 QR Code 報到/簽退系統。它使用 FastAPI 作為後端，Google Sheets 作為資料庫，並且**由 FastAPI 直接提供前端掃描器介面**。

## ✨ 功能特色

- **單體式部署**：後端 API 與前端介面整合在同一個應用程式中，只需啟動一個伺服器，簡化了本地開發與雲端部署的流程。
- **低成本**：完全基於免費服務 (Google Sheets, Render)。
- **專業郵件寄送**：整合 Mailgun API，確保 QR Code 郵件穩定送達。
... (其他特色與前一版本相同) ...

---

## 🚀 專案設定指南
... (Mailgun 與 Google Sheets 的設定指南與前一版本相同) ...

---

## 💻 本地開發與執行 (新流程)

### 1. 複製專案與安裝依賴
... (此處內容與前一版本相同) ...

### 2. 設定環境變數
... (此處內容與前一版本相同) ...

### 3. 執行初始化與郵寄腳本
```bash
# 步驟 1: 初始化 Google Sheets 資料庫
python scripts/1_setup_database.py

# 步驟 2: 透過 Mailgun 寄送 QR Code 給賓客
python scripts/2_send_qr_codes.py
```

### 4. 啟動整合式伺服器

現在，您只需要執行 **一個** 指令來同時啟動後端 API 和前端介面：
```bash
uvicorn app.main:app --reload
```
伺服器啟動後：
- **前端掃描器**：請在瀏覽器中開啟 `http://localhost:8000`
- **API 文件**：您可以在 `http://localhost:8000/docs` 查看 Swagger UI

您不再需要另外啟動 `python -m http.server`。

---

## ☁️ 部署指南 (新流程)

### 後端與前端部署 (Render)

由於前端檔案現在已整合至 FastAPI 應用程式中，我們不再需要 Netlify 或 GitHub Pages。您只需要將整個專案部署到 Render 的一個 Web Service 上即可。

1.  **登入 Render** 並建立一個新的 **Web Service**。
2.  連接您的 GitHub 帳戶並選擇此專案。
3.  設定服務：
    - **Name**: `qr-code-checkin-system` (或您喜歡的名稱)
    - **Environment**: `Python 3`
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4.  在 **Advanced Settings** 中，設定您在 `.env` 中使用的所有環境變數 (例如 `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64`, `MAILGUN_API_KEY` 等)。
5.  點擊 **Create Web Service**。

部署完成後，您可以直接訪問 Render 提供給您的 `onrender.com` 網址，即可看到前端掃描器介面。

---

## 🧪 測試指南
... (此處內容與前一版本相同) ...
