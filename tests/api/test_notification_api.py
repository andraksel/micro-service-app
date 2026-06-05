import pytest


pytestmark = pytest.mark.api


def test_notifications_endpoint_returns_list(client):
    response = client.get("/api/notifications")

    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)
