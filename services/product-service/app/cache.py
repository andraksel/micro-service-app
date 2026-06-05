import json
import os
import time
from typing import Any

import redis


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "60"))

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def product_cache_key(product_id: str) -> str:
    return f"product:{product_id}"


def wait_for_redis(retries: int = 30, delay_seconds: float = 1.0) -> None:
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            redis_client.ping()
            return
        except Exception as exc:  # pragma: no cover - startup resilience
            last_error = exc
            time.sleep(delay_seconds)
    raise RuntimeError(f"Redis is not ready: {last_error}")


def is_redis_ready() -> bool:
    try:
        redis_client.ping()
        return True
    except Exception:
        return False


def get_cached_product(product_id: str) -> dict[str, Any] | None:
    try:
        raw = redis_client.get(product_cache_key(product_id))
    except redis.RedisError:
        return None
    if raw is None:
        return None
    return json.loads(raw)


def set_cached_product(product_id: str, payload: dict[str, Any]) -> None:
    try:
        redis_client.setex(product_cache_key(product_id), CACHE_TTL_SECONDS, json.dumps(payload, default=str))
    except redis.RedisError:
        return


def invalidate_product_cache(product_id: str) -> None:
    try:
        redis_client.delete(product_cache_key(product_id))
    except redis.RedisError:
        return
