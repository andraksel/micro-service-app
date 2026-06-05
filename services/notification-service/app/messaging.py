import json
import logging
import os
import threading
import time
from collections.abc import Callable
from typing import Any

import pika


RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
ORDERS_EXCHANGE = os.getenv("ORDERS_EXCHANGE", "orders.exchange")
ORDERS_DLX = os.getenv("ORDERS_DLX", "orders.dlx")
NOTIFICATION_QUEUE = os.getenv("NOTIFICATION_QUEUE", "notification.order-events.queue")
NOTIFICATION_DLQ = os.getenv("NOTIFICATION_DLQ", "notification.order-events.dlq")

logger = logging.getLogger("notification-service")


def _params() -> pika.URLParameters:
    params = pika.URLParameters(RABBITMQ_URL)
    params.heartbeat = 30
    params.blocked_connection_timeout = 10
    return params


def _connect() -> pika.BlockingConnection:
    return pika.BlockingConnection(_params())


def declare_topology(channel: Any) -> None:
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


def setup_rabbitmq(retries: int = 90, delay_seconds: float = 1.0) -> None:
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            with _connect() as connection:
                channel = connection.channel()
                declare_topology(channel)
            return
        except Exception as exc:  # pragma: no cover - startup resilience
            last_error = exc
            time.sleep(delay_seconds)
    raise RuntimeError(f"RabbitMQ is not ready: {last_error!r}")


def is_rabbitmq_ready() -> bool:
    try:
        with _connect() as connection:
            channel = connection.channel()
            declare_topology(channel)
        return True
    except Exception:
        return False


def consume_forever(
    stop_event: threading.Event,
    process_message: Callable[[dict, str | None], None],
    reconnect_delay_seconds: float = 2.0,
) -> None:
    while not stop_event.is_set():
        connection = None
        try:
            connection = _connect()
            channel = connection.channel()
            declare_topology(channel)
            channel.basic_qos(prefetch_count=1)
            logger.info("rabbitmq_consumer_started", extra={"event": "rabbitmq.consumer_started"})

            for method, properties, body in channel.consume(NOTIFICATION_QUEUE, inactivity_timeout=1):
                if stop_event.is_set():
                    break
                if method is None:
                    continue
                try:
                    payload = json.loads(body.decode("utf-8"))
                    process_message(payload, getattr(properties, "correlation_id", None))
                    channel.basic_ack(method.delivery_tag)
                except Exception as exc:
                    logger.exception(
                        "message_processing_failed",
                        extra={"event": "rabbitmq.message_failed", "error": str(exc)},
                    )
                    channel.basic_nack(method.delivery_tag, requeue=False)
            channel.cancel()
        except Exception as exc:
            logger.warning("rabbitmq_consumer_error", extra={"event": "rabbitmq.consumer_error", "error": str(exc)})
            time.sleep(reconnect_delay_seconds)
        finally:
            if connection is not None and connection.is_open:
                connection.close()
