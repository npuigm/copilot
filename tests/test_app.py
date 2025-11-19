import copy

from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Keep tests isolated by restoring the in-memory DB after each test
    orig = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(orig)


def test_get_activities():
    client = TestClient(app)
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    # Ensure a few known activities exist
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_and_remove_participant():
    client = TestClient(app)
    activity = "Chess Club"
    email = "testuser@example.com"

    # Ensure not present initially
    res = client.get("/activities")
    assert email not in res.json()[activity]["participants"]

    # Sign up
    res = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert res.status_code == 200
    assert f"Signed up {email}" in res.json()["message"]

    # Verify present
    res = client.get("/activities")
    assert email in res.json()[activity]["participants"]

    # Remove participant
    res = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert res.status_code == 200
    assert f"Removed {email}" in res.json()["message"]

    # Verify removed
    res = client.get("/activities")
    assert email not in res.json()[activity]["participants"]


def test_remove_nonexistent_participant_returns_404():
    client = TestClient(app)
    activity = "Chess Club"
    email = "nonexistent@example.com"

    res = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert res.status_code == 404
    assert res.json()["detail"] == "Participant not found"
