import base64
import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Manages application settings using environment variables.
    Reads from a .env file for local development.
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Google Cloud
    GOOGLE_SERVICE_ACCOUNT_JSON_BASE64: str = ""
    GOOGLE_ACCOUNT_EMAIL_TO_SHARE: Optional[str] = None

    # API Security
    API_KEY: str = "your_default_api_key"

    # --- Mailgun Configuration ---
    MAILGUN_API_KEY: str = ""
    MAILGUN_DOMAIN: str = ""
    MAILGUN_SENDER_EMAIL: str = "QR Code System <noreply@your-mailgun-domain.com>"
    # Use "https://api.eu.mailgun.net/v3" if your account is in the EU region
    MAILGUN_API_BASE_URL: str = "https://api.mailgun.net/v3"

    # Google Sheets
    SPREADSHEET_NAME: str = "尾牙報到系統"
    WORKSHEET_NAME: str = "賓客名單"

    # --- Google Sheets Column Names ---
    COL_UNIQUE_ID: str = "UniqueID"
    COL_NAME: str = "Name"
    COL_DEPARTMENT: str = "Department"
    COL_EMAIL: str = "Email"
    COL_EMAIL_SENT_STATUS: str = "EmailSentStatus"
    COL_CHECK_IN_STATUS: str = "CheckInStatus"
    COL_CHECK_IN_TIME: str = "CheckInTime"
    COL_CHECK_OUT_STATUS: str = "CheckOutStatus"
    COL_CHECK_OUT_TIME: str = "CheckOutTime"

    @property
    def google_credentials(self) -> dict:
        if not self.GOOGLE_SERVICE_ACCOUNT_JSON_BASE64:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON_BASE64 environment variable not set.")
        decoded_json = base64.b64decode(self.GOOGLE_SERVICE_ACCOUNT_JSON_BASE64)
        return json.loads(decoded_json)

settings = Settings()
