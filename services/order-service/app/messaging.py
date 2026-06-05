import json
import os
import time
from datetime import datetime
from typing import Any

import pika


RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
ORDERS_EXCHANGE = os.getenv("ORDERS_EXCHANGE", "orders.exchange")
ORDERS_DLX = os.getenv("ORDERS_DLX", "orders.dlx")
NOTIFICATION_QUEUE = os.getenv("NOTIFICATION_QUEUE", "notification.order-events.queue")
NOTIFICATION_DLQ = os.getenv("NOTIFICATION_DLQ", "notification.order-events.dlq")


def _params() -> pika.URLParameters:
    params = pika.URLParameters(RABBITMQ_URL)
    params.heartbeat = 30
    params.blocked_connection_timeout = 10
    return params


def _connect() -> pika.BlockingConnection:
    return pika.BlockingConnection(_params())


def setup_rabbitmq(retries: int = 90, delay_seconds: float = 1.0) -> None:
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            with _connect() as connection:
                channel = connection.channel()
                _declare_topology(channel)
            return
        except Exception as exc:  # pragma: no cover - startup resilience
            last_error = exc
            time.sleep(delay_seconds)
    raise RuntimeError(f"RabbitMQ is not ready: {last_error!r}")


def _declare_topology(channel: Any) -> None:
    channel.exchange_declare(exchange=ORDERS_EXCHANGE, exchange_type="direct", durable=True)
    channel.exchange_declare(exchange=ORDERS_DLX, exchange_type="direct", durable=True)
    channel.queue_declare(queue=NOTIFICATION_DLQ, durable=True)
    channel.queue_bind(exchange=ORDERS_DLX, queue=NOTIFICATION_DLQ, routing_key=NOTIFICATION_DLQ)
    channel.queue_declare(
        queue=NOTIFICATION_QUEUE,
        durable=True,
        arguments={
            "x-dead-letter-exchange": ORDERS_DLX,
            "x-dead-letter-routing-key": NOTIFICATION_DLQ,
        },
    )
    for routing_key in ("order.created", "order.paid", "order.cancelled"):
        channel.queue_bind(exchange=ORDERS_EXCHANGE, queue=NOTIFICATION_QUEUE, routing_key=routing_key)


def is_rabbitmq_ready() -> bool:
    try:
        with _connect() as connection:
            channel = connection.channel()
            _declare_topology(channel)
        return True
    except Exception:
        return False


def publish_order_event(event: dict[str, Any], request_id: str) -> None:
    body = json.dumps(event, default=_json_default).encode("utf-8")
    with _connect() as connection:
        channel = connection.channel()
        _declare_topology(channel)
        channel.basic_publish(
            exchange=ORDERS_EXCHANGE,
            routing_key=event["event_type"],
            body=body,
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
                message_id=event["event_id"],
                correlation_id=request_id,
                timestamp=int(time.time()),
            ),
            mandatory=False,
        )


def _json_default(value: Any) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)
