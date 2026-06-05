import pytest


pytestmark = pytest.mark.api


def test_create_and_get_product(client):
    create_response = client.post(
        "/api/products",
        json={
            "name": "API Test Product",
            "description": "Product for API test",
            "price": "24.99",
            "currency": "USD",
            "stock": 5,
        },
    )

    assert create_response.status_code == 201, create_response.text
    created = create_response.json()

    get_response = client.get(f"/api/products/{created['id']}")
    assert get_response.status_code == 200, get_response.text
    assert get_response.json()["id"] == created["id"]
    assert get_response.headers["x-cache"] == "MISS"


def test_create_product_rejects_negative_stock(client):
    response = client.post(
        "/api/products",
        json={
            "name": "Invalid Stock Product",
            "description": "Invalid",
            "price": "10.00",
            "currency": "USD",
            "stock": -1,
        },
    )

    assert response.status_code == 422
