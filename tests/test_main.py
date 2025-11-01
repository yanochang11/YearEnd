import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# It's a good practice to set up the test environment before importing the app
# For example, by setting a specific environment variable
import os
os.environ['API_KEY'] = 'test-api-key'

# Now, import the app
from app.main import app
from app.dependencies import get_api_key

# --- Test Fixtures ---

@pytest.fixture(scope="module")
def client():
    """Provides a TestClient instance for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def mock_gsheet_client(mocker):
    """Mocks the GSheetClient and its methods."""
    # Create a mock object for the GSheetClient instance
    mock_instance = MagicMock()

    # Patch the factory method `from_settings` to return our mock instance
    # This is the key to injecting the mock into our API calls
    mocker.patch('app.gsheet_client.GSheetClient.from_settings', return_value=mock_instance)

    return mock_instance

# --- Helper to override dependency ---
# This allows us to bypass the API key check in tests
async def override_get_api_key():
    return os.environ['API_KEY']

app.dependency_overrides[get_api_key] = override_get_api_key


# --- Test Cases for POST /check-in ---

def test_checkin_success(client, mock_gsheet_client):
    """Test successful check-in."""
    # Arrange: Configure the mock
    unique_id = "uuid-success"
    attendee_data = {
        "Name": "王大明", "Department": "工程部",
        "UniqueID": unique_id, "CheckInStatus": "FALSE"
    }
    mock_gsheet_client.find_row_by_unique_id.return_value = attendee_data
    mock_gsheet_client.update_check_in_status.return_value = True

    # Act: Make the API call
    response = client.post("/check-in", json={"unique_id": unique_id})

    # Assert: Check the response and mock calls
    assert response.status_code == 200
    assert response.json() == {"status": "success", "name": "王大明", "department": "工程部"}
    mock_gsheet_client.find_row_by_unique_id.assert_called_once_with(mock_gsheet_client.get_worksheet(), unique_id)
    mock_gsheet_client.update_check_in_status.assert_called_once_with(mock_gsheet_client.get_worksheet(), unique_id)

def test_checkin_user_not_found(client, mock_gsheet_client):
    """Test check-in when user's unique ID is not found."""
    # Arrange
    unique_id = "uuid-not-found"
    mock_worksheet = MagicMock()
    mock_gsheet_client.get_worksheet.return_value = mock_worksheet
    mock_gsheet_client.find_row_by_unique_id.return_value = None

    # Act
    response = client.post("/check-in", json={"unique_id": unique_id})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "賓客 ID 不存在"}
    mock_gsheet_client.find_row_by_unique_id.assert_called_once_with(mock_worksheet, unique_id)
    mock_gsheet_client.update_check_in_status.assert_not_called()

def test_checkin_already_checked_in(client, mock_gsheet_client):
    """Test check-in when user is already checked in."""
    # Arrange
    unique_id = "uuid-already-checked-in"
    attendee_data = {
        "Name": "陳小美", "Department": "市場部",
        "UniqueID": unique_id, "CheckInStatus": "TRUE"
    }
    mock_gsheet_client.find_row_by_unique_id.return_value = attendee_data

    # Act
    response = client.post("/check-in", json={"unique_id": unique_id})

    # Assert
    assert response.status_code == 409
    assert response.json() == {"detail": "此人已簽到", "name": "陳小美"}
    mock_gsheet_client.update_check_in_status.assert_not_called()


# --- Test Cases for POST /check-out ---

def test_checkout_success(client, mock_gsheet_client):
    """Test successful check-out."""
    unique_id = "uuid-checkout-success"
    attendee_data = {
        "Name": "李中天", "Department": "人資部",
        "UniqueID": unique_id,
        "CheckInStatus": "TRUE",
        "CheckOutStatus": "FALSE"
    }
    mock_gsheet_client.find_row_by_unique_id.return_value = attendee_data
    mock_gsheet_client.update_check_out_status.return_value = True

    response = client.post("/check-out", json={"unique_id": unique_id})

    assert response.status_code == 200
    assert response.json() == {"status": "success", "name": "李中天", "department": "人資部"}
    mock_gsheet_client.update_check_out_status.assert_called_once()

def test_checkout_not_checked_in(client, mock_gsheet_client):
    """Test check-out when user has not checked in yet."""
    unique_id = "uuid-not-checked-in"
    attendee_data = {
        "Name": "王大明", "UniqueID": unique_id,
        "CheckInStatus": "FALSE", "CheckOutStatus": "FALSE"
    }
    mock_gsheet_client.find_row_by_unique_id.return_value = attendee_data

    response = client.post("/check-out", json={"unique_id": unique_id})

    assert response.status_code == 400
    assert response.json() == {"detail": "此人尚未簽到，無法簽退"}
    mock_gsheet_client.update_check_out_status.assert_not_called()

def test_checkout_already_checked_out(client, mock_gsheet_client):
    """Test check-out when user is already checked out."""
    unique_id = "uuid-already-checked-out"
    attendee_data = {
        "Name": "陳小美", "UniqueID": unique_id,
        "CheckInStatus": "TRUE", "CheckOutStatus": "TRUE"
    }
    mock_gsheet_client.find_row_by_unique_id.return_value = attendee_data

    response = client.post("/check-out", json={"unique_id": unique_id})

    assert response.status_code == 409
    assert response.json() == {"detail": "此人已簽退", "name": "陳小美"}
    mock_gsheet_client.update_check_out_status.assert_not_called()


# --- Test Case for GET /status ---

def test_get_status(client, mock_gsheet_client):
    """Test the status endpoint."""
    # Arrange
    status_data = {
        "total_attendees": 500,
        "checked_in_count": 150,
        "checked_out_count": 50
    }
    mock_gsheet_client.get_status_counts.return_value = status_data

    # Act
    response = client.get("/status")

    # Assert
    assert response.status_code == 200
    assert response.json() == status_data
    mock_gsheet_client.get_status_counts.assert_called_once()
