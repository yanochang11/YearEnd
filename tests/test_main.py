import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import os

# Set up test environment before importing the app
os.environ['API_KEY'] = 'test-api-key'

from app.main import app
from app.dependencies import get_api_key
from app.config import settings

# --- Test Fixtures ---

@pytest.fixture(scope="module")
def client():
    """Provides a TestClient instance for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def mock_gsheet_client(mocker):
    """Mocks the GSheetClient and its methods."""
    mock_instance = MagicMock()
    mocker.patch('app.gsheet_client.GSheetClient.from_settings', return_value=mock_instance)

    # Also mock the worksheet object that the client's methods will receive
    mock_worksheet = MagicMock()
    mock_instance.get_worksheet.return_value = mock_worksheet

    return mock_instance

# --- Helper to override dependency ---
async def override_get_api_key():
    return os.environ['API_KEY']

app.dependency_overrides[get_api_key] = override_get_api_key


# --- Test Cases for POST /check-in ---

def test_checkin_success(client, mock_gsheet_client):
    """Test successful check-in."""
    unique_id = "uuid-success"
    attendee_data = {
        settings.COL_NAME: "王大明",
        settings.COL_DEPARTMENT: "工程部",
        settings.COL_UNIQUE_ID: unique_id,
        settings.COL_CHECK_IN_STATUS: "FALSE"
    }
    mock_gsheet_client.find_row_by_unique_id.return_value = attendee_data
    mock_gsheet_client.update_check_in_status.return_value = True

    response = client.post("/check-in", json={"unique_id": unique_id})

    assert response.status_code == 200
    assert response.json() == {"status": "success", "name": "王大明", "department": "工程部"}
    mock_gsheet_client.find_row_by_unique_id.assert_called_once()
    mock_gsheet_client.update_check_in_status.assert_called_once()

def test_checkin_user_not_found(client, mock_gsheet_client):
    """Test check-in when user's unique ID is not found."""
    unique_id = "uuid-not-found"
    mock_gsheet_client.find_row_by_unique_id.return_value = None

    response = client.post("/check-in", json={"unique_id": unique_id})

    assert response.status_code == 404
    assert response.json() == {"detail": "賓客 ID 不存在"}

def test_checkin_already_checked_in(client, mock_gsheet_client):
    """Test check-in when user is already checked in."""
    unique_id = "uuid-already-checked-in"
    attendee_data = {
        settings.COL_NAME: "陳小美",
        settings.COL_UNIQUE_ID: unique_id,
        settings.COL_CHECK_IN_STATUS: "TRUE"
    }
    mock_gsheet_client.find_row_by_unique_id.return_value = attendee_data

    response = client.post("/check-in", json={"unique_id": unique_id})

    assert response.status_code == 409
    assert response.json() == {"detail": "此人已簽到", "name": "陳小美"}


# --- Test Cases for POST /check-out ---

def test_checkout_success(client, mock_gsheet_client):
    """Test successful check-out."""
    unique_id = "uuid-checkout-success"
    attendee_data = {
        settings.COL_NAME: "李中天",
        settings.COL_DEPARTMENT: "人資部",
        settings.COL_UNIQUE_ID: unique_id,
        settings.COL_CHECK_IN_STATUS: "TRUE",
        settings.COL_CHECK_OUT_STATUS: "FALSE"
    }
    mock_gsheet_client.find_row_by_unique_id.return_value = attendee_data
    mock_gsheet_client.update_check_out_status.return_value = True

    response = client.post("/check-out", json={"unique_id": unique_id})

    assert response.status_code == 200
    assert response.json() == {"status": "success", "name": "李中天", "department": "人資部"}

def test_checkout_not_checked_in(client, mock_gsheet_client):
    """Test check-out when user has not checked in yet."""
    unique_id = "uuid-not-checked-in"
    attendee_data = {
        settings.COL_NAME: "王大明",
        settings.COL_UNIQUE_ID: unique_id,
        settings.COL_CHECK_IN_STATUS: "FALSE",
        settings.COL_CHECK_OUT_STATUS: "FALSE"
    }
    mock_gsheet_client.find_row_by_unique_id.return_value = attendee_data

    response = client.post("/check-out", json={"unique_id": unique_id})

    assert response.status_code == 400
    assert response.json() == {"detail": "此人尚未簽到，無法簽退"}

def test_checkout_already_checked_out(client, mock_gsheet_client):
    """Test check-out when user is already checked out."""
    unique_id = "uuid-already-checked-out"
    attendee_data = {
        settings.COL_NAME: "陳小美",
        settings.COL_UNIQUE_ID: unique_id,
        settings.COL_CHECK_IN_STATUS: "TRUE",
        settings.COL_CHECK_OUT_STATUS: "TRUE"
    }
    mock_gsheet_client.find_row_by_unique_id.return_value = attendee_data

    response = client.post("/check-out", json={"unique_id": unique_id})

    assert response.status_code == 409
    assert response.json() == {"detail": "此人已簽退", "name": "陳小美"}


# --- Test Case for GET /status ---

def test_get_status(client, mock_gsheet_client):
    """Test the status endpoint."""
    status_data = {
        "total_attendees": 500,
        "checked_in_count": 150,
        "checked_out_count": 50
    }
    mock_gsheet_client.get_status_counts.return_value = status_data

    response = client.get("/status")

    assert response.status_code == 200
    assert response.json() == status_data
