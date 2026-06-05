import logging
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import get_db, init_db, is_database_ready
from app.logging_config import RequestIdMiddleware, configure_logging
from app.messaging import is_rabbitmq_ready, publish_order_event, setup_rabbitmq
from app.metrics import setup_metrics
from app.models import Order, OrderItem
from app.schemas import (
    OrderCreate,
    OrderEventPayload,
    OrderResponse,
    PaymentAuthorizeRequest,
    PaymentContract,
    ProductContract,
    UserContract,
)


configure_logging()
logger = logging.getLogger("order-service")

USER_SERVICE_BASE_URL = os.getenv("USER_SERVICE_BASE_URL", "http://localhost:8001")
PRODUCT_SERVICE_BASE_URL = os.getenv("PRODUCT_SERVICE_BASE_URL", "http://localhost:8002")
PAYMENT_SERVICE_BASE_URL = os.getenv("PAYMENT_SERVICE_BASE_URL", "http://localhost:8003")
HTTP_TIMEOUT_SECONDS = float(os.getenv("HTTP_TIMEOUT_SECONDS", "2"))

app = FastAPI(title="order-service", version="1.0.0")
app.add_middleware(RequestIdMiddleware)
setup_metrics(app)


@app.on_event("startup")
def startup() -> None:
    init_db()
    setup_rabbitmq()
    logger.info("service_started", extra={"event": "service.started"})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "order-service"}


@app.get("/ready")
def ready() -> dict[str, str]:
    if not is_database_ready():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="database is not ready")
    if not is_rabbitmq_ready():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="rabbitmq is not ready")
    return {"status": "ready", "service": "order-service"}


@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, request: Request, db: Session = Depends(get_db)) -> Order:
    request_id = request.state.request_id
    user = fetch_user(payload.user_id, request_id)
    if user.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user is not active")

    product_contracts: list[tuple[ProductContract, int]] = []
    for item in payload.items:
        product = fetch_product(item.product_id, request_id)
        if product.status != "active":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"product {product.id} is not active")
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"product {product.id} has insufficient stock",
            )
        product_contracts.append((product, item.quantity))

    total_amount = sum((product.price * quantity for product, quantity in product_contracts), Decimal("0.00"))
    order = Order(user_id=user.id, total_amount=total_amount, currency="USD", status="created")
    order.items = [
        OrderItem(product_id=product.id, quantity=quantity, unit_price=product.price)
        for product, quantity in product_contracts
    ]
    db.add(order)
    db.commit()
    db.refresh(order)

    publish_event("order.created", order, request_id)

    payment = authorize_payment(order, request_id)
    if payment is not None and payment.status == "authorized":
        order.status = "paid"
        db.commit()
        db.refresh(order)
        publish_event("order.paid", order, request_id)
    else:
        order.status = "payment_failed"
        db.commit()
        db.refresh(order)

    logger.info("order_created", extra={"event": "order.created", "order_id": order.id})
    return order


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, db: Session = Depends(get_db)) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
    return order


@app.get("/orders", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db)) -> list[Order]:
    return list(db.query(Order).order_by(Order.created_at.desc()).all())


@app.patch("/orders/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: str, request: Request, db: Session = Depends(get_db)) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
    if order.status == "cancelled":
        return order

    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    publish_event("order.cancelled", order, request.state.request_id)
    logger.info("order_cancelled", extra={"event": "order.cancelled", "order_id": order.id})
    return order


def fetch_user(user_id: str, request_id: str) -> UserContract:
    url = f"{USER_SERVICE_BASE_URL}/users/{user_id}"
    data = dependency_get(url, "user-service", request_id)
    try:
        return UserContract.model_validate(data)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"user contract violation: {exc.errors()}")


def fetch_product(product_id: str, request_id: str) -> ProductContract:
    url = f"{PRODUCT_SERVICE_BASE_URL}/products/{product_id}"
    data = dependency_get(url, "product-service", request_id)
    try:
        return ProductContract.model_validate(data)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"product contract violation: {exc.errors()}")


def dependency_get(url: str, dependency: str, request_id: str) -> dict:
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT_SECONDS, headers={"X-Request-ID": request_id}) as client:
            response = client.get(url)
    except httpx.TimeoutException:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=f"{dependency} timed out")
    except httpx.HTTPError as exc:
        logger.warning(
            "dependency_http_error",
            extra={"event": "dependency.http_error", "dependency": dependency, "error": str(exc)},
        )
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"{dependency} unavailable")

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{dependency} resource not found")
    if response.status_code >= 500:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"{dependency} returned server error")
    if response.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.text)
    return response.json()


def authorize_payment(order: Order, request_id: str) -> PaymentContract | None:
    payload = PaymentAuthorizeRequest(order_id=order.id, amount=order.total_amount, currency=order.currency)
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT_SECONDS, headers={"X-Request-ID": request_id}) as client:
            response = client.post(f"{PAYMENT_SERVICE_BASE_URL}/payments/authorize", json=payload.model_dump(mode="json"))
    except httpx.TimeoutException:
        logger.warning(
            "payment_timeout",
            extra={"event": "payment.timeout", "dependency": "payment-service", "order_id": order.id},
        )
        return None
    except httpx.HTTPError as exc:
        logger.warning(
            "payment_unavailable",
            extra={
                "event": "payment.unavailable",
                "dependency": "payment-service",
                "order_id": order.id,
                "error": str(exc),
            },
        )
        return None

    if response.status_code >= 500:
        logger.warning(
            "payment_server_error",
            extra={"event": "payment.server_error", "dependency": "payment-service", "order_id": order.id},
        )
        return None
    if response.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.text)

    try:
        return PaymentContract.model_validate(response.json())
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"payment contract violation: {exc.errors()}")


def publish_event(event_type: str, order: Order, request_id: str) -> None:
    event = OrderEventPayload(
        event_type=event_type,  # type: ignore[arg-type]
        event_id=str(uuid.uuid4()),
        order_id=order.id,
        user_id=order.user_id,
        occurred_at=datetime.now(timezone.utc),
    )
    publish_order_event(event.model_dump(mode="json"), request_id)
    logger.info("order_event_published", extra={"event": event_type, "order_id": order.id})
