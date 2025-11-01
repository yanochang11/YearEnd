from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
import gspread

from .config import settings
from .dependencies import get_api_key
from .gsheet_client import GSheetClient
from .models import (
    CheckInRequest,
    CheckInSuccessResponse,
    CheckOutSuccessResponse,
    ErrorResponse,
    ConflictResponse,
    StatusResponse,
)

app = FastAPI(
    title="尾牙報到/簽退 API 系統",
    description="一個使用 FastAPI 和 Google Sheets 的 QR Code 報到系統。",
    version="1.0.0",
)

# --- Exception Handlers ---

@app.exception_handler(ValueError)
async def value_error_exception_handler(request, exc):
    """Handles exceptions related to missing environment variables."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )

@app.exception_handler(gspread.exceptions.SpreadsheetNotFound)
async def spreadsheet_not_found_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": f"Google Sheet '{settings.SPREADSHEET_NAME}' not found. Please run setup script."},
    )

@app.exception_handler(gspread.exceptions.WorksheetNotFound)
async def worksheet_not_found_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": f"Worksheet '{settings.WORKSHEET_NAME}' not found. Please run setup script."},
    )


# --- API Endpoints ---

@app.post("/check-in",
          response_model=CheckInSuccessResponse,
          responses={
              404: {"model": ErrorResponse},
              409: {"model": ConflictResponse},
              401: {"model": ErrorResponse},
          })
def check_in(request: CheckInRequest, api_key: str = Depends(get_api_key)):
    """Handles attendee check-in."""
    try:
        gsheet_client = GSheetClient.from_settings()
        worksheet = gsheet_client.get_worksheet(settings.WORKSHEET_NAME)

        attendee = gsheet_client.find_row_by_unique_id(worksheet, request.unique_id)

        if not attendee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="賓客 ID 不存在")

        if str(attendee.get(settings.COL_CHECK_IN_STATUS, "FALSE")).upper() == "TRUE":
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"detail": "此人已簽到", "name": attendee.get(settings.COL_NAME, "")}
            )

        success = gsheet_client.update_check_in_status(worksheet, request.unique_id)
        if not success:
            raise HTTPException(status_code=500, detail="更新簽到狀態失敗")

        return CheckInSuccessResponse(
            name=attendee.get(settings.COL_NAME, ""),
            department=attendee.get(settings.COL_DEPARTMENT, "")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"內部伺服器錯誤: {e}")


@app.post("/check-out",
          response_model=CheckOutSuccessResponse,
          responses={
              400: {"model": ErrorResponse},
              404: {"model": ErrorResponse},
              409: {"model": ConflictResponse},
              401: {"model": ErrorResponse},
          })
def check_out(request: CheckInRequest, api_key: str = Depends(get_api_key)):
    """Handles attendee check-out."""
    try:
        gsheet_client = GSheetClient.from_settings()
        worksheet = gsheet_client.get_worksheet(settings.WORKSHEET_NAME)

        attendee = gsheet_client.find_row_by_unique_id(worksheet, request.unique_id)

        if not attendee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="賓客 ID 不存在")

        if str(attendee.get(settings.COL_CHECK_IN_STATUS, "FALSE")).upper() == "FALSE":
             return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "此人尚未簽到，無法簽退"}
            )

        if str(attendee.get(settings.COL_CHECK_OUT_STATUS, "FALSE")).upper() == "TRUE":
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"detail": "此人已簽退", "name": attendee.get(settings.COL_NAME, "")}
            )

        success = gsheet_client.update_check_out_status(worksheet, request.unique_id)
        if not success:
            raise HTTPException(status_code=500, detail="更新簽退狀態失敗")

        return CheckOutSuccessResponse(
            name=attendee.get(settings.COL_NAME, ""),
            department=attendee.get(settings.COL_DEPARTMENT, "")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"內部伺服器錯誤: {e}")


@app.get("/status",
         response_model=StatusResponse,
         responses={401: {"model": ErrorResponse}})
def get_status(api_key: str = Depends(get_api_key)):
    """Returns the current check-in and check-out status."""
    try:
        gsheet_client = GSheetClient.from_settings()
        worksheet = gsheet_client.get_worksheet(settings.WORKSHEET_NAME)

        counts = gsheet_client.get_status_counts(worksheet)

        return StatusResponse(**counts)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"內部伺服器錯誤: {e}")
