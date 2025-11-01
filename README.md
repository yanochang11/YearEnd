# QR Code 尾牙報到/簽退 API 系統

這是一個專為中小型活動設計的輕量級、易於部署的 QR Code 報到/簽退系統。它使用 FastAPI 作為後端，Google Sheets 作為資料庫，並提供一個純前端的 HTML 掃描器。

## ✨ 功能特色
... (此處內容與前一版本相同) ...

## 🚀 專案設定指南
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

    # (強烈建議) 您的個人 Google 帳號 Email
    # 如果設定此項，初始化腳本會自動將建立的 Google Sheet 分享給您，
    # 方便您直接在 Google Drive 中查看和管理，並避免因儲存配額問題導致錯誤。
    GOOGLE_ACCOUNT_EMAIL_TO_SHARE=your-email@gmail.com

    # 您的 Gmail 帳號與 16 位元應用程式密碼
    GMAIL_SENDER=your-email@gmail.com
    GMAIL_APP_PASSWORD=your16charapppassword
    ...
    ```

... (文件其餘部分與前一版本相同) ...

---

## ☁️ 部署指南

### 後端部署 (Render)
... (步驟 1-4 與前一版本相同) ...

5.  點擊 **Advanced Settings**，設定環境變數：
    - **Environment Variables**:
        - `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64`: (您的 Base64 編碼金鑰)
        - **(建議)** `GOOGLE_ACCOUNT_EMAIL_TO_SHARE`: `your-email@gmail.com`
        - `GMAIL_SENDER`: `your-email@gmail.com`
        ...

... (文件其餘部分與前一版本相同) ...
```
