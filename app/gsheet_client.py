import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, Optional, Any, Callable
from datetime import datetime, timezone
import time
import random
from functools import wraps

from .config import settings

# --- Retry Logic ---
def retry_with_backoff(retries=5, backoff_in_seconds=1):
    def rwb(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return f(*args, **kwargs)
                except gspread.exceptions.APIError as e:
                    if e.response.status_code == 429: # Rate limit exceeded
                        attempts += 1
                        if attempts >= retries:
                            raise e

                        sleep_time = (backoff_in_seconds * 2 ** attempts + random.uniform(0, 1))
                        print(f"Rate limit exceeded. Retrying in {sleep_time:.2f} seconds...")
                        time.sleep(sleep_time)
                    else:
                        raise e # Re-raise other API errors immediately
            raise gspread.exceptions.APIError("Exceeded max retries for rate limited requests.")
        return wrapper
    return rwb

# --- Scopes and Client ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly"
]

class GSheetClient:
    """A client to interact with Google Sheets."""

    def __init__(self, credentials: dict, spreadsheet_name: str):
        self.creds = Credentials.from_service_account_info(credentials, scopes=SCOPES)
        self.client = gspread.authorize(self.creds)
        self.spreadsheet = self.client.open(spreadsheet_name)

    @classmethod
    def from_settings(cls) -> "GSheetClient":
        return cls(
            credentials=settings.google_credentials,
            spreadsheet_name=settings.SPREADSHEET_NAME
        )

    @retry_with_backoff()
    def get_worksheet(self, worksheet_name: str) -> gspread.Worksheet:
        return self.spreadsheet.worksheet(worksheet_name)

    @retry_with_backoff()
    def find_row_by_employee_id(self, worksheet: gspread.Worksheet, employee_id: str) -> Optional[Dict[str, Any]]:
        try:
            headers = worksheet.row_values(1)
            uid_col_name = settings.COL_UNIQUE_ID
            if uid_col_name not in headers:
                raise ValueError(f"Column '{uid_col_name}' not found.")

            employee_id_col_index = headers.index(uid_col_name) + 1
            cell = worksheet.find(employee_id, in_column=employee_id_col_index)
            if not cell:
                return None

            row_data = worksheet.row_values(cell.row)
            return dict(zip(headers, row_data))
        except gspread.exceptions.CellNotFound:
            return None

    @retry_with_backoff()
    def update_check_in_status(self, worksheet: gspread.Worksheet, employee_id: str, timestamp_str: str) -> bool:
        try:
            headers = worksheet.row_values(1)
            uid_col_index = headers.index(settings.COL_UNIQUE_ID) + 1
            cell = worksheet.find(employee_id, in_column=uid_col_index)
            if not cell: return False

            updates = [
                {'range': f'{gspread.utils.rowcol_to_a1(cell.row, headers.index(settings.COL_CHECK_IN_STATUS) + 1)}', 'values': [['TRUE']]},
                {'range': f'{gspread.utils.rowcol_to_a1(cell.row, headers.index(settings.COL_CHECK_IN_TIME) + 1)}', 'values': [[timestamp_str]]},
            ]
            worksheet.batch_update(updates)
            return True
        except (gspread.exceptions.CellNotFound, ValueError):
            return False

    @retry_with_backoff()
    def update_check_out_status(self, worksheet: gspread.Worksheet, employee_id: str, timestamp_str: str) -> bool:
        try:
            headers = worksheet.row_values(1)
            uid_col_index = headers.index(settings.COL_UNIQUE_ID) + 1
            cell = worksheet.find(employee_id, in_column=uid_col_index)
            if not cell: return False

            updates = [
                {'range': f'{gspread.utils.rowcol_to_a1(cell.row, headers.index(settings.COL_CHECK_OUT_STATUS) + 1)}', 'values': [['TRUE']]},
                {'range': f'{gspread.utils.rowcol_to_a1(cell.row, headers.index(settings.COL_CHECK_OUT_TIME) + 1)}', 'values': [[timestamp_str]]},
            ]
            worksheet.batch_update(updates)
            return True
        except (gspread.exceptions.CellNotFound, ValueError):
            return False

    @retry_with_backoff()
    def get_status_counts(self, worksheet: gspread.Worksheet) -> Dict[str, int]:
        all_records = worksheet.get_all_records()
        total_attendees = len(all_records)
        check_in_col = settings.COL_CHECK_IN_STATUS
        check_out_col = settings.COL_CHECK_OUT_STATUS
        checked_in_count = sum(1 for record in all_records if str(record.get(check_in_col, 'FALSE')).upper() == 'TRUE')
        checked_out_count = sum(1 for record in all_records if str(record.get(check_out_col, 'FALSE')).upper() == 'TRUE')
        return {
            "total_attendees": total_attendees,
            "checked_in_count": checked_in_count,
            "checked_out_count": checked_out_count,
        }
