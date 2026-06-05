# order-service

Owns order lifecycle and demonstrates synchronous orchestration plus asynchronous event publishing.

Dependencies:

- user-service over HTTP
- product-service over HTTP
- payment-service over HTTP
- RabbitMQ for `order.created`, `order.paid`, and `order.cancelled` events

Configuration:

```text
USER_SERVICE_BASE_URL=http://user-service:8000
PRODUCT_SERVICE_BASE_URL=http://product-service:8000
PAYMENT_SERVICE_BASE_URL=http://payment-service:8000
HTTP_TIMEOUT_SECONDS=2
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
```
