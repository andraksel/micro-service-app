# QA Learning Guide

Follow this path to learn the system incrementally.

## 1. Run The System

```bash
docker compose up --build
```

## 2. Check Health

Open the QA Dashboard:

```text
http://localhost:8080
```

The dashboard shows service readiness and lets you run the main user/product/order/payment/notification flow from the browser.

```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/users/ready
curl http://localhost:8080/api/products/ready
curl http://localhost:8080/api/orders/ready
```

## 3. Create A User

```bash
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"email":"qa-user@example.com","full_name":"QA User"}'
```

## 4. Create A Product

```bash
curl -X POST http://localhost:8080/api/products \
  -H "Content-Type: application/json" \
  -d '{"name":"QA Product","description":"Training product","price":"15.00","currency":"USD","stock":10}'
```

## 5. Create An Order

Use the user and product IDs returned by the previous calls:

```bash
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id":"USER_ID","items":[{"product_id":"PRODUCT_ID","quantity":1}]}'
```

## 6. Observe RabbitMQ

Open:

```text
http://localhost:15672
```

Check `orders.exchange` and `notification.order-events.queue`.

## 7. Observe Metrics

Open Grafana:

```text
http://localhost:3000
admin / admin
```

Open Prometheus:

```text
http://localhost:9090
```

Query examples:

```promql
sum by (service) (rate(http_requests_total[1m]))
histogram_quantile(0.95, sum by (le, service) (rate(http_request_duration_seconds_bucket[5m])))
```

## 8. Observe Notifications

```bash
curl http://localhost:8080/api/notifications
```

## 9. Run API Tests

```bash
pytest -m api
```

## 10. Run Integration Tests

```bash
pytest -m integration
```

## 11. Simulate Payment Failure

```bash
curl -X POST http://localhost:8080/api/payments/test-controls/payment-mode \
  -H "Content-Type: application/json" \
  -d '{"mode":"failure"}'
```

Create an order and verify it becomes `payment_failed`.

## 12. Simulate Payment Timeout

```bash
curl -X POST http://localhost:8080/api/payments/test-controls/payment-mode \
  -H "Content-Type: application/json" \
  -d '{"mode":"timeout"}'
```

Create an order and verify `order-service` handles timeout.

## 13. Inspect Logs With Request ID

```bash
docker compose logs -f order-service
docker compose logs -f user-service
docker compose logs -f product-service
```

Send requests with:

```text
X-Request-ID: qa-learning-001
```

## 14. Test Redis Cache

Call the same product twice:

```bash
curl -i http://localhost:8080/api/products/PRODUCT_ID
curl -i http://localhost:8080/api/products/PRODUCT_ID
```

Verify:

```text
X-Cache: MISS
X-Cache: HIT
```

## 15. Break A Service

Stop one dependency and observe behavior:

```bash
docker compose stop payment-service
```

Then create an order and inspect the response and logs.

Start it again:

```bash
docker compose start payment-service
```
