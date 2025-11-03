from pydantic import BaseModel, Field
from typing import Optional

class CheckInRequest(BaseModel):
    """Request model for the check-in endpoint."""
    employeeID: str = Field(..., description="The unique ID of the attendee.")

class CheckInSuccessResponse(BaseModel):
    """Response model for a successful check-in."""
    status: str = "success"
    name: str
    department: str
    table_number: Optional[str] = None

class CheckOutSuccessResponse(BaseModel):
    """Response model for a successful check-out."""
    status: str = "success"
    name: str
    department: str

class ErrorResponse(BaseModel):
    """Generic error response model."""
    detail: str

class ConflictResponse(BaseModel):
    """Error response for conflicts (e.g., already checked in)."""
    detail: str
    name: str

class StatusResponse(BaseModel):
    """Response model for the status endpoint."""
    total_attendees: int
    checked_in_count: int
    checked_out_count: int
