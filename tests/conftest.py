import os
import uuid
from collections.abc import Callable, Generator

import httpx
import pytest

from tests.utils.polling import wait_until


@pytest.fixture(scope="session")
def gateway_url() -> str:
    return os.getenv("GATEWAY_URL", "http://localhost:8080").rstrip("/")


@pytest.fixture(scope="session")
def rabbitmq_url() -> str:
    return os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")


@pytest.fixture(scope="session")
def client(gateway_url: str) -> Generator[httpx.Client, None, None]:
    headers = {"X-Request-ID": f"pytest-session-{uuid.uuid4()}"}
    with httpx.Client(base_url=gateway_url, timeout=12, headers=headers) as http_client:
        yield http_client


@pytest.fixture
def unique_email() -> str:
    return f"qa-{uuid.uuid4().hex}@example.com"


@pytest.fixture
def create_user(client: httpx.Client) -> Callable[..., dict]:
    def _create_user(status: str = "active") -> dict:
        response = client.post(
            "/api/users",
            json={"email": f"qa-{uuid.uuid4().hex}@example.com", "full_name": "QA Test User"},
        )
        assert response.status_code == 201, response.text
        user = response.json()

        if status != "active":
            status_response = client.patch(f"/api/users/{user['id']}/status", json={"status": status})
            assert status_response.status_code == 200, status_response.text
            user = status_response.json()

        return user

    return _create_user


@pytest.fixture
def create_product(client: httpx.Client) -> Callable[..., dict]:
    def _create_product(stock: int = 10, price: str = "15.50", status: str = "active") -> dict:
        response = client.post(
            "/api/products",
            json={
                "name": f"QA Product {uuid.uuid4().hex[:8]}",
                "description": "Created by pytest fixture",
                "price": price,
                "currency": "USD",
                "stock": stock,
                "status": status,
            },
        )
        assert response.status_code == 201, response.text
        return response.json()

    return _create_product


@pytest.fixture
def set_payment_mode(client: httpx.Client) -> Callable[[str], dict]:
    def _set_payment_mode(mode: str) -> dict:
        response = client.post("/api/payments/test-controls/payment-mode", json={"mode": mode})
        assert response.status_code == 200, response.text
        return response.json()

    return _set_payment_mode


@pytest.fixture
def create_order(client: httpx.Client) -> Callable[..., dict]:
    def _create_order(user_id: str, product_id: str, quantity: int = 1, expected_status_code: int = 201) -> dict:
        response = client.post(
            "/api/orders",
            json={"user_id": user_id, "items": [{"product_id": product_id, "quantity": quantity}]},
        )
        assert response.status_code == expected_status_code, response.text
        return response.json()

    return _create_order


@pytest.fixture
def wait_for_notification(client: httpx.Client) -> Callable[..., list[dict]]:
    def _wait_for_notification(
        *,
        order_id: str | None = None,
        event_id: str | None = None,
        event_type: str | None = None,
        timeout: float = 12,
    ) -> list[dict]:
        def condition() -> list[dict] | bool:
            params = {}
            if order_id:
                params["order_id"] = order_id
            if event_id:
                params["event_id"] = event_id

            response = client.get("/api/notifications", params=params)
            response.raise_for_status()
            notifications = response.json()
            if event_type:
                notifications = [item for item in notifications if item["event_type"] == event_type]
            return notifications or False

        return wait_until(condition, timeout=timeout, interval=0.5)

    return _wait_for_notification
