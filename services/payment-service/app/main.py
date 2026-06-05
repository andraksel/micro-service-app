import asyncio
import logging
import os
import random
import uuid

from fastapi import FastAPI, HTTPException, status

from app.logging_config import RequestIdMiddleware, configure_logging
from app.metrics import setup_metrics
from app.schemas import PaymentAuthorizeRequest, PaymentMode, PaymentModeResponse, PaymentModeUpdate, PaymentResponse


configure_logging()
logger = logging.getLogger("payment-service")

app = FastAPI(title="payment-service", version="1.0.0")
app.add_middleware(RequestIdMiddleware)
setup_metrics(app)

payment_mode: PaymentMode = os.getenv("PAYMENT_MODE", "success")  # type: ignore[assignment]
payments: dict[str, PaymentResponse] = {}


@app.on_event("startup")
def startup() -> None:
    logger.info("service_started", extra={"event": "service.started", "payment_mode": payment_mode})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "payment-service"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready", "service": "payment-service"}


@app.post("/test-controls/payment-mode", response_model=PaymentModeResponse)
def set_payment_mode(payload: PaymentModeUpdate) -> PaymentModeResponse:
    global payment_mode
    payment_mode = payload.mode
    logger.info("payment_mode_changed", extra={"event": "payment.mode_changed", "payment_mode": payment_mode})
    return PaymentModeResponse(mode=payment_mode)


@app.post("/payments/authorize", response_model=PaymentResponse)
async def authorize_payment(payload: PaymentAuthorizeRequest) -> PaymentResponse:
    mode = payment_mode
    if mode == "random":
        mode = random.choice(["success", "failure"])  # nosec - deterministic security is irrelevant in this lab

    if mode == "timeout":
        await asyncio.sleep(float(os.getenv("PAYMENT_TIMEOUT_SLEEP_SECONDS", "3.5")))
        status_value = "timeout_simulated"
    elif mode == "failure":
        status_value = "declined"
    elif mode == "success":
        status_value = "authorized"
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="invalid payment mode")

    payment_id = str(uuid.uuid4())
    payment = PaymentResponse(
        payment_id=payment_id,
        order_id=payload.order_id,
        status=status_value,
        amount=payload.amount,
        currency=payload.currency,
    )
    payments[payment_id] = payment
    logger.info(
        "payment_authorized",
        extra={"event": "payment.authorized", "payment_mode": payment_mode, "order_id": payload.order_id},
    )
    return payment


@app.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: str) -> PaymentResponse:
    payment = payments.get(payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="payment not found")
    return payment
