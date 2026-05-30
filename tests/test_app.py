from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
original_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(original_activities))
    yield
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    email = "newstudent@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    activity_data = client.get("/activities").json()["Chess Club"]
    assert email in activity_data["participants"]


def test_signup_duplicate_returns_400():
    email = "duplicate@mergington.edu"

    first = client.post("/activities/Chess Club/signup", params={"email": email})
    assert first.status_code == 200

    second = client.post("/activities/Chess Club/signup", params={"email": email})
    assert second.status_code == 400
    assert second.json()["detail"] == "Student is already signed up for this activity"

    activity_data = client.get("/activities").json()["Chess Club"]
    assert activity_data["participants"].count(email) == 1


def test_remove_participant_success():
    email = "michael@mergington.edu"

    response = client.delete("/activities/Chess Club/participants", params={"email": email})
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]

    activity_data = client.get("/activities").json()["Chess Club"]
    assert email not in activity_data["participants"]


def test_remove_participant_not_found_returns_404():
    response = client.delete("/activities/Chess Club/participants", params={"email": "missing@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
