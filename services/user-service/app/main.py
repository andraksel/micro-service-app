import logging

from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db, init_db, is_database_ready
from app.logging_config import RequestIdMiddleware, configure_logging
from app.metrics import setup_metrics
from app.models import User
from app.schemas import UserCreate, UserResponse, UserStatusUpdate


configure_logging()
logger = logging.getLogger("user-service")

app = FastAPI(title="user-service", version="1.0.0")
app.add_middleware(RequestIdMiddleware)
setup_metrics(app)


@app.on_event("startup")
def startup() -> None:
    init_db()
    logger.info("service_started", extra={"event": "service.started"})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "user-service"}


@app.get("/ready")
def ready() -> dict[str, str]:
    if not is_database_ready():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="database is not ready")
    return {"status": "ready", "service": "user-service"}


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    user = User(email=str(payload.email).lower(), full_name=payload.full_name)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already exists")
    db.refresh(user)
    logger.info("user_created", extra={"event": "user.created"})
    return user


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    return user


@app.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)) -> list[User]:
    return list(db.query(User).order_by(User.created_at.desc()).all())


@app.patch("/users/{user_id}/status", response_model=UserResponse)
def update_user_status(user_id: str, payload: UserStatusUpdate, db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    user.status = payload.status
    db.commit()
    db.refresh(user)
    logger.info("user_status_updated", extra={"event": "user.status_updated"})
    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, db: Session = Depends(get_db)) -> Response:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    user.status = "deleted"
    db.commit()
    logger.info("user_deleted", extra={"event": "user.deleted"})
    return Response(status_code=status.HTTP_204_NO_CONTENT)
