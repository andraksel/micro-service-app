# notification-service

Consumes order events from RabbitMQ and stores notification records.

## Idempotency

`event_id` is unique in the notification database. Duplicate messages with the same `event_id` are acknowledged without creating another notification.

## Endpoints

- `GET /notifications`
- `GET /notifications/{notification_id}`
- `GET /health`
- `GET /ready`
