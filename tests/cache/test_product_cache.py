import pytest


pytestmark = pytest.mark.cache


def test_product_cache_hit_and_invalidation(client, create_product):
    product = create_product(stock=6, price="20.00")

    first_get = client.get(f"/api/products/{product['id']}")
    second_get = client.get(f"/api/products/{product['id']}")

    assert first_get.status_code == 200, first_get.text
    assert second_get.status_code == 200, second_get.text
    assert first_get.headers["x-cache"] == "MISS"
    assert second_get.headers["x-cache"] == "HIT"

    patch_response = client.patch(f"/api/products/{product['id']}", json={"price": "21.00"})
    assert patch_response.status_code == 200, patch_response.text

    after_update_get = client.get(f"/api/products/{product['id']}")
    cached_after_update_get = client.get(f"/api/products/{product['id']}")

    assert after_update_get.headers["x-cache"] == "MISS"
    assert cached_after_update_get.headers["x-cache"] == "HIT"
    assert str(after_update_get.json()["price"]) in ("21.00", "21.0")
