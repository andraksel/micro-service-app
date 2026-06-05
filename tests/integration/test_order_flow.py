import pytest


pytestmark = [pytest.mark.integration, pytest.mark.e2e]


def test_paid_order_flow_creates_notification(
    create_user,
    create_product,
    create_order,
    set_payment_mode,
    wait_for_notification,
):
    set_payment_mode("success")
    user = create_user()
    product = create_product(stock=3, price="12.00")

    order = create_order(user["id"], product["id"], quantity=2)

    assert order["status"] == "paid"
    assert order["total_amount"] in ("24.00", 24.0, "24.0")

    notifications = wait_for_notification(order_id=order["id"], event_type="order.paid")
    assert len(notifications) == 1
    assert notifications[0]["order_id"] == order["id"]
