# QR Code 尾牙報到/簽退 API 系統

這是一個專為中小型活動設計的輕量級、易於部署的 QR Code 報到/簽退系統。它使用 FastAPI 作為後端，Google Sheets 作為資料庫，並提供一個純前端的 HTML 掃描器。

## ✨ 功能特色
... (此處內容與前一版本相同) ...

## 🚀 專案設定指南

在開始之前，您需要完成以下幾個平台的帳號設定。

### 1. Google Cloud Platform (GCP) 設定

您需要一個服務帳戶金鑰 (JSON 格式) 來授權您的應用程式存取 Google Sheets。

1.  **啟用 API**：
    - 前往 [Google Cloud Console API Library](https://console.cloud.google.com/apis/library)。
    - **重要：** 請搜尋並啟用以下兩個 API：
        - **Google Sheets API**
        - **Google Drive API** (這是 `gspread` 函式庫用來按名稱尋找和建立試算表所必需的)
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
    - 瀏覽器會自動下載一個 `.json` 檔案。**請妥善保管此檔案，不要上傳到 Git**。

... (文件其餘部分與前一版本相同) ...
