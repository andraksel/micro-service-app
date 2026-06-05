# Troubleshooting

## Check Container Status

```bash
docker compose ps
```

## View Logs

```bash
docker compose logs -f order-service
docker compose logs -f notification-service
docker compose logs -f rabbitmq
```

## Reset Everything

```bash
docker compose down -v
docker compose up --build
```

## Port Conflicts

The compose file exposes:

- `8080` gateway
- `15672` RabbitMQ UI
- `5672` RabbitMQ AMQP
- `6379` Redis
- `8001` to `8005` service debug ports

If a port is already used locally, change or remove the host-side port mapping in `docker-compose.yml`.

PostgreSQL databases are intentionally not published to the host by default. Services reach them through the Docker Compose network.

## RabbitMQ UI

Open:

```text
http://localhost:15672
```

Credentials:

```text
guest / guest
```

## Gateway Is Up But Tests Fail

Check service readiness:

```bash
curl http://localhost:8080/api/users/ready
curl http://localhost:8080/api/products/ready
curl http://localhost:8080/api/orders/ready
curl http://localhost:8080/api/notifications/ready
```

## Payment Timeout Test Is Slow

This is expected. The timeout mode makes `payment-service` sleep longer than `order-service` HTTP timeout so the order can transition to `payment_failed`.
