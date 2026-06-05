import os
from time import perf_counter

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest


SERVICE_NAME = os.getenv("SERVICE_NAME", "unknown-service")

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests.",
    ["service", "method", "path", "status_code"],
)
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["service", "method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)
HTTP_EXCEPTIONS = Counter(
    "http_request_exceptions_total",
    "Unhandled HTTP request exceptions.",
    ["service", "method", "path"],
)


def setup_metrics(app: FastAPI) -> None:
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)

        start_time = perf_counter()
        status_code = "500"
        try:
            response = await call_next(request)
            status_code = str(response.status_code)
            return response
        except Exception:
            HTTP_EXCEPTIONS.labels(SERVICE_NAME, request.method, _route_path(request)).inc()
            raise
        finally:
            path = _route_path(request)
            HTTP_REQUESTS.labels(SERVICE_NAME, request.method, path, status_code).inc()
            HTTP_REQUEST_DURATION.labels(SERVICE_NAME, request.method, path).observe(perf_counter() - start_time)

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def _route_path(request: Request) -> str:
    route = request.scope.get("route")
    return getattr(route, "path", request.url.path)
