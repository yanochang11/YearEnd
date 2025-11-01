import sys
import requests
import qrcode
from io import BytesIO
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings
from app.gsheet_client import GSheetClient

def send_qr_code_emails_mailgun():
    """
    Reads the guest list, generates QR codes, and emails them using the Mailgun API.
    """
    if not all([settings.MAILGUN_API_KEY, settings.MAILGUN_DOMAIN]):
        print("錯誤：尚未設定 MAILGUN_API_KEY 和 MAILGUN_DOMAIN。請檢查您的 .env 檔案。")
        return

    print("正在連接 Google Sheets...")
    try:
        gsheet_client = GSheetClient.from_settings()
        worksheet = gsheet_client.get_worksheet(settings.WORKSHEET_NAME)
    except Exception as e:
        print(f"錯誤：無法連接 Google Sheets。請檢查設定。({e})")
        return

    print("正在讀取賓客名單...")
    all_attendees = worksheet.get_all_records()

    attendees_to_email = [
        attendee for attendee in all_attendees
        if str(attendee.get(settings.COL_EMAIL_SENT_STATUS, 'FALSE')).upper() == 'FALSE'
    ]

    if not attendees_to_email:
        print("所有賓客的報到憑證皆已寄送。")
        return

    print(f"找到 {len(attendees_to_email)} 位賓客需要寄送報到憑證...")

    mailgun_api_url = f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages"
    sent_count = 0

    for attendee in attendees_to_email:
        name = attendee.get(settings.COL_NAME)
        email = attendee.get(settings.COL_EMAIL)
        unique_id = attendee.get(settings.COL_UNIQUE_ID)

        if not all([name, email, unique_id]):
            print(f"警告：賓客資料不完整，跳過此筆記錄：{attendee}")
            continue

        print(f"正在處理 '{name}' ({email})...")

        # --- Generate QR Code in memory ---
        qr_img = qrcode.make(unique_id)
        img_byte_arr = BytesIO()
        qr_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # --- Prepare Email Body ---
        html_body = f"""
        <html><body>
            <p>Hi {name},</p>
            <p>誠摯邀請您參加本次的年度尾牙！</p>
            <p>請於活動當天出示此 QR Code 進行報到與簽退。</p><br>
            <img src="cid:qrcode.png"><br>
            <p>期待您的蒞臨！</p>
        </body></html>
        """

        # --- Send Email via Mailgun API ---
        try:
            response = requests.post(
                mailgun_api_url,
                auth=("api", settings.MAILGUN_API_KEY),
                files=[("inline", ("qrcode.png", img_byte_arr.read(), "image/png"))],
                data={
                    "from": settings.MAILGUN_SENDER_EMAIL,
                    "to": f"{name} <{email}>",
                    "subject": "【尾牙邀請函】您的專屬報到 QR Code",
                    "html": html_body
                }
            )
            response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)

            print(f"  -> Email 寄送成功。")

            # --- Update Google Sheet ---
            uid_col_header = settings.COL_UNIQUE_ID
            status_col_header = settings.COL_EMAIL_SENT_STATUS

            cell = worksheet.find(str(unique_id), in_column=worksheet.find(uid_col_header).col)
            worksheet.update_cell(cell.row, worksheet.find(status_col_header).col, 'TRUE')
            print(f"  -> Google Sheet 狀態更新成功。")

            sent_count += 1
        except requests.exceptions.HTTPError as e:
            print(f"錯誤：Mailgun API 回應錯誤: {e.response.status_code} {e.response.text}")
        except Exception as e:
            print(f"錯誤：寄送 Email 給 {name} ({email}) 時失敗: {e}")

    print(f"\n任務完成。已成功寄送 {sent_count} 封報到憑證。")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    send_qr_code_emails_mailgun()
