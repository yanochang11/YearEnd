import base64
import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Manages application settings using environment variables.
    Reads from a .env file for local development.
    """
    # Configure Pydantic to ignore extra fields from the environment
    # This prevents errors if old variables (like GMAIL_*) are still in the .env file
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Google Cloud Service Account JSON, base64 encoded
    GOOGLE_SERVICE_ACCOUNT_JSON_BASE64: str = ""

    # (Optional) Personal Google account to share the created sheet with
    GOOGLE_ACCOUNT_EMAIL_TO_SHARE: Optional[str] = None

    # API Security Key
    API_KEY: str = "your_default_api_key"

    # --- Mailgun Configuration ---
    MAILGUN_API_KEY: str = ""
    MAILGUN_DOMAIN: str = ""
    MAILGUN_SENDER_EMAIL: str = "QR Code System <noreply@your-mailgun-domain.com>"

    # Google Sheets configuration
    SPREADSHEET_NAME: str = "尾牙報到系統"
    WORKSHEET_NAME: str = "賓客名單"

    # --- Google Sheets Column Names (for robustness) ---
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
        """
        Decodes the base64 encoded Google service account JSON.
        Raises ValueError if the environment variable is not set.
        """
        if not self.GOOGLE_SERVICE_ACCOUNT_JSON_BASE64:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON_BASE64 environment variable not set.")

        decoded_json = base64.b64decode(self.GOOGLE_SERVICE_ACCOUNT_JSON_BASE64)
        return json.loads(decoded_json)

# Create a single instance of the settings to be used throughout the application
settings = Settings()
