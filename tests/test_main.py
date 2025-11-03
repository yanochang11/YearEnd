import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import os

os.environ['API_KEY'] = 'test-api-key'

# Mock CacheManager before it's imported by other modules
mock_cache_manager = MagicMock()
mock_cache_manager.is_initialized = True

with patch('app.cache_manager.cache_manager', mock_cache_manager):
    from app.main import app
    from app.dependencies import get_api_key
    from app.config import settings

@pytest.fixture(scope="module")
def client():
    # The app is already loaded with the patched cache_manager
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_mock_cache():
    mock_cache_manager.reset_mock()
    mock_cache_manager.is_initialized = True


async def override_get_api_key():
    return os.environ['API_KEY']

app.dependency_overrides[get_api_key] = override_get_api_key

def test_checkin_success(client):
    employee_id = "uuid-success"
    attendee_data = {
        settings.COL_NAME: "王大明",
        settings.COL_DEPARTMENT: "工程部",
        settings.COL_TABLE_NUMBER: "A1",
        settings.COL_UNIQUE_ID: employee_id,
        settings.COL_CHECK_IN_STATUS: "FALSE"
    }
    mock_cache_manager.get_attendee.return_value = attendee_data
    mock_cache_manager.update_check_in_status.return_value = {**attendee_data, settings.COL_CHECK_IN_STATUS: "TRUE"}

    response = client.post("/api/check-in", json={"employeeId": employee_id})

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "王大明"
    assert response_json["table_number"] == "A1"
    mock_cache_manager.update_check_in_status.assert_called_with(employee_id)


def test_checkin_user_not_found(client):
    mock_cache_manager.get_attendee.return_value = None
    response = client.post("/api/check-in", json={"employeeId": "uuid-not-found"})
    assert response.status_code == 404

def test_checkin_already_checked_in(client):
    employee_id = "uuid-already-checked-in"
    attendee_data = {
        settings.COL_NAME: "陳小美", settings.COL_UNIQUE_ID: employee_id,
        settings.COL_CHECK_IN_STATUS: "TRUE",
        settings.COL_TABLE_NUMBER: "B2"
    }
    mock_cache_manager.get_attendee.return_value = attendee_data

    response = client.post("/api/check-in", json={"employeeId": employee_id})
    assert response.status_code == 409
    assert response.json()["detail"] == "此人已簽到"
    assert response.json()["table_number"] == "B2"

def test_checkout_success(client):
    employee_id = "uuid-checkout-success"
    attendee_data = {
        settings.COL_NAME: "李中天", settings.COL_DEPARTMENT: "人資部",
        settings.COL_UNIQUE_ID: employee_id,
        settings.COL_CHECK_IN_STATUS: "TRUE",
        settings.COL_CHECK_OUT_STATUS: "FALSE"
    }
    mock_cache_manager.get_attendee.return_value = attendee_data
    mock_cache_manager.update_check_out_status.return_value = {**attendee_data, settings.COL_CHECK_OUT_STATUS: "TRUE"}

    response = client.post("/api/check-out", json={"employeeId": employee_id})
    assert response.status_code == 200
    mock_cache_manager.update_check_out_status.assert_called_with(employee_id)


def test_checkout_not_checked_in(client):
    attendee_data = {settings.COL_CHECK_IN_STATUS: "FALSE"}
    mock_cache_manager.get_attendee.return_value = attendee_data
    response = client.post("/api/check-out", json={"employeeId": "uuid-not-checked-in"})
    assert response.status_code == 400

def test_checkout_already_checked_out(client):
    employee_id = "uuid-already-checked-out"
    attendee_data = {
        settings.COL_NAME: "陳小美",
        settings.COL_UNIQUE_ID: employee_id,
        settings.COL_CHECK_IN_STATUS: "TRUE",
        settings.COL_CHECK_OUT_STATUS: "TRUE"
    }
    mock_cache_manager.get_attendee.return_value = attendee_data
    response = client.post("/api/check-out", json={"employeeId": employee_id})
    assert response.status_code == 409

def test_get_status(client):
    status_data = [
        {settings.COL_CHECK_IN_STATUS: "TRUE", settings.COL_CHECK_OUT_STATUS: "FALSE"},
        {settings.COL_CHECK_IN_STATUS: "TRUE", settings.COL_CHECK_OUT_STATUS: "TRUE"},
        {settings.COL_CHECK_IN_STATUS: "FALSE", settings.COL_CHECK_OUT_STATUS: "FALSE"},
    ]
    mock_cache_manager.get_all_attendees.return_value = status_data
    response = client.get("/api/status")
    assert response.status_code == 200
    assert response.json() == {"total_attendees": 3, "checked_in_count": 2, "checked_out_count": 1}
