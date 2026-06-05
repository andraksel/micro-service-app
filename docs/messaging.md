# Messaging

RabbitMQ is used for asynchronous order events.

## Exchange

```text
orders.exchange
```

Type:

```text
direct
```

## Routing Keys

```text
order.created
order.paid
order.cancelled
```

## Queues

```text
notification.order-events.queue
notification.order-events.dlq
```

`notification.order-events.queue` is durable and bound to all order routing keys.

The main queue has dead-letter configuration:

```text
x-dead-letter-exchange: orders.dlx
x-dead-letter-routing-key: notification.order-events.dlq
```

## Event Payload

```json
{
  "event_type": "order.paid",
  "event_id": "uuid",
  "order_id": "uuid",
  "user_id": "uuid",
  "occurred_at": "datetime"
}
```

## Idempotency

`notification-service` stores `event_id` with a unique constraint.

If a duplicate message arrives:

1. the existing notification is detected
2. no new record is created
3. the duplicate message is acknowledged

This gives QA engineers a concrete duplicate-message scenario to test.

## Acknowledgment Behavior

Messages are acknowledged only after successful processing. Invalid or failed messages are negatively acknowledged with `requeue=False`, causing RabbitMQ to dead-letter them.
