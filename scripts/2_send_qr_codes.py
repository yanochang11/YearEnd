import sys
import os
import smtplib
import qrcode
from io import BytesIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings
from app.gsheet_client import GSheetClient

def send_qr_code_emails():
    """
    Reads the guest list from Google Sheets, generates QR codes, and emails them.
    - Connects to Google Sheets.
    - Finds attendees with EmailSentStatus = FALSE.
    - Generates a QR code from their UniqueID.
    - Sends a personalized email with the QR code embedded.
    - Updates EmailSentStatus to TRUE upon success.
    """
    print("正在連接 Google Sheets...")
    try:
        gsheet_client = GSheetClient.from_settings()
        worksheet = gsheet_client.get_worksheet(settings.WORKSHEET_NAME)
    except Exception as e:
        print(f"錯誤：無法連接 Google Sheets。請檢查設定。({e})")
        return

    print("正在讀取賓客名單...")
    all_attendees = worksheet.get_all_records()

    # Filter for attendees who have not been sent an email
    attendees_to_email = [
        attendee for attendee in all_attendees
        if str(attendee.get('EmailSentStatus', 'FALSE')).upper() == 'FALSE'
    ]

    if not attendees_to_email:
        print("所有賓客的報到憑證皆已寄送。")
        return

    print(f"找到 {len(attendees_to_email)} 位賓客需要寄送報到憑證...")

    # --- SMTP Server Setup ---
    try:
        print("正在設定 Gmail (SMTP) 伺服器...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(settings.GMAIL_SENDER, settings.GMAIL_APP_PASSWORD)
        print("SMTP 登入成功。")
    except Exception as e:
        print(f"錯誤：無法登入 Gmail SMTP 伺服器。請檢查您的 GMAIL_SENDER 和 GMAIL_APP_PASSWORD 設定。({e})")
        return

    sent_count = 0
    for attendee in attendees_to_email:
        name = attendee.get('Name')
        email = attendee.get('Email')
        unique_id = attendee.get('UniqueID')

        if not all([name, email, unique_id]):
            print(f"警告：賓客資料不完整，跳過此筆記錄：{attendee}")
            continue

        print(f"正在處理 '{name}' ({email})...")

        # --- Generate QR Code in memory ---
        qr_img = qrcode.make(unique_id)
        img_byte_arr = BytesIO()
        qr_img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # --- Create Email ---
        msg = MIMEMultipart()
        msg['From'] = settings.GMAIL_SENDER
        msg['To'] = email
        msg['Subject'] = "【尾牙邀請函】您的專屬報到 QR Code"

        # Email Body
        body = f"""
        <html>
        <body>
            <p>Hi {name},</p>
            <p>誠摯邀請您參加本次的年度尾牙！</p>
            <p>請於活動當天出示此 QR Code 進行報到與簽退。</p>
            <br>
            <img src="cid:qrcode">
            <br>
            <p>期待您的蒞臨！</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        # Attach QR Code Image
        image = MIMEImage(img_byte_arr, name='qrcode.png')
        image.add_header('Content-ID', '<qrcode>')
        msg.attach(image)

        # --- Send Email ---
        try:
            server.sendmail(settings.GMAIL_SENDER, email, msg.as_string())
            print(f"  -> Email 寄送成功。")

            # --- Update Google Sheet ---
            # Find the row of the attendee to update the 'EmailSentStatus'
            cell = worksheet.find(unique_id, in_column=worksheet.find('UniqueID').col)
            worksheet.update_cell(cell.row, worksheet.find('EmailSentStatus').col, 'TRUE')
            print(f"  -> Google Sheet 狀態更新成功。")

            sent_count += 1
        except Exception as e:
            print(f"錯誤：寄送 Email 給 {name} ({email}) 時失敗: {e}")

    server.quit()
    print(f"\n任務完成。已成功寄送 {sent_count} 封報到憑證。")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    send_qr_code_emails()
