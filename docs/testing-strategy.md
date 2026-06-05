# Testing Strategy

The test suite is intentionally organized by what a QA Automation Engineer should learn from each layer.

## API Tests

Marker: `api`

Covers direct resource behavior through the gateway:

- user creation, validation, and uniqueness
- product creation and validation
- payment authorization behavior
- notification API availability

## Integration Tests

Marker: `integration`

Covers cross-service business flow:

1. create user
2. create product
3. create order
4. payment succeeds
5. order becomes `paid`
6. `order.paid` notification eventually appears

## Contract Tests

Marker: `contract`

Uses Pydantic models to validate shapes consumed across service boundaries:

- user response consumed by `order-service`
- product response consumed by `order-service`
- order event consumed by `notification-service`

## Async Event Tests

Marker: `async_events`

Covers RabbitMQ and eventual consistency:

- publish an order event
- wait until notification appears
- publish duplicate `event_id`
- verify only one notification is created

Tests use polling, not fixed sleeps.

## Cache Tests

Marker: `cache`

Covers Redis behavior:

- first product retrieval returns `X-Cache: MISS`
- second retrieval returns `X-Cache: HIT`
- update invalidates cache
- next retrieval returns `MISS` again

## Resilience Tests

Marker: `resilience`

Covers controlled dependency failure:

- payment failure produces `payment_failed` order
- payment timeout produces `payment_failed` order
- blocked user cannot create an order

The `payment-service` test-control endpoint is local-only and exists for deterministic QA scenarios.
