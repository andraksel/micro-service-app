import time
from collections.abc import Callable
from typing import TypeVar


T = TypeVar("T")


def wait_until(condition: Callable[[], T | bool], timeout: float = 10, interval: float = 0.5) -> T:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            result = condition()
            if result:
                return result  # type: ignore[return-value]
        except Exception as exc:
            last_error = exc
        time.sleep(interval)

    detail = f" Last error: {last_error}" if last_error else ""
    raise AssertionError(f"condition was not met within {timeout} seconds.{detail}")
