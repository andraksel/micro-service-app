import pytest


pytestmark = pytest.mark.api


def test_payment_authorization_success(client, set_payment_mode):
    set_payment_mode("success")

    response = client.post(
        "/api/payments/authorize",
        json={"order_id": "order-api-test", "amount": "9.99", "currency": "USD"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "authorized"
    assert body["order_id"] == "order-api-test"


def test_payment_authorization_failure_mode(client, set_payment_mode):
    set_payment_mode("failure")

    response = client.post(
        "/api/payments/authorize",
        json={"order_id": "order-api-test-failure", "amount": "9.99", "currency": "USD"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "declined"
    set_payment_mode("success")
