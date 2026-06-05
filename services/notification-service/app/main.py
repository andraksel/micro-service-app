import logging
import threading

from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db, init_db, is_database_ready
from app.logging_config import RequestIdMiddleware, configure_logging
from app.messaging import consume_forever, is_rabbitmq_ready, setup_rabbitmq
from app.metrics import setup_metrics
from app.models import Notification
from app.schemas import NotificationResponse, OrderEventPayload


configure_logging()
logger = logging.getLogger("notification-service")

app = FastAPI(title="notification-service", version="1.0.0")
app.add_middleware(RequestIdMiddleware)
setup_metrics(app)

stop_consumer_event = threading.Event()
consumer_thread: threading.Thread | None = None


@app.on_event("startup")
def startup() -> None:
    global consumer_thread
    init_db()
    setup_rabbitmq()
    stop_consumer_event.clear()
    consumer_thread = threading.Thread(
        target=consume_forever,
        args=(stop_consumer_event, process_order_event),
        daemon=True,
    )
    consumer_thread.start()
    logger.info("service_started", extra={"event": "service.started"})


@app.on_event("shutdown")
def shutdown() -> None:
    stop_consumer_event.set()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "notification-service"}


@app.get("/ready")
def ready() -> dict[str, str]:
    if not is_database_ready():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="database is not ready")
    if not is_rabbitmq_ready():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="rabbitmq is not ready")
    return {"status": "ready", "service": "notification-service"}


@app.get("/notifications", response_model=list[NotificationResponse])
def list_notifications(
    event_id: str | None = Query(default=None),
    order_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[Notification]:
    query = db.query(Notification)
    if event_id:
        query = query.filter(Notification.event_id == event_id)
    if order_id:
        query = query.filter(Notification.order_id == order_id)
    return list(query.order_by(Notification.created_at.desc()).all())


@app.get("/notifications/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: str, db: Session = Depends(get_db)) -> Notification:
    notification = db.get(Notification, notification_id)
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="notification not found")
    return notification


def process_order_event(raw_payload: dict, request_id: str | None) -> None:
    try:
        event = OrderEventPayload.model_validate(raw_payload)
    except ValidationError as exc:
        logger.warning("invalid_event_payload", extra={"event": "event.invalid", "error": str(exc)})
        raise

    db = SessionLocal()
    try:
        existing = db.query(Notification).filter(Notification.event_id == event.event_id).one_or_none()
        if existing is not None:
            logger.info(
                "duplicate_event_ignored",
                extra={"event": "event.duplicate_ignored", "event_id": event.event_id, "order_id": event.order_id},
            )
            return

        notification = Notification(
            event_id=event.event_id,
            event_type=event.event_type,
            order_id=event.order_id,
            user_id=event.user_id,
            status="created",
            message=f"Notification created for {event.event_type} on order {event.order_id}",
        )
        db.add(notification)
        db.commit()
        logger.info(
            "notification_created",
            extra={
                "event": "notification.created",
                "event_id": event.event_id,
                "order_id": event.order_id,
                "request_id": request_id,
            },
        )
    except IntegrityError:
        db.rollback()
        logger.info(
            "duplicate_event_ignored",
            extra={"event": "event.duplicate_ignored", "event_id": event.event_id, "order_id": event.order_id},
        )
    finally:
        db.close()
