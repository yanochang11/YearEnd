import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional, Any
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

    def find_row(self, worksheet: gspread.Worksheet, column: str, value: str) -> Optional[Dict[str, Any]]:
        """
        Finds a row by a specific value in a given column.
        Returns the entire row as a dictionary or None if not found.
        """
        try:
            cell = worksheet.find(value, in_column=worksheet.find(column).col)
            if cell:
                row_values = worksheet.row_values(cell.row)
                headers = worksheet.row_values(1)
                return dict(zip(headers, row_values))
            return None
        except (gspread.exceptions.CellNotFound, gspread.exceptions.WorksheetNotFound):
            return None

    def find_row_by_unique_id(self, worksheet: gspread.Worksheet, unique_id: str) -> Optional[Dict[str, Any]]:
        """
        Finds a guest's record by their UniqueID.
        """
        # Google Sheets `find` can be slow. A more efficient way for larger sheets
        # would be to fetch all records and search in-memory, but `find` is simpler.
        try:
            # Assuming 'UniqueID' is the header for the unique ID column.
            # We first find the column index for 'UniqueID'.
            headers = worksheet.row_values(1)
            if 'UniqueID' not in headers:
                raise ValueError("Column 'UniqueID' not found in the worksheet.")

            unique_id_col_index = headers.index('UniqueID') + 1

            # Now find the cell with the unique_id in that specific column
            cell = worksheet.find(unique_id, in_column=unique_id_col_index)
            if not cell:
                return None

            row_data = worksheet.row_values(cell.row)
            return dict(zip(headers, row_data))

        except gspread.exceptions.CellNotFound:
            return None


    def update_cell(self, worksheet: gspread.Worksheet, row_index: int, col_name: str, value: Any) -> None:
        """Updates a single cell in a given row."""
        try:
            col_index = worksheet.find(col_name).col
            worksheet.update_cell(row_index, col_index, value)
        except gspread.exceptions.CellNotFound:
            raise ValueError(f"Column '{col_name}' not found.")

    def update_check_in_status(self, worksheet: gspread.Worksheet, unique_id: str) -> bool:
        """Updates the check-in status and timestamp for a user."""
        try:
            headers = worksheet.row_values(1)
            uid_col_index = headers.index('UniqueID') + 1

            cell = worksheet.find(unique_id, in_column=uid_col_index)
            if not cell:
                return False

            # Prepare batch updates
            updates = [
                {'range': f'{gspread.utils.rowcol_to_a1(cell.row, headers.index("CheckInStatus") + 1)}', 'values': [['TRUE']]},
                {'range': f'{gspread.utils.rowcol_to_a1(cell.row, headers.index("CheckInTime") + 1)}', 'values': [[datetime.now(timezone.utc).isoformat()]]},
            ]
            worksheet.batch_update(updates)
            return True
        except (gspread.exceptions.CellNotFound, ValueError):
            return False

    def update_check_out_status(self, worksheet: gspread.Worksheet, unique_id: str) -> bool:
        """Updates the check-out status and timestamp for a user."""
        try:
            headers = worksheet.row_values(1)
            uid_col_index = headers.index('UniqueID') + 1

            cell = worksheet.find(unique_id, in_column=uid_col_index)
            if not cell:
                return False

            updates = [
                {'range': f'{gspread.utils.rowcol_to_a1(cell.row, headers.index("CheckOutStatus") + 1)}', 'values': [['TRUE']]},
                {'range': f'{gspread.utils.rowcol_to_a1(cell.row, headers.index("CheckOutTime") + 1)}', 'values': [[datetime.now(timezone.utc).isoformat()]]},
            ]
            worksheet.batch_update(updates)
            return True
        except (gspread.exceptions.CellNotFound, ValueError):
            return False

    def get_status_counts(self, worksheet: gspread.Worksheet) -> Dict[str, int]:
        """Calculates and returns the counts of total, checked-in, and checked-out attendees."""
        all_records = worksheet.get_all_records()
        total_attendees = len(all_records)
        checked_in_count = sum(1 for record in all_records if str(record.get('CheckInStatus', 'FALSE')).upper() == 'TRUE')
        checked_out_count = sum(1 for record in all_records if str(record.get('CheckOutStatus', 'FALSE')).upper() == 'TRUE')

        return {
            "total_attendees": total_attendees,
            "checked_in_count": checked_in_count,
            "checked_out_count": checked_out_count,
        }
