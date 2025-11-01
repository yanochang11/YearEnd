import sys
import csv
import uuid
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import gspread
from google.oauth2.service_account import Credentials
from app.config import settings

# Define the necessary scopes for the setup script
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"  # Full drive access is needed to create and manage files
]

def setup_database():
    """
    Initializes the Google Sheet database from a local CSV file.
    """
    print("正在連接 Google Sheets...")
    try:
        creds = Credentials.from_service_account_info(
            settings.google_credentials,
            scopes=SCOPES
        )
        client = gspread.authorize(creds)
    except Exception as e:
        print(f"錯誤：無法連接 Google API。請檢查您的 'service_account.json' 設定。 ({e})")
        return

    try:
        print(f"正在建立或開啟試算表：'{settings.SPREADSHEET_NAME}'...")
        spreadsheet = client.open(settings.SPREADSHEET_NAME)
    except gspread.exceptions.SpreadsheetNotFound:
        spreadsheet = client.create(settings.SPREADSHEET_NAME)
        print(f"試算表建立成功！")

    try:
        worksheet = spreadsheet.worksheet(settings.WORKSHEET_NAME)
        print(f"警告：工作表 '{settings.WORKSHEET_NAME}' 已存在，將清空並重新寫入資料。")
        worksheet.clear()
    except gspread.exceptions.WorksheetNotFound:
        print(f"正在建立工作表：'{settings.WORKSHEET_NAME}'...")
        worksheet = spreadsheet.add_worksheet(title=settings.WORKSHEET_NAME, rows="100", cols="20")

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

    # Use column names from settings
    original_headers = list(attendees[0].keys())
    headers = original_headers + [
        settings.COL_UNIQUE_ID,
        settings.COL_EMAIL_SENT_STATUS,
        settings.COL_CHECK_IN_STATUS,
        settings.COL_CHECK_IN_TIME,
        settings.COL_CHECK_OUT_STATUS,
        settings.COL_CHECK_OUT_TIME
    ]

    rows_to_insert = [headers]
    for attendee in attendees:
        row = [attendee.get(h, '') for h in original_headers] + [
            str(uuid.uuid4()),
            'FALSE',
            'FALSE',
            '',
            'FALSE',
            ''
        ]
        rows_to_insert.append(row)

    print(f"正在將 {len(attendees)} 筆資料寫入工作表...")
    worksheet.update('A1', rows_to_insert, value_input_option='USER_ENTERED')

    print("\n資料庫初始化完成！")
    print(f"您現在可以前往以下連結查看您的 Google Sheet：")
    print(spreadsheet.url)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    setup_database()
