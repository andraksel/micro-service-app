import pytest


pytestmark = pytest.mark.resilience


def test_payment_failure_marks_order_payment_failed(create_user, create_product, create_order, set_payment_mode):
    set_payment_mode("failure")
    user = create_user()
    product = create_product(stock=2)

    order = create_order(user["id"], product["id"])

    assert order["status"] == "payment_failed"
    set_payment_mode("success")


def test_payment_timeout_marks_order_payment_failed(create_user, create_product, create_order, set_payment_mode):
    set_payment_mode("timeout")
    user = create_user()
    product = create_product(stock=2)

    order = create_order(user["id"], product["id"])

    assert order["status"] == "payment_failed"
    set_payment_mode("success")


def test_blocked_user_cannot_create_order(client, create_user, create_product, set_payment_mode):
    set_payment_mode("success")
    user = create_user(status="blocked")
    product = create_product(stock=2)

    response = client.post(
        "/api/orders",
        json={"user_id": user["id"], "items": [{"product_id": product["id"], "quantity": 1}]},
    )

    assert response.status_code == 400
    assert "user is not active" in response.text
