from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import gspread
from pathlib import Path

from .config import settings
from .dependencies import get_api_key
from .gsheet_client import GSheetClient
from .models import CheckInRequest, CheckInSuccessResponse, CheckOutSuccessResponse, ErrorResponse, ConflictResponse, StatusResponse

app = FastAPI(title="尾牙報到/簽退 API 系統", version="2.1.0")
api_router = APIRouter(prefix="/api")

@app.exception_handler(gspread.exceptions.SpreadsheetNotFound)
async def spreadsheet_not_found_handler(request, exc):
    return JSONResponse(status_code=503, content={"detail": f"Google Sheet '{settings.SPREADSHEET_NAME}' not found."})

@app.exception_handler(gspread.exceptions.WorksheetNotFound)
async def worksheet_not_found_handler(request, exc):
    return JSONResponse(status_code=503, content={"detail": f"Worksheet '{settings.WORKSHEET_NAME}' not found."})


@api_router.post("/check-in", response_model=CheckInSuccessResponse, tags=["Check-in/Out"])
def check_in(request: CheckInRequest, api_key: str = Depends(get_api_key)):
    try:
        gsheet_client = GSheetClient.from_settings()
        worksheet = gsheet_client.get_worksheet(settings.WORKSHEET_NAME)
        attendee = gsheet_client.find_row_by_unique_id(worksheet, request.unique_id)

        if not attendee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="賓客 ID 不存在")

        if str(attendee.get(settings.COL_CHECK_IN_STATUS, "FALSE")).upper() == "TRUE":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"detail": "此人已簽到", "name": attendee.get(settings.COL_NAME, "")}
            )

        gsheet_client.update_check_in_status(worksheet, request.unique_id)

        return CheckInSuccessResponse(
            name=attendee.get(settings.COL_NAME, ""),
            department=attendee.get(settings.COL_DEPARTMENT, ""),
            table_number=attendee.get(settings.COL_TABLE_NUMBER)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"內部伺服器錯誤: {e}")

@api_router.post("/check-out", response_model=CheckOutSuccessResponse, tags=["Check-in/Out"])
def check_out(request: CheckInRequest, api_key: str = Depends(get_api_key)):
    try:
        gsheet_client = GSheetClient.from_settings()
        worksheet = gsheet_client.get_worksheet(settings.WORKSHEET_NAME)
        attendee = gsheet_client.find_row_by_unique_id(worksheet, request.unique_id)

        if not attendee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="賓客 ID 不存在")

        if str(attendee.get(settings.COL_CHECK_IN_STATUS, "FALSE")).upper() == "FALSE":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="此人尚未簽到，無法簽退")

        if str(attendee.get(settings.COL_CHECK_OUT_STATUS, "FALSE")).upper() == "TRUE":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"detail": "此人已簽退", "name": attendee.get(settings.COL_NAME, "")}
            )

        gsheet_client.update_check_out_status(worksheet, request.unique_id)
        return CheckOutSuccessResponse(name=attendee.get(settings.COL_NAME, ""), department=attendee.get(settings.COL_DEPARTMENT, ""))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"內部伺服器錯誤: {e}")

@api_router.get("/status", response_model=StatusResponse, tags=["Status"])
def get_status(api_key: str = Depends(get_api_key)):
    try:
        gsheet_client = GSheetClient.from_settings()
        worksheet = gsheet_client.get_worksheet(settings.WORKSHEET_NAME)
        return StatusResponse(**gsheet_client.get_status_counts(worksheet))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"內部伺服器錯誤: {e}")

app.include_router(api_router)
static_files_path = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=static_files_path, html=True), name="static")
