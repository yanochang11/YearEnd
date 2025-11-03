import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import os

os.environ['API_KEY'] = 'test-api-key'

from app.main import app
from app.dependencies import get_api_key
from app.config import settings

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture
def mock_gsheet_client(mocker):
    mock_instance = MagicMock()
    mocker.patch('app.gsheet_client.GSheetClient.from_settings', return_value=mock_instance)
    mock_worksheet = MagicMock()
    mock_instance.get_worksheet.return_value = mock_worksheet
    return mock_instance

async def override_get_api_key():
    return os.environ['API_KEY']

app.dependency_overrides[get_api_key] = override_get_api_key

def test_checkin_success(client, mock_gsheet_client):
    employee_id = "uuid-success"
    attendee_data = {
        settings.COL_NAME: "王大明",
        settings.COL_DEPARTMENT: "工程部",
        settings.COL_TABLE_NUMBER: "A1",
        settings.COL_UNIQUE_ID: employee_id,
        settings.COL_CHECK_IN_STATUS: "FALSE"
    }
    mock_gsheet_client.find_row_by_employee_id.return_value = attendee_data
    response = client.post("/api/check-in", json={"employeeId": employee_id})

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "王大明"
    assert response_json["table_number"] == "A1"

def test_checkin_user_not_found(client, mock_gsheet_client):
    mock_gsheet_client.find_row_by_employee_id.return_value = None
    response = client.post("/api/check-in", json={"employeeId": "uuid-not-found"})
    assert response.status_code == 404

def test_checkin_already_checked_in(client, mock_gsheet_client):
    employee_id = "uuid-already-checked-in"
    attendee_data = {
        settings.COL_NAME: "陳小美", settings.COL_UNIQUE_ID: employee_id,
        settings.COL_CHECK_IN_STATUS: "TRUE"
    }
    mock_gsheet_client.find_row_by_employee_id.return_value = attendee_data
    response = client.post("/api/check-in", json={"employeeId": employee_id})
    assert response.status_code == 409
    assert response.json()["detail"] == "此人已簽到"

def test_checkout_success(client, mock_gsheet_client):
    employee_id = "uuid-checkout-success"
    attendee_data = {
        settings.COL_NAME: "李中天", settings.COL_DEPARTMENT: "人資部",
        settings.COL_UNIQUE_ID: employee_id,
        settings.COL_CHECK_IN_STATUS: "TRUE", settings.COL_CHECK_OUT_STATUS: "FALSE"
    }
    mock_gsheet_client.find_row_by_employee_id.return_value = attendee_data
    response = client.post("/api/check-out", json={"employeeId": employee_id})
    assert response.status_code == 200

def test_checkout_not_checked_in(client, mock_gsheet_client):
    attendee_data = {settings.COL_CHECK_IN_STATUS: "FALSE"}
    mock_gsheet_client.find_row_by_employee_id.return_value = attendee_data
    response = client.post("/api/check-out", json={"employeeId": "uuid-not-checked-in"})
    assert response.status_code == 400

def test_checkout_already_checked_out(client, mock_gsheet_client):
    employee_id = "uuid-already-checked-out"
    attendee_data = {
        settings.COL_NAME: "陳小美", settings.COL_UNIQUE_ID: employee_id,
        settings.COL_CHECK_IN_STATUS: "TRUE", settings.COL_CHECK_OUT_STATUS: "TRUE"
    }
    mock_gsheet_client.find_row_by_employee_id.return_value = attendee_data
    response = client.post("/api/check-out", json={"employeeId": employee_id})
    assert response.status_code == 409

def test_get_status(client, mock_gsheet_client):
    status_data = {"total_attendees": 500, "checked_in_count": 150, "checked_out_count": 50}
    mock_gsheet_client.get_status_counts.return_value = status_data
    response = client.get("/api/status")
    assert response.status_code == 200
    assert response.json() == status_data
