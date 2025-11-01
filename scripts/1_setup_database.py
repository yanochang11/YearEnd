import sys
import os
import csv
import uuid
from pathlib import Path

# Add project root to the Python path
# This allows us to import modules from the 'app' directory
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import gspread
from google.oauth2.service_account import Credentials
from app.config import settings

def setup_database():
    """
    Initializes the Google Sheet database from a local CSV file.
    - Creates a new spreadsheet.
    - Creates a worksheet.
    - Writes headers and attendee data.
    - Adds extra columns required for the application.
    """
    print("正在連接 Google Sheets...")
    try:
        creds = Credentials.from_service_account_info(
            settings.google_credentials,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        client = gspread.authorize(creds)
    except Exception as e:
        print(f"錯誤：無法連接 Google API。請檢查您的 'service_account.json' 設定。 ({e})")
        return

    # --- Create Spreadsheet ---
    try:
        print(f"正在建立新的試算表：'{settings.SPREADSHEET_NAME}'...")
        spreadsheet = client.create(settings.SPREADSHEET_NAME)
        print(f"試算表建立成功！分享給您的 Google 帳號以便在瀏覽器中查看...")
        # You can share this sheet with your personal Google account to easily view it
        # spreadsheet.share('your-email@gmail.com', perm_type='user', role='writer')
    except gspread.exceptions.APIError as e:
        if e.response.status_code == 409: # Conflict, spreadsheet already exists
             print(f"警告：試算表 '{settings.SPREADSHEET_NAME}' 已存在，將使用現有的試算表。")
             spreadsheet = client.open(settings.SPREADSHEET_NAME)
        else:
            print(f"錯誤：建立試算表時發生 API 錯誤。({e})")
            return

    # --- Create Worksheet ---
    try:
        # Delete default "Sheet1" if it exists
        if "Sheet1" in [ws.title for ws in spreadsheet.worksheets()]:
             spreadsheet.del_worksheet(spreadsheet.worksheet("Sheet1"))

        print(f"正在建立工作表：'{settings.WORKSHEET_NAME}'...")
        worksheet = spreadsheet.add_worksheet(title=settings.WORKSHEET_NAME, rows="100", cols="20")
    except gspread.exceptions.APIError as e:
        if e.response.status_code == 400 and 'already exists' in str(e):
            print(f"警告：工作表 '{settings.WORKSHEET_NAME}' 已存在，將清空並重新寫入資料。")
            worksheet = spreadsheet.worksheet(settings.WORKSHEET_NAME)
            worksheet.clear()
        else:
            print(f"錯誤：建立工作表時發生 API 錯誤。({e})")
            return

    # --- Read CSV and Prepare Data ---
    csv_path = project_root / 'attendees.csv'
    if not csv_path.exists():
        print(f"錯誤：找不到 'attendees.csv' 檔案於：{csv_path}")
        return

    print("正在讀取 'attendees.csv'...")
    with open(csv_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        attendees = list(reader)

    if not attendees:
        print("警告：'attendees.csv' 為空或格式不正確。")
        return

    # --- Prepare Headers and Rows for Google Sheets ---
    headers = list(attendees[0].keys()) + [
        'UniqueID', 'EmailSentStatus', 'CheckInStatus',
        'CheckInTime', 'CheckOutStatus', 'CheckOutTime'
    ]

    rows_to_insert = [headers]
    for attendee in attendees:
        row = list(attendee.values()) + [
            str(uuid.uuid4()),  # UniqueID
            'FALSE',            # EmailSentStatus
            'FALSE',            # CheckInStatus
            '',                 # CheckInTime
            'FALSE',            # CheckOutStatus
            ''                  # CheckOutTime
        ]
        rows_to_insert.append(row)

    # --- Write to Worksheet ---
    print(f"正在將 {len(attendees)} 筆資料寫入工作表...")
    worksheet.update('A1', rows_to_insert, value_input_option='USER_ENTERED')

    print("\n資料庫初始化完成！")
    print(f"您現在可以前往以下連結查看您的 Google Sheet：")
    print(spreadsheet.url)


if __name__ == "__main__":
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()
    setup_database()
