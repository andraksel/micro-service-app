from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class OrderEventPayload(BaseModel):
    event_type: Literal["order.created", "order.paid", "order.cancelled"]
    event_id: str
    order_id: str
    user_id: str
    occurred_at: datetime


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_id: str
    event_type: str
    order_id: str
    user_id: str
    status: str
    message: str
    created_at: datetime
