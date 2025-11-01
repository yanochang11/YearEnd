# QR Code 尾牙報到/簽退 API 系統

這是一個專為中小型活動設計的輕量級、易於部署的 QR Code 報到/簽退系統。它使用 FastAPI 作為後端，Google Sheets 作為資料庫，並提供一個純前端的 HTML 掃描器。

## 🚀 專案設定指南 (新流程)

**重要：** 為了確保系統的穩定性並避免 Google API 的配額問題，我們將採用「**由您建立檔案，由程式讀寫**」的最佳實踐模式。

### 步驟 1: 手動建立 Google Sheet

1.  前往您的個人 [Google Drive](https://drive.google.com/)。
2.  建立一個**全新的、空白的** Google 試算表。
3.  將其命名為 `尾牙報到系統` (或您希望在 `.env` 中設定的任何名稱)。

### 步驟 2: 取得 GCP 服務帳戶金鑰

1.  **啟用 API**：
    - 前往 [Google Cloud Console API Library](https://console.cloud.google.com/apis/library)。
    - 請搜尋並啟用以下兩個 API：
        - **Google Sheets API**
        - **Google Drive API**
2.  **建立服務帳戶**並**產生金鑰** (詳細步驟請參考舊版 README)。
3.  您會下載一個 `service_account.json` 檔案。

### 步驟 3: 分享 Google Sheet 給服務帳戶

1.  打開您剛剛下載的 `service_account.json` 檔案。
2.  複製 `client_email` 欄位的值 (例如 `...gserviceaccount.com`)。
3.  回到您在**步驟 1** 中建立的 Google Sheet。
4.  點擊右上角的 **共用 (Share)** 按鈕。
5.  將 `client_email` 的值貼上，並確保給予 **編輯者 (Editor)** 權限。

### 步驟 4: (可選) 取得 Gmail 應用程式密碼
如果您需要使用 QR Code 郵件寄送功能，請完成此步驟。
... (此處內容與前一版本相同) ...

---

## 💻 本地開發與執行

### 1. 複製專案與安裝依賴
... (此處內容與前一版本相同) ...

### 2. 設定環境變數

1.  將 `.env.example` 複製為 `.env`。
2.  編輯 `.env` 檔案，填入您的 `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64`、`API_KEY` 等資訊。
    - **請確保 `SPREADSHEET_NAME` 的值與您在步驟 1 中建立的檔案名稱完全一致。**
    - `GOOGLE_ACCOUNT_EMAIL_TO_SHARE` 這個變數已不再需要。

### 3. 執行資料庫初始化腳本

現在，您可以安全地執行初始化腳本。它會找到您分享給它的檔案，並將 `attendees.csv` 的資料寫入其中。

```bash
python scripts/1_setup_database.py
```

... (文件其餘部分與新流程保持一致) ...
