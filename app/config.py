import base64
import json
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Manages application settings using environment variables.
    Reads from a .env file for local development.
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    # Google Cloud Service Account JSON, base64 encoded
    GOOGLE_SERVICE_ACCOUNT_JSON_BASE64: str = ""

    # API Security Key
    API_KEY: str = "your_default_api_key"

    # Gmail credentials for sending QR codes
    GMAIL_SENDER: str = ""
    GMAIL_APP_PASSWORD: str = ""

    # Google Sheets configuration
    SPREADSHEET_NAME: str = "尾牙報到系統"
    WORKSHEET_NAME: str = "賓客名單"

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
