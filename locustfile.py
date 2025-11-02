# locustfile.py
import random
from locust import HttpUser, task, between

# --- 您需要修改的區域 ---

# 1. 準備一個包含所有 "假員工ID" 的列表
# 執行測試前，請確保這些 ID 存在於您的 "壓力測試" Google Sheet 中
# 您可以從 attendees.csv 複製 EmployeeID 欄位的內容來填充此列表
TEST_EMPLOYEE_IDS = ["101", "102", "103"] # 範例 ID，請替換為您測試用的 ID 列表

# 2. 您的 API 端點 (Endpoint)
CHECKIN_ENDPOINT = "/api/check-in"
DASHBOARD_ENDPOINT = "/api/status"

# 3. 您的 API Key (從 .env 取得)
# 最好是為測試環境設定一個專用的 Key
API_KEY = "your_test_api_key_here" # 請替換為您的測試 API Key

# --- 腳本主體 ---

class WebsiteUser(HttpUser):
    # 虛擬使用者在執行任務間會隨機等待 1 到 5 秒
    wait_time = between(1, 5)

    @task(3) # 75% 的權重：模擬報到
    def simulate_checkin(self):
        if not self.environment.runner:
            # 在非測試執行環境下直接返回
            return

        # 使用 self.test_employee_ids 以確保每個 user 有自己的 ID 列表
        if not self.test_employee_ids:
            print("所有測試 ID 已用完")
            return

        # 隨機抽取一個 ID 並從列表中移除，確保不重複報到
        user_id = self.test_employee_ids.pop(random.randint(0, len(self.test_employee_ids) - 1))

        # 模擬前端 JS 發送的請求
        self.client.post(
            CHECKIN_ENDPOINT,
            json={"unique_id": user_id}, # API 預期的 payload key 是 unique_id
            headers={"X-API-Key": API_KEY}
        )

    @task(1) # 25% 的權重：模擬主管查看儀表板
    def view_dashboard(self):
        self.client.get(
            DASHBOARD_ENDPOINT,
            headers={"X-API-Key": API_KEY}
        )

    def on_start(self):
        # 每個虛擬使用者開始時，都複製一份乾淨的 ID 列表
        # 這樣才能在 Web UI 中增加或減少使用者數量時，動態地管理 ID
        self.test_employee_ids = TEST_EMPLOYEE_IDS[:]
