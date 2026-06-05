# Architecture

`microservices-qa-lab` is a local, Docker Compose based system designed for QA automation practice.

## Why These Services Exist

`user-service` owns user data and status. `order-service` depends on this service to verify that a user exists and is active.

`product-service` owns product catalog and stock data. It also owns Redis cache behavior so QA engineers can test cache hit, miss, and invalidation scenarios.

`order-service` owns order lifecycle. It demonstrates synchronous service-to-service communication by calling user, product, and payment services, then demonstrates asynchronous communication by publishing RabbitMQ events.

`payment-service` simulates an external provider. It has local-only test controls so failure and timeout behavior can be tested deterministically.

`notification-service` consumes order events and stores notification records. It demonstrates eventual consistency and idempotent async processing.

## Separate Database Ownership

Each persistent business service has its own PostgreSQL database:

- `user-db`
- `product-db`
- `order-db`
- `notification-db`

This mirrors microservice data ownership. Tests should use APIs for normal setup and assertions unless a scenario explicitly teaches database verification.

## Synchronous Communication

`order-service` calls:

- `GET /users/{user_id}` on `user-service`
- `GET /products/{product_id}` on `product-service`
- `POST /payments/authorize` on `payment-service`

The request ID is propagated with the `X-Request-ID` header.

## Asynchronous Communication

`order-service` publishes:

- `order.created`
- `order.paid`
- `order.cancelled`

`notification-service` consumes those events from RabbitMQ and creates records after processing.

## Redis

Redis is used only by `product-service` for `GET /products/{product_id}`. The documented key format is:

```text
product:{product_id}
```

Updates and deletes invalidate the key.

## Nginx

Nginx provides one black-box testing surface:

```text
http://localhost:8080
```

The individual service ports are exposed for debugging, but tests should prefer the gateway.
