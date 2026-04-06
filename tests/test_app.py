import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_state)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity():
    email = "newstudent@mergington.edu"
    activity = quote("Chess Club", safe="")

    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    email = "michael@mergington.edu"
    activity = quote("Chess Club", safe="")

    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_participant():
    email = "daniel@mergington.edu"
    activity = quote("Chess Club", safe="")

    response = client.delete(f"/activities/{activity}/participants?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_nonexistent_participant_returns_404():
    email = "nonexistent@mergington.edu"
    activity = quote("Chess Club", safe="")

    response = client.delete(f"/activities/{activity}/participants?email={email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_signup_activity_not_found():
    email = "newstudent@mergington.edu"
    activity = quote("Unknown Activity", safe="")

    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_activity_not_found():
    email = "newstudent@mergington.edu"
    activity = quote("Unknown Activity", safe="")

    response = client.delete(f"/activities/{activity}/participants?email={email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
