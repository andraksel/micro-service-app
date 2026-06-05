import pytest


pytestmark = pytest.mark.api


def test_create_and_get_user(client, unique_email):
    create_response = client.post(
        "/api/users",
        json={"email": unique_email, "full_name": "Ada Lovelace"},
    )

    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created["email"] == unique_email
    assert created["status"] == "active"

    get_response = client.get(f"/api/users/{created['id']}")
    assert get_response.status_code == 200, get_response.text
    assert get_response.json()["id"] == created["id"]
    assert "x-request-id" in get_response.headers


def test_create_user_rejects_invalid_email(client):
    response = client.post(
        "/api/users",
        json={"email": "not-an-email", "full_name": "Invalid Email"},
    )

    assert response.status_code == 422


def test_user_email_must_be_unique(client, unique_email):
    payload = {"email": unique_email, "full_name": "Unique User"}
    first = client.post("/api/users", json=payload)
    second = client.post("/api/users", json=payload)

    assert first.status_code == 201, first.text
    assert second.status_code == 409
