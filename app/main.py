from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import gspread
from pathlib import Path
from contextlib import asynccontextmanager

from .config import settings
from .dependencies import get_api_key
from .gsheet_client import GSheetClient
from .models import CheckInRequest, CheckInSuccessResponse, CheckOutSuccessResponse, ErrorResponse, ConflictResponse, StatusResponse
from .cache_manager import cache_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    cache_manager.start()
    yield
    # Shutdown
    cache_manager.stop()

app = FastAPI(title="尾牙報到/簽退 API 系統", version="3.0.0", lifespan=lifespan)
api_router = APIRouter(prefix="/api")


@app.exception_handler(gspread.exceptions.SpreadsheetNotFound)
async def spreadsheet_not_found_handler(request, exc):
    return JSONResponse(status_code=503, content={"detail": f"Google Sheet '{settings.SPREADSHEET_NAME}' not found."})

@app.exception_handler(gspread.exceptions.WorksheetNotFound)
async def worksheet_not_found_handler(request, exc):
    return JSONResponse(status_code=503, content={"detail": f"Worksheet '{settings.WORKSHEET_NAME}' not found."})

@app.exception_handler(gspread.exceptions.APIError)
async def gspread_api_error_handler(request, exc):
    return JSONResponse(status_code=503, content={"detail": f"Google Sheets API error: {exc}"})

@api_router.post("/check-in", tags=["Check-in/Out"])
def check_in(request: CheckInRequest, api_key: str = Depends(get_api_key)):
    if not cache_manager.is_initialized:
        raise HTTPException(status_code=503, detail="Cache is not initialized yet.")

    attendee = cache_manager.get_attendee(request.employeeId)

    if not attendee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="賓客 ID 不存在")

    if str(attendee.get(settings.COL_CHECK_IN_STATUS, "FALSE")).upper() == "TRUE":
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "此人已簽到",
                "name": attendee.get(settings.COL_NAME, ""),
                "table_number": attendee.get(settings.COL_TABLE_NUMBER)
            }
        )

    updated_attendee = cache_manager.update_check_in_status(request.employeeId)

    return CheckInSuccessResponse(
        name=updated_attendee.get(settings.COL_NAME, ""),
        department=updated_attendee.get(settings.COL_DEPARTMENT, ""),
        table_number=updated_attendee.get(settings.COL_TABLE_NUMBER)
    )

@api_router.post("/check-out", response_model=CheckOutSuccessResponse, tags=["Check-in/Out"])
def check_out(request: CheckInRequest, api_key: str = Depends(get_api_key)):
    if not cache_manager.is_initialized:
        raise HTTPException(status_code=503, detail="Cache is not initialized yet.")

    attendee = cache_manager.get_attendee(request.employeeId)

    if not attendee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="賓客 ID 不存在")

    if str(attendee.get(settings.COL_CHECK_IN_STATUS, "FALSE")).upper() == "FALSE":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="此人尚未簽到，無法簽退")

    if str(attendee.get(settings.COL_CHECK_OUT_STATUS, "FALSE")).upper() == "TRUE":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "此人已簽退", "name": attendee.get(settings.COL_NAME, "")}
        )

    updated_attendee = cache_manager.update_check_out_status(request.employeeId)

    return CheckOutSuccessResponse(
        name=updated_attendee.get(settings.COL_NAME, ""),
        department=updated_attendee.get(settings.COL_DEPARTMENT, "")
    )

@api_router.get("/status", response_model=StatusResponse, tags=["Status"])
def get_status(api_key: str = Depends(get_api_key)):
    if not cache_manager.is_initialized:
        raise HTTPException(status_code=503, detail="Cache is not initialized yet.")

    all_attendees = cache_manager.get_all_attendees()
    total_attendees = len(all_attendees)
    checked_in_count = sum(1 for record in all_attendees if str(record.get(settings.COL_CHECK_IN_STATUS, 'FALSE')).upper() == 'TRUE')
    checked_out_count = sum(1 for record in all_attendees if str(record.get(settings.COL_CHECK_OUT_STATUS, 'FALSE')).upper() == 'TRUE')

    return StatusResponse(
        total_attendees=total_attendees,
        checked_in_count=checked_in_count,
        checked_out_count=checked_out_count,
    )

app.include_router(api_router)
static_files_path = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=static_files_path, html=True), name="static")
