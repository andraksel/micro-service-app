import pytest


pytestmark = pytest.mark.api


def test_service_metrics_are_exposed_through_gateway(client):
    services = [
        ("/api/users/ready", "/api/users/metrics", "user-service"),
        ("/api/products/ready", "/api/products/metrics", "product-service"),
        ("/api/orders/ready", "/api/orders/metrics", "order-service"),
        ("/api/payments/ready", "/api/payments/metrics", "payment-service"),
        ("/api/notifications/ready", "/api/notifications/metrics", "notification-service"),
    ]

    for ready_path, metrics_path, service_name in services:
        ready = client.get(ready_path)
        assert ready.status_code == 200, ready.text

        metrics = client.get(metrics_path)
        assert metrics.status_code == 200, metrics.text
        assert "http_requests_total" in metrics.text
        assert f'service="{service_name}"' in metrics.text
