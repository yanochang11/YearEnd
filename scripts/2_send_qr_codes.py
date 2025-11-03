import sys
import argparse
import requests
import qrcode
from io import BytesIO
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings
from app.gsheet_client import GSheetClient

def send_qr_code_emails_mailgun(limit: int = None):
    """
    Reads the guest list, generates QR codes, and emails them using the Mailgun API.
    An optional limit can be provided to send emails in batches.
    """
    if not all([settings.MAILGUN_API_KEY, settings.MAILGUN_DOMAIN]):
        print("錯誤：尚未設定 Mailgun。請檢查 .env 檔案。")
        return

    print("正在連接 Google Sheets...")
    try:
        gsheet_client = GSheetClient.from_settings()
        worksheet = gsheet_client.get_worksheet(settings.WORKSHEET_NAME)
    except Exception as e:
        print(f"錯誤：無法連接 Google Sheets。 ({e})")
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

    # Apply the limit if provided
    if limit is not None and limit > 0:
        print(f"找到 {len(attendees_to_email)} 位未寄送的賓客，本次將處理最多 {limit} 位。")
        attendees_to_email = attendees_to_email[:limit]
    else:
        print(f"找到 {len(attendees_to_email)} 位賓客需要寄送報到憑證...")

    mailgun_api_url = f"{settings.MAILGUN_API_BASE_URL.rstrip('/')}/{settings.MAILGUN_DOMAIN}/messages"
    sent_count = 0

    for attendee in attendees_to_email:
        name = attendee.get(settings.COL_NAME)
        email = attendee.get(settings.COL_EMAIL)
        unique_id = attendee.get(settings.COL_UNIQUE_ID)
        table_number = attendee.get(settings.COL_TABLE_NUMBER)

        if not all([name, email, unique_id, table_number]):
            print(f"警告：賓客資料不完整，跳過此筆記錄：{attendee}")
            continue

        print(f"正在處理 '{name}' ({email})...")

        # --- Generate QR Code and send email ---
        try:
            qr_img = qrcode.make(unique_id)
            img_byte_arr = BytesIO()
            qr_img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            html_body = f"""
            <html><body>
                <p>Hi {name},</p>
                <p>這是您的尾牙報到 QR Code。</p>
                <p>您的座位在 <strong>{table_number}</strong> 號桌。</p><br>
                <img src="cid:qrcode.png"><br>
                <p>期待您的蒞臨！</p>
            </body></html>
            """

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
            response.raise_for_status()

            print(f"  -> Email 寄送成功。")

            cell = worksheet.find(str(unique_id), in_column=worksheet.find(settings.COL_UNIQUE_ID).col)
            worksheet.update_cell(cell.row, worksheet.find(settings.COL_EMAIL_SENT_STATUS).col, 'TRUE')
            print(f"  -> Google Sheet 狀態更新成功。")

            sent_count += 1
        except requests.exceptions.HTTPError as e:
            print(f"錯誤：Mailgun API 回應錯誤: {e.response.status_code} {e.response.text}")
        except Exception as e:
            print(f"錯誤：寄送 Email 給 {name} ({email}) 時失敗: {e}")

    print(f"\n任務完成。已成功寄送 {sent_count} 封報到憑證。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send QR code emails to attendees.")
    parser.add_argument("--limit", type=int, help="Limit the number of emails to send in this batch.")
    args = parser.parse_args()

    from dotenv import load_dotenv
    load_dotenv()

    send_qr_code_emails_mailgun(limit=args.limit)
