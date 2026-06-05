import json
import os
import uuid
from datetime import datetime, timezone
from urllib.parse import quote, unquote, urlparse

import httpx
import pika
import pytest


pytestmark = pytest.mark.async_events


def test_duplicate_event_id_creates_single_notification(rabbitmq_url, wait_for_notification):
    event_id = str(uuid.uuid4())
    event = {
        "event_type": "order.paid",
        "event_id": event_id,
        "order_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }

    publish_order_event(rabbitmq_url, event)
    publish_order_event(rabbitmq_url, event)

    notifications = wait_for_notification(event_id=event_id, timeout=12)

    assert len(notifications) == 1
    assert notifications[0]["event_id"] == event_id


def publish_order_event(rabbitmq_url: str, event: dict) -> None:
    management_url = rabbitmq_management_url(rabbitmq_url)
    parsed = urlparse(rabbitmq_url)
    username = unquote(parsed.username or "guest")
    password = unquote(parsed.password or "guest")
    vhost = unquote(parsed.path.lstrip("/") or "/")

    response = httpx.post(
        f"{management_url}/api/exchanges/{quote(vhost, safe='')}/orders.exchange/publish",
        auth=(username, password),
        timeout=10,
        json={
            "routing_key": event["event_type"],
            "payload": json.dumps(event),
            "payload_encoding": "string",
            "properties": {
                "content_type": "application/json",
                "delivery_mode": 2,
                "message_id": event["event_id"],
            },
        },
    )
    response.raise_for_status()
    assert response.json()["routed"] is True


def publish_order_event_over_amqp(rabbitmq_url: str, event: dict) -> None:
    params = pika.URLParameters(rabbitmq_url)
    connection = pika.BlockingConnection(params)
    try:
        channel = connection.channel()
        channel.exchange_declare(exchange="orders.exchange", exchange_type="direct", durable=True)
        channel.basic_publish(
            exchange="orders.exchange",
            routing_key=event["event_type"],
            body=json.dumps(event).encode("utf-8"),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
                message_id=event["event_id"],
            ),
        )
    finally:
        connection.close()


def rabbitmq_management_url(rabbitmq_url: str) -> str:
    configured = os.getenv("RABBITMQ_MANAGEMENT_URL")
    if configured:
        return configured.rstrip("/")

    parsed = urlparse(rabbitmq_url)
    host = parsed.hostname or "localhost"
    return f"http://{host}:15672"
