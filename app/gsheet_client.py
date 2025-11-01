import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, Optional, Any
from datetime import datetime, timezone

from .config import settings

class GSheetClient:
    """A client to interact with Google Sheets."""

    def __init__(self, credentials: dict, spreadsheet_name: str):
        """
        Initializes the client with Google service account credentials and spreadsheet name.
        """
        self.creds = Credentials.from_service_account_info(
            credentials,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        self.client = gspread.authorize(self.creds)
        self.spreadsheet = self.client.open(spreadsheet_name)

    @classmethod
    def from_settings(cls) -> "GSheetClient":
        """Factory method to create a client from application settings."""
        return cls(
            credentials=settings.google_credentials,
            spreadsheet_name=settings.SPREADSHEET_NAME
        )

    def get_worksheet(self, worksheet_name: str) -> gspread.Worksheet:
        """Gets a worksheet by name. Raises gspread.exceptions.WorksheetNotFound if not found."""
        return self.spreadsheet.worksheet(worksheet_name)

    def find_row_by_unique_id(self, worksheet: gspread.Worksheet, unique_id: str) -> Optional[Dict[str, Any]]:
        """
        Finds a guest's record by their UniqueID.
        """
        try:
            headers = worksheet.row_values(1)
            uid_col_name = settings.COL_UNIQUE_ID
            if uid_col_name not in headers:
                raise ValueError(f"Column '{uid_col_name}' not found in the worksheet.")

            unique_id_col_index = headers.index(uid_col_name) + 1

            cell = worksheet.find(unique_id, in_column=unique_id_col_index)
            if not cell:
                return None

            row_data = worksheet.row_values(cell.row)
            return dict(zip(headers, row_data))

        except gspread.exceptions.CellNotFound:
            return None

    def update_check_in_status(self, worksheet: gspread.Worksheet, unique_id: str) -> bool:
        """Updates the check-in status and timestamp for a user."""
        try:
            headers = worksheet.row_values(1)
            uid_col_index = headers.index(settings.COL_UNIQUE_ID) + 1

            cell = worksheet.find(unique_id, in_column=uid_col_index)
            if not cell:
                return False

            updates = [
                {'range': f'{gspread.utils.rowcol_to_a1(cell.row, headers.index(settings.COL_CHECK_IN_STATUS) + 1)}', 'values': [['TRUE']]},
                {'range': f'{gspread.utils.rowcol_to_a1(cell.row, headers.index(settings.COL_CHECK_IN_TIME) + 1)}', 'values': [[datetime.now(timezone.utc).isoformat()]]},
            ]
            worksheet.batch_update(updates)
            return True
        except (gspread.exceptions.CellNotFound, ValueError):
            return False

    def update_check_out_status(self, worksheet: gspread.Worksheet, unique_id: str) -> bool:
        """Updates the check-out status and timestamp for a user."""
        try:
            headers = worksheet.row_values(1)
            uid_col_index = headers.index(settings.COL_UNIQUE_ID) + 1

            cell = worksheet.find(unique_id, in_column=uid_col_index)
            if not cell:
                return False

            updates = [
                {'range': f'{gspread.utils.rowcol_to_a1(cell.row, headers.index(settings.COL_CHECK_OUT_STATUS) + 1)}', 'values': [['TRUE']]},
                {'range': f'{gspread.utils.rowcol_to_a1(cell.row, headers.index(settings.COL_CHECK_OUT_TIME) + 1)}', 'values': [[datetime.now(timezone.utc).isoformat()]]},
            ]
            worksheet.batch_update(updates)
            return True
        except (gspread.exceptions.CellNotFound, ValueError):
            return False

    def get_status_counts(self, worksheet: gspread.Worksheet) -> Dict[str, int]:
        """Calculates and returns the counts of total, checked-in, and checked-out attendees."""
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
